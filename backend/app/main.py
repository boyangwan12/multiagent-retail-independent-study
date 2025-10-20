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
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Azure OpenAI endpoint: {settings.AZURE_OPENAI_ENDPOINT}")

    yield

    # Shutdown
    logger.info("👋 Fashion Forecast Backend shutting down...")

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
