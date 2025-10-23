# Story: OpenAI Agents SDK Integration - Agent Scaffolding with Handoff Configuration

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-009
**Status:** Ready for Review
**Estimate:** 4 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-004 (FastAPI Setup), PHASE3-005 (Parameter Extraction), PHASE3-007 (Workflow Orchestration)

---

## Story

As a backend developer,
I want to scaffold all 4 agents (Orchestrator, Demand, Inventory, Pricing) using OpenAI Agents SDK with handoff configuration,
So that Phase 8 (Orchestrator Agent) can integrate seamlessly with the existing infrastructure without major refactoring.

**Business Value:** This scaffolding establishes the **multi-agent architecture foundation**. While actual LLM logic is implemented in Phases 5-8, this story creates the agent structure, handoff configuration, and parameter-passing interfaces. This ensures the architecture is correct from the start, preventing costly refactoring later.

**Epic Context:** This is Task 9 of 14 in Phase 3. It builds on parameter extraction (PHASE3-005) and workflow orchestration (PHASE3-007) to create the agent coordination layer. The scaffolding includes placeholder tools and prompts that will be replaced with full implementations in Phases 5-8.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ Orchestrator agent created with handoff configuration to all 3 specialist agents
2. ✅ Demand agent scaffold with placeholder tools (forecast, clustering, allocation)
3. ✅ Inventory agent scaffold with placeholder tools (manufacturing, allocation, replenishment)
4. ✅ Pricing agent scaffold with placeholder tools (markdown calculation)
5. ✅ Agent handoffs pass `SeasonParameters` in context
6. ✅ LLM reasoning prompts explain how parameters affect agent decisions
7. ✅ Dynamic re-forecast handoff configuration (enabled/disabled at runtime)
8. ✅ Agent tool schemas use Pydantic for validation

### Quality Requirements

9. ✅ All agents use gpt-4o-mini model (Standard OpenAI)
10. ✅ Agent instructions are clear and parameter-aware
11. ✅ Tool output validation with guardrails
12. ✅ Logging shows agent handoff events
13. ✅ Agent factory pattern for dependency injection

---

## Tasks

### Task 1: Create Agent Base Configuration

Create shared configuration and utilities for all agents.

**File:** `backend/app/agents/config.py`

```python
from pydantic_settings import BaseSettings
from pydantic import Field


class AgentConfig(BaseSettings):
    """Configuration for OpenAI Agents SDK."""

    # Standard OpenAI settings (loaded from .env)
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")

    # Agent settings
    agent_model: str = "gpt-4o-mini"
    agent_temperature: float = 0.7
    agent_max_tokens: int = 4096

    class Config:
        env_file = ".env"


# Global agent configuration instance
agent_config = AgentConfig()
```

**Expected Output:**
- AgentConfig class with standard OpenAI settings
- Environment variable loading
- Global configuration instance

---

### Task 2: Create Orchestrator Agent

Create Orchestrator agent with handoff configuration.

**File:** `backend/app/agents/orchestrator.py`

