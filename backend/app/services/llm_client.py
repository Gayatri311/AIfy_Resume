import json
import logging
import re

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "google": "gemini-2.5-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-20250514",
}


class LLMQuotaError(RuntimeError):
    """Raised when the LLM provider rate-limits or quota is exhausted."""


class LLMError(RuntimeError):
    """Raised when an LLM call fails for a non-quota reason."""


def _provider() -> str:
    return (settings.llm_provider or "gemini").strip().lower()


def llm_available() -> bool:
    provider = _provider()
    if provider in ("gemini", "google"):
        return bool(settings.google_api_key)
    if provider == "openai":
        return bool(settings.openai_api_key)
    if provider == "anthropic":
        return bool(settings.anthropic_api_key)
    return bool(settings.google_api_key or settings.openai_api_key or settings.anthropic_api_key)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _resolve_model(provider: str) -> str:
    if settings.llm_model:
        return settings.llm_model
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS["gemini"])


def _is_quota_error(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    return (
        "resourceexhausted" in name
        or "429" in msg
        or "quota" in msg
        or "rate limit" in msg
        or "rate_limit" in msg
    )


def _wrap_llm_error(exc: Exception) -> Exception:
    if _is_quota_error(exc):
        return LLMQuotaError(str(exc))
    return LLMError(str(exc))


def call_llm(system: str, user: str, temperature: float = 0.2) -> dict:
    """Call configured LLM and parse JSON response. Fails fast on quota errors (no long retries)."""
    provider = _provider()

    try:
        if provider in ("gemini", "google"):
            if not settings.google_api_key:
                raise RuntimeError("GOOGLE_API_KEY is not configured")
            return _call_gemini(system, user, temperature)

        if provider == "openai":
            if not settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured")
            return _call_openai(system, user, temperature)

        if provider == "anthropic":
            if not settings.anthropic_api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is not configured")
            return _call_anthropic(system, user, temperature)

        if settings.google_api_key:
            return _call_gemini(system, user, temperature)
        if settings.openai_api_key:
            return _call_openai(system, user, temperature)
        if settings.anthropic_api_key:
            return _call_anthropic(system, user, temperature)

        raise RuntimeError("No LLM API key configured")
    except (LLMQuotaError, LLMError, RuntimeError):
        raise
    except Exception as exc:
        raise _wrap_llm_error(exc) from exc


def _call_gemini(system: str, user: str, temperature: float) -> dict:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import SystemMessage, HumanMessage

    llm = ChatGoogleGenerativeAI(
        model=_resolve_model("gemini"),
        google_api_key=settings.google_api_key,
        temperature=temperature,
        max_retries=0,
        timeout=90,
    )
    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    except Exception as exc:
        raise _wrap_llm_error(exc) from exc
    content = response.content if isinstance(response.content, str) else str(response.content)
    return _extract_json(content)


def _call_openai(system: str, user: str, temperature: float) -> dict:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    llm = ChatOpenAI(
        model=_resolve_model("openai"),
        api_key=settings.openai_api_key,
        temperature=temperature,
        max_retries=0,
        timeout=90,
    )
    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    except Exception as exc:
        raise _wrap_llm_error(exc) from exc
    content = response.content if isinstance(response.content, str) else str(response.content)
    return _extract_json(content)


def _call_anthropic(system: str, user: str, temperature: float) -> dict:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import SystemMessage, HumanMessage

    model = settings.llm_model or DEFAULT_MODELS["anthropic"]
    if "claude" not in model.lower():
        model = DEFAULT_MODELS["anthropic"]

    llm = ChatAnthropic(
        model=model,
        api_key=settings.anthropic_api_key,
        temperature=temperature,
        max_retries=0,
        timeout=90,
    )
    try:
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    except Exception as exc:
        raise _wrap_llm_error(exc) from exc
    content = response.content if isinstance(response.content, str) else str(response.content)
    return _extract_json(content)
