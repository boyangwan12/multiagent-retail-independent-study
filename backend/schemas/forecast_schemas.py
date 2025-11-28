"""
Forecast Schemas - Structured output for Demand Agent

These Pydantic models define the output_type for the demand forecasting agent.
The SDK automatically enforces these schemas when output_type is set.

SDK Pattern:
    agent = Agent(
        name="Demand Agent",
        output_type=ForecastResult,  # Enables structured output
    )

    result = await Runner.run(agent, "Forecast women's dresses for 12 weeks")
    forecast: ForecastResult = result.final_output  # Typed!
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SeasonalityExplanation(BaseModel):
    """Seasonality data and explanation for forecast transparency."""

    months_covered: List[str] = Field(
        default_factory=list,
        description="Month names in forecast period (e.g., ['August', 'September', 'October'])",
    )
    peak_week: int = Field(
        default=0,
        description="Week number with highest seasonal demand (1-indexed)",
    )
    trough_week: int = Field(
        default=0,
        description="Week number with lowest seasonal demand (1-indexed)",
    )
    seasonal_range_pct: float = Field(
        default=0.0,
        description="Seasonal variation as percentage (e.g., 15.5 means ±15.5% swing)",
    )
    yearly_effects: List[float] = Field(
        default_factory=list,
        description="Yearly seasonality multipliers per week",
    )
    insight: str = Field(
        default="",
        description="Agent-generated natural language explanation of seasonal patterns",
    )


class WeeklyForecast(BaseModel):
    """Forecast data for a single week."""

    week: int = Field(..., description="Week number (1-52)", ge=1, le=52)
    demand: int = Field(..., description="Forecasted demand in units", ge=0)
    lower_bound: Optional[int] = Field(
        None, description="Lower confidence bound (5th percentile)", ge=0
    )
    upper_bound: Optional[int] = Field(
        None, description="Upper confidence bound (95th percentile)", ge=0
    )


class ForecastResult(BaseModel):
    """
    Structured output from Demand Forecasting Agent.

    This is used as output_type on the demand agent, enabling:
    - Typed access via result.final_output
    - Output guardrail validation
    - Direct data passing to inventory workflow

    SDK Note: When output_type is set, the agent MUST return data
    conforming to this schema. The SDK handles JSON parsing automatically.
    """

    total_demand: int = Field(
        ...,
        description="Total forecasted demand in units (sum of all weeks)",
        ge=0,
    )
    forecast_by_week: List[int] = Field(
        ...,
        description="Weekly demand predictions as list of integers",
        min_length=1,
    )
    safety_stock_pct: float = Field(
        ...,
        description="Safety stock percentage (0.10-0.50)",
        ge=0.10,
        le=0.50,
    )
    confidence: float = Field(
        ...,
        description="Forecast confidence score (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    model_used: str = Field(
        ...,
        description="Forecasting model used: 'prophet_arima_ensemble', 'prophet', or 'arima'",
    )
    weekly_average: Optional[int] = Field(
        None,
        description="Average weekly demand in units",
        ge=0,
    )
    lower_bound: List[int] = Field(
        default_factory=list,
        description="Lower confidence bounds per week (5th percentile)",
    )
    upper_bound: List[int] = Field(
        default_factory=list,
        description="Upper confidence bounds per week (95th percentile)",
    )
    data_quality: str = Field(
        default="good",
        description="Data quality assessment: 'excellent', 'good', or 'poor'",
    )
    seasonality: Optional[SeasonalityExplanation] = Field(
        default=None,
        description="Seasonality analysis with data-driven metrics and agent explanation",
    )
    explanation: str = Field(
        ...,
        description="Agent's reasoning about the forecast - why it looks the way it does",
    )

    def model_post_init(self, __context) -> None:
        """Calculate derived fields after initialization."""
        # Calculate weekly average if not provided
        if self.weekly_average is None and self.forecast_by_week:
            object.__setattr__(
                self,
                "weekly_average",
                self.total_demand // len(self.forecast_by_week),
            )
