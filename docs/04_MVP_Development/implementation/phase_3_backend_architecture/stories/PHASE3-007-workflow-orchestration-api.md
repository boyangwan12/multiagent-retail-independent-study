# Story: Workflow Orchestration API - Pre-Season Forecast & Re-Forecast Endpoints

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-007
**Status:** Draft
**Estimate:** 4 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-004 (FastAPI Setup), PHASE3-005 (Parameter Extraction)

---

## Story

As a backend developer,
I want to create workflow orchestration endpoints that initiate and manage multi-agent forecast workflows,
So that the frontend can trigger pre-season forecasts, handle variance-triggered re-forecasts, and monitor workflow status via polling.

**Business Value:** This is the **core orchestration layer** that coordinates all 3 agents (Demand, Inventory, Pricing). Without this, the multi-agent system cannot execute forecast workflows. The workflow API enables parameter-driven agent execution, dynamic re-forecast triggering, and real-time progress tracking.

**Epic Context:** This is Task 7 of 14 in Phase 3. It builds on FastAPI setup (PHASE3-004) and parameter extraction (PHASE3-005) to create the orchestration layer. This enables frontend Section 1 (Configure Strategy & Run Forecast), Section 4 (Variance Monitoring), and Section 6 (Markdown Re-forecast). Phase 8 (Orchestrator Agent) will replace placeholder logic with full LLM-driven coordination.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `POST /api/workflows/forecast` endpoint creates new pre-season forecast workflow
2. ✅ Endpoint accepts `SeasonParameters` in request body (extracted from PHASE3-005)
3. ✅ Workflow session created in database with `workflow_id` and initial status "pending"
4. ✅ Orchestrator agent initialized (placeholder - no actual LLM calls yet)
5. ✅ Response includes `workflow_id`, `status`, and `websocket_url`
6. ✅ `POST /api/workflows/reforecast` endpoint creates variance-triggered or manual re-forecast
7. ✅ Re-forecast endpoint accepts `forecast_id`, `actual_sales_week_1_to_n`, `remaining_weeks`
8. ✅ `GET /api/workflows/{workflow_id}` endpoint returns workflow status (polling alternative to WebSocket)
9. ✅ `GET /api/workflows/{workflow_id}/results` endpoint returns final workflow results

### Quality Requirements

10. ✅ All endpoints follow FastAPI dependency injection pattern
11. ✅ Pydantic request/response models with validation
12. ✅ Database transactions use SQLAlchemy session management
13. ✅ Error handling returns JSON responses with meaningful error messages
14. ✅ OpenAPI documentation auto-generated for all endpoints

---

## Tasks

### Task 1: Create Workflow Database Model

Create SQLAlchemy model for workflow sessions to track workflow state.

