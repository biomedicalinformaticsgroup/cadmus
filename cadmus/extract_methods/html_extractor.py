# cadmus_processor/formats/html_extractor.py
import re
import os
import zipfile
import logging
from pathlib import Path
from io import TextIOWrapper
import json
import pandas as pd
from bs4 import BeautifulSoup
from typing import Tuple, Optional

# These two functions should come from wherever you implemented your section‐detection rules
from cadmus.extract_methods.section_detection_rules import (
    is_start_of_materials_methods,
    is_end_of_materials_methods,
)

# Shared helpers (make sure utils.py implements these)
from cadmus.extract_methods.utils import setup_logger, ensure_dir

def can_handle(pmid: str, cadmus_base_dir: str, metadata_row: pd.Series, logger: logging.Logger = None) -> Tuple[bool, Optional[str]]:
    """
    Return True if this row indicates an HTML zip is available on disk.
    We expect metadata_row['html'] == 1 and metadata_row['html_parse_d']['file_path'] exists.
    """
    if logger is None:
        logger = setup_logger(__name__)

    if metadata_row.get("html", 0) != 1:
        logger.debug(f"[HTML][SKIP] PMID {pmid}: 'html' flag is not 1.")
        return False, None

    parse_info = metadata_row.get("html_parse_d", {})
    zip_path = parse_info.get("file_path", "")
    zip_path = zip_path.replace("output", str(cadmus_base_dir)).replace(".//", "/")

    if not zip_path:
        logger.debug(f"[HTML][SKIP] PMID {pmid}: No file path found in metadata.")
        return False, None

    if os.path.exists(zip_path):
        logger.info(f"[HTML][FOUND] PMID {pmid}: File found at {zip_path}")
        return True, zip_path
    else:
        logger.warning(f"[HTML][MISSING] PMID {pmid}: File not found at {zip_path}")
        return False, None



def extract_methods(
    pmid: str,
    file_path: Path,
    output_dir: Path,
    logs_dir: Path,
    logger: logging.Logger = None
) -> (bool, int): # type: ignore
    """
    Attempt to extract “Materials & Methods” paragraphs from the HTML zip.

    Parameters:
        pmid (str): Document identifier.
        output_dir (Path): Directory where we will write `methods_subtitles_{pmid}.csv`.
        logs_dir (Path): Directory where format‐specific logs (e.g. no_methods_docs_html.txt) go.
        logger (logging.Logger): If None, we create a local one just for this module.

    Returns:
        (was_successful: bool, num_unique_subtitles: int)
    """
    if logger is None:
        logger = setup_logger(__name__)

    zip_path = file_path

    try:
        soup = _process_html_from_zip(zip_path)
    except Exception as e:
        logger.error(f"[HTML][ERROR] Failed to unzip/parse HTML for PMID {pmid}: {e}")
        _append_to_log(logs_dir / "html_processing_errors.txt", f"{pmid}\t{zip_path}\t{e}")
        return False, 0

    # Attempt extraction via multiple strategies
    paragraphs = None
    for strategy in [
        _extract_from_standard_sections,
        _extract_from_semantic_sections_with_roles,
        _extract_from_nlm_structured_divs,
        _extract_from_fallback_divs,
        _extract_from_ovid_format,
        _walk_forward_from_methods_heading
    ]:
        try:
            paragraphs = strategy(soup, pmid)
        except Exception as e:
            logger.debug(f"[HTML][DEBUG] Strategy {strategy.__name__} raised exception for PMID {pmid}: {e}")
            paragraphs = None

        if paragraphs:
            logger.info(f"[HTML] {pmid}: extracted using {strategy.__name__}")
            break

    if not paragraphs:
        # No strategy succeeded → log to no_methods_docs_html.txt
        _append_to_log(logs_dir / "no_methods_docs_html.txt", pmid)
        return False, 0

    # Build DataFrame, dedupe by (doc_id, subtitle)
    df = pd.DataFrame(paragraphs, columns=["doc_id", "subtitle", "paragraph"])
    df = (
        df
        .groupby(["doc_id", "subtitle"], as_index=False)
        .agg({"paragraph": lambda grp: "\n\n".join(grp)})
    )

    ensure_dir(output_dir)
    output_json = output_dir / f"methods_subtitles_{pmid}.json"
    # Convert to list of dictionaries and write to JSON
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    num_unique_subtitles = df["subtitle"].nunique()
    return True, num_unique_subtitles


def _append_to_log(log_path: Path, text: str) -> None:
    """
    Append a single line (or tab-separated values) to log_path.
    """
    ensure_dir(log_path.parent)
    with open(str(log_path), "a") as f:
        f.write(f"{text}\n")


