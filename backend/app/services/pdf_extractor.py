"""Layout-aware PDF text extraction for resumes."""

from __future__ import annotations

import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None  # type: ignore

from pypdf import PdfReader

from app.services.section_patterns import split_embedded_section_headers
from app.services.text_cleanup import split_merged_lines


def extract_text_from_pdf(path: str) -> str:
    """Extract resume text from PDF with layout-aware line grouping."""
    if pdfplumber is not None:
        try:
            return _extract_with_pdfplumber(path)
        except Exception as exc:
            logger.warning("pdfplumber extraction failed, falling back to pypdf: %s", exc)

    return _extract_with_pypdf(path)


def _extract_with_pdfplumber(path: str) -> str:
    parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(
                x_tolerance=2,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=True,
            )
            if words:
                parts.extend(_group_words_into_lines(words, page.width or 612))
                continue

            text = page.extract_text(x_tolerance=2, y_tolerance=3, layout=True)
            if text:
                parts.append(text.strip())

    raw = "\n".join(parts)
    raw = _split_embedded_sections(raw)
    return _cleanup_pdf_text(raw, preserve_line_spacing=True)


def _group_words_into_lines(words: list[dict], page_width: float) -> list[str]:
    """Group PDF words into reading-order lines; split multi-column rows."""
    rows: dict[int, list[dict]] = defaultdict(list)
    for word in words:
        bucket = int(round(word["top"] / 3.0))
        rows[bucket].append(word)

    lines: list[str] = []
    gap_threshold = max(28.0, page_width * 0.06)

    for bucket in sorted(rows.keys()):
        row_words = sorted(rows[bucket], key=lambda w: w["x0"])
        segments: list[list[dict]] = []
        current: list[dict] = []

        for word in row_words:
            if current and word["x0"] - current[-1]["x1"] > gap_threshold:
                segments.append(current)
                current = []
            current.append(word)
        if current:
            segments.append(current)

        for segment in segments:
            line = " ".join(w["text"] for w in segment).strip()
            if line:
                lines.append(line)

    return lines


def _split_embedded_sections(text: str) -> str:
    return split_embedded_section_headers(text)


def _extract_with_pypdf(path: str) -> str:
    reader = PdfReader(path)
    raw = "\n".join(page.extract_text() or "" for page in reader.pages)
    raw = _repair_word_per_line(raw)
    raw = _split_embedded_sections(raw)
    return _cleanup_pdf_text(raw)


def _repair_word_per_line(text: str) -> str:
    """Merge PDFs where every word landed on its own line (common Canva/export issue)."""
    lines = [ln.strip() for ln in text.split("\n")]
    if not lines:
        return text

    short_lines = sum(1 for ln in lines if ln and len(ln.split()) <= 2)
    if short_lines / max(len(lines), 1) < 0.55:
        return text

    merged: list[str] = []
    buffer = ""

    def flush():
        nonlocal buffer
        if buffer.strip():
            merged.append(re.sub(r"\s{2,}", " ", buffer.strip()))
        buffer = ""

    bullet_start = re.compile(r"^[\u2022\-\*•●▪◦]\s*")
    section_like = re.compile(
        r"^(work experience|experience|education|skills|projects|summary|objective|"
        r"professional summary|certifications|awards|key competencies)$",
        re.I,
    )

    for line in lines:
        if not line:
            flush()
            continue

        if bullet_start.match(line) or section_like.match(line.rstrip(":")):
            flush()
            merged.append(re.sub(r"\s{2,}", " ", line))
            continue

        if buffer:
            buffer += " " + line
        else:
            buffer = line

    flush()
    return "\n".join(merged)


def _cleanup_pdf_text(text: str, *, preserve_line_spacing: bool = False) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("⋄", " · ")
    if not preserve_line_spacing:
        text = re.sub(r"[ \t]+", " ", text)
    else:
        text = re.sub(r"\t", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return split_merged_lines(text.strip())
