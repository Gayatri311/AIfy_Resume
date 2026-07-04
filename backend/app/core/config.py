import os
from functools import lru_cache
from typing import Optional

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

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: Optional[str]) -> str:
        v = (
            os.environ.get("DATABASE_URL")
            or os.environ.get("DATABASE_PRIVATE_URL")
            or v
            or "postgresql+asyncpg://alfy:alfy@localhost:5432/alfy_resume"
        )
        return _to_asyncpg_url(v)

    @field_validator("database_url_sync", mode="before")
    @classmethod
    def normalize_database_url_sync(cls, v: Optional[str]) -> str:
        v = (
            os.environ.get("DATABASE_URL")
            or os.environ.get("DATABASE_PRIVATE_URL")
            or v
            or "postgresql://alfy:alfy@localhost:5432/alfy_resume"
        )
        return _to_sync_pg_url(v)


@lru_cache
def get_settings() -> Settings:
    return Settings()
