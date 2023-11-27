from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings

sql_url = (
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@"
    f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_async_engine(sql_url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def run_upgrade(connection, cfg) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def run_async_upgrade() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, Config("api/alembic.ini"))