```python
from openai import OpenAI
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrator agent coordinates 3 specialist agents based on SeasonParameters.

    Responsibilities:
    - Parse SeasonParameters from workflow request
    - Hand off to Demand Agent for forecasting
    - Hand off to Inventory Agent for allocation
    - Conditionally hand off to Pricing Agent (if markdown_checkpoint_week specified)
    - Monitor variance and dynamically enable re-forecast handoff
    - Coordinate human-in-the-loop approvals
    - Broadcast workflow status via WebSocket
    """

    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.name = "Orchestrator"
        self.model = "gpt-4o-mini"

        # Instructions for parameter-driven coordination
        self.instructions = """
        You are the Orchestrator agent for a parameter-driven retail forecasting system.

        Your role is to coordinate 3 specialist agents based on SeasonParameters:

        **Demand Agent:**
        - Always hand off for initial forecast (Prophet + ARIMA ensemble)
        - Hand off for re-forecast if variance exceeds 20%

        **Inventory Agent:**
        - Always hand off for manufacturing order and allocation
        - Conditionally execute replenishment phase:
          - If replenishment_strategy = "none": Skip replenishment entirely
          - If replenishment_strategy = "weekly" or "bi-weekly": Execute replenishment

        **Pricing Agent:**
        - Conditionally hand off:
          - If markdown_checkpoint_week is specified: Hand off at that week
          - If markdown_checkpoint_week is null: Skip pricing agent entirely

        **Parameter Awareness:**
        - dc_holdback_percentage = 0.0: Allocate 100% to stores at Week 0, skip DC holdback
        - dc_holdback_percentage = 0.45: Standard 55/45 split (55% stores, 45% DC)
        - replenishment_strategy = "none": No ongoing replenishment, one-shot allocation
        - markdown_checkpoint_week = 6: Trigger pricing analysis at Week 6

        **Variance Monitoring:**
        - After each weekly actuals upload, calculate variance
        - If variance > 20%: Enable re-forecast handoff, pass context to Demand Agent
        - If variance <= 20%: Continue with current forecast

        **Workflow Coordination:**
        1. Start: Receive SeasonParameters from workflow request
        2. Forecast: Hand off to Demand Agent
        3. Allocation: Hand off to Inventory Agent
        4. Approval: Trigger human-in-the-loop for manufacturing order
        5. Replenishment: Conditional phase (based on strategy)
        6. Markdown: Conditional phase (based on checkpoint week)
        7. Complete: Broadcast workflow_complete via WebSocket

        Always pass SeasonParameters in handoff context so specialist agents can reason about how parameters affect their decisions.
        """

    def create_agent_definition(self) -> Dict[str, Any]:
        """
        Create agent definition for OpenAI Agents SDK.

        Note: This is a placeholder for Phase 3. Full implementation in Phase 8.
        """
        return {
            "name": self.name,
            "instructions": self.instructions,
            "model": self.model,
            "handoffs": ["demand", "inventory", "pricing"],  # Agent names for handoff
            "tools": []  # Orchestrator has no direct tools (coordination only)
        }

    async def coordinate_forecast_workflow(
        self,
        workflow_id: str,
        season_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate full forecast workflow.

        Args:
            workflow_id: Workflow identifier
            season_parameters: Extracted parameters from natural language

        Returns:
            Workflow results

        Note: This is a placeholder. Phase 8 will implement actual agent execution.
        """
        logger.info(f"Orchestrator coordinating workflow {workflow_id}")
        logger.info(f"Parameters: {season_parameters}")

        # TODO (Phase 8): Implement actual agent coordination
        # from openai_agents import Session
        # session = Session()
        # result = session.run(orchestrator_agent, input={
        #     "action": "generate_forecast",
        #     "parameters": season_parameters
        # })

        # Placeholder: Return mock result
        return {
            "status": "completed",
            "forecast_id": "f_mock",
            "allocation_id": "a_mock",
            "message": "Orchestrator agent scaffolding complete. Actual implementation in Phase 8."
        }


def get_orchestrator_agent(openai_client: OpenAI) -> OrchestratorAgent:
    """Factory function for Orchestrator agent (dependency injection)."""
    return OrchestratorAgent(openai_client)
```

**Expected Output:**
- OrchestratorAgent class with parameter-aware instructions
- Handoff configuration to 3 specialist agents
- Placeholder coordination method
- Factory function for dependency injection

---

### Task 3: Create Demand Agent Scaffold

Create Demand agent with placeholder tools.

**File:** `backend/app/agents/demand.py`

