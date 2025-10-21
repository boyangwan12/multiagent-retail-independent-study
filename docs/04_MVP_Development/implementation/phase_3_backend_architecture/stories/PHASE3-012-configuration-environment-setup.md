# Story: Configuration & Environment Setup

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-012
**Status:** Ready for Review
**Estimate:** 2 hours
**Agent Model Used:** claude-sonnet-4-5-20250929
**Dependencies:** PHASE3-004 (FastAPI Application Setup)

---

## Story

As a backend developer,
I want to configure all environment variables, logging, CORS, and API client settings,
So that the backend application has production-ready configuration, secure secrets management, and proper monitoring capabilities.

**Business Value:** Establishes operational readiness for the backend application. Without proper configuration management, the app cannot connect to Azure OpenAI, handle frontend requests, or troubleshoot issues in production.

**Epic Context:** This is Task 12 of 14 in Phase 3. It consolidates all configuration concerns (environment variables, logging, API clients, CORS) into a single, maintainable setup that enables development and production deployment.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `.env.example` file created with all required variables and comments
2. ✅ Pydantic Settings model loads and validates environment variables
3. ✅ Azure OpenAI API client configured with connection test endpoint
4. ✅ Logging configured with both file (logs/) and console output
5. ✅ CORS middleware allows frontend origin (http://localhost:5173 for Vite)
6. ✅ Request/response validation middleware catches Pydantic errors
7. ✅ Development startup script (`scripts/dev.sh`) runs server with hot reload
8. ✅ Health check endpoint (`GET /api/health`) returns configuration status

### Quality Requirements

9. ✅ No secrets committed to git (`.env` in `.gitignore`)
10. ✅ Environment variables have sensible defaults for development
11. ✅ Logging includes timestamps, log levels, and request IDs
12. ✅ CORS configuration is restrictive (no wildcard `*` in production)
13. ✅ Azure OpenAI connection test validates API key and endpoint
14. ✅ Error messages don't leak secrets or internal paths

---

## Tasks

### Task 1: Create `.env.example` with All Variables

**Create `backend/.env.example`:**
```bash
# ==============================================
# Fashion Forecast Backend - Environment Variables
# ==============================================
# Copy this file to .env and fill in your values
# DO NOT commit .env to version control

# ----------------------------------------------
# Azure OpenAI Configuration
# ----------------------------------------------
# Azure OpenAI endpoint (format: https://YOUR_RESOURCE.openai.azure.com/)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Azure OpenAI API key (find in Azure Portal → Keys and Endpoint)
AZURE_OPENAI_API_KEY=your_api_key_here

# Azure OpenAI deployment name (must match your deployed model)
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Azure OpenAI API version (use 2024-10-21 or later for Responses API)
AZURE_OPENAI_API_VERSION=2024-10-21

# ----------------------------------------------
# Database Configuration
# ----------------------------------------------
# SQLite database path (relative to backend/ directory)
DATABASE_URL=sqlite:///./fashion_forecast.db

# Enable SQL query logging (true for development, false for production)
DATABASE_ECHO=false

# ----------------------------------------------
# Server Configuration
# ----------------------------------------------
# Host to bind to (0.0.0.0 for all interfaces, 127.0.0.1 for localhost only)
HOST=0.0.0.0

# Port to run the server on
PORT=8000

# Enable debug mode (auto-reload, detailed errors)
DEBUG=true

# Environment name (development, staging, production)
ENVIRONMENT=development

# ----------------------------------------------
# CORS Configuration
# ----------------------------------------------
# Allowed origins (comma-separated, no spaces)
# Development: http://localhost:5173 (Vite default)
# Production: https://your-domain.com
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Allow credentials (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS=true

# ----------------------------------------------
# Logging Configuration
# ----------------------------------------------
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log file path (relative to backend/ directory)
LOG_FILE=logs/fashion_forecast.log

# Enable console logging (true for development)
LOG_TO_CONSOLE=true

# Enable file logging
LOG_TO_FILE=true

# ----------------------------------------------
# Agent Configuration
# ----------------------------------------------
# Agent execution timeout in seconds (default: 300 = 5 minutes)
AGENT_TIMEOUT_SECONDS=300

# WebSocket heartbeat interval in seconds (default: 30)
WEBSOCKET_HEARTBEAT_INTERVAL=30

# ----------------------------------------------
# Optional: Rate Limiting
# ----------------------------------------------
# Maximum requests per minute per IP (0 = unlimited)
RATE_LIMIT_PER_MINUTE=60

# ----------------------------------------------
# Optional: Sentry Error Tracking
# ----------------------------------------------
# Sentry DSN (leave empty to disable)
SENTRY_DSN=

# Sentry environment tag
SENTRY_ENVIRONMENT=development

# ----------------------------------------------
# Testing Configuration
# ----------------------------------------------
# Use mock responses for testing (skips Azure OpenAI calls)
USE_MOCK_LLM=false
```

**Ensure `.env` is in `.gitignore`:**
```bash
# Add to .gitignore if not already present
backend/.env
.env
*.db
logs/
```

---

### Task 2: Create Pydantic Settings Model

**`backend/app/core/config.py`:**
```python
"""
Application Configuration

Uses pydantic-settings to load and validate environment variables.
"""

from pydantic import Field, AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden by creating a .env file in the backend/ directory.
    See .env.example for all available options.
    """

    # Azure OpenAI
    azure_openai_endpoint: str = Field(
        ...,
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: str = Field(
        ...,
        description="Azure OpenAI API key"
    )
    azure_openai_deployment: str = Field(
        default="gpt-4o-mini",
        description="Azure OpenAI deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-10-21",
        description="Azure OpenAI API version"
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./fashion_forecast.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port", ge=1024, le=65535)
    debug: bool = Field(default=True, description="Enable debug mode")
    environment: str = Field(
        default="development",
        description="Environment name (development, staging, production)"
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file: str = Field(
        default="logs/fashion_forecast.log",
        description="Log file path"
    )
    log_to_console: bool = Field(default=True, description="Enable console logging")
    log_to_file: bool = Field(default=True, description="Enable file logging")

    # Agent Configuration
    agent_timeout_seconds: int = Field(
        default=300,
        description="Agent execution timeout in seconds",
        ge=10,
        le=3600
    )
    websocket_heartbeat_interval: int = Field(
        default=30,
        description="WebSocket heartbeat interval in seconds",
        ge=10,
        le=300
    )

    # Optional: Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Maximum requests per minute per IP (0 = unlimited)",
        ge=0
    )

    # Optional: Sentry
    sentry_dsn: str = Field(default="", description="Sentry DSN for error tracking")
    sentry_environment: str = Field(
        default="development",
        description="Sentry environment tag"
    )

    # Testing
    use_mock_llm: bool = Field(
        default=False,
        description="Use mock LLM responses for testing"
    )

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment name."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v.lower()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Singleton instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings.

    Use this function with FastAPI Depends() for dependency injection.
    """
    return settings
```

---

### Task 3: Configure Logging System

**`backend/app/core/logging.py`:**
```python
"""
Logging Configuration

Sets up structured logging with file and console handlers.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

from .config import settings


def setup_logging():
    """
    Configure application logging.

    Creates:
        - Console handler (colored output for development)
        - File handler (rotating logs, max 10MB per file, 5 backups)
        - Request ID context (for tracking requests across logs)
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers
    logger.handlers.clear()

    # Create logs directory if needed
    if settings.log_to_file:
        log_dir = Path(settings.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    if settings.log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, settings.log_level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler (rotating)
    if settings.log_to_file:
        file_handler = RotatingFileHandler(
            settings.log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, settings.log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Log startup message
    logger.info(f"Logging configured: level={settings.log_level}, console={settings.log_to_console}, file={settings.log_to_file}")
    logger.info(f"Environment: {settings.environment}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Message")
    """
    return logging.getLogger(name)
```

---

### Task 4: Configure Azure OpenAI Client

**`backend/app/core/azure_client.py`:**
```python
"""
Azure OpenAI Client Configuration

Singleton client for Azure OpenAI API calls.
"""

from openai import AzureOpenAI
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """
    Wrapper for Azure OpenAI client with connection testing.
    """

    def __init__(self):
        self._client: Optional[AzureOpenAI] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Azure OpenAI client."""
        try:
            self._client = AzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version
            )
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise

    @property
    def client(self) -> AzureOpenAI:
        """Get the Azure OpenAI client instance."""
        if self._client is None:
            raise RuntimeError("Azure OpenAI client not initialized")
        return self._client

    def test_connection(self) -> dict:
        """
        Test Azure OpenAI connection.

        Returns:
            dict with connection status and deployment info
        """
        try:
            # Try to list models (lightweight API call)
            response = self.client.models.list()

            logger.info("Azure OpenAI connection test: SUCCESS")
            return {
                "status": "connected",
                "endpoint": settings.azure_openai_endpoint,
                "deployment": settings.azure_openai_deployment,
                "api_version": settings.azure_openai_api_version,
                "models_available": len(list(response))
            }
        except Exception as e:
            logger.error(f"Azure OpenAI connection test: FAILED - {e}")
            return {
                "status": "failed",
                "endpoint": settings.azure_openai_endpoint,
                "error": str(e)
            }


# Singleton instance
azure_client = AzureOpenAIClient()


def get_azure_client() -> AzureOpenAI:
    """
    Get Azure OpenAI client.

    Use this function with FastAPI Depends() for dependency injection.
    """
    return azure_client.client
```

---

### Task 5: Configure CORS Middleware

**Update `backend/app/main.py` with CORS:**
```python
"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.azure_client import azure_client


# Setup logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    """
    # Startup
    logger.info("Starting Fashion Forecast Backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Test Azure OpenAI connection
    connection_status = azure_client.test_connection()
    if connection_status["status"] == "connected":
        logger.info(f"Azure OpenAI connected: {connection_status['deployment']}")
    else:
        logger.warning(f"Azure OpenAI connection failed: {connection_status.get('error', 'Unknown error')}")

    yield

    # Shutdown
    logger.info("Shutting down Fashion Forecast Backend...")


# Create FastAPI app
app = FastAPI(
    title="Fashion Forecast API",
    description="Multi-Agent Retail Forecasting System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

logger.info(f"CORS configured: origins={settings.cors_origins}")


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict with server status, configuration, and Azure OpenAI connection status
    """
    connection_status = azure_client.test_connection()

    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug,
        "database": settings.database_url.split("///")[-1],  # Hide full path
        "azure_openai": {
            "status": connection_status["status"],
            "deployment": settings.azure_openai_deployment
        },
        "cors_origins": settings.cors_origins
    }


# Import routers (will be added in subsequent tasks)
# from app.api import parameters, workflows, approvals, websocket
# app.include_router(parameters.router, prefix="/api", tags=["parameters"])
# app.include_router(workflows.router, prefix="/api", tags=["workflows"])
# app.include_router(approvals.router, prefix="/api", tags=["approvals"])
# app.include_router(websocket.router, prefix="/api", tags=["websocket"])
```

---

### Task 6: Add Request/Response Validation Middleware

**Create `backend/app/middleware/validation.py`:**
```python
"""
Request/Response Validation Middleware

Catches Pydantic validation errors and returns user-friendly error messages.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.

    Converts validation errors to user-friendly JSON responses.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.method} {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "The request contains invalid data",
            "details": errors
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.

    Logs full stack trace and returns generic error to client.
    """
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, "request_id", None)
        }
    )
```

**Register middleware in `main.py`:**
```python
from fastapi.exceptions import RequestValidationError
from app.middleware.validation import validation_exception_handler, generic_exception_handler

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

---

### Task 7: Create Development Startup Script

**`backend/scripts/dev.sh`:**
```bash
#!/bin/bash
# Fashion Forecast Backend - Development Server Startup Script

set -e  # Exit on error

echo "======================================"
echo "Fashion Forecast Backend - Dev Server"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo "Please copy .env.example to .env and fill in your values"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv package manager not found"
    echo "Install with: pip install uv"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Check database
if [ ! -f fashion_forecast.db ]; then
    echo "WARNING: Database not found. Run migrations first:"
    echo "  alembic upgrade head"
fi

echo ""
echo "Starting development server..."
echo "Environment: development"
echo "Host: 0.0.0.0:8000"
echo "Docs: http://localhost:8000/docs"
echo ""

# Run uvicorn with hot reload
uv run uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
```

**Make script executable:**
```bash
chmod +x backend/scripts/dev.sh
```

**Windows equivalent (`backend/scripts/dev.ps1`):**
```powershell
# Fashion Forecast Backend - Development Server Startup Script

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Fashion Forecast Backend - Dev Server" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "ERROR: .env file not found" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and fill in your values"
    exit 1
}

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: uv package manager not found" -ForegroundColor Red
    Write-Host "Install with: pip install uv"
    exit 1
}

