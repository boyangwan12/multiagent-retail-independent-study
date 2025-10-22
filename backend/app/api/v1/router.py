from fastapi import APIRouter
from app.api.v1.endpoints import health, parameters, workflows, websocket_stream, approvals

api_router = APIRouter()

# Include health check endpoint
api_router.include_router(health.router, tags=["Health"])

# Include parameter extraction endpoint
api_router.include_router(parameters.router, tags=["Parameters"])

# Include workflow orchestration endpoints
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])

# Include WebSocket endpoint for real-time agent updates
api_router.include_router(websocket_stream.router, tags=["WebSocket"])

# Include approval endpoints for human-in-the-loop decisions
api_router.include_router(approvals.router, tags=["Approvals"])

# Future routers will be added here:
# api_router.include_router(forecasts.router, prefix="/forecasts", tags=["Forecasts"])
# etc.
