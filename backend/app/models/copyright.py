from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base
from enum import Enum

class CopyrightMonitor(Base):
    __tablename__ = "copyright_monitor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    platform = Column(String, nullable=False)  # youtube, instagram, tiktok
    content_id = Column(String, nullable=False)  # platform-specific content ID
    detected_on = Column(DateTime, default=datetime.utcnow)
    infringement_type = Column(String, default="unknown")  # reused, reuploaded, partial, etc.
    status = Column(String, default="pending")  # pending, resolved, disputed

    evidence = Column(JSON, default=dict)
    notes = Column(String)
    is_resolved = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="copyright_monitors")

    def __repr__(self):
        return f"<CopyrightMonitor(platform='{self.platform}', status='{self.status}')>"


class ViolationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    DISPUTED = "disputed"