```python
from openai import OpenAI
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DemandAgent:
    """
    Demand agent forecasts category demand and allocates to stores.

    Responsibilities:
    - Run ensemble forecasting (Prophet + ARIMA)
    - Cluster stores using K-means (K=3, 7 features)
    - Calculate store allocation factors (70% historical + 30% attributes)
    - Distribute forecast across clusters and stores
    - Reason about parameter impacts (e.g., no replenishment → increase safety stock)

    Tools:
    - forecast_category_demand: Run Prophet + ARIMA ensemble
    - cluster_stores: K-means clustering
    - calculate_store_allocations: Distribute forecast to stores
    """

    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.name = "Demand Agent"
        self.model = "gpt-4o-mini"

        self.instructions = """
        You are the Demand Agent responsible for category-level forecasting.

        **Core Tasks:**
        1. Run ensemble forecasting (Prophet + ARIMA, average results)
        2. Cluster stores using K-means (K=3)
        3. Calculate store allocation factors
        4. Distribute forecast across stores

        **Parameter Awareness - Autonomous Reasoning:**

        When replenishment_strategy = "none":
        - Recognize there is NO ongoing replenishment (one-shot allocation)
        - Increase safety stock from 20% to 25% to account for lack of buffer
        - Reasoning: "No replenishment configured → increasing safety stock to 25%"

        When replenishment_strategy = "weekly" or "bi-weekly":
        - Use standard 20% safety stock
        - Reasoning: "Ongoing replenishment provides buffer → 20% safety stock sufficient"

        When dc_holdback_percentage = 0.0:
        - Note that 100% will be allocated to stores at Week 0
        - Inventory Agent will skip DC holdback phase
        - Reasoning: "0% holdback → all inventory allocated to stores immediately"

        **Output Format:**
        Return forecast object with:
        - total_season_demand (integer)
        - prophet_forecast (integer)
        - arima_forecast (integer)
        - weekly_demand_curve (list of week-by-week demand)
        - cluster_distribution (list of cluster allocations)
        - safety_stock_reasoning (string explaining parameter impact)

        **Tools Available:**
        - forecast_category_demand(historical_sales_csv, weeks)
        - cluster_stores(stores_csv)
        - calculate_store_allocations(forecast, stores, clusters)
        """

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define tools for Demand Agent.

        Note: Actual ML implementations in Phase 5. These are placeholders.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "forecast_category_demand",
                    "description": "Run Prophet + ARIMA ensemble forecasting for category-level demand",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "historical_sales_csv": {
                                "type": "string",
                                "description": "Path to historical sales CSV file"
                            },
                            "weeks": {
                                "type": "integer",
                                "description": "Forecast horizon in weeks (from SeasonParameters.forecast_horizon_weeks)"
                            },
                            "safety_stock_adjustment": {
                                "type": "number",
                                "description": "Safety stock percentage (0.20 or 0.25 based on replenishment_strategy)"
                            }
                        },
                        "required": ["historical_sales_csv", "weeks", "safety_stock_adjustment"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cluster_stores",
                    "description": "Cluster stores using K-means (K=3) with 7 features",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stores_csv": {
                                "type": "string",
                                "description": "Path to store attributes CSV file"
                            }
                        },
                        "required": ["stores_csv"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_store_allocations",
                    "description": "Calculate store-level allocations using cluster factors",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "total_demand": {
                                "type": "integer",
                                "description": "Total season demand from forecast"
                            },
                            "clusters": {
                                "type": "array",
                                "description": "Cluster assignments from cluster_stores"
                            }
                        },
                        "required": ["total_demand", "clusters"]
                    }
                }
            }
        ]

    async def forecast_category_demand_placeholder(
        self,
        historical_sales_csv: str,
        weeks: int,
        safety_stock_adjustment: float
    ) -> Dict[str, Any]:
        """
        Placeholder tool: Forecast category demand.

        Phase 5 will implement actual Prophet + ARIMA.
        """
        logger.info(f"Demand Agent: Forecasting {weeks} weeks with safety stock {safety_stock_adjustment}")

        # Mock forecast result
        return {
            "total_season_demand": 8000,
            "prophet_forecast": 8200,
            "arima_forecast": 7800,
            "forecasting_method": "ensemble_prophet_arima",
            "safety_stock_pct": safety_stock_adjustment,
            "safety_stock_reasoning": f"Safety stock set to {safety_stock_adjustment:.0%} based on replenishment strategy"
        }

    async def cluster_stores_placeholder(self, stores_csv: str) -> List[Dict[str, Any]]:
        """
        Placeholder tool: K-means clustering.

        Phase 5 will implement actual K-means.
        """
        logger.info("Demand Agent: Clustering stores")

        # Mock cluster result
        return [
            {"cluster_id": "fashion_forward", "cluster_name": "Fashion Forward", "store_count": 20},
            {"cluster_id": "mainstream", "cluster_name": "Mainstream", "store_count": 18},
            {"cluster_id": "value_conscious", "cluster_name": "Value Conscious", "store_count": 12}
        ]


def get_demand_agent(openai_client: OpenAI) -> DemandAgent:
    """Factory function for Demand agent."""
    return DemandAgent(openai_client)
```

**Expected Output:**
- DemandAgent class with parameter-aware instructions
- 3 tool definitions (forecast, cluster, allocate)
- Placeholder tool implementations
- Autonomous reasoning prompts

---

### Task 4: Create Inventory Agent Scaffold

Create Inventory agent with placeholder tools.

**File:** `backend/app/agents/inventory.py`

