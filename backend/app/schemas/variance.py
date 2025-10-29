"""Variance Analysis Schemas"""

from pydantic import BaseModel, Field


class VarianceAnalysisDetail(BaseModel):
    """Variance analysis between forecast and actuals."""

    forecast_id: str
    week_number: int = Field(..., ge=1, le=52)
    forecasted_cumulative: int = Field(..., ge=0, description="Cumulative forecasted units")
    actual_cumulative: int = Field(..., ge=0, description="Cumulative actual units sold")
    variance_pct: float = Field(..., ge=0.0, le=1.0, description="Variance percentage (0.0-1.0)")
    threshold_exceeded: bool = Field(..., description="True if variance >20%")
    action_taken: str = Field(..., description="'reforecast_triggered' or 'none'")
