from pydantic import BaseModel
from datetime import datetime

class AnalyticsBase(BaseModel):
    platform: str
    views: int
    clicks: int

class AnalyticsResponse(AnalyticsBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