```python
from openai import OpenAI
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class InventoryAgent:
    """
    Inventory agent calculates manufacturing orders and allocations.

    Responsibilities:
    - Calculate manufacturing order (forecast + parameter-driven safety stock)
    - Hierarchical allocation (parameter-driven: 100% or 55/45 split)
    - Conditional replenishment planning (skip if strategy = "none")
    - Reason about parameter impacts (e.g., 0% holdback → 100% allocation)

    Tools:
    - calculate_manufacturing_order: Compute total units to manufacture
    - allocate_initial_inventory: Distribute to stores (parameter-driven split)
    - plan_weekly_replenishment: Calculate replenishment needs (conditional)
    """

    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.name = "Inventory Agent"
        self.model = "gpt-4o-mini"

        self.instructions = """
        You are the Inventory Agent responsible for manufacturing and allocation.

        **Core Tasks:**
        1. Calculate manufacturing order quantity
        2. Allocate inventory hierarchically (parameter-driven)
        3. Plan weekly replenishment (conditional)

        **Parameter Awareness - Autonomous Reasoning:**

        When dc_holdback_percentage = 0.0 (Zara-style):
        - Allocate 100% of manufacturing to stores at Week 0
        - Skip DC holdback entirely
        - Skip replenishment phase (no DC inventory to draw from)
        - Reasoning: "0% DC holdback → 100% allocated to stores at Week 0, replenishment phase skipped"

        When dc_holdback_percentage = 0.45 (Standard):
        - Allocate 55% to stores at Week 0 (initial allocation)
        - Hold 45% at DC for weekly replenishment
        - Execute replenishment phase if replenishment_strategy != "none"
        - Reasoning: "45% DC holdback → 55% initial allocation, 45% reserved for replenishment"

        When replenishment_strategy = "none":
        - Skip weekly replenishment planning entirely
        - All inventory allocated at Week 0 (one-shot allocation)
        - Reasoning: "No replenishment strategy → all inventory allocated upfront"

        **Output Format:**
        Return allocation plan with:
        - manufacturing_qty (integer)
        - safety_stock_percentage (from Demand Agent)
        - initial_allocation_total (integer, parameter-driven)
        - holdback_total (integer, parameter-driven)
        - store_allocations (list of store-level allocations)
        - allocation_reasoning (string explaining parameter impact)

        **Tools Available:**
        - calculate_manufacturing_order(forecast_total, safety_stock_pct)
        - allocate_initial_inventory(manufacturing_qty, dc_holdback_pct)
        - plan_weekly_replenishment(current_inventory, forecast, replenishment_strategy)
        """

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define tools for Inventory Agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_manufacturing_order",
                    "description": "Calculate total units to manufacture (forecast + safety stock)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "forecast_total": {
                                "type": "integer",
                                "description": "Total season demand from Demand Agent"
                            },
                            "safety_stock_pct": {
                                "type": "number",
                                "description": "Safety stock percentage (0.20 or 0.25)"
                            }
                        },
                        "required": ["forecast_total", "safety_stock_pct"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "allocate_initial_inventory",
                    "description": "Allocate manufactured inventory to stores (parameter-driven split)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "manufacturing_qty": {
                                "type": "integer",
                                "description": "Total units manufactured"
                            },
                            "dc_holdback_pct": {
                                "type": "number",
                                "description": "DC holdback percentage from SeasonParameters"
                            },
                            "store_allocations": {
                                "type": "array",
                                "description": "Store allocation factors from Demand Agent"
                            }
                        },
                        "required": ["manufacturing_qty", "dc_holdback_pct", "store_allocations"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "plan_weekly_replenishment",
                    "description": "Plan weekly replenishment (conditional based on strategy)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "replenishment_strategy": {
                                "type": "string",
                                "description": "Replenishment strategy from SeasonParameters"
                            },
                            "dc_inventory_available": {
                                "type": "integer",
                                "description": "Units available at DC"
                            }
                        },
                        "required": ["replenishment_strategy", "dc_inventory_available"]
                    }
                }
            }
        ]

    async def calculate_manufacturing_order_placeholder(
        self,
        forecast_total: int,
        safety_stock_pct: float
    ) -> Dict[str, Any]:
        """Placeholder tool: Calculate manufacturing order."""
        logger.info(f"Inventory Agent: Calculating manufacturing order")

        manufacturing_qty = int(forecast_total * (1 + safety_stock_pct))

        return {
            "manufacturing_qty": manufacturing_qty,
            "safety_stock_pct": safety_stock_pct,
            "reasoning": f"Manufacturing order = {forecast_total} × (1 + {safety_stock_pct:.0%}) = {manufacturing_qty}"
        }


def get_inventory_agent(openai_client: OpenAI) -> InventoryAgent:
    """Factory function for Inventory agent."""
    return InventoryAgent(openai_client)
```

