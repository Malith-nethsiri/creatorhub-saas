from sqlalchemy.orm import Session
from typing import List
from app.models.analytics import AnalyticsData
from app.models.user import User

def get_user_analytics(db: Session, user: User) -> List[AnalyticsData]:
    return (
        db.query(AnalyticsData)
        .filter(AnalyticsData.user_id == user.id)
        .all()
    )

def get_platform_analytics(db: Session, user: User, platform: str) -> AnalyticsData:
    return (
        db.query(AnalyticsData)
        .filter(
            AnalyticsData.user_id == user.id,
            AnalyticsData.platform == platform
        )
        .first()
    )
