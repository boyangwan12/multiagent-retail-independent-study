"""
Variance Checking Tools - Pure Functions for Workflow Layer

IMPORTANT: These are NOT agent tools. They are pure functions called directly
by the workflow layer for deterministic variance analysis.

The variance check determines if re-forecasting is needed based on:
- Actual vs forecasted sales comparison
- Threshold-based high variance detection
- Store-level variance breakdown (optional)

Usage in workflow:
    variance = check_variance(
        actual_sales=[500, 480, 520],
        forecast_by_week=[550, 500, 510],
        week_number=3,
        threshold=0.20
    )

    if variance.is_high_variance:
        # Re-forecast needed
        new_forecast = await Runner.run(demand_agent, ...)
"""

# ============================================================================
# SECTION 1: Imports & Models
# ============================================================================

from typing import Dict, List, Optional
import logging

from schemas.variance_schemas import VarianceResult

logger = logging.getLogger("variance_tools")


# ============================================================================
# SECTION 2: Helper Functions
# ============================================================================


def calculate_cumulative_variance(
    actual: List[int], forecast: List[int]
) -> tuple[int, int, int, float]:
    """
    Calculate cumulative variance between actual and forecast.

    Args:
        actual: List of actual sales by week
        forecast: List of forecasted sales by week

    Returns:
        Tuple of (actual_total, forecast_total, variance_units, variance_pct)
    """
    # Calculate totals up to the available data
    weeks_with_data = min(len(actual), len(forecast))

    if weeks_with_data == 0:
        return 0, 0, 0, 0.0

    actual_total = sum(actual[:weeks_with_data])
    forecast_total = sum(forecast[:weeks_with_data])

    variance_units = forecast_total - actual_total

    # Calculate variance percentage
    if forecast_total > 0:
        variance_pct = variance_units / forecast_total
    elif actual_total > 0:
        variance_pct = 1.0 if variance_units > 0 else -1.0
    else:
        variance_pct = 0.0

    return actual_total, forecast_total, variance_units, variance_pct


def determine_variance_direction(variance_pct: float, threshold: float) -> str:
    """
    Determine variance direction: 'over', 'under', or 'on_target'.

    Args:
        variance_pct: Variance as percentage (positive = over-forecast)
        threshold: Threshold for considering variance significant

    Returns:
        'over', 'under', or 'on_target'
    """
    if abs(variance_pct) <= threshold:
        return "on_target"
    elif variance_pct > 0:
        return "over"  # Forecast was higher than actual (over-forecast)
    else:
        return "under"  # Forecast was lower than actual (under-forecast)


def generate_variance_recommendation(
    variance_pct: float,
    direction: str,
    is_high_variance: bool,
    week_number: int,
) -> str:
    """
    Generate human-readable recommendation based on variance analysis.

    Args:
        variance_pct: Variance as percentage
        direction: 'over', 'under', or 'on_target'
        is_high_variance: Whether variance exceeds threshold
        week_number: Current week number

    Returns:
        Recommendation string
    """
    abs_variance = abs(variance_pct) * 100

    if not is_high_variance:
        return (
            f"Week {week_number}: Variance of {abs_variance:.1f}% is within acceptable range. "
            "No action needed - continue with current forecast."
        )

    if direction == "over":
        return (
            f"Week {week_number}: OVER-FORECAST by {abs_variance:.1f}%. "
            "Actual sales are lower than predicted. Consider: "
            "(1) Re-forecast with updated data, "
            "(2) Review inventory levels at DC, "
            "(3) Evaluate markdown strategy to accelerate sales."
        )
    else:  # under
        return (
            f"Week {week_number}: UNDER-FORECAST by {abs_variance:.1f}%. "
            "Actual sales exceed predictions. Consider: "
            "(1) Re-forecast to capture momentum, "
            "(2) Expedite replenishment from DC, "
            "(3) Review store allocations for high-performers."
        )


def calculate_store_level_variance(
    store_actuals: Dict[str, List[int]],
    store_forecasts: Dict[str, List[int]],
    week_number: int,
) -> Dict[str, float]:
    """
    Calculate variance at store level.

    Args:
        store_actuals: Dict of store_id -> list of weekly actuals
        store_forecasts: Dict of store_id -> list of weekly forecasts
        week_number: Number of weeks to analyze

    Returns:
        Dict of store_id -> variance_pct
    """
    store_variance = {}

    for store_id in store_actuals.keys():
        if store_id in store_forecasts:
            actual = store_actuals[store_id][:week_number]
            forecast = store_forecasts[store_id][:week_number]

            actual_sum = sum(actual)
            forecast_sum = sum(forecast)

            if forecast_sum > 0:
                variance_pct = (forecast_sum - actual_sum) / forecast_sum
            elif actual_sum > 0:
                variance_pct = -1.0  # Complete under-forecast
            else:
                variance_pct = 0.0

            store_variance[store_id] = variance_pct

    return store_variance


