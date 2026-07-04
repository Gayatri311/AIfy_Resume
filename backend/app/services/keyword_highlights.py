"""Keywords to bold in resume preview for ATS visibility."""

from typing import List, Optional

from app.schemas.resume import ResumeData

# High-impact terms recruiters scan for (matched case-insensitively)
SCAN_TERMS = [
    "python", "javascript", "typescript", "react", "node", "java", "aws", "azure", "gcp",
    "kubernetes", "docker", "sql", "postgresql", "mongodb", "redis", "api", "rest", "graphql",
    "machine learning", "deep learning", "llm", "llms", "rag", "nlp", "ai", "genai",
    "langchain", "tensorflow", "pytorch", "spark", "kafka", "ci/cd", "devops", "agile", "scrum",
    "leadership", "cross-functional", "stakeholder", "roi", "kpi", "saas", "b2b", "b2c",
    "prompt engineering", "vector", "embedding", "fine-tuning", "automation",
]


def build_highlight_keywords(
    resume: ResumeData,
    missing_keywords: Optional[List[str]] = None,
    max_keywords: int = 40,
) -> list:
    """Longest-first unique keywords for safe substring highlighting."""
    seen: set[str] = set()
    keywords: list[str] = []

    def add(term: str) -> None:
        t = term.strip()
        if not t or len(t) < 2:
            return
        key = t.lower()
        if key in seen:
            return
        seen.add(key)
        keywords.append(t)

    for skill in resume.skills or []:
        add(skill)
        for part in skill.replace("/", ",").split(","):
            add(part.strip())

    for cert in resume.certifications or []:
        add(cert)

    for proj in resume.projects or []:
        for tech in proj.tech_stack or []:
            add(tech)

    for term in SCAN_TERMS:
        add(term)

    for term in missing_keywords or []:
        add(term)

    for exp in resume.experience or []:
        for bullet in exp.bullets or []:
            for term in SCAN_TERMS:
                if term.lower() in bullet.lower():
                    add(term)

    keywords.sort(key=lambda x: len(x), reverse=True)
    return keywords[:max_keywords]
