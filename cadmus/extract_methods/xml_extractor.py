# cadmus_processor/formats/xml_extractor.py

import os
import re
import zipfile
import logging
import xml.etree.ElementTree as ET
from io import TextIOWrapper
from pathlib import Path
import json
import pandas as pd
from typing import Tuple, Optional
from ftfy import fix_text

from cadmus.extract_methods.section_detection_rules import (
    is_start_of_materials_methods,
    is_end_of_materials_methods,
)
from cadmus.extract_methods.utils import setup_logger, ensure_dir


def can_handle(pmid: str, cadmus_base_dir: str, metadata_row: pd.Series, logger: logging.Logger = None) -> Tuple[bool, Optional[str]]:
    """
    Return True if this row indicates an XML zip is available on disk.
    We expect metadata_row['xml'] == 1 and that metadata_row['xml_parse_d']['file_path'] exists.
    """
    if logger is None:
        logger = setup_logger(__name__)

    if metadata_row.get("xml", 0) != 1:
        logger.debug(f"[XML][SKIP] PMID {pmid}: 'xml' flag is not 1.")
        return False, None

    parse_info = metadata_row.get("xml_parse_d", {})
    zip_path = parse_info.get("file_path", "")
    zip_path = zip_path.replace("output", str(cadmus_base_dir)).replace(".//", "/")

    if not zip_path:
        logger.debug(f"[XML][SKIP] PMID {pmid}: No file path found in metadata.")
        return False, None

    if os.path.exists(zip_path):
        logger.info(f"[XML][FOUND] PMID {pmid}: File found at {zip_path}")
        return True, zip_path
    else:
        logger.warning(f"[XML][MISSING] PMID {pmid}: File not found at {zip_path}")
        return False, None


