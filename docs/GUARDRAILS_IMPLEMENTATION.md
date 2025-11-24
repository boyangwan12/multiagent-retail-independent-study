# Guardrails Implementation Guide

## Overview

This document explains the output guardrail implementation for the OpenAI Agents SDK-based retail forecasting system. Guardrails enforce data integrity contracts **before** agent outputs reach the UI, preventing invalid or hallucinated data from breaking visualizations or business logic.

## Architecture

### 3-Layer Validation Strategy

1. **Layer 1: Tool Input Validation** (in `agent_tools/demand_tools.py`)
   - Validates function parameters before execution
   - Example: Check `forecast_horizon_weeks > 0`, category exists in data

2. **Layer 2: Agent Output Guardrails** (in `guardrails/demand_guardrails.py`)
   - Validates agent output structure and business rules
   - **Runs BEFORE** data reaches UI
   - Triggers exception if validation fails

3. **Layer 3: UI Validation** (in `streamlit_app.py`)
   - Error boundaries around visualization functions
   - Graceful degradation with fallback parsing
   - User-friendly error messages

## Output Guardrail Pattern

### When to Use Output Guardrails

Use output guardrails when:
- Agent returns **structured data** that downstream systems depend on
- Business rules must be **mathematically enforced** (e.g., unit conservation)
- Invalid data would **break visualizations** or cause errors
- You need to **prevent hallucinations** in numeric fields

**DO NOT use guardrails for:**
- Conversational text quality (use instructions instead)
- Simple input validation (use tool parameter validation)
- Performance optimization (not their purpose)

### Implementation Pattern

```python
from agents import output_guardrail, GuardrailFunctionOutput, RunContextWrapper, Agent
from typing import List

@output_guardrail
async def validate_forecast_output(
    ctx: RunContextWrapper,
    agent: Agent,
    output: ForecastResult  # Your Pydantic model
) -> GuardrailFunctionOutput:
    """
    Validate agent output before it reaches the UI.

    Returns:
        GuardrailFunctionOutput with tripwire_triggered=True if validation fails
    """
    issues: List[str] = []

    # Validation 1: Range checks
    if not (0.0 <= output.confidence <= 1.0):
        issues.append(f"Confidence {output.confidence} out of range [0.0, 1.0]")

    # Validation 2: Business rules
    if not (0.1 <= output.safety_stock_pct <= 0.5):
        issues.append(f"Safety stock {output.safety_stock_pct} out of range [10%, 50%]")

    # Validation 3: Mathematical integrity
    calculated_sum = sum(output.forecast_by_week)
    if calculated_sum != output.total_demand:
        issues.append(f"Unit conservation violated: {calculated_sum} ≠ {output.total_demand}")

    # Validation 4: No invalid values
    negative_weeks = [i+1 for i, x in enumerate(output.forecast_by_week) if x < 0]
    if negative_weeks:
        issues.append(f"Negative predictions in weeks: {negative_weeks}")

    return GuardrailFunctionOutput(
        tripwire_triggered=len(issues) > 0,
        output_info={
            "validation_errors": issues,
            "data_summary": {"total_demand": output.total_demand, ...}
        }
    )
```

## Demand Forecasting Guardrail

### File: `guardrails/demand_guardrails.py`

**Validations Enforced:**

1. **Confidence Range**: Must be in [0.0, 1.0]
   - Prevents math errors in safety stock calculation
   - Formula: `safety_stock = 1.0 - confidence`

2. **Safety Stock Range**: Must be in [0.1, 0.5] (10-50%)
   - Business rule for fashion retail
   - Too low = stockouts, too high = excess inventory

3. **Unit Conservation**: `sum(forecast_by_week) == total_demand`
   - Mathematical integrity check
   - Prevents allocation errors downstream

4. **No Negative Predictions**: All weekly forecasts >= 0
   - Cannot allocate negative inventory
   - Flags model errors

5. **Non-Empty Forecasts**: `forecast_by_week` must have data
   - Prevents empty chart rendering
   - Ensures model actually ran

