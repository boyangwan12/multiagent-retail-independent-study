"""Service for processing human-in-the-loop approvals."""

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

        # For Phase 3, allow approval from pending or awaiting_approval state
        # Phase 8 will use awaiting_approval exclusively
        if workflow.status not in [WorkflowStatus.pending, WorkflowStatus.awaiting_approval]:
            logger.warning(
                f"Workflow {request.workflow_id} status is {workflow.status.value}, "
                "proceeding anyway (Phase 3 placeholder)"
            )

        # Extract forecast total from workflow context
        # (In Phase 8, this would come from Demand Agent output)
        forecast_total = workflow.input_data.get("forecast_total", 8000) if workflow.input_data else 8000

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


def get_approval_service(db: Session = None) -> ApprovalService:
    """Factory function for ApprovalService (dependency injection)."""
    if db is None:
        from app.database.db import SessionLocal
        db = SessionLocal()
    return ApprovalService(db)
