"""Build optional resume suggestions (not added to enhanced resume body)."""

from typing import Union

from app.schemas.resume import ResumeData, ResumeSuggestionOut, SuggestedProject, GapAnalysisOut


def _has_real_projects(projects: list) -> bool:
    return any((p.title or "").strip() for p in projects)


def _interview_readiness_steps(original: ResumeData, enhanced: ResumeData) -> list[ResumeSuggestionOut]:
    """Actionable steps so the candidate can actually defend the AI-ready resume in interviews."""
    title = enhanced.personal.title or original.personal.title or "your role"
    steps = [
        ResumeSuggestionOut(
            section="interview_ready",
            title="Build proof for AI claims",
            suggestion=(
                "Ship one small portfolio project this month (RAG chatbot, AI doc assistant, or workflow "
                "automation) and be ready to walk through architecture, prompts used, and limitations."
            ),
            why=(
                "Recruiters will ask for specifics behind AI bullets on your resume. A real demo or GitHub "
                "repo turns positioning into credible interview stories."
            ),
        ),
        ResumeSuggestionOut(
            section="interview_ready",
            title="Prepare 5 STAR stories with metrics",
            suggestion=(
                "Write five Situation–Task–Action–Result stories from your top accomplishments. "
                "Each should include at least one number (%, $, time saved, users impacted)."
            ),
            why=(
                "Behavioral rounds decide many hires. Metrics make your experience memorable and verify "
                "the impact implied on your resume."
            ),
        ),
        ResumeSuggestionOut(
            section="interview_ready",
            title="Practice explaining your AI skills",
            suggestion=(
                "For Prompt Engineering, LLM workflows, and automation on your resume: prepare a 60-second "
                "explanation of a real task you improved, the tool/model used, and what you would do differently."
            ),
            why=(
                "AI keywords get you past ATS; interviewers test whether you can discuss trade-offs, "
                "hallucination risk, and evaluation — not just buzzwords."
            ),
        ),
        ResumeSuggestionOut(
            section="interview_ready",
            title="Run a mock technical screen",
            suggestion=(
                "Schedule 2 mock interviews: one behavioral (leadership, conflict, ownership) and one "
                f"role-specific for {title} (system design, case study, or live problem-solving)."
            ),
            why=(
                "Mock interviews surface gaps before real companies do. Feedback on clarity and depth "
                "is the fastest way to become interview-ready."
            ),
        ),
        ResumeSuggestionOut(
            section="interview_ready",
            title="Research target companies",
            suggestion=(
                "For each company you apply to: read 3 recent job posts, note repeated skills, and tailor "
                "your opening pitch to their product and hiring priorities."
            ),
            why=(
                "Generic applications underperform. Company-specific talking points show preparation "
                "and improve cold outreach response rates."
            ),
        ),
        ResumeSuggestionOut(
            section="interview_ready",
            title="Close with clear next steps",
            suggestion=(
                "End every interview by asking: 'What are the next steps in your process, and is there "
                "anything else I can clarify about my background?' Follow up within 24 hours with a thank-you note."
            ),
            why=(
                "Strong closes signal professionalism and keep you top-of-mind while hiring committees debrief."
            ),
        ),
    ]
    return steps


def build_suggestions(
    original: ResumeData,
    enhanced: ResumeData,
    gaps: Union[GapAnalysisOut, dict],
    suggested_projects: Union[list[SuggestedProject], list[dict]],
    llm_suggestions=None,
) -> list[ResumeSuggestionOut]:
    """Interview-readiness actions + optional section improvements — never injected into enhanced resume."""
    if llm_suggestions is None:
        llm_suggestions = []
    items: list[ResumeSuggestionOut] = []
    seen: set[str] = set()

    def add(section: str, title: str, suggestion: str, why: str) -> None:
        key = f"{section}:{title.lower()[:80]}"
        if key in seen or not suggestion.strip():
            return
        seen.add(key)
        items.append(
            ResumeSuggestionOut(
                section=section,
                title=title.strip(),
                suggestion=suggestion.strip(),
                why=why.strip(),
            )
        )

    for step in _interview_readiness_steps(original, enhanced):
        add(step.section, step.title, step.suggestion, step.why)

    for entry in llm_suggestions or []:
        add(
            entry.get("section", "general"),
            entry.get("title", "Suggestion"),
            entry.get("suggestion") or entry.get("description") or "",
            entry.get("why") or "",
        )

    if not _has_real_projects(original.projects):
        for proj in suggested_projects[:2]:
            title = proj.title if hasattr(proj, "title") else proj.get("title", "")
            desc = proj.business_impact if hasattr(proj, "business_impact") else proj.get("business_impact", "")
            arch = proj.architecture if hasattr(proj, "architecture") else proj.get("architecture", "")
            tech = proj.tech_stack if hasattr(proj, "tech_stack") else proj.get("tech_stack", [])
            suggestion = desc or arch or f"Build a portfolio project using {', '.join(tech[:4])}."
            add(
                "projects",
                title or "Portfolio project",
                suggestion,
                (
                    "Your resume has no projects section. A hands-on build gives interviewers proof "
                    "beyond bullet points — especially for AI-adjacent roles."
                ),
            )

    gap_skills = gaps.missing_skills if hasattr(gaps, "missing_skills") else gaps.get("missing_skills", [])
    for skill in gap_skills[:3]:
        add(
            "skills",
            f"Upskill: {skill}",
            f"Take a short course or complete one tutorial project in {skill}, then add it only if you can demo it.",
            (
                f"{skill} shows up in job descriptions for your target role. Learn enough to discuss it honestly "
                "in interviews before listing it prominently."
            ),
        )

    if not (original.summary or "").strip() and not (enhanced.summary or "").strip():
        add(
            "summary",
            "Add a professional summary",
            "Write 2–3 sentences covering your role, years of experience, and top strengths.",
            "A summary helps recruiters understand your fit in the first few seconds.",
        )

    return items[:14]
