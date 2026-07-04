import re
from copy import deepcopy
from app.schemas.resume import ResumeData, ProjectItem, EducationItem
from app.services.resume_format import parse_experience_text

NO_CHANGE_NOTE = "\n\n—\nNote: No change required for this section."
EMPTY_LABELS = {
    "summary": "No summary found in your resume.",
    "experience": "No professional experience found in your resume.",
    "projects": "No projects listed in your resume.",
    "skills": "No skills listed in your resume.",
    "education": "No education listed in your resume.",
}


def strip_no_change_note(text: str) -> str:
    if NO_CHANGE_NOTE in text:
        return text.replace(NO_CHANGE_NOTE, "").strip()
    return text.strip()


def _is_empty_placeholder(text: str, section: str) -> bool:
    return text.strip() == EMPTY_LABELS.get(section, "")


def apply_section_text(data: ResumeData, section: str, text: str) -> ResumeData:
    """Merge accepted section text back into structured resume data."""
    updated = deepcopy(data)
    clean = strip_no_change_note(text)

    if section == "summary":
        if not _is_empty_placeholder(clean, "summary"):
            updated.summary = clean
        return updated

    if section == "experience":
        if _is_empty_placeholder(clean, "experience"):
            return updated
        updated.experience = parse_experience_text(clean)
        return updated

    if section == "projects":
        if _is_empty_placeholder(clean, "projects"):
            updated.projects = []
            return updated
        updated.projects = _parse_projects_text(clean)
        return updated

    if section == "skills":
        if _is_empty_placeholder(clean, "skills"):
            updated.skills = []
            return updated
        updated.skills = [s.strip() for s in re.split(r"[,•|]", clean) if s.strip()]
        return updated

    if section == "education":
        if _is_empty_placeholder(clean, "education"):
            updated.education = []
            return updated
        updated.education = _parse_education_text(clean)
        return updated

    return updated


def _parse_projects_text(text: str) -> list[ProjectItem]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    projects: list[ProjectItem] = []

    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        title = lines[0]
        description = ""
        tech_stack: list[str] = []
        for line in lines[1:]:
            if line.lower().startswith("tech:"):
                tech_stack = [t.strip() for t in line[5:].split(",") if t.strip()]
            else:
                description += (" " if description else "") + line
        projects.append(
            ProjectItem(title=title, description=description.strip(), tech_stack=tech_stack)
        )

    return projects


def _parse_education_text(text: str) -> list[EducationItem]:
    items: list[EducationItem] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        year_match = re.search(r",\s*((?:19|20)\d{2})\s*$", line)
        year = year_match.group(1) if year_match else ""
        core = line[: year_match.start()] if year_match else line
        if " — " in core:
            degree, institution = core.split(" — ", 1)
        elif ", " in core:
            parts = core.split(", ", 1)
            degree, institution = parts[0], parts[1] if len(parts) > 1 else ""
        else:
            degree, institution = "", core
        items.append(
            EducationItem(
                degree=degree.strip(),
                institution=institution.strip(),
                year=year,
            )
        )
    return items
