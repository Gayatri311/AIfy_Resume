"""Merge wrapped lines and normalize extracted resume text before parsing."""

from __future__ import annotations

import re
from typing import Callable, Optional

from app.services.bullet_utils import is_bullet_line, strip_bullet_prefix
from app.services.section_patterns import split_embedded_section_headers, match_section_line

SECTION_LIKE = re.compile(
    r"^(professional\s+)?(summary|profile|objective|about(\s+me)?|"
    r"(work\s+)?experience(\s+history)?|employment(\s+history)?|work\s+history|"
    r"education(?:\s*&\s*certifications?)?|skills|key\s+competencies|projects|"
    r"certifications?|awards?|honors?|key\s+achievements(?:\s+and\s+interests)?|"
    r"technical\s+skills|core\s+competencies|languages|interests)(:?\s*)?$",
    re.I,
)

DATE_HINT = re.compile(
    r"(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b|"
    r"\b\d{1,2}/\d{4}\b|\b\d{4}\b)\s*[-–—to]+\s*"
    r"(\b(?:present|current|now)\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b|"
    r"\b\d{1,2}/\d{4}\b|\b\d{4}\b)",
    re.I,
)

# Split accomplishment sentences when PDF merged bullets into one paragraph.
ACCOMPLISHMENT_SPLIT = re.compile(
    r"(?<=[.;])\s+(?=(?:"
    r"Designed|Developed|Delivered|Built|Created|Implemented|Integrated|Managed|Led|"
    r"Configured|Applied|Enhanced|Contributed|Worked|Supported|Collaborated|Recognized|"
    r"Fine-tuned|Optimized|Mentored|Reduced|Automated|Streamlined|Established|"
    r"Executed|Improved|Maintained|Partnered|Spearheaded|Architected|Deployed|"
    r"Utilized|Leveraged|Oversaw|Coordinated|Facilitated|Analyzed|Researched|"
    r"Presented|Trained|Supervised|Directed|Owned|Drove|Achieved|Increased|Decreased"
    r")\b)",
    re.I,
)

EMAIL_INLINE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_INLINE = re.compile(r"\+?\d[\d\s().\-]{8,}\d")


def _looks_like_section(line: str) -> bool:
    clean = line.strip().rstrip(":")
    return bool(SECTION_LIKE.match(clean)) or match_section_line(clean) is not None


def _looks_like_job_header(line: str) -> bool:
    if is_bullet_line(line):
        return False
    if DATE_HINT.search(line):
        return True
    if "|" in line and len(line) < 140:
        return True
    if re.search(r"\b(19|20)\d{2}\b", line) and len(line) < 120:
        return True
    return False


def _join_fragments(base: str, nxt: str) -> str:
    base = base.rstrip()
    nxt = nxt.lstrip()
    if base.endswith("-"):
        return base[:-1] + nxt
    return f"{base} {nxt}"


CONTINUATION_START = re.compile(
    r"^(?:and|or|with|for|to|in|of|on|via|using|including|while|as|through|across|"
    r"among|within|without|such|that|which|where|when|by|from|into|onto|upon|"
    r"between|during|after|before|because|although|though|if|but|nor|yet|so)\b",
    re.I,
)


def is_wrap_continuation(base: str, nxt: str) -> bool:
    """True when nxt is a PDF line-wrap continuation of base, not a new bullet."""
    base = base.rstrip()
    nxt = nxt.strip()
    if not base or not nxt:
        return False
    if is_bullet_line(nxt) or _looks_like_section(nxt) or _looks_like_job_header(nxt):
        return False
    if nxt[0].islower():
        return True
    if CONTINUATION_START.match(nxt):
        return True
    if base.endswith((",", "-", "(", ";", ":", "/")):
        return True
    return False


def split_merged_lines(text: str) -> str:
    """Split lines glued together by PDF extraction."""
    text = split_embedded_section_headers(text)
    lines: list[str] = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            lines.append("")
            continue

        if len(line) > 180 and ACCOMPLISHMENT_SPLIT.search(line):
            if _looks_like_job_with_body(line):
                lines.append(line)
                continue
            for chunk in ACCOMPLISHMENT_SPLIT.split(line):
                chunk = chunk.strip()
                if chunk:
                    lines.append(f"• {chunk}" if not is_bullet_line(chunk) else chunk)
            continue

        lines.append(line)

    return "\n".join(lines)


def _looks_like_job_with_body(line: str) -> bool:
    return bool(
        re.match(
            r"^.+?\b(?:Engineer|Developer|Manager|Analyst|Intern|Lead|Architect|Consultant|"
            r"Specialist|Associate|Director|Coordinator|Designer|Administrator|Scientist)\s+"
            r"(?:Designed|Developed|Built|Created|Implemented|Managed|Led|Delivered)",
            line,
            re.I,
        )
    )


def join_wrapped_lines(
    lines: list[str],
    *,
    is_section: Optional[Callable[[str], bool]] = None,
) -> list[str]:
    """Turn PDF line wraps into one line per bullet, paragraph, or header."""
    section_check = is_section or _looks_like_section
    result: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue

        if section_check(line):
            result.append(line.rstrip(":"))
            continue

        if is_bullet_line(line):
            bullet = strip_bullet_prefix(line)
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt:
                    i += 1
                    break
                if is_bullet_line(nxt) or section_check(nxt) or _looks_like_job_header(nxt):
                    break
                if len(nxt) < 60 or is_wrap_continuation(bullet, nxt):
                    bullet = _join_fragments(bullet, nxt)
                    i += 1
                    continue
                break
            result.append(f"• {bullet.strip()}")
            continue

        if _looks_like_job_header(line):
            result.append(line.strip())
            continue

        para = line
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                i += 1
                break
            if is_bullet_line(nxt) or section_check(nxt) or _looks_like_job_header(nxt):
                break
            if len(nxt) >= 60 and not is_wrap_continuation(para, nxt):
                break
            para = _join_fragments(para, nxt)
            i += 1
        result.append(para.strip())

    return result


def split_name_contact_line(line: str) -> tuple[str, str]:
    """Pull email/phone out of a name line merged by PDF extraction."""
    email = EMAIL_INLINE.search(line)
    phone = PHONE_INLINE.search(line)

    name = line
    contact_bits: list[str] = []
    if email:
        contact_bits.append(email.group(0))
        name = name.replace(email.group(0), " ")
    if phone:
        contact_bits.append(phone.group(0))
        name = name.replace(phone.group(0), " ")

    name = re.sub(r"\s{2,}", " ", name).strip(" ,-|")
    return name, " ".join(contact_bits)


def preprocess_resume_text(text: str) -> list[str]:
    """Full pre-parse cleanup pipeline for raw extracted text."""
    text = split_merged_lines(text)
    raw_lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    return join_wrapped_lines(raw_lines)
