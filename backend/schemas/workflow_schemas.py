"""
Workflow Schemas - Parameters and results for season workflow

These schemas define the inputs and outputs for the full season workflow,
which orchestrates all three agents (demand, inventory, pricing).
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

from .forecast_schemas import ForecastResult
from .allocation_schemas import AllocationResult
from .pricing_schemas import MarkdownResult
from .variance_schemas import VarianceResult


class WorkflowParams(BaseModel):
    """
    Parameters for the season workflow.

    These are extracted from user's natural language description
    or provided directly via the UI.
    """

    # Required parameters
    category: str = Field(
        ...,
        description="Product category to forecast (e.g., 'Women's Dresses')",
    )

    # Forecast parameters
    forecast_horizon_weeks: int = Field(
        default=12,
        description="Number of weeks to forecast",
        ge=1,
        le=52,
    )
    season_start_date: Optional[date] = Field(
        default=None,
        description="Season start date (YYYY-MM-DD)",
    )

    # Inventory parameters
    dc_holdback_pct: float = Field(
        default=0.45,
        description="Percentage to hold at DC for replenishment (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    replenishment_strategy: str = Field(
        default="weekly",
        description="Replenishment strategy: 'none', 'weekly', or 'bi-weekly'",
    )
    safety_stock_pct: float = Field(
        default=0.20,
        description="Safety stock percentage (0.10-0.50)",
        ge=0.10,
        le=0.50,
    )

    # Pricing parameters
    markdown_week: int = Field(
        default=6,
        description="Week to check for markdown (1-12)",
        ge=1,
    )
    markdown_threshold: float = Field(
        default=0.60,
        description="Sell-through threshold to trigger markdown (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    elasticity: float = Field(
        default=2.0,
        description="Price elasticity for markdown calculation",
        ge=0.0,
    )

    # Variance parameters
    variance_threshold: float = Field(
        default=0.20,
        description="Variance threshold to trigger re-forecast (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    max_reforecasts: int = Field(
        default=2,
        description="Maximum number of re-forecasts allowed",
        ge=0,
        le=5,
    )


class SeasonResult(BaseModel):
    """
    Final output from full season workflow.

    Contains all results from each phase:
    1. Demand forecast (with possible re-forecasts)
    2. Inventory allocation
    3. Pricing/markdown (if triggered)
    4. Variance history
    """

    # Phase 1: Forecast
    forecast: ForecastResult = Field(
        ...,
        description="Final demand forecast result",
    )

    # Phase 2: Allocation
    allocation: AllocationResult = Field(
        ...,
        description="Inventory allocation result",
    )

    # Phase 3: Pricing (optional - only if markdown triggered)
    markdown: Optional[MarkdownResult] = Field(
        default=None,
        description="Markdown result (None if no markdown needed)",
    )

    # Variance tracking
    variance_history: List[VarianceResult] = Field(
        default_factory=list,
        description="History of variance checks performed",
    )
    reforecast_count: int = Field(
        default=0,
        description="Number of times re-forecasting was triggered",
        ge=0,
    )

    # Workflow metadata
    total_duration_seconds: Optional[float] = Field(
        default=None,
        description="Total workflow execution time in seconds",
    )
    phases_completed: List[str] = Field(
        default_factory=list,
        description="List of phases completed: ['forecast', 'allocation', 'pricing']",
    )

    @property
    def markdown_applied(self) -> bool:
        """Returns True if markdown was applied."""
        return self.markdown is not None and self.markdown.markdown_needed

    @property
    def had_high_variance(self) -> bool:
        """Returns True if any variance check triggered re-forecast."""
        return any(v.is_high_variance for v in self.variance_history)
