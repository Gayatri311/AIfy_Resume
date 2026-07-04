"""Heuristic resume quality assessment — drives REBUILD vs POLISH enhancement modes."""

import re

WEAK_OPENERS = re.compile(
    r"^(assisted with|assisted in|helped with|helped|worked on|responsible for|"
    r"duties included|participated in|involved in|handled|managed)\s+",
    re.I,
)

DUTY_PHRASES = (
    "duties included",
    "various tasks",
    "day to day",
    "day-to-day",
    "and other",
    "etc.",
)


def is_vague_bullet(bullet: str) -> bool:
    text = (bullet or "").strip()
    if not text:
        return True
    if len(text.split()) < 12:
        return True
    if WEAK_OPENERS.match(text):
        return True
    lower = text.lower()
    if any(p in lower for p in DUTY_PHRASES):
        return True
    if not any(c.isdigit() for c in text) and "%" not in text and len(text.split()) < 18:
        return True
    return False


def assess_resume_quality(resume) -> dict:
    score = 100
    issues: list[str] = []

    summary = (resume.summary or "").strip()
    if not summary:
        score -= 18
        issues.append("missing_summary")
    elif len(summary.split()) < 25:
        score -= 10
        issues.append("thin_summary")

    if not resume.experience:
        score -= 25
        issues.append("no_experience")
    else:
        if not (resume.personal.title or "").strip():
            if not any((e.title or "").strip() for e in resume.experience):
                score -= 8
                issues.append("missing_title")

    total_bullets = sum(len(e.bullets) for e in resume.experience)
    weak_bullets = sum(1 for e in resume.experience for b in e.bullets if is_vague_bullet(b))

    if total_bullets == 0 and resume.experience:
        score -= 20
        issues.append("no_bullets")
    elif total_bullets > 0:
        weak_ratio = weak_bullets / total_bullets
        if weak_ratio >= 0.5:
            score -= 18
            issues.append("mostly_weak_bullets")
        elif weak_ratio >= 0.25:
            score -= 10
            issues.append("some_weak_bullets")

        measurable = sum(
            1 for e in resume.experience for b in e.bullets if any(c.isdigit() for c in b) or "%" in b
        )
        if measurable / total_bullets < 0.15:
            score -= 12
            issues.append("few_metrics")

    if len(resume.skills) < 6:
        score -= 12
        issues.append("sparse_skills")

    if not resume.projects:
        score -= 8
        issues.append("no_projects")

    ai_text = summary.lower() + " ".join(resume.skills).lower()
    if not any(k in ai_text for k in ("ai", "automation", "data", "llm", "prompt", "python")):
        score -= 6
        issues.append("no_modern_keywords")

    score = max(0, min(100, score))

    if score < 50:
        tier = "weak"
    elif score < 72:
        tier = "moderate"
    else:
        tier = "strong"

    return {
        "quality_score": score,
        "tier": tier,
        "issues": issues,
        "weak_bullet_count": weak_bullets,
        "total_bullet_count": total_bullets,
    }
