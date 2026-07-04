AI_KEYWORDS = [
    "ai", "machine learning", "automation", "llm", "nlp", "data-driven",
    "predictive", "langchain", "prompt engineering", "rag",
]


def analyze_ats(resume) -> dict:
    issues = []
    missing_keywords = []

    text = resume.summary + " ".join(
        b for exp in resume.experience for b in exp.bullets
    ) + " ".join(resume.skills)
    text_lower = text.lower()

    if len(resume.experience) == 0:
        issues.append("No professional experience section detected")
    if not resume.summary:
        issues.append("Missing professional summary")
    if len(resume.skills) < 5:
        issues.append("Skills section is too sparse for ATS keyword matching")

    for kw in AI_KEYWORDS:
        if kw not in text_lower:
            missing_keywords.append(kw)

    format_score = 100 - len(issues) * 15
    keyword_score = max(0, 100 - len(missing_keywords) * 8)
    ats_score = min(100, (format_score + keyword_score) / 2)

    return {
        "ats_score": round(ats_score),
        "issues": issues,
        "missing_keywords": missing_keywords[:10],
    }
