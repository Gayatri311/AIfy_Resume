from typing import Optional

from fastapi import Header, HTTPException

SESSION_HEADER = "x-alfy-session"


def require_session_id(x_alfy_session: Optional[str] = Header(None, alias=SESSION_HEADER)) -> str:
    if not x_alfy_session or len(x_alfy_session.strip()) < 8:
        raise HTTPException(
            400,
            "Missing session ID. Ensure the app sends the X-Alfy-Session header.",
        )
    return x_alfy_session.strip()


def optional_session_id(x_alfy_session: Optional[str] = Header(None, alias=SESSION_HEADER)) -> Optional[str]:
    if x_alfy_session and len(x_alfy_session.strip()) >= 8:
        return x_alfy_session.strip()
    return None