# ============================================================================
# SECTION 3: Main Variance Check Function (Pure Function - NOT an agent tool)
# ============================================================================


def check_variance(
    actual_sales: List[int],
    forecast_by_week: List[int],
    week_number: int,
    threshold: float = 0.20,
    store_actuals: Optional[Dict[str, List[int]]] = None,
    store_forecasts: Optional[Dict[str, List[int]]] = None,
) -> VarianceResult:
    """
    Check variance between actual sales and forecast.

    THIS IS A PURE FUNCTION - called directly by workflow, NOT by an agent.
    The workflow uses the returned is_high_variance flag to decide whether
    to trigger re-forecasting.

    Formula:
        variance_pct = (forecast_total - actual_total) / forecast_total
        is_high_variance = abs(variance_pct) > threshold

    Args:
        actual_sales: List of actual sales by week (cumulative through current week)
        forecast_by_week: Original forecast by week
        week_number: Current week number being analyzed
        threshold: Variance threshold for triggering re-forecast (default: 0.20 = 20%)
        store_actuals: Optional dict of store_id -> weekly actuals
        store_forecasts: Optional dict of store_id -> weekly forecasts

    Returns:
        VarianceResult with is_high_variance flag for workflow decision

    Example:
        >>> variance = check_variance(
        ...     actual_sales=[500, 480, 520],
        ...     forecast_by_week=[550, 500, 510, 520, 530, 540],
        ...     week_number=3,
        ...     threshold=0.20
        ... )
        >>> if variance.is_high_variance:
        ...     # Trigger re-forecast
        ...     pass
    """
    logger.info("=" * 80)
    logger.info("FUNCTION: check_variance - Variance Analysis")
    logger.info("=" * 80)

    logger.info(
        f"Inputs: week={week_number}, threshold={threshold:.0%}, "
        f"actual_weeks={len(actual_sales)}, forecast_weeks={len(forecast_by_week)}"
    )

    # Calculate cumulative variance
    actual_total, forecast_total, variance_units, variance_pct = calculate_cumulative_variance(
        actual=actual_sales,
        forecast=forecast_by_week[:len(actual_sales)],  # Only compare available weeks
    )

    # Determine if high variance
    is_high_variance = abs(variance_pct) > threshold

    # Determine direction
    direction = determine_variance_direction(variance_pct, threshold)

    # Generate recommendation
    recommendation = generate_variance_recommendation(
        variance_pct=variance_pct,
        direction=direction,
        is_high_variance=is_high_variance,
        week_number=week_number,
    )

    # Calculate store-level variance if provided
    store_level_variance = None
    if store_actuals is not None and store_forecasts is not None:
        store_level_variance = calculate_store_level_variance(
            store_actuals=store_actuals,
            store_forecasts=store_forecasts,
            week_number=week_number,
        )

        # Log stores with high variance
        high_variance_stores = [
            store_id for store_id, var in store_level_variance.items()
            if abs(var) > threshold
        ]
        if high_variance_stores:
            logger.warning(
                f"High variance stores ({len(high_variance_stores)}): "
                f"{high_variance_stores[:5]}..."
            )

    # Build result
    result = VarianceResult(
        week_number=week_number,
        actual_total=actual_total,
        forecast_total=forecast_total,
        variance_units=variance_units,
        variance_pct=variance_pct,
        threshold_pct=threshold,
        is_high_variance=is_high_variance,
        direction=direction,
        store_level_variance=store_level_variance,
        recommendation=recommendation,
    )

    logger.info(
        f"Result: actual={actual_total}, forecast={forecast_total}, "
        f"variance={variance_pct:.1%}, high_variance={is_high_variance}"
    )

    if is_high_variance:
        logger.warning(f"HIGH VARIANCE DETECTED: {direction}-forecast by {abs(variance_pct):.1%}")
    else:
        logger.info(f"Variance within threshold: {direction}")

    return result


def check_weekly_variance(
    actual_week: int,
    forecast_week: int,
    week_number: int,
    threshold: float = 0.20,
) -> VarianceResult:
    """
    Check variance for a single week (simplified version).

    Useful for quick single-week checks without cumulative analysis.

    Args:
        actual_week: Actual sales for the week
        forecast_week: Forecasted sales for the week
        week_number: Week number being analyzed
        threshold: Variance threshold

    Returns:
        VarianceResult for single week
    """
    return check_variance(
        actual_sales=[actual_week],
        forecast_by_week=[forecast_week],
        week_number=week_number,
        threshold=threshold,
    )
