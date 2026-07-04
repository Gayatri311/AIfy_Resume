import os
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings


def _to_asyncpg_url(url: str) -> str:
    url = url.strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _to_sync_pg_url(url: str) -> str:
    url = url.strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


def _env(name: str) -> Optional[str]:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _postgres_url_from_parts() -> Optional[str]:
    """Railway sometimes exposes PGHOST/PGPORT/... instead of DATABASE_URL on the API service."""
    host = _env("PGHOST")
    if not host:
        return None
    user = _env("PGUSER") or "postgres"
    password = _env("PGPASSWORD") or ""
    port = _env("PGPORT") or "5432"
    database = _env("PGDATABASE") or "railway"
    auth = f"{user}:{password}@" if password else f"{user}@"
    return f"postgresql://{auth}{host}:{port}/{database}"


def _env_status(name: str) -> str:
    if name not in os.environ:
        return "missing"
    if not os.environ[name].strip():
        return "empty"
    return "set"


def resolve_database_url(from_settings: Optional[str] = None) -> str:
    env_url = (
        _env("DATABASE_URL")
        or _env("DATABASE_PRIVATE_URL")
        or _env("POSTGRES_URL")
        or _postgres_url_from_parts()
    )
    if env_url:
        return _to_asyncpg_url(env_url)
    if from_settings and from_settings.strip() and not database_url_is_localhost(from_settings):
        return _to_asyncpg_url(from_settings.strip())
    if from_settings and from_settings.strip():
        return _to_asyncpg_url(from_settings.strip())
    return _to_asyncpg_url("postgresql+asyncpg://alfy:alfy@localhost:5432/alfy_resume")


def is_railway_runtime() -> bool:
    return bool(_env("RAILWAY_ENVIRONMENT") or _env("RAILWAY_PROJECT_ID"))


def resolve_database_url_sync(from_settings: Optional[str] = None) -> str:
    env_url = (
        _env("DATABASE_URL")
        or _env("DATABASE_PRIVATE_URL")
        or _env("POSTGRES_URL")
        or _postgres_url_from_parts()
    )
    if env_url:
        return _to_sync_pg_url(env_url)
    if from_settings and from_settings.strip():
        return _to_sync_pg_url(from_settings.strip())
    return _to_sync_pg_url("postgresql://alfy:alfy@localhost:5432/alfy_resume")


def database_env_status() -> str:
    names = (
        "DATABASE_URL",
        "DATABASE_PRIVATE_URL",
        "POSTGRES_URL",
        "PGHOST",
        "PGPORT",
        "PGUSER",
        "PGPASSWORD",
        "PGDATABASE",
    )
    parts = [f"{name}={_env_status(name)}" for name in names]
    related = sorted(k for k in os.environ if "DATABASE" in k.upper() or k.startswith("PG"))
    if related:
        parts.append("keys=" + ",".join(related))
    return ", ".join(parts)


def database_url_is_localhost(url: str) -> bool:
    host = urlparse(url.replace("+asyncpg", "")).hostname or ""
    return host in ("localhost", "127.0.0.1")


class Settings(BaseSettings):
    app_name: str = "Alfy Resume API"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://alfy:alfy@localhost:5432/alfy_resume"
    database_url_sync: str = "postgresql://alfy:alfy@localhost:5432/alfy_resume"
    redis_url: str = "redis://localhost:6379/0"
    google_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash"
    supabase_url: str = ""
    supabase_key: str = ""
    cors_origins: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    max_upload_mb: int = 10
    use_celery: bool = False

    # Stripe billing
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_monthly: str = ""
    stripe_price_yearly: str = ""

    model_config = {
        "env_file": None if os.environ.get("RAILWAY_ENVIRONMENT") else ".env",
        "extra": "ignore",
    }

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: Optional[str]) -> str:
        return resolve_database_url(v if isinstance(v, str) else None)

    @field_validator("database_url_sync", mode="before")
    @classmethod
    def normalize_database_url_sync(cls, v: Optional[str]) -> str:
        return resolve_database_url_sync(v if isinstance(v, str) else None)


@lru_cache
def get_settings() -> Settings:
    return Settings()