**File:** `backend/app/models/workflow.py`

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, JSON
from sqlalchemy.sql import func
import enum
from ..db.base import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow status enum."""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    awaiting_approval = "awaiting_approval"


class Workflow(Base):
    """Workflow session model."""
    __tablename__ = "workflows"

    workflow_id = Column(String, primary_key=True, index=True)
    workflow_type = Column(String, nullable=False)  # "forecast" or "reforecast"
    forecast_id = Column(String, nullable=True)  # FK to forecasts (null for initial forecast)
    category_id = Column(String, nullable=False)

    # Status tracking
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.pending, nullable=False)
    current_agent = Column(String, nullable=True)  # "demand", "inventory", "pricing", null
    progress_pct = Column(Integer, default=0)

    # Session parameters (from SeasonParameters)
    forecast_horizon_weeks = Column(Integer, nullable=False)
    season_start_date = Column(String, nullable=False)
    replenishment_strategy = Column(String, nullable=False)
    dc_holdback_percentage = Column(Float, nullable=False)
    markdown_checkpoint_week = Column(Integer, nullable=True)

    # Workflow context (JSON)
    input_data = Column(JSON, nullable=True)  # Original request body
    output_data = Column(JSON, nullable=True)  # Final results
    error_message = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Expected Output:**
- Workflows table with all required columns
- Status enum for workflow state machine
- JSON columns for flexible context storage

---

### Task 2: Create Workflow Pydantic Schemas

Create request/response models for workflow endpoints.

**File:** `backend/app/schemas/workflow.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from .parameters import SeasonParameters


class WorkflowCreateRequest(BaseModel):
    """Request to create new pre-season forecast workflow."""

    category_id: str = Field(..., description="Category to forecast (e.g., 'womens_dresses')")
    parameters: SeasonParameters = Field(..., description="Extracted season parameters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": "womens_dresses",
                "parameters": {
                    "forecast_horizon_weeks": 12,
                    "season_start_date": "2025-03-01",
                    "replenishment_strategy": "none",
                    "dc_holdback_percentage": 0.0,
                    "markdown_checkpoint_week": 6
                }
            }
        }
    )


class ReforecastRequest(BaseModel):
    """Request to re-forecast remaining weeks due to variance."""

    forecast_id: str = Field(..., description="Original forecast ID to re-forecast")
    actual_sales_week_1_to_n: int = Field(..., description="Actual sales through week N")
    forecasted_week_1_to_n: int = Field(..., description="Original forecast through week N")
    remaining_weeks: int = Field(..., ge=1, le=12, description="Weeks remaining in season")
    variance_pct: float = Field(..., description="Variance percentage (e.g., 0.255 = 25.5%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "forecast_id": "f_spring_2025",
                "actual_sales_week_1_to_n": 3200,
                "forecasted_week_1_to_n": 2550,
                "remaining_weeks": 8,
                "variance_pct": 0.255
            }
        }
    )


class WorkflowResponse(BaseModel):
    """Response after workflow creation."""

    workflow_id: str = Field(..., description="Unique workflow identifier")
    status: Literal["pending", "running", "completed", "failed", "awaiting_approval"]
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "status": "pending",
                "websocket_url": "ws://localhost:8000/api/workflows/wf_abc123/stream"
            }
        }
    )


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status polling."""

    workflow_id: str
    workflow_type: Literal["forecast", "reforecast"]
    status: Literal["pending", "running", "completed", "failed", "awaiting_approval"]
    current_agent: Optional[str] = None
    progress_pct: int = Field(0, ge=0, le=100)
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "workflow_type": "forecast",
                "status": "running",
                "current_agent": "Inventory Agent",
                "progress_pct": 66,
                "started_at": "2025-10-12T10:30:00Z",
                "updated_at": "2025-10-12T10:30:45Z",
                "completed_at": None,
                "error_message": None
            }
        }
    )


class WorkflowResultsResponse(BaseModel):
    """Response for completed workflow results."""

    workflow_id: str
    status: Literal["completed", "failed"]
    forecast_id: Optional[str] = None
    allocation_id: Optional[str] = None
    markdown_id: Optional[str] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "status": "completed",
                "forecast_id": "f_spring_2025",
                "allocation_id": "a_spring_2025",
                "markdown_id": None,
                "output_data": {
                    "total_season_demand": 8000,
                    "manufacturing_qty": 9600,
                    "workflow_duration_seconds": 58
                },
                "error_message": None
            }
        }
    )
