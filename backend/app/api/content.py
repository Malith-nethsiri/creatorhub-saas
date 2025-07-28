import os
import traceback
import logging
import asyncio
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form, status
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

# Core & Models
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.content import GeneratedContent, ContentType
from app.schemas.content import (
    ContentIdeaRequest,
    ContentIdeaResponse,
    VideoRepurposeResponse,
    ContentHistoryResponse,
)
from app.services.ai_service import ai_service
from app.services.content_service import content_service

router = APIRouter()
logger = logging.getLogger(__name__)

# =========================================================
# ✅ GENERATE CONTENT IDEAS (ASYNC)
# =========================================================
@router.post("/generate-ideas", response_model=List[ContentIdeaResponse])
async def generate_content_ideas(
    request: ContentIdeaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"===== [DEBUG] Generating content ideas for user: {current_user.email} =====")

    if not current_user.can_generate_content_ideas():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Monthly content idea limit reached",
                "current_plan": current_user.subscription_plan.value,
                "upgrade_required": True
            }
        )

    def safe_str(field): return str(field) if field else ""

    try:
        niche = request.niche or safe_str(current_user.primary_niche)
        audience = request.audience or safe_str(current_user.target_audience)

        logger.info(f"STAGE ✅: Requesting AI Service: Topic={request.topic}, Niche={niche}, Audience={audience}")
        ideas = await ai_service.generate_content_ideas(
            topic=request.topic,
            niche=niche,
            audience=audience,
            count=min(request.count, 10),
            platform=request.platform
        )

        saved_ideas: List[ContentIdeaResponse] = []

        for idea in ideas:
            content_id = uuid4()
            user_id = UUID(str(current_user.id))
            content_record = GeneratedContent(
                id=content_id,
                user_id=user_id,
                content_type=ContentType.IDEA,
                title=idea.get("title", ""),
                content=idea.get("description", ""),
                metadata={
                    "topic": request.topic,
                    "niche": request.niche,
                    "platform": request.platform,
                    "engagement_potential": idea.get("engagement_score", 0)
                }
            )
            db.add(content_record)

            saved_ideas.append(
                ContentIdeaResponse(
                    id=content_id,
                    title=idea.get("title", ""),
                    description=idea.get("description", ""),
                    engagement_score=idea.get("engagement_score", 0),
                    hashtags=idea.get("hashtags", []),
                    platform_optimized=request.platform
                )
            )

        current_user.increment_content_ideas_used()
        await db.commit()

        logger.info(f"✅ Successfully generated & saved {len(saved_ideas)} ideas for {current_user.email}")
        return saved_ideas

    except Exception as e:
        logger.error(f"❌ Error generating content ideas: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to generate content ideas.")


# =========================================================
# ✅ REPURPOSE VIDEO CONTENT (ASYNC)
# =========================================================
@router.post("/repurpose-video", response_model=VideoRepurposeResponse)
async def repurpose_video_content(
    video_file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    target_platforms: str = Form("youtube,instagram,tiktok"),
    tone: str = Form("professional"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    trace_id = f"repurpose-{uuid4()}"
    logger.info(f"===== [TRACE {trace_id}] Starting video repurpose for {current_user.email} =====")

    if not current_user.can_repurpose_video():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Monthly video repurposing limit reached",
                "current_plan": current_user.subscription_plan.value,
                "upgrade_required": True
            }
        )

    valid_ext = (".mp4", ".m4a", ".mp3", ".wav", ".webm", ".mpeg", ".ogg", ".flac")
    if not video_file.filename.lower().endswith(valid_ext):
        raise HTTPException(status_code=400, detail="File must be a valid audio/video format")

    try:
        transcript = None
        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[TRACE {trace_id}] STAGE ✅: Transcription attempt {attempt}...")
                transcript = await ai_service.transcribe_video(video_file)
                if transcript and len(transcript.strip()) > 20:
                    logger.info(f"[TRACE {trace_id}] STAGE ✅: Transcription succeeded")
                    break
                else:
                    raise Exception("Transcript too short or empty.")
            except Exception as e:
                logger.error(f"[TRACE {trace_id}] ❌ Whisper attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    raise HTTPException(status_code=500, detail="Failed to transcribe video after retries.")
                await asyncio.sleep(2)

        platforms = [p.strip().lower() for p in target_platforms.split(",") if p.strip()]
        logger.info(f"[TRACE {trace_id}] STAGE ✅: Starting repurposing for platforms: {platforms}")
        repurposed_content = {}

        for platform in platforms:
            try:
                repurposed = await ai_service.repurpose_content(
                    transcript=transcript,
                    original_title=title,
                    original_description=description or "",
                    target_platforms=[platform],
                    tone=tone
                )
                repurposed_content[platform] = repurposed.get(platform, "")
                logger.info(f"[TRACE {trace_id}] STAGE ✅: Repurposing success for {platform}")
            except Exception as e:
                logger.error(f"[TRACE {trace_id}] ❌ Repurposing failed for {platform}: {e}")
                repurposed_content[platform] = f"Fallback snippet: {transcript[:120]}..."

        content_id = uuid4()
        user_id = UUID(str(current_user.id))

        content_record = GeneratedContent(
            id=content_id,
            user_id=user_id,
            content_type=ContentType.REPURPOSED_VIDEO,
            title=title,
            content=transcript,
            metadata={
                "trace_id": trace_id,
                "original_file": video_file.filename,
                "platforms": platforms,
                "tone": tone,
                "repurposed_content": repurposed_content
            }
        )
        db.add(content_record)
        current_user.increment_video_repurposing_used()
        await db.commit()

        logger.info(f"[TRACE {trace_id}] ✅ Video repurposed successfully for {current_user.email}")

        return VideoRepurposeResponse(
            id=content_id,
            original_title=title,
            transcript=transcript,
            repurposed_content=repurposed_content,
            platforms_generated=platforms
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TRACE {trace_id}] ❌ Pipeline error: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")


# =========================================================
# ✅ CONTENT HISTORY (ASYNC)
# =========================================================
@router.get("/history", response_model=List[ContentHistoryResponse])
async def get_content_history(
    content_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"===== [DEBUG] Fetching content history for {current_user.email} =====")
        limit = min(limit, 100)
        history = await content_service.get_user_content_history(
            db=db,
            user_id=UUID(str(current_user.id)),
            content_type=content_type,
            limit=limit,
            offset=offset
        )

        return [
            ContentHistoryResponse(
                id=UUID(str(item.id)),
                content_type=str(item.content_type.value) if hasattr(item.content_type, "value") else "",
                title=item.title or "",
                created_at=item.created_at if isinstance(item.created_at, datetime) else datetime.utcnow(),
                metadata=item.metadata or {}
            )
            for item in history
        ]

    except Exception as e:
        logger.error(f"❌ Error fetching content history: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to fetch content history")


# =========================================================
# ✅ DELETE CONTENT (ASYNC)
# =========================================================
@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"===== [DEBUG] Deleting content {content_id} for {current_user.email} =====")
        stmt = select(GeneratedContent).where(
            GeneratedContent.id == UUID(content_id),
            GeneratedContent.user_id == current_user.id
        )
        result = await db.execute(stmt)
        content = result.scalars().first()

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        await db.delete(content)
        await db.commit()
        logger.info(f"✅ Content {content_id} deleted for {current_user.email}")
        return {"message": "Content deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting content: {e}")
        logger.error(traceback.format_exc())
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete content")
