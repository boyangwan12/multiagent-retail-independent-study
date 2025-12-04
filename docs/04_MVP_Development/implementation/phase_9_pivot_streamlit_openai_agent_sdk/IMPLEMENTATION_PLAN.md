# Implementation Plan: Deterministic Workflow Architecture

**Version:** 1.1
**Date:** 2025-11-24
**Status:** Planning
**Previous:** `backend-agent-as-tool/` (archived)
**New:** `backend/` (deterministic workflow)

> **SDK Reference:** All patterns in this document are validated against OpenAI Agents Python SDK documentation via Context7.

---

## Executive Summary

This plan transitions from the **agent-as-tool** pattern (where agents call agents as tools) to a **deterministic workflow orchestration** pattern (where Python code controls agent execution via `Runner.run()`).

### Why This Change?

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| Tools don't pass Pydantic data | `agent.as_tool()` returns text only | Use `Runner.run()` with `output_type` |
| Variance loop unreliable | String pattern matching is brittle | Workflow layer checks `is_high_variance` directly |
| Handoffs don't return | Handoffs are one-way transfers | Use deterministic `if/while` control flow |
| Guardrails don't work | Requires `output_type` on agent | Set `output_type` since we're not using `as_tool()` |

### Target Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT UI LAYER                                │
│  streamlit_app.py - User interface, file uploads, visualizations            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW LAYER (Python)                             │
│           Deterministic orchestration with if/while control flow            │
│                                                                             │
│  workflows/                                                                 │
│    ├── season_workflow.py      # Full 12-week season orchestration          │
│    ├── forecast_workflow.py    # Demand forecast + variance loop            │
│    ├── allocation_workflow.py  # Clustering + allocation                    │
│    ├── pricing_workflow.py     # Markdown checkpoint logic                  │
│    └── workflow_types.py       # WorkflowParams, WorkflowResult             │
│                                                                             │
│  Key Operations:                                                            │
│    - Runner.run(demand_agent, output_type=ForecastResult)                   │
│    - if variance > threshold: rerun forecast                                │
│    - if week == 6 and sell_through < 0.60: run pricing                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                   ┌─────────────────┼─────────────────┐
                   ▼                 ▼                 ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│   DEMAND AGENT       │ │  INVENTORY AGENT     │ │   PRICING AGENT      │
│                      │ │                      │ │                      │
│ output_type=         │ │ output_type=         │ │ output_type=         │
│   ForecastResult     │ │   AllocationResult   │ │   MarkdownResult     │
│                      │ │                      │ │                      │
│ Tools:               │ │ Tools:               │ │ Tools:               │
│ - run_demand_forecast│ │ - cluster_stores     │ │ - calculate_markdown │
│                      │ │ - allocate_inventory │ │                      │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘
                   │                 │                 │
                   └─────────────────┼─────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TOOLS LAYER                                    │
│  agent_tools/ - Pure computation, no LLM reasoning                          │
│    ├── demand_tools.py         # Prophet/ARIMA forecasting                  │
│    ├── inventory_tools.py      # K-means clustering, allocation             │
│    ├── pricing_tools.py        # Gap × Elasticity calculation               │
│    └── variance_tools.py       # Called DIRECTLY by workflow (not agent)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation & Types (Day 1)

### Objective
Set up the new backend folder structure and define all shared Pydantic types.

### Files to Create

```
backend/
├── __init__.py
├── requirements.txt
├── .env.example
│
├── config/
│   ├── __init__.py
│   └── settings.py              # OPENAI_MODEL, OPENAI_API_KEY
│
├── schemas/
│   ├── __init__.py
│   ├── forecast_schemas.py      # ForecastResult, ForecastParams
│   ├── allocation_schemas.py    # AllocationResult, ClusterResult
│   ├── pricing_schemas.py       # MarkdownResult, MarkdownParams
│   ├── variance_schemas.py      # VarianceResult
│   └── workflow_schemas.py      # WorkflowParams, WorkflowResult
│
└── utils/
    ├── __init__.py
    ├── data_loader.py           # Copy from old backend (TrainingDataLoader)
    └── context.py               # ForecastingContext
```

