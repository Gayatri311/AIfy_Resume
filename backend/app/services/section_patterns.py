"""Shared resume section header patterns."""

from __future__ import annotations

import re
from typing import Optional

# Unambiguous multi-word headers only (avoid matching "Skills" inside "Problem-Solving Skills").
EMBEDDED_SECTION_HEADERS = [
    "KEY ACHIEVEMENTS AND INTERESTS",
    "EDUCATION & CERTIFICATIONS",
    "PROFESSIONAL EXPERIENCE",
    "WORK EXPERIENCE",
    "PROFESSIONAL SUMMARY",
    "KEY COMPETENCIES",
    "CORE COMPETENCIES",
    "TECHNICAL SKILLS",
    "ACHIEVEMENTS AND INTERESTS",
    "ACADEMIC BACKGROUND",
    "LANGUAGES",
]


def split_embedded_section_headers(text: str) -> str:
    """Insert line breaks before section titles glued into paragraph text."""
    result = text
    for header in EMBEDDED_SECTION_HEADERS:
        escaped = re.escape(header)
        result = re.sub(
            rf"(.{{20,}})\s+({escaped})\s+",
            rf"\1\n\2\n",
            result,
            flags=re.I,
        )
    return re.sub(r"\n{3,}", "\n\n", result)


SECTION_LINE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("summary", re.compile(r"^(professional\s+)?(summary|profile|objective|about(\s+me)?)\s*:?\s*$", re.I)),
    (
        "experience",
        re.compile(
            r"^(professional\s+)?((?:work\s+)?experience(?:\s+history)?|employment(?:\s+history)?|work\s+history)\s*:?\s*$",
            re.I,
        ),
    ),
    ("projects", re.compile(r"^((?:personal\s+)?projects|key\s+projects)\s*:?\s*$", re.I)),
    (
        "skills",
        re.compile(
            r"^((?:technical\s+)?skills|core\s+competencies|key\s+competencies|technologies)\s*:?\s*$",
            re.I,
        ),
    ),
    (
        "education",
        re.compile(r"^(education(?:\s*&\s*certifications?)?|academic(?:\s+background)?)\s*:?\s*$", re.I),
    ),
    ("certifications", re.compile(r"^(certifications?|licenses?(?:\s+and\s+certifications?)?)\s*:?\s*$", re.I)),
    ("awards", re.compile(r"^(key\s+achievements(?:\s+and\s+interests)?|achievements?|awards?|honors?)\s*:?\s*$", re.I)),
    ("languages", re.compile(r"^languages\s*:?\s*$", re.I)),
    ("interests", re.compile(r"^interests\s*:?\s*$", re.I)),
]


def match_section_line(line: str) -> Optional[str]:
    clean = line.strip().rstrip(":")
    if not clean:
        return None
    for key, pattern in SECTION_LINE_PATTERNS:
        if pattern.match(clean):
            return key
    return None
