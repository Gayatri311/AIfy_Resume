"""Assemble and split full resume documents for side-by-side review."""

from __future__ import annotations

from app.schemas.resume import PersonalDetails, ResumeData, SectionDiff
from app.services.section_extractor import REVIEW_SECTIONS, SECTION_EMPTY_LABELS, extract_sections_verbatim
from app.services.section_sync import strip_no_change_note, EMPTY_LABELS

DEFAULT_HEADINGS = {
    "summary": "Professional Summary",
    "experience": "Professional Experience",
    "projects": "Projects",
    "skills": "Skills",
    "education": "Education",
}


def format_personal_header(personal: PersonalDetails) -> str:
    lines: list[str] = []
    if personal.name:
        lines.append(personal.name.strip())
    if personal.title:
        lines.append(personal.title.strip())

    contacts: list[str] = []
    if personal.phone:
        contacts.append(personal.phone.strip())
    if personal.email:
        contacts.append(personal.email.strip())
    if personal.location:
        contacts.append(personal.location.strip())
    if personal.linkedin:
        contacts.append(personal.linkedin.strip())
    if personal.github:
        contacts.append(personal.github.strip())
    if personal.website:
        contacts.append(personal.website.strip())

    if contacts:
        lines.append(" | ".join(contacts))
    return "\n".join(lines)


def _is_empty_section(text: str, section: str) -> bool:
    clean = (text or "").strip()
    if not clean:
        return True
    return clean in (SECTION_EMPTY_LABELS.get(section, ""), EMPTY_LABELS.get(section, ""))


def _section_heading(original: str, section: str) -> str:
    if original and not _is_empty_section(original, section):
        first = original.split("\n", 1)[0].strip()
        if first:
            return first
    return DEFAULT_HEADINGS.get(section, section.title())


def _format_section_block(original: str, enhanced: str, section: str) -> str:
    body = strip_no_change_note(enhanced).strip()
    if not body or _is_empty_section(body, section):
        return ""

    heading = _section_heading(original, section)
    first_body_line = body.split("\n", 1)[0].strip().lower()
    if first_body_line == heading.lower():
        return body
    return f"{heading}\n{body}"


def build_full_original(personal: PersonalDetails, diffs: list[SectionDiff]) -> str:
    parts: list[str] = []
    header = format_personal_header(personal)
    if header:
        parts.append(header)

    for section in REVIEW_SECTIONS:
        diff = next((d for d in diffs if d.section == section), None)
        if not diff:
            continue
        original = (diff.original or "").strip()
        if not original or _is_empty_section(original, section):
            continue
        parts.append(original)

    return "\n\n".join(parts)


def build_full_enhanced(personal: PersonalDetails, diffs: list[SectionDiff]) -> str:
    parts: list[str] = []
    header = format_personal_header(personal)
    if header:
        parts.append(header)

    for section in REVIEW_SECTIONS:
        diff = next((d for d in diffs if d.section == section), None)
        if not diff:
            continue
        block = _format_section_block(diff.original or "", diff.enhanced or "", section)
        if block:
            parts.append(block)

    return "\n\n".join(parts)


def split_document_sections(text: str) -> dict[str, str]:
    """Split edited full resume text back into review sections."""
    sections = extract_sections_verbatim(text)
    return {key: value for key, value in sections.items() if key in REVIEW_SECTIONS}


def section_body_for_apply(section: str, block: str) -> str:
    """Strip section heading line before parsing section text into structured data."""
    lines = [line for line in block.strip().split("\n")]
    if not lines:
        return ""

    from app.services.section_extractor import _is_section_header

    if _is_section_header(lines[0]) == section:
        body = "\n".join(lines[1:]).strip()
        return body or lines[0].strip()
    return block.strip()


def apply_document_to_resume(
    data: ResumeData,
    diffs: list,
    full_text: str,
) -> tuple[ResumeData, dict[str, str]]:
    """
    Parse full enhanced document text into structured resume data and per-section blocks.
    Returns updated ResumeData and section blocks (with headings) for diff storage.
    """
    from app.services.section_sync import apply_section_text

    sections = split_document_sections(full_text)
    if not sections:
        raise ValueError(
            "Could not detect resume sections. Keep headings like Summary, Experience, Skills, and Education."
        )

    updated = data
    stored_blocks: dict[str, str] = {}

    for section in REVIEW_SECTIONS:
        if section not in sections:
            continue
        block = sections[section].strip()
        stored_blocks[section] = block
        body = section_body_for_apply(section, block)
        updated = apply_section_text(updated, section, body)

    return updated, stored_blocks
