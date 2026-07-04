"""Extract resume sections verbatim from document text — preserve headings and layout."""

from __future__ import annotations

from typing import Optional

from app.services.section_patterns import SECTION_LINE_PATTERNS, match_section_line

REVIEW_SECTIONS = ["summary", "experience", "projects", "skills", "education"]

SECTION_EMPTY_LABELS = {
    "summary": "No summary found in your resume.",
    "experience": "No professional experience found in your resume.",
    "projects": "No projects listed in your resume.",
    "skills": "No skills listed in your resume.",
    "education": "No education listed in your resume.",
}

SECTION_PATTERNS = SECTION_LINE_PATTERNS

HEADER_TO_REVIEW = {
    "summary": "summary",
    "experience": "experience",
    "projects": "projects",
    "skills": "skills",
    "education": "education",
    "certifications": "education",
}


def _is_section_header(line: str) -> Optional[str]:
    key = match_section_line(line)
    if not key:
        return None
    return HEADER_TO_REVIEW.get(key)


def extract_sections_verbatim(text: str) -> dict[str, str]:
    if not text or not text.strip():
        return {}

    lines = text.split("\n")
    headers: list[tuple[int, str]] = []

    for i, line in enumerate(lines):
        key = _is_section_header(line)
        if key:
            headers.append((i, key))

    if not headers:
        return {}

    sections: dict[str, str] = {}

    for idx, (start_line, key) in enumerate(headers):
        end_line = headers[idx + 1][0] if idx + 1 < len(headers) else len(lines)
        block = "\n".join(lines[start_line:end_line]).strip()
        if not block:
            continue
        if key in sections:
            sections[key] = f"{sections[key]}\n\n{block}"
        else:
            sections[key] = block

    return sections


def get_section_verbatim(sections: dict[str, str], section: str) -> str:
    text = sections.get(section, "").strip()
    if text:
        return text
    return SECTION_EMPTY_LABELS.get(section, "")