### Context Pattern (SDK-Validated)

> **SDK Pattern:** Use dataclass or Pydantic model for context. Pass to `Runner.run()` via `context=` parameter.
> Tools access context via `RunContextWrapper[ContextType]`.
>
> **From SDK Docs:**
> ```python
> from dataclasses import dataclass
> from agents import Agent, RunContextWrapper, Runner, function_tool
>
> @dataclass
> class UserInfo:
>     name: str
>     uid: int
>
> @function_tool
> async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:
>     """Fetch the age of the user."""
>     return f"The user {wrapper.context.name} is 47 years old"
>
> agent = Agent[UserInfo](
>     name="Assistant",
>     tools=[fetch_user_age],
> )
>
> result = await Runner.run(
>     starting_agent=agent,
>     input="What is the age of the user?",
>     context=user_info,  # Pass context here
> )
> ```

**`utils/context.py`:**
```python
from dataclasses import dataclass, field
from typing import List, Optional
from utils.data_loader import TrainingDataLoader

@dataclass
class ForecastingContext:
    """Shared context for all agents in the workflow.

    SDK Note: Pass this to Runner.run(context=...) and access
    in tools via wrapper.context
    """
    data_loader: TrainingDataLoader
    session_id: str

    # Workflow state
    current_week: int = 0
    forecast_by_week: List[int] = field(default_factory=list)

    # Variance checking
    variance_file_path: Optional[str] = None
    actual_sales: Optional[List[int]] = None

    # Pricing state
    total_allocated: int = 0
    total_sold: int = 0

    @property
    def has_actual_sales(self) -> bool:
        return self.actual_sales is not None and len(self.actual_sales) > 0

    def calculate_sell_through(self) -> float:
        if self.total_allocated == 0:
            return 0.0
        return self.total_sold / self.total_allocated
```

### Key Schema Definitions

> **SDK Pattern:** Use Pydantic `BaseModel` for `output_type`. The SDK automatically enforces these schemas.
>
> **From SDK Docs:**
> ```python
> from pydantic import BaseModel
> from agents import Agent
>
> class CalendarEvent(BaseModel):
>     name: str
>     date: str
>     participants: list[str]
>
> agent = Agent(
>     name="Calendar extractor",
>     instructions="Extract calendar events from text",
>     output_type=CalendarEvent,
> )
> ```

**`schemas/forecast_schemas.py`:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ForecastResult(BaseModel):
    """Output from Demand Agent - used as output_type

    SDK Note: When output_type is set, the agent MUST return data
    conforming to this schema. The SDK handles JSON parsing automatically.
    """
    total_demand: int = Field(description="Sum of all weekly forecasts")
    forecast_by_week: List[int] = Field(description="Weekly demand predictions")
    safety_stock_pct: float = Field(ge=0.10, le=0.50, description="Safety stock (10-50%)")
    confidence: float = Field(ge=0.0, le=1.0, description="Forecast confidence")
    model_used: str = Field(description="'prophet_arima_ensemble', 'prophet', or 'arima'")
    lower_bound: List[int] = Field(default_factory=list)
    upper_bound: List[int] = Field(default_factory=list)
    explanation: str = Field(description="Agent's reasoning about the forecast")
```

**`schemas/variance_schemas.py`:**
```python
class VarianceResult(BaseModel):
    """Output from check_variance - called directly by workflow"""
    week_number: int
    actual_total: int
    forecast_total: int
    variance_pct: float
    is_high_variance: bool  # Workflow uses this directly!
    recommendation: str
```

**`schemas/workflow_schemas.py`:**
```python
class WorkflowParams(BaseModel):
    """Parameters extracted from user's natural language"""
    category: str
    forecast_horizon_weeks: int = 12
    season_start_date: str
    dc_holdback_pct: float = 0.45
    replenishment_strategy: str = "weekly"  # "none", "weekly", "bi-weekly"
    markdown_week: int = 6
    markdown_threshold: float = 0.60
    variance_threshold: float = 0.20

