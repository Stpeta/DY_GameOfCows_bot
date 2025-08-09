from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models import Base

DATABASE_URL = "sqlite+aiosqlite:///database.db"

engine = create_async_engine(DATABASE_URL, echo=False)
# Session factory used across the project
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
async_session_maker = AsyncSessionLocal


async def init_db() -> None:
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Provide a transactional scope around a series of operations."""
    async with async_session_maker() as session:
        yield session

