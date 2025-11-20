"""
Variance Checking Tools - Compare actual sales vs forecasts

Provides tools for variance analysis to trigger re-forecasting when needed.
"""

import pandas as pd
from typing import Dict, Any
from pydantic import BaseModel, Field
from agents import function_tool, RunContextWrapper
import logging

logger = logging.getLogger(__name__)


class VarianceResult(BaseModel):
    """Result from variance analysis"""
    week_number: int = Field(description="Week number analyzed")
    actual_total: int = Field(description="Total actual sales")
    forecast_total: int = Field(description="Total forecasted sales")
    variance_pct: float = Field(description="Variance percentage (positive = over-forecast, negative = under-forecast)")
    is_high_variance: bool = Field(description="True if variance exceeds threshold (15%)")
    recommendation: str = Field(description="Business recommendation based on variance")
    store_level_variance: Dict[str, float] = Field(description="Variance by store ID")


@function_tool
def check_variance(
    ctx: RunContextWrapper,
    week_number: int,
    variance_threshold: float = 0.15
) -> VarianceResult:
    """
    Compare actual sales against forecast for a specific week to determine if re-forecasting is needed.

    Use this tool when the user uploads actual sales data or wants to check forecast accuracy.
    The tool will analyze variance and recommend re-forecasting if variance exceeds the threshold.

    **IMPORTANT:** This tool accesses data from the context (like other tools). The agent does NOT need to provide:
    - actual_sales_csv path (automatically retrieved from context.variance_file_path)
    - forecast_by_week (automatically retrieved from context.forecast_by_week)

    Args:
        ctx: Run context wrapper (provides access to variance_file_path and forecast_by_week)
        week_number: Which week to check (1-indexed, e.g., 1 for first week, 6 for mid-season)
        variance_threshold: Variance threshold percentage to trigger re-forecast recommendation (default 0.15 = 15%)

    Returns:
        VarianceResult with detailed comparison metrics and business recommendations
    """
    logger.info("=" * 80)
    logger.info("TOOL: check_variance - Variance Analysis")
    logger.info("=" * 80)

    # Get variance data from context (like cluster_stores and run_demand_forecast do)
    try:
        variance_file_path = ctx.context.variance_file_path
        forecast_by_week = ctx.context.forecast_by_week

        if variance_file_path is None:
            raise RuntimeError(
                "Variance file path not found in context. "
                "Please ensure the user has uploaded actual sales data through the UI first."
            )

        if forecast_by_week is None or len(forecast_by_week) == 0:
            raise RuntimeError(
                "Forecast data not found in context. "
                "Please ensure a forecast has been generated before checking variance."
            )

        logger.info(f"Loading actual sales from: {variance_file_path}")
        logger.info(f"Forecast by week: {forecast_by_week}")
        logger.info(f"Checking week: {week_number}")

    except AttributeError as e:
        logger.error("Required data not found in context")
        raise RuntimeError(
            "Variance checking data not available in context. "
            "Ensure the user has uploaded actual sales data and generated a forecast."
        ) from e

    # Load actual sales
    df_actuals = pd.read_csv(variance_file_path)

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

    # Generate recommendation with signal for coordinator
    if is_high_variance:
        if variance_pct > 0:
            # Over-forecasted (actual < forecast)
            recommendation = f"⚠️ Over-forecasted by {abs(variance_pct)*100:.1f}%. Actual demand is lower than predicted. Consider re-forecasting with updated data to avoid excess inventory.\n\n**Action Required:** HIGH_VARIANCE_REFORECAST_NEEDED"
        else:
            # Under-forecasted (actual > forecast)
            recommendation = f"⚠️ Under-forecasted by {abs(variance_pct)*100:.1f}%. Actual demand is higher than predicted. Consider re-forecasting and increasing safety stock to prevent stock-outs.\n\n**Action Required:** HIGH_VARIANCE_REFORECAST_NEEDED"
    else:
        recommendation = f"✅ Variance is within acceptable range ({abs(variance_pct)*100:.1f}%). Forecast accuracy is good. Continue with current plan.\n\n**Status:** No re-forecasting needed."

    result = VarianceResult(
        week_number=week_number,
        actual_total=actual_total,
        forecast_total=forecast_total,
        variance_pct=round(variance_pct, 4),
        is_high_variance=is_high_variance,
        recommendation=recommendation,
        store_level_variance=store_variance
    )

    logger.info(f"Variance check complete: Actual={actual_total}, Forecast={forecast_total}, Variance={variance_pct*100:.1f}%")

    return result


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