class SeasonResult(BaseModel):
    """Final output from full season workflow"""
    forecast: ForecastResult
    allocation: AllocationResult
    markdown: Optional[MarkdownResult] = None
    variance_history: List[VarianceResult] = []
    reforecast_count: int = 0
```

### Tasks
- [ ] Create folder structure
- [ ] Define all Pydantic schemas
- [ ] Copy `data_loader.py` and `context.py` from old backend
- [ ] Create `config/settings.py` with environment variable loading
- [ ] Create `requirements.txt`

---

## Phase 2: Agent Tools (Day 2)

### Objective
Port the existing tools with minimal changes. The tools already work correctly.

### Files to Create

```
backend/
└── agent_tools/
    ├── __init__.py
    ├── demand_tools.py          # Copy from old backend (minor schema import changes)
    ├── inventory_tools.py       # Copy from old backend
    └── pricing_tools.py         # NEW - Gap × Elasticity calculation
```

### Key Addition: Pricing Tool

> **SDK Pattern:** Use `@function_tool` decorator. Tools can return Pydantic models.
>
> **From SDK Docs:**
> ```python
> from typing import Annotated
> from pydantic import BaseModel, Field
> from agents import Agent, Runner, function_tool
>
> class Weather(BaseModel):
>     city: str = Field(description="The city name")
>     temperature_range: str = Field(description="Temperature in Celsius")
>     conditions: str = Field(description="Weather conditions")
>
> @function_tool
> def get_weather(city: Annotated[str, "The city to get weather for"]) -> Weather:
>     """Get current weather information for a specified city."""
>     return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")
> ```

**`agent_tools/pricing_tools.py`:**
```python
from typing import Annotated
from pydantic import BaseModel, Field
from agents import function_tool

class MarkdownResult(BaseModel):
    """Result from markdown calculation"""
    recommended_markdown_pct: float = Field(description="Markdown % (0-40, rounded to 5%)")
    current_sell_through: float = Field(description="Current sell-through rate")
    target_sell_through: float = Field(description="Target rate (usually 0.60)")
    gap: float = Field(description="Gap = target - current")
    elasticity_used: float = Field(description="Price elasticity factor")
    explanation: str = Field(description="Reasoning for the markdown")

@function_tool
def calculate_markdown(
    current_sell_through: Annotated[float, "Current sell-through rate (0.0-1.0)"],
    target_sell_through: Annotated[float, "Target rate (default 0.60)"] = 0.60,
    elasticity: Annotated[float, "Price elasticity (default 2.0)"] = 2.0,
    max_markdown: Annotated[float, "Maximum allowed markdown (default 40%)"] = 0.40
) -> MarkdownResult:
    """
    Calculate markdown using Gap × Elasticity formula.

    Args:
        current_sell_through: Current sell-through rate (0.0-1.0)
        target_sell_through: Target rate (default 0.60)
        elasticity: Price elasticity (default 2.0)
        max_markdown: Maximum allowed markdown (default 40%)

    Returns:
        MarkdownResult with recommended markdown percentage
    """
    gap = target_sell_through - current_sell_through

    if gap <= 0:
        # Already at or above target
        return MarkdownResult(
            recommended_markdown_pct=0.0,
            current_sell_through=current_sell_through,
            target_sell_through=target_sell_through,
            gap=gap,
            elasticity_used=elasticity,
            explanation=f"Sell-through ({current_sell_through:.1%}) meets target ({target_sell_through:.1%}). No markdown needed."
        )

    # Gap × Elasticity formula
    raw_markdown = gap * elasticity

    # Round to nearest 5%
    rounded_markdown = round(raw_markdown * 20) / 20

    # Cap at max_markdown
    final_markdown = min(rounded_markdown, max_markdown)

    return MarkdownResult(
        recommended_markdown_pct=final_markdown,
        current_sell_through=current_sell_through,
        target_sell_through=target_sell_through,
        gap=gap,
        elasticity_used=elasticity,
        explanation=f"Gap ({gap:.1%}) × Elasticity ({elasticity}) = {raw_markdown:.1%}, rounded to {final_markdown:.0%}"
    )