**Expected Output:**
- InventoryAgent class with parameter-aware instructions
- 3 tool definitions (manufacturing, allocation, replenishment)
- Placeholder tool implementations
- Conditional replenishment logic prompts

---

### Task 5: Create Pricing Agent Scaffold

Create Pricing agent with placeholder tools.

**File:** `backend/app/agents/pricing.py`

```python
from openai import OpenAI
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PricingAgent:
    """
    Pricing agent calculates markdown recommendations.

    Responsibilities:
    - Evaluate Week N checkpoint (markdown_checkpoint_week from parameters)
    - Calculate markdown using Gap × Elasticity formula
    - Reason about markdown timing and depth
    - Apply markdown uniformly across all stores

    Tools:
    - calculate_markdown_recommendation: Compute markdown depth based on sell-through
    """

    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.name = "Pricing Agent"
        self.model = "gpt-4o-mini"

        self.instructions = """
        You are the Pricing Agent responsible for markdown decisions.

        **Core Task:**
        Calculate markdown depth using Gap × Elasticity formula at markdown checkpoint week.

        **Parameter Awareness:**

        When markdown_checkpoint_week is specified (e.g., Week 6):
        - Trigger markdown analysis at that week
        - Calculate sell-through percentage
        - If sell-through < target (60%): Recommend markdown
        - If sell-through >= target: No markdown needed

        When markdown_checkpoint_week is null:
        - Skip pricing agent entirely (Orchestrator will not hand off)
        - No markdown analysis performed

        **Markdown Formula:**
        markdown_pct = (target_sell_through - actual_sell_through) × elasticity_coefficient

        Where:
        - target_sell_through = 0.60 (60% by Week 6)
        - elasticity_coefficient = 2.0 (tunable parameter)
        - markdown_pct capped at 40%
        - Round to nearest 5%

        **Output Format:**
        Return markdown recommendation with:
        - recommended_markdown_pct (float, 0.0 to 0.40)
        - gap_pct (float, target - actual)
        - elasticity_coefficient (float, default 2.0)
        - expected_demand_lift_pct (float, estimated sales increase)
        - reasoning (string explaining calculation)

        **Tools Available:**
        - calculate_markdown_recommendation(actual_sell_through_pct, target_sell_through_pct, elasticity_coefficient)
        """

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define tools for Pricing Agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_markdown_recommendation",
                    "description": "Calculate markdown percentage using Gap × Elasticity formula",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actual_sell_through_pct": {
                                "type": "number",
                                "description": "Actual sell-through percentage by checkpoint week (e.g., 0.50)"
                            },
                            "target_sell_through_pct": {
                                "type": "number",
                                "description": "Target sell-through percentage (default 0.60)"
                            },
                            "elasticity_coefficient": {
                                "type": "number",
                                "description": "Demand elasticity coefficient (default 2.0)"
                            }
                        },
                        "required": ["actual_sell_through_pct", "target_sell_through_pct", "elasticity_coefficient"]
                    }
                }
            }
        ]

    async def calculate_markdown_recommendation_placeholder(
        self,
        actual_sell_through_pct: float,
        target_sell_through_pct: float = 0.60,
        elasticity_coefficient: float = 2.0
    ) -> Dict[str, Any]:
        """Placeholder tool: Calculate markdown recommendation."""
        logger.info(f"Pricing Agent: Calculating markdown recommendation")

        gap = target_sell_through_pct - actual_sell_through_pct

        if gap <= 0:
            # On track or ahead of target
            return {
                "recommended_markdown_pct": 0.0,
                "gap_pct": gap,
                "reasoning": "On track or ahead of target, no markdown needed"
            }

        # Calculate markdown
        markdown_raw = gap * elasticity_coefficient
        markdown_capped = min(markdown_raw, 0.40)  # Cap at 40%
        markdown_rounded = round(markdown_capped * 20) / 20  # Round to nearest 5%

        return {
            "recommended_markdown_pct": markdown_rounded,
            "gap_pct": gap,
            "elasticity_coefficient": elasticity_coefficient,
            "expected_demand_lift_pct": markdown_rounded * 1.5,  # Assumes 1% markdown = 1.5% lift
            "reasoning": f"{gap*100:.1f}% gap × {elasticity_coefficient} elasticity = {markdown_rounded*100:.0f}% markdown"
        }


def get_pricing_agent(openai_client: OpenAI) -> PricingAgent:
    """Factory function for Pricing agent."""
    return PricingAgent(openai_client)
```

