import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("fashion_forecast")

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests with timing and status code"""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip logging for health check (reduces noise)
        if request.url.path == "/api/v1/health":
            return await call_next(request)

        # Start timer
        start_time = time.time()

        # Log incoming request
        logger.info(f"→ {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"[{response.status_code}] {duration_ms:.2f}ms"
        )

        return response