```

### Tasks
- [ ] Copy `demand_tools.py` (update imports)
- [ ] Copy `inventory_tools.py` (update imports)
- [ ] Create `pricing_tools.py` with Gap × Elasticity
- [ ] Create `variance_tools.py` (simplified - pure function, no agent wrapper)
- [ ] Verify all tools return Pydantic models

---

## Phase 3: Agents with output_type (Day 3)

### Objective
Create agents that use `output_type` for structured output. No more `as_tool()`.

> **SDK Pattern:** When `output_type` is set, the agent returns typed Pydantic data instead of text.
> Access it via `result.final_output` (typed) or `result.final_output_as(MyType)`.
>
> **From SDK Docs:**
> ```python
> @dataclass
> class JokeCollection:
>     jokes: list[str]
>     theme: str
>     total_count: int
>
> agent = Agent(
>     name="Comedian",
>     instructions="Generate jokes based on user request.",
>     output_type=JokeCollection
> )
>
> result = await Runner.run(agent, "Tell me 3 programming jokes.")
> jokes = result.final_output_as(JokeCollection)  # Typed access!
> print(f"Theme: {jokes.theme}")
> ```

### Files to Create

```
backend/
└── my_agents/
    ├── __init__.py
    ├── demand_agent.py          # output_type=ForecastResult
    ├── inventory_agent.py       # output_type=AllocationResult
    └── pricing_agent.py         # output_type=MarkdownResult (NEW)
```

### Key Pattern: Agent with output_type

**`my_agents/demand_agent.py`:**
```python
from agents import Agent
from config.settings import OPENAI_MODEL
from schemas.forecast_schemas import ForecastResult
from agent_tools.demand_tools import run_demand_forecast

demand_agent = Agent(
    name="Demand Forecasting Agent",
    instructions="""You are an expert Demand Forecasting Agent.

    ## YOUR ROLE
    Generate accurate demand forecasts using Prophet + ARIMA ensemble.

    ## WHEN CALLED
    1. Extract category and forecast_horizon from input
    2. Call run_demand_forecast tool
    3. Interpret results and explain your reasoning

    ## OUTPUT
    Your output MUST conform to ForecastResult schema:
    - total_demand: Sum of weekly forecasts
    - forecast_by_week: List of weekly predictions
    - safety_stock_pct: 10-50% based on confidence
    - confidence: 0.0-1.0
    - model_used: Which model generated this
    - explanation: Your reasoning about the forecast

    Be concise but explain WHY the forecast looks the way it does.
    """,
    model=OPENAI_MODEL,
    tools=[run_demand_forecast],
    output_type=ForecastResult  # KEY: Enables structured output + guardrails
)
```

**`my_agents/pricing_agent.py`:** (NEW)
```python
from agents import Agent
from config.settings import OPENAI_MODEL
from schemas.pricing_schemas import MarkdownResult
from agent_tools.pricing_tools import calculate_markdown

pricing_agent = Agent(
    name="Pricing Agent",
    instructions="""You are an expert Pricing Agent for markdown optimization.

    ## YOUR ROLE
    Determine optimal markdown percentages to achieve sell-through targets.

    ## WHEN CALLED
    You receive:
    - current_sell_through: How much inventory has sold
    - target_sell_through: Target (usually 60%)
    - week_number: Current week in season

    ## FORMULA
    Gap × Elasticity = Markdown
    - Gap = target - current (e.g., 0.60 - 0.45 = 0.15)
    - Elasticity = 2.0 (configurable)
    - Markdown = 0.15 × 2.0 = 0.30 (30%)

    ## CONSTRAINTS
    - Round to nearest 5%
    - Cap at 40% maximum
    - Apply uniformly across all stores

    ## OUTPUT
    Return MarkdownResult with your recommended markdown and explanation.
    """,
    model=OPENAI_MODEL,
    tools=[calculate_markdown],
    output_type=MarkdownResult
)
```

### Tasks
- [ ] Create `demand_agent.py` with `output_type=ForecastResult`
- [ ] Create `inventory_agent.py` with `output_type=AllocationResult`
- [ ] Create `pricing_agent.py` with `output_type=MarkdownResult`
- [ ] Remove all `as_tool()` usage
- [ ] Test each agent individually with `Runner.run()`

---

## Phase 4: Workflow Orchestration (Day 4-5)

### Objective
Create the deterministic workflow layer that orchestrates agents.

> **SDK Pattern:** Use `Runner.run()` to execute agents. The workflow code controls WHEN agents run (deterministic), while agents control HOW they reason (agentic).
>
> **From SDK Docs:**
> ```python
> from agents import Agent, Runner
>
> async def main():
>     agent = Agent(name="Assistant", instructions="You are a helpful assistant")
>     result = await Runner.run(agent, "Write a haiku about recursion in programming.")
>     print(result.final_output)
> ```

### Files to Create

```
backend/
└── workflows/
    ├── __init__.py
    ├── forecast_workflow.py     # Demand forecast + variance loop
    ├── allocation_workflow.py   # Clustering + allocation
    ├── pricing_workflow.py      # Markdown checkpoint
    └── season_workflow.py       # Full season orchestration
