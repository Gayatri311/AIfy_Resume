from contextlib import asynccontextmanager
import logging
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import engine, Base
from app.api.routes import resumes

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_host = urlparse(settings.database_url).hostname or "unknown"
    if db_host in ("localhost", "127.0.0.1") and not settings.debug:
        logger.error(
            "DATABASE_URL points to %s — Postgres is not reachable inside Railway. "
            "Add a Postgres plugin and reference its DATABASE_URL on this service.",
            db_host,
        )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
    return {"status": "ok", "service": "alfy-resume-api"}
