import re
from copy import deepcopy
from typing import Optional
from app.schemas.resume import ResumeData, ProjectItem
from app.agents.project_generator import suggest_ai_project_for_role, role_based_skills
from app.agents.resume_quality import assess_resume_quality, is_vague_bullet

NO_CHANGE_NOTE = "\n\n—\nNote: No change required for this section."

MAX_CONTEXTUAL_ENHANCEMENTS = 5
MAX_MODERATE_ENHANCEMENTS = 12

WEAK_OPENERS = re.compile(
    r"^(assisted with|assisted in|helped with|helped|worked on|responsible for|"
    r"duties included|participated in|involved in)\s+",
    re.I,
)

ACTION_VERB_UPGRADES = [
    (re.compile(r"^assisted with\s+", re.I), "Supported "),
    (re.compile(r"^assisted in\s+", re.I), "Contributed to "),
    (re.compile(r"^helped with\s+", re.I), "Partnered on "),
    (re.compile(r"^helped\s+", re.I), "Supported "),
    (re.compile(r"^worked on\s+", re.I), "Delivered "),
    (re.compile(r"^responsible for\s+", re.I), "Owned "),
    (re.compile(r"^participated in\s+", re.I), "Contributed to "),
    (re.compile(r"^involved in\s+", re.I), "Collaborated on "),
]

CONTEXTUAL_REWRITES: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"(document|documentation|wiki|playbook|runbook|onboard|sop)", re.I),
        "{core}, using structured templates so updates stay consistent across the team.",
    ),
    (
        re.compile(r"(report|dashboard|metric|kpi|analytic|insight)", re.I),
        "{core}, standardizing recurring reports to reduce weekly prep time.",
    ),
    (
        re.compile(r"(deploy|ci/?cd|pipeline|release|automation|workflow)", re.I),
        "{core}, reducing manual steps through repeatable workflow improvements.",
    ),
    (
        re.compile(r"(data|database|sql|excel|spreadsheet)", re.I),
        "{core}, applying structured data checks before sharing results with stakeholders.",
    ),
    (
        re.compile(r"(stakeholder|cross-functional|team|communicat|coordination)", re.I),
        "{core}, keeping stakeholders aligned with clear updates and follow-through.",
    ),
    (
        re.compile(r"(customer|client|user|support)", re.I),
        "{core}, prioritizing responsiveness and clear resolution paths.",
    ),
]

MODERN_SKILLS_BY_THEME = {
    "data": ["Data Analysis", "Data-Driven Reporting", "Excel / SQL"],
    "tech": ["Python", "API Integration", "Workflow Automation"],
    "ai": ["Prompt Engineering", "AI-Assisted Productivity", "Process Automation"],
    "collab": ["Cross-functional Collaboration", "Stakeholder Communication", "Process Documentation"],
}


def _infer_title(resume: ResumeData) -> str:
    if resume.personal.title.strip():
        return resume.personal.title.strip()
    for exp in resume.experience:
        if exp.title.strip():
            return exp.title.strip()
    return "Professional"


def _collect_themes(resume: ResumeData) -> list[str]:
    blob = (resume.summary + " " + " ".join(
        b for e in resume.experience for b in e.bullets
    )).lower()
    themes = []
    if any(k in blob for k in ("data", "analyt", "report", "metric", "dashboard")):
        themes.append("data")
    if any(k in blob for k in ("python", "code", "develop", "engineer", "api", "software")):
        themes.append("tech")
    if any(k in blob for k in ("ai", "llm", "automation", "prompt")):
        themes.append("ai")
    if any(k in blob for k in ("team", "stakeholder", "cross", "client", "customer")):
        themes.append("collab")
    return themes or ["collab", "ai"]


def _build_summary_from_resume(resume: ResumeData) -> str:
    title = _infer_title(resume)
    themes = _collect_themes(resume)
    strength_parts = []
    if "data" in themes:
        strength_parts.append("data-informed decision making")
    if "tech" in themes:
        strength_parts.append("technical problem solving")
    if "collab" in themes:
        strength_parts.append("cross-functional delivery")
    if "ai" in themes:
        strength_parts.append("AI-adjacent workflow improvement")
    strengths = ", ".join(strength_parts[:3]) or "reliable execution in fast-paced environments"

    recent = resume.experience[0] if resume.experience else None
    context = ""
    if recent and recent.company:
        context = f" with recent experience at {recent.company}"

    return (
        f"{title}{context}. Brings hands-on experience across {len(resume.experience)} professional role(s), "
        f"with strengths in {strengths}."
    )


