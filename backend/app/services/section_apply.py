from copy import deepcopy
from app.schemas.resume import ResumeData


def apply_section_from_source(
    accepted: ResumeData,
    source: ResumeData,
    section: str,
) -> ResumeData:
    """Copy one section from source (suggested or original) into accepted resume."""
    updated = deepcopy(accepted)

    if section == "summary":
        updated.summary = source.summary
    elif section == "experience":
        updated.experience = deepcopy(source.experience)
    elif section == "projects":
        updated.projects = deepcopy(source.projects)
    elif section == "skills":
        updated.skills = list(source.skills)
    elif section == "education":
        updated.education = deepcopy(source.education)

    return updated


def apply_accept(
    accepted: ResumeData,
    original: ResumeData,
    suggested: ResumeData,
    section: str,
    accepted_flag: bool,
) -> ResumeData:
    """Accept uses suggested section; reject restores original section."""
    source = suggested if accepted_flag else original
    return apply_section_from_source(accepted, source, section)