6. **Required Fields Present**: `total_demand`, `model_used` must exist
   - Prevents KeyError in UI
   - Ensures complete results

### Integration with Agent

```python
from agents import Agent
from agent_tools.demand_tools import ForecastResult
from guardrails.demand_guardrails import validate_forecast_output

demand_agent = Agent(
    name="Demand Forecasting Agent",
    output_type=ForecastResult,  # REQUIRED: Structured output schema
    output_guardrails=[validate_forecast_output],  # ENFORCED: Before output reaches UI
    instructions="...",
    tools=[run_demand_forecast]
)
```

### Exception Handling in UI

```python
from agents import OutputGuardrailTripwireTriggered

try:
    result = Runner.run(coordinator_agent, input_data)
except OutputGuardrailTripwireTriggered as guardrail_error:
    st.error("⚠️ **Data Validation Failed**")

    # Extract validation errors from guardrail
    output_info = guardrail_error.guardrail_result.output_info
    if 'validation_errors' in output_info:
        for error in output_info['validation_errors']:
            st.markdown(f"- {error}")
```

## Critical Pattern: Agents-as-Tools vs output_type

### When NOT to Use output_type

**IMPORTANT**: Do **NOT** use `output_type` on agents that are used with `.as_tool()`.

**Why**: When an agent is converted to a tool via `.as_tool()`, it needs to return a simple serializable value (text). If the agent also has `output_type`, there's a conflict:
- Agent wants to return structured `ForecastResult`
- But as a tool, it must return text for function calling

This causes: `Error: Invalid JSON when parsing...`

### Correct Pattern for Agents-as-Tools

```python
# WRONG ❌ - Don't use output_type with .as_tool()
demand_agent = Agent(
    name="Demand Forecasting Agent",
    output_type=ForecastResult,  # ❌ Causes "Invalid JSON" error
    output_guardrails=[validate_forecast_output],  # ❌ Won't work without output_type
    tools=[run_demand_forecast]
)

coordinator = Agent(
    name="Coordinator",
    tools=[demand_agent.as_tool(tool_name="demand_expert")]  # ❌ Conflict!
)
```

```python
# CORRECT ✅ - Agent returns text, tool validation is automatic
demand_agent = Agent(
    name="Demand Forecasting Agent",
    # No output_type - agent returns conversational text
    # No output_guardrails - Pydantic validates tool output automatically
    tools=[run_demand_forecast]  # Tool returns ForecastResult (validated by Pydantic)
)

coordinator = Agent(
    name="Coordinator",
    tools=[demand_agent.as_tool(tool_name="demand_expert")]  # ✅ Works!
)
```

### How Validation Works

**3-Layer Architecture:**

1. **Tool Layer** (`run_demand_forecast`):
   - Decorated with `@function_tool`
   - Returns `ForecastResult` (Pydantic model)
   - Pydantic **automatically validates** the return value
   - If validation fails → Pydantic raises ValidationError

2. **Agent Layer** (`demand_agent`):
   - Calls `run_demand_forecast` tool
   - Receives validated `ForecastResult` from tool
   - Formats it as conversational text for user
   - Returns text (not structured data)

3. **Coordinator Layer** (`coordinator_agent`):
   - Calls `demand_agent` via `.as_tool()`
   - Receives text response from demand agent
   - Continues workflow

### Data Capture Strategy

Since hooks don't fire for nested tools (tools called inside agent-as-tool), you have two options:

**Option A: Parse from Agent Text** (Current Approach)
```python
async def on_tool_end(self, ctx, agent, tool, output):
    if tool.name == 'demand_forecasting_expert':
        # Output is text - parse numbers from it
        import re
        total_match = re.search(r'Total Demand.*?(\d+,?\d*)\s+units', output)
        # Store parsed data
```

**Option B: Return Structured Data from Agent** (Requires Different Pattern)
- Don't use `.as_tool()` - use handoffs or direct agent calls
- Then you can use `output_type` on the agent
- Hooks will fire and capture structured data

**Recommendation**: Stick with Option A (text parsing) since you're already using agents-as-tools pattern. The Pydantic validation at the tool level ensures data integrity even if you're parsing text at the hook level.

