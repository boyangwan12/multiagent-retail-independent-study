"""
Forecast Workflow - Demand Forecasting with Variance Loop

This workflow orchestrates the demand agent with variance-triggered re-forecasting.

TWO MODES AVAILABLE:
1. DETERMINISTIC (run_forecast_with_variance_loop):
   - Python code controls the loop
   - Variance check is a pure function
   - Fixed threshold-based decisions

2. AGENTIC (run_forecast_with_agentic_variance):
   - Variance Agent analyzes and reasons about variance
   - Agent decides whether to reforecast
   - Considers trends, causes, and remaining season

Usage:
    # Deterministic mode
    forecast, variance_history = await run_forecast_with_variance_loop(...)

    # Agentic mode
    forecast, analysis_history = await run_forecast_with_agentic_variance(...)
"""

import logging
from typing import List, Tuple, Optional, Union

from agents import Runner

from my_agents.demand_agent import demand_agent
from my_agents.variance_agent import variance_agent, VarianceAnalysis
from schemas.forecast_schemas import ForecastResult
from schemas.variance_schemas import VarianceResult
from agent_tools.variance_tools import check_variance
from utils.context import ForecastingContext

logger = logging.getLogger("forecast_workflow")


async def run_forecast(
    context: ForecastingContext,
    category: str,
    forecast_horizon: int,
) -> ForecastResult:
    """
    Run demand forecast without variance checking.

    Simple wrapper for cases where no variance loop is needed
    (e.g., pre-season planning with no actual sales data).

    Args:
        context: ForecastingContext with data_loader
        category: Product category to forecast
        forecast_horizon: Number of weeks to forecast

    Returns:
        ForecastResult with typed forecast data
    """
    logger.info(f"Running forecast for {category}, horizon={forecast_horizon} weeks")

    result = await Runner.run(
        starting_agent=demand_agent,
        input=f"Forecast demand for {category} for {forecast_horizon} weeks",
        context=context,
    )

    forecast: ForecastResult = result.final_output
    logger.info(
        f"Forecast complete: total={forecast.total_demand}, "
        f"confidence={forecast.confidence:.2f}"
    )

    return forecast


