from sqlalchemy.orm import Session
from app.database.models import Workflow, WorkflowStatus
from app.schemas.workflow_schemas import (
    WorkflowCreateRequest,
    ReforecastRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    WorkflowResultsResponse
)
from app.agents import get_orchestrator
from datetime import datetime
import uuid
import logging

logger = logging.getLogger("fashion_forecast")


class WorkflowService:
    """Service for managing workflow orchestration."""

    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = get_orchestrator()

    def create_forecast_workflow(
        self,
        request: WorkflowCreateRequest,
        host: str = "localhost:8000"
    ) -> WorkflowResponse:
        """
        Create a new pre-season forecast workflow.

        Args:
            request: Workflow creation request with parameters
            host: Server host (unused, kept for backward compatibility)

        Returns:
            WorkflowResponse with workflow_id and status
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
            season_start_date=str(request.parameters.season_start_date),  # Convert date to string
            replenishment_strategy=request.parameters.replenishment_strategy,
            dc_holdback_percentage=request.parameters.dc_holdback_percentage,
            markdown_checkpoint_week=request.parameters.markdown_checkpoint_week,
            input_data=request.model_dump(mode='json'),  # Convert dates to strings
            output_data=None,
            error_message=None
            # Let database handle created_at, started_at, completed_at with defaults
        )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        logger.info(f"Created forecast workflow {workflow_id} for category {request.category_id}")

        # TODO (Phase 8): Execute orchestrator workflow with OpenAI Agents SDK
        # This will be implemented in Phase 8 with:
        # 1. Background task execution (asyncio/celery)
        # 2. WebSocket streaming for progress updates
        # 3. Database updates as agents complete
        #
        # Example implementation:
        # async with workflow_session():
        #     result = await self.orchestrator.run_forecast_workflow(
        #         category_id=request.category_id,
        #         parameters=request.parameters,
        #         workflow_id=workflow_id
        #     )
        #     # Update workflow with results
        #     workflow.forecast_id = result["forecast_id"]
        #     workflow.output_data = result
        #     workflow.status = WorkflowStatus.completed
        #     self.db.commit()

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="pending"
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
            host: Server host (unused, kept for backward compatibility)

        Returns:
            WorkflowResponse with workflow_id and status
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
            input_data=request.model_dump(mode='json'),  # Convert to JSON-serializable
            output_data=None,
            error_message=None
            # Let database handle timestamps with defaults
        )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        logger.info(f"Created re-forecast workflow {workflow_id} for forecast {request.forecast_id} (variance: {request.variance_pct:.1%})")

        # TODO (Phase 8): Execute re-forecast workflow with dynamic handoff
        # This will be implemented in Phase 8 with:
        # 1. Dynamic handoff enabling for re-forecast
        # 2. Pass actual sales context to Demand Agent
        # 3. Re-allocation and re-markdown execution
        #
        # Example implementation:
        # async with workflow_session():
        #     result = await self.orchestrator.run_reforecast_workflow(
        #         forecast_id=request.forecast_id,
        #         actual_sales=request.actual_sales_week_1_to_n,
        #         forecasted_sales=request.forecasted_week_1_to_n,
        #         remaining_weeks=request.remaining_weeks,
        #         variance_pct=request.variance_pct,
        #         workflow_id=workflow_id
        #     )
        #     # Update workflow with results
        #     workflow.output_data = result
        #     workflow.status = WorkflowStatus.completed
        #     self.db.commit()

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="pending"
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