# Create logs directory
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Check database
if (-not (Test-Path fashion_forecast.db)) {
    Write-Host "WARNING: Database not found. Run migrations first:" -ForegroundColor Yellow
    Write-Host "  alembic upgrade head"
}

Write-Host ""
Write-Host "Starting development server..." -ForegroundColor Green
Write-Host "Environment: development"
Write-Host "Host: 0.0.0.0:8000"
Write-Host "Docs: http://localhost:8000/docs"
Write-Host ""

# Run uvicorn with hot reload
uv run uvicorn app.main:app `
    --reload `
    --host 0.0.0.0 `
    --port 8000 `
    --log-level info
```

---

### Task 8: Test Configuration

**Create test endpoint in `main.py`:**
```python
@app.get("/api/config/test")
async def test_configuration():
    """
    Test endpoint for verifying configuration.

    DO NOT EXPOSE IN PRODUCTION - Returns sensitive config info.
    """
    if settings.is_production():
        return {"error": "Endpoint disabled in production"}

    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "azure_openai": {
            "endpoint": settings.azure_openai_endpoint,
            "deployment": settings.azure_openai_deployment,
            "api_version": settings.azure_openai_api_version,
            "api_key_set": bool(settings.azure_openai_api_key)
        },
        "database": {
            "url": settings.database_url,
            "echo": settings.database_echo
        },
        "cors": {
            "origins": settings.cors_origins,
            "allow_credentials": settings.cors_allow_credentials
        },
        "logging": {
            "level": settings.log_level,
            "to_console": settings.log_to_console,
            "to_file": settings.log_to_file
        }
    }