```

### Key Pattern: Deterministic Orchestration

**`workflows/forecast_workflow.py`:**
```python
from agents import Runner
from my_agents.demand_agent import demand_agent
from schemas.forecast_schemas import ForecastResult
from schemas.variance_schemas import VarianceResult
from agent_tools.variance_tools import check_variance  # Direct call!
from utils.context import ForecastingContext

async def run_forecast_with_variance_loop(
    context: ForecastingContext,
    category: str,
    forecast_horizon: int,
    variance_threshold: float = 0.20,
    max_reforecasts: int = 2
) -> tuple[ForecastResult, list[VarianceResult]]:
    """
    Run demand forecast with automatic variance-triggered re-forecasting.

    This is DETERMINISTIC orchestration:
    - Python code controls the loop (not LLM)
    - Variance check is pure function call (no agent needed)
    - Agent is called via Runner.run() with output_type
    """
    variance_history = []
    reforecast_count = 0

    while True:
        # Step 1: Run demand agent with output_type
        result = await Runner.run(
            starting_agent=demand_agent,
            input=f"Forecast {category} for {forecast_horizon} weeks",
            context=context
        )

        forecast: ForecastResult = result.final_output  # Typed!

        # Step 2: Check if we have actual sales data to compare
        if not context.has_actual_sales:
            # Pre-season: no variance check needed
            return forecast, variance_history

        # Step 3: Check variance (DIRECT CALL - no agent)
        variance = check_variance(
            actual_sales=context.actual_sales,
            forecast_by_week=forecast.forecast_by_week,
            week_number=context.current_week,
            threshold=variance_threshold
        )
        variance_history.append(variance)

        # Step 4: Deterministic decision
        if not variance.is_high_variance:
            # Variance acceptable - done!
            return forecast, variance_history

        if reforecast_count >= max_reforecasts:
            # Hit max reforecasts - return best we have
            return forecast, variance_history

        # Step 5: Re-forecast with updated context
        context.add_actual_sales_to_history()  # Enrich training data
        reforecast_count += 1
        # Loop continues...

    return forecast, variance_history
```

**`workflows/season_workflow.py`:**
```python
from agents import Runner
from workflows.forecast_workflow import run_forecast_with_variance_loop
from workflows.allocation_workflow import run_allocation
from workflows.pricing_workflow import run_markdown_check
from schemas.workflow_schemas import WorkflowParams, SeasonResult
from utils.context import ForecastingContext