**Expected Output:**
- PricingAgent class with parameter-aware instructions
- 1 tool definition (calculate markdown)
- Placeholder tool implementation with Gap × Elasticity formula
- Conditional markdown logic prompts

---

### Task 6: Create Agent Factory

Create factory module to initialize all agents with dependency injection.

**File:** `backend/app/agents/factory.py`

```python
from openai import OpenAI
from .config import agent_config
from .orchestrator import get_orchestrator_agent, OrchestratorAgent
from .demand import get_demand_agent, DemandAgent
from .inventory import get_inventory_agent, InventoryAgent
from .pricing import get_pricing_agent, PricingAgent
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory for creating agent instances with dependency injection.

    Ensures all agents share the same OpenAI client instance.
    """

    def __init__(self):
        # Initialize standard OpenAI client
        self.openai_client = OpenAI(
            api_key=agent_config.openai_api_key
        )
        logger.info("Agent factory initialized with standard OpenAI client")

    def create_orchestrator(self) -> OrchestratorAgent:
        """Create Orchestrator agent instance."""
        return get_orchestrator_agent(self.openai_client)

    def create_demand_agent(self) -> DemandAgent:
        """Create Demand agent instance."""
        return get_demand_agent(self.openai_client)

    def create_inventory_agent(self) -> InventoryAgent:
        """Create Inventory agent instance."""
        return get_inventory_agent(self.openai_client)

    def create_pricing_agent(self) -> PricingAgent:
        """Create Pricing agent instance."""
        return get_pricing_agent(self.openai_client)

    def create_all_agents(self) -> dict:
        """Create all agents and return as dictionary."""
        return {
            "orchestrator": self.create_orchestrator(),
            "demand": self.create_demand_agent(),
            "inventory": self.create_inventory_agent(),
            "pricing": self.create_pricing_agent()
        }


# Global agent factory instance
agent_factory = AgentFactory()
```

**Expected Output:**
- AgentFactory class with dependency injection
- Shared standard OpenAI client instance
- Factory methods for each agent
- Global factory instance

---

### Task 7: Update Workflow Service to Use Agents

Integrate agent scaffolding into workflow service.

**File:** `backend/app/services/workflow_service.py` (modifications)

```python
# Add imports
from ..agents.factory import agent_factory
import logging

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing workflow orchestration."""

    def __init__(self, db: Session):
        self.db = db
        # Initialize agents
        self.agents = agent_factory.create_all_agents()
        logger.info("Workflow service initialized with agent scaffolding")

    def create_forecast_workflow(
        self,
        request: WorkflowCreateRequest,
        host: str = "localhost:8000"
    ) -> WorkflowResponse:
        """Create a new pre-season forecast workflow."""

        # ... (existing workflow creation code)

        # TODO (Phase 8): Execute orchestrator agent
        # result = await self.agents["orchestrator"].coordinate_forecast_workflow(
        #     workflow_id=workflow_id,
        #     season_parameters=request.parameters.model_dump()
        # )

        logger.info(f"Created forecast workflow {workflow_id} (agents ready for Phase 8)")

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="pending",
            websocket_url=websocket_url
        )
```

**Expected Output:**
- Workflow service imports agent factory
- Agents initialized on service creation
- Placeholder for Phase 8 agent execution
- Logging confirms agent readiness

---

### Task 8: Test Agent Scaffolding

Create pytest tests for agent scaffolding.

**File:** `backend/tests/test_agents.py`

