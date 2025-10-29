import logging
import traceback
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

logger = logging.getLogger("fashion_forecast")

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch all exceptions and return JSON error responses"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log full stack trace to file
            logger.error(
                f"Unhandled exception on {request.method} {request.url.path}: {exc}",
                exc_info=True
            )

            # Determine status code
            status_code = getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Build error response
            error_response = {
                "error": str(exc),
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
            }

            # Include stack trace in debug mode only
            if settings.DEBUG:
                error_response["traceback"] = traceback.format_exc()

            return JSONResponse(
                status_code=status_code,
                content=error_response,
            )
