from pydantic_settings import BaseSettings
from functools import lru_cache


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


@lru_cache
def get_settings() -> Settings:
    return Settings()
