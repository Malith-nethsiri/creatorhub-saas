import logging
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, AsyncSessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)

# =========================================================
# ✅ Reset Monthly Usage Task
# =========================================================
async def reset_monthly_usage() -> None:
    """
    Resets monthly usage counters for all users.
    Triggered by Celery Beat every 1st of the month (00:00 UTC).
    """
    logger.info("STAGE ✅: Starting monthly quota reset for all users...")

    async with AsyncSessionLocal() as session:
        try:
            now = datetime.utcnow()

            # ✅ Bulk update instead of looping all users
            stmt = (
                update(User)
                .values(
                    content_ideas_used_this_month=0,
                    video_repurposing_used_this_month=0,
                    copyright_alerts_used_this_month=0,
                    last_usage_reset=now
                )
            )
            await session.execute(stmt)
            await session.commit()

            logger.info("✅ Monthly usage counters reset successfully for all users.")

        except Exception as e:
            logger.error(f"❌ Monthly quota reset failed: {e}")
            await session.rollback()
            raise