```python
import pytest
from app.agents.factory import AgentFactory


def test_agent_factory_initialization():
    """Test agent factory creates all agents successfully."""

    factory = AgentFactory()
    agents = factory.create_all_agents()

    assert "orchestrator" in agents
    assert "demand" in agents
    assert "inventory" in agents
    assert "pricing" in agents

    assert agents["orchestrator"].name == "Orchestrator"
    assert agents["demand"].name == "Demand Agent"
    assert agents["inventory"].name == "Inventory Agent"
    assert agents["pricing"].name == "Pricing Agent"


def test_orchestrator_agent_instructions():
    """Test Orchestrator agent has parameter-aware instructions."""

    factory = AgentFactory()
    orchestrator = factory.create_orchestrator()

    assert "SeasonParameters" in orchestrator.instructions
    assert "replenishment_strategy" in orchestrator.instructions
    assert "dc_holdback_percentage" in orchestrator.instructions
    assert "markdown_checkpoint_week" in orchestrator.instructions


def test_demand_agent_tools():
    """Test Demand agent has 3 tools defined."""

    factory = AgentFactory()
    demand_agent = factory.create_demand_agent()

    tools = demand_agent.get_tools()

    assert len(tools) == 3
    assert tools[0]["function"]["name"] == "forecast_category_demand"
    assert tools[1]["function"]["name"] == "cluster_stores"
    assert tools[2]["function"]["name"] == "calculate_store_allocations"


def test_inventory_agent_parameter_awareness():
    """Test Inventory agent instructions mention parameter-driven allocation."""

    factory = AgentFactory()
    inventory_agent = factory.create_inventory_agent()

    assert "dc_holdback_percentage = 0.0" in inventory_agent.instructions
    assert "100% allocated to stores" in inventory_agent.instructions
    assert "replenishment_strategy" in inventory_agent.instructions


def test_pricing_agent_markdown_formula():
    """Test Pricing agent has Gap × Elasticity formula in instructions."""

    factory = AgentFactory()
    pricing_agent = factory.create_pricing_agent()

    assert "Gap × Elasticity" in pricing_agent.instructions or "gap" in pricing_agent.instructions.lower()
    assert "elasticity_coefficient" in pricing_agent.instructions


@pytest.mark.asyncio
async def test_demand_agent_placeholder_forecast():
    """Test Demand agent placeholder tool returns mock forecast."""

    factory = AgentFactory()
    demand_agent = factory.create_demand_agent()

    result = await demand_agent.forecast_category_demand_placeholder(
        historical_sales_csv="mock.csv",
        weeks=12,
        safety_stock_adjustment=0.20
    )

    assert result["total_season_demand"] == 8000
    assert result["prophet_forecast"] == 8200
    assert result["arima_forecast"] == 7800
    assert result["safety_stock_pct"] == 0.20


@pytest.mark.asyncio
async def test_pricing_agent_markdown_calculation():
    """Test Pricing agent calculates markdown correctly."""

    factory = AgentFactory()
    pricing_agent = factory.create_pricing_agent()

    result = await pricing_agent.calculate_markdown_recommendation_placeholder(
        actual_sell_through_pct=0.50,
        target_sell_through_pct=0.60,
        elasticity_coefficient=2.0
    )

    # Gap = 0.10, Elasticity = 2.0 → Markdown = 0.20 (20%)
    assert result["recommended_markdown_pct"] == 0.20
    assert result["gap_pct"] == 0.10
    assert "20%" in result["reasoning"] or "0.2" in result["reasoning"]
```

**Expected Output:**
- All tests passing
- Agent factory creates agents successfully
- Tool definitions validated
- Parameter awareness confirmed in instructions
- Placeholder tools return mock results

---

## Dev Notes

### OpenAI Agents SDK Architecture

**Key Concepts:**

1. **Agent Definition:**
```python
agent = {
    "name": "Demand Agent",
    "instructions": "You are responsible for forecasting...",
    "model": "gpt-4o-mini",
    "tools": [tool1, tool2, tool3],
    "handoffs": ["inventory", "pricing"]
}
```

2. **Tool Schema:**
```python
tool = {
    "type": "function",
    "function": {
        "name": "forecast_category_demand",
        "description": "Run Prophet + ARIMA ensemble",
        "parameters": {
            "type": "object",
            "properties": {
                "weeks": {"type": "integer"}
            },
            "required": ["weeks"]
        }
    }
}
```

3. **Handoff Configuration:**
```python
orchestrator_handoffs = ["demand", "inventory", "pricing"]
# Orchestrator can hand off to any of these 3 agents
```

4. **Dynamic Handoff Enabling:**
```python
# Re-forecast handoff (disabled by default, enabled when variance >20%)
handoff(
    demand_agent,
    name="reforecast",
    description="Re-forecast demand based on variance alert",
    enabled=False  # Toggled at runtime
)
```

### Parameter-Driven Autonomous Reasoning

**Key Pattern:**

```python
# Agent instructions include parameter-based reasoning
instructions = """
When replenishment_strategy = "none":
  - Reasoning: "No replenishment configured → increase safety stock to 25%"
  - Action: Adjust safety_stock_pct from 0.20 to 0.25

When dc_holdback_percentage = 0.0:
  - Reasoning: "0% holdback → allocate 100% to stores at Week 0"
  - Action: Skip DC allocation phase entirely
"""
```

