"""
Variance Schemas - Output from variance checking

NOTE: Variance checking is called DIRECTLY by the workflow layer,
not by an agent. This is deterministic logic - pure math with no LLM reasoning needed.

The workflow uses is_high_variance to decide whether to re-forecast.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional


class VarianceResult(BaseModel):
    """
    Output from variance checking.

    This is NOT an agent output_type - it's returned by a pure function
    called directly by the workflow layer.

    The workflow checks is_high_variance to decide if re-forecasting is needed:

        variance = check_variance(actual_sales, forecast_by_week, week, threshold)
        if variance.is_high_variance:
            # Deterministic decision: re-forecast
            forecast = await run_forecast_again(...)
    """

    week_number: int = Field(
        ...,
        description="Week number being analyzed",
        ge=1,
    )
    actual_total: int = Field(
        ...,
        description="Total actual sales in units",
        ge=0,
    )
    forecast_total: int = Field(
        ...,
        description="Total forecasted sales in units",
        ge=0,
    )
    variance_units: int = Field(
        ...,
        description="Variance in units (forecast - actual)",
    )
    variance_pct: float = Field(
        ...,
        description="Variance as percentage (positive = over-forecast, negative = under-forecast)",
    )
    threshold_pct: float = Field(
        ...,
        description="Threshold used for high variance detection",
        ge=0.0,
        le=1.0,
    )
    is_high_variance: bool = Field(
        ...,
        description="True if abs(variance_pct) > threshold_pct - WORKFLOW USES THIS DIRECTLY",
    )
    direction: str = Field(
        ...,
        description="'over' if forecast > actual, 'under' if forecast < actual, 'on_target' if within threshold",
    )
    store_level_variance: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional variance breakdown by store ID",
    )
    recommendation: str = Field(
        ...,
        description="Human-readable recommendation based on variance",
    )

    @property
    def needs_reforecast(self) -> bool:
        """Alias for is_high_variance for clearer workflow code."""
        return self.is_high_variance
