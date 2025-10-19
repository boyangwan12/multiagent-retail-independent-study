# Story: Approval Endpoints - Human-in-the-Loop Manufacturing & Markdown Approvals

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-010
**Status:** Draft
**Estimate:** 2 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-004 (FastAPI Setup), PHASE3-007 (Workflow Orchestration), PHASE3-008 (WebSocket Server)

---

## Story

As a backend developer,
I want to create approval endpoints that handle human-in-the-loop decisions for manufacturing orders and markdown recommendations,
So that users can review agent proposals, adjust parameters (safety stock, elasticity), and trigger agent recalculation or final acceptance.

**Business Value:** Human-in-the-loop approvals are **critical for trust and control**. This story enables PRD Story 1.5 (Approve Manufacturing Order) and Story 4.3 (Apply Markdown), where users can iteratively adjust parameters and see updated recommendations before committing to decisions. This builds confidence in AI-driven recommendations while maintaining human oversight.

**Epic Context:** This is Task 10 of 14 in Phase 3. It builds on workflow orchestration (PHASE3-007) and WebSocket server (PHASE3-008) to add the approval layer. These endpoints enable frontend approval modals with real-time parameter adjustment. Phase 8 (Orchestrator Agent) will trigger these approvals when agents require human input.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `POST /api/approvals/manufacturing` endpoint accepts manufacturing order approval
2. ✅ Endpoint accepts adjusted safety stock % (10-30%) and returns recalculated manufacturing quantity
3. ✅ `POST /api/approvals/markdown` endpoint accepts markdown approval
4. ✅ Endpoint accepts elasticity coefficient (1.0-3.0) and returns recalculated markdown %
5. ✅ Both endpoints update workflow status in database (pending → running → awaiting_approval → running → completed)
6. ✅ Approval triggers agent continuation via WebSocket broadcast
7. ✅ "Modify" action recalculates and returns updated recommendation without committing
8. ✅ "Accept" action saves decision to database and advances workflow

### Quality Requirements

9. ✅ Pydantic schemas validate input parameters (safety stock 10-30%, elasticity 1.0-3.0)
10. ✅ Database transactions ensure atomic updates
11. ✅ WebSocket broadcasts approval events to all connected clients
12. ✅ Error handling for invalid workflow states
13. ✅ Logging shows approval events and parameter adjustments

---

## Tasks

### Task 1: Create Approval Pydantic Schemas

Create request/response models for approval endpoints.

**File:** `backend/app/schemas/approval.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class ManufacturingApprovalRequest(BaseModel):
    """Request to approve or modify manufacturing order."""

    workflow_id: str = Field(..., description="Workflow identifier")
    action: Literal["modify", "accept"] = Field(..., description="Approval action")
    safety_stock_pct: float = Field(..., ge=0.10, le=0.30, description="Safety stock percentage (10-30%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "safety_stock_pct": 0.25
            }
        }
    )


class ManufacturingApprovalResponse(BaseModel):
    """Response after manufacturing approval (modify or accept)."""

    workflow_id: str
    action: Literal["modify", "accept"]
    manufacturing_qty: int = Field(..., description="Recalculated manufacturing quantity")
    safety_stock_pct: float
    forecast_total: int = Field(..., description="Original forecast total")
    reasoning: str = Field(..., description="Agent reasoning for safety stock adjustment")
    status: Literal["recalculated", "approved"] = Field(..., description="recalculated if modify, approved if accept")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "manufacturing_qty": 10000,
                "safety_stock_pct": 0.25,
                "forecast_total": 8000,
                "reasoning": "Safety stock increased to 25% to account for no replenishment buffer",
                "status": "recalculated"
            }
        }
    )


class MarkdownApprovalRequest(BaseModel):
    """Request to approve or adjust markdown recommendation."""

    workflow_id: str = Field(..., description="Workflow identifier")
    action: Literal["modify", "accept"] = Field(..., description="Approval action")
    elasticity_coefficient: float = Field(..., ge=1.0, le=3.0, description="Elasticity coefficient (1.0-3.0)")
    actual_sell_through_pct: float = Field(..., ge=0.0, le=1.0, description="Actual sell-through by checkpoint week")
    target_sell_through_pct: float = Field(0.60, ge=0.0, le=1.0, description="Target sell-through (default 60%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "elasticity_coefficient": 2.5,
                "actual_sell_through_pct": 0.55,
                "target_sell_through_pct": 0.60
            }
        }
    )


class MarkdownApprovalResponse(BaseModel):
    """Response after markdown approval (modify or accept)."""

    workflow_id: str
    action: Literal["modify", "accept"]
    recommended_markdown_pct: float = Field(..., ge=0.0, le=0.40, description="Recalculated markdown %")
    elasticity_coefficient: float
    gap_pct: float = Field(..., description="Sell-through gap")
    expected_demand_lift_pct: float = Field(..., description="Expected sales increase")
    reasoning: str = Field(..., description="Markdown calculation explanation")
    status: Literal["recalculated", "approved"] = Field(..., description="recalculated if modify, approved if accept")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "recommended_markdown_pct": 0.125,
                "elasticity_coefficient": 2.5,
                "gap_pct": 0.05,
                "expected_demand_lift_pct": 0.1875,
                "reasoning": "5.0% gap × 2.5 elasticity = 12.5% markdown",
                "status": "recalculated"
            }
        }
    )
```

