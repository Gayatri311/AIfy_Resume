"""Product hook: position the enhanced resume as AI-career-ready (marketing layer on top of real content)."""

import re
from copy import deepcopy

from app.schemas.resume import ResumeData

AI_SKILLS = [
    "Prompt Engineering",
    "AI-Assisted Workflows",
    "LLM Integration",
    "Workflow Automation",
    "Generative AI Tools",
]

AI_KEYWORDS = ("ai", "llm", "prompt", "rag", "machine learning", "automation", "genai", "copilot")


def _has_ai_signal(text: str) -> bool:
    lower = (text or "").lower()
    return any(k in lower for k in AI_KEYWORDS)


def _skill_present(skills: list[str], needle: str) -> bool:
    n = needle.lower()
    return any(n in s.lower() for s in skills)


def _infer_task(bullet: str) -> str:
    cleaned = re.sub(r"^[\-•*]\s*", "", (bullet or "").strip())
    cleaned = re.sub(
        r"(?i)^(led|managed|developed|built|created|implemented|designed|drove|owned|supported|delivered)\s+",
        "",
        cleaned,
    )
    words = cleaned.split()[:6]
    task = " ".join(words).rstrip(".,;")
    return task or "day-to-day deliverables"


def apply_ai_career_hook(original: ResumeData, enhanced: ResumeData) -> ResumeData:
    """Layer AI-career positioning onto the enhanced resume without removing original content."""
    out = deepcopy(enhanced)
    title = (out.personal.title or original.personal.title or "Professional").strip()

    if not _has_ai_signal(out.summary):
        if (out.summary or "").strip():
            out.summary = (
                f"{out.summary.rstrip()} "
                "Focused on applying AI-assisted workflows, prompt engineering, and automation "
                "to accelerate delivery and improve cross-functional outcomes."
            )
        else:
            out.summary = (
                f"Results-oriented {title} with a track record of measurable impact. "
                "Experienced in leveraging generative AI tools, LLM workflows, and intelligent automation "
                "to modernize processes and support data-driven decision making."
            )

    added_skills = 0
    for skill in AI_SKILLS:
        if added_skills >= 4:
            break
        if not _skill_present(out.skills, skill):
            out.skills.append(skill)
            added_skills += 1

    for job in out.experience[:4]:
        blob = " ".join(job.bullets or [])
        if _has_ai_signal(blob):
            continue
        if not job.bullets:
            continue
        task = _infer_task(job.bullets[0])
        job.bullets.append(
            f"Leveraged AI-assisted tooling and prompt-engineering patterns to streamline {task}, "
            "improving team velocity and output quality."
        )
        if len(job.bullets) < 5:
            job.bullets.append(
                "Explored LLM-based automation for documentation, analysis, and stakeholder reporting."
            )

    if out.projects:
        for proj in out.projects[:3]:
            if not _has_ai_signal(proj.description):
                prefix = (proj.description or "").strip()
                hook = (
                    "Built with an AI-first approach using LLM workflows and intelligent automation. "
                )
                proj.description = f"{hook}{prefix}" if prefix else hook.rstrip()

    if out.personal.title and not _has_ai_signal(out.personal.title):
        if not any(c in out.personal.title for c in ("|", "—", "/")):
            out.personal.title = f"{out.personal.title} · AI-Forward"

    return out
