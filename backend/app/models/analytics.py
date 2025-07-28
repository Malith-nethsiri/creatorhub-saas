from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey,
    JSON, Boolean, Float, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid



from app.core.database import Base


# ---------------------------
# ANALYTICS DATA MODEL
# ---------------------------
class AnalyticsData(Base):
    __tablename__ = "analytics_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Date and Platform
    date = Column(DateTime, nullable=False)
    platform = Column(String, nullable=False)

    # Follower Metrics
    followers = Column(Integer, default=0)
    followers_change = Column(Integer, default=0)
    following = Column(Integer, default=0)

    # Content Metrics (Daily Aggregated)
    posts_published = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)

    # Engagement Metrics
    engagement_rate = Column(Float, default=0.0)
    average_views_per_post = Column(Integer, default=0)
    top_performing_post_views = Column(Integer, default=0)

    # Audience Insights
    audience_demographics = Column(JSON, default=dict)
    top_countries = Column(JSON, default=list)
    age_groups = Column(JSON, default=dict)
    gender_split = Column(JSON, default=dict)

    # Performance Trends
    trending_hashtags = Column(JSON, default=list)
    peak_activity_hours = Column(JSON, default=list)

    # Revenue Tracking
    revenue_today = Column(Integer, default=0)
    ad_revenue = Column(Integer, default=0)
    sponsorship_revenue = Column(Integer, default=0)

    # Metadata
    data_source = Column(String)
    is_estimated = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<AnalyticsData(platform={self.platform}, date={self.date.strftime('%Y-%m-%d')})>"


# ---------------------------
# PLATFORM METRICS MODEL
# ---------------------------
class PlatformMetrics(Base):
    __tablename__ = "platform_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Platform Configuration
    platform = Column(String, nullable=False)
    platform_username = Column(String)
    platform_user_id = Column(String)

    # Authentication/API
    access_token = Column(String)
    refresh_token = Column(String)
    token_expires_at = Column(DateTime)

    # Account Status
    is_connected = Column(Boolean, default=False)
    is_business_account = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # Current Stats (Real-time)
    current_followers = Column(Integer, default=0)
    current_following = Column(Integer, default=0)
    total_posts = Column(Integer, default=0)

    # Performance Averages (Last 30 days)
    avg_engagement_rate = Column(Float, default=0.0)
    avg_views_per_post = Column(Integer, default=0)
    avg_likes_per_post = Column(Integer, default=0)

    # Content Performance
    best_performing_content_type = Column(String)
    best_posting_times = Column(JSON, default=list)
    top_hashtags = Column(JSON, default=list)

    # Monetization
    estimated_earnings_per_post = Column(Integer, default=0)
    brand_collaboration_rate = Column(Integer, default=0)

    # Sync Configuration
    auto_sync_enabled = Column(Boolean, default=True)
    last_sync_at = Column(DateTime)
    sync_frequency_hours = Column(Integer, default=24)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<PlatformMetrics(platform={self.platform}, username={self.platform_username})>"


# ---------------------------
# COMPETITOR ANALYSIS MODEL
# ---------------------------
class CompetitorAnalysis(Base):
    __tablename__ = "competitor_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Competitor Information
    competitor_name = Column(String, nullable=False)
    competitor_handle = Column(String, nullable=False)
    platform = Column(String, nullable=False)

    # Competitor Metrics
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    total_posts = Column(Integer, default=0)

    # Performance Analysis
    avg_engagement_rate = Column(Float, default=0.0)
    avg_views_per_post = Column(Integer, default=0)
    posting_frequency = Column(Float, default=0.0)

    # Content Analysis
    top_content_types = Column(JSON, default=list)
    common_hashtags = Column(JSON, default=list)
    posting_times = Column(JSON, default=list)

    # Growth Analysis
    follower_growth_rate = Column(Float, default=0.0)
    engagement_trend = Column(String)

    # Insights
    strengths = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    content_gaps = Column(JSON, default=list)

    # Analysis Metadata
    analysis_date = Column(DateTime, default=func.now())
    data_quality_score = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<CompetitorAnalysis(competitor={self.competitor_name}, platform={self.platform})>"


