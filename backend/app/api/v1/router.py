from fastapi import APIRouter
from app.api.v1.endpoints import health, parameters

api_router = APIRouter()

# Include health check endpoint
api_router.include_router(health.router, tags=["Health"])

# Include parameter extraction endpoint
api_router.include_router(parameters.router, tags=["Parameters"])

# Future routers will be added here:
# api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
# api_router.include_router(forecasts.router, prefix="/forecasts", tags=["Forecasts"])
# etc.
