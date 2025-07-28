from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.analytics import AnalyticsData
from app.schemas.analytics import AnalyticsResponse
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[AnalyticsResponse])
def get_user_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    analytics = (
        db.query(AnalyticsData)
        .filter(AnalyticsData.user_id == current_user.id)
        .all()
    )
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analytics data found for this user."
        )
    return analytics


@router.get("/{platform}", response_model=AnalyticsResponse)
def get_platform_analytics(
    platform: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    analytics = (
        db.query(AnalyticsData)
        .filter(
            AnalyticsData.user_id == current_user.id,
            AnalyticsData.platform == platform
        )
        .first()
    )
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analytics data found for platform '{platform}'."
        )
    return analytics
