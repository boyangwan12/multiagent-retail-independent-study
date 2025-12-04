# Architecture Analysis: Agent-as-Tool vs Handoffs vs Deterministic Workflows

## Executive Summary

This document analyzes the current implementation of the retail forecasting system and explains why **deterministic workflow orchestration** is the recommended approach for the variance-triggered re-forecasting use case, as opposed to the current agent-as-tool pattern or handoffs.

---

## Table of Contents

1. [Current Implementation Overview](#1-current-implementation-overview)
2. [The Problem: Agent-as-Tool Limitations](#2-the-problem-agent-as-tool-limitations)
3. [Why Handoffs Won't Work Either](#3-why-handoffs-wont-work-either)
4. [The Solution: Deterministic Workflow Orchestration](#4-the-solution-deterministic-workflow-orchestration)
5. [Guardrails Implementation](#5-guardrails-implementation)
6. [Recommended Architecture](#6-recommended-architecture)
7. [Implementation Roadmap](#7-implementation-roadmap)

---

## 1. Current Implementation Overview

### 1.1 Target Architecture

The new architecture uses **deterministic workflow orchestration** with direct agent calls:

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW LAYER                                │
│         (Python code - deterministic orchestration)              │
│                                                                  │
│  forecast_workflow.py                                            │
│    ├── Calls demand_agent via Runner.run()                       │
│    ├── Calls inventory_agent via Runner.run()                    │
│    └── Calls check_variance() DIRECTLY (no agent)                │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
          ┌────────┴────────┐                   │
          ▼                 ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  demand_agent   │ │ inventory_agent │ │  DIRECT CALL    │
│                 │ │                 │ │                 │
│  tools=[        │ │  tools=[        │ │  check_variance │
│   run_demand_   │ │   cluster_      │ │  (from workflow)│
│   forecast      │ │   stores,       │ │                 │
│  ]              │ │   allocate_     │ │                 │
│                 │ │   inventory     │ │                 │
│  output_type=   │ │  ]              │ │                 │
│  ForecastResult │ │                 │ │                 │
└────────┬────────┘ │  output_type=   │ └─────────────────┘
         │          │  AllocationResult
         ▼          └────────┬────────┘
┌─────────────────┐          ▼
│  demand_tools   │ ┌─────────────────┐
│                 │ │ inventory_tools │
│  run_demand_    │ │                 │
│  forecast()     │ │  cluster_       │
│                 │ │  stores()       │
│  ForecastResult │ │                 │
└─────────────────┘ │  allocate_      │
                    │  inventory()    │
                    └─────────────────┘
```

### 1.2 Current Flow (Legacy - Being Replaced)

1. User provides parameters (category, horizon, etc.)
2. Coordinator calls `demand_forecasting_expert` (demand_agent.as_tool())
3. Demand agent calls `run_demand_forecast` tool
4. Coordinator receives text response, presents to user
5. User confirms → Coordinator calls `inventory_allocation_expert`
6. Inventory agent calls `cluster_stores` then `allocate_inventory`
7. User uploads actual sales data → Coordinator calls inventory agent for variance check
8. **PROBLEM**: If variance is high, coordinator tries to call demand agent again

### 1.3 The Variance Re-Forecasting Logic

From `coordinator_agent.py:254-275`:

```python
**CRITICAL: Check for HIGH_VARIANCE_REFORECAST_NEEDED signal**
- If the inventory agent's response contains "HIGH_VARIANCE_REFORECAST_NEEDED",
  this means variance exceeded threshold
- You MUST automatically trigger re-forecasting (do NOT ask user for permission)
- This creates a self-healing feedback loop
```

This logic relies on **string pattern matching** in the LLM's response to trigger re-forecasting - an inherently fragile approach.

---

## 2. The Problem: Agent-as-Tool Limitations

### 2.1 Pydantic Data Serialization Issue

**Core Issue**: When using `agent.as_tool()`, the sub-agent returns **text output only**, not structured Pydantic data.

From `demand_agent.py:8-10`:
```python
# NOTE: Do NOT use output_type when agent is used with .as_tool()
# The agent returns conversational text; structured data comes from the tool it calls
# Data validation happens automatically via Pydantic in the run_demand_forecast tool
```

This means:
- The `ForecastResult` Pydantic model is validated **inside** the demand agent's tool
- But the coordinator only sees the **text formatted output**, not the structured data
- To pass forecast results to the inventory agent, the coordinator must:
  1. Parse the text output (fragile regex)
  2. Reconstruct the data structure (error-prone)
  3. Hope the LLM formats everything correctly (unreliable)

### 2.2 Why `.as_tool()` Returns Text, Not Pydantic Objects

From OpenAI Agents SDK documentation:

> "The mental model for agents as tools is that the tool agent goes off and runs on its own, and then **returns the result to the original agent** as text."

The SDK's `as_tool()` pattern:
1. Creates a wrapper that converts the agent to a callable tool
2. Runs the agent with its own LLM context
3. Returns `result.final_output` as a **string** to the caller

There is a `custom_output_extractor` parameter, but it operates on `RunResult.new_items` (chat history), not on Pydantic objects:

```python
async def extract_json_payload(run_result: RunResult) -> str:
    for item in reversed(run_result.new_items):
        if isinstance(item, ToolCallOutputItem) and item.output.strip().startswith("{"):
            return item.output.strip()
    return "{}"
```

This requires the sub-agent to **output JSON as text** in its chat - still fragile.

### 2.3 The Variance Loop Problem

Current implementation attempts this flow:

```
User uploads actuals
       │
       ▼
Coordinator asks inventory agent to check_variance
       │
       ▼
Inventory agent returns text with "HIGH_VARIANCE_REFORECAST_NEEDED"
       │
       ▼
Coordinator parses this string (FRAGILE!)
       │
       ▼
Coordinator calls demand agent AGAIN with same parameters
       │
       ▼
Demand agent generates new forecast
       │
       ▼
Coordinator tries to pass new forecast to inventory agent
       │
       ▼
🔥 BREAKS: How does coordinator know the forecast parameters?
            How does it pass the ForecastResult to inventory?
            What if the LLM doesn't include the signal string?
```

### 2.4 Evidence of Problems in Current Code

From `streamlit_app.py:156-178`, the UI has extensive fallback logic:

```python
# FALLBACK: Try to parse from agent response text (brittle but better than nothing)
import re
total_match = re.search(r'Total Demand.*?(\d+,?\d*)\s+units', response, re.IGNORECASE)
confidence_match = re.search(r'Confidence.*?(\d+)%', response, re.IGNORECASE)

if total_match or confidence_match:
    st.warning("⚠️ **Using fallback text parsing** (structured data wasn't captured)")
```

This demonstrates that the structured data pipeline is already unreliable.

---

## 3. Why Handoffs Won't Work Either

### 3.1 Handoff Mental Model

From SDK documentation:

> "The mental model for handoffs is that the new agent **takes over**. It sees the previous conversation history, and **owns the conversation from that point onwards**."

This means:
- Control transfers **completely** to the new agent
- The original agent **cannot** receive results back
- There's no "call and return" - it's a one-way transfer

### 3.2 Handoff Flow Visualization

```
Coordinator ──handoff──▶ Demand Agent
                              │
                              │ (Demand agent now owns the conversation)
                              │
                              ▼
                         User interacts with demand agent directly
                              │
                              │ Can handoff to another agent,
                              │ but cannot "return" to coordinator
                              ▼
                         Inventory Agent (takes over)
```

### 3.3 Why This Doesn't Work for Re-Forecasting

The variance re-forecasting loop requires:
1. **Conditional branching**: If variance > threshold, re-forecast; else continue
2. **Data passing**: Pass ForecastResult from demand to inventory agent
3. **Iteration**: Potentially re-forecast multiple times until variance is acceptable
4. **Orchestration control**: Coordinator decides when to stop

Handoffs cannot provide:
- Return-to-caller semantics
- Conditional execution based on results
- Iterative loops with exit conditions
- Central orchestration of the flow

---

## 4. The Solution: Deterministic Workflow Orchestration

### 4.1 SDK Documentation on Deterministic Flows

From OpenAI Agents SDK `multi_agent.md`:

> "While orchestrating via LLM is powerful, **orchestrating via code makes tasks more deterministic and predictable**, in terms of speed, cost and performance. Common patterns here are:
> - **Chaining multiple agents** by transforming the output of one into the input of the next."

From `agent_patterns/README.md`:

> "A common tactic is to **break down a task into a series of smaller steps**. Each task can be performed by an agent, and the **output of one agent is used as input to the next**."

### 4.2 Deterministic Flow Pattern

```python
# DETERMINISTIC ORCHESTRATION (Recommended)
async def run_forecast_workflow(params):
    # Step 1: Run demand forecast
    demand_result = await Runner.run(demand_agent, params.to_prompt())
    forecast: ForecastResult = demand_result.final_output_as(ForecastResult)

    # Step 2: Run inventory allocation
    inventory_result = await Runner.run(
        inventory_agent,
        f"Allocate inventory based on forecast: {forecast.model_dump_json()}"
    )
    allocation: AllocationResult = inventory_result.final_output_as(AllocationResult)

    # Step 3: Variance checking loop (DETERMINISTIC!)
    while True:
        variance_result = check_variance(
            week_number=params.current_week,
            forecast_by_week=forecast.forecast_by_week,
            actuals=params.actual_sales
        )

        if not variance_result.is_high_variance:
            break  # Exit loop - variance acceptable

        # Re-forecast with updated data
        demand_result = await Runner.run(
            demand_agent,
            f"Re-forecast incorporating actual sales: {params.actual_sales}"
        )
        forecast = demand_result.final_output_as(ForecastResult)

    return WorkflowResult(forecast=forecast, allocation=allocation)
```

### 4.3 Key Benefits of Deterministic Orchestration

| Aspect | Agent-as-Tool | Handoffs | Deterministic |
|--------|---------------|----------|---------------|
| Data Passing | Text only (fragile) | Conversation history | **Pydantic objects (type-safe)** |
| Conditional Logic | LLM decides (unpredictable) | Not possible | **Code-controlled (reliable)** |
| Iteration/Loops | Prompt engineering | Not possible | **Native Python loops** |
| Error Handling | LLM may ignore | Transfers ownership | **try/except (standard)** |
| Debugging | Trace LLM reasoning | Follow handoff chain | **Step-through code** |
| Cost | Multiple LLM calls for orchestration | LLM calls per agent | **Minimal orchestration overhead** |
| Latency | LLM parsing at each step | Each handoff is LLM call | **Direct function calls** |

### 4.4 Why This Solves the Variance Problem

```python
# Variance-triggered re-forecasting with deterministic control
async def variance_checking_loop(
    forecast: ForecastResult,
    actual_sales: pd.DataFrame,
    variance_threshold: float = 0.15,
    max_iterations: int = 3
) -> ForecastResult:
    """
    Deterministic loop that re-forecasts if variance exceeds threshold.

    This is IMPOSSIBLE to implement reliably with agent-as-tool or handoffs
    because:
    1. We need to pass Pydantic ForecastResult between iterations
    2. We need conditional exit based on variance calculation
    3. We need iteration count to prevent infinite loops
    """

    for iteration in range(max_iterations):
        # Check variance (deterministic calculation)
        variance = calculate_variance(forecast.forecast_by_week, actual_sales)

        if abs(variance) <= variance_threshold:
            logger.info(f"Variance {variance:.1%} within threshold - exiting loop")
            return forecast  # DETERMINISTIC EXIT

        logger.warning(f"Iteration {iteration+1}: Variance {variance:.1%} exceeds threshold")

        # Re-forecast (agent call, but orchestration is code-controlled)
        result = await Runner.run(
            demand_agent,
            input=f"Re-forecast incorporating week {iteration+1} actuals"
        )
        forecast = result.final_output_as(ForecastResult)  # TYPE-SAFE!

    logger.error(f"Max iterations reached - returning best forecast")
    return forecast
```

---

## 5. Guardrails Implementation

### 5.1 Current Guardrail (Output Validation)

From `guardrails/demand_guardrails.py`:

```python
@output_guardrail
async def validate_forecast_output(
    ctx: RunContextWrapper,
    agent: Agent,
    output: ForecastResult
) -> GuardrailFunctionOutput:
    """
    Validate forecast output data integrity.
    """
    issues: List[str] = []

    # 1. Confidence Range
    if not (0.0 <= output.confidence <= 1.0):
        issues.append(f"Confidence {output.confidence:.3f} out of range")

    # 2. Safety Stock Range
    if not (0.1 <= output.safety_stock_pct <= 0.5):
        issues.append(f"Safety stock {output.safety_stock_pct:.2%} out of range")

    # 3. Unit Conservation
    if sum(output.forecast_by_week) != output.total_demand:
        issues.append("Unit conservation violated")

    return GuardrailFunctionOutput(
        tripwire_triggered=len(issues) > 0,
        output_info={"validation_errors": issues}
    )
```

### 5.2 Problem: Guardrails Only Work with `output_type`

The current guardrail **cannot work** with the agent-as-tool pattern because:

1. Output guardrails require `output_type` to be set on the agent:
   ```python
   agent = Agent(
       output_type=ForecastResult,  # Required for output guardrails
       output_guardrails=[validate_forecast_output]
   )
   ```

2. But `output_type` breaks `as_tool()`:
   ```python
   # From demand_agent.py comment:
   # NOTE: Do NOT use output_type when agent is used with .as_tool()
   ```

This is a fundamental incompatibility.

### 5.3 Guardrails in Deterministic Architecture

With deterministic orchestration, guardrails can be properly implemented:

```python
# demand_agent.py - WITH output_type (enabled by deterministic architecture)
demand_agent = Agent(
    name="Demand Forecasting Agent",
    instructions="...",
    model=OPENAI_MODEL,
    output_type=ForecastResult,  # NOW POSSIBLE!
    output_guardrails=[validate_forecast_output],  # NOW WORKS!
    tools=[run_demand_forecast]
)

# orchestrator.py - Direct agent calls (not as_tool)
async def run_demand_forecast_step(params) -> ForecastResult:
    try:
        result = await Runner.run(demand_agent, params.to_prompt())
        return result.final_output_as(ForecastResult)  # Type-safe!
    except OutputGuardrailTripwireTriggered as e:
        # Handle validation failure deterministically
        logger.error(f"Forecast validation failed: {e.guardrail_result.output_info}")
        raise ForecastValidationError(e.guardrail_result.output_info)
```

### 5.4 Complete Guardrails Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT GUARDRAILS                              │
│  - Validate user parameters before forecasting                   │
│  - Check category exists in data                                 │
│  - Validate date ranges                                          │
│  - Reject malicious/nonsensical inputs                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DEMAND AGENT                                  │
│  output_type=ForecastResult                                      │
│  output_guardrails=[validate_forecast_output]                    │
│  - Confidence in [0.0, 1.0]                                      │
│  - Safety stock in [0.1, 0.5]                                    │
│  - Unit conservation (sum = total)                               │
│  - No negative predictions                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INVENTORY AGENT                               │
│  output_type=AllocationResult                                    │
│  output_guardrails=[validate_allocation_output]                  │
│  - Unit conservation (manufacturing = DC + stores)               │
│  - No negative allocations                                       │
│  - All stores receive allocation                                 │
│  - Cluster percentages sum to 100%                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VARIANCE GUARDRAILS                           │
│  (Implemented as deterministic code, not LLM guardrails)         │
│  - Variance calculation is mathematical                          │
│  - Threshold comparison is boolean                               │
│  - Re-forecast trigger is conditional code                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Recommended Architecture

### 6.1 New Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                DETERMINISTIC WORKFLOW ORCHESTRATOR               │
│                     (Python Code Control)                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  async def run_workflow(params: WorkflowParams):         │   │
│  │      # Step 1: Demand Forecasting                        │   │
│  │      forecast = await run_demand_step(params)            │   │
│  │                                                          │   │
│  │      # Step 2: Inventory Allocation                      │   │
│  │      allocation = await run_allocation_step(forecast)    │   │
│  │                                                          │   │
│  │      # Step 3: Variance Loop (deterministic!)            │   │
│  │      while has_new_actuals():                            │   │
│  │          variance = check_variance(forecast, actuals)    │   │
│  │          if variance.is_high:                            │   │
│  │              forecast = await run_demand_step(params)    │   │
│  │              allocation = await run_allocation_step(...)│   │
│  │                                                          │   │
│  │      return WorkflowResult(forecast, allocation)         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌─────────────────────┐            ┌─────────────────────────┐
│   Demand Agent      │            │   Inventory Agent        │
│   output_type=      │            │   output_type=           │
│   ForecastResult    │            │   AllocationResult       │
│                     │            │                          │
│   output_guardrails │            │   output_guardrails      │
│   =[validate_       │            │   =[validate_            │
│     forecast]       │            │     allocation]          │
└─────────────────────┘            └─────────────────────────┘
```

### 6.2 Code Structure

```
backend/
├── workflows/
│   ├── __init__.py
│   ├── forecast_workflow.py      # Main workflow orchestrator
│   ├── variance_loop.py          # Variance checking + re-forecast logic
│   └── workflow_types.py         # WorkflowParams, WorkflowResult
│
├── my_agents/
│   ├── demand_agent.py           # With output_type=ForecastResult
│   └── inventory_agent.py        # With output_type=AllocationResult
│
├── agent_tools/                   # UNCHANGED - Tools stay where they are
│   ├── __init__.py
│   ├── demand_tools.py           # run_demand_forecast(), ForecastResult
│   ├── inventory_tools.py        # cluster_stores(), allocate_inventory()
│   └── variance_tools.py         # check_variance() - called DIRECTLY by workflow
│
├── guardrails/
│   ├── demand_guardrails.py      # Output validation for forecasts
│   ├── inventory_guardrails.py   # Output validation for allocations
│   └── input_guardrails.py       # Parameter validation
│
└── streamlit_app.py              # UI (unchanged, but receives typed data)
```

**Key insight on tools:**
| Tool | Called By | Why |
|------|-----------|-----|
| `run_demand_forecast` | demand_agent | Needs LLM reasoning about data quality |
| `cluster_stores` | inventory_agent | Needs LLM interpretation of clusters |
| `allocate_inventory` | inventory_agent | Needs LLM reasoning about factors |
| `check_variance` | **workflow directly** | Pure math - no LLM needed |

### 6.3 Key Implementation Changes

#### 6.3.1 Demand Agent (with output_type)

```python
# my_agents/demand_agent.py
from agents import Agent
from agent_tools.demand_tools import run_demand_forecast, ForecastResult
from guardrails.demand_guardrails import validate_forecast_output

demand_agent = Agent(
    name="Demand Forecasting Agent",
    instructions="...",  # Simplified - just format results
    model=OPENAI_MODEL,
    output_type=ForecastResult,  # NOW ENABLED!
    output_guardrails=[validate_forecast_output],
    tools=[run_demand_forecast]
)
```

#### 6.3.2 Workflow Orchestrator

```python
# workflows/forecast_workflow.py
from agents import Runner
from my_agents.demand_agent import demand_agent
from my_agents.inventory_agent import inventory_agent
from workflows.variance_loop import variance_checking_loop
from workflows.workflow_types import WorkflowParams, WorkflowResult

async def run_forecast_workflow(params: WorkflowParams) -> WorkflowResult:
    """
    Deterministic workflow orchestration.

    This replaces the LLM-based coordinator with code-controlled flow.
    """

    # Step 1: Generate demand forecast
    forecast = await run_demand_step(
        category=params.category,
        horizon_weeks=params.forecast_horizon_weeks
    )

    # Step 2: Allocate inventory
    allocation = await run_allocation_step(
        forecast=forecast,
        dc_holdback_pct=params.dc_holdback_percentage,
        replenishment_strategy=params.replenishment_strategy
    )

    # Step 3: Variance loop (when actuals are available)
    if params.actual_sales is not None:
        forecast = await variance_checking_loop(
            forecast=forecast,
            actual_sales=params.actual_sales,
            variance_threshold=params.variance_threshold
        )

        # Re-allocate with updated forecast
        allocation = await run_allocation_step(
            forecast=forecast,
            dc_holdback_pct=params.dc_holdback_percentage,
            replenishment_strategy=params.replenishment_strategy
        )

    return WorkflowResult(
        forecast=forecast,
        allocation=allocation,
        params=params
    )


async def run_demand_step(category: str, horizon_weeks: int) -> ForecastResult:
    """Run demand agent and return typed ForecastResult."""
    result = await Runner.run(
        demand_agent,
        f"Generate demand forecast for {category} over {horizon_weeks} weeks"
    )
    return result.final_output_as(ForecastResult)


async def run_allocation_step(
    forecast: ForecastResult,
    dc_holdback_pct: float,
    replenishment_strategy: str
) -> AllocationResult:
    """Run inventory agent and return typed AllocationResult."""
    result = await Runner.run(
        inventory_agent,
        f"Allocate inventory. Forecast: {forecast.model_dump_json()}. "
        f"DC holdback: {dc_holdback_pct}, Strategy: {replenishment_strategy}"
    )
    return result.final_output_as(AllocationResult)
```

#### 6.3.3 Variance Loop

```python
# workflows/variance_loop.py
async def variance_checking_loop(
    forecast: ForecastResult,
    actual_sales: pd.DataFrame,
    variance_threshold: float = 0.15,
    max_iterations: int = 3
) -> ForecastResult:
    """
    Deterministic variance checking with re-forecasting.

    This is the logic that CANNOT be reliably implemented with:
    - agent-as-tool (text-only, no type safety)
    - handoffs (no return semantics)
    """

    for iteration in range(max_iterations):
        variance = calculate_variance(
            forecast.forecast_by_week,
            actual_sales
        )

        if abs(variance.variance_pct) <= variance_threshold:
            logger.info(
                f"Variance {variance.variance_pct:.1%} acceptable "
                f"after {iteration} re-forecasts"
            )
            return forecast

        logger.warning(
            f"Iteration {iteration+1}: "
            f"Variance {variance.variance_pct:.1%} > {variance_threshold:.1%}"
        )

        # Re-forecast with actual data
        forecast = await run_demand_step_with_actuals(
            category=forecast.category,
            horizon_weeks=len(forecast.forecast_by_week),
            actual_sales=actual_sales
        )

    logger.error("Max iterations reached")
    return forecast
```

---

## 7. Implementation Roadmap

### Phase 1: Enable output_type on Agents

1. Remove `# NOTE: Do NOT use output_type` comments
2. Add `output_type=ForecastResult` to demand_agent
3. Add `output_type=AllocationResult` to inventory_agent
4. Test that guardrails now work correctly

### Phase 2: Create Workflow Orchestrator

1. Create `workflows/` directory
2. Implement `forecast_workflow.py` with deterministic control
3. Implement `variance_loop.py` with iteration logic
4. Create `workflow_types.py` for shared types

### Phase 3: Update Streamlit App

1. Replace `Runner.run(coordinator_agent, ...)` with `run_forecast_workflow(...)`
2. Remove text parsing fallbacks (data is now typed)
3. Update visualization hooks to use typed data directly

### Phase 4: Remove Coordinator Agent

1. Delete `coordinator_agent.py` (no longer needed)
2. Clean up `agent.as_tool()` usage
3. Update imports and tests

### Phase 5: Enhanced Guardrails

1. Add input guardrails for parameter validation
2. Add inventory allocation guardrails
3. Add variance calculation guardrails (sanity checks)

---

## Summary

| Approach | Pydantic Support | Conditional Logic | Iteration | Guardrails | Recommendation |
|----------|------------------|-------------------|-----------|------------|----------------|
| Agent-as-Tool | ❌ Text only | ⚠️ LLM decides | ⚠️ Fragile | ❌ Incompatible | Not for complex flows |
| Handoffs | ❌ Conversation | ❌ One-way | ❌ No return | ⚠️ Per-agent | Not for loops |
| **Deterministic** | ✅ Native | ✅ Code control | ✅ Python loops | ✅ Full support | **Recommended** |

**Conclusion**: The variance-triggered re-forecasting requirement fundamentally needs:
- Type-safe data passing (ForecastResult, AllocationResult)
- Conditional branching (if variance > threshold)
- Iteration (re-forecast until acceptable)
- Error handling (guardrail tripwires)

Only **deterministic workflow orchestration** provides all of these reliably. The current agent-as-tool architecture should be refactored to use direct `Runner.run()` calls with `output_type` enabled, orchestrated by Python code rather than LLM instructions.
