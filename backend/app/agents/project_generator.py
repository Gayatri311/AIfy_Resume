from app.schemas.resume import ProjectItem

ROLE_PROJECTS = {
    "engineer": {
        "title": "AI Code Review Assistant",
        "description": (
            "Personal project exploring LLM-assisted code review suggestions and documentation "
            "generation for internal tooling — built to learn prompt patterns and workflow automation."
        ),
        "tech_stack": ["Python", "OpenAI API", "GitHub Actions"],
        "status": "SUGGESTED PROJECT",
    },
    "product": {
        "title": "AI Documentation Assistant",
        "description": (
            "Side project to organize team docs and answer process questions faster using "
            "retrieval-style search — practical way to apply AI to operations work."
        ),
        "tech_stack": ["Python", "LangChain", "Vector DB"],
        "status": "SUGGESTED PROJECT",
    },
    "hr": {
        "title": "Resume Screening Assistant",
        "description": (
            "Learning project to practice structured candidate screening criteria and "
            "consistent feedback templates with LLM support."
        ),
        "tech_stack": ["Python", "LangChain", "FastAPI"],
        "status": "SUGGESTED PROJECT",
    },
    "sales": {
        "title": "Lead Research Assistant",
        "description": (
            "Small automation to summarize account research and draft outreach notes — "
            "focused on saving prep time, not replacing judgment."
        ),
        "tech_stack": ["Python", "OpenAI API", "CRM exports"],
        "status": "SUGGESTED PROJECT",
    },
    "marketing": {
        "title": "Content Repurposing Workflow",
        "description": (
            "Personal workflow using AI-assisted drafting to turn long-form content into "
            "channel-specific snippets with human review."
        ),
        "tech_stack": ["Prompt templates", "Notion", "OpenAI API"],
        "status": "SUGGESTED PROJECT",
    },
    "analyst": {
        "title": "Automated Reporting Helper",
        "description": (
            "Project to streamline recurring reports with templated analysis and "
            "data-driven summaries — emphasizes reproducible workflows."
        ),
        "tech_stack": ["Python", "Pandas", "OpenAI API"],
        "status": "SUGGESTED PROJECT",
    },
    "default": {
        "title": "Workflow Automation Assistant",
        "description": (
            "Starter project to automate a repetitive weekly task using simple scripts "
            "and AI-assisted drafting — honest learning project for AI readiness."
        ),
        "tech_stack": ["Python", "LangChain", "Slack or Email API"],
        "status": "SUGGESTED PROJECT",
    },
}

ROLE_SKILLS = {
    "engineer": ["API Integration", "Workflow Automation", "Prompt Engineering"],
    "product": ["Process Optimization", "AI-Assisted Documentation", "Cross-functional Alignment"],
    "hr": ["Structured Screening", "AI-Assisted Workflows", "Process Documentation"],
    "sales": ["Lead Research", "CRM Automation", "AI-Assisted Outreach Drafting"],
    "marketing": ["Content Workflows", "AI-Assisted Copy Drafting", "Campaign Analytics"],
    "analyst": ["Data-Driven Reporting", "Dashboard Automation", "Predictive Insights"],
    "default": ["Workflow Automation", "AI-Assisted Productivity", "Process Improvement"],
}


def _detect_role_key(title: str, skills: list[str]) -> str:
    blob = f"{title} {' '.join(skills)}".lower()
    if any(k in blob for k in ("software", "engineer", "developer", "devops", "sre")):
        return "engineer"
    if any(k in blob for k in ("product", "operations", "program manager", "pm")):
        return "product"
    if any(k in blob for k in ("hr", "human resources", "recruiter", "talent")):
        return "hr"
    if any(k in blob for k in ("sales", "account executive", "business development")):
        return "sales"
    if any(k in blob for k in ("marketing", "growth", "content", "seo")):
        return "marketing"
    if any(k in blob for k in ("analyst", "analytics", "data")):
        return "analyst"
    return "default"


def suggest_ai_project_for_role(resume) -> ProjectItem:
    key = _detect_role_key(resume.personal.title, resume.skills)
    template = ROLE_PROJECTS[key]
    return ProjectItem(**template)


def role_based_skills(resume) -> list[str]:
    key = _detect_role_key(resume.personal.title, resume.skills)
    return ROLE_SKILLS[key][:3]


def generate_projects(resume) -> list[dict]:
    """Return suggested projects for dashboard (includes roadmap metadata)."""
    key = _detect_role_key(resume.personal.title, resume.skills)
    base = ROLE_PROJECTS[key]
    return [{
        "title": base["title"],
        "difficulty": "Beginner" if key == "default" else "Intermediate",
        "tech_stack": base["tech_stack"],
        "architecture": "Start small: one workflow, one user, measurable time saved",
        "roadmap": [
            "Pick one repetitive task from your current role",
            "Prototype a simple automation or AI-assisted draft",
            "Document results and limitations honestly",
            "Add to portfolio or internal demo",
        ],
        "business_impact": base["description"],
    }]
