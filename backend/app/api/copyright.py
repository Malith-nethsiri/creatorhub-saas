from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.copyright import CopyrightMonitor
from app.schemas.copyright import CopyrightViolationResponse, CopyrightViolationCreate
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CopyrightViolationResponse])
def get_user_copyright_violations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    violations = (
        db.query(CopyrightMonitor)
        .filter(CopyrightMonitor.user_id == current_user.id)
        .all()
    )
    if not violations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No copyright violations found for this user."
        )
    return violations


@router.post("/", response_model=CopyrightViolationResponse)
def log_copyright_violation(
    violation_data: CopyrightViolationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_violation = CopyrightMonitor(
        user_id=current_user.id,
        platform=violation_data.platform,
        content_url=violation_data.content_url,
        detected_at=violation_data.detected_at,
        status=violation_data.status
    )
    db.add(new_violation)
    db.commit()
    db.refresh(new_violation)
    return new_violation


@router.get("/{violation_id}", response_model=CopyrightViolationResponse)
def get_copyright_violation(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    violation = (
        db.query(CopyrightMonitor)
        .filter(
            CopyrightMonitor.id == violation_id,
            CopyrightMonitor.user_id == current_user.id
        )
        .first()
    )
    if not violation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Copyright violation not found."
        )
    return violation
