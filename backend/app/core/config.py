from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    # ---------------------------
    # App Configuration
    # ---------------------------
    APP_NAME: str = "CreatorHub.ai"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ---------------------------
    # Security
    # ---------------------------
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---------------------------
    # Database
    # ---------------------------
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/creatorhub"
    JWT_ALGORITHM: str = "HS256"

    # ---------------------------
    # CORS
    # ---------------------------
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://creatorhub.ai",
        "https://app.creatorhub.ai"
    ]

    # ---------------------------
    # AI Services
    # ---------------------------
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 2000

    # ---------------------------
    # File Storage
    # ---------------------------
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "creatorhub-storage"

    # ---------------------------
    # Redis (for background tasks)
    # ---------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---------------------------
    # Email Configuration
    # ---------------------------
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@creatorhub.ai"

    # ---------------------------
    # Stripe Configuration
    # ---------------------------
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # ---------------------------
    # Rate Limiting
    # ---------------------------
    RATE_LIMIT_PER_MINUTE: int = 60

    # ---------------------------
    # Logging
    # ---------------------------
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = "D:\\creatorhub-ai\\.env"
        case_sensitive = True
        populate_by_name = True
        extra = "allow"

# ✅ Instantiate settings
settings = Settings()

# ✅ Centralized Subscription Quotas (single source of truth)
SUBSCRIPTION_QUOTAS = {
    "FREE": {
        "content_ideas_per_month": 10,
        "video_repurposes_per_month": 2
    },
    "PRO": {
        "content_ideas_per_month": 1000,
        "video_repurposes_per_month": 200
    },
    "AGENCY": {
        "content_ideas_per_month": 5000,
        "video_repurposes_per_month": 1000
    },
    "ENTERPRISE": {
        "content_ideas_per_month": -1,    # Unlimited (custom pricing)
        "video_repurposes_per_month": -1
    }
}
