from app.schemas.resume import ResumeData, SectionDiff, NextAction, ChangeExplanation
from typing import Optional
from app.services.parser import parse_resume_text, extract_text
from app.services.resume_validator import validate_resume_text
from app.services.llm_client import llm_available
from app.agents.ats_analyzer import analyze_ats
from app.agents.experience_enhancer import enhance_resume, NO_CHANGE_NOTE
from app.agents.llm_enhancer import enhance_resume_with_llm
from app.agents.authenticity_validator import filter_enhancements
from app.agents.readiness_scorer import calculate_ai_readiness
from app.agents.gap_analyzer import analyze_gaps
from app.agents.project_generator import generate_projects
from app.agents.interview_generator import generate_interview_questions

PROCESSING_STEPS = [
    "Reading Resume",
    "Understanding Career Journey",
    "Identifying Transferable Skills",
    "Detecting Automation Opportunities",
    "Calculating ATS Score",
    "Finding AI Opportunities",
    "Building AI Career Narrative",
    "Creating Interview Preparation Plan",
]

from app.services.section_extractor import (
    REVIEW_SECTIONS,
    SECTION_EMPTY_LABELS,
    extract_sections_verbatim,
    get_section_verbatim,
)
from app.services.resume_format import (
    format_experience_text,
    format_projects_text,
    normalize_resume_data,
)
from app.services.resume_cleanup import strip_invented_sections, ensure_project_coverage, ensure_experience_bullets, ensure_ai_projects
from app.services.link_preservation import preserve_links
from app.services.ai_career_hook import apply_ai_career_hook
from app.services.suggestion_builder import build_suggestions
from app.services.company_outreach import generate_company_outreach
from app.services.keyword_highlights import build_highlight_keywords

NO_CHANGE_EXPLANATION = ChangeExplanation(
    why="This section already reads clearly for ATS and recruiters. No edits were needed.",
    confidence=98,
    authenticity="SAFE",
    interview_risk="LOW",
)


def _section_text_summary(data: ResumeData) -> str:
    return (data.summary or "").strip()


def _section_text_experience(data: ResumeData) -> str:
    return format_experience_text(data.experience)


def _section_text_projects(data: ResumeData) -> str:
    return format_projects_text(data.projects)


def _section_text_skills(data: ResumeData) -> str:
    return ", ".join(data.skills) if data.skills else ""


def _section_text_education(data: ResumeData) -> str:
    if not data.education:
        return ""
    lines = []
    for e in data.education:
        if e.degree and e.institution:
            line = f"{e.degree} — {e.institution}"
        else:
            line = e.degree or e.institution
        if e.year:
            line += f", {e.year}"
        lines.append(line)
    return "\n".join(lines).strip()


SECTION_BUILDERS = {
    "summary": _section_text_summary,
    "experience": _section_text_experience,
    "projects": _section_text_projects,
    "skills": _section_text_skills,
    "education": _section_text_education,
}


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _changes_for_section(section: str, all_changes: list) -> list[ChangeExplanation]:
    matched = []
    for c in all_changes:
        if c.get("section") == section:
            matched.append(ChangeExplanation(
                why=c.get("why", ""),
                confidence=float(c.get("confidence", 85)),
                authenticity=c.get("authenticity", "SAFE"),
                interview_risk=c.get("interview_risk", "LOW"),
            ))

    if matched:
        return matched[:5]

    keywords = {
        "summary": ("summary", "wording", "role", "profile", "strategy", "positioning"),
        "experience": ("bullet", "experience", "accomplishment", "rewrote", "verb", "phrasing"),
        "projects": ("project", "starter", "description"),
        "skills": ("skill", "complementary", "appended"),
        "education": ("education",),
    }
    keys = keywords.get(section, ())
    for c in all_changes:
        why = c.get("why", "").lower()
        if any(k in why for k in keys):
            matched.append(ChangeExplanation(**{
                "why": c.get("why", ""),
                "confidence": float(c.get("confidence", 85)),
                "authenticity": c.get("authenticity", "SAFE"),
                "interview_risk": c.get("interview_risk", "LOW"),
            }))
    return matched[:5]


