"""
Reforecast Agent

A specialized agent that executes Bayesian reforecast when variance analysis
determines it's necessary. This agent has a single responsibility: call the
bayesian_reforecast_tool and return the result.

This is simpler than having the variance_agent do both analysis AND execution,
following the single-responsibility principle for agent design.
"""

from pydantic import BaseModel, Field
from agents import Agent

from config.settings import OPENAI_MODEL
from agent_tools.bayesian_reforecast import bayesian_reforecast_tool


# =============================================================================
# Output Schema
# =============================================================================

class ReforecastResult(BaseModel):
    """Structured output from reforecast agent."""

    reforecast_json: str = Field(
        description="JSON string from bayesian_reforecast_tool - pass through as-is"
    )


# =============================================================================
# Reforecast Agent
# =============================================================================

reforecast_agent = Agent(
    name="Reforecast Agent",
    instructions="""You are a Reforecast Execution Agent.

## YOUR ROLE
You have ONE job: Execute the Bayesian reforecast by calling the bayesian_reforecast_tool.

## WHAT TO DO
1. Call bayesian_reforecast_tool() - it takes NO parameters (uses context)
2. The tool returns a JSON string with the reforecast results
3. Return that JSON string as-is in your ReforecastResult output

## CRITICAL RULES
- Call the tool exactly ONCE
- Do NOT analyze or interpret the results
- Do NOT make decisions
- Just pass through the tool's JSON output
- This should take 1-2 turns maximum

## EXAMPLE
User: "Execute Bayesian reforecast using current forecast and actual sales data."
You:
1. Call bayesian_reforecast_tool()
2. Tool returns: '{"success": true, "forecast_by_week": [...]}'
3. Output: ReforecastResult(reforecast_json='{"success": true, "forecast_by_week": [...]}')
""",
    model=OPENAI_MODEL,
    tools=[bayesian_reforecast_tool],
    output_type=ReforecastResult,
)