### Pydantic Schema Configuration

**CRITICAL**: OpenAI Agents SDK requires **strict schemas** - you CANNOT use `extra='allow'`.

All fields must be explicitly defined:

```python
from pydantic import BaseModel, Field, ConfigDict

class ForecastResult(BaseModel):
    # SDK REQUIREMENT: Must use extra='forbid' (strict schema)
    # All possible fields must be explicitly declared
    model_config = ConfigDict(extra='forbid')

    # REQUIRED CORE FIELDS (validated by guardrail)
    total_demand: int = Field(description="Sum of all weekly forecasts")
    forecast_by_week: List[int] = Field(description="Weekly demand predictions")
    safety_stock_pct: float = Field(description="Safety stock (0.10 to 0.50)")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    model_used: str = Field(description="Which model(s) were used")

    # OPTIONAL FIELDS (confidence intervals)
    lower_bound: List[int] = Field(default_factory=list)
    upper_bound: List[int] = Field(default_factory=list)

    # OPTIONAL FIELDS (UI enhancements - must be explicit!)
    weekly_average: Optional[float] = Field(default=None, description="Average weekly demand")
    data_quality: Optional[str] = Field(default=None, description="'Excellent', 'Good', or 'Fair'")
    summary: Optional[str] = Field(default=None, description="Markdown summary for UI")

    # OPTIONAL FIELDS (error handling)
    error: Optional[str] = Field(default=None, description="Error message if failed")
```

**Why `extra='forbid'`?**
- The OpenAI Agents SDK requires strict JSON schemas for function calling
- Using `extra='allow'` causes: `UserError: additionalProperties should not be set`
- Solution: Explicitly define ALL optional fields the agent might populate
- Guardrail validates **required** fields, optional fields can be None

## Testing Guardrails

### Successful Validation

**Console Output**:
```
✅ [DEMAND GUARDRAIL] Validation PASSED
[GUARDRAIL] Forecast data integrity confirmed:
  - Total Demand: 17,554 units
  - Confidence: 55.0%
  - Safety Stock: 45.0%
  - Horizon: 12 weeks
  - Model: prophet_arima_ensemble
```

**UI Behavior**:
- Full forecast dashboard displays
- Charts render correctly
- No fallback warnings

### Failed Validation

**Console Output**:
```
❌ [DEMAND GUARDRAIL] Validation FAILED - blocking invalid forecast
[GUARDRAIL] Issues found (2):
  1. Confidence 1.5 is out of valid range [0.0, 1.0]
  2. Unit conservation violated: sum (15000) ≠ total_demand (17554)
[GUARDRAIL] Tripwire TRIGGERED - OutputGuardrailTripwireTriggered will be raised
```

**UI Behavior**:
- Shows "⚠️ Data Validation Failed" error
- Lists specific issues found
- Prevents broken visualizations
- User sees helpful error instead of crash

## Common Issues & Solutions

### Issue 1: "additionalProperties should not be set for object types"

**Symptom**:
```
agents.exceptions.UserError: additionalProperties should not be set for object types.
This could be because you're using an older version of Pydantic, or because you
configured additional properties to be allowed.
```

**Cause**: Pydantic schema has `extra='allow'` which the OpenAI Agents SDK doesn't support

**Fix**:
1. Change to `model_config = ConfigDict(extra='forbid')`
2. Explicitly define ALL optional fields in your schema:
```python
# WRONG (SDK doesn't support this)
model_config = ConfigDict(extra='allow')

# CORRECT (explicitly define all fields)
model_config = ConfigDict(extra='forbid')
weekly_average: Optional[float] = Field(default=None)
data_quality: Optional[str] = Field(default=None)
```

### Issue 2: Guardrail Not Firing

**Symptom**: Invalid data reaches UI without triggering guardrail

**Cause**: Agent not configured with `output_type`

**Fix**: Add `output_type=YourPydanticModel` to Agent constructor

### Issue 3: "Invalid JSON when parsing" (misleading error)

**Symptom**: Console shows `Error: Invalid JSON when parsing {"total_demand":17554,...`

