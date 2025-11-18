"""Orchestrator Agent for coordinating specialist agents."""

from typing import Any, Dict
from app.agents.config import AgentConfig
from app.schemas.workflow_schemas import SeasonParameters
import logging

logger = logging.getLogger("fashion_forecast")


class OrchestratorAgent:
    """
    Orchestrator Agent coordinates specialist agents (Demand, Inventory, Pricing).

    Responsibilities:
    - Accept SeasonParameters from WorkflowService
    - Route to Demand Agent -> Inventory Agent -> Pricing Agent
    - Manage handoffs between agents
    - Return consolidated results to WorkflowService

    Phase 8 Implementation: Will use OpenAI Agents SDK with handoff configuration
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Orchestrator Agent.

        Args:
            config: Agent configuration with OpenAI client
        """
        self.config = config
        self.client = config.openai_client
        logger.info(" Orchestrator Agent initialized")

    async def run_forecast_workflow(
        self,
        category_id: str,
        parameters: SeasonParameters,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Execute pre-season forecast workflow.

        Workflow sequence:
        1. Hand off to Demand Agent -> forecast + clustering + allocation
        2. Hand off to Inventory Agent -> manufacturing + allocation + replenishment
        3. Hand off to Pricing Agent -> markdown calculation (if applicable)

        Args:
            category_id: Category identifier
            parameters: Season parameters
            workflow_id: Workflow session ID

        Returns:
            Consolidated workflow results with forecast_id, allocation_id, markdown_id
        """
        logger.info(f"[{workflow_id}] Orchestrator starting forecast workflow for {category_id}")

        # TODO (Phase 8): Implement OpenAI Agents SDK orchestration
        # 1. Configure handoffs: orchestrator � demand � inventory � pricing
        # 2. Execute session.run() with handoff context
        # 3. Stream progress updates to WebSocket
        # 4. Return consolidated results

        # Placeholder implementation
        return {
            "forecast_id": f"f_{category_id}_{workflow_id[:8]}",
            "allocation_id": f"a_{category_id}_{workflow_id[:8]}",
            "markdown_id": None,
            "total_season_demand": 0,
            "manufacturing_qty": 0,
            "workflow_duration_seconds": 0,
            "message": "Orchestrator agent placeholder - Phase 8 implementation pending"
        }

    async def run_reforecast_workflow(
        self,
        forecast_id: str,
        actual_sales: int,
        forecasted_sales: int,
        remaining_weeks: int,
        variance_pct: float,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Execute re-forecast workflow (variance-triggered or manual).

        Workflow sequence:
        1. Enable re-forecast handoff dynamically
        2. Hand off to Demand Agent with actuals context
        3. Hand off to Inventory Agent for updated allocation
        4. Hand off to Pricing Agent for updated markdown

        Args:
            forecast_id: Original forecast ID
            actual_sales: Actual sales through week N
            forecasted_sales: Original forecast through week N
            remaining_weeks: Weeks remaining in season
            variance_pct: Variance percentage
            workflow_id: Workflow session ID

        Returns:
            Consolidated re-forecast results
        """
        logger.info(
            f"[{workflow_id}] Orchestrator starting re-forecast for {forecast_id} "
            f"(variance: {variance_pct:.1%})"
        )

        # TODO (Phase 8): Implement dynamic handoff for re-forecast
        # 1. Enable re-forecast handoff: orchestrator.enable_handoff("reforecast")
        # 2. Pass actuals context to Demand Agent
        # 3. Execute re-allocation and re-markdown
        # 4. Return updated results

        # Placeholder implementation
        return {
            "forecast_id": forecast_id,
            "allocation_id": f"a_reforecast_{workflow_id[:8]}",
            "markdown_id": f"m_reforecast_{workflow_id[:8]}",
            "updated_season_demand": 0,
            "updated_manufacturing_qty": 0,
            "workflow_duration_seconds": 0,
            "message": "Re-forecast orchestrator placeholder - Phase 8 implementation pending"
        }

    def get_instructions(self) -> str:
        """
        Get agent instructions (system prompt).

        Returns:
            Orchestrator agent instructions
        """
        return """
You are the Orchestrator Agent for a fashion retail forecasting system.

Your responsibilities:
1. Accept season parameters from the WorkflowService
2. Coordinate three specialist agents in sequence:
   - Demand Agent: Forecasts demand, clusters stores, allocates units
   - Inventory Agent: Determines manufacturing qty, allocates to DC/stores, manages replenishment
   - Pricing Agent: Calculates markdown strategies if needed

3. Manage handoffs between agents:
   - Pass Demand Agent output to Inventory Agent
   - Pass Inventory Agent output to Pricing Agent
   - Return consolidated results to WorkflowService

4. Handle two workflow types:
   - Pre-season forecast: Full workflow (Demand -> Inventory -> Pricing)
   - Re-forecast: Dynamic handoff triggered by variance (20%+ deviation)

5. Stream progress updates:
   - Current agent name
   - Progress percentage (0-100)
   - Status messages

Rules:
- Follow the exact sequence: Demand -> Inventory -> Pricing
- Do not skip agents unless explicitly allowed (e.g., no markdown if not applicable)
- Validate outputs between handoffs
- Handle errors gracefully and report failures
- Update workflow status in database after each agent completes
""".strip()