def _expand_bullet_aggressive(bullet: str, exp) -> str:
    """Turn thin/vague bullets into clearer achievement statements."""
    core = _core_phrase(bullet)

    for pattern, template in CONTEXTUAL_REWRITES:
        if pattern.search(bullet):
            enhanced = template.format(core=core)
            enhanced = _capitalize_first(enhanced)
            if not enhanced.endswith("."):
                enhanced += "."
            if enhanced.rstrip(".") != bullet.strip().rstrip("."):
                return enhanced

    polished = _light_polish(bullet)
    if polished.rstrip(".") != bullet.strip().rstrip("."):
        return polished

    return _capitalize_first(core) + "."


def _capitalize_first(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def _light_polish(bullet: str) -> str:
    text = bullet.strip().rstrip(".")
    if not text:
        return bullet

    for pattern, replacement in ACTION_VERB_UPGRADES:
        if pattern.match(text):
            text = pattern.sub(replacement, text, count=1)
            break
    else:
        cleaned = WEAK_OPENERS.sub("", text).strip()
        if cleaned:
            text = cleaned

    text = _capitalize_first(text)
    if not text.endswith("."):
        text += "."

    if text.rstrip(".") == bullet.strip().rstrip("."):
        return bullet
    return text


def _core_phrase(bullet: str) -> str:
    text = WEAK_OPENERS.sub("", bullet.strip()).rstrip(".")
    text = _capitalize_first(text)
    return text[0].lower() + text[1:] if len(text) > 1 else text


def _contextual_rewrite(bullet: str, used_themes: set) -> Optional[tuple]:
    core = _core_phrase(bullet)
    for idx, (pattern, template) in enumerate(CONTEXTUAL_REWRITES):
        if idx in used_themes:
            continue
        if pattern.search(bullet):
            enhanced = template.format(core=core)
            enhanced = _capitalize_first(enhanced)
            if not enhanced.endswith("."):
                enhanced += "."
            if enhanced.rstrip(".") == bullet.strip().rstrip("."):
                continue
            return enhanced, {
                "section": "experience",
                "why": (
                    "Strengthened this bullet with clearer action language and a practical outcome "
                    "that still reflects your original work."
                ),
                "confidence": 88,
                "authenticity": "SAFE",
                "interview_risk": "LOW",
            }, idx
    return None


def _enhance_summary(summary: str, title: str, *, rebuild: bool = False, resume: Optional[ResumeData] = None) -> tuple[str, Optional[dict]]:
    if rebuild and resume is not None:
        new_summary = _build_summary_from_resume(resume)
        if new_summary.rstrip(".") != summary.strip().rstrip("."):
            return new_summary, {
                "section": "summary",
                "why": (
                    "Your resume lacked a strong professional summary — wrote one from your experience "
                    "to position you clearly for recruiters and ATS."
                ),
                "confidence": 85,
                "authenticity": "SAFE",
                "interview_risk": "LOW",
            }
        return summary, None

    if not summary.strip():
        if resume is not None:
            return _enhance_summary("", title, rebuild=True, resume=resume)
        return summary, None

    text = summary.strip()
    if rebuild or len(text.split()) < 25:
        polished = _light_polish(text.replace("\n", " "))
        role = title or _infer_title(resume) if resume else title
        if role and len(polished.split()) < 20:
            hook = f"{role} with a track record of "
            if not polished.lower().startswith(role.lower()[:6]):
                polished = hook + polished[0].lower() + polished[1:]
        if polished.rstrip(".") != text.rstrip("."):
            return polished, {
                "section": "summary",
                "why": "Rewrote a thin or generic summary into a clear, role-focused statement.",
                "confidence": 88,
                "authenticity": "SAFE",
                "interview_risk": "LOW",
            }

    polished = _light_polish(text.replace("\n", " "))
    if len(polished.split()) < 12 and title:
        role_hook = f"{title.strip()} focused on "
        if not polished.lower().startswith(title.lower()[:8]):
            polished = role_hook + polished[0].lower() + polished[1:] if polished else polished

    if polished.rstrip(".") != text.rstrip("."):
        return polished, {
            "section": "summary",
            "why": "Tightened your summary with clearer role positioning and stronger opening language.",
            "confidence": 90,
            "authenticity": "SAFE",
            "interview_risk": "LOW",
        }
    return text, None


def _enhance_project_descriptions(projects: list) -> tuple[list, list]:
    changes = []
    enhanced = []
    for p in projects:
        desc = (p.description or "").strip()
        if desc and len(desc.split()) < 8:
            new_desc = desc.rstrip(".") + ", delivering measurable value for the team."
            enhanced.append(type(p)(**{**p.model_dump(), "description": new_desc}))
            changes.append({
                "section": "projects",
                "why": "Expanded a brief project description so recruiters understand scope and impact.",
                "confidence": 85,
                "authenticity": "SAFE",
                "interview_risk": "LOW",
            })
        else:
            enhanced.append(p)
    return enhanced, changes


def _append_modern_skills(resume: ResumeData, merged: list[str], *, aggressive: bool = False) -> tuple[list[str], bool]:
    themes = _collect_themes(resume)
    candidates = list(role_based_skills(resume))
    for theme in themes:
        candidates.extend(MODERN_SKILLS_BY_THEME.get(theme, []))
    if aggressive:
        candidates.extend(["Process Documentation", "Cross-functional Communication"])

    existing = {s.lower() for s in merged}
    added = False
    limit = 4 if aggressive else 3
    for skill in candidates:
        if len([s for s in merged if s not in resume.skills]) >= limit:
            break
        if skill.lower() not in existing:
            merged.append(skill)
            existing.add(skill.lower())
            added = True
    return merged, added


def _enhance_experience_bullets(
    original: ResumeData,
    enhanced: ResumeData,
    *,
    rebuild: bool = False,
    max_changes: int = MAX_CONTEXTUAL_ENHANCEMENTS,
) -> list[dict]:
    all_changes: list[dict] = []
    used_themes: set = set()
    changes_left = max_changes if not rebuild else 999

    for exp_orig, exp_enh in zip(original.experience, enhanced.experience):
        new_bullets = []
        for bullet in exp_orig.bullets:
            result = bullet
            applied = False

            if rebuild or is_vague_bullet(bullet):
                expanded = _expand_bullet_aggressive(bullet, exp_orig)
                if expanded.rstrip(".") != bullet.strip().rstrip("."):
                    result = expanded
                    all_changes.append({
                        "section": "experience",
                        "why": (
                            "Rebuilt a weak or vague bullet into a clear achievement statement with "
                            "stronger action language and modern workflow impact."
                        ),
                        "confidence": 86,
                        "authenticity": "SAFE" if is_vague_bullet(bullet) else "STRETCH",
                        "interview_risk": "LOW" if is_vague_bullet(bullet) else "MEDIUM",
                    })
                    applied = True

            if not applied and changes_left > 0:
                rewrite = _contextual_rewrite(bullet, used_themes)
                if rewrite:
                    result, change, theme_idx = rewrite
                    used_themes.add(theme_idx)
                    changes_left -= 1
                    all_changes.append(change)
                    applied = True

            if not applied:
                polished = _light_polish(bullet)
                if polished != bullet:
                    result = polished
                    all_changes.append({
                        "section": "experience",
                        "why": "Upgraded weak phrasing to a stronger action verb while keeping your accomplishment intact.",
                        "confidence": 92,
                        "authenticity": "SAFE",
                        "interview_risk": "LOW",
                    })

            new_bullets.append(result)
        exp_enh.bullets = new_bullets

    return all_changes


def enhance_resume(original: ResumeData) -> tuple[ResumeData, list]:
    """Rule-based enhancements when LLM unavailable — scales effort to resume quality."""
    quality = assess_resume_quality(original)
    tier = quality["tier"]
    enhanced = deepcopy(original)
    all_changes: list[dict] = []
    rebuild = tier == "weak"
    moderate = tier == "moderate"

    title = _infer_title(original)
    new_summary, summary_change = _enhance_summary(
        original.summary,
        title,
        rebuild=rebuild or moderate,
        resume=original,
    )
    enhanced.summary = new_summary
    if summary_change:
        all_changes.append(summary_change)

    max_bullet_changes = 999 if rebuild else (MAX_MODERATE_ENHANCEMENTS if moderate else MAX_CONTEXTUAL_ENHANCEMENTS)
    all_changes.extend(_enhance_experience_bullets(
        original, enhanced, rebuild=rebuild, max_changes=max_bullet_changes
    ))

    enhanced.projects, proj_changes = _enhance_project_descriptions(enhanced.projects)
    all_changes.extend(proj_changes)

    merged = list(original.skills)
    merged, added_any = _append_modern_skills(original, merged, aggressive=rebuild or moderate)
    enhanced.skills = merged

    if added_any:
        all_changes.append({
            "section": "skills",
            "why": (
                "Expanded your skills section with modern, role-relevant capabilities including "
                "AI-adjacent skills your resume was missing for ATS and recruiter screening."
            ),
            "confidence": 90,
            "authenticity": "SAFE",
            "interview_risk": "LOW",
        })

    return enhanced, all_changes
