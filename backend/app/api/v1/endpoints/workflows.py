from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.workflow_schemas import (
    WorkflowCreateRequest,
    ReforecastRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    WorkflowResultsResponse
)
from app.services.workflow_service import WorkflowService
import logging

logger = logging.getLogger("fashion_forecast")

router = APIRouter()


def get_workflow_service(db: Session = Depends(get_db)) -> WorkflowService:
    """Dependency injection for WorkflowService."""
    return WorkflowService(db)


@router.post("/forecast", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast_workflow(
    request: WorkflowCreateRequest,
    http_request: Request,
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Create a new pre-season forecast workflow.

    **Workflow Steps:**
    1. Accept SeasonParameters from parameter extraction (PHASE3-005)
    2. Create workflow session in database with status "pending"
    3. Initialize Orchestrator agent (placeholder for Phase 8)
    4. Return workflow_id and WebSocket URL

    **Example Request:**
    ```json
    {
      "category_id": "womens_dresses",
      "parameters": {
        "forecast_horizon_weeks": 12,
        "season_start_date": "2025-03-01",
        "replenishment_strategy": "none",
        "dc_holdback_percentage": 0.0,
        "markdown_checkpoint_week": 6
      }
    }
    ```

    **Example Response:**
    ```json
    {
      "workflow_id": "wf_abc123",
      "status": "pending",
      "websocket_url": "ws://localhost:8000/api/workflows/wf_abc123/stream"
    }
    ```
    """
    try:
        # Get host from request for WebSocket URL
        host = http_request.headers.get("host", "localhost:8000")

        # Create workflow
        response = service.create_forecast_workflow(request, host)

        logger.info(f"Forecast workflow created: {response.workflow_id}")
        return response

    except Exception as e:
        logger.error(f"Failed to create forecast workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")


@router.post("/reforecast", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_reforecast_workflow(
    request: ReforecastRequest,
    http_request: Request,
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Create a re-forecast workflow (variance-triggered or manual).

    **Triggered When:**
    - Variance exceeds 20% threshold after weekly actuals upload
    - User manually requests re-forecast

    **Workflow Steps:**
    1. Accept forecast_id and actual sales data
    2. Calculate variance percentage
    3. Enable re-forecast handoff dynamically (Phase 8)
    4. Return workflow_id and WebSocket URL

    **Example Request:**
    ```json
    {
      "forecast_id": "f_spring_2025",
      "actual_sales_week_1_to_n": 3200,
      "forecasted_week_1_to_n": 2550,
      "remaining_weeks": 8,
      "variance_pct": 0.255
    }
    ```

    **Example Response:**
    ```json
    {
      "workflow_id": "wf_def456",
      "status": "pending",
      "websocket_url": "ws://localhost:8000/api/workflows/wf_def456/stream"
    }
    ```
    """
    try:
        # Get host from request
        host = http_request.headers.get("host", "localhost:8000")

        # Create re-forecast workflow
        response = service.create_reforecast_workflow(request, host)

        logger.info(f"Re-forecast workflow created: {response.workflow_id} (variance: {request.variance_pct:.1%})")
        return response

    except Exception as e:
        logger.error(f"Failed to create re-forecast workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Re-forecast creation failed: {str(e)}")


@router.get("/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Get workflow status (polling alternative to WebSocket).

    **Use Case:**
    - Frontend can poll this endpoint instead of WebSocket
    - Useful for debugging or when WebSocket connection fails
    - Recommended: WebSocket for real-time updates, polling as fallback

    **Example Response:**
    ```json
    {
      "workflow_id": "wf_abc123",
      "workflow_type": "forecast",
      "status": "running",
      "current_agent": "Inventory Agent",
      "progress_pct": 66,
      "started_at": "2025-10-12T10:30:00Z",
      "updated_at": "2025-10-12T10:30:45Z",
      "completed_at": null,
      "error_message": null
    }
    ```
    """
    try:
        return service.get_workflow_status(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.get("/{workflow_id}/results", response_model=WorkflowResultsResponse)
async def get_workflow_results(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Get final workflow results (only when status = completed or failed).

    **Use Case:**
    - Retrieve forecast_id, allocation_id, markdown_id after workflow completes
    - Frontend uses these IDs to fetch detailed results via resource endpoints

    **Example Response:**
    ```json
    {
      "workflow_id": "wf_abc123",
      "status": "completed",
      "forecast_id": "f_spring_2025",
      "allocation_id": "a_spring_2025",
      "markdown_id": null,
      "output_data": {
        "total_season_demand": 8000,
        "manufacturing_qty": 9600,
        "workflow_duration_seconds": 58
      },
      "error_message": null
    }
    ```
    """
    try:
        return service.get_workflow_results(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get workflow results: {e}")
        raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")
