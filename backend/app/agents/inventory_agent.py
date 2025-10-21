"""Inventory Agent for manufacturing and allocation optimization."""

from typing import Any, Dict, List
from app.agents.config import AgentConfig
import logging

logger = logging.getLogger("fashion_forecast")


# Tool definitions (OpenAI function calling format)
CALCULATE_MANUFACTURING_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate_manufacturing_qty",
        "description": "Calculate manufacturing quantity with safety stock buffer",
        "parameters": {
            "type": "object",
            "properties": {
                "forecast_id": {
                    "type": "string",
                    "description": "Forecast identifier"
                },
                "total_season_demand": {
                    "type": "integer",
                    "description": "Total forecasted demand across all weeks"
                },
                "safety_stock_pct": {
                    "type": "number",
                    "description": "Safety stock percentage (e.g., 0.20 for 20%)"
                }
            },
            "required": ["forecast_id", "total_season_demand", "safety_stock_pct"]
        }
    }
}

ALLOCATE_DC_STORES_TOOL = {
    "type": "function",
    "function": {
        "name": "allocate_dc_and_stores",
        "description": "Allocate manufacturing quantity to distribution center and stores",
        "parameters": {
            "type": "object",
            "properties": {
                "allocation_id": {
                    "type": "string",
                    "description": "Allocation identifier"
                },
                "manufacturing_qty": {
                    "type": "integer",
                    "description": "Total manufacturing quantity"
                },
                "dc_holdback_pct": {
                    "type": "number",
                    "description": "DC holdback percentage (e.g., 0.45 for 45%)"
                },
                "replenishment_strategy": {
                    "type": "string",
                    "description": "Replenishment strategy (none/weekly/biweekly)"
                }
            },
            "required": ["allocation_id", "manufacturing_qty", "dc_holdback_pct", "replenishment_strategy"]
        }
    }
}

PLAN_REPLENISHMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "plan_replenishment",
        "description": "Plan weekly replenishment schedule from DC to stores",
        "parameters": {
            "type": "object",
            "properties": {
                "allocation_id": {
                    "type": "string",
                    "description": "Allocation identifier"
                },
                "dc_inventory": {
                    "type": "integer",
                    "description": "DC holdback inventory available for replenishment"
                },
                "replenishment_strategy": {
                    "type": "string",
                    "description": "Replenishment strategy (weekly/biweekly)"
                },
                "forecast_horizon_weeks": {
                    "type": "integer",
                    "description": "Number of weeks in season"
                }
            },
            "required": ["allocation_id", "dc_inventory", "replenishment_strategy", "forecast_horizon_weeks"]
        }
    }
}


