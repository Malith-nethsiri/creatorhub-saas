from sqlalchemy.orm import Session
from typing import List
from app.models.monetization import BrandDeal
from app.schemas.monetization import BrandDealCreate
from app.models.user import User

def get_user_brand_deals(db: Session, user: User) -> List[BrandDeal]:
    return (
        db.query(BrandDeal)
        .filter(BrandDeal.user_id == user.id)
        .all()
    )

def create_brand_deal(db: Session, user: User, deal_data: BrandDealCreate) -> BrandDeal:
    new_deal = BrandDeal(
        user_id=user.id,
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

def get_brand_deal(db: Session, user: User, deal_id: int) -> BrandDeal:
    return (
        db.query(BrandDeal)
        .filter(BrandDeal.id == deal_id, BrandDeal.user_id == user.id)
        .first()
    )