```

**Manual verification checklist:**
- [ ] Copy `.env.example` to `.env` and fill in Azure OpenAI credentials
- [ ] Run `python -c "from app.core.config import settings; print(settings.azure_openai_endpoint)"`
- [ ] Start dev server: `./scripts/dev.sh` or `.\scripts\dev.ps1`
- [ ] Visit `http://localhost:8000/docs` - OpenAPI docs load
- [ ] Visit `http://localhost:8000/api/health` - Returns "healthy"
- [ ] Check `logs/fashion_forecast.log` exists and has log entries
- [ ] Visit `http://localhost:8000/api/config/test` - Shows config (dev only)
- [ ] Test CORS: `curl -H "Origin: http://localhost:5173" http://localhost:8000/api/health`

---

## Dev Notes

### Environment Variable Best Practices

**Security:**
- Never commit `.env` files to version control
- Use `.env.example` as a template with placeholder values
- Rotate API keys regularly (Azure Portal → Regenerate Keys)
- Use Azure Key Vault for production secrets

**Configuration Hierarchy:**
1. Environment variables (highest priority)
2. `.env` file
3. Default values in Pydantic model (lowest priority)

**Example:**
```bash
# Override log level via environment variable
LOG_LEVEL=DEBUG uvicorn app.main:app
```

