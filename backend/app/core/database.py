import ssl
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()


def _railway_public_host(host: str) -> bool:
    return host.endswith(".railway.app") or "proxy.rlwy.net" in host


def db_target_label(database_url: str) -> str:
    parsed = urlparse(database_url.replace("+asyncpg", ""))
    host = parsed.hostname or "unknown"
    port = parsed.port or 5432
    if _railway_public_host(host):
        mode = "ssl"
    elif _connect_args(database_url):
        mode = "ssl"
    else:
        mode = "no-ssl"
    return f"{host}:{port} ({mode})"


def _connect_args(database_url: str) -> dict:
    """Railway public Postgres proxies require SSL with relaxed cert verify."""
    host = urlparse(database_url.replace("+asyncpg", "")).hostname or ""
    if _railway_public_host(host):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return {"ssl": ctx}
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
