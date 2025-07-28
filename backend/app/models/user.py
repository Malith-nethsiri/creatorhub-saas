from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
import logging
from typing import cast

from app.core.database import Base
from app.core.config import SUBSCRIPTION_QUOTAS

logger = logging.getLogger(__name__)


class SubscriptionPlan(enum.Enum):
    FREE = "free"
    PRO = "pro"
    AGENCY = "agency"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    # ---------------------------
    # Core User Info
    # ---------------------------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active: bool = cast(bool, Column(Boolean, default=True))
    is_verified: bool = cast(bool, Column(Boolean, default=False))

    # ---------------------------
    # Profile Information
    # ---------------------------
    primary_niche = Column(String, nullable=True)
    target_audience = Column(Text, nullable=True)
    social_media_handles = Column(Text, nullable=True)

    # ---------------------------
    # Subscription Info
    # ---------------------------
    subscription_plan: SubscriptionPlan = cast(
        SubscriptionPlan,
        Column(
            SQLEnum(SubscriptionPlan, name="subscriptionplan"),
            default=SubscriptionPlan.FREE,
            nullable=False
        )
    )
    subscription_status = Column(String, default="active")
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # ---------------------------
    # Usage Tracking
    # ---------------------------
    content_ideas_used_this_month: int = cast(int, Column(Integer, default=0))
    video_repurposing_used_this_month: int = cast(int, Column(Integer, default=0))
    copyright_alerts_used_this_month: int = cast(int, Column(Integer, default=0))
    last_usage_reset = Column(DateTime, default=datetime.utcnow)

    # ---------------------------
    # Timestamps
    # ---------------------------
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    # ---------------------------
    # Relationships
    # ---------------------------
    generated_content = relationship(
        "GeneratedContent",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    brand_deals = relationship(
        "BrandDeal",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    copyright_monitors = relationship(
        "CopyrightMonitor",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------
    # Business Logic Methods
    # ---------------------------
    def reset_monthly_usage_if_needed(self) -> None:
        now = datetime.utcnow()
        if self.last_usage_reset is None or (now - self.last_usage_reset).days >= 30:
            logger.info(f"STAGE ✅ Resetting monthly usage for user {self.email}")
            self.content_ideas_used_this_month = 0
            self.video_repurposing_used_this_month = 0
            self.copyright_alerts_used_this_month = 0
            self.last_usage_reset = now

    def increment_content_ideas_used(self) -> None:
        self.content_ideas_used_this_month = (self.content_ideas_used_this_month or 0) + 1

    def increment_video_repurposing_used(self) -> None:
        self.video_repurposing_used_this_month = (self.video_repurposing_used_this_month or 0) + 1

    def can_generate_content_ideas(self) -> bool:
        self.reset_monthly_usage_if_needed()

        if not self.is_subscription_active():
            return False

        plan_key = self.subscription_plan.value.upper()
        quota = SUBSCRIPTION_QUOTAS.get(plan_key, SUBSCRIPTION_QUOTAS["FREE"])
        limit = quota["content_ideas_per_month"]

        if limit == -1:  # Unlimited
            return True
        return (self.content_ideas_used_this_month or 0) < limit

    def can_repurpose_video(self) -> bool:
        self.reset_monthly_usage_if_needed()

        if not self.is_subscription_active():
            return False

        plan_key = self.subscription_plan.value.upper()
        quota = SUBSCRIPTION_QUOTAS.get(plan_key, SUBSCRIPTION_QUOTAS["FREE"])
        limit = quota["video_repurposes_per_month"]

        if limit == -1:  # Unlimited
            return True
        return (self.video_repurposing_used_this_month or 0) < limit

    def is_subscription_active(self) -> bool:
        if self.subscription_end_date is None:
            return bool(self.subscription_plan == SubscriptionPlan.FREE)
        # Ensure both are Python datetime objects, not SQLAlchemy columns
        return datetime.utcnow() <= self.subscription_end_date if isinstance(self.subscription_end_date, datetime) else False


    def get_plan_limits(self) -> dict:
        plan_key = self.subscription_plan.value.upper()
        quota = SUBSCRIPTION_QUOTAS.get(plan_key, SUBSCRIPTION_QUOTAS["FREE"])
        return {
            "content_ideas_monthly": quota["content_ideas_per_month"],
            "video_repurposing_monthly": quota["video_repurposes_per_month"],
            "analytics_history_days": 7 if plan_key == "FREE" else 90 if plan_key == "PRO" else -1,
            "copyright_monitoring": plan_key in ["PRO", "AGENCY", "ENTERPRISE"],
            "priority_support": plan_key in ["PRO", "AGENCY", "ENTERPRISE"],
            "custom_ai_training": plan_key in ["ENTERPRISE"]
        }
