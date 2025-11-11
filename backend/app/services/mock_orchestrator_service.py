"""Mock Orchestrator Service - Now uses AgentHandoffManager for proper orchestration."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
import uuid
from sqlalchemy.orm import Session
from app.database.models import Workflow, WorkflowStatus, Forecast, Allocation, Markdown
from app.orchestrator.agent_handoff import AgentHandoffManager
from app.schemas.workflow_schemas import SeasonParameters

logger = logging.getLogger("fashion_forecast")


class MockOrchestratorService:
    """
    Mock orchestrator for Phase 4.

    Simulates running Demand, Inventory, and Pricing agents with fake delays
    and returns hard-coded mock data.

    This will be replaced with real OpenAI Agent SDK orchestration in Phase 8.
    """

    def __init__(self, db: Session):
        self.db = db
        self.handoff_manager = AgentHandoffManager()

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute workflow using AgentHandoffManager.

        Phase 5 Update: Now uses proper agent orchestration framework instead of
        hard-coded sequential calls.

        Args:
            workflow_id: Workflow ID to execute

        Returns:
            Workflow results from agent chain
        """
        logger.info(f"[ORCHESTRATOR] Starting workflow execution: {workflow_id}")

        # Get workflow from database
        workflow = self.db.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Extract season parameters from workflow input_data (which contains full parameters)
        input_data = workflow.input_data or {}
        params_dict = input_data.get("parameters", {})

        season_params = SeasonParameters(
            forecast_horizon_weeks=params_dict.get("forecast_horizon_weeks") or workflow.forecast_horizon_weeks or 12,
            season_start_date=params_dict.get("season_start_date") or workflow.season_start_date,
            season_end_date=params_dict.get("season_end_date"),  # Only in input_data
            replenishment_strategy=params_dict.get("replenishment_strategy") or workflow.replenishment_strategy or "weekly",
            dc_holdback_percentage=params_dict.get("dc_holdback_percentage") or workflow.dc_holdback_percentage or 0.45,
            markdown_checkpoint_week=params_dict.get("markdown_checkpoint_week") or workflow.markdown_checkpoint_week,
            markdown_threshold=params_dict.get("markdown_threshold", 0.6)  # Default 0.6
        )

        # Update status to running
        workflow.status = WorkflowStatus.running
        workflow.started_at = datetime.utcnow()
        workflow.current_agent = "Demand Agent"
        workflow.progress_pct = 0
        self.db.commit()

        try:
            # Register mock agents with handoff manager
            self._register_agents(workflow)

            # Execute agent chain using handoff manager
            logger.info(f"[ORCHESTRATOR] Executing agent chain: Demand → Inventory → Pricing")

            # Run agents sequentially with progress tracking
            demand_result = await self._run_agent_with_tracking(
                "demand", season_params, workflow,
                agent_name="Demand Agent", progress_start=10, progress_end=40
            )

            inventory_result = await self._run_agent_with_tracking(
                "inventory", demand_result, workflow,
                agent_name="Inventory Agent", progress_start=50, progress_end=70
            )

            pricing_result = await self._run_agent_with_tracking(
                "pricing", inventory_result, workflow,
                agent_name="Pricing Agent", progress_start=75, progress_end=95
            )

            # Combine results
            final_results = {
                "demand": demand_result,
                "inventory": inventory_result,
                "pricing": pricing_result
            }

            # Persist results to database tables
            print(f"[PERSIST] About to call persistence methods for workflow {workflow_id}", flush=True)
            self._persist_forecast_data(workflow, demand_result)
            print(f"[PERSIST] Called _persist_forecast_data", flush=True)
            self._persist_allocation_data(workflow, demand_result, inventory_result)
            print(f"[PERSIST] Called _persist_allocation_data", flush=True)
            self._persist_markdown_data(workflow, pricing_result)
            print(f"[PERSIST] Called _persist_markdown_data", flush=True)

            # Mark workflow as complete
            workflow.status = WorkflowStatus.completed
            workflow.progress_pct = 100
            workflow.completed_at = datetime.utcnow()
            workflow.current_agent = None
            workflow.output_data = final_results

            # Extract forecast_id from demand agent result
            workflow.forecast_id = final_results.get("demand", {}).get("forecast_id")

            self.db.commit()

            logger.info(f"[ORCHESTRATOR] Workflow execution completed: {workflow_id}")

            return final_results

        except asyncio.TimeoutError as e:
            error_msg = str(e)  # Includes enhanced message from AgentHandoffManager
            logger.error(
                f"[ORCHESTRATOR] Workflow timed out: {workflow_id}",
                extra={"workflow_id": workflow_id, "error_message": error_msg}
            )

            # Update workflow status with retry
            try:
                workflow.status = WorkflowStatus.failed
                workflow.error_message = error_msg
                workflow.completed_at = datetime.utcnow()
                self.db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update workflow status after timeout: {db_error}")
                # Try one more time with fresh session
                try:
                    self.db.rollback()
                    workflow = self.db.query(Workflow).filter_by(workflow_id=workflow_id).first()
                    if workflow:
                        workflow.status = WorkflowStatus.failed
                        workflow.error_message = error_msg
                        workflow.completed_at = datetime.utcnow()
                        self.db.commit()
                except:
                    logger.critical(f"Cannot update workflow status - database issue", exc_info=True)

            raise

        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"[ORCHESTRATOR] Workflow execution failed: {workflow_id}",
                exc_info=True,
                extra={
                    "workflow_id": workflow_id,
                    "error_type": type(e).__name__,
                    "error_message": error_msg
                }
            )

            # Update workflow status with retry (same pattern)
            try:
                workflow.status = WorkflowStatus.failed
                workflow.error_message = error_msg
                workflow.completed_at = datetime.utcnow()
                self.db.commit()
            except Exception as db_error:
                logger.error(f"Failed to update workflow status: {db_error}")
                try:
                    self.db.rollback()
                    workflow = self.db.query(Workflow).filter_by(workflow_id=workflow_id).first()
                    if workflow:
                        workflow.status = WorkflowStatus.failed
                        workflow.error_message = error_msg
                        workflow.completed_at = datetime.utcnow()
                        self.db.commit()
                except:
                    logger.critical(f"Cannot update workflow status - database issue", exc_info=True)

            raise

    def _register_agents(self, workflow: Workflow):
        """Register mock agents with the handoff manager."""

        # Create closures that capture workflow context
        async def demand_agent_handler(context):
            return await self._run_mock_demand_agent(workflow)

        async def inventory_agent_handler(demand_result):
            return await self._run_mock_inventory_agent(workflow, demand_result)

        async def pricing_agent_handler(inventory_result):
            # Extract demand result from inventory result context
            demand_result = {"total_forecast": inventory_result.get("total_units", 8000)}
            return await self._run_mock_pricing_agent(workflow, demand_result, inventory_result)

        self.handoff_manager.register_agent("demand", demand_agent_handler)
        self.handoff_manager.register_agent("inventory", inventory_agent_handler)
        self.handoff_manager.register_agent("pricing", pricing_agent_handler)

    async def _run_agent_with_tracking(
        self,
        agent_key: str,
        context: Any,
        workflow: Workflow,
        agent_name: str,
        progress_start: int,
        progress_end: int
    ) -> Dict[str, Any]:
        """
        Run agent and update workflow progress in database.

        Args:
            agent_key: Agent identifier for handoff manager (demand, inventory, pricing)
            context: Input context for agent
            workflow: Workflow database model
            agent_name: Display name for current_agent field (e.g., "Demand Agent")
            progress_start: Starting progress percentage
            progress_end: Ending progress percentage

        Returns:
            Agent result
        """
        # Update progress before agent runs
        workflow.current_agent = agent_name
        workflow.progress_pct = progress_start
        self.db.commit()

        # Execute agent using handoff manager (with timeout)
        result = await self.handoff_manager.call_agent(
            agent_key,
            context,
            timeout=300  # 5 minute timeout per agent
        )

        # Update progress after agent completes
        workflow.progress_pct = progress_end
        self.db.commit()

        return result

    async def _run_mock_demand_agent(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Mock Demand Agent - Returns hard-coded forecast data.

        Args:
            workflow: Workflow database model

        Returns:
            Mock demand forecast results
        """
        logger.info("[MOCK] Demand Agent: Generating forecast...")

        # Get parameters from workflow
        forecast_horizon = workflow.forecast_horizon_weeks or 12
        replenishment_strategy = workflow.replenishment_strategy or "none"

        # Adjust safety stock based on replenishment strategy
        if replenishment_strategy == "none":
            safety_stock_multiplier = 1.25
        elif replenishment_strategy == "weekly":
            safety_stock_multiplier = 1.20
        else:  # biweekly
            safety_stock_multiplier = 1.22

        # Generate mock weekly curve (bell curve pattern)
        weekly_curve = [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480]

        # Trim to forecast horizon
        weekly_curve = weekly_curve[:forecast_horizon]

        # Calculate total
        total_forecast = sum(weekly_curve)

        return {
            "agent": "demand",
            "forecast_id": f"f_{workflow.workflow_id}",
            "category_id": workflow.category_id,
            "total_forecast": total_forecast,
            "safety_stock_multiplier": safety_stock_multiplier,
            "weekly_curve": weekly_curve,
            "clusters": [
                {
                    "cluster_id": "Fashion_Forward",
                    "store_count": 20,
                    "allocation_pct": 40,
                    "units": int(total_forecast * 0.40),
                    "characteristics": {
                        "location_tier": "Urban Premium",
                        "median_income_range": "$125k+",
                        "store_size_range": "20,000+ sqft"
                    }
                },
                {
                    "cluster_id": "Mainstream",
                    "store_count": 20,
                    "allocation_pct": 40,
                    "units": int(total_forecast * 0.40),
                    "characteristics": {
                        "location_tier": "Suburban Standard",
                        "median_income_range": "$75k-$110k",
                        "store_size_range": "15,000-20,000 sqft"
                    }
                },
                {
                    "cluster_id": "Value_Conscious",
                    "store_count": 10,
                    "allocation_pct": 20,
                    "units": int(total_forecast * 0.20),
                    "characteristics": {
                        "location_tier": "Rural/Outlet",
                        "median_income_range": "<$75k",
                        "store_size_range": "<15,000 sqft"
                    }
                }
            ],
            "message": "Mock forecast generated for Phase 4 testing"
        }

    async def _run_mock_inventory_agent(
        self,
        workflow: Workflow,
        demand_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mock Inventory Agent - Returns hard-coded replenishment orders.

        Args:
            workflow: Workflow database model
            demand_result: Results from Demand Agent

        Returns:
            Mock inventory/replenishment results
        """
        logger.info("[MOCK] Inventory Agent: Calculating replenishment...")

        total_forecast = demand_result["total_forecast"]
        dc_holdback_pct = workflow.dc_holdback_percentage or 0.0
        dc_holdback_units = int(total_forecast * dc_holdback_pct)

        # Calculate manufacturing orders (mock logic)
        order_1_units = int(total_forecast * 0.40)
        order_2_units = int(total_forecast * 0.35)
        order_3_units = total_forecast - order_1_units - order_2_units - dc_holdback_units

        return {
            "agent": "inventory",
            "manufacturing_orders": [
                {
                    "order_id": "MO_001",
                    "week_range": "1-4",
                    "quantity": order_1_units,
                    "type": "Initial Order",
                    "delivery_week": 1,
                    "status": "Scheduled"
                },
                {
                    "order_id": "MO_002",
                    "week_range": "5-8",
                    "quantity": order_2_units,
                    "type": "Replenishment",
                    "delivery_week": 5,
                    "status": "Scheduled"
                },
                {
                    "order_id": "MO_003",
                    "week_range": "9-12",
                    "quantity": order_3_units,
                    "type": "Final Replenishment",
                    "delivery_week": 9,
                    "status": "Scheduled"
                }
            ],
            "dc_holdback": {
                "units": dc_holdback_units,
                "percentage": dc_holdback_pct,
                "purpose": "Emergency stock for high performers",
                "release_strategy": "As needed weeks 8-12"
            },
            "total_units": total_forecast,
            "message": "Mock replenishment plan generated for Phase 4 testing"
        }

    async def _run_mock_pricing_agent(
        self,
        workflow: Workflow,
        demand_result: Dict[str, Any],
        inventory_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mock Pricing Agent - Returns hard-coded markdown strategy.

        Args:
            workflow: Workflow database model
            demand_result: Results from Demand Agent
            inventory_result: Results from Inventory Agent

        Returns:
            Mock pricing/markdown results
        """
        logger.info("[MOCK] Pricing Agent: Optimizing markdown strategy...")

        total_forecast = demand_result["total_forecast"]

        return {
            "agent": "pricing",
            "markdown_strategy": [
                {
                    "week_range": "1-8",
                    "markdown_pct": 0,
                    "label": "Full Price",
                    "rationale": "High demand phase",
                    "expected_sales_units": int(total_forecast * 0.70),
                    "expected_revenue": int(total_forecast * 0.70 * 30)  # $30 avg price
                },
                {
                    "week_range": "9-10",
                    "markdown_pct": 15,
                    "label": "15% markdown",
                    "rationale": "Accelerate velocity",
                    "expected_sales_units": int(total_forecast * 0.175),
                    "expected_revenue": int(total_forecast * 0.175 * 30 * 0.85)
                },
                {
                    "week_range": "11-12",
                    "markdown_pct": 30,
                    "label": "30% markdown",
                    "rationale": "Clear inventory",
                    "expected_sales_units": int(total_forecast * 0.125),
                    "expected_revenue": int(total_forecast * 0.125 * 30 * 0.70)
                }
            ],
            "summary": {
                "expected_sellthrough_pct": 95,
                "expected_revenue": 240000,
                "average_discount_pct": 8,
                "final_inventory_units": int(total_forecast * 0.05)
            },
            "message": "Mock markdown strategy generated for Phase 4 testing"
        }

    def _persist_forecast_data(self, workflow: Workflow, demand_result: Dict[str, Any]):
        """Save forecast data to database."""
        logger.info(f"[PERSIST] Starting forecast persistence for workflow {workflow.workflow_id}")
        forecast_id = demand_result.get("forecast_id")
        logger.info(f"[PERSIST] Forecast ID: {forecast_id}")

        # Check if forecast already exists
        existing = self.db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()
        if existing:
            logger.info(f"Forecast {forecast_id} already exists, skipping")
            return

        # Build weekly_demand_curve in the expected format
        weekly_curve = demand_result.get("weekly_curve", [])
        weekly_demand_curve = [
            {"week_number": i+1, "demand_units": units}
            for i, units in enumerate(weekly_curve)
        ]

        forecast = Forecast(
            forecast_id=forecast_id,
            category_id=workflow.category_id,
            season="Spring 2025",  # Mock data
            forecast_horizon_weeks=workflow.forecast_horizon_weeks or 12,
            total_season_demand=demand_result.get("total_forecast", 0),
            weekly_demand_curve=weekly_demand_curve,
            peak_week=4,  # Mock data
            forecasting_method="ensemble_prophet_arima",
            models_used=["prophet", "arima"],
            prophet_forecast=demand_result.get("total_forecast", 0),
            arima_forecast=demand_result.get("total_forecast", 0)
        )

        self.db.add(forecast)
        self.db.flush()
        logger.info(f"Persisted forecast {forecast_id} to database")

    def _persist_allocation_data(self, workflow: Workflow, demand_result: Dict[str, Any], inventory_result: Dict[str, Any]):
        """Save allocation data to database."""
        logger.info(f"[PERSIST] Starting allocation persistence for workflow {workflow.workflow_id}")
        forecast_id = demand_result.get("forecast_id")
        allocation_id = f"a_{workflow.workflow_id}"
        logger.info(f"[PERSIST] Allocation ID: {allocation_id}, Forecast ID: {forecast_id}")

        # Check if allocation already exists
        existing = self.db.query(Allocation).filter(Allocation.allocation_id == allocation_id).first()
        if existing:
            logger.info(f"Allocation {allocation_id} already exists, skipping")
            return

        total_units = inventory_result.get("total_units", 0)
        dc_holdback = inventory_result.get("dc_holdback", {})

        allocation = Allocation(
            allocation_id=allocation_id,
            forecast_id=forecast_id,
            manufacturing_qty=total_units,
            safety_stock_percentage=0.20,  # Mock data
            initial_allocation_total=total_units - dc_holdback.get("units", 0),
            holdback_total=dc_holdback.get("units", 0),
            store_allocations=[]  # Will be populated later
        )

        self.db.add(allocation)
        self.db.flush()
        logger.info(f"Persisted allocation {allocation_id} to database")

    def _persist_markdown_data(self, workflow: Workflow, pricing_result: Dict[str, Any]):
        """Save markdown data to database."""
        logger.info(f"[PERSIST] Starting markdown persistence for workflow {workflow.workflow_id}")
        forecast_id = f"f_{workflow.workflow_id}"
        markdown_id = f"m_{workflow.workflow_id}"
        logger.info(f"[PERSIST] Markdown ID: {markdown_id}, Forecast ID: {forecast_id}")

        # Check if markdown already exists
        existing = self.db.query(Markdown).filter(Markdown.markdown_id == markdown_id).first()
        if existing:
            logger.info(f"Markdown {markdown_id} already exists, skipping")
            return

        summary = pricing_result.get("summary", {})

        # Calculate fields for markdown record
        target_sell_through_pct = 0.60  # Target 60% sell-through
        sell_through_pct = summary.get("expected_sellthrough_pct", 95) / 100.0  # Convert % to decimal
        gap_pct = target_sell_through_pct - sell_through_pct  # Gap between target and actual

        markdown = Markdown(
            markdown_id=markdown_id,
            forecast_id=forecast_id,
            week_number=workflow.markdown_checkpoint_week or 6,
            sell_through_pct=sell_through_pct,
            target_sell_through_pct=target_sell_through_pct,
            gap_pct=gap_pct,
            recommended_markdown_pct=0.10,  # Mock data
            elasticity_coefficient=2.0,
            expected_demand_lift_pct=0.10 * 1.5,  # markdown_pct * elasticity factor
            reasoning="Mock markdown strategy",
            status="pending"
        )

        self.db.add(markdown)
        self.db.flush()
        logger.info(f"Persisted markdown {markdown_id} to database")
