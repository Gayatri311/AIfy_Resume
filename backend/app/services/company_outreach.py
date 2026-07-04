"""Generate best-matching job opportunities and cold-email outreach."""

import json
import logging
import re
from html import unescape
from typing import Optional
from urllib.parse import quote_plus

from app.schemas.resume import ResumeData, PotentialCompanyOut, ColdEmailOut, OutreachOut
from app.services.llm_client import call_llm, llm_available, LLMQuotaError
from app.services.job_lookup import enrich_companies_parallel, is_search_only_url

logger = logging.getLogger(__name__)

OUTREACH_SYSTEM = """You are an expert recruiter who matches candidates to open roles.
Return valid JSON only — no markdown."""

OUTREACH_USER = """Match this candidate to exactly 10 REAL job opportunities (company + specific job title).

CANDIDATE PROFILE:
{profile_json}

MATCHING RULES (strict):
1. Each listing must be a plausible open role for THIS candidate — match their seniority, domain, and skills.
2. rank by fit: match_score 70–100 (100 = near-perfect overlap with their experience).
3. role MUST be that employer's specific job posting title (e.g. "Senior Machine Learning Engineer" at Databricks) — NEVER copy the candidate's LinkedIn headline or pipe-separated tagline (e.g. never "AI Engineer | Generative AI | LLMs").
4. fit_reason MUST cite something concrete from their resume (a company they worked at, a skill, a project, or an achievement).
5. Prefer employers in the candidate's industry/domain. Do NOT default to FAANG unless their background clearly fits big tech.
6. Include mix of company sizes, but every company must realistically hire someone with this exact background.
7. search_keywords: 3–6 words combining the role title + their top matching skills (used for job search links).
8. Sort companies by match_score descending (best match first).

Return JSON:
{{
  "companies": [
    {{
      "name": "Company name",
      "role": "Specific job title that matches their experience level",
      "match_score": 92,
      "search_keywords": "senior product manager AI platform",
      "why_hiring": "One sentence on why this company is hiring for this role now",
      "fit_reason": "One sentence citing a specific resume detail that makes them a strong match",
      "careers_hint": "Brief note on where to find this role on their careers site",
      "linkedin_url": "https://www.linkedin.com/company/company-slug"
    }}
  ],
  "cold_email": {{
    "subject": "Short subject line (under 60 chars)",
    "body": "3-4 sentence email: intro, 1 proof point from resume, attach resume mention, clear ask for 15-min chat. Under 100 words. Professional, not salesy."
  }},
  "outreach_tip": "One sentence on applying to these best-match roles with the attached resume"
}}"""


# (company, role_suffix, domains, linkedin_url, why_hiring)
_JOB_POOL: list[tuple[str, str, set[str], str, str]] = [
    ("Stripe", "Payments Engineer", {"fintech", "backend", "general"}, "https://www.linkedin.com/company/stripe", "Payments and fintech infrastructure teams hire weekly."),
    ("Plaid", "Software Engineer", {"fintech", "backend", "api"}, "https://www.linkedin.com/company/plaid-", "Financial data APIs drive steady engineering hiring."),
    ("Databricks", "Data Engineer", {"data", "ai", "ml"}, "https://www.linkedin.com/company/databricks", "Lakehouse and ML platform teams are actively recruiting."),
    ("Snowflake", "Solutions Engineer", {"data", "cloud", "enterprise"}, "https://www.linkedin.com/company/snowflake-computing", "Enterprise data cloud expansion creates new roles."),
    ("Anthropic", "Research Engineer", {"ai", "ml", "nlp"}, "https://www.linkedin.com/company/anthropicresearch", "AI safety and model teams continue to grow."),
    ("OpenAI", "Applied AI Engineer", {"ai", "ml", "nlp"}, "https://www.linkedin.com/company/openai", "Applied AI product teams post roles regularly."),
    ("Figma", "Product Engineer", {"frontend", "product", "design"}, "https://www.linkedin.com/company/figma", "Design tooling and collaboration products need product engineers."),
    ("Notion", "Full Stack Engineer", {"frontend", "product", "general"}, "https://www.linkedin.com/company/notionhq", "Productivity platform scales engineering headcount."),
    ("HubSpot", "Growth Product Manager", {"product", "marketing", "saas"}, "https://www.linkedin.com/company/hubspot", "B2B SaaS growth teams maintain open reqs."),
    ("Shopify", "Commerce Engineer", {"ecommerce", "backend", "general"}, "https://www.linkedin.com/company/shopify", "Merchant platform engineering hires continuously."),
    ("Atlassian", "Software Engineer", {"enterprise", "product", "general"}, "https://www.linkedin.com/company/atlassian", "Collaboration software teams hire for delivery tooling."),
    ("Cloudflare", "Systems Engineer", {"backend", "infra", "security"}, "https://www.linkedin.com/company/cloudflare", "Edge and security infrastructure teams are expanding."),
    ("MongoDB", "Developer Advocate", {"data", "backend", "general"}, "https://www.linkedin.com/company/mongodbinc", "Database platform teams hire for developer experience."),
    ("Canva", "Frontend Engineer", {"frontend", "design", "product"}, "https://www.linkedin.com/company/canva", "Design-tech product teams recruit frontend talent."),
    ("Ramp", "Product Manager", {"fintech", "product", "startup"}, "https://www.linkedin.com/company/ramp", "Corporate spend fintech scales product org."),
    ("Vercel", "Developer Experience Engineer", {"frontend", "infra", "general"}, "https://www.linkedin.com/company/vercel", "Frontend cloud platform grows DX and engineering teams."),
    ("Scale AI", "ML Operations Engineer", {"ai", "ml", "data"}, "https://www.linkedin.com/company/scaleai", "AI data infrastructure hiring remains strong."),
    ("Coinbase", "Backend Engineer", {"fintech", "crypto", "backend"}, "https://www.linkedin.com/company/coinbase", "Crypto exchange platform maintains engineering hiring."),
    ("Airbnb", "Senior Software Engineer", {"product", "general", "frontend"}, "https://www.linkedin.com/company/airbnb", "Marketplace product engineering posts roles weekly."),
    ("Datadog", "Site Reliability Engineer", {"infra", "backend", "data"}, "https://www.linkedin.com/company/datadog", "Observability platform teams expand SRE hiring."),
]

_DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ai": ("machine learning", "ml", "llm", "gpt", "nlp", "deep learning", "neural", "ai ", "artificial intelligence", "rag", "prompt"),
    "ml": ("machine learning", "ml", "tensorflow", "pytorch", "model", "training"),
    "nlp": ("nlp", "natural language", "llm", "gpt", "transformer"),
    "data": ("data", "analytics", "sql", "etl", "warehouse", "spark", "pipeline", "bi "),
    "fintech": ("fintech", "payment", "banking", "finance", "trading", "lending", "stripe"),
    "crypto": ("crypto", "blockchain", "web3", "defi"),
    "frontend": ("react", "frontend", "typescript", "javascript", "vue", "angular", "css", "ui ", "ux "),
    "backend": ("backend", "api", "microservice", "java", "python", "go ", "golang", "node", "rest"),
    "infra": ("kubernetes", "k8s", "devops", "aws", "gcp", "azure", "terraform", "docker", "sre", "infrastructure"),
    "security": ("security", "cyber", "auth", "encryption"),
    "product": ("product manager", "product management", "roadmap", "stakeholder", "pm "),
    "marketing": ("marketing", "growth", "seo", "campaign", "brand"),
    "saas": ("saas", "b2b", "subscription", "crm"),
    "ecommerce": ("ecommerce", "e-commerce", "retail", "commerce", "shopify"),
    "enterprise": ("enterprise", "b2b", "salesforce", "crm"),
    "design": ("design", "figma", "ui/ux", "user experience"),
    "cloud": ("cloud", "aws", "azure", "gcp", "saas"),
    "startup": ("founder", "startup", "early stage", "0 to 1"),
    "api": ("api", "rest", "graphql", "integration"),
}


def _linkedin_company_url(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"https://www.linkedin.com/company/{slug}"


def _linkedin_job_search_url(company: str, role: str, keywords: str = "") -> str:
    query = (keywords or f"{role} {company}").strip()
    return f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(query)}&f_TPR=r604800"


def _careers_job_search_url(company: str, role: str, keywords: str = "") -> str:
    q = quote_plus((keywords or role).strip())
    slug = company.lower().strip()
    templates = {
        "google": f"https://www.google.com/about/careers/applications/jobs/results/?q={q}",
        "microsoft": f"https://careers.microsoft.com/us/en/search-results?keywords={q}",
        "amazon": f"https://www.amazon.jobs/en/search?base_query={q}",
        "salesforce": f"https://careers.salesforce.com/en/jobs/?search={q}",
        "adobe": f"https://careers.adobe.com/us/en/search-results?keywords={q}",
        "stripe": f"https://stripe.com/jobs/search?query={q}",
        "hubspot": f"https://www.hubspot.com/careers/jobs?query={q}",
        "databricks": f"https://www.databricks.com/company/careers/open-positions?keywords={q}",
        "shopify": f"https://www.shopify.com/careers/search?query={q}",
        "atlassian": f"https://www.atlassian.com/company/careers/all-jobs?search={q}",
    }
    for key, url in templates.items():
        if key in slug:
            return url
    return _linkedin_job_search_url(company, role, keywords)


