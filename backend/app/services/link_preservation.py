"""Extract and preserve hyperlinks from the original resume in the enhanced version."""

import re
from copy import deepcopy

from app.schemas.resume import ResumeData, ProjectItem

URL_PATTERN = re.compile(
    r"(?:https?://|www\.)[^\s\)\]>\"']+|"
    r"(?:linkedin\.com/in/[\w\-]+|github\.com/[\w\-/]+)",
    re.I,
)
LINKEDIN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+", re.I)
GITHUB = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w\-/]+", re.I)
EMAIL = re.compile(r"[\w.\-+]+@[\w.\-]+\.\w+")


def _normalize_url(url: str) -> str:
    u = url.strip().rstrip(".,;)")
    if u and not u.lower().startswith("http"):
        return f"https://{u}"
    return u


def _collect_text_blobs(data: ResumeData) -> list[str]:
    blobs: list[str] = []
    p = data.personal
    for val in (p.email, p.phone, p.location, p.linkedin, p.website, p.github, p.name, p.title):
        if val:
            blobs.append(str(val))
    if data.summary:
        blobs.append(data.summary)
    for exp in data.experience:
        blobs.extend([exp.company, exp.title, exp.start_date, exp.end_date])
        blobs.extend(exp.bullets or [])
    for proj in data.projects:
        blobs.extend([proj.title, proj.description, proj.url or ""])
    blobs.extend(data.skills or [])
    for edu in data.education:
        blobs.extend([edu.institution, edu.degree, edu.year])
    return blobs


def extract_urls_from_resume(data: ResumeData, raw_text: str = "") -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for blob in _collect_text_blobs(data) + ([raw_text] if raw_text else []):
        for match in URL_PATTERN.findall(blob):
            norm = _normalize_url(match)
            key = norm.lower()
            if key not in seen:
                seen.add(key)
                urls.append(norm)
    return urls


def _url_in_text(url: str, text: str) -> bool:
    bare = url.replace("https://", "").replace("http://", "").lower()
    return bare in (text or "").lower() or url.lower() in (text or "").lower()


def _append_url_to_bullet(bullet: str, url: str) -> str:
    if _url_in_text(url, bullet):
        return bullet
    return f"{bullet.rstrip()} — {url}"


def preserve_links(original: ResumeData, enhanced: ResumeData, raw_text: str = "") -> ResumeData:
    """Keep contact links and inline URLs from the original in the enhanced resume."""
    out = deepcopy(enhanced)
    orig_p = original.personal
    out_p = out.personal

    for field in ("email", "phone", "location", "linkedin", "website", "github"):
        if not getattr(out_p, field) and getattr(orig_p, field):
            setattr(out_p, field, getattr(orig_p, field))

    all_urls = extract_urls_from_resume(original, raw_text)

    for url in all_urls:
        lower = url.lower()
        if "linkedin.com/in" in lower and not out_p.linkedin:
            out_p.linkedin = url
        elif "github.com" in lower and not out_p.github:
            out_p.github = url
        elif not out_p.website and "linkedin.com" not in lower and "github.com" not in lower:
            out_p.website = url

    for email in EMAIL.findall(raw_text or ""):
        if not out_p.email:
            out_p.email = email
            break

    orig_projects = {(p.title or "").lower(): p for p in original.projects if (p.title or "").strip()}
    for proj in out.projects:
        orig = orig_projects.get((proj.title or "").lower())
        if orig and orig.url and not proj.url:
            proj.url = orig.url
        if orig and orig.url and orig.url not in (proj.description or ""):
            if proj.description and not _url_in_text(orig.url, proj.description):
                proj.description = f"{proj.description.rstrip()}\n{orig.url}"

    orig_bullets = []
    for exp in original.experience:
        orig_bullets.extend(exp.bullets or [])

    for exp in out.experience:
        new_bullets = []
        for bullet in exp.bullets or []:
            updated = bullet
            for url in all_urls:
                for ob in orig_bullets:
                    if url.lower() in ob.lower() and not _url_in_text(url, bullet):
                        updated = _append_url_to_bullet(updated, url)
                        break
            new_bullets.append(updated)
        exp.bullets = new_bullets

    return out