def _process_html_from_zip(zip_path: str) -> BeautifulSoup:
    """
    Unzip the given HTML zip and return a BeautifulSoup for the first .html file found.
    Raises if no .html is found or if unzip fails.
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        html_files = [name for name in z.namelist() if name.lower().endswith(".html")]
        if not html_files:
            raise FileNotFoundError(f"No .html file inside zip: {zip_path}")

        html_filename = html_files[0]
        with z.open(html_filename) as html_file:
            soup = BeautifulSoup(TextIOWrapper(html_file, "utf-8"), "html.parser")
            return soup


# ——————————————————————————————————————————————————————————————
# Below: all the “per‐strategy” extraction functions.
#
# Each returns a List[dict] with keys {"doc_id", "subtitle", "paragraph"} or None.
# ——————————————————————————————————————————————————————————————


def _extract_from_standard_sections(soup: BeautifulSoup, doc_id: str):
    """
    Strategy 1–3 from your original code:
      1) <section data-title="Materials and Methods">
      2) <section> or <div> whose immediate child heading matches “Materials and Methods”
      3) <section class="article-section__content"> with a <h2 class="article-section__title">
    """
    candidate_blocks = []

    # Strategy 1: <section data-title="materials and methods">
    section = soup.find(
        "section",
        {"data-title": re.compile(r"materials\s*(and|&)?\s*methods", re.IGNORECASE)}
    )
    if section:
        candidate_blocks.append(section)

    # Strategy 2: Look for any <section> or <div> whose top‐level <h1/2/3> matches start‐of‐materials‐methods
    for block in soup.find_all(["section", "div"]):
        heading = block.find(["h1", "h2", "h3"], recursive=False)
        if heading and is_start_of_materials_methods(heading.get_text(strip=True)):
            candidate_blocks.append(block)

    # Strategy 3: Class‐based “article‐section__content” with an <h2 class="article-section__title">
    for block in soup.find_all("section", class_="article-section__content"):
        h2 = block.find("h2", class_="article-section__title")
        if h2 and is_start_of_materials_methods(h2.get_text(strip=True)):
            candidate_blocks.append(block)

    if not candidate_blocks:
        return None

    rows = []
    for block in candidate_blocks:
        rows.extend(_extract_paragraphs_from_section(block, doc_id, default_subtitle="Materials and Methods"))

    return rows if rows else None


def _extract_from_fallback_divs(soup: BeautifulSoup, doc_id: str):
    """
    Strategy 4:
      - Look for <div id="methods"> or <div id="section-2">
      - If not found, find an <a href="#..."> whose text starts “Materials and Methods”, then resolve that id.
    """
    div_candidates = ["methods", "section-2"]
    target_div = None

    for div_id in div_candidates:
        target_div = soup.find("div", {"id": div_id})
        if target_div:
            break

    # If still none, attempt to find <a href="#something"> whose text is start‐of‐materials‐methods
    if not target_div:
        for anchor in soup.find_all("a", href=True):
            if is_start_of_materials_methods(anchor.get_text(strip=True)):
                ref_id = anchor["href"].lstrip("#")
                target_div = soup.find("div", {"id": ref_id})
                if target_div:
                    break

    if not target_div:
        return None

    rows = []
    current_subtitle = "Methods"
    for tag in target_div.find_all(["p", "span"]):
        text = tag.get_text(strip=True)
        if not text or is_end_of_materials_methods(text):
            break

        # If it’s a <span> with class “level-4”, treat as a sub‐subtitle
        if tag.name == "span" and "level-4" in tag.get("class", []):
            current_subtitle = text
        elif tag.name == "p":
            rows.append({
                "doc_id": doc_id,
                "subtitle": current_subtitle,
                "paragraph": text
            })

    return rows if rows else None


def _extract_from_ovid_format(soup: BeautifulSoup, doc_id: str):
    """
    Strategy 5: OVID‐style HTML uses <h2 class="ejp-article-outline-heading">…
    Walk siblings until the next <h2> of the same class.
    """
    for h2 in soup.find_all("h2", class_="ejp-article-outline-heading"):
        if is_start_of_materials_methods(h2.get_text(strip=True)):
            content_blocks = []
            sibling = h2.find_next_sibling()
            while sibling and not (
                sibling.name == "h2"
                and "ejp-article-outline-heading" in sibling.get("class", [])
            ):
                content_blocks.append(sibling)
                sibling = sibling.find_next_sibling()

            rows = []
            current_subtitle = "Materials and Methods"
            for block in content_blocks:
                if block.name == "p":
                    text = block.get_text(strip=True)
                    if not text or is_end_of_materials_methods(text):
                        break

                    # If <p> has a <strong><em>… that’s a new subtitle
                    strong_em = block.find("strong")
                    if strong_em and strong_em.find("em"):
                        current_subtitle = strong_em.get_text(strip=True).rstrip(":")

                    rows.append({
                        "doc_id": doc_id,
                        "subtitle": current_subtitle,
                        "paragraph": text
                    })
            return rows if rows else None

    return None


def _walk_forward_from_methods_heading(soup: BeautifulSoup, doc_id: str):
    """
    Strategy 6: Locate the first heading (<h1–h4>) that marks the start of 
    the "Materials and Methods" section. Walk through its siblings until 
    another heading signals the end of the section, collecting all 
    paragraphs (including those nested inside containers) along the way.
    """
    methods_heading = None
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        if is_start_of_materials_methods(tag.get_text(strip=True)):
            methods_heading = tag
            break

    if not methods_heading:
        return None

    rows = []
    current_subtitle = "Materials and Methods"
    current = methods_heading.find_next_sibling()

    while current:
        text = current.get_text(strip=True)
        if is_end_of_materials_methods(text):
            break

        if current.name in ["h2", "h3", "h4"]:
            current_subtitle = text.rstrip(":.")
        elif current.name == "p":
            if text:
                rows.append({
                    "doc_id": doc_id,
                    "subtitle": current_subtitle,
                    "paragraph": text
                })
        else:
            # If it’s a container, grab all nested <p>
            for p in current.find_all("p", recursive=True):
                p_text = p.get_text(strip=True)
                if p_text and not is_end_of_materials_methods(p_text):
                    rows.append({
                        "doc_id": doc_id,
                        "subtitle": current_subtitle,
                        "paragraph": p_text
                    })
        current = current.find_next_sibling()

    return rows if rows else None


def _extract_from_nlm_structured_divs(soup: BeautifulSoup, doc_id: str):
    """
    Strategy 7: NLM‐style <div class="NLM_sec NLM_sec_level_1"> … find the one whose <h2> is “Materials and Methods”.
    Then dive into its children <div class="NLM_sec NLM_sec_level_2"> … aggregate all <div class="NLM_p"> text.
    """
    methods_container = None
    for section in soup.find_all("div", class_="NLM_sec NLM_sec_level_1"):
        heading = section.find("h2")
        if heading and is_start_of_materials_methods(heading.get_text(strip=True)):
            methods_container = section
            break

    if not methods_container:
        return None

    rows = []
    current_subtitle = "Materials and Methods"
    # For each level‐2 subsection, update subtitle if there’s an <h3> or <h4>
    for subsection in methods_container.find_all(
        "div", class_="NLM_sec NLM_sec_level_2", recursive=True
    ):
        h3 = subsection.find(["h3", "h4"])
        if h3:
            current_subtitle = h3.get_text(strip=True).rstrip(":.")
        for para in subsection.find_all("div", class_="NLM_p", recursive=True):
            text = para.get_text(strip=True)
            if text and not is_end_of_materials_methods(text):
                rows.append({
                    "doc_id": doc_id,
                    "subtitle": current_subtitle,
                    "paragraph": text
                })

    return rows if rows else None


def _extract_from_semantic_sections_with_roles(soup: BeautifulSoup, doc_id: str):
    """
    Strategy 8: <section data-type="materials methods"> … inside it, look for nested <section> blocks.
    Each nested <section> may have <h3> or <h4> as subtitles, and paragraphs are <div role="paragraph">.
    """
    methods_section = soup.find(
        "section",
        {"data-type": re.compile(r"materials\s*methods", re.IGNORECASE)}
    )
    if not methods_section:
        return None

    rows = []
    current_subtitle = "Materials and Methods"
    for subsec in methods_section.find_all("section", recursive=True):
        heading = subsec.find(["h3", "h4"])
        if heading:
            current_subtitle = heading.get_text(strip=True).rstrip(":.")
        for para_div in subsec.find_all("div", attrs={"role": "paragraph"}):
            text = para_div.get_text(strip=True)
            if text and not is_end_of_materials_methods(text):
                rows.append({
                    "doc_id": doc_id,
                    "subtitle": current_subtitle,
                    "paragraph": text
                })
    return rows if rows else None


def _extract_paragraphs_from_section(section, doc_id: str, default_subtitle="Materials and Methods"):
    """
    Helper for Strategy 1, 2, 3: Given a <section> (or any Tag), walk its descendants.
    Whenever you hit <h2/3/4>, update current_subtitle. Whenever you hit <p> or <div role="paragraph">,
    append a row under current_subtitle until you see is_end_of_materials_methods.
    """
    rows = []
    current_subtitle = default_subtitle

    for el in section.descendants:
        if getattr(el, "name", None) in {"h2", "h3", "h4"}:
            heading_text = el.get_text(strip=True)
            if is_end_of_materials_methods(heading_text):
                break
            current_subtitle = heading_text.rstrip(":.")
        elif getattr(el, "name", None) in {"p", "div"}:
            # either <p> or <div role="paragraph">
            if el.name == "p" or el.get("role") == "paragraph":
                para_text = el.get_text(strip=True)
                if para_text and not is_end_of_materials_methods(para_text):
                    rows.append({
                        "doc_id": doc_id,
                        "subtitle": current_subtitle,
                        "paragraph": para_text
                    })

    return rows


# End of html_extractor.py
