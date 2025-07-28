from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from uuid import UUID

# =========================================================
# ✅ CONTENT IDEA SCHEMAS
# =========================================================
class ContentIdeaRequest(BaseModel):
    """Request schema for generating content ideas."""
    topic: str = Field(..., description="Main topic to generate ideas for")
    niche: Optional[str] = Field(None, description="Specific niche (e.g., fitness, finance)")
    audience: Optional[str] = Field(None, description="Target audience details")
    count: int = Field(default=5, ge=1, le=10, description="Number of ideas to generate (1-10)")
    platform: Optional[str] = Field(None, description="Optional target platform (e.g., TikTok, Instagram)")

class ContentIdeaResponse(BaseModel):
    """Response schema for generated content ideas."""
    id: UUID
    title: str
    description: str
    engagement_score: int = Field(..., ge=0, le=100)
    hashtags: List[str] = Field(default_factory=list)
    platform_optimized: Optional[str] = None

    class Config:
        orm_mode = True
        extra = "forbid"


# =========================================================
# ✅ VIDEO REPURPOSING SCHEMAS
# =========================================================
class VideoRepurposeRequest(BaseModel):
    """Request schema for repurposing video content."""
    title: str = Field(..., description="Original video title")
    description: Optional[str] = Field(None, description="Original video description")
    target_platforms: List[str] = Field(..., min_items=1, description="List of target platforms")
    tone: str = Field(default="professional", description="Tone style (motivational, casual, etc.)")

class VideoRepurposeResponse(BaseModel):
    """Response schema for repurposed video content."""
    id: UUID
    original_title: str
    transcript: str
    repurposed_content: Dict[str, str]  # e.g., {"tiktok": "new caption", "instagram": "new caption"}
    platforms_generated: List[str] = Field(default_factory=list)

    class Config:
        orm_mode = True
        extra = "forbid"


# =========================================================
# ✅ CONTENT HISTORY SCHEMAS
# =========================================================
class ContentHistoryResponse(BaseModel):
    """Response schema for content history records."""
    id: UUID
    content_type: str = Field(..., description="e.g., idea, repurposed_video")
    title: str
    created_at: datetime
    metadata: Optional[Dict] = Field(default_factory=dict)

    class Config:
        orm_mode = True
        extra = "forbid"
