# cadmus_processor/formats/plain_extractor.py

import os
import re
import zipfile
import logging
from pathlib import Path
import json
import pandas as pd
from cadmus.extract_methods.utils import setup_logger, ensure_dir
from typing import Tuple, Optional


def can_handle(pmid: str, cadmus_base_dir: Path, metadata_row: pd.Series, logger: logging.Logger = None) -> Tuple[bool, Optional[str]]:
    """
    Return True if this row indicates a plain-text ZIP is available on disk.
    We expect metadata_row['plain'] == 1 and metadata_row['plain_parse_d']['file_path'] exists.
    """
    if logger is None:
        logger = setup_logger(__name__)

    if metadata_row.get("plain", 0) != 1:
        logger.debug(f"[PLAIN][SKIP] PMID {pmid}: 'plain' flag is not 1.")
        return False, None

    parse_info = metadata_row.get("plain_parse_d", {})
    zip_path = parse_info.get("file_path", "")
    zip_path = zip_path.replace("output", str(cadmus_base_dir)).replace(".//", "/")

    if not zip_path:
        logger.debug(f"[PLAIN][SKIP] PMID {pmid}: No file path found in metadata.")
        return False, None

    if os.path.exists(zip_path):
        logger.info(f"[PLAIN][FOUND] PMID {pmid}: File found at {zip_path}")
        return True, zip_path
    else:
        logger.warning(f"[PLAIN][MISSING] PMID {pmid}: File not found at {zip_path}")
        return False, None


def extract_methods(
    pmid: str,
    file_path: Path,
    output_dir: Path,
    logs_dir: Path,
    logger: logging.Logger = None
) -> (bool, int): # type: ignore
    """
    Attempt to extract “Materials & Methods” sections from a plain-text ZIP.

    Parameters:
        pmid (str): Document identifier.
        output_dir (Path): Directory where we will write methods_subtitles_{pmid}.csv.
        logs_dir (Path): Directory where plain-text–specific logs (e.g. no_methods_docs_plain.txt) go.
        logger (logging.Logger): If None, create a local one.

    Returns:
        (was_successful: bool, num_unique_subtitles: int)
    """
    if logger is None:
        logger = setup_logger(__name__)

    zip_path = file_path

    ensure_dir(output_dir)
    ensure_dir(logs_dir)

    # Set up a per-module log file
    plain_log = logs_dir / "plain_processing.log"
    setup_logger(str(plain_log))

    subtitle_counts = []

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            txt_files = [f for f in z.namelist() if f.lower().endswith(".txt")]
            if not txt_files:
                logger.info(f"[PLAIN] No .txt files in ZIP for PMID {pmid}")
                _append_to_log(logs_dir / "no_methods_docs_plain.txt", pmid)
                return False, 0

            # For each .txt inside, attempt extraction
            for fname in txt_files:
                with z.open(fname) as fh:
                    text = fh.read().decode("utf-8")
                    #output_csv_path = output_dir / f"methods_subtitles_{pmid}.csv"
                    output_json_path = output_dir / f"methods_subtitles_{pmid}.json"
                    
                    was_successful, df = _extract_methods_from_txt(
                        text=text,
                        doc_id=pmid,
                        output_json=output_json_path,
                        logs_dir=str(logs_dir)
                    )
                    if was_successful and isinstance(df, pd.DataFrame):
                        count = df["subtitle"].nunique()
                        subtitle_counts.append(count)
    except Exception as e:
        logger.error(f"[PLAIN][ERROR] Failed to unzip/process for PMID {pmid}: {e}")
        _append_to_log(logs_dir / "processing_errors_plain.txt", f"{pmid}\t{zip_path}\t{e}")
        return False, 0

    total_subtitles = sum(subtitle_counts)
    if total_subtitles == 0:
        # Nothing extracted
        _append_to_log(logs_dir / "no_methods_docs_plain.txt", pmid)
        return False, 0

    return True, total_subtitles


def _append_to_log(log_path: Path, text: str) -> None:
    """
    Append a single line to the given log file.
    """
    ensure_dir(log_path.parent)
    with open(str(log_path), "a") as f:
        f.write(f"{text}\n")


def is_likely_junk_section(text: str) -> bool:
    """
    Heuristics to skip “junk” sections (e.g. author roles, addresses, etc.).
    """
    if len(re.findall(
        r'(writing|project administration|review|editing|funding acquisition|methodology|conceptualization)',
        text, flags=re.IGNORECASE
    )) > 5:
        return True
    if len(re.findall(r'[A-Z][a-z]+ [A-Z]\.', text)) > 5:  # many names
        return True
    return False