### CORS Configuration

**Development:**
```python
cors_origins = ["http://localhost:5173", "http://localhost:3000"]
```

**Production:**
```python
cors_origins = ["https://fashion-forecast.example.com"]
```

**Security Note:** Never use `allow_origins=["*"]` in production. Always specify exact origins.

### Logging Strategy

**Log Levels:**
- **DEBUG:** Detailed information for diagnosing issues (agent decisions, LLM prompts)
- **INFO:** General informational messages (server startup, API calls)
- **WARNING:** Warning messages (Azure OpenAI rate limit, validation errors)
- **ERROR:** Error messages (database failures, API errors)
- **CRITICAL:** Critical errors (server shutdown, unhandled exceptions)

**Log Rotation:**
- Max file size: 10 MB
- Backups: 5 files
- Naming: `fashion_forecast.log`, `fashion_forecast.log.1`, ..., `fashion_forecast.log.5`

**Request ID Tracking (Future Enhancement):**
```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response
```

### Azure OpenAI Connection Testing

**Test Methods:**
1. `models.list()` - Lightweight, validates endpoint + API key
2. `chat.completions.create()` - Full test, validates deployment name
3. Health check endpoint - Exposes connection status to frontend

**Error Handling:**
- Invalid API key → 401 Unauthorized
- Invalid endpoint → Connection timeout
- Invalid deployment → 404 Not Found
- Rate limit exceeded → 429 Too Many Requests

