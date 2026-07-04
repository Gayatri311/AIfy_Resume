from typing import Optional

"""Server-side plan limits — must match frontend/src/lib/pricing.ts."""

FREE_REVIEW_SECTIONS = frozenset({"summary", "experience"})
FREE_INTERVIEW_QUESTIONS = 3
PRO_STATUSES = frozenset({"active", "trialing"})


def is_pro(plan: str, status: str) -> bool:
    return plan == "pro" and status in PRO_STATUSES


def can_access_section(section: str, plan: str, status: str) -> bool:
    if is_pro(plan, status):
        return True
    return section in FREE_REVIEW_SECTIONS


def interview_question_limit(plan: str, status: str) -> Optional[int]:
    if is_pro(plan, status):
        return None
    return FREE_INTERVIEW_QUESTIONS


def export_needs_watermark(plan: str, status: str) -> bool:
    return not is_pro(plan, status)