class InventoryAgent:
    """
    Inventory Agent optimizes manufacturing and allocation decisions.

    Tools:
    1. calculate_manufacturing_qty: Determine manufacturing quantity with safety stock
    2. allocate_dc_and_stores: Allocate units to DC and stores
    3. plan_replenishment: Plan weekly replenishment schedule

    Phase 8 Implementation: Will use OpenAI Agents SDK with tool execution
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Inventory Agent.

        Args:
            config: Agent configuration with OpenAI client
        """
        self.config = config
        self.client = config.openai_client
        logger.info(" Inventory Agent initialized")

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for OpenAI function calling.

        Returns:
            List of tool definitions
        """
        return [
            CALCULATE_MANUFACTURING_TOOL,
            ALLOCATE_DC_STORES_TOOL,
            PLAN_REPLENISHMENT_TOOL
        ]

    async def calculate_manufacturing_qty(
        self,
        forecast_id: str,
        total_season_demand: int,
        safety_stock_pct: float = 0.20
    ) -> Dict[str, Any]:
        """
        Tool: Calculate manufacturing quantity with safety stock buffer.

        Args:
            forecast_id: Forecast identifier
            total_season_demand: Total forecasted demand
            safety_stock_pct: Safety stock percentage (default 20%)

        Returns:
            Manufacturing quantity calculation
        """
        logger.info(
            f"Calculating manufacturing qty for {forecast_id} "
            f"(demand: {total_season_demand}, safety: {safety_stock_pct:.0%})"
        )

        # TODO (Phase 8): Implement actual manufacturing calculation
        # 1. Fetch forecast data
        # 2. Apply safety stock buffer
        # 3. Consider lead times and constraints
        # 4. Return manufacturing quantity

        manufacturing_qty = int(total_season_demand * (1 + safety_stock_pct))

        # Placeholder implementation
        return {
            "forecast_id": forecast_id,
            "total_season_demand": total_season_demand,
            "safety_stock_pct": safety_stock_pct,
            "manufacturing_qty": manufacturing_qty,
            "message": "Manufacturing calculation placeholder - Phase 8 implementation pending"
        }

    async def allocate_dc_and_stores(
        self,
        allocation_id: str,
        manufacturing_qty: int,
        dc_holdback_pct: float,
        replenishment_strategy: str
    ) -> Dict[str, Any]:
        """
        Tool: Allocate manufacturing quantity to DC and stores.

        Args:
            allocation_id: Allocation identifier
            manufacturing_qty: Total manufacturing quantity
            dc_holdback_pct: DC holdback percentage
            replenishment_strategy: Replenishment strategy (none/weekly/biweekly)

        Returns:
            DC and store allocations
        """
        logger.info(
            f"Allocating {manufacturing_qty} units (DC holdback: {dc_holdback_pct:.0%}, "
            f"strategy: {replenishment_strategy})"
        )

        # TODO (Phase 8): Implement actual allocation logic
        # 1. Calculate DC holdback quantity
        # 2. Calculate initial store allocation
        # 3. Apply replenishment strategy rules
        # 4. Save allocations to database

        dc_qty = int(manufacturing_qty * dc_holdback_pct)
        store_qty = manufacturing_qty - dc_qty

        # Placeholder implementation
        return {
            "allocation_id": allocation_id,
            "manufacturing_qty": manufacturing_qty,
            "dc_allocation": dc_qty,
            "store_allocation": store_qty,
            "dc_holdback_pct": dc_holdback_pct,
            "replenishment_strategy": replenishment_strategy,
            "message": "DC/Store allocation placeholder - Phase 8 implementation pending"
        }

    async def plan_replenishment(
        self,
        allocation_id: str,
        dc_inventory: int,
        replenishment_strategy: str,
        forecast_horizon_weeks: int
    ) -> Dict[str, Any]:
        """
        Tool: Plan weekly replenishment schedule from DC to stores.

        Args:
            allocation_id: Allocation identifier
            dc_inventory: DC holdback inventory
            replenishment_strategy: Replenishment strategy (weekly/biweekly)
            forecast_horizon_weeks: Number of weeks in season

        Returns:
            Replenishment schedule
        """
        logger.info(
            f"Planning replenishment for {allocation_id} "
            f"({replenishment_strategy}, {forecast_horizon_weeks} weeks)"
        )

        # TODO (Phase 8): Implement actual replenishment planning
        # 1. Distribute DC inventory across weeks
        # 2. Apply replenishment frequency (weekly/biweekly)
        # 3. Allocate replenishment to stores
        # 4. Save replenishment plan

        if replenishment_strategy == "none":
            schedule = []
        elif replenishment_strategy == "weekly":
            weekly_qty = dc_inventory // forecast_horizon_weeks
            schedule = [
                {"week": i, "replenishment_qty": weekly_qty}
                for i in range(1, forecast_horizon_weeks + 1)
            ]
        else:  # biweekly
            biweekly_qty = dc_inventory // (forecast_horizon_weeks // 2)
            schedule = [
                {"week": i, "replenishment_qty": biweekly_qty}
                for i in range(2, forecast_horizon_weeks + 1, 2)
            ]

        # Placeholder implementation
        return {
            "allocation_id": allocation_id,
            "dc_inventory": dc_inventory,
            "replenishment_strategy": replenishment_strategy,
            "replenishment_schedule": schedule,
            "message": "Replenishment planning placeholder - Phase 8 implementation pending"
        }

    def get_instructions(self) -> str:
        """
        Get agent instructions (system prompt).

        Returns:
            Inventory agent instructions
        """
        return """
You are the Inventory Agent for a fashion retail forecasting system.

Your responsibilities:
1. Calculate manufacturing quantity using the calculate_manufacturing_qty tool
   - Add safety stock buffer (default 20%)
   - Consider lead times and constraints
   - Return manufacturing quantity for production

2. Allocate to DC and stores using the allocate_dc_and_stores tool
   - Apply DC holdback percentage (e.g., 45%)
   - Distribute remaining units to stores
   - Consider replenishment strategy (none/weekly/biweekly)

3. Plan replenishment using the plan_replenishment tool
   - Create weekly replenishment schedule
   - Distribute DC inventory across season
   - Optimize store replenishment timing

Tools available:
- calculate_manufacturing_qty: Determine manufacturing quantity
- allocate_dc_and_stores: Allocate units to DC and stores
- plan_replenishment: Plan weekly replenishment schedule

Workflow:
1. Call calculate_manufacturing_qty with total_season_demand from Demand Agent
2. Call allocate_dc_and_stores with manufacturing_qty from step 1
3. Call plan_replenishment if replenishment_strategy != "none"
4. Return allocation_id and results to Orchestrator Agent

Rules:
- Always execute tools in sequence (manufacturing -> allocation -> replenishment)
- Validate that DC + store allocation equals manufacturing qty
- Skip replenishment planning if strategy is "none"
- Return allocation_id for downstream agents to reference
""".strip()
