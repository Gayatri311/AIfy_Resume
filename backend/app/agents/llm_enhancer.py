import json
import logging
from copy import deepcopy
from typing import Optional

from pydantic import ValidationError

from app.schemas.resume import ResumeData, ProjectItem
from app.agents.prompts import (
    RESUME_ENHANCEMENT_SYSTEM,
    RESUME_ENHANCEMENT_USER,
    RESUME_FULL_REWRITE_SYSTEM,
    RESUME_FULL_REWRITE_USER,
)
from app.services.llm_client import call_llm, LLMQuotaError
from app.agents.experience_enhancer import enhance_resume as rule_enhance
from app.agents.authenticity_validator import validate_authenticity
from app.agents.resume_quality import assess_resume_quality, is_vague_bullet
from app.services.resume_format import normalize_resume_data
from app.services.resume_cleanup import strip_invented_sections, ensure_experience_bullets, ensure_project_coverage
from app.services.link_preservation import preserve_links

logger = logging.getLogger(__name__)


def enhance_resume_with_llm(original: ResumeData, raw_text: str) -> tuple[ResumeData, list[dict], list[dict]]:
    """Rewrite resume via LLM for ATS-friendly structured output. Falls back to rules on failure."""
    quality = assess_resume_quality(original)
    temperature = 0.45 if quality["tier"] == "weak" else 0.35

    try:
        enhanced, changes, suggestions = _try_full_rewrite(original, raw_text, quality, temperature)
        if enhanced and changes:
            logger.info("LLM full rewrite applied with %d change notes (tier=%s)", len(changes), quality["tier"])
            return enhanced, changes, suggestions
    except LLMQuotaError as e:
        logger.warning("LLM quota exhausted during full rewrite — using rule-based fallback: %s", e)
        enhanced, changes = rule_enhance(original)
        enhanced = strip_invented_sections(original, enhanced)
        enhanced = ensure_project_coverage(original, enhanced)
        enhanced = ensure_experience_bullets(original, enhanced)
        enhanced = normalize_resume_data(enhanced)
        return enhanced, changes, []
    except Exception as e:
        logger.warning("LLM full rewrite failed: %s", e)

    try:
        user_prompt = RESUME_ENHANCEMENT_USER.format(
            original_json=json.dumps(original.model_dump(), indent=2),
            raw_text=raw_text[:12000],
            quality_tier=quality["tier"],
            quality_score=quality["quality_score"],
            quality_issues=", ".join(quality["issues"]) or "none",
            weak_bullet_count=quality["weak_bullet_count"],
            total_bullet_count=quality["total_bullet_count"],
        )
        result = call_llm(RESUME_ENHANCEMENT_SYSTEM, user_prompt, temperature=temperature)
        enhanced, changes = _apply_enhancement_deltas(original, result)
        if changes:
            logger.info("LLM delta enhancements applied: %d changes", len(changes))
            enhanced = strip_invented_sections(original, enhanced)
            enhanced = ensure_project_coverage(original, enhanced)
            enhanced = ensure_experience_bullets(original, enhanced)
            enhanced = normalize_resume_data(enhanced)
            return enhanced, changes, []
    except LLMQuotaError as e:
        logger.warning("LLM quota exhausted during delta enhancement — using rule-based fallback: %s", e)
    except Exception as e:
        logger.warning("LLM delta enhancement failed: %s", e)

    logger.warning("Using rule-based enhancement fallback")
    enhanced, changes = rule_enhance(original)
    enhanced = strip_invented_sections(original, enhanced)
    enhanced = ensure_project_coverage(original, enhanced)
    enhanced = ensure_experience_bullets(original, enhanced)
    enhanced = normalize_resume_data(enhanced)
    return enhanced, changes, []


def _try_full_rewrite(
    original: ResumeData,
    raw_text: str,
    quality: dict,
    temperature: float,
) -> tuple[Optional[ResumeData], list[dict], list[dict]]:
    user_prompt = RESUME_FULL_REWRITE_USER.format(
        original_json=json.dumps(original.model_dump(), indent=2),
        raw_text=raw_text[:12000],
        quality_tier=quality["tier"],
        quality_score=quality["quality_score"],
        quality_issues=", ".join(quality["issues"]) or "none",
    )
    result = call_llm(RESUME_FULL_REWRITE_SYSTEM, user_prompt, temperature=temperature)
    enhanced, changes, suggestions = _apply_full_rewrite(original, result)
    return enhanced, changes, suggestions


