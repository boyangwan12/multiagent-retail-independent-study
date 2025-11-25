"""
Pydantic Schemas for Structured Agent Outputs

These schemas are used as output_type on agents, enabling:
1. Typed responses from Runner.run()
2. Output guardrail validation
3. Reliable data passing between workflow steps
"""

from .forecast_schemas import (
    ForecastResult,
    WeeklyForecast,
)
from .allocation_schemas import (
    AllocationResult,
    ClusterAllocation,
    StoreAllocation,
)
from .pricing_schemas import (
    MarkdownResult,
)
from .variance_schemas import (
    VarianceResult,
)
from .workflow_schemas import (
    WorkflowParams,
    SeasonResult,
)

__all__ = [
    # Forecast
    "ForecastResult",
    "WeeklyForecast",
    # Allocation
    "AllocationResult",
    "ClusterAllocation",
    "StoreAllocation",
    # Pricing
    "MarkdownResult",
    # Variance
    "VarianceResult",
    # Workflow
    "WorkflowParams",
    "SeasonResult",
]