**Expected Output:**
- 4 Pydantic models (2 request, 2 response)
- Parameter validation (safety stock 10-30%, elasticity 1.0-3.0)
- Example JSON payloads

---

### Task 2: Create Approval Service

Create business logic for processing approvals.

**File:** `backend/app/services/approval_service.py`

```python
from sqlalchemy.orm import Session
from ..models.workflow import Workflow, WorkflowStatus
from ..schemas.approval import (
    ManufacturingApprovalRequest,
    ManufacturingApprovalResponse,
    MarkdownApprovalRequest,
    MarkdownApprovalResponse
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ApprovalService:
    """Service for processing human-in-the-loop approvals."""

    def __init__(self, db: Session):
        self.db = db

    def process_manufacturing_approval(
        self,
        request: ManufacturingApprovalRequest
    ) -> ManufacturingApprovalResponse:
        """
        Process manufacturing order approval (modify or accept).

        Args:
            request: Approval request with action and safety_stock_pct

        Returns:
            ManufacturingApprovalResponse with recalculated values

        Raises:
            ValueError: If workflow not found or invalid state
        """
        # Fetch workflow
        workflow = self.db.query(Workflow).filter(
            Workflow.workflow_id == request.workflow_id
        ).first()

        if not workflow:
            raise ValueError(f"Workflow {request.workflow_id} not found")

        if workflow.status != WorkflowStatus.awaiting_approval:
            raise ValueError(
                f"Workflow {request.workflow_id} is not awaiting approval "
                f"(status: {workflow.status.value})"
            )

        # Extract forecast total from workflow context
        # (In Phase 8, this would come from Demand Agent output)
        forecast_total = workflow.input_data.get("forecast_total", 8000)  # Placeholder

        # Calculate manufacturing quantity
        manufacturing_qty = int(forecast_total * (1 + request.safety_stock_pct))

        # Generate reasoning
        reasoning = self._generate_safety_stock_reasoning(
            safety_stock_pct=request.safety_stock_pct,
            replenishment_strategy=workflow.replenishment_strategy
        )

        # Handle action
        if request.action == "modify":
            # Recalculate and return without committing
            logger.info(
                f"Manufacturing approval modified: workflow={request.workflow_id}, "
                f"safety_stock={request.safety_stock_pct:.0%}, mfg_qty={manufacturing_qty}"
            )

            return ManufacturingApprovalResponse(
                workflow_id=request.workflow_id,
                action="modify",
                manufacturing_qty=manufacturing_qty,
                safety_stock_pct=request.safety_stock_pct,
                forecast_total=forecast_total,
                reasoning=reasoning,
                status="recalculated"
            )

        elif request.action == "accept":
            # Save decision to database and advance workflow
            workflow.status = WorkflowStatus.running
            workflow.updated_at = datetime.utcnow()

            # Store approved manufacturing quantity in workflow output
            if not workflow.output_data:
                workflow.output_data = {}
            workflow.output_data["manufacturing_qty"] = manufacturing_qty
            workflow.output_data["safety_stock_pct"] = request.safety_stock_pct

            self.db.commit()
            self.db.refresh(workflow)

            logger.info(
                f"Manufacturing approval accepted: workflow={request.workflow_id}, "
                f"mfg_qty={manufacturing_qty}"
            )

            # TODO (Phase 8): Trigger agent continuation via WebSocket
            # await broadcast_agent_started(request.workflow_id, "Inventory Agent")

            return ManufacturingApprovalResponse(
                workflow_id=request.workflow_id,
                action="accept",
                manufacturing_qty=manufacturing_qty,
                safety_stock_pct=request.safety_stock_pct,
                forecast_total=forecast_total,
                reasoning=reasoning,
                status="approved"
            )

    def process_markdown_approval(
        self,
        request: MarkdownApprovalRequest
    ) -> MarkdownApprovalResponse:
        """
        Process markdown recommendation approval (modify or accept).

        Args:
            request: Approval request with elasticity and sell-through data

        Returns:
            MarkdownApprovalResponse with recalculated markdown

        Raises:
            ValueError: If workflow not found or invalid state
        """
        # Fetch workflow
        workflow = self.db.query(Workflow).filter(
            Workflow.workflow_id == request.workflow_id
        ).first()

        if not workflow:
            raise ValueError(f"Workflow {request.workflow_id} not found")

        # Calculate markdown using Gap × Elasticity formula
        gap = request.target_sell_through_pct - request.actual_sell_through_pct

        if gap <= 0:
            # On track or ahead of target - no markdown needed
            markdown_pct = 0.0
            reasoning = "On track or ahead of target, no markdown needed"
        else:
            # Calculate markdown
            markdown_raw = gap * request.elasticity_coefficient
            markdown_capped = min(markdown_raw, 0.40)  # Cap at 40%
            markdown_pct = round(markdown_capped * 20) / 20  # Round to nearest 5%

            reasoning = (
                f"{gap*100:.1f}% gap × {request.elasticity_coefficient} elasticity = "
                f"{markdown_pct*100:.0f}% markdown"
            )

        # Expected demand lift (assumes 1% markdown = 1.5% demand increase)
        expected_lift = markdown_pct * 1.5

        # Handle action
        if request.action == "modify":
            # Recalculate and return without committing
            logger.info(
                f"Markdown approval modified: workflow={request.workflow_id}, "
                f"elasticity={request.elasticity_coefficient}, markdown={markdown_pct:.0%}"
            )

            return MarkdownApprovalResponse(
                workflow_id=request.workflow_id,
                action="modify",
                recommended_markdown_pct=markdown_pct,
                elasticity_coefficient=request.elasticity_coefficient,
                gap_pct=gap,
                expected_demand_lift_pct=expected_lift,
                reasoning=reasoning,
                status="recalculated"
            )

        elif request.action == "accept":
            # Save decision to database and advance workflow
            workflow.status = WorkflowStatus.running
            workflow.updated_at = datetime.utcnow()

            # Store approved markdown in workflow output
            if not workflow.output_data:
                workflow.output_data = {}
            workflow.output_data["markdown_pct"] = markdown_pct
            workflow.output_data["elasticity_coefficient"] = request.elasticity_coefficient

            self.db.commit()
            self.db.refresh(workflow)

            logger.info(
                f"Markdown approval accepted: workflow={request.workflow_id}, "
                f"markdown={markdown_pct:.0%}"
            )

            # TODO (Phase 8): Trigger markdown application and re-forecast
            # await broadcast_agent_started(request.workflow_id, "Pricing Agent")

            return MarkdownApprovalResponse(
                workflow_id=request.workflow_id,
                action="accept",
                recommended_markdown_pct=markdown_pct,
                elasticity_coefficient=request.elasticity_coefficient,
                gap_pct=gap,
                expected_demand_lift_pct=expected_lift,
                reasoning=reasoning,
                status="approved"
            )

    def _generate_safety_stock_reasoning(
        self,
        safety_stock_pct: float,
        replenishment_strategy: str
    ) -> str:
        """
        Generate agent reasoning for safety stock adjustment.

        Args:
            safety_stock_pct: Approved safety stock percentage
            replenishment_strategy: Replenishment strategy from workflow

        Returns:
            Reasoning string explaining safety stock choice
        """
        if replenishment_strategy == "none":
            if safety_stock_pct >= 0.25:
                return (
                    f"No replenishment configured → safety stock set to {safety_stock_pct:.0%} "
                    "to account for lack of ongoing replenishment buffer"
                )
            else:
                return (
                    f"Safety stock set to {safety_stock_pct:.0%} (below recommended 25% for "
                    "no-replenishment scenarios)"
                )
        else:
            return (
                f"Ongoing {replenishment_strategy} replenishment provides buffer → "
                f"safety stock set to {safety_stock_pct:.0%}"
            )


def get_approval_service(db: Session) -> ApprovalService:
    """Factory function for ApprovalService (dependency injection)."""
    return ApprovalService(db)
```

