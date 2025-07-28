from sqlalchemy.orm import Session
from typing import List
from app.models.copyright import CopyrightMonitor
from app.schemas.copyright import CopyrightViolationCreate
from app.models.user import User

def get_user_copyright_violations(db: Session, user: User) -> List[CopyrightMonitor]:
    return (
        db.query(CopyrightMonitor)
        .filter(CopyrightMonitor.user_id == user.id)
        .all()
    )

def log_copyright_violation(
    db: Session, user: User, violation_data: CopyrightViolationCreate
) -> CopyrightMonitor:
    new_violation = CopyrightMonitor(
        user_id=user.id,
        platform=violation_data.platform,
        content_url=violation_data.content_url,
        detected_at=violation_data.detected_at,
        status=violation_data.status,
    )
    db.add(new_violation)
    db.commit()
    db.refresh(new_violation)
    return new_violation

def get_copyright_violation(
    db: Session, user: User, violation_id: int
) -> CopyrightMonitor:
    return (
        db.query(CopyrightMonitor)
        .filter(
            CopyrightMonitor.id == violation_id,
            CopyrightMonitor.user_id == user.id
        )
        .first()
    )