def _apply_full_rewrite(original: ResumeData, result: dict) -> tuple[ResumeData, list[dict], list[dict]]:
    payload = result.get("enhanced_resume") or result.get("resume")
    suggestions = result.get("suggestions") or []
    if not payload:
        return original, [], suggestions

    try:
        enhanced = ResumeData(**payload)
    except ValidationError as e:
        logger.warning("Invalid enhanced_resume from LLM: %s", e)
        return original, [], suggestions

    enhanced = _merge_original_identity(original, enhanced)
    enhanced = _ensure_experience_coverage(original, enhanced)
    enhanced = strip_invented_sections(original, enhanced)
    enhanced = ensure_project_coverage(original, enhanced)
    enhanced = ensure_experience_bullets(original, enhanced)
    enhanced = normalize_resume_data(enhanced)

    changes: list[dict] = []
    for entry in result.get("changes") or []:
        meta = _normalize_change(entry, entry.get("section", ""))
        if meta:
            changes.append(meta)

    if not changes:
        changes = _default_rewrite_changes(original, enhanced)

    return enhanced, changes, suggestions


def _merge_original_identity(original: ResumeData, enhanced: ResumeData) -> ResumeData:
    """Keep contact details and name from original when LLM omits them."""
    merged = deepcopy(enhanced)
    orig_p = original.personal
    out_p = merged.personal

    if not out_p.name.strip():
        out_p.name = orig_p.name
    for field in ("email", "phone", "location", "linkedin", "website", "github"):
        if not getattr(out_p, field) and getattr(orig_p, field):
            setattr(out_p, field, getattr(orig_p, field))
    if not out_p.title.strip() and orig_p.title.strip():
        out_p.title = orig_p.title

    return merged


def _ensure_experience_coverage(original: ResumeData, enhanced: ResumeData) -> ResumeData:
    """If LLM dropped jobs, append missing ones from original with cleaned bullets."""
    if not original.experience:
        return enhanced

    seen = {(e.company.lower(), e.title.lower()) for e in enhanced.experience}
    for job in original.experience:
        key = (job.company.lower(), job.title.lower())
        if key not in seen and job.company.lower() not in ("experience", "company"):
            enhanced.experience.append(deepcopy(job))
            seen.add(key)

    return enhanced


def _default_rewrite_changes(original: ResumeData, enhanced: ResumeData) -> list[dict]:
    """Generate change notes when LLM omits the changes array."""
    notes: list[dict] = []
    if enhanced.summary.strip() and enhanced.summary.strip() != (original.summary or "").strip():
        notes.append({
            "section": "summary",
            "why": "Rewrote summary for clearer role positioning and ATS readability.",
            "confidence": 88,
            "authenticity": "SAFE",
            "interview_risk": "LOW",
        })
    if enhanced.experience:
        notes.append({
            "section": "experience",
            "why": "Restructured experience bullets — one accomplishment per line with action verbs for ATS and recruiters.",
            "confidence": 90,
            "authenticity": "SAFE",
            "interview_risk": "LOW",
        })
    if enhanced.skills:
        notes.append({
            "section": "skills",
            "why": "Organized skills into a clean, scannable list for ATS keyword matching.",
            "confidence": 85,
            "authenticity": "SAFE",
            "interview_risk": "LOW",
        })
    return notes


def _normalize_change(entry: dict, section: str) -> Optional[dict]:
    why = (entry.get("why") or "").strip()
    if not why:
        return None
    return {
        "section": section or entry.get("section", ""),
        "why": why,
        "confidence": float(entry.get("confidence", 85)),
        "authenticity": entry.get("authenticity", "SAFE"),
        "interview_risk": entry.get("interview_risk", "LOW"),
    }


def _bullet_is_valid(original: str, enhanced: str) -> bool:
    if not enhanced.strip() or enhanced.strip() == original.strip():
        return False
    if is_vague_bullet(original):
        return validate_authenticity(original, enhanced) != "UNVERIFIABLE"
    auth = validate_authenticity(original, enhanced)
    return auth != "UNVERIFIABLE"


