# cadmus_processor/formats/pdf_extractor.py

import os
import logging
import zipfile
from pathlib import Path
from collections import defaultdict
from typing import Tuple, Optional

import pandas as pd
from papermage.recipes import CoreRecipe
import json
from cadmus.extract_methods.section_detection_rules import (
    is_start_of_materials_methods,
    is_end_of_materials_methods,
)
from cadmus.extract_methods.utils import setup_logger, ensure_dir
from cadmus.extract_methods.plain_extractor import _extract_methods_from_txt

# Create a single, module‐wide PaperMage recipe instance
_CORE_RECIPE = CoreRecipe()


def can_handle(
    pmid: str,
    cadmus_base_dir: str,
    metadata_row: pd.Series,
    logger: logging.Logger = None
) -> Tuple[bool, Optional[str]]:
    """
    Return True if this row indicates a PDF is available on disk.
    Also returns the corrected file path if found, else None.
    """
    if logger is None:
        logger = setup_logger(__name__)

    if metadata_row.get("pdf", 0) != 1:
        logger.debug(f"[PDF][SKIP] PMID {pmid}: 'pdf' flag is not 1.")
        return False, None

    parse_info = metadata_row.get("pdf_parse_d", {})
    pdf_path = parse_info.get("file_path", "")
    pdf_path = pdf_path.replace("output", str(cadmus_base_dir)).replace(".//", "/")

    if not pdf_path:
        logger.debug(f"[PDF][SKIP] PMID {pmid}: No file path found in metadata.")
        return False, None

    if os.path.exists(pdf_path):
        logger.info(f"[PDF][FOUND] PMID {pmid}: File found at {pdf_path}")
        return True, pdf_path
    else:
        logger.warning(f"[PDF][MISSING] PMID {pmid}: File not found at {pdf_path}")
        return False, None

def extract_pdf_from_path(
    pmid: str,
    pdf_or_zip: str,
    output_dir: Path,
    logs_dir: Path,
    logger: logging.Logger
) -> tuple[bool, str | None, bool]:
    """
    Returns:
        (success: bool, pdf_path: str | None, is_temp: bool)
    """
    if pdf_or_zip.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(pdf_or_zip, "r") as z:
                pdf_candidates = [name for name in z.namelist() if name.lower().endswith(".pdf")]
                if not pdf_candidates:
                    logger.error(f"[PDF][ERROR] No .pdf found inside zip for PMID {pmid}: {pdf_or_zip}")
                    _append_to_log(logs_dir / "pdf_processing_errors.txt", f"{pmid}\tNo inner PDF in {pdf_or_zip}")
                    return False, None, False

                inner_pdf_name = pdf_candidates[0]
                temp_pdf_path = output_dir / f"{pmid}_temp.pdf"
                ensure_dir(output_dir)
                with z.open(inner_pdf_name) as inner_fh:
                    pdf_bytes = inner_fh.read()
                    temp_pdf_path.write_bytes(pdf_bytes)

                return True, str(temp_pdf_path), True
        except Exception as e:
            logger.error(f"[PDF][ERROR] Failed to extract PDF from ZIP for PMID {pmid}: {e}")
            _append_to_log(logs_dir / "pdf_processing_errors.txt", f"{pmid}\t{pdf_or_zip}\t{e}")
            return False, None, False
    else:
        return True, pdf_or_zip, False