def build_diffs(
    original: ResumeData,
    enhanced: ResumeData,
    changes: list,
    original_sections: Optional[dict] = None,
) -> list[SectionDiff]:
    diffs = []
    verbatim = original_sections or {}

    for section in REVIEW_SECTIONS:
        builder = SECTION_BUILDERS[section]
        orig_text = get_section_verbatim(verbatim, section)
        if orig_text in SECTION_EMPTY_LABELS.values():
            fallback = builder(original)
            if fallback:
                orig_text = fallback

        enh_text = builder(enhanced)

        if section == "projects" and not enhanced.projects:
            continue

        section_changes = _changes_for_section(section, changes)
        unchanged = _normalize(orig_text) == _normalize(enh_text) or not enh_text

        if unchanged:
            enhanced_display = orig_text.rstrip() + NO_CHANGE_NOTE
            diff_changes = [NO_CHANGE_EXPLANATION]
        else:
            enhanced_display = enh_text if enh_text else orig_text
            diff_changes = section_changes if section_changes else [
                ChangeExplanation(
                    why="Targeted improvements applied while keeping your original content intact.",
                    confidence=90,
                    authenticity="SAFE",
                    interview_risk="LOW",
                )
            ]

        diffs.append(SectionDiff(
            section=section,
            original=orig_text,
            enhanced=enhanced_display,
            changes=diff_changes,
            no_change_required=unchanged,
        ))

    return diffs


def run_pipeline(file_path: str) -> dict:
    text = extract_text(file_path)
    original_sections = extract_sections_verbatim(text)
    original = parse_resume_text(text)
    validate_resume_text(text, original)

    llm_suggestions: list = []
    if llm_available():
        enhanced, changes, llm_suggestions = enhance_resume_with_llm(original, text)
    else:
        enhanced, changes = enhance_resume(original)

    enhanced, changes = filter_enhancements(original, enhanced, changes)
    enhanced = strip_invented_sections(original, enhanced)
    enhanced = ensure_experience_bullets(original, enhanced)
    original = normalize_resume_data(original)
    enhanced = normalize_resume_data(enhanced)
    enhanced = preserve_links(original, enhanced, text)
    enhanced = ensure_project_coverage(original, enhanced)
    enhanced = ensure_ai_projects(enhanced)
    enhanced = apply_ai_career_hook(original, enhanced)

    ats_result = analyze_ats(original)
    scores = calculate_ai_readiness(enhanced, ats_result["ats_score"])
    gaps = analyze_gaps(enhanced)
    projects = generate_projects(original)
    questions = generate_interview_questions(enhanced)
    diffs = build_diffs(original, enhanced, changes, original_sections)
    suggestions = build_suggestions(original, enhanced, gaps, projects, llm_suggestions)
    outreach = generate_company_outreach(enhanced)
    highlight_keywords = build_highlight_keywords(enhanced, ats_result.get("missing_keywords", []))

    next_actions = [
        NextAction(
            title="Build an AI Documentation Assistant using RAG",
            description="Create a hands-on project to prove your AI workflow claims with technical evidence.",
            type="project",
        ),
        NextAction(
            title="Complete Prompt Engineering certification",
            description="Strengthen credibility for LLM-related resume claims with recognized credentials.",
            type="certification",
        ),
        NextAction(
            title="Learn LangChain basics",
            description="Foundation for building AI agents and RAG pipelines mentioned in your enhanced resume.",
            type="learning",
        ),
    ]

    return {
        "original": original.model_dump(),
        "enhanced": enhanced.model_dump(),
        "original_sections": original_sections,
        "diffs": [d.model_dump() for d in diffs],
        "scores": scores,
        "gap_analysis": gaps,
        "suggested_projects": projects,
        "interview_questions": questions,
        "next_actions": [a.model_dump() for a in next_actions],
        "suggestions": [s.model_dump() for s in suggestions],
        "outreach": outreach.model_dump(),
        "highlight_keywords": highlight_keywords,
        "ats_issues": ats_result["issues"],
        "missing_keywords": ats_result["missing_keywords"],
        "confidence_strengths": [
            {"label": "AI-assisted documentation", "level": "STRONG"},
            {"label": "Prompt Engineering", "level": "STRONG"},
            {"label": "Predictive Ops", "level": "GOOD"},
        ],
        "experience_gaps": [
            {"label": "AI Agent Frameworks", "level": "MISSING"},
            {"label": "Workflow Automation", "level": "WEAK"},
            {"label": "Model Fine-tuning", "level": "GAP"},
        ],
    }
