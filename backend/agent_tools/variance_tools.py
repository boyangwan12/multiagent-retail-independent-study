"""
Variance Checking Tools - Compare actual sales vs forecasts

Provides tools for variance analysis to trigger re-forecasting when needed.
"""

import pandas as pd
from typing import Dict, Any
from pydantic import BaseModel, Field


class VarianceResult(BaseModel):
    """Result from variance analysis"""
    week_number: int = Field(description="Week number analyzed")
    actual_total: int = Field(description="Total actual sales")
    forecast_total: int = Field(description="Total forecasted sales")
    variance_pct: float = Field(description="Variance percentage (positive = over-forecast, negative = under-forecast)")
    is_high_variance: bool = Field(description="True if variance exceeds threshold (15%)")
    recommendation: str = Field(description="Business recommendation based on variance")
    store_level_variance: Dict[str, float] = Field(description="Variance by store ID")


def check_variance(
    actual_sales_csv: str,
    forecast_by_week: list,
    week_number: int,
    variance_threshold: float = 0.15
) -> VarianceResult:
    """
    Compare actual sales against forecast for a specific week.

    Args:
        actual_sales_csv: Path to CSV file with columns: date, store_id, quantity_sold
        forecast_by_week: List of forecasted units per week from demand forecast
        week_number: Which week to check (1-indexed)
        variance_threshold: Threshold for triggering re-forecast (default 15%)

    Returns:
        VarianceResult with comparison metrics and recommendation
    """
    # Load actual sales
    df_actuals = pd.read_csv(actual_sales_csv)

    # Calculate total actual sales
    actual_total = df_actuals['quantity_sold'].sum()

    # Get forecasted amount for this week
    if week_number < 1 or week_number > len(forecast_by_week):
        raise ValueError(f"Week number {week_number} out of range (1-{len(forecast_by_week)})")

    forecast_total = forecast_by_week[week_number - 1]  # 0-indexed

    # Calculate variance
    variance_pct = (forecast_total - actual_total) / actual_total if actual_total > 0 else 0.0

    # Check if high variance
    is_high_variance = abs(variance_pct) > variance_threshold

    # Store-level variance
    store_variance = {}
    for _, row in df_actuals.iterrows():
        store_id = row['store_id']
        actual = row['quantity_sold']
        # Approximate per-store forecast (this could be improved with actual store-level forecasts)
        avg_forecast_per_store = forecast_total / len(df_actuals)
        store_var = (avg_forecast_per_store - actual) / actual if actual > 0 else 0.0
        store_variance[store_id] = round(store_var, 3)

    # Generate recommendation
    if is_high_variance:
        if variance_pct > 0:
            recommendation = f"⚠️ Over-forecasted by {abs(variance_pct)*100:.1f}%. Actual demand is lower than predicted. Consider re-forecasting with updated data to avoid excess inventory."
        else:
            recommendation = f"⚠️ Under-forecasted by {abs(variance_pct)*100:.1f}%. Actual demand is higher than predicted. Consider re-forecasting and increasing safety stock to prevent stock-outs."
    else:
        recommendation = f"✅ Variance is within acceptable range ({abs(variance_pct)*100:.1f}%). Forecast accuracy is good. Continue with current plan."

    return VarianceResult(
        week_number=week_number,
        actual_total=actual_total,
        forecast_total=forecast_total,
        variance_pct=round(variance_pct, 4),
        is_high_variance=is_high_variance,
        recommendation=recommendation,
        store_level_variance=store_variance
    )


def calculate_mape(actuals: list, forecasts: list) -> float:
    """
    Calculate Mean Absolute Percentage Error (MAPE).

    Args:
        actuals: List of actual sales values
        forecasts: List of forecasted values

    Returns:
        MAPE as a percentage (0-100)
    """
    if len(actuals) != len(forecasts):
        raise ValueError("Actuals and forecasts must have same length")

    absolute_percentage_errors = []
    for actual, forecast in zip(actuals, forecasts):
        if actual > 0:
            ape = abs((actual - forecast) / actual)
            absolute_percentage_errors.append(ape)

    if len(absolute_percentage_errors) == 0:
        return 0.0

    mape = sum(absolute_percentage_errors) / len(absolute_percentage_errors) * 100
    return round(mape, 2)