def extract_methods(
    pmid: str,
    file_path: Path,
    parse_info: dict,
    output_dir: Path,
    logs_dir: Path,
    logger: logging.Logger = None
) -> (bool, int): # type: ignore
    """
    Attempt to extract “Materials & Methods” text from a PDF via PaperMage.

    Parameters:
        pmid (str): Document identifier.
        parse_info (dict): Should contain {"file_path": "<absolute or relative path to .pdf>"}.
        output_dir (Path): Directory under which we will write:
            - {pmid}_full_text.csv   (one row with all extracted M&M text)
            - {pmid}_sections.csv    (one row per M&M subsection)
        logs_dir (Path): Directory where format‐specific logs (e.g. errors) go.
        logger (logging.Logger): If None, creates a local logger.

    Returns:
        (was_successful: bool, num_unique_subsections: int)
    """
    if logger is None:
        logger = setup_logger(__name__)

    pdf_or_zip = file_path
    output_json = output_dir / f"methods_subtitles_{pmid}.json"

    success, pdf_real_path, is_temp_file = extract_pdf_from_path(pmid, pdf_or_zip, output_dir, logs_dir, logger)
    if not success or not pdf_real_path:
        return False, 0

    # Ensure output/log directories exist
    ensure_dir(output_dir)
    ensure_dir(logs_dir)

    # Set up a file handler for this module if not already present
    log_file = logs_dir / "pdf_processing.log"
    setup_logger(str(log_file))

    try:
        logger.info(f"[PDF] Running PaperMage on {pdf_real_path} (PMID {pmid})")
        doc = _CORE_RECIPE.run(pdf_real_path)
        if is_temp_file:
            Path(pdf_real_path).unlink()
    except Exception as e:
        err_msg = f"[PDF][ERROR] Failed to run PaperMage on PMID {pmid}, file {pdf_real_path}: {e}"
        logger.error(err_msg)
        _append_to_log(logs_dir / "pdf_processing_errors.txt", f"{pmid}\t{pdf_real_path}\t{e}")
        return False, 0

    # Group all paragraphs by section heading
    section_paragraphs = _group_paragraphs_by_section(doc)
    
    if list(section_paragraphs)[0] == "Plain text":
        # No sections detected, just one big block of text
        logger.info(f"[PDF] No sections found for PMID {pmid}, treating as plain text.")
        plain_text = section_paragraphs['Plain text']
        status, df_from_plain = _extract_methods_from_txt(
            text=plain_text,
            doc_id=pmid,
            output_json=output_json,
            logs_dir=str(logs_dir)
        )
        return status, df_from_plain["subtitle"].nunique() if isinstance(df_from_plain, pd.DataFrame) else 0
        
    # Now, keep only sections between “Materials and Methods” start/end
    sub_sections = defaultdict(list)
    inside_mm = False
    current_title = None

    for section_title, paras in section_paragraphs.items():
        if is_start_of_materials_methods(section_title):
            inside_mm = True
            current_title = section_title
            logger.info(f"[PDF] Detected start of M&M section: '{section_title}'")
            sub_sections[current_title].extend(paras)
            continue

        if inside_mm:
            if is_end_of_materials_methods(section_title):
                inside_mm = False
                logger.info(f"[PDF] Detected end of M&M at section: '{section_title}'")
                break

            # If we have moved to a new subsection heading
            if current_title != section_title:
                logger.debug(f"[PDF] Detected M&M subsection: '{section_title}'")
                current_title = section_title

            sub_sections[current_title].extend(paras)

    if not sub_sections:
        # No materials & methods found → log and return failure
        _append_to_log(logs_dir / "no_methods_docs_pdf.txt", pmid)
        return False, 0

    # Build DataFrames:
    # 1) One row per subsection (doc_id, Subsection, Text)
    section_rows = []
    final_text_parts = []

    for subsection, paras in sorted(sub_sections.items()):
        joined_text = " ".join(paras).strip()
        # Skip very short headings or empty content
        if not subsection or len(joined_text) < 5 or subsection.islower():
            continue

        section_rows.append({
            "doc_id": pmid,
            "subtitle": subsection,
            "paragraph": joined_text
        })
        final_text_parts.append(f"{subsection}\n{joined_text}")

    if not section_rows:
        # After filtering too‐short subsections, nothing to write
        _append_to_log(logs_dir / "no_valid_subsections_pdf.txt", pmid)
        return False, 0

    # 2) One row containing the entire M&M text (joined by two newlines)
    full_text_string = "\n\n".join(final_text_parts)
    full_row = {"doc_id": pmid, "Text": full_text_string}

    # Write outputs
    df_sections = pd.DataFrame(section_rows)
    #rename columns to match expected output
    
    # Convert to list of dictionaries and write to JSON
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(df_sections.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        
    #csv_full_path = output_dir / f"{pmid}_full_text.csv"
    #csv_sections_path = output_dir / f"{pmid}_sections.csv"

    #df_full = pd.DataFrame([full_row])
    #df_sections = pd.DataFrame(section_rows)

    #df_full.to_csv(str(csv_full_path), index=False)
    #df_sections.to_csv(str(csv_sections_path), index=False)

    num_subsections = df_sections["subtitle"].nunique()
    logger.info(f"[PDF] Extracted {num_subsections} unique subsections for PMID {pmid}")
    return True, num_subsections


def _append_to_log(log_path: Path, text: str) -> None:
    """
    Append a single line (or tab-separated values) to log_path.
    """
    ensure_dir(log_path.parent)
    with open(str(log_path), "a") as f:
        f.write(f"{text}\n")


def _group_paragraphs_by_section(doc) -> dict[str, list[str]]:
    """
    Build a dict mapping section headings (if present) to paragraph texts.
    If no sections exist, return a single entry with all text under 'Plain text'.
    """
    result: dict[str, list[str]] = {}

    if doc.sections:
        # Use semantic section headings
        section_boundaries = sorted(
            [(sec.spans[0].start, sec) for sec in doc.sections if sec.spans],
            key=lambda x: x[0]
        )
        max_para_end = max(p.spans[0].end for p in doc.paragraphs if p.spans)
        section_boundaries.append((max_para_end + 1, None))

        for idx in range(len(section_boundaries) - 1):
            this_start, sec_entity = section_boundaries[idx]
            next_start, _ = section_boundaries[idx + 1]

            paras_in_section = [
                p for p in doc.paragraphs
                if p.spans and this_start <= p.spans[0].start < next_start
            ]
            paras_in_section.sort(key=lambda p: p.spans[0].start)

            heading = sec_entity.text if sec_entity is not None else "<no heading>"
            result[heading] = [p.text for p in paras_in_section]
    else:
        # Fallback: merge all paragraphs under a single key -> can happen with older or malformed PDFs
        all_paras = [p.text for p in doc.paragraphs if p.text.strip()]
        result["Plain text"] = ' '.join(all_paras)

    return result