**Benefits:**
- Agents autonomously adapt to different retail strategies
- No hard-coded business logic (LLM reasons about parameters)
- Same code handles Zara (0% holdback) and Standard (45% holdback) scenarios

### Scaffolding vs Full Implementation

**Phase 3 (This Story) - Scaffolding:**
- Agent classes created with instructions
- Tool definitions with Pydantic schemas
- Placeholder tool implementations return mock data
- No actual LLM calls (agent.coordinate_forecast_workflow is placeholder)

**Phase 8 (Full Implementation):**
- Replace placeholders with `openai_agents.Session.run()`
- Actual LLM reasoning (agents decide when to call tools)
- Real tool implementations call ML models
- WebSocket broadcasting of agent progress

### Tool Output Validation (Guardrails)

**Pattern (Phase 8):**
```python
from openai_agents import Guardrail

def validate_forecast_output(result: dict) -> dict:
    if result.get("total_season_demand", 0) <= 0:
        raise ValueError("Forecast must be positive")
    if result.get("total_season_demand", 0) > 100000:
        raise ValueError("Forecast exceeds reasonable limit")
    return result

demand_agent = Agent(
    name="Demand Agent",
    tools=[...],
    guardrails=[Guardrail(output_validation=validate_forecast_output)]
)
```

### Critical References

- **Planning Spec:** `planning/3_technical_architecture_v3.3.md` lines 900-1600 (Agent detailed approaches)
- **Implementation Plan:** `implementation_plan.md` lines 320-352 (Task 9 details)
- **OpenAI Agents SDK Docs:** https://platform.openai.com/docs/agents (official documentation)

---

## Testing

### Manual Testing Checklist

- [ ] Agent factory initializes all 4 agents successfully
- [ ] Orchestrator agent has handoff configuration to 3 specialist agents
- [ ] Demand agent has 3 tools defined (forecast, cluster, allocate)
- [ ] Inventory agent has 3 tools defined (manufacturing, allocation, replenishment)
- [ ] Pricing agent has 1 tool defined (markdown calculation)
- [ ] All agent instructions mention SeasonParameters
- [ ] Placeholder tools return mock data
- [ ] Workflow service imports agent factory
- [ ] Pytest tests passing for all agents
- [ ] Logging shows agent initialization events

### Verification Commands

```bash
# Run pytest tests
cd backend
uv run pytest tests/test_agents.py -v

# Check agent initialization in logs
tail -f logs/backend.log | grep "Agent"

# Verify standard OpenAI client configuration
python -c "from app.agents.config import agent_config; print(agent_config.openai_model)"

# Test workflow service with agents
uv run uvicorn app.main:app --reload
```

---

## File List

**Files to Create:**
- `backend/app/agents/config.py` (AgentConfig class with standard OpenAI settings)
- `backend/app/agents/orchestrator.py` (OrchestratorAgent class with handoff configuration)
- `backend/app/agents/demand.py` (DemandAgent class with 3 tools)
- `backend/app/agents/inventory.py` (InventoryAgent class with 3 tools)
- `backend/app/agents/pricing.py` (PricingAgent class with 1 tool)
- `backend/app/agents/factory.py` (AgentFactory class with dependency injection)
- `backend/tests/test_agents.py` (pytest tests for all agents)

**Files to Modify:**
- `backend/app/services/workflow_service.py` (integrate agent factory)

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

- [ ] AgentConfig class created with standard OpenAI settings
- [ ] OrchestratorAgent class with parameter-aware instructions
- [ ] Orchestrator handoff configuration to 3 specialist agents
- [ ] DemandAgent class with 3 tool definitions
- [ ] InventoryAgent class with 3 tool definitions
- [ ] PricingAgent class with 1 tool definition
- [ ] All agent instructions mention SeasonParameters and parameter-driven reasoning
- [ ] Placeholder tool implementations return mock data
- [ ] AgentFactory class with dependency injection
- [ ] Workflow service integrates agent factory
- [ ] All pytest tests passing
- [ ] Logging shows agent initialization
- [ ] Agent scaffolding ready for Phase 8 full implementation
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
**Last Updated:** 2025-10-21 (Implementation completed)
**Story Points:** 4
**Priority:** P0 (Blocker for Phase 8 - Orchestrator Agent)
