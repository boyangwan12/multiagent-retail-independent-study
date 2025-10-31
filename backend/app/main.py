from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.api.v1.router import api_router

# Set up logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events (startup/shutdown)"""
    # Startup
    logger.info("🚀 Fashion Forecast Backend starting...")

    # Validate critical environment variables
    _validate_environment()

    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"OpenAI model: {settings.OPENAI_MODEL}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")

    yield

    # Shutdown
    logger.info("👋 Fashion Forecast Backend shutting down...")

def _validate_environment():
    """Validate that all required environment variables are set"""
    errors = []

    # Check OpenAI API key
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-placeholder-replace-with-actual-key":
        errors.append(
            "⚠️  OPENAI_API_KEY is not set or using placeholder. "
            "Get your key from https://platform.openai.com/api-keys"
        )

    # Check CORS origins
    if not settings.CORS_ORIGINS:
        errors.append("⚠️  CORS_ORIGINS is empty. Frontend will not be able to connect.")

    # Log warnings but don't block startup (allow development with placeholder)
    if errors:
        logger.warning("=" * 60)
        logger.warning("ENVIRONMENT CONFIGURATION WARNINGS:")
        for error in errors:
            logger.warning(error)
        logger.warning("=" * 60)
        if settings.ENVIRONMENT == "production":
            raise ValueError("Cannot start in production with missing environment variables")
        else:
            logger.warning("⚠️  Starting in development mode with warnings. Some features may not work.")
    else:
        logger.info("✅ All required environment variables are set")

# Create FastAPI app instance
app = FastAPI(
    title="Fashion Forecast API",
    description="Multi-agent retail forecasting system with parameter-driven workflows",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware (must be first middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Add request logging middleware
app.add_middleware(RequestLoggerMiddleware)

# Add error handling middleware (catches all exceptions)
app.add_middleware(ErrorHandlerMiddleware)

# Include API router (all endpoints under /api/v1)
app.include_router(api_router, prefix="/api/v1")

# Root endpoint (redirect to docs)
@app.get("/")
async def root():
    return {
        "message": "Fashion Forecast API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
