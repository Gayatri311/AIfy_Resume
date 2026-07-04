"""Clean enhanced resume data — preserve bullets; always allow AI project hook."""

from copy import deepcopy

from app.schemas.resume import ResumeData, ProjectItem
from app.agents.project_generator import suggest_ai_project_for_role, _detect_role_key
from app.services.bullet_utils import normalize_bullet_list, split_merged_accomplishments, strip_bullet_prefix


def _is_real_project(title: str, description: str) -> bool:
    t = (title or "").strip().lower()
    d = (description or "").strip()
    if not t or t in ("project", "projects", "untitled"):
        return False
    if not d and t in ("suggested project", "portfolio project"):
        return False
    return True


def ensure_ai_projects(enhanced: ResumeData) -> ResumeData:
    """Ensure the AI-fied resume always includes at least one AI career project."""
    real = [p for p in enhanced.projects if _is_real_project(p.title, p.description)]
    if real:
        enhanced.projects = real
        return enhanced

    primary = suggest_ai_project_for_role(enhanced)
    desc = (primary.description or "").strip()
    if "ai-first" not in desc.lower():
        desc = (
            "Built with an AI-first approach using LLM workflows and intelligent automation. "
            f"{desc}"
        )
    primary.description = desc

    secondary_titles = {
        "engineer": "RAG Knowledge Base Prototype",
        "product": "AI Ops Playbook Generator",
        "analyst": "Automated Insights Dashboard",
        "marketing": "AI Content Pipeline",
        "sales": "Prospect Intelligence Bot",
        "hr": "Candidate Match Assistant",
        "default": "Intelligent Workflow Automation Suite",
    }
    key = _detect_role_key(enhanced.personal.title, enhanced.skills)
    secondary = ProjectItem(
        title=secondary_titles.get(key, secondary_titles["default"]),
        description=(
            "Designed an end-to-end automation combining prompt engineering, API integrations, "
            "and AI-assisted reporting to reduce manual work and improve decision speed."
        ),
        tech_stack=["Python", "LangChain", "OpenAI API"],
        status="AI PROJECT",
    )

    enhanced.projects = [primary, secondary]
    return enhanced


def strip_invented_sections(original: ResumeData, enhanced: ResumeData) -> ResumeData:
    """Drop empty junk projects; keep original projects + AI hook projects."""
    if original.projects:
        orig_titles = {(p.title or "").lower() for p in original.projects if (p.title or "").strip()}
        kept = [
            p for p in enhanced.projects
            if (p.title or "").lower() in orig_titles and _is_real_project(p.title, p.description)
        ]
        enhanced.projects = kept
        enhanced = ensure_project_coverage(original, enhanced)
    else:
        enhanced.projects = [
            p for p in enhanced.projects
            if _is_real_project(p.title, p.description)
        ]

    enhanced.projects = [
        p for p in enhanced.projects
        if _is_real_project(p.title, p.description)
    ]
    return enhanced


def ensure_project_coverage(original: ResumeData, enhanced: ResumeData) -> ResumeData:
    """If original had projects, ensure every original project appears in enhanced (with URLs)."""
    if not original.projects:
        return enhanced

    orig_map = {
        (p.title or "").lower(): p
        for p in original.projects
        if (p.title or "").strip()
    }
    enh_map = {(p.title or "").lower(): p for p in enhanced.projects}

    for title, orig in orig_map.items():
        if title not in enh_map:
            enhanced.projects.append(deepcopy(orig))
            continue
        ep = enh_map[title]
        if orig.url and not ep.url:
            ep.url = orig.url
        if orig.description and not (ep.description or "").strip():
            ep.description = orig.description
        elif orig.url and orig.url not in (ep.description or ""):
            if not ep.url:
                ep.url = orig.url

    return enhanced


def ensure_experience_bullets(original: ResumeData, enhanced: ResumeData) -> ResumeData:
    """Keep accomplishment bullets when LLM rewrite drops or merges them."""
    for job in enhanced.experience:
        job.bullets = _expand_bullets(job.bullets)
        if job.bullets:
            continue

        for orig in original.experience:
            if (
                orig.company.lower() == job.company.lower()
                or (orig.title.lower() == job.title.lower() and orig.company.lower() in job.company.lower())
            ):
                job.bullets = _expand_bullets(orig.bullets)
                break

    return enhanced


def _expand_bullets(bullets: list[str]) -> list[str]:
    expanded: list[str] = []
    for raw in bullets or []:
        text = strip_bullet_prefix((raw or "").strip())
        if not text:
            continue
        parts = normalize_bullet_list([text])
        if len(parts) == 1 and len(parts[0]) > 100:
            parts = split_merged_accomplishments(parts[0])
        for part in parts:
            clean = strip_bullet_prefix(part)
            if clean and clean not in expanded:
                expanded.append(clean)
    return expanded
