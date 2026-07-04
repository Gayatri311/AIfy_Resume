"""Format structured resume sections as display text and parse them back."""

import re
from app.schemas.resume import ResumeData, ExperienceItem, ProjectItem, EducationItem
from app.services.bullet_utils import (
    is_bullet_line,
    normalize_bullet_list,
    strip_bullet_prefix,
)

DATE_IN_HEADER = re.compile(
    r"(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b|\b\d{4}\b)"
    r"\s*[-–—to]+\s*"
    r"(\b(?:present|current|now)\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b|\b\d{4}\b)",
    re.I,
)


def normalize_resume_data(data: ResumeData) -> ResumeData:
    """Clean bullet lists and drop empty entries after parsing."""
    for exp in data.experience:
        exp.bullets = normalize_bullet_list(exp.bullets)
    for proj in data.projects:
        if proj.description:
            desc_bullets = normalize_bullet_list(
                [strip_bullet_prefix(l) for l in proj.description.split("\n") if l.strip()]
            )
            proj.description = "\n".join(f"• {b}" for b in desc_bullets) if desc_bullets else proj.description
    return data


def format_experience_text(experience: list[ExperienceItem]) -> str:
    if not experience:
        return ""
    blocks: list[str] = []
    for exp in experience:
        lines: list[str] = []
        header = exp.company.strip()
        if exp.start_date or exp.end_date:
            start = exp.start_date or ""
            end = exp.end_date or "Present"
            if start or end:
                header = f"{header} | {start} – {end}".strip(" |")
        if header:
            lines.append(header)
        if exp.title and exp.title not in ("Role", "Company"):
            lines.append(exp.title.strip())
        for bullet in normalize_bullet_list(exp.bullets):
            lines.append(f"• {bullet}")
        if lines:
            blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def format_projects_text(projects: list[ProjectItem]) -> str:
    if not projects:
        return ""
    blocks: list[str] = []
    for proj in projects:
        lines = [proj.title]
        if proj.description:
            for part in normalize_bullet_list(proj.description.split("\n")):
                lines.append(f"• {part}" if not is_bullet_line(part) else f"• {strip_bullet_prefix(part)}")
        if proj.url and proj.url not in (proj.description or ""):
            lines.append(proj.url)
        if proj.tech_stack:
            lines.append(f"Tech: {', '.join(proj.tech_stack)}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _parse_job_header_line(line: str) -> tuple[str, str, str, str]:
    dates = DATE_IN_HEADER.search(line)
    start, end = "", "Present"
    remainder = line

    if dates:
        start = dates.group(1).strip()
        end = dates.group(2).strip()
        remainder = line[: dates.start()] + line[dates.end() :]

    remainder = remainder.replace("|", " — ").strip(" -—–|,")

    company, title = "Company", "Role"
    if " — " in remainder:
        parts = [p.strip() for p in remainder.split(" — ") if p.strip()]
        company = parts[0]
        title = parts[1] if len(parts) > 1 else "Role"
    elif " at " in remainder.lower():
        idx = remainder.lower().index(" at ")
        title = remainder[:idx].strip()
        company = remainder[idx + 4 :].strip()
    elif "," in remainder:
        parts = [p.strip() for p in remainder.split(",", 1)]
        company = parts[0]
        title = parts[1] if len(parts) > 1 else "Role"
    else:
        company = remainder or "Company"

    return company, title, start, end


def _looks_like_job_header(line: str) -> bool:
    if is_bullet_line(line):
        return False
    if DATE_IN_HEADER.search(line):
        return True
    if "|" in line and len(line) < 120:
        return True
    if re.search(r"\b(19|20)\d{2}\b", line) and len(line) < 100:
        return True
    return False


def parse_experience_text(text: str) -> list[ExperienceItem]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    items: list[ExperienceItem] = []

    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue

        company, title, start, end = "Company", "Role", "", "Present"
        body_start = 0

        if _looks_like_job_header(lines[0]):
            company, parsed_title, start, end = _parse_job_header_line(lines[0])
            title = parsed_title
            body_start = 1
            if body_start < len(lines) and not is_bullet_line(lines[body_start]):
                if lines[body_start] not in (title, company) and len(lines[body_start]) < 100:
                    title = lines[body_start]
                    body_start += 1
        else:
            company = lines[0]
            body_start = 1
            if body_start < len(lines) and not is_bullet_line(lines[body_start]):
                title = lines[body_start]
                body_start += 1

        bullets = normalize_bullet_list(
            [strip_bullet_prefix(l) for l in lines[body_start:] if strip_bullet_prefix(l)]
        )

        items.append(
            ExperienceItem(
                company=company,
                title=title,
                start_date=start,
                end_date=end,
                bullets=bullets,
            )
        )

    return items
