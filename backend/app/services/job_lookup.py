"""Resolve real job posting URLs from public job board APIs."""

from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html import unescape
from typing import Optional
from urllib.parse import quote_plus

import httpx

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 7.0
_USER_AGENT = "Mozilla/5.0 (compatible; AlfyResume/1.0; job-matching)"
_LOOKUP_CACHE: dict[str, tuple[str, str]] = {}

# Company name fragment -> Greenhouse board slug (verified public boards).
_GREENHOUSE_SLUGS: dict[str, str] = {
    "stripe": "stripe",
    "databricks": "databricks",
    "coinbase": "coinbase",
    "figma": "figma",
    "notion": "notion",
    "mongodb": "mongodb",
    "cloudflare": "cloudflare",
    "datadog": "datadog",
    "hubspot": "hubspot",
    "shopify": "shopify",
    "airbnb": "airbnb",
    "atlassian": "atlassian",
    "snowflake": "snowflake",
    "plaid": "plaid",
    "scale ai": "scaleai",
    "scaleai": "scaleai",
    "anthropic": "anthropic",
    "openai": "openai",
    "ramp": "ramp",
    "vercel": "vercel",
    "canva": "canva",
}

_STOP_WORDS = frozenset(
    {"senior", "junior", "lead", "staff", "principal", "the", "and", "or", "ii", "iii", "i", "a", "an"}
)


@dataclass
class JobPosting:
    title: str
    url: str
    company: str
    source: str  # greenhouse | linkedin


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP_WORDS and len(t) > 1}


def _title_match_score(query: str, title: str) -> float:
    q, t = _tokenize(query), _tokenize(title)
    if not q:
        return 0.0
    return len(q & t) / len(q)


def _greenhouse_slug(company: str) -> Optional[str]:
    slug = company.lower().strip()
    if slug in _GREENHOUSE_SLUGS:
        return _GREENHOUSE_SLUGS[slug]
    for key, board in _GREENHOUSE_SLUGS.items():
        if key in slug:
            return board
    normalized = re.sub(r"[^a-z0-9]+", "", slug)
    if normalized in _GREENHOUSE_SLUGS.values():
        return normalized
    return normalized if len(normalized) >= 3 else None


def _fetch_greenhouse_jobs(board_slug: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_slug}/jobs"
    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT, headers={"User-Agent": _USER_AGENT}) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
            return resp.json().get("jobs") or []
    except Exception as exc:
        logger.debug("Greenhouse fetch failed for %s: %s", board_slug, exc)
        return []


def _fetch_linkedin_jobs(keywords: str, location: str = "United States") -> list[JobPosting]:
    url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={quote_plus(keywords)}&location={quote_plus(location)}&start=0"
    )
    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT, headers={"User-Agent": _USER_AGENT}) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
            html = resp.text
    except Exception as exc:
        logger.debug("LinkedIn job fetch failed: %s", exc)
        return []

    ids = re.findall(r"urn:li:jobPosting:(\d+)", html)
    titles = re.findall(r'class="base-search-card__title[^"]*"[^>]*>\s*([^<]+?)\s*</', html)
    companies = re.findall(r'class="base-search-card__subtitle[^"]*"[^>]*>\s*([^<]+?)\s*</', html)

    results: list[JobPosting] = []
    for i, job_id in enumerate(ids[:15]):
        title = unescape(titles[i].strip()) if i < len(titles) else "Job Opening"
        comp = unescape(companies[i].strip()) if i < len(companies) else ""
        results.append(
            JobPosting(
                title=title,
                url=f"https://www.linkedin.com/jobs/view/{job_id}/",
                company=comp,
                source="linkedin",
            )
        )
    return results


def _pick_best_posting(postings: list[JobPosting], role: str, company: str) -> Optional[JobPosting]:
    if not postings:
        return None
    company_l = company.lower()

    def score(p: JobPosting) -> float:
        title_score = _title_match_score(role, p.title)
        company_bonus = 0.25 if company_l and company_l in p.company.lower() else 0.0
        return title_score + company_bonus

    ranked = sorted(postings, key=score, reverse=True)
    best = ranked[0]
    if score(best) >= 0.25:
        return best
    return ranked[0] if ranked else None


def find_exact_job_posting(
    company: str,
    role: str,
    keywords: str = "",
    location: str = "United States",
) -> Optional[JobPosting]:
    """Find a real job posting URL for company + role."""
    query = (keywords or role).strip()
    board = _greenhouse_slug(company)
    if board:
        jobs = _fetch_greenhouse_jobs(board)
        gh_postings = [
            JobPosting(
                title=unescape(j.get("title", "")),
                url=j.get("absolute_url", ""),
                company=company,
                source="greenhouse",
            )
            for j in jobs
            if j.get("absolute_url")
        ]
        match = _pick_best_posting(gh_postings, role, company)
        if match and _title_match_score(role, match.title) >= 0.2:
            return match
        if match and len(gh_postings) > 0:
            # Still return best greenhouse posting — exact URL on their careers site.
            return match

    li_query = f"{query} {company}".strip()
    li_postings = _fetch_linkedin_jobs(li_query, location)
    if company:
        li_postings = [
            p for p in li_postings if not p.company or company.lower() in p.company.lower()
        ] or _fetch_linkedin_jobs(li_query, location)
    match = _pick_best_posting(li_postings, role, company)
    return match


def is_search_only_url(url: str) -> bool:
    u = (url or "").lower()
    return (
        not u.startswith("http")
        or "/jobs/search" in u
        or "/search-results" in u
        or "/search?" in u
        or "keywords=" in u
        or "/jobs/results" in u
        or "/open-positions?" in u
        or "/all-jobs?" in u
    )


def enrich_company_job_url(
    company: str,
    role: str,
    keywords: str,
    current_url: str,
    location: str = "United States",
) -> tuple[str, str]:
    """Return (job_url, display_role) — uses live posting when found."""
    cache_key = f"{company}|{role}|{keywords}|{location}"
    if cache_key in _LOOKUP_CACHE:
        return _LOOKUP_CACHE[cache_key]

    if current_url and not is_search_only_url(current_url):
        result = (current_url, role)
        _LOOKUP_CACHE[cache_key] = result
        return result

    posting = find_exact_job_posting(company, role, keywords, location)
    if posting:
        result = (posting.url, posting.title)
        _LOOKUP_CACHE[cache_key] = result
        return result
    result = (current_url, role)
    _LOOKUP_CACHE[cache_key] = result
    return result


def enrich_companies_parallel(
    items: list[tuple[str, str, str, str]],
    location: str = "United States",
    max_workers: int = 5,
) -> list[tuple[str, str]]:
    """Enrich list of (company, role, keywords, current_url) -> (url, role)."""
    results: list[tuple[str, str]] = [("", "")] * len(items)

    def task(idx: int, company: str, role: str, keywords: str, url: str) -> tuple[int, str, str]:
        new_url, new_role = enrich_company_job_url(company, role, keywords, url, location)
        return idx, new_url, new_role

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(task, i, company, role, kw, url)
            for i, (company, role, kw, url) in enumerate(items)
        ]
        for fut in as_completed(futures):
            try:
                idx, new_url, new_role = fut.result()
                results[idx] = (new_url, new_role)
            except Exception as exc:
                logger.debug("Job enrich task failed: %s", exc)

    return results