```

**Expected Output:**
- 5 Pydantic models with validation
- Example JSON payloads in OpenAPI docs
- Type safety for workflow requests/responses

---

### Task 3: Create Workflow Service (Business Logic)

Create service layer that handles workflow orchestration logic (placeholder - no agent calls yet).

**File:** `backend/app/services/workflow_service.py`

```python
from sqlalchemy.orm import Session
from ..models.workflow import Workflow, WorkflowStatus
from ..schemas.workflow import (
    WorkflowCreateRequest,
    ReforecastRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    WorkflowResultsResponse
)
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing workflow orchestration."""

    def __init__(self, db: Session):
        self.db = db

    def create_forecast_workflow(
        self,
        request: WorkflowCreateRequest,
        host: str = "localhost:8000"
    ) -> WorkflowResponse:
        """
        Create a new pre-season forecast workflow.

        Args:
            request: Workflow creation request with parameters
            host: Server host for WebSocket URL construction

        Returns:
            WorkflowResponse with workflow_id and WebSocket URL
        """
        # Generate unique workflow ID
        workflow_id = f"wf_{uuid.uuid4().hex[:12]}"

        # Create workflow session in database
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_type="forecast",
            forecast_id=None,  # Will be set when Demand Agent completes
            category_id=request.category_id,
            status=WorkflowStatus.pending,
            current_agent=None,
            progress_pct=0,
            forecast_horizon_weeks=request.parameters.forecast_horizon_weeks,
            season_start_date=request.parameters.season_start_date,
            replenishment_strategy=request.parameters.replenishment_strategy,
            dc_holdback_percentage=request.parameters.dc_holdback_percentage,
            markdown_checkpoint_week=request.parameters.markdown_checkpoint_week,
            input_data=request.model_dump(),
            output_data=None,
            error_message=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None
        )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        logger.info(f"Created forecast workflow {workflow_id} for category {request.category_id}")

        # Construct WebSocket URL
        websocket_url = f"ws://{host}/api/workflows/{workflow_id}/stream"

        # TODO (Phase 8): Initialize Orchestrator agent here
        # orchestrator = get_orchestrator_agent()
        # session = Session()
        # result = session.run(orchestrator, input=request.model_dump())

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="pending",
            websocket_url=websocket_url
        )

    def create_reforecast_workflow(
        self,
        request: ReforecastRequest,
        host: str = "localhost:8000"
    ) -> WorkflowResponse:
        """
        Create a re-forecast workflow (variance-triggered or manual).

        Args:
            request: Re-forecast request with actuals and variance
            host: Server host for WebSocket URL construction

        Returns:
            WorkflowResponse with workflow_id and WebSocket URL
        """
        # Generate unique workflow ID
        workflow_id = f"wf_{uuid.uuid4().hex[:12]}"

        # Fetch original forecast to get parameters
        # (In real implementation, fetch from forecasts table)
        # For now, use placeholder parameters

        # Create workflow session
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_type="reforecast",
            forecast_id=request.forecast_id,
            category_id="placeholder",  # TODO: Fetch from forecast
            status=WorkflowStatus.pending,
            current_agent=None,
            progress_pct=0,
            forecast_horizon_weeks=request.remaining_weeks,
            season_start_date="placeholder",  # TODO: Fetch from forecast
            replenishment_strategy="placeholder",
            dc_holdback_percentage=0.45,
            markdown_checkpoint_week=None,
            input_data=request.model_dump(),
            output_data=None,
            error_message=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None
        )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        logger.info(f"Created re-forecast workflow {workflow_id} for forecast {request.forecast_id} (variance: {request.variance_pct:.1%})")

        # Construct WebSocket URL
        websocket_url = f"ws://{host}/api/workflows/{workflow_id}/stream"

        # TODO (Phase 8): Enable re-forecast handoff dynamically
        # orchestrator.enable_handoff("reforecast")
        # orchestrator.handoff(demand_agent, input=reforecast_context)

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="pending",
            websocket_url=websocket_url
        )

    def get_workflow_status(self, workflow_id: str) -> WorkflowStatusResponse:
        """
        Get workflow status (polling alternative to WebSocket).

        Args:
            workflow_id: Workflow ID to query

        Returns:
            WorkflowStatusResponse with current status

        Raises:
            ValueError: If workflow not found
        """
        workflow = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()

        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        return WorkflowStatusResponse(
            workflow_id=workflow.workflow_id,
            workflow_type=workflow.workflow_type,
            status=workflow.status.value,
            current_agent=workflow.current_agent,
            progress_pct=workflow.progress_pct,
            started_at=workflow.started_at,
            updated_at=workflow.updated_at,
            completed_at=workflow.completed_at,
            error_message=workflow.error_message
        )

    def get_workflow_results(self, workflow_id: str) -> WorkflowResultsResponse:
        """
        Get final workflow results.

        Args:
            workflow_id: Workflow ID to query

        Returns:
            WorkflowResultsResponse with output data

        Raises:
            ValueError: If workflow not found or not completed
        """
        workflow = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()

        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if workflow.status not in [WorkflowStatus.completed, WorkflowStatus.failed]:
            raise ValueError(f"Workflow {workflow_id} is not completed (status: {workflow.status.value})")

        return WorkflowResultsResponse(
            workflow_id=workflow.workflow_id,
            status=workflow.status.value,
            forecast_id=workflow.forecast_id,
            allocation_id=None,  # TODO: Extract from output_data
            markdown_id=None,
            output_data=workflow.output_data,
            error_message=workflow.error_message
        )
```

**Expected Output:**
- WorkflowService class with 4 methods
- Database session management
- Placeholder for Phase 8 agent integration
- Logging for debugging

---

### Task 4: Create Workflow API Endpoints

Create FastAPI router with workflow endpoints.

**File:** `backend/app/api/workflows.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..schemas.workflow import (
    WorkflowCreateRequest,
    ReforecastRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    WorkflowResultsResponse
)
from ..services.workflow_service import WorkflowService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


def get_workflow_service(db: Session = Depends(get_db)) -> WorkflowService:
    """Dependency injection for WorkflowService."""
    return WorkflowService(db)


@router.post("/forecast", response_model=WorkflowResponse, status_code=201)
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


@router.post("/reforecast", response_model=WorkflowResponse, status_code=201)
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
```

**Expected Output:**
- 4 FastAPI endpoints with dependency injection
- OpenAPI documentation with examples
- Error handling with meaningful HTTP status codes
- Logging for debugging

---

### Task 5: Register Workflow Router in Main Application

Add workflow router to FastAPI app.

**File:** `backend/app/main.py` (modifications)

```python
from fastapi import FastAPI
from .api import workflows  # Import workflow router

app = FastAPI(
    title="Fashion Forecast API",
    description="Multi-agent retail forecasting system with parameter-driven workflows",
    version="0.1.0"
)

# Include workflow router
app.include_router(workflows.router)

# Other routers...
# app.include_router(parameters.router)
# app.include_router(data.router)
```

**Expected Output:**
- Workflow endpoints registered at `/api/workflows/*`
- OpenAPI docs accessible at `http://localhost:8000/docs`

---

### Task 6: Create Database Migration for Workflows Table

Generate Alembic migration for `workflows` table.

**Commands:**

```bash
# Generate migration
cd backend
uv run alembic revision --autogenerate -m "Add workflows table"

# Review migration file (backend/alembic/versions/XXXX_add_workflows_table.py)
# Verify columns match Workflow model

# Run migration
uv run alembic upgrade head
```

**Expected Output:**
- `workflows` table created in SQLite database
- Migration applied successfully
- No errors in migration logs

---

### Task 7: Test Workflow Endpoints

Create pytest tests for workflow endpoints.

**File:** `backend/tests/test_workflows.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_forecast_workflow():
    """Test POST /api/workflows/forecast endpoint."""

    request_data = {
        "category_id": "womens_dresses",
        "parameters": {
            "forecast_horizon_weeks": 12,
            "season_start_date": "2025-03-01",
            "replenishment_strategy": "none",
            "dc_holdback_percentage": 0.0,
            "markdown_checkpoint_week": 6
        }
    }

    response = client.post("/api/workflows/forecast", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert "workflow_id" in data
    assert data["status"] == "pending"
    assert "ws://" in data["websocket_url"]
    assert data["workflow_id"] in data["websocket_url"]


def test_create_reforecast_workflow():
    """Test POST /api/workflows/reforecast endpoint."""

    request_data = {
        "forecast_id": "f_spring_2025",
        "actual_sales_week_1_to_n": 3200,
        "forecasted_week_1_to_n": 2550,
        "remaining_weeks": 8,
        "variance_pct": 0.255
    }

    response = client.post("/api/workflows/reforecast", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert "workflow_id" in data
    assert data["status"] == "pending"
    assert "ws://" in data["websocket_url"]


def test_get_workflow_status():
    """Test GET /api/workflows/{workflow_id} endpoint."""

    # Create workflow first
    create_response = client.post("/api/workflows/forecast", json={
        "category_id": "womens_dresses",
        "parameters": {
            "forecast_horizon_weeks": 12,
            "season_start_date": "2025-03-01",
            "replenishment_strategy": "weekly",
            "dc_holdback_percentage": 0.45,
            "markdown_checkpoint_week": 6
        }
    })
    workflow_id = create_response.json()["workflow_id"]

    # Get status
    response = client.get(f"/api/workflows/{workflow_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert data["workflow_type"] == "forecast"
    assert data["status"] in ["pending", "running", "completed", "failed", "awaiting_approval"]
    assert data["progress_pct"] >= 0 and data["progress_pct"] <= 100


def test_get_workflow_status_not_found():
    """Test GET /api/workflows/{workflow_id} with invalid ID."""

    response = client.get("/api/workflows/invalid_id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_workflow_results_not_completed():
    """Test GET /api/workflows/{workflow_id}/results before completion."""

    # Create workflow
    create_response = client.post("/api/workflows/forecast", json={
        "category_id": "womens_dresses",
        "parameters": {
            "forecast_horizon_weeks": 12,
            "season_start_date": "2025-03-01",
            "replenishment_strategy": "none",
            "dc_holdback_percentage": 0.0,
            "markdown_checkpoint_week": None
        }
    })
    workflow_id = create_response.json()["workflow_id"]

    # Try to get results
    response = client.get(f"/api/workflows/{workflow_id}/results")

    # Should fail because workflow is not completed
    assert response.status_code in [400, 404]
```

**Expected Output:**
- All tests passing
- Workflow creation returns valid `workflow_id`
- Status endpoint returns workflow state
- Results endpoint validates completion

---

### Task 8: Manual Testing & Verification

Test workflow endpoints manually using curl or Postman.

**Test 1: Create Forecast Workflow**

```bash
curl -X POST http://localhost:8000/api/workflows/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "womens_dresses",
    "parameters": {
      "forecast_horizon_weeks": 12,
      "season_start_date": "2025-03-01",
      "replenishment_strategy": "none",
      "dc_holdback_percentage": 0.0,
      "markdown_checkpoint_week": 6
    }
  }'
```

**Expected Response:**
```json
{
  "workflow_id": "wf_abc123def456",
  "status": "pending",
  "websocket_url": "ws://localhost:8000/api/workflows/wf_abc123def456/stream"
}
```

**Test 2: Get Workflow Status**

```bash
curl http://localhost:8000/api/workflows/wf_abc123def456
```

**Expected Response:**
```json
{
  "workflow_id": "wf_abc123def456",
  "workflow_type": "forecast",
  "status": "pending",
  "current_agent": null,
  "progress_pct": 0,
  "started_at": null,
  "updated_at": "2025-10-19T10:30:00Z",
  "completed_at": null,
  "error_message": null
}
```

**Test 3: Create Re-Forecast Workflow**

```bash
curl -X POST http://localhost:8000/api/workflows/reforecast \
  -H "Content-Type: application/json" \
  -d '{
    "forecast_id": "f_spring_2025",
    "actual_sales_week_1_to_n": 3200,
    "forecasted_week_1_to_n": 2550,
    "remaining_weeks": 8,
    "variance_pct": 0.255
  }'
```

**Expected Response:**
```json
{
  "workflow_id": "wf_def456abc789",
  "status": "pending",
  "websocket_url": "ws://localhost:8000/api/workflows/wf_def456abc789/stream"
}
```

**Test 4: Verify Database Entries**

```bash
# Connect to SQLite database
sqlite3 backend/fashion_forecast.db

# Query workflows table
SELECT workflow_id, workflow_type, status, category_id, forecast_horizon_weeks
FROM workflows
ORDER BY created_at DESC
LIMIT 5;
```

**Expected Output:**
- 2 workflow entries (1 forecast, 1 reforecast)
- Correct parameters stored
- Status = "pending"

---

## Dev Notes

### Workflow Orchestration Pattern

**Current Implementation (Phase 3 - Scaffolding):**
- Endpoints accept requests and create workflow sessions in database
- No actual agent execution (placeholder for Phase 8)
- Returns workflow_id and WebSocket URL immediately

**Future Implementation (Phase 8 - Orchestrator Agent):**
```python
# In WorkflowService.create_forecast_workflow()
from openai_agents import Agent, Session

orchestrator = Agent(
    name="Orchestrator",
    instructions="""
    You coordinate 3 specialized agents (Demand, Inventory, Pricing).
    Pass SeasonParameters to each agent for context-rich handoffs.
    Monitor variance and dynamically enable re-forecast handoff.
    """,
    model="gpt-4o-mini",
    handoffs=["demand", "inventory", "pricing"]
)

session = Session()
result = session.run(orchestrator, input={
    "action": "generate_forecast",
    "category_id": request.category_id,
    "parameters": request.parameters.model_dump()
})
```

**Parameter-Driven Agent Behavior:**
- **Replenishment Strategy = "none":** Orchestrator skips replenishment phase entirely
- **DC Holdback = 0%:** Inventory Agent allocates 100% to stores at Week 0
- **Markdown Checkpoint = null:** Orchestrator skips Pricing Agent
- **Variance > 20%:** Orchestrator dynamically enables re-forecast handoff

### Workflow State Machine

```
pending → running → completed
                 → failed
                 → awaiting_approval → running → completed/failed
```

**Status Transitions:**
- `pending`: Workflow created, not yet started
- `running`: Orchestrator executing, current_agent updated
- `awaiting_approval`: Human-in-the-loop approval required (manufacturing order, markdown)
- `completed`: All agents finished, results saved
- `failed`: Agent error or timeout

### WebSocket URL Construction

**Pattern:** `ws://{host}/api/workflows/{workflow_id}/stream`

**Examples:**
- Local dev: `ws://localhost:8000/api/workflows/wf_abc123/stream`
- Production: `wss://api.fashionforecast.com/api/workflows/wf_abc123/stream`

**Note:** WebSocket server implementation is in PHASE3-008. This story only constructs the URL.

### Database Design Rationale

**Why JSON columns for input_data/output_data?**
- Flexible schema (parameters change between Zara/Standard archetypes)
- Avoids complex foreign key relationships for workflow context
- Easy to serialize/deserialize for agent handoffs

**Why separate workflows table from forecasts table?**
- Workflows are ephemeral (track execution state)
- Forecasts are permanent (business artifacts)
- One workflow can produce multiple forecasts (re-forecast scenarios)

### Critical References

- **Planning Spec:** `planning/3_technical_architecture_v3.3.md` lines 1650-1724 (Workflow endpoints)
- **Implementation Plan:** `implementation_plan.md` lines 257-272 (Task 7 details)
- **PRD:** `planning/4_prd_v3.3.md` lines 800-899 (Real-time updates, variance monitoring)

---

## Testing

### Manual Testing Checklist

- [ ] `POST /api/workflows/forecast` creates workflow with valid `workflow_id`
- [ ] Response includes `websocket_url` with correct format
- [ ] `GET /api/workflows/{workflow_id}` returns workflow status
- [ ] `POST /api/workflows/reforecast` creates re-forecast workflow
- [ ] Database `workflows` table populated with correct parameters
- [ ] OpenAPI docs display all 4 endpoints at `/docs`
- [ ] Invalid `workflow_id` returns 404 error
- [ ] Workflow status includes `progress_pct` (0-100)
- [ ] All Pydantic models validate input correctly
- [ ] Logs show workflow creation events

### Verification Commands

```bash
# Start FastAPI server
cd backend
uv run uvicorn app.main:app --reload

# Open browser to OpenAPI docs
open http://localhost:8000/docs

# Test forecast workflow endpoint
curl -X POST http://localhost:8000/api/workflows/forecast \
  -H "Content-Type: application/json" \
  -d @test_forecast_request.json

# Test workflow status endpoint
curl http://localhost:8000/api/workflows/wf_abc123

# Run pytest tests
uv run pytest tests/test_workflows.py -v

# Check database
sqlite3 backend/fashion_forecast.db "SELECT * FROM workflows;"
```

---

## File List

**Files to Create:**
- `backend/app/models/workflow.py` (Workflow SQLAlchemy model + WorkflowStatus enum)
- `backend/app/schemas/workflow.py` (5 Pydantic models: WorkflowCreateRequest, ReforecastRequest, WorkflowResponse, WorkflowStatusResponse, WorkflowResultsResponse)
- `backend/app/services/workflow_service.py` (WorkflowService class with 4 methods)
- `backend/app/api/workflows.py` (FastAPI router with 4 endpoints)
- `backend/tests/test_workflows.py` (pytest tests for workflow endpoints)
- `backend/alembic/versions/XXXX_add_workflows_table.py` (Alembic migration)

**Files to Modify:**
- `backend/app/main.py` (register workflow router)
- `backend/app/db/base.py` (import Workflow model for Alembic autogenerate)

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

_Dev Agent notes completion details here_

---

## Definition of Done

- [ ] Workflow SQLAlchemy model created with all required columns
- [ ] WorkflowStatus enum defined (5 states)
- [ ] 5 Pydantic schemas created with validation
- [ ] WorkflowService class with 4 methods implemented
- [ ] 4 FastAPI endpoints functional (forecast, reforecast, status, results)
- [ ] Workflow router registered in main.py
- [ ] Alembic migration applied (workflows table exists)
- [ ] All pytest tests passing
- [ ] OpenAPI docs display all endpoints
- [ ] Manual testing with curl successful
- [ ] Database stores workflow sessions correctly
- [ ] WebSocket URLs constructed correctly
- [ ] Logging shows workflow creation events
- [ ] File List updated with all created/modified files

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
**Story Points:** 4
**Priority:** P0 (Blocker for Phase 8 - Orchestrator Agent)