async def run_full_season(
    context: ForecastingContext,
    params: WorkflowParams
) -> SeasonResult:
    """
    Full 12-week season workflow with all 3 agents.

    DETERMINISTIC FLOW:
    1. Demand Agent → ForecastResult
    2. Inventory Agent → AllocationResult
    3. Weekly variance checks (loop)
    4. Week 6: Pricing Agent → MarkdownResult (if needed)
    """

    # Phase 1: Pre-season forecast
    forecast, variance_history = await run_forecast_with_variance_loop(
        context=context,
        category=params.category,
        forecast_horizon=params.forecast_horizon_weeks,
        variance_threshold=params.variance_threshold
    )

    # Phase 2: Inventory allocation
    allocation = await run_allocation(
        context=context,
        forecast=forecast,
        dc_holdback_pct=params.dc_holdback_pct,
        replenishment_strategy=params.replenishment_strategy
    )

    # Phase 3: In-season monitoring (simplified for MVP)
    markdown = None

    # Phase 4: Markdown checkpoint at configured week
    if context.current_week >= params.markdown_week:
        sell_through = context.calculate_sell_through()

        # DETERMINISTIC: Python decides if pricing agent runs
        if sell_through < params.markdown_threshold:
            markdown = await run_markdown_check(
                context=context,
                current_sell_through=sell_through,
                target_sell_through=params.markdown_threshold
            )

    return SeasonResult(
        forecast=forecast,
        allocation=allocation,
        markdown=markdown,
        variance_history=variance_history,
        reforecast_count=len([v for v in variance_history if v.is_high_variance])
    )
```

### Tasks
- [ ] Create `forecast_workflow.py` with variance loop
- [ ] Create `allocation_workflow.py`
- [ ] Create `pricing_workflow.py`
- [ ] Create `season_workflow.py` (full orchestration)
- [ ] Test workflows with mock data
- [ ] Verify Pydantic data flows correctly between agents

---

## Phase 5: Guardrails (Day 6)

### Objective
Add output validation guardrails that were impossible with `as_tool()`.

> **SDK Pattern:** Output guardrails validate agent responses BEFORE returning to caller. Use `@output_guardrail` decorator.
> When `tripwire_triggered=True`, raises `OutputGuardrailTripwireTriggered` exception.
>
> **From SDK Docs:**
> ```python
> from pydantic import BaseModel
> from agents import (
>     Agent, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered,
>     RunContextWrapper, Runner, output_guardrail,
> )
>
> class MessageOutput(BaseModel):
>     response: str
>
> class MathOutput(BaseModel):
>     reasoning: str
>     is_math: bool
>
> guardrail_agent = Agent(
>     name="Guardrail check",
>     instructions="Check if the output includes any math.",
>     output_type=MathOutput,
> )
>
> @output_guardrail
> async def math_guardrail(
>     ctx: RunContextWrapper, agent: Agent, output: MessageOutput
> ) -> GuardrailFunctionOutput:
>     result = await Runner.run(guardrail_agent, output.response, context=ctx.context)
>     return GuardrailFunctionOutput(
>         output_info=result.final_output,
>         tripwire_triggered=result.final_output.is_math,
>     )
>
> agent = Agent(
>     name="Customer support agent",
>     instructions="You help customers with their questions.",
>     output_guardrails=[math_guardrail],
>     output_type=MessageOutput,
> )
> ```

### Files to Create

```
backend/
└── guardrails/
    ├── __init__.py
    ├── forecast_guardrails.py   # Validate ForecastResult
    ├── allocation_guardrails.py # Validate unit conservation
    └── pricing_guardrails.py    # Validate markdown bounds
```

### Key Pattern: Output Guardrail

**`guardrails/forecast_guardrails.py`:**
```python
from agents import output_guardrail, GuardrailFunctionOutput, RunContextWrapper, Agent
from schemas.forecast_schemas import ForecastResult

@output_guardrail
async def validate_forecast(
    ctx: RunContextWrapper,
    agent: Agent,
    output: ForecastResult
) -> GuardrailFunctionOutput:
    """
    Validate forecast output before returning to workflow.

    NOW WORKS because agent has output_type=ForecastResult!
    """
    errors = []

    # Rule 1: Total demand must equal sum of weekly forecasts
    expected_total = sum(output.forecast_by_week)
    if output.total_demand != expected_total:
        errors.append(
            f"Unit conservation violated: total_demand ({output.total_demand}) "
            f"!= sum(forecast_by_week) ({expected_total})"
        )

    # Rule 2: Safety stock must be in valid range
    if not (0.10 <= output.safety_stock_pct <= 0.50):
        errors.append(
            f"Safety stock {output.safety_stock_pct:.0%} out of range [10%, 50%]"
        )

    # Rule 3: No negative forecasts
    if any(f < 0 for f in output.forecast_by_week):
        errors.append("Negative forecast values detected")

    # Rule 4: Confidence must be valid
    if not (0.0 <= output.confidence <= 1.0):
        errors.append(f"Invalid confidence: {output.confidence}")

    if errors:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"validation_errors": errors}
        )

    return GuardrailFunctionOutput(tripwire_triggered=False)