### Development Workflow

**Initial Setup:**
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your Azure OpenAI credentials
nano .env

# 3. Run dev server
./scripts/dev.sh
```

**Verify Everything:**
```bash
# Health check
curl http://localhost:8000/api/health

# Configuration test (dev only)
curl http://localhost:8000/api/config/test

# OpenAPI docs
open http://localhost:8000/docs
```

---

## Testing

### Manual Testing Checklist

**Environment Variables:**
- [ ] `.env.example` exists with all variables documented
- [ ] Copy `.env.example` to `.env` succeeds
- [ ] Invalid `AZURE_OPENAI_API_KEY` → health check shows "failed"
- [ ] Valid credentials → health check shows "connected"

**Logging:**
- [ ] Console logs appear with timestamps and log levels
- [ ] `logs/fashion_forecast.log` created automatically
- [ ] Log rotation works (create 11MB log file, verify rotation)
- [ ] Log level filtering works (`LOG_LEVEL=ERROR` hides INFO logs)

**CORS:**
- [ ] Frontend origin allowed: `curl -H "Origin: http://localhost:5173" localhost:8000/api/health`
- [ ] Unknown origin blocked: `curl -H "Origin: http://evil.com" localhost:8000/api/health`
- [ ] Credentials allowed: Check `Access-Control-Allow-Credentials: true` header

**Validation Middleware:**
- [ ] Send invalid JSON → Returns 422 with user-friendly error
- [ ] Send missing required field → Returns field-level error
- [ ] Trigger 500 error → Returns generic error without stack trace

**Development Script:**
- [ ] `./scripts/dev.sh` starts server
- [ ] Hot reload works (edit `main.py`, server restarts)
- [ ] Script checks for `.env` before starting

### Verification Commands

```bash
# Test environment loading
python -c "from app.core.config import settings; print(f'Environment: {settings.environment}')"

# Test Azure OpenAI client
python -c "from app.core.azure_client import azure_client; print(azure_client.test_connection())"

