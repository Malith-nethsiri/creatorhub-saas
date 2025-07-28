from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    # Relationship to user
    user = relationship("User", backref="api_keys")

    def __repr__(self):
        return f"<APIKey(id={self.id}, active={self.is_active})>"
