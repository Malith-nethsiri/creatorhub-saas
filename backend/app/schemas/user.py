from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user import SubscriptionPlan

# ----------- Shared User Base -----------

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

# ----------- User Create -----------

class UserCreate(UserBase):
    password: str

# ----------- User Response -----------

class UserResponseBase(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    subscription_plan: str
    created_at: datetime

    class Config:
        orm_mode = True

# ----------- Login -----------

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ----------- Authenticated User -----------

class UserMe(UserResponseBase):
    last_login: Optional[datetime] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    subscription_plan: SubscriptionPlan
    created_at: datetime

    # ✅ Add usage tracking fields
    content_ideas_used_this_month: int
    video_repurposing_used_this_month: int
    copyright_alerts_used_this_month: int

    class Config:
        from_attributes = True
