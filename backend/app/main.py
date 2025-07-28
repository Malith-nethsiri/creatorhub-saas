from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api import auth, content, analytics, monetization, copyright

# =============================
# ✅ Logging Configuration
# =============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s | %(message)s"
)
logger = logging.getLogger("CreatorHub")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events"""
    try:
        logger.info("🚀 CreatorHub.ai backend starting up...")
        await create_tables()
        logger.info("✅ Database tables created/verified")
        logger.info(f"DEBUG MODE: {'ON' if settings.DEBUG else 'OFF'}")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        raise

    yield

    logger.info("🛑 CreatorHub.ai backend shutting down...")

# =============================
# ✅ FastAPI App Initialization
# =============================
app = FastAPI(
    title="CreatorHub.ai API",
    description="AI-powered content creation and management platform for creators",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# =============================
# ✅ Middleware
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def log_request_timing(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.2f} ms")
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# =============================
# ✅ Global Exception Handler
# =============================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error",
            "path": request.url.path
        }
    )

# =============================
# ✅ Health & Root Endpoints
# =============================
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "CreatorHub.ai API",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to CreatorHub.ai API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

# =============================
# ✅ Include API Routers
# =============================
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(monetization.router, prefix="/api/v1/monetization", tags=["Monetization"])
app.include_router(copyright.router, prefix="/api/v1/copyright", tags=["Copyright"])

# =============================
# ✅ Local Development Runner
# =============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
