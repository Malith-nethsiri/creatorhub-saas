import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from app.core.config import settings

logger = logging.getLogger(__name__)

# =========================================================
# ✅ Create Async Engine (Production Pool Settings)
# =========================================================
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# ✅ Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# ✅ Base Class for Models
Base = declarative_base()
metadata = Base.metadata


# =========================================================
# ✅ FastAPI Dependency (Async)
# =========================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session for FastAPI (routes control commits)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"❌ Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# =========================================================
# ✅ Create Tables (Dev Only)
# =========================================================
async def create_tables():
    """Create tables (dev only; use Alembic in production)."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


# =========================================================
# ✅ Sync Fallback (Only for Scripts/Tests)
# =========================================================
def get_db_sync():
    raise NotImplementedError("Use async sessions in production")