async def run_forecast_with_variance_loop(
    context: ForecastingContext,
    category: str,
    forecast_horizon: int,
    variance_threshold: float = 0.20,
    max_reforecasts: int = 2,
) -> Tuple[ForecastResult, List[VarianceResult]]:
    """
    Run demand forecast with automatic variance-triggered re-forecasting.

    This is DETERMINISTIC orchestration:
    - Python code controls the loop (not LLM)
    - Variance check is pure function call (no agent needed)
    - Agent is called via Runner.run() with output_type

    Flow:
    1. Run demand agent → ForecastResult
    2. If no actual sales data → return (pre-season mode)
    3. Check variance (direct function call)
    4. If variance OK → return
    5. If variance high AND reforecast_count < max → re-forecast
    6. Loop until variance acceptable or max reforecasts reached

    Args:
        context: ForecastingContext with data_loader and optional actual_sales
        category: Product category to forecast
        forecast_horizon: Number of weeks to forecast
        variance_threshold: Threshold for high variance (default: 0.20 = 20%)
        max_reforecasts: Maximum re-forecast attempts (default: 2)

    Returns:
        Tuple of (ForecastResult, List[VarianceResult])
    """
    logger.info("=" * 80)
    logger.info("WORKFLOW: Forecast with Variance Loop")
    logger.info(f"Category: {category}, Horizon: {forecast_horizon} weeks")
    logger.info(f"Variance threshold: {variance_threshold:.0%}, Max reforecasts: {max_reforecasts}")
    logger.info("=" * 80)

    variance_history: List[VarianceResult] = []
    reforecast_count = 0
    forecast: Optional[ForecastResult] = None

    while True:
        # Step 1: Run demand agent with output_type
        logger.info(f"Running forecast (attempt {reforecast_count + 1})...")

        result = await Runner.run(
            starting_agent=demand_agent,
            input=f"Forecast demand for {category} for {forecast_horizon} weeks",
            context=context,
        )

        forecast = result.final_output
        logger.info(
            f"Forecast received: total={forecast.total_demand}, "
            f"confidence={forecast.confidence:.2f}, model={forecast.model_used}"
        )

        # Update context with forecast
        context.forecast_by_week = forecast.forecast_by_week

        # Step 2: Check if we have actual sales data to compare
        if not context.has_actual_sales:
            logger.info("No actual sales data - pre-season mode, skipping variance check")
            return forecast, variance_history

        # Step 3: Check variance (DIRECT CALL - no agent)
        logger.info(f"Checking variance at week {context.current_week}...")

        variance = check_variance(
            actual_sales=context.actual_sales,
            forecast_by_week=forecast.forecast_by_week,
            week_number=context.current_week,
            threshold=variance_threshold,
        )
        variance_history.append(variance)

        logger.info(
            f"Variance result: {variance.variance_pct:.1%} ({variance.direction}), "
            f"high_variance={variance.is_high_variance}"
        )

        # Step 4: Deterministic decision
        if not variance.is_high_variance:
            logger.info("Variance acceptable - forecast complete")
            return forecast, variance_history

        if reforecast_count >= max_reforecasts:
            logger.warning(
                f"Max reforecasts ({max_reforecasts}) reached. "
                f"Returning best available forecast with high variance."
            )
            return forecast, variance_history

        # Step 5: Prepare for re-forecast
        logger.info(
            f"High variance detected ({variance.variance_pct:.1%}). "
            f"Triggering re-forecast..."
        )

        # Enrich training data with actual sales if method available
        if hasattr(context, "add_actual_sales_to_history"):
            context.add_actual_sales_to_history()
            logger.info("Added actual sales to training history for re-forecast")

        reforecast_count += 1
        # Loop continues...

    # Should not reach here, but return last forecast if we do
    return forecast, variance_history


async def check_forecast_variance(
    context: ForecastingContext,
    forecast: ForecastResult,
    variance_threshold: float = 0.20,
) -> Optional[VarianceResult]:
    """
    Check variance for an existing forecast.

    Standalone function for checking variance outside the main loop,
    useful for in-season monitoring.

    Args:
        context: ForecastingContext with actual_sales
        forecast: ForecastResult to compare against
        variance_threshold: Threshold for high variance

    Returns:
        VarianceResult or None if no actual sales data
    """
    if not context.has_actual_sales:
        return None

    variance = check_variance(
        actual_sales=context.actual_sales,
        forecast_by_week=forecast.forecast_by_week,
        week_number=context.current_week,
        threshold=variance_threshold,
    )

    return variance


# =============================================================================
# AGENTIC VARIANCE LOOP - Agent decides whether to reforecast
# =============================================================================