def _extract_methods_from_txt(text: str, doc_id: str, output_json: str = None, logs_dir: str = None):
    """
    Extracts all 'Materials and Methods'-like sections from a single plain-text string.

    Parameters:
        text (str): Flat article text.
        doc_id (str): Document identifier.
        output_json (str): Path to JSON for saving extracted content.
        logs_dir (str, optional): Path to store logs on failures.

    Returns:
        (bool, pd.DataFrame|False): (True, DataFrame) if found; (False, False) otherwise.
    """
    rows = []
    text_lower = text.lower()

    # Regex to match potential methods-like headers
    section_header_pattern = (
        r'(?<!\w)'
        r'(?:\d{1,2}(?:\.\d{1,2})?\s+)?'                             # optional "2." or "2.1"
        r'(materials\s*(?:and|&)\s*methods|'                         # materials and methods
        r'experimental\s+(?:procedures|section)|methodology|methods)'
        r'\b'
        r'(?!\s*(?:was|were)\s+(?:performed|conducted|carried\s+out))'
    )
    section_header_matches = list(re.finditer(
        section_header_pattern, text, flags=re.IGNORECASE))

    # Regex for stop sections
    stop_section_regex = re.compile(
        r'(?<!\w)(\d{0,2}\.?\d{0,2}\s*)?(' +
        '|'.join(re.escape(title) for title in [
            "results", "discussion", "conclusion", "references",
            "acknowledgments", "acknowledgment", "bibliography",
            "supplementary materials", "supporting information"
        ]) + r')\b',
        flags=re.IGNORECASE
    )

    if not section_header_matches:
        if logs_dir:
            ensure_dir(Path(logs_dir))
            with open(os.path.join(logs_dir, "no_methods_docs_plain.txt"), "a") as f:
                f.write(f"{doc_id}\n")
        return False, False

    extracted_ranges = []
    for match in section_header_matches:
        start_idx = match.start()
        end_idx_match = match.end()

        # Skip if inside an already‐extracted range
        if any(prev_start <= start_idx < prev_end for prev_start, prev_end in extracted_ranges):
            continue

        # 1) Skip if next char is ')' or ','
        if end_idx_match < len(text) and text[end_idx_match] in [")", ","]:
            continue
            
        # 2) Skip if next characters are " in" or " for"
        if re.match(r'\s+(in|for|is|of|by|to)\b', text_lower[end_idx_match:end_idx_match + 10]):
            continue

        # 3) Skip if citation-like phrase is near the match
        context_window_before = 50
        context_window_after = 50
        
        context_before = text_lower[max(0, start_idx - context_window_before):start_idx]
        context_after = text_lower[end_idx_match:end_idx_match + context_window_after]
        
        citation_phrases = [
            "as described in",
            "as previously described",
            "previously reported in",
            "as reported in",
            "according to",
            "in accordance with",
            "see also",
            "see e.g.",
            "has been described"
        ]
        
        # Skip if any phrase found in context before or after
        if any(phrase in context_before or phrase in context_after for phrase in citation_phrases):
            continue

        # 4) Skip if followed by mostly numbers or bracketed integer
        if re.match(r'\s+(?:[\d\s,]{5,}|\[\d+\])', text[end_idx_match:end_idx_match + 20]):
            continue

        section_title = match.group().strip()
        end_idx = None

        # Find the first valid stop section after start_idx
        next_text = text[start_idx:]
        for stop_match in stop_section_regex.finditer(next_text):
            end_candidate_start = start_idx + stop_match.start()

            # 1) Skip if the stop section title is preceded by a context that suggests it’s not a section
            context_before_stop = text_lower[max(0, end_candidate_start - 30): end_candidate_start]
            if re.search(
                r'\b(?:the|this|that|these|those|our|their|its|and|of|all|in|'
                r'similar|reliable|significant|preliminary|previous|current|presented|further|recorded|unpublished)\s+$',
                context_before_stop,
            ):
                continue

            # 2) skip if the title is "results" or "references" and followed by a passive or active verb
            title = stop_match.group(2).lower()
            after = next_text[stop_match.end(): stop_match.end() + 30].lower()
            if title == "results" or title == "references":
                if re.match(r'\s*,', after):
                    continue
                # most common passives: are/were + participle
                if re.match(
                    r'\s*(?:are|were)\s+(?:shown|presented|reported|provided|expressed|'
                    r'described|listed|summarized|summarised|compared|indicated|'
                    r'displayed|illustrated|obtained|analysed|analyzed)\b',
                    after,
                ):
                    continue
                # very common actives immediately after "results"
                if re.match(r'\s*(?:show|shows|showed|indicate|indicates|indicated|'
                            r'suggest|suggests|suggested)\b', after):
                    continue
                # frequent noun-phrase starts
                if re.match(r'\s*(?:of|from|for|in)\b', after):
                    continue

            end_idx = end_candidate_start
            break

        # Extract from start to valid end (or to end of text)
        section_text = (text[start_idx:end_idx].strip() if end_idx
                        else text[start_idx:].strip())

        if is_likely_junk_section(section_text):
            continue

        extracted_ranges.append((start_idx, end_idx if end_idx else len(text)))
        rows.append({
            "doc_id": doc_id,
            "subtitle": section_title,
            "paragraph": section_text
        })

    if not rows:
        if logs_dir:
            ensure_dir(Path(logs_dir))
            with open(os.path.join(logs_dir, "no_methods_docs_plain.txt"), "a") as f:
                f.write(f"{doc_id}\n")
        return False, False
    
    df = pd.DataFrame(rows, columns=["doc_id", "subtitle", "paragraph"]).drop_duplicates()

    # Convert to list of dictionaries and write to JSON
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    return True, df


# End of plain_extractor.py
