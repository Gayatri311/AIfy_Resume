from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()


def db_target_label(database_url: str) -> str:
    parsed = urlparse(database_url.replace("+asyncpg", ""))
    host = parsed.hostname or "unknown"
    port = parsed.port or 5432
    ssl = "ssl" if _connect_args(database_url) else "no-ssl"
    return f"{host}:{port} ({ssl})"


def _connect_args(database_url: str) -> dict:
    """Railway public Postgres proxies require SSL; internal *.railway.internal does not."""
    host = urlparse(database_url.replace("+asyncpg", "")).hostname or ""
    if host.endswith(".railway.app") or "proxy.rlwy.net" in host:
        return {"ssl": True}
    return {}


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=_connect_args(settings.database_url),
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
