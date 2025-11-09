"""Mock Orchestrator Service for Phase 4 - Runs mock agents and generates fake data."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Workflow, WorkflowStatus

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

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute mock agent workflow.

        Args:
            workflow_id: Workflow ID to execute

        Returns:
            Mock workflow results
        """
        logger.info(f"[MOCK] Starting mock workflow execution: {workflow_id}")

        # Get workflow from database
        workflow = self.db.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Update status to running
        workflow.status = WorkflowStatus.running
        workflow.started_at = datetime.utcnow()
        workflow.current_agent = "Demand Agent"
        workflow.progress_pct = 0
        self.db.commit()

        try:
            # Step 1: Run Demand Agent (mock)
            logger.info(f"[MOCK] Running Demand Agent...")
            workflow.current_agent = "Demand Agent"
            workflow.progress_pct = 10
            self.db.commit()

            demand_result = await self._run_mock_demand_agent(workflow)
            await asyncio.sleep(1.5)  # Simulate processing time

            workflow.progress_pct = 40
            self.db.commit()

            # Step 2: Run Inventory Agent (mock)
            logger.info(f"[MOCK] Running Inventory Agent...")
            workflow.current_agent = "Inventory Agent"
            workflow.progress_pct = 50
            self.db.commit()
            inventory_result = await self._run_mock_inventory_agent(workflow, demand_result)
            await asyncio.sleep(1.2)  # Simulate processing time

            workflow.progress_pct = 70
            self.db.commit()

            # Step 3: Run Pricing Agent (mock)
            logger.info(f"[MOCK] Running Pricing Agent...")
            workflow.current_agent = "Pricing Agent"
            workflow.progress_pct = 75
            self.db.commit()
            pricing_result = await self._run_mock_pricing_agent(workflow, demand_result, inventory_result)
            await asyncio.sleep(1.0)  # Simulate processing time

            workflow.progress_pct = 95
            self.db.commit()

            # Combine results
            final_results = {
                "demand": demand_result,
                "inventory": inventory_result,
                "pricing": pricing_result
            }

            # Mark workflow as complete
            workflow.status = WorkflowStatus.completed
            workflow.progress_pct = 100
            workflow.completed_at = datetime.utcnow()
            workflow.current_agent = None
            workflow.output_data = final_results
            self.db.commit()

            logger.info(f"[MOCK] Mock workflow execution completed: {workflow_id}")

            return final_results

        except Exception as e:
            logger.error(f"[MOCK] Mock workflow execution failed: {e}", exc_info=True)
            workflow.status = WorkflowStatus.failed
            workflow.error_message = str(e)
            workflow.completed_at = datetime.utcnow()
            self.db.commit()
            raise

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
