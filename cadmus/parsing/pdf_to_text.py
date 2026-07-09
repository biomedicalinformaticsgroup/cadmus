import fitz  # PyMuPDF
import io
import re
from typing import List

def pdf_to_text(path: str) -> str:
    """Extracts plain text from a PDF using PyMuPDF."""
    doc = fitz.open(path)
    parts: List[str] = []
    for page in doc:
        text = page.get_text("text")
        parts.append(text)
    doc.close()
    return "\n".join(parts)


def pdf_to_markdown(path: str) -> str:
    """A simple conversion from PDF text to Markdown.

    This is heuristic: preserves blank-line paragraph breaks and converts
    obvious all-caps lines to headings.
    """
    txt = pdf_to_text(path)
    lines = [l.rstrip() for l in txt.splitlines()]
    out_lines: List[str] = []
    for i, line in enumerate(lines):
        if not line.strip():
            out_lines.append("")
            continue
        # heuristic: if line is short and ALL CAPS, treat as heading
        if 2 <= len(line) <= 120 and line.strip().upper() == line.strip() and re.search(r"[A-Z]", line):
            out_lines.append(f"## {line.strip().title()}")
            continue
        # collapse excessive spaces
        cleaned = re.sub(r"\s+", " ", line).strip()
        out_lines.append(cleaned)
    # join paragraphs with double-newline
    md = "\n".join(out_lines)
    # simple post-processing: ensure paragraphs separated
    md = re.sub(r"(?:\n\s*){3,}", "\n\n", md)
    return md


def extract_pages(path: str, pages: List[int]) -> str:
    """Extract text from specific 0-based page indices."""
    doc = fitz.open(path)
    parts: List[str] = []
    for p in pages:
        if 0 <= p < doc.page_count:
            parts.append(doc[p].get_text("text"))
    doc.close()
    return "\n".join(parts)