def _apply_enhancement_deltas(original: ResumeData, result: dict) -> tuple[ResumeData, list[dict]]:
    enhanced = deepcopy(original)
    changes: list[dict] = []

    if "sections" in result and "enhancements" not in result and "enhanced_resume" not in result:
        return _apply_legacy_sections(original, result)

    if "enhanced_resume" in result:
        enhanced, changes, suggestions = _apply_full_rewrite(original, result)
        return enhanced, changes

    enhancements = result.get("enhancements") or []

    for entry in enhancements:
        section = entry.get("section", "")
        change_meta = _normalize_change(entry, section)
        if not change_meta:
            continue

        if section == "summary" and entry.get("enhanced_text"):
            text = entry["enhanced_text"].strip()
            if text and text != enhanced.summary.strip():
                enhanced.summary = text
                changes.append(change_meta)

        elif section == "experience":
            job_idx = entry.get("job_index", 0)
            append_text = (entry.get("append_bullet") or "").strip()
            if append_text and job_idx < len(enhanced.experience):
                enhanced.experience[job_idx].bullets.append(append_text)
                changes.append(change_meta)
                continue

            bullet_idx = entry.get("bullet_index", 0)
            text = (entry.get("enhanced_text") or "").strip()
            if (
                text
                and job_idx < len(enhanced.experience)
                and bullet_idx < len(enhanced.experience[job_idx].bullets)
            ):
                orig_bullet = enhanced.experience[job_idx].bullets[bullet_idx]
                if _bullet_is_valid(orig_bullet, text):
                    enhanced.experience[job_idx].bullets[bullet_idx] = text
                    changes.append(change_meta)

        elif section == "skills" and entry.get("append_skills"):
            merged = list(enhanced.skills)
            added = False
            existing = {s.lower() for s in merged}
            for skill in entry["append_skills"]:
                if skill and skill.lower() not in existing:
                    merged.append(skill)
                    existing.add(skill.lower())
                    added = True
            if added:
                enhanced.skills = merged
                changes.append(change_meta)

        elif section == "projects":
            if entry.get("append_project"):
                proj_data = entry["append_project"]
                title = (proj_data.get("title") or "").strip()
                if title and title.lower() not in {p.title.lower() for p in enhanced.projects}:
                    enhanced.projects.append(
                        ProjectItem(
                            title=title,
                            description=proj_data.get("description", ""),
                            tech_stack=proj_data.get("tech_stack") or [],
                            url=proj_data.get("url"),
                            status=proj_data.get("status") or "SUGGESTED PROJECT",
                        )
                    )
                    changes.append(change_meta)

            proj_idx = entry.get("project_index")
            desc = (entry.get("enhanced_description") or entry.get("enhanced_text") or "").strip()
            if desc and proj_idx is not None and proj_idx < len(enhanced.projects):
                orig_desc = enhanced.projects[proj_idx].description or ""
                if desc != orig_desc.strip():
                    enhanced.projects[proj_idx].description = desc
                    changes.append(change_meta)

        elif section == "education" and entry.get("enhanced_text"):
            change_meta["section"] = "education"
            changes.append(change_meta)

    return enhanced, changes


def _apply_legacy_sections(original: ResumeData, result: dict) -> tuple[ResumeData, list[dict]]:
    enhanced = deepcopy(original)
    changes: list[dict] = []
    sections = result.get("sections", {})

    summary_block = sections.get("summary", {})
    content = (summary_block.get("content") or "").strip()
    if content and content != original.summary.strip():
        enhanced.summary = content
        for c in summary_block.get("changes", []):
            meta = _normalize_change(c, "summary")
            if meta:
                changes.append(meta)

    exp_block = sections.get("experience", {})
    items = exp_block.get("items") or []
    for i, item in enumerate(items):
        if i >= len(enhanced.experience):
            break
        bullets = item.get("bullets") or []
        for j, new_b in enumerate(bullets):
            if j >= len(enhanced.experience[i].bullets):
                break
            orig_b = enhanced.experience[i].bullets[j]
            if _bullet_is_valid(orig_b, new_b):
                enhanced.experience[i].bullets[j] = new_b.strip()
    for c in exp_block.get("changes", []):
        meta = _normalize_change(c, "experience")
        if meta:
            changes.append(meta)

    skills_block = sections.get("skills", {})
    for s in skills_block.get("items") or []:
        if s.lower() not in {x.lower() for x in enhanced.skills}:
            enhanced.skills.append(s)
    for c in skills_block.get("changes", []):
        meta = _normalize_change(c, "skills")
        if meta:
            changes.append(meta)

    proj_block = sections.get("projects", {})
    for item in proj_block.get("items") or []:
        title = item.get("title", "")
        if title.lower() not in {p.title.lower() for p in enhanced.projects}:
            enhanced.projects.append(ProjectItem(**item))

    return enhanced, changes
