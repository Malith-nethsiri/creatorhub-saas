from sqlalchemy import (
    Column, String, Text, DateTime, Integer, ForeignKey,
    Enum as SQLEnum, JSON, Boolean, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base

# ---------------------------
# ✅ ENUMS
# ---------------------------
class ContentType(enum.Enum):
    IDEA = "idea"
    REPURPOSED_VIDEO = "repurposed_video"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    NEWSLETTER = "newsletter"
    SCRIPT = "script"

class ContentStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"

# ---------------------------
# ✅ MAIN GENERATED CONTENT MODEL
# ---------------------------
class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Content Information
    content_type = Column(SQLEnum(ContentType, name="contenttype"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # ✅ Metadata - Safe JSON Defaults
    content_metadata = Column("metadata", JSON, default=lambda: {})
    tags = Column(JSON, default=lambda: [])

    # Status and Publishing
    status = Column(SQLEnum(ContentStatus, name="contentstatus"), default=ContentStatus.DRAFT, nullable=False)
    published_at = Column(DateTime, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)

    # Performance Tracking
    views = Column(Integer, default=0)
    engagement_score = Column(Integer, default=0)
    performance_data = Column(JSON, default=lambda: {})

    # AI Generation Details
    ai_model_used = Column(String, nullable=True)
    generation_prompt = Column(Text, nullable=True)
    generation_parameters = Column(JSON, default=lambda: {})

    # File References
    original_file_path = Column(String, nullable=True)
    generated_files = Column(JSON, default=lambda: [])

    # Timestamps
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="generated_content")
    analytics = relationship(
        "ContentAnalytics",
        back_populates="content",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<GeneratedContent(id={self.id}, type={self.content_type.value}, "
            f"status={self.status.value}, created_at={self.created_at}, title='{self.title[:50]}...')>"
        )

# ---------------------------
# ✅ CONTENT ANALYTICS MODEL
# ---------------------------
class ContentAnalytics(Base):
    __tablename__ = "content_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id", ondelete="CASCADE"), nullable=False)

    # Platform Information
    platform = Column(String, nullable=False)
    platform_content_id = Column(String, nullable=True)

    # Engagement Metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    saves = Column(Integer, default=0)

    # Reach and Impressions
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    click_through_rate = Column(Integer, default=0)

    # Audience Demographics
    audience_data = Column(JSON, default=lambda: {})

    # Time-based Metrics
    watch_time_seconds = Column(Integer, default=0)
    average_view_duration = Column(Integer, default=0)

    # Revenue Data
    revenue_generated = Column(Integer, default=0)
    ad_revenue = Column(Integer, default=0)
    sponsorship_revenue = Column(Integer, default=0)

    # Metadata
    data_collected_at = Column(DateTime, default=func.now(), server_default=func.now())

    # Relationships
    content = relationship("GeneratedContent", back_populates="analytics")

    def __repr__(self):
        return f"<ContentAnalytics(platform={self.platform}, views={self.views}, collected={self.data_collected_at})>"

# ---------------------------
# ✅ CONTENT TEMPLATE MODEL
# ---------------------------
class ContentTemplate(Base):
    __tablename__ = "content_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Template Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(SQLEnum(ContentType, name="templatecontenttype"), nullable=False)

    # Template Content
    template_content = Column(Text, nullable=False)
    prompt_template = Column(Text, nullable=True)
    parameters = Column(JSON, default=lambda: {})
    tags = Column(JSON, default=lambda: [])

    # Template Status
    is_public = Column(Boolean, default=False)
    is_system_template = Column(Boolean, default=False)

    # Usage Statistics
    usage_count = Column(Integer, default=0)
    average_rating = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<ContentTemplate(name='{self.name}', type={self.content_type.value}, usage={self.usage_count})>"