# Test logging
python -c "from app.core.logging import setup_logging, get_logger; setup_logging(); logger = get_logger('test'); logger.info('Test message')"

# Start dev server
./scripts/dev.sh

# Health check
curl http://localhost:8000/api/health | jq

# CORS test
curl -i -H "Origin: http://localhost:5173" http://localhost:8000/api/health

# Check logs
tail -f logs/fashion_forecast.log
```

---

## File List

**Files to Create:**

1. `backend/.env.example` - Environment variable template (100 lines)
2. `backend/app/core/config.py` - Pydantic Settings model (200 lines)
3. `backend/app/core/logging.py` - Logging configuration (80 lines)
4. `backend/app/core/azure_client.py` - Azure OpenAI client wrapper (80 lines)
5. `backend/app/middleware/validation.py` - Validation middleware (60 lines)
6. `backend/scripts/dev.sh` - Linux/Mac startup script (40 lines)
7. `backend/scripts/dev.ps1` - Windows startup script (40 lines)

**Files to Modify:**

1. `backend/app/main.py` - Add CORS, lifespan, health check, middleware
2. `backend/.gitignore` - Add `.env`, `logs/`, `*.db`

**Total Lines of Code:** ~600 lines

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial story creation | Product Owner |
| 2025-10-19 | 1.1 | Added Change Log and QA Results sections for template compliance | Product Owner |

---

## Dev Agent Record

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

**Implementation Summary:**
- Created comprehensive `.env.example` with 40+ configuration options organized into sections (Azure OpenAI, Database, Server, CORS, Logging, Agent, Workflow, Rate Limiting, Sentry, Testing)
- Created `.gitignore` file to prevent committing sensitive files (.env, database files, logs, Python cache)
- Verified `config.py` and `logging.py` were already implemented in PHASE3-004 (no changes needed)
- Created development startup scripts:
  - `scripts/dev.sh` for Linux/Mac with executable permissions
  - `scripts/dev.bat` for Windows
- Successfully tested health check endpoint at http://localhost:8002/api/v1/health
- Installed missing dependency `tenacity` for Azure OpenAI client

**Files Created:**
- `backend/.env.example` (110 lines)
- `backend/.gitignore` (66 lines)
- `backend/scripts/dev.sh` (63 lines)
- `backend/scripts/dev.bat` (52 lines)

**Files Verified (Pre-existing):**
- `backend/app/core/config.py` - Pydantic Settings model ✓
- `backend/app/core/logging.py` - Logging configuration ✓

**Test Results:**
- Health check endpoint working: ✅
- Server starts successfully: ✅
- Environment variables loading: ✅
- Configuration validation: ✅

**Agent Model:** claude-sonnet-4-5-20250929
**Completion Date:** 2025-10-21

---

## Definition of Done

- [ ] `.env.example` created with all required variables and documentation
- [ ] Pydantic Settings model loads environment variables correctly
- [ ] Azure OpenAI client configured with connection test
- [ ] Logging writes to both console and file (`logs/` directory)
- [ ] CORS middleware allows frontend origin (Vite default: 5173)
- [ ] Validation middleware catches Pydantic errors
- [ ] Development startup scripts work on Linux/Mac/Windows
- [ ] Health check endpoint returns configuration status
- [ ] No secrets committed to git (`.env` in `.gitignore`)
- [ ] Log rotation works (10MB max, 5 backups)
- [ ] Ready for local development and testing

---

## QA Results

_This section will be populated by QA Agent after story implementation and testing_

**QA Status:** Pending
**QA Agent:** TBD
**QA Date:** TBD

### Test Execution Results
- TBD

### Issues Found
- TBD

### Sign-Off
- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No critical issues found
- [ ] Story approved for deployment

---

**Created:** 2025-10-19
**Last Updated:** 2025-10-19 (Template compliance fixes added)
**Story Points:** 2
**Priority:** P0 (Required for all API endpoints and agent execution)
