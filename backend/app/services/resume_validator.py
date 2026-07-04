import re
from typing import Optional

from app.schemas.resume import ResumeData
from app.services.exceptions import ResumeValidationError, RESUME_NOT_VALID_MESSAGE
from app.services.llm_client import llm_available, call_llm
from app.agents.prompts import RESUME_VALIDATION_SYSTEM, RESUME_VALIDATION_USER

RESUME_KEYWORDS = re.compile(
    r"\b(experience|employment|work history|education|skills|resume|curriculum vitae|cv\b|"
    r"professional summary|objective|certification|projects|responsibilities|"
    r"achievements|bachelor|master|mba|engineer|manager|developer|analyst|intern|"
    r"university|linkedin|proficient|proficiency)\b",
    re.I,
)

NON_RESUME_KEYWORDS = re.compile(
    r"\b(invoice|receipt|purchase order|terms and conditions|dear sir|dear hiring manager|"
    r"cover letter only|table of contents|chapter \d|abstract\s*:|research paper|"
    r"bill to:|ship to:|total amount due|payment due)\b",
    re.I,
)


def validate_resume_text(raw_text: str, parsed: Optional[ResumeData] = None) -> None:
    """Raise ResumeValidationError if document does not appear to be a resume."""
    text = (raw_text or "").strip()
    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))

    if len(text) < 80:
        raise ResumeValidationError()
    if len(text) < 120 and not has_email:
        raise ResumeValidationError()

    if NON_RESUME_KEYWORDS.search(text) and not RESUME_KEYWORDS.search(text):
        raise ResumeValidationError()

    resume_signals = 0
    if RESUME_KEYWORDS.search(text):
        resume_signals += 1
    if has_email:
        resume_signals += 1
    if re.search(r"\b(19|20)\d{2}\b", text):
        resume_signals += 1
    if re.search(r"\b(present|current)\b", text, re.I):
        resume_signals += 1

    has_experience = parsed and len(parsed.experience) > 0
    has_education = parsed and len(parsed.education) > 0
    has_skills = parsed and len(parsed.skills) >= 3
    has_summary = parsed and len(parsed.summary) > 40

    if has_experience:
        resume_signals += 2
    if has_education:
        resume_signals += 1
    if has_skills:
        resume_signals += 1
    if has_summary:
        resume_signals += 1

    # Need at least experience OR (education + skills) OR reasonable text signals
    career_content = (
        has_experience
        or (has_education and has_skills)
        or resume_signals >= 3
        or (has_email and len(text) >= 120 and RESUME_KEYWORDS.search(text))
    )

    if not career_content:
        raise ResumeValidationError()

    # LLM double-check only for ambiguous uploads — avoid rejecting good resumes in production
    ambiguous = career_content and not has_experience and not has_education and resume_signals < 4
    if llm_available() and ambiguous:
        _llm_validate(text)


def _llm_validate(text: str) -> None:
    try:
        snippet = text[:8000]
        result = call_llm(
            RESUME_VALIDATION_SYSTEM,
            RESUME_VALIDATION_USER.format(document_text=snippet),
            temperature=0,
        )
        if not result.get("is_resume", False):
            reason = result.get("reason", "")
            if reason:
                raise ResumeValidationError(
                    f"{RESUME_NOT_VALID_MESSAGE} ({reason})"
                )
            raise ResumeValidationError()
    except ResumeValidationError:
        raise
    except Exception:
        # If LLM fails, trust heuristic validation
        pass
