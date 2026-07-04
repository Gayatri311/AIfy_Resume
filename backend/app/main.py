from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Optional
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import (
    get_settings,
    is_railway_runtime,
    database_url_is_localhost,
    database_env_status,
)
from app.core.database import engine, Base, db_target_label
from app.api.routes import resumes

settings = get_settings()
logger = logging.getLogger(__name__)

_STARTUP_DB_ATTEMPTS = 15
_STARTUP_DB_DELAY_SEC = 2


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Database env: %s", database_env_status())

    if is_railway_runtime() and database_url_is_localhost(settings.database_url):
        logger.error(
            "DATABASE_URL is NOT injected into this Railway container (using localhost). "
            "You likely set it on the Postgres service instead of the API service. "
            "Fix: API/backend service → Variables → + New Variable → Add Reference → "
            "PostgreSQL → DATABASE_URL → Save → Redeploy THIS service."
        )
        raise RuntimeError("DATABASE_URL missing on Railway backend service")

    db_host = urlparse(settings.database_url).hostname or "unknown"
    if database_url_is_localhost(settings.database_url) and not settings.debug:
        logger.error(
            "DATABASE_URL points to %s — set a real Postgres URL before running in production.",
            db_host,
        )
    else:
        logger.info("Database target: %s", db_target_label(settings.database_url))

    last_error: Optional[Exception] = None
    for attempt in range(1, _STARTUP_DB_ATTEMPTS + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            if attempt > 1:
                logger.info("Database connected on attempt %s", attempt)
            break
        except Exception as exc:
            last_error = exc
            if attempt >= _STARTUP_DB_ATTEMPTS:
                logger.error(
                    "Database unreachable after %s attempts (%s). "
                    "Check Postgres is Active, DATABASE_URL is on the backend service, "
                    "and public URLs use the proxy port (not 5432).",
                    _STARTUP_DB_ATTEMPTS,
                    db_target_label(settings.database_url),
                )
                raise last_error from exc
            logger.warning(
                "Database not ready (attempt %s/%s): %s",
                attempt,
                _STARTUP_DB_ATTEMPTS,
                exc,
            )
            await asyncio.sleep(_STARTUP_DB_DELAY_SEC)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes.router, prefix="/api/v1")


@app.get("/health")
async def health():
    from urllib.parse import urlparse

    db_host = urlparse(settings.database_url.replace("+asyncpg", "")).hostname or "unknown"
    return {
        "status": "ok",
        "service": "alfy-resume-api",
        "db_host": db_host,
        "db_env": database_env_status(),
    }
