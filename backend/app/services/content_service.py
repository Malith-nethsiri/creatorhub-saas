import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import GeneratedContent, ContentType

logger = logging.getLogger(__name__)


class ContentService:
    # =========================================================
    # ✅ FETCH USER CONTENT HISTORY (ASYNC + OPTIMIZED)
    # =========================================================
    async def get_user_content_history(
        self,
        db: AsyncSession,
        user_id: UUID,
        content_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[GeneratedContent]:
        """
        Fetch user's generated content history with optional filtering.
        Fully async & optimized for large datasets.
        """
        try:
            logger.info(f"STAGE ✅: Fetching content history for {user_id} | Limit={limit}, Offset={offset}")

            stmt = select(GeneratedContent).where(GeneratedContent.user_id == user_id)

            if content_type:
                try:
                    stmt = stmt.where(GeneratedContent.content_type == ContentType(content_type))
                except ValueError:
                    logger.warning(f"❌ Invalid content_type '{content_type}', returning empty list.")
                    return []

            stmt = stmt.order_by(GeneratedContent.created_at.desc()).offset(offset).limit(limit)
            result = await db.execute(stmt)
            records = result.scalars().all()

            logger.info(f"STAGE ✅: Retrieved {len(records)} records for {user_id}")
            return list(records)

        except Exception as e:
            logger.error(f"❌ Error fetching content history for {user_id}: {e}")
            return []

    # =========================================================
    # ✅ DELETE USER CONTENT (ASYNC + SAFE)
    # =========================================================
    async def delete_user_content(
        self,
        db: AsyncSession,
        content_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a specific content record belonging to the user.
        Fully async & rollback-safe.
        """
        try:
            logger.info(f"STAGE ✅: Attempting to delete content {content_id} for user {user_id}")

            stmt = delete(GeneratedContent).where(
                GeneratedContent.id == content_id,
                GeneratedContent.user_id == user_id
            ).execution_options(synchronize_session="fetch")

            result = await db.execute(stmt)

            if result.rowcount == 0:
                logger.warning(f"❌ Content {content_id} not found for user {user_id}")
                return False

            await db.commit()
            logger.info(f"✅ Content {content_id} deleted for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error deleting content {content_id} for {user_id}: {e}")
            await db.rollback()
            return False

    # =========================================================
    # ✅ FUTURE: BULK INSERT (FOR IDEA GENERATION)
    # =========================================================
    async def bulk_insert_content(
        self,
        db: AsyncSession,
        content_records: List[GeneratedContent]
    ) -> bool:
        """
        Bulk insert generated content records (optimized for large idea generation batches).
        """
        try:
            logger.info(f"STAGE ✅: Bulk inserting {len(content_records)} content records...")
            db.add_all(content_records)
            await db.commit()
            logger.info("✅ Bulk insert successful.")
            return True
        except Exception as e:
            logger.error(f"❌ Bulk insert failed: {e}")
            await db.rollback()
            return False


# ✅ GLOBAL INSTANCE (import this directly in routes)
content_service = ContentService()
