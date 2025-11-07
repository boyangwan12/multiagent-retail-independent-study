from fastapi import APIRouter
from app.api.v1.endpoints import health, parameters, workflows, approvals, forecasts_endpoints, resources, uploads, data_uploads

api_router = APIRouter()

# Include health check endpoint
api_router.include_router(health.router, tags=["Health"])

# Include parameter extraction endpoint
api_router.include_router(parameters.router, tags=["Parameters"])

# Include workflow orchestration endpoints
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])

# Include CSV upload endpoints
api_router.include_router(uploads.router, prefix="/workflows", tags=["Uploads"])

# Include historical/training data upload endpoints
api_router.include_router(data_uploads.router, prefix="/data", tags=["Data Uploads"])

# Include approval endpoints for human-in-the-loop decisions
api_router.include_router(approvals.router, tags=["Approvals"])

# Include forecast resource endpoints
api_router.include_router(forecasts_endpoints.router)

# Include data management endpoints (allocations, markdowns, categories, stores, uploads)
api_router.include_router(resources.router)

# Future routers will be added here:
# etc.
