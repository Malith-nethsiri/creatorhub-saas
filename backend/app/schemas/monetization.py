from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum

class DealStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class BrandDealBase(BaseModel):
    brand_name: str
    amount: float
    status: DealStatus
    start_date: date
    end_date: date

class BrandDealCreate(BrandDealBase):
    pass

class BrandDealResponse(BrandDealBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