def _is_linkedin_headline(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if "|" in t:
        return True
    if len(t) > 55:
        return True
    if t.count("·") > 1 or t.count("/") > 2:
        return True
    return False


def _primary_role_title_from_string(title: str) -> str:
    """Extract a single clean job title from a LinkedIn-style headline."""
    t = (title or "").strip()
    if not t:
        return ""
    for sep in ("|", "·", "—", " – ", " / ", ","):
        if sep in t:
            t = t.split(sep)[0].strip()
            break
    t = re.sub(r"\s*·\s*AI-Forward.*$", "", t, flags=re.I)
    return t.strip()


def _primary_role_from_resume(resume: ResumeData) -> str:
    """Best single job title for matching — experience title beats headline."""
    for exp in resume.experience[:2]:
        exp_title = (exp.title or "").strip()
        if exp_title and not _is_linkedin_headline(exp_title):
            return _primary_role_title_from_string(exp_title) or exp_title
    from_headline = _primary_role_title_from_string(resume.personal.title or "")
    return from_headline or "Professional"


def _sanitize_job_title(role: str, fallback: str = "Professional") -> str:
    """Ensure displayed role is a single posting title, not a headline."""
    role = (role or "").strip()
    if not role:
        return _primary_role_title_from_string(fallback) or fallback
    if _is_linkedin_headline(role):
        return _primary_role_title_from_string(role) or fallback
    return role


def outreach_needs_refresh(companies: list[PotentialCompanyOut]) -> bool:
    if not companies:
        return False
    if all(c.match_score == 0 for c in companies):
        return True
    roles = [c.role for c in companies]
    if any(_is_linkedin_headline(r) for r in roles):
        return True
    if len(roles) > 1 and len(set(roles)) == 1:
        return True
    return False


def _resume_text_blob(resume: ResumeData) -> str:
    parts = [
        resume.summary,
        resume.personal.title or "",
        " ".join(resume.skills),
    ]
    for exp in resume.experience:
        parts.append(exp.title)
        parts.append(exp.company)
        parts.extend(exp.bullets)
    for proj in resume.projects:
        parts.append(proj.title)
        parts.append(proj.description)
        parts.extend(proj.tech_stack)
    return " ".join(p for p in parts if p).lower()


def _infer_domains(resume: ResumeData) -> set[str]:
    blob = _resume_text_blob(resume)
    matched = {domain for domain, keywords in _DOMAIN_KEYWORDS.items() if any(k in blob for k in keywords)}
    return matched or {"general"}


def _seniority_prefix(resume: ResumeData) -> str:
    blob = _resume_text_blob(resume)
    title = _primary_role_from_resume(resume).lower()
    if any(x in blob or x in title for x in ("director", "vp ", "head of", "chief", "principal")):
        return "Senior "
    if any(x in blob or x in title for x in ("senior", "sr.", "lead", "staff")):
        return "Senior "
    if any(x in blob or x in title for x in ("junior", "intern", "associate", "entry")):
        return ""
    exp_count = len(resume.experience)
    if exp_count >= 4:
        return "Senior "
    if exp_count <= 1:
        return ""
    return ""


def _top_skills(resume: ResumeData, limit: int = 4) -> list[str]:
    return [s for s in resume.skills if s.strip()][:limit]


def _build_resume_matching_context(resume: ResumeData) -> dict:
    recent_experience = []
    for exp in resume.experience[:5]:
        recent_experience.append(
            {
                "company": exp.company,
                "title": exp.title,
                "dates": f"{exp.start_date}–{exp.end_date}",
                "highlights": exp.bullets[:4],
            }
        )
    projects = [
        {
            "title": p.title,
            "tech_stack": p.tech_stack[:6],
            "description": (p.description or "")[:250],
        }
        for p in resume.projects[:4]
    ]
    return {
        "name": resume.personal.name,
        "primary_role": _primary_role_from_resume(resume),
        "headline": resume.personal.title,
        "location": resume.personal.location,
        "summary": resume.summary[:600],
        "skills": resume.skills[:30],
        "domains_detected": sorted(_infer_domains(resume)),
        "recent_experience": recent_experience,
        "projects": projects,
        "education": [
            {"institution": e.institution, "degree": e.degree, "year": e.year}
            for e in resume.education[:3]
        ],
    }


def _score_job_pool_entry(resume: ResumeData, domains: set[str], entry: tuple) -> int:
    _company, _role_suffix, entry_domains, _linkedin, _why = entry
    overlap = len(domains & entry_domains)
    base = 68 + overlap * 8
    blob = _resume_text_blob(resume)
    for skill in _top_skills(resume, 6):
        if skill.lower() in blob and skill.lower() in _role_suffix.lower():
            base += 4
    return min(base, 97)


def _fit_reason_from_resume(resume: ResumeData, company: str, role: str) -> str:
    skills = _top_skills(resume, 3)
    if resume.experience:
        exp = resume.experience[0]
        if exp.bullets:
            highlight = exp.bullets[0][:120].rstrip(".")
            return f"Your {exp.title} experience at {exp.company} — \"{highlight}...\" — maps directly to {role} at {company}."
        return f"Your background as {exp.title} at {exp.company} aligns with {role} requirements at {company}."
    if skills:
        return f"Your skills in {', '.join(skills)} are a strong match for {role} at {company}."
    title = resume.personal.title or "your background"
    return f"Your {title} profile is well suited for {role} at {company}."


def _build_search_keywords(resume: ResumeData, role: str, company: str = "") -> str:
    """Short search query from the job title — never the full LinkedIn headline."""
    clean_role = _sanitize_job_title(role)
    skills = _top_skills(resume, 1)
    if skills:
        return f"{clean_role} {skills[0]}".strip()
    if company:
        return f"{clean_role} {company}".strip()
    return clean_role


def _role_for_candidate(resume: ResumeData, role_suffix: str) -> str:
    """Company-specific posting title — never reuse the candidate's headline."""
    prefix = _seniority_prefix(resume)
    return f"{prefix}{role_suffix}".strip()


def _enrich_with_live_jobs(
    companies: list[PotentialCompanyOut], resume: ResumeData
) -> list[PotentialCompanyOut]:
    """Attach real job posting URLs from Greenhouse / LinkedIn when available."""
    location = (resume.personal.location or "").strip() or "United States"
    items = [(c.name, c.role, c.search_keywords or c.role, c.job_url) for c in companies]
    if not any(is_search_only_url(url) for _, _, _, url in items):
        return companies

    enriched = enrich_companies_parallel(items, location=location)
    updated: list[PotentialCompanyOut] = []
    for company, (url, live_role) in zip(companies, enriched):
        if url and not is_search_only_url(url):
            updated.append(
                company.model_copy(
                    update={
                        "job_url": url,
                        "role": unescape(live_role or company.role),
                        "careers_hint": "Live job posting",
                    }
                )
            )
        else:
            updated.append(company)
    return updated


def _fallback_outreach(resume: ResumeData) -> OutreachOut:
    name = resume.personal.name or "Candidate"
    primary_role = _primary_role_from_resume(resume)
    domains = _infer_domains(resume)

    scored_pool = sorted(
        [(entry, _score_job_pool_entry(resume, domains, entry)) for entry in _JOB_POOL],
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    companies = []
    for entry, score in scored_pool:
        company, role_suffix, _entry_domains, linkedin, why_hiring = entry
        role = _role_for_candidate(resume, role_suffix)
        keywords = _build_search_keywords(resume, role, company)
        companies.append(
            PotentialCompanyOut(
                name=company,
                role=role,
                match_score=score,
                search_keywords=keywords,
                why_hiring=why_hiring,
                fit_reason=_fit_reason_from_resume(resume, company, role),
                careers_hint=f"Search {company} careers for \"{role}\"",
                job_url=_careers_job_search_url(company, role, keywords),
                linkedin_url=linkedin,
            )
        )

    companies = _enrich_with_live_jobs(companies, resume)

    return OutreachOut(
        companies=companies,
        cold_email=ColdEmailOut(
            subject=f"{primary_role} — interested in matching roles — {name.split()[0] if name else 'Applicant'}",
            body=(
                f"Hi [Hiring Manager],\n\n"
                f"I'm {name}, a {primary_role} whose experience aligns closely with your team. "
                f"I've attached my resume and would value 15 minutes to discuss a fit.\n\n"
                f"Would you be open to a brief conversation this week?\n\n"
                f"Best,\n{name}"
            ),
        ),
        outreach_tip=(
            "Apply to these best-match roles with your PDF resume — personalize each application "
            "to cite the specific experience that maps to that job."
        ),
    )


def _parse_company(c: dict, resume: ResumeData, target_role: str) -> PotentialCompanyOut:
    name = c.get("name", "Company")
    raw_role = c.get("role", target_role)
    role = _sanitize_job_title(raw_role, target_role)
    keywords = (c.get("search_keywords") or "").strip()
    if not keywords or _is_linkedin_headline(keywords):
        keywords = _build_search_keywords(resume, role, name)
    else:
        keywords = _sanitize_job_title(keywords, role)
    raw_score = c.get("match_score", 80)
    try:
        match_score = max(70, min(100, int(raw_score)))
    except (TypeError, ValueError):
        match_score = 80

    return PotentialCompanyOut(
        name=name,
        role=role,
        match_score=match_score,
        search_keywords=keywords,
        why_hiring=c.get("why_hiring", "Active hiring for this profile."),
        fit_reason=c.get("fit_reason", "Strong alignment with your background."),
        careers_hint=c.get("careers_hint", "Check company careers page"),
        job_url=_careers_job_search_url(name, role, keywords),
        linkedin_url=c.get("linkedin_url") or _linkedin_company_url(name),
    )


def _sort_companies(companies: list[PotentialCompanyOut]) -> list[PotentialCompanyOut]:
    return sorted(companies, key=lambda c: c.match_score, reverse=True)


def sanitize_outreach_companies(
    companies: list[PotentialCompanyOut],
    resume: Optional[ResumeData] = None,
) -> list[PotentialCompanyOut]:
    """Re-resolve job URLs on read, fix headline-style roles, keep best matches first."""
    if resume and outreach_needs_refresh(companies):
        return _fallback_outreach(resume).companies

    sanitized = []
    for c in companies:
        role = _sanitize_job_title(c.role, _primary_role_from_resume(resume) if resume else "Professional")
        keywords = (c.search_keywords or "").strip()
        if _is_linkedin_headline(keywords):
            keywords = _build_search_keywords(resume, role, c.name) if resume else role
        elif not keywords:
            keywords = role
        sanitized.append(
            c.model_copy(
                update={
                    "role": role,
                    "search_keywords": keywords,
                    "job_url": _careers_job_search_url(c.name, role, keywords),
                }
            )
        )
    if sanitized and all(c.match_score == 0 for c in sanitized):
        sanitized = [
            c.model_copy(update={"match_score": max(72, 92 - i * 2)})
            for i, c in enumerate(sanitized)
        ]
    sanitized = _sort_companies(sanitized)
    if resume:
        sanitized = _enrich_with_live_jobs(sanitized, resume)
    return sanitized


def generate_company_outreach(resume: ResumeData) -> OutreachOut:
    target_role = _primary_role_from_resume(resume)
    profile = _build_resume_matching_context(resume)

    if not llm_available():
        return _fallback_outreach(resume)

    try:
        result = call_llm(
            OUTREACH_SYSTEM,
            OUTREACH_USER.format(profile_json=json.dumps(profile, indent=2)[:9000]),
            temperature=0.3,
        )
        companies = _sort_companies(
            [
                _parse_company(c, resume, target_role)
                for c in (result.get("companies") or [])[:10]
            ]
        )
        email_data = result.get("cold_email") or {}
        if len(companies) < 5:
            return _fallback_outreach(resume)
        companies = _enrich_with_live_jobs(companies, resume)
        return OutreachOut(
            companies=companies,
            cold_email=ColdEmailOut(
                subject=email_data.get("subject", f"Interest in {target_role} role"),
                body=email_data.get("body", ""),
            ),
            outreach_tip=result.get(
                "outreach_tip",
                "Apply to these best-match roles with your resume — tailor each to the fit reason shown.",
            ),
        )
    except LLMQuotaError as e:
        logger.warning("Company outreach skipped (LLM quota): %s", e)
        return _fallback_outreach(resume)
    except Exception as e:
        logger.warning("Company outreach LLM failed: %s", e)
        return _fallback_outreach(resume)


def outreach_to_store_payload(outreach: OutreachOut) -> list[dict]:
    return [outreach.model_dump()]


def outreach_from_stored(stored: Optional[list]) -> Optional[OutreachOut]:
    if not stored:
        return None
    try:
        data = stored[0] if isinstance(stored, list) else stored
        if isinstance(data, str):
            data = json.loads(data)
        outreach = OutreachOut(**data)
        outreach.companies = _sort_companies(outreach.companies)
        return outreach
    except Exception:
        return None