async def run_forecast_with_agentic_variance(
    context: ForecastingContext,
    category: str,
    forecast_horizon: int,
    max_reforecasts: int = 2,
) -> Tuple[ForecastResult, List[VarianceAnalysis]]:
    """
    Run demand forecast with AGENTIC variance analysis.

    Unlike the deterministic version, this uses a Variance Analysis Agent
    that reasons about variance patterns and decides whether to reforecast.

    The agent considers:
    - Variance magnitude AND trend
    - Likely causes of variance
    - Remaining season (is reforecast worth it?)
    - Alternative actions (reallocate, markdown)

    Flow:
    1. Run demand agent → ForecastResult
    2. If no actual sales → return (pre-season mode)
    3. Run variance agent → VarianceAnalysis (agent REASONS about variance)
    4. If agent says reforecast AND count < max → re-forecast
    5. Loop until agent says no reforecast or max reached

    Args:
        context: ForecastingContext with data_loader and optional actual_sales
        category: Product category to forecast
        forecast_horizon: Number of weeks to forecast
        max_reforecasts: Maximum re-forecast attempts (default: 2)

    Returns:
        Tuple of (ForecastResult, List[VarianceAnalysis])
    """
    logger.info("=" * 80)
    logger.info("WORKFLOW: Forecast with AGENTIC Variance Analysis")
    logger.info(f"Category: {category}, Horizon: {forecast_horizon} weeks")
    logger.info(f"Max reforecasts: {max_reforecasts}")
    logger.info("=" * 80)

    analysis_history: List[VarianceAnalysis] = []
    reforecast_count = 0
    forecast: Optional[ForecastResult] = None

    while True:
        # Step 1: Run demand agent
        logger.info(f"Running demand forecast (attempt {reforecast_count + 1})...")

        result = await Runner.run(
            starting_agent=demand_agent,
            input=f"Forecast demand for {category} for {forecast_horizon} weeks",
            context=context,
        )

        forecast = result.final_output
        logger.info(
            f"Forecast received: total={forecast.total_demand}, "
            f"confidence={forecast.confidence:.2f}"
        )

        # Update context with forecast
        context.forecast_by_week = forecast.forecast_by_week

        # Step 2: Check if we have actual sales data
        if not context.has_actual_sales:
            logger.info("No actual sales data - pre-season mode, skipping variance analysis")
            return forecast, analysis_history

        # Step 3: Run VARIANCE AGENT (agentic analysis!)
        logger.info(f"Running variance agent analysis at week {context.current_week}...")

        variance_result = await Runner.run(
            starting_agent=variance_agent,
            input=f"Analyze variance for week {context.current_week}. "
                  f"We have {forecast_horizon - context.current_week} weeks remaining in the season. "
                  f"This is reforecast attempt {reforecast_count + 1} of {max_reforecasts + 1}.",
            context=context,
        )

        analysis: VarianceAnalysis = variance_result.final_output
        analysis_history.append(analysis)

        logger.info(f"Variance Agent Analysis:")
        logger.info(f"  - Severity: {analysis.severity}")
        logger.info(f"  - Likely Cause: {analysis.likely_cause}")
        logger.info(f"  - Trend: {analysis.trend_direction}")
        logger.info(f"  - Recommended Action: {analysis.recommended_action}")
        logger.info(f"  - Should Reforecast: {analysis.should_reforecast}")
        logger.info(f"  - Confidence: {analysis.confidence:.0%}")

        # Step 4: Agent decides whether to reforecast
        if not analysis.should_reforecast:
            logger.info(f"Variance agent recommends: {analysis.recommended_action}")
            logger.info("No reforecast needed - returning current forecast")
            return forecast, analysis_history

        if reforecast_count >= max_reforecasts:
            logger.warning(
                f"Max reforecasts ({max_reforecasts}) reached. "
                f"Agent wanted to reforecast but limit hit."
            )
            return forecast, analysis_history

        # Step 5: Agent recommended reforecast - prepare and loop
        logger.info(
            f"Variance agent triggered reforecast. "
            f"Adjustments: {analysis.reforecast_adjustments}"
        )

        # Could pass adjustments to demand agent here in future
        # For now, just re-run with updated context

        reforecast_count += 1
        # Loop continues...

    return forecast, analysis_history


async def run_agentic_variance_check(
    context: ForecastingContext,
) -> VarianceAnalysis:
    """
    Run standalone agentic variance analysis.

    Use this when you want the agent's analysis without triggering
    a full reforecast loop.

    Args:
        context: ForecastingContext with forecast_by_week and actual_sales

    Returns:
        VarianceAnalysis with agent's recommendations
    """
    result = await Runner.run(
        starting_agent=variance_agent,
        input=f"Analyze variance for week {context.current_week}.",
        context=context,
    )

    return result.final_output
