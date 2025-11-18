"""FastAPI endpoints for approval workflows."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.workflow_schemas import (
    ManufacturingApprovalRequest,
    ManufacturingApprovalResponse,
    MarkdownApprovalRequest,
    MarkdownApprovalResponse
)
from app.services.approval_service import ApprovalService, get_approval_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("/manufacturing")
async def approve_manufacturing_order(
    request: ManufacturingApprovalRequest,
    db: Session = Depends(get_db)
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
    """
    try:
        service = ApprovalService(db)
        response = service.process_manufacturing_approval(request)

        if request.action == "accept":
            logger.info(f"Manufacturing order approved: {request.workflow_id}")
            # TODO: Broadcast via WebSocket
            # await broadcast_agent_started(request.workflow_id, "Inventory Agent")

        return response.model_dump()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process manufacturing approval: {e}")
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {str(e)}")


@router.post("/markdown")
async def approve_markdown_recommendation(
    request: MarkdownApprovalRequest,
    db: Session = Depends(get_db)
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
      "reasoning": "5.0% gap × 2.5 elasticity = 12.5% markdown",
      "status": "recalculated"
    }
    ```
    """
    try:
        service = ApprovalService(db)
        response = service.process_markdown_approval(request)

        if request.action == "accept":
            logger.info(f"Markdown approved: {request.workflow_id}, markdown={response.recommended_markdown_pct:.0%}")
            # TODO: Broadcast via WebSocket
            # await broadcast_agent_started(request.workflow_id, "Pricing Agent")

        return response.model_dump()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process markdown approval: {e}")
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {str(e)}")
