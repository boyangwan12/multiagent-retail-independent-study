"""
Agent Tools Module

Contains @function_tool decorated functions that agents can call.
Tools perform actual computation and return Pydantic models.

Key insight: Tools are called BY agents (via LLM tool calls),
EXCEPT for variance_tools which is called DIRECTLY by the workflow.

Tool Summary:
    - run_demand_forecast: Prophet + ARIMA ensemble forecasting
    - cluster_stores: K-means store segmentation
    - allocate_inventory: Hierarchical inventory allocation
    - calculate_markdown: Gap × Elasticity markdown calculation
    - check_variance: Pure function for variance analysis (workflow-level)
"""

# Demand forecasting tool
from agent_tools.demand_tools import (
    run_demand_forecast,
    ForecastToolResult,
)

# Inventory allocation tools
from agent_tools.inventory_tools import (
    cluster_stores,
    allocate_inventory,
    ClusteringToolResult,
    AllocationToolResult,
    ClusterStats,
    ClusterQualityMetrics,
)

# Pricing/markdown tool
from agent_tools.pricing_tools import (
    calculate_markdown,
    MarkdownToolResult,
)

# Variance checking (pure function, NOT an agent tool)
from agent_tools.variance_tools import (
    check_variance,
    check_weekly_variance,
)

__all__ = [
    # Demand tools
    "run_demand_forecast",
    "ForecastToolResult",
    # Inventory tools
    "cluster_stores",
    "allocate_inventory",
    "ClusteringToolResult",
    "AllocationToolResult",
    "ClusterStats",
    "ClusterQualityMetrics",
    # Pricing tools
    "calculate_markdown",
    "MarkdownToolResult",
    # Variance tools (workflow-level)
    "check_variance",
    "check_weekly_variance",
]