**Expected Output:**
- ApprovalService class with 2 public methods
- Manufacturing approval logic (recalculate or accept)
- Markdown approval logic with Gap × Elasticity formula
- Reasoning generation based on parameters
- Database transaction management

---

### Task 3: Create Approval API Endpoints

Create FastAPI router with approval endpoints.

**File:** `backend/app/api/approvals.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..schemas.approval import (
    ManufacturingApprovalRequest,
    ManufacturingApprovalResponse,
    MarkdownApprovalRequest,
    MarkdownApprovalResponse
)
from ..services.approval_service import ApprovalService, get_approval_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.post("/manufacturing", response_model=ManufacturingApprovalResponse)
async def approve_manufacturing_order(
    request: ManufacturingApprovalRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Approve or modify manufacturing order with adjusted safety stock.

    **Workflow:**
    1. User reviews manufacturing order in approval modal
    2. User adjusts safety stock slider (10-30%)
    3. If action = "modify": Agent recalculates, modal updates in real-time
    4. If action = "accept": Saves to database, closes modal, advances workflow

    **Example Request (Modify):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "modify",
      "safety_stock_pct": 0.25
    }
    ```

    **Example Response (Modify):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "modify",
      "manufacturing_qty": 10000,
      "safety_stock_pct": 0.25,
      "forecast_total": 8000,
      "reasoning": "No replenishment configured → safety stock set to 25%",
      "status": "recalculated"
    }
    ```

    **Example Request (Accept):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "accept",
      "safety_stock_pct": 0.20
    }
    ```

    **Example Response (Accept):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "accept",
      "manufacturing_qty": 9600,
      "safety_stock_pct": 0.20,
      "forecast_total": 8000,
      "reasoning": "Ongoing weekly replenishment provides buffer → safety stock set to 20%",
      "status": "approved"
    }
    ```
    """
    try:
        response = service.process_manufacturing_approval(request)

        if request.action == "accept":
            logger.info(f"Manufacturing order approved: {request.workflow_id}")
            # TODO: Broadcast via WebSocket
            # await broadcast_agent_started(request.workflow_id, "Inventory Agent")

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process manufacturing approval: {e}")
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {str(e)}")


@router.post("/markdown", response_model=MarkdownApprovalResponse)
async def approve_markdown_recommendation(
    request: MarkdownApprovalRequest,
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Approve or modify markdown recommendation with adjusted elasticity.

    **Workflow:**
    1. User reviews markdown recommendation in Week 6 checkpoint modal
    2. User adjusts elasticity slider (1.0-3.0)
    3. If action = "modify": Agent recalculates markdown, modal updates
    4. If action = "accept": Applies markdown, triggers re-forecast

    **Example Request (Modify):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "modify",
      "elasticity_coefficient": 2.5,
      "actual_sell_through_pct": 0.55,
      "target_sell_through_pct": 0.60
    }
    ```

    **Example Response (Modify):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "modify",
      "recommended_markdown_pct": 0.125,
      "elasticity_coefficient": 2.5,
      "gap_pct": 0.05,
      "expected_demand_lift_pct": 0.1875,
      "reasoning": "5.0% gap × 2.5 elasticity = 12.5% markdown (rounded to 15%)",
      "status": "recalculated"
    }
    ```

    **Example Request (Accept):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "accept",
      "elasticity_coefficient": 2.0,
      "actual_sell_through_pct": 0.55,
      "target_sell_through_pct": 0.60
    }
    ```

    **Example Response (Accept):**
    ```json
    {
      "workflow_id": "wf_abc123",
      "action": "accept",
      "recommended_markdown_pct": 0.10,
      "elasticity_coefficient": 2.0,
      "gap_pct": 0.05,
      "expected_demand_lift_pct": 0.15,
      "reasoning": "5.0% gap × 2.0 elasticity = 10% markdown",
      "status": "approved"
    }
    ```
    """
    try:
        response = service.process_markdown_approval(request)

        if request.action == "accept":
            logger.info(f"Markdown approved: {request.workflow_id}, markdown={response.recommended_markdown_pct:.0%}")
            # TODO: Broadcast via WebSocket
            # await broadcast_agent_started(request.workflow_id, "Pricing Agent")

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process markdown approval: {e}")
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {str(e)}")
```

**Expected Output:**
- 2 FastAPI endpoints with dependency injection
- OpenAPI documentation with examples
- Error handling with meaningful HTTP status codes
- Placeholder for WebSocket broadcasting

---

### Task 4: Register Approval Router in Main Application

Add approval router to FastAPI app.

**File:** `backend/app/main.py` (modifications)

```python
from fastapi import FastAPI
from .api import workflows, websocket, approvals  # Import approval router

app = FastAPI(
    title="Fashion Forecast API",
    description="Multi-agent retail forecasting system with parameter-driven workflows",
    version="0.1.0"
)

# Include routers
app.include_router(workflows.router)
app.include_router(websocket.router)
app.include_router(approvals.router)  # Register approval endpoints

# Other routers...
```

**Expected Output:**
- Approval endpoints registered at `/api/approvals/*`
- OpenAPI docs include approval endpoints

---

### Task 5: Test Approval Endpoints

Create pytest tests for approval functionality.

**File:** `backend/tests/test_approvals.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_manufacturing_approval_modify():
    """Test manufacturing approval with modify action."""

    # First create a workflow (prerequisite)
    workflow_response = client.post("/api/workflows/forecast", json={
        "category_id": "womens_dresses",
        "parameters": {
            "forecast_horizon_weeks": 12,
            "season_start_date": "2025-03-01",
            "replenishment_strategy": "none",
            "dc_holdback_percentage": 0.0,
            "markdown_checkpoint_week": 6
        }
    })
    workflow_id = workflow_response.json()["workflow_id"]

    # Mock: Set workflow status to awaiting_approval
    # (In real implementation, Demand Agent would set this)

    # Test modify action
    response = client.post("/api/approvals/manufacturing", json={
        "workflow_id": workflow_id,
        "action": "modify",
        "safety_stock_pct": 0.25
    })

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "modify"
    assert data["safety_stock_pct"] == 0.25
    assert data["manufacturing_qty"] > 0  # Should be forecast × 1.25
    assert data["status"] == "recalculated"
    assert "reasoning" in data


def test_manufacturing_approval_accept():
    """Test manufacturing approval with accept action."""

    # Create workflow
    workflow_response = client.post("/api/workflows/forecast", json={
        "category_id": "womens_dresses",
        "parameters": {
            "forecast_horizon_weeks": 12,
            "season_start_date": "2025-03-01",
            "replenishment_strategy": "weekly",
            "dc_holdback_percentage": 0.45,
            "markdown_checkpoint_week": 6
        }
    })
    workflow_id = workflow_response.json()["workflow_id"]

    # Test accept action
    response = client.post("/api/approvals/manufacturing", json={
        "workflow_id": workflow_id,
        "action": "accept",
        "safety_stock_pct": 0.20
    })

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "accept"
    assert data["safety_stock_pct"] == 0.20
    assert data["status"] == "approved"


def test_manufacturing_approval_invalid_safety_stock():
    """Test manufacturing approval with invalid safety stock (out of range)."""

    workflow_id = "wf_test123"

    # Safety stock below 10%
    response = client.post("/api/approvals/manufacturing", json={
        "workflow_id": workflow_id,
        "action": "modify",
        "safety_stock_pct": 0.05
    })

    assert response.status_code == 422  # Pydantic validation error


def test_markdown_approval_modify():
    """Test markdown approval with modify action."""

    workflow_id = "wf_test456"

    response = client.post("/api/approvals/markdown", json={
        "workflow_id": workflow_id,
        "action": "modify",
        "elasticity_coefficient": 2.5,
        "actual_sell_through_pct": 0.55,
        "target_sell_through_pct": 0.60
    })

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "modify"
    assert data["elasticity_coefficient"] == 2.5
    assert data["gap_pct"] == 0.05
    assert data["recommended_markdown_pct"] > 0
    assert data["status"] == "recalculated"
    assert "reasoning" in data


def test_markdown_approval_accept():
    """Test markdown approval with accept action."""

    workflow_id = "wf_test789"

    response = client.post("/api/approvals/markdown", json={
        "workflow_id": workflow_id,
        "action": "accept",
        "elasticity_coefficient": 2.0,
        "actual_sell_through_pct": 0.55,
        "target_sell_through_pct": 0.60
    })

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "accept"
    assert data["status"] == "approved"


def test_markdown_approval_no_markdown_needed():
    """Test markdown approval when sell-through exceeds target."""

    workflow_id = "wf_test_on_track"

    response = client.post("/api/approvals/markdown", json={
        "workflow_id": workflow_id,
        "action": "modify",
        "elasticity_coefficient": 2.0,
        "actual_sell_through_pct": 0.65,  # Above target
        "target_sell_through_pct": 0.60
    })

    assert response.status_code == 200
    data = response.json()
    assert data["recommended_markdown_pct"] == 0.0
    assert "no markdown needed" in data["reasoning"].lower() or "on track" in data["reasoning"].lower()
```

**Expected Output:**
- All tests passing
- Modify action recalculates without saving
- Accept action saves and advances workflow
- Validation errors for out-of-range parameters

---

### Task 6: Manual Testing with curl

Test approval endpoints manually.

**Test 1: Manufacturing Approval (Modify)**

```bash
curl -X POST http://localhost:8000/api/approvals/manufacturing \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf_abc123",
    "action": "modify",
    "safety_stock_pct": 0.25
  }'
```

**Expected Response:**
```json
{
  "workflow_id": "wf_abc123",
  "action": "modify",
  "manufacturing_qty": 10000,
  "safety_stock_pct": 0.25,
  "forecast_total": 8000,
  "reasoning": "No replenishment configured → safety stock set to 25%",
  "status": "recalculated"
}
```

**Test 2: Manufacturing Approval (Accept)**

```bash
curl -X POST http://localhost:8000/api/approvals/manufacturing \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf_abc123",
    "action": "accept",
    "safety_stock_pct": 0.20
  }'
```

**Expected Response:**
```json
{
  "workflow_id": "wf_abc123",
  "action": "accept",
  "manufacturing_qty": 9600,
  "safety_stock_pct": 0.20,
  "forecast_total": 8000,
  "reasoning": "Ongoing weekly replenishment provides buffer → safety stock set to 20%",
  "status": "approved"
}
```

**Test 3: Markdown Approval (Modify)**

```bash
curl -X POST http://localhost:8000/api/approvals/markdown \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf_abc123",
    "action": "modify",
    "elasticity_coefficient": 2.5,
    "actual_sell_through_pct": 0.55,
    "target_sell_through_pct": 0.60
  }'
```

**Expected Response:**
```json
{
  "workflow_id": "wf_abc123",
  "action": "modify",
  "recommended_markdown_pct": 0.125,
  "elasticity_coefficient": 2.5,
  "gap_pct": 0.05,
  "expected_demand_lift_pct": 0.1875,
  "reasoning": "5.0% gap × 2.5 elasticity = 12.5% markdown",
  "status": "recalculated"
}
```

---

## Dev Notes

### Human-in-the-Loop Approval Pattern

**Modify Action (Iterative Adjustment):**
```
User → Adjust slider → POST /api/approvals/* (action=modify)
                    ← Recalculated values (no database save)
User → Adjust slider again → POST (action=modify)
                          ← Updated values
User → Satisfied → POST (action=accept)
                ← Saved to database, workflow continues
```

**Frontend Pattern:**
```javascript
// Real-time slider adjustment
const handleSliderChange = async (value) => {
  const response = await fetch('/api/approvals/manufacturing', {
    method: 'POST',
    body: JSON.stringify({
      workflow_id: 'wf_abc123',
      action: 'modify',
      safety_stock_pct: value
    })
  });
  const data = await response.json();

  // Update modal in real-time
  setManufacturingQty(data.manufacturing_qty);
  setReasoning(data.reasoning);
};

// Final acceptance
const handleAccept = async () => {
  await fetch('/api/approvals/manufacturing', {
    method: 'POST',
    body: JSON.stringify({
      workflow_id: 'wf_abc123',
      action: 'accept',
      safety_stock_pct: selectedSafetyStock
    })
  });

  // Close modal, advance workflow
  closeModal();
};
```

### Safety Stock Reasoning Logic

**Replenishment Strategy = "none" (Zara-style):**
- Recommended safety stock: 25%
- Reasoning: "No replenishment configured → safety stock set to 25% to account for lack of buffer"

**Replenishment Strategy = "weekly" or "bi-weekly":**
- Recommended safety stock: 20%
- Reasoning: "Ongoing weekly replenishment provides buffer → safety stock set to 20%"

**User Overrides:**
- User can adjust slider to any value 10-30%
- Reasoning updates dynamically to explain user's choice

### Gap × Elasticity Markdown Formula

**Formula:**
```python
gap = target_sell_through - actual_sell_through  # e.g., 0.60 - 0.55 = 0.05
markdown_raw = gap × elasticity_coefficient       # e.g., 0.05 × 2.0 = 0.10
markdown_rounded = round(markdown_raw × 20) / 20  # Round to nearest 5%: 0.10 → 10%
markdown_final = min(markdown_rounded, 0.40)      # Cap at 40%
```

**Example Calculations:**
| Gap | Elasticity | Raw | Rounded | Final |
|-----|-----------|-----|---------|-------|
| 5% | 2.0 | 10% | 10% | 10% |
| 5% | 2.5 | 12.5% | 15% | 15% |
| 10% | 2.0 | 20% | 20% | 20% |
| 25% | 2.0 | 50% | 50% | **40%** (capped) |

### Workflow Status State Machine

```
pending → running → awaiting_approval (manufacturing)
                 ← modify (recalculate, stay in awaiting_approval)
                 ← accept (advance to running)
                 → running → awaiting_approval (markdown)
                          ← modify
                          ← accept → running → completed
```

### Integration with Phase 8 (Orchestrator Agent)

**Current (Phase 3):**
- Endpoints exist, placeholder logic
- No actual agent calls
- Manual workflow status updates

**Future (Phase 8):**
```python
# In Inventory Agent tool
async def approve_manufacturing_order(manufacturing_qty: int) -> dict:
    # Trigger human-in-the-loop via WebSocket
    await broadcast_human_input_required(
        workflow_id=workflow_id,
        agent="Inventory Agent",
        action="approve_manufacturing_order",
        data={
            "manufacturing_qty": manufacturing_qty,
            "forecast_total": forecast_total,
            "safety_stock_pct": 0.20
        },
        options=["modify", "accept"]
    )

    # Wait for user approval (workflow pauses)
    # User interacts with modal, calls /api/approvals/manufacturing
    # Approval service returns result to agent
```

### Critical References

- **Planning Spec:** `planning/3_technical_architecture_v3.3.md` lines 1100-1350 (Inventory/Pricing agents)
- **Implementation Plan:** `implementation_plan.md` lines 354-366 (Task 10 details)
- **PRD:** `planning/4_prd_v3.3.md` lines 340-360 (Story 1.5), lines 557-605 (Story 4.3)

---

## Testing

### Manual Testing Checklist

- [ ] `POST /api/approvals/manufacturing` with action=modify returns recalculated values
- [ ] Modify action does NOT save to database
- [ ] `POST /api/approvals/manufacturing` with action=accept saves to database
- [ ] Accept action advances workflow status from awaiting_approval to running
- [ ] `POST /api/approvals/markdown` with action=modify recalculates markdown
- [ ] Markdown formula: Gap × Elasticity works correctly
- [ ] Markdown capped at 40%
- [ ] Markdown rounded to nearest 5%
- [ ] Safety stock validation: rejects <10% or >30%
- [ ] Elasticity validation: rejects <1.0 or >3.0
- [ ] Reasoning generated correctly based on replenishment strategy
- [ ] OpenAPI docs display approval endpoints
- [ ] All pytest tests passing

### Verification Commands

```bash
# Start FastAPI server
cd backend
uv run uvicorn app.main:app --reload

# Open OpenAPI docs
open http://localhost:8000/docs

# Test manufacturing approval (modify)
curl -X POST http://localhost:8000/api/approvals/manufacturing \
  -H "Content-Type: application/json" \
  -d @test_manufacturing_modify.json

# Test markdown approval (accept)
curl -X POST http://localhost:8000/api/approvals/markdown \
  -H "Content-Type: application/json" \
  -d @test_markdown_accept.json

# Run pytest tests
uv run pytest tests/test_approvals.py -v

# Check database after accept
sqlite3 backend/fashion_forecast.db "SELECT workflow_id, status, output_data FROM workflows WHERE workflow_id='wf_abc123';"
```

---

## File List

**Files to Create:**
- `backend/app/schemas/approval.py` (4 Pydantic models: ManufacturingApprovalRequest, ManufacturingApprovalResponse, MarkdownApprovalRequest, MarkdownApprovalResponse)
- `backend/app/services/approval_service.py` (ApprovalService class with 2 methods)
- `backend/app/api/approvals.py` (FastAPI router with 2 endpoints)
- `backend/tests/test_approvals.py` (pytest tests for approval endpoints)

**Files to Modify:**
- `backend/app/main.py` (register approval router)

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

- [ ] 4 Pydantic schemas created with validation (safety stock 10-30%, elasticity 1.0-3.0)
- [ ] ApprovalService class with 2 methods (manufacturing, markdown)
- [ ] Manufacturing approval logic (modify recalculates, accept saves)
- [ ] Markdown approval logic with Gap × Elasticity formula
- [ ] Reasoning generation based on replenishment strategy
- [ ] 2 FastAPI endpoints functional (/manufacturing, /markdown)
- [ ] Approval router registered in main.py
- [ ] All pytest tests passing
- [ ] Modify action does NOT save to database
- [ ] Accept action saves and advances workflow
- [ ] Workflow status updates correctly (awaiting_approval → running)
- [ ] Parameter validation working (safety stock, elasticity)
- [ ] OpenAPI docs include approval endpoints
- [ ] Logging shows approval events
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
**Story Points:** 2
**Priority:** P0 (Blocker for human-in-the-loop approvals)
