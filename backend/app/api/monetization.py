from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.monetization import BrandDeal
from app.schemas.monetization import BrandDealResponse, BrandDealCreate
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[BrandDealResponse])
def get_user_brand_deals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    deals = (
        db.query(BrandDeal)
        .filter(BrandDeal.user_id == current_user.id)
        .all()
    )
    if not deals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No brand deals found for this user."
        )
    return deals


@router.post("/", response_model=BrandDealResponse)
def create_brand_deal(
    deal_data: BrandDealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_deal = BrandDeal(
        user_id=current_user.id,
        brand_name=deal_data.brand_name,
        amount=deal_data.amount,
        status=deal_data.status,
        start_date=deal_data.start_date,
        end_date=deal_data.end_date,
    )
    db.add(new_deal)
    db.commit()
    db.refresh(new_deal)
    return new_deal


@router.get("/{deal_id}", response_model=BrandDealResponse)
def get_brand_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    deal = (
        db.query(BrandDeal)
        .filter(
            BrandDeal.id == deal_id,
            BrandDeal.user_id == current_user.id
        )
        .first()
    )
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand deal not found."
        )
    return deal
