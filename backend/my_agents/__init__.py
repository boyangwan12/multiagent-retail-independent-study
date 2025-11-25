"""
Agents Module

Contains Agent definitions with output_type for structured output.
Each agent has:
- name: Identifier
- instructions: System prompt
- tools: List of @function_tool functions it can call
- output_type: Pydantic model for typed output
- output_guardrails: Validation functions (optional, Phase 5)

Key pattern:
    agent = Agent(
        name="Demand Agent",
        output_type=ForecastResult,  # Enables typed output
    )

    result = await Runner.run(agent, "Forecast women's dresses")
    forecast: ForecastResult = result.final_output  # Typed!

Agent Summary:
    - demand_agent: Prophet + ARIMA forecasting, output_type=ForecastResult
    - inventory_agent: K-means clustering + allocation, output_type=AllocationResult
    - pricing_agent: Gap × Elasticity markdown, output_type=MarkdownResult
"""

# Demand forecasting agent
from my_agents.demand_agent import demand_agent

# Inventory allocation agent
from my_agents.inventory_agent import inventory_agent

# Pricing/markdown agent
from my_agents.pricing_agent import pricing_agent

__all__ = [
    "demand_agent",
    "inventory_agent",
    "pricing_agent",
]