```

### Apply Guardrails to Agents

```python
# In my_agents/demand_agent.py
from guardrails.forecast_guardrails import validate_forecast

demand_agent = Agent(
    name="Demand Forecasting Agent",
    instructions="...",
    model=OPENAI_MODEL,
    tools=[run_demand_forecast],
    output_type=ForecastResult,
    output_guardrails=[validate_forecast]  # NOW WORKS!
)
```

### Handling Guardrail Exceptions

```python
# In workflow code
from agents.exceptions import OutputGuardrailTripwireTriggered

try:
    result = await Runner.run(demand_agent, input_prompt, context=context)
    forecast = result.final_output
except OutputGuardrailTripwireTriggered as e:
    # Guardrail triggered - handle validation failure
    print(f"Validation failed: {e.guardrail_result.output_info}")
    # Could retry, log, or raise to user
```

### Tasks
- [ ] Create `forecast_guardrails.py`
- [ ] Create `allocation_guardrails.py` (unit conservation)
- [ ] Create `pricing_guardrails.py` (40% cap, 5% rounding)
- [ ] Apply guardrails to all agents
- [ ] Test guardrail triggers with invalid outputs

---

## Phase 6: Streamlit Integration (Day 7-8)

### Objective
Connect the new workflow layer to Streamlit UI.

### Files to Create/Modify

```
backend/
└── streamlit_app.py             # New UI connecting to workflows
```

### Key Changes

1. **Remove coordinator agent** - workflows handle orchestration
2. **Call workflows directly** from Streamlit
3. **Display typed results** - no more regex parsing
4. **Show variance loop progress** in real-time

**UI Flow:**
```
User Input → Parameter Extraction → workflow/season_workflow.py
                                           ↓
                              ┌────────────┴────────────┐
                              ↓                         ↓
                        ForecastResult            AllocationResult
                              ↓                         ↓
                    Display forecast chart    Display allocation table
                              ↓
                    Show variance status
                              ↓
                    (Week 6) MarkdownResult
```

### Tasks
- [ ] Update Streamlit to call workflows instead of coordinator
- [ ] Remove regex parsing - use typed results directly
- [ ] Add variance loop progress indicator
- [ ] Add pricing agent UI section
- [ ] Test full user flow

---

## Phase 7: Testing & Polish (Day 9-10)

### Objective
Comprehensive testing and cleanup.

### Test Files

```
backend/
└── tests/
    ├── __init__.py
    ├── test_schemas.py          # Pydantic validation
    ├── test_tools.py            # Tool unit tests
    ├── test_agents.py           # Agent output validation
    ├── test_workflows.py        # Integration tests
    └── test_guardrails.py       # Guardrail trigger tests