**Cause**: This is actually a Pydantic validation error, not a JSON parsing error. The agent returned valid JSON but with fields not in the schema (when using `extra='forbid'`)

**Fix**: Add the missing fields as Optional in your schema

### Issue 4: Hook Not Capturing Data

**Symptom**: `on_agent_end` fires but `final_output_as()` returns None

**Cause**: Agent-as-tool pattern - hooks fire at coordinator level only

**Fix**: Use `output_type` pattern instead of relying on tool hooks

## Decision: Instructions vs Guardrails

### When to Use Instructions

Use instructions when:
- Guiding agent **reasoning** and **decision-making**
- Explaining **why** to do something
- Providing **examples** and **context**
- Defining **workflow steps**

Example:
```python
instructions="""
## SAFETY STOCK CALCULATION

Calculate safety stock using: safety_stock_pct = 1.0 - confidence

Guidelines:
- High confidence (0.8-1.0) → Low safety stock (10-20%)
- Medium confidence (0.6-0.79) → Moderate safety stock (21-40%)
"""
```

### When to Use Guardrails

Use guardrails when:
- Enforcing **mathematical constraints** (cannot be violated)
- Validating **data structure** (required fields, types)
- Preventing **downstream errors** (negative values, empty arrays)
- Enforcing **business rules** (ranges, limits)

Example:
```python
@output_guardrail
async def validate_forecast_output(...):
    # ENFORCEMENT: This MUST be true
    if not (0.1 <= output.safety_stock_pct <= 0.5):
        issues.append("Safety stock out of range")
```

### The Key Difference

**Instructions**: "You *should* do X because Y"
- Agent can ignore (if confused or hallucinating)
- Soft guidance

**Guardrails**: "X *must* be true or I block the output"
- Agent cannot bypass (enforced by SDK)
- Hard constraint

## Future Guardrails

### Inventory Allocation Guardrail (Pending)

```python
@output_guardrail
async def validate_allocation_output(ctx, agent, output: AllocationResult):
    issues = []

    # Unit conservation: allocations sum to manufactured quantity
    total_allocated = sum(output.allocations_by_store.values())
    if total_allocated != output.manufactured_quantity:
        issues.append(f"Allocation mismatch: {total_allocated} ≠ {output.manufactured_quantity}")

    # No negative allocations
    negative_stores = [store for store, qty in output.allocations_by_store.items() if qty < 0]
    if negative_stores:
        issues.append(f"Negative allocations for: {negative_stores}")

    # All stores have allocation (even if 0)
    if len(output.allocations_by_store) != output.num_stores:
        issues.append(f"Missing allocations: expected {output.num_stores} stores")

    return GuardrailFunctionOutput(tripwire_triggered=len(issues) > 0, ...)
```

### Variance Check Guardrail (If Needed)

```python
@output_guardrail
async def validate_variance_output(ctx, agent, output: VarianceResult):
    issues = []

    # Variance percentage in valid range
    if not (-1.0 <= output.variance_pct <= 10.0):
        issues.append(f"Variance {output.variance_pct:.1%} out of expected range")

    # Forecast vs actual data lengths match
    if len(output.forecast_data) != len(output.actual_data):
        issues.append("Data length mismatch")

    return GuardrailFunctionOutput(tripwire_triggered=len(issues) > 0, ...)
```

## Best Practices

1. **Log Validation Results**: Always print what passed/failed
2. **Provide Context**: Include actual values in error messages
3. **List All Issues**: Don't stop at first failure, collect all problems
4. **Return Metadata**: Include data summary in output_info for debugging
5. **Test Edge Cases**: Negative values, empty arrays, None fields
6. **Document WHY**: Explain business reason for each validation

## Summary

**Guardrails enforce data contracts that instructions cannot guarantee.**

- Instructions guide the agent's reasoning
- Guardrails validate the agent's output
- Together they create robust, reliable agent systems

**Key Takeaway**: If downstream systems (UI, databases, other agents) depend on data being valid, use an output guardrail to enforce that contract. Don't rely on instructions alone.