def extract_methods(
    pmid: str,
    file_path: Path,
    output_dir: Path,
    logs_dir: Path,
    logger: logging.Logger = None
) -> (bool, int): # type: ignore
    """
    Attempt to extract “Materials & Methods” paragraphs from an XML-in-ZIP.

    Parameters:
        pmid (str): Document identifier.
        output_dir (Path): Directory where we will write methods_subtitles_{pmid}.csv.
        logs_dir (Path): Directory where XML-specific logs (e.g. no_methods_docs_xml.txt) go.
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
    xml_log = logs_dir / "xml_processing.log"
    setup_logger(str(xml_log))

    # First attempt “Wiley-like” extraction
    try:
        paragraphs = _extract_materials_methods_from_xml(zip_path, pmid)
    except Exception as e:
        logger.error(f"[XML][ERROR] Wiley-like extraction failed for PMID {pmid}: {e}")
        paragraphs = None

    # If Wiley-like returns no paragraphs, attempt JATS-like
    if not paragraphs:
        logger.info(f"[XML] Falling back to JATS-like extractor for PMID {pmid}")
        try:
            paragraphs = _extract_from_jats_like_article(zip_path, pmid)
        except Exception as e:
            logger.error(f"[XML][ERROR] JATS-like extraction failed for PMID {pmid}: {e}")
            paragraphs = None
            
    # If returns no paragraphs, attempt PMC-like
    if not paragraphs:
        logger.info(f"[XML] Falling back to PMC-like extractor for PMID {pmid}")
        try:
            paragraphs = _extract_from_pmc_xml(zip_path, pmid)
        except Exception as e:
            logger.error(f"[XML][ERROR] PMC-like extraction failed for PMID {pmid}: {e}")
            paragraphs = None

    if not paragraphs:
        # Nothing found → log and return failure
        _append_to_log(logs_dir / "no_methods_docs_xml.txt", pmid)
        return False, 0

    # Build DataFrame, group by (doc_id, subtitle)
    df = pd.DataFrame(paragraphs, columns=["doc_id", "subtitle", "paragraph"])
    df = (
        df
        .groupby(["doc_id", "subtitle"], as_index=False)
        .agg({"paragraph": lambda grp: "\n\n".join(grp)})
    )

    output_json = output_dir / f"methods_subtitles_{pmid}.json"
    # Convert to list of dictionaries and write to JSON
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    num_unique = df["subtitle"].nunique()
    return True, num_unique


def _append_to_log(log_path: Path, text: str) -> None:
    """
    Append a single line to the given log file.
    """
    ensure_dir(log_path.parent)
    with open(str(log_path), "a") as f:
        f.write(f"{text}\n")


def _extract_materials_methods_from_xml(file_path: str, doc_id: str):
    """
    Wiley-like XML extraction:
    Supports both:
      - ZIP archives containing an XML file
      - Direct XML files

    Logic:
    - Detect namespace (if present).
    - Traverse <section> elements in order.
    - When a <section>'s <title> matches start‐of‐methods, set in_methods = True.
    - Collect all <p> under that section/subsections until an end-of-methods title is encountered.
    """
    def parse_xml(root):
        # Detect namespace
        m = re.match(r"\{(.*)\}", root.tag)
        ns_uri = m.group(1) if m else ""
        has_ns = bool(ns_uri)
        ns = {"ns": ns_uri} if has_ns else {}

        section_path = ".//ns:section" if has_ns else ".//section"
        title_tag = "ns:title" if has_ns else "title"
        p_tag = "ns:p" if has_ns else "p"

        results = []
        in_methods = False
        current_subtitle = "Materials and Methods"

        for section in root.findall(section_path, ns):
            title_elem = section.find(title_tag, ns) if has_ns else section.find(title_tag)
            title_text = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

            if not in_methods and is_start_of_materials_methods(title_text):
                in_methods = True
                current_subtitle = title_text or current_subtitle
            elif in_methods and is_end_of_materials_methods(title_text):
                break
            elif in_methods:
                current_subtitle = title_text or current_subtitle

            if in_methods:
                for para in section.findall(p_tag, ns):
                    text = "".join(para.itertext()).strip()
                    if text:
                        results.append({
                            "doc_id": doc_id,
                            "subtitle": current_subtitle,
                            "paragraph": text
                        })

        return results if results else None

    # Handle .zip or .xml
    if str(file_path).lower().endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as z:
            xml_files = [f for f in z.namelist() if f.lower().endswith(".xml")]
            if not xml_files:
                return None
            with z.open(xml_files[0]) as xml_file:
                tree = ET.parse(TextIOWrapper(xml_file, "utf-8"))
                return parse_xml(tree.getroot())
    else:
        # Plain XML file
        with open(file_path, "r", encoding="utf-8") as xml_file:
            tree = ET.parse(xml_file)
            return parse_xml(tree.getroot())


def _extract_from_jats_like_article(file_path: str, doc_id: str):
    """
    JATS-like XML extraction:
    - Supports both .zip and .xml input files.
    - Finds <body>, then recursively searches for the first <sec> whose <title> matches start-of-methods.
    - parse_sec(sec, current_subtitle) collects all <p> until an end-of-methods title is found, then stops.
    """

    def parse_jats_article(root):
        # Detect namespace
        m = re.match(r"\{(.*)\}", root.tag)
        ns_uri = m.group(1) if m else ""
        ns = {"ns": ns_uri} if ns_uri else {}
        use_ns = bool(ns_uri)

        def tag(name: str) -> str:
            return f"ns:{name}" if use_ns else name

        # Locate <body>
        body = root.find(f".//{tag('body')}", ns)
        if body is None:
            return None

        results = []

        def parse_sec(sec, current_subtitle):
            title_elem = sec.find(tag("title"), ns)
            title_text = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

            if is_end_of_materials_methods(title_text):
                return False

            subtitle = title_text or current_subtitle

            for p in sec.findall(tag("p"), ns):
                text = "".join(p.itertext()).strip()
                if text:
                    results.append({
                        "doc_id": doc_id,
                        "subtitle": subtitle,
                        "paragraph": text
                    })

            for child_sec in sec.findall(tag("sec"), ns):
                if parse_sec(child_sec, subtitle) is False:
                    return False

            return True

        def find_first_methods_sec(node):
            for sec in node.findall(tag("sec"), ns):
                title_elem = sec.find(tag("title"), ns)
                title_text = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

                if is_start_of_materials_methods(title_text):
                    return parse_sec(sec, title_text)

                if find_first_methods_sec(sec):
                    return True

            return False

        found = find_first_methods_sec(body)
        return results if found and results else None

    # Detect and load from ZIP or XML file
    if str(file_path).lower().endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as z:
            xml_files = [f for f in z.namelist() if f.lower().endswith(".xml")]
            if not xml_files:
                return None
            with z.open(xml_files[0]) as xml_file:
                tree = ET.parse(TextIOWrapper(xml_file, "utf-8"))
                return parse_jats_article(tree.getroot())
    else:
        with open(file_path, "r", encoding="utf-8") as xml_file:
            tree = ET.parse(xml_file)
            return parse_jats_article(tree.getroot())

def _extract_from_pmc_xml(file_path: str, doc_id: str):
    """
    PMC-style (OAI-PMH-wrapped) XML extraction:
    - Supports both raw .xml files and ZIP archives.
    - Finds <article> inside nested OAI-PMH structure.
    - Locates <body> and extracts Materials & Methods from nested <sec> tags.
    """

    def parse_pmc_article(root):
        # Find the <article> element, regardless of nesting
        article_elem = next((el for el in root.iter() if el.tag.endswith("}article")), None)
        if article_elem is None:
            return None
        root = article_elem

        # Detect namespace
        m = re.match(r"\{(.*)\}", root.tag)
        ns_uri = m.group(1) if m else ""
        ns = {"ns": ns_uri} if ns_uri else {}
        use_ns = bool(ns_uri)

        def tag(name: str) -> str:
            return f"ns:{name}" if use_ns else name

        # Find <body>
        body = root.find(f".//{tag('body')}", ns)
        if body is None:
            return None

        results = []

        def parse_sec(sec, current_subtitle):
            title_elem = sec.find(tag("title"), ns)
            title_text = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
            title_text = fix_text(title_text)

            if is_end_of_materials_methods(title_text):
                return False

            subtitle = title_text or current_subtitle

            for p in sec.findall(tag("p"), ns):
                text = "".join(p.itertext()).strip()
                text = fix_text(text)  
                if text:
                    results.append({
                        "doc_id": doc_id,
                        "subtitle": subtitle,
                        "paragraph": text
                    })

            for child_sec in sec.findall(tag("sec"), ns):
                if parse_sec(child_sec, subtitle) is False:
                    return False

            return True

        def find_first_methods_sec(node):
            for sec in node.findall(tag("sec"), ns):
                title_elem = sec.find(tag("title"), ns)
                title_text = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                title_text = fix_text(title_text)

                if is_start_of_materials_methods(title_text):
                    return parse_sec(sec, title_text)

                if find_first_methods_sec(sec):
                    return True

            return False

        found = find_first_methods_sec(body)
        return results if found and results else None

    # File handling: support .zip and .xml
    file_path_str = str(file_path)  # Ensure we can use string methods
    if file_path_str.lower().endswith(".zip"):
        with zipfile.ZipFile(file_path_str, "r") as z:
            xml_files = [f for f in z.namelist() if f.lower().endswith(".xml")]
            if not xml_files:
                return None
            with z.open(xml_files[0]) as xml_file:
                raw_bytes = xml_file.read()

                encoding_match = re.search(rb'encoding=["\']([^"\']+)["\']', raw_bytes[:200])
                encoding = encoding_match.group(1).decode('ascii') if encoding_match else 'utf-8'

                tree = ET.ElementTree(ET.fromstring(raw_bytes.decode(encoding)))
                return parse_pmc_article(tree.getroot())
    else:
        with open(file_path_str, "rb") as xml_file:
            raw_bytes = xml_file.read()

            encoding_match = re.search(rb'encoding=["\']([^"\']+)["\']', raw_bytes[:200])
            encoding = encoding_match.group(1).decode('ascii') if encoding_match else 'utf-8'

            tree = ET.ElementTree(ET.fromstring(raw_bytes.decode(encoding)))
            return parse_pmc_article(tree.getroot())