```

### Test Scenarios

1. **Happy Path**: Forecast → Allocation → Markdown (no variance issues)
2. **Variance Loop**: High variance triggers reforecast (max 2x)
3. **Guardrail Trip**: Invalid output is caught and rejected
4. **Edge Cases**:
   - 0% DC holdback (Zara model)
   - No replenishment strategy
   - Sell-through already above target (no markdown)

### Tasks
- [ ] Write unit tests for all schemas
- [ ] Write integration tests for workflows
- [ ] Test variance loop with mock data
- [ ] Test guardrail triggers
- [ ] Performance testing (<60s workflow)
- [ ] Code cleanup and documentation

---

## Appendix A: What Stays the Same

These components work well and will be copied with minimal changes:

| Component | Location | Changes Needed |
|-----------|----------|----------------|
| `TrainingDataLoader` | `utils/data_loader.py` | Update imports |
| `ForecastingContext` | `utils/context.py` | Add pricing fields |
| `run_demand_forecast` | `agent_tools/demand_tools.py` | Update schema imports |
| `cluster_stores` | `agent_tools/inventory_tools.py` | Update schema imports |
| `allocate_inventory` | `agent_tools/inventory_tools.py` | Update schema imports |
| Mock data files | `data/` | No changes |

---

## Appendix B: What Gets Removed

These patterns are replaced by deterministic orchestration:

| Pattern | Why Removed | Replacement |
|---------|-------------|-------------|
| `agent.as_tool()` | Returns text, no Pydantic | `Runner.run()` with `output_type` |
| `coordinator_agent.py` | LLM orchestration unreliable | Python workflow layer |
| String pattern matching | Brittle, breaks easily | Typed Pydantic fields |
| `HIGH_VARIANCE_REFORECAST_NEEDED` | String signal in agent output | `VarianceResult.is_high_variance` |
| Handoffs | One-way, no return | `Runner.run()` calls with returns |

---

## Appendix C: Agentic vs Deterministic

| What | Who Decides | Why |
|------|-------------|-----|
| **When to forecast** | Workflow (code) | Business rule: pre-season |
| **How to forecast** | Demand Agent (LLM) | Reasoning: model selection, confidence interpretation |
| **When to check variance** | Workflow (code) | Business rule: when actual data available |
| **What variance threshold** | Workflow (code) | Business rule: 20% |
| **If variance is high** | Workflow (code) | Math: `abs(variance_pct) > threshold` |
| **Why variance is high** | Demand Agent (LLM) | Reasoning: explain contributing factors |
| **When to markdown** | Workflow (code) | Business rule: Week 6, <60% sell-through |
| **What markdown %** | Pricing Agent (LLM) | Reasoning: Gap × Elasticity with explanation |

---

## Appendix D: File Checklist

### Phase 1: Foundation
- [ ] `backend/__init__.py`
- [ ] `backend/requirements.txt`
- [ ] `backend/config/__init__.py`
- [ ] `backend/config/settings.py`
- [ ] `backend/schemas/__init__.py`
- [ ] `backend/schemas/forecast_schemas.py`
- [ ] `backend/schemas/allocation_schemas.py`
- [ ] `backend/schemas/pricing_schemas.py`
- [ ] `backend/schemas/variance_schemas.py`
- [ ] `backend/schemas/workflow_schemas.py`
- [ ] `backend/utils/__init__.py`
- [ ] `backend/utils/data_loader.py`
- [ ] `backend/utils/context.py`

### Phase 2: Tools
- [ ] `backend/agent_tools/__init__.py`
- [ ] `backend/agent_tools/demand_tools.py`
- [ ] `backend/agent_tools/inventory_tools.py`
- [ ] `backend/agent_tools/pricing_tools.py`
- [ ] `backend/agent_tools/variance_tools.py`

### Phase 3: Agents
- [ ] `backend/my_agents/__init__.py`
- [ ] `backend/my_agents/demand_agent.py`
- [ ] `backend/my_agents/inventory_agent.py`
- [ ] `backend/my_agents/pricing_agent.py`

### Phase 4: Workflows
- [ ] `backend/workflows/__init__.py`
- [ ] `backend/workflows/forecast_workflow.py`
- [ ] `backend/workflows/allocation_workflow.py`
- [ ] `backend/workflows/pricing_workflow.py`
- [ ] `backend/workflows/season_workflow.py`

### Phase 5: Guardrails
- [ ] `backend/guardrails/__init__.py`
- [ ] `backend/guardrails/forecast_guardrails.py`
- [ ] `backend/guardrails/allocation_guardrails.py`
- [ ] `backend/guardrails/pricing_guardrails.py`

### Phase 6: UI
- [ ] `backend/streamlit_app.py`

### Phase 7: Tests
- [ ] `backend/tests/__init__.py`
- [ ] `backend/tests/test_schemas.py`
- [ ] `backend/tests/test_tools.py`
- [ ] `backend/tests/test_agents.py`
- [ ] `backend/tests/test_workflows.py`
- [ ] `backend/tests/test_guardrails.py`

---

## Ready to Start?

When you're ready to begin implementation, say: **"Let's start Phase 1"**

I'll create the foundation files and we'll build up from there.
