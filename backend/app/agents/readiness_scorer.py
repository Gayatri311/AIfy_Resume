def calculate_ai_readiness(resume, ats_score: float) -> dict:
    text = resume.summary + " ".join(
        b for exp in resume.experience for b in exp.bullets
    )
    text_lower = text.lower()

    ai_terms = sum(1 for kw in ["ai", "llm", "automation", "predictive", "langchain", "rag", "prompt"] if kw in text_lower)
    ai_terminology = min(100, ai_terms * 15 + 20)

    project_evidence = min(100, len(resume.projects) * 35 + 10)
    technical_depth = min(100, len([s for s in resume.skills if any(t in s.lower() for t in ["python", "api", "data", "cloud"])]) * 20 + 30)

    measurable = sum(1 for exp in resume.experience for b in exp.bullets if "%" in b or any(c.isdigit() for c in b))
    measurable_achievements = min(100, measurable * 25 + 20)

    ai_readiness = (
        ats_score * 0.25
        + ai_terminology * 0.25
        + project_evidence * 0.20
        + technical_depth * 0.15
        + measurable_achievements * 0.15
    )

    if ai_readiness <= 40:
        band = "Beginner"
    elif ai_readiness <= 60:
        band = "Emerging"
    elif ai_readiness <= 80:
        band = "AI Aware"
    else:
        band = "AI Ready"

    return {
        "ai_readiness": round(ai_readiness),
        "ats_score": round(ats_score),
        "ai_terminology": round(ai_terminology),
        "project_evidence": round(project_evidence),
        "technical_depth": round(technical_depth),
        "measurable_achievements": round(measurable_achievements),
        "band": band,
    }
