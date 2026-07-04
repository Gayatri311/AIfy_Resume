def analyze_gaps(resume) -> dict:
    text = (resume.summary + " ".join(resume.skills)).lower()

    all_ai_skills = [
        "LangChain", "RAG", "Prompt Engineering", "Vector Databases",
        "AI Agent Frameworks", "Model Fine-tuning", "Workflow Automation",
    ]
    missing_skills = [s for s in all_ai_skills if s.lower().split()[0] not in text]

    missing_projects = []
    if not resume.projects:
        missing_projects.append("Hands-on AI project demonstrating technical claims")

    missing_certs = []
    if "prompt engineering" not in text:
        missing_certs.append("Prompt Engineering Certification")
    if "langchain" not in text:
        missing_certs.append("LangChain Developer Certificate")

    return {
        "missing_skills": missing_skills[:5],
        "missing_projects": missing_projects,
        "missing_certifications": missing_certs,
        "missing_frameworks": ["LangGraph", "CrewAI"] if "agent" not in text else [],
    }
