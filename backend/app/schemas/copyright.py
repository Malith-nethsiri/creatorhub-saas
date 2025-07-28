from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class ViolationStatus(str, Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"

class CopyrightViolationBase(BaseModel):
    platform: str
    content_url: str
    detected_at: datetime
    status: ViolationStatus

class CopyrightViolationCreate(CopyrightViolationBase):
    pass

class CopyrightViolationResponse(CopyrightViolationBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
