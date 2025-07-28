from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from app.core.database import Base

class BrandDeal(Base):
    __tablename__ = "brand_deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Brand Information
    brand_name = Column(String, nullable=False)
    brand_website = Column(String)
    contact_email = Column(String)
    deal_type = Column(String, default="sponsorship")  # sponsorship, affiliate, partnership

    # Deal Terms
    campaign_name = Column(String)
    deliverables = Column(JSON, default=list)  # e.g., ["1 YouTube video", "3 Instagram posts"]
    agreed_amount = Column(Integer, default=0)  # in cents
    currency = Column(String, default="USD")
    payment_status = Column(String, default="pending")  # pending, paid, overdue

    # Performance Tracking
    performance_metrics = Column(JSON, default=dict)
    revenue_generated = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="brand_deals")

    def __repr__(self):
        return f"<BrandDeal(brand='{self.brand_name}', user_id='{self.user_id}')>"

class AffiliateEarnings(Base):
    __tablename__ = "affiliate_earnings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    program_name = Column(String, nullable=False)
    total_clicks = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    earnings = Column(Integer, default=0)  # in cents

    last_payment_date = Column(DateTime)
    notes = Column(String)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

    def __repr__(self):
        return f"<AffiliateEarnings(program='{self.program_name}', earnings={self.earnings})>"

class DealStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


