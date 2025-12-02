"""
Forecast Workflow - Demand Forecasting with Agentic Variance Analysis

This workflow orchestrates the demand agent with variance-triggered re-forecasting
using an intelligent Variance Analysis Agent.

AGENTIC MODE:
- Variance Agent analyzes and reasons about variance
- Agent decides whether to reforecast based on trends, causes, and remaining season
- Considers multiple factors beyond simple thresholds

Usage:
    forecast, analysis_history = await run_forecast_with_variance_loop(...)
"""

import logging
from typing import List, Tuple, Optional

from agents import Runner, RunHooks

from my_agents.demand_agent import demand_agent
from my_agents.variance_agent import variance_agent, VarianceAnalysis
from my_agents.reforecast_agent import reforecast_agent, ReforecastResult
from schemas.forecast_schemas import ForecastResult
from utils.context import ForecastingContext

logger = logging.getLogger("forecast_workflow")


async def run_forecast(
    context: ForecastingContext,
    category: str,
    forecast_horizon: int,
    hooks: Optional[RunHooks] = None,
) -> ForecastResult:
    """
    Run demand forecast without variance checking.

    Simple wrapper for cases where no variance loop is needed
    (e.g., pre-season planning with no actual sales data).

    Args:
        context: ForecastingContext with data_loader
        category: Product category to forecast
        forecast_horizon: Number of weeks to forecast
        hooks: Optional RunHooks for UI updates

    Returns:
        ForecastResult with typed forecast data
    """
    logger.info(f"Running forecast for {category}, horizon={forecast_horizon} weeks")

    result = await Runner.run(
        starting_agent=demand_agent,
        input=f"Forecast demand for {category} for {forecast_horizon} weeks",
        context=context,
        hooks=hooks,
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
    variance_threshold: float = 0.20,  # Kept for API compatibility, agent uses its own logic
    max_reforecasts: int = 2,  # Kept for API compatibility, no longer loops
    hooks: Optional[RunHooks] = None,
) -> Tuple[ForecastResult, List[VarianceAnalysis]]:
    """
    Run demand forecast with AGENTIC variance analysis.

    Uses a Variance Analysis Agent that reasons about variance patterns
    and decides whether to reforecast. The agent now directly executes
    the reforecast using the bayesian_reforecast_tool.

    The agent considers:
    - Variance magnitude AND trend
    - Likely causes of variance
    - Remaining season (is reforecast worth it?)
    - Alternative actions (reallocate, markdown)

    Flow:
    1. Run demand agent → ForecastResult
    2. If no actual sales → return (pre-season mode)
    3. Run variance agent → VarianceAnalysis (agent REASONS about variance)
    4. If agent decides reforecast needed → agent calls bayesian_reforecast_tool
    5. Return agent's result (with optional reforecast applied)

    Args:
        context: ForecastingContext with data_loader and optional actual_sales
        category: Product category to forecast
        forecast_horizon: Number of weeks to forecast
        variance_threshold: Kept for API compatibility (agent uses its own reasoning)
        max_reforecasts: Kept for API compatibility (no longer loops)

    Returns:
        Tuple of (ForecastResult, List[VarianceAnalysis])
    """
    logger.info("=" * 80)
    logger.info("WORKFLOW: Forecast with Agentic Variance Analysis")
    logger.info(f"Category: {category}, Horizon: {forecast_horizon} weeks")
    logger.info("=" * 80)

    analysis_history: List[VarianceAnalysis] = []

    # Step 1: Run demand agent
    logger.info("Running demand forecast...")

    result = await Runner.run(
        starting_agent=demand_agent,
        input=f"Forecast demand for {category} for {forecast_horizon} weeks",
        context=context,
        hooks=hooks,
    )

    forecast = result.final_output
    logger.info(
        f"Forecast received: total={forecast.total_demand}, "
        f"confidence={forecast.confidence:.2f}"
    )

    # Update context with forecast and store the forecast result for bayesian tool
    context.forecast_by_week = forecast.forecast_by_week
    context.forecast_result = forecast

    # Step 2: Check if we have actual sales data
    if not context.has_actual_sales:
        logger.info("No actual sales data - pre-season mode, skipping variance analysis")
        return forecast, analysis_history

    # Step 3: Run VARIANCE AGENT (agentic analysis with optional reforecast!)
    logger.info(f"Running variance agent analysis at week {context.current_week}...")

    variance_result = await Runner.run(
        starting_agent=variance_agent,
        input=f"Analyze variance for week {context.current_week}. "
              f"We have {forecast_horizon - context.current_week} weeks remaining in the season. "
              f"If reforecast is warranted, execute it using the bayesian_reforecast_tool.",
        context=context,
        hooks=hooks,
        max_turns=25,  # Increased to allow tool calling
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

    # Step 4: If variance agent recommends reforecast, hand off to Reforecast Agent
    if analysis.should_reforecast:
        logger.info("Variance Agent recommends reforecast - handing off to Reforecast Agent...")

        reforecast_result_obj = await Runner.run(
            starting_agent=reforecast_agent,
            input="Execute Bayesian reforecast using current forecast and actual sales data.",
            context=context,
            hooks=hooks,
            max_turns=15,  # Simple agent, but allow enough turns for tool calling
        )

        reforecast_result: ReforecastResult = reforecast_result_obj.final_output

        # Parse the JSON from the agent
        import json
        reforecast_data = json.loads(reforecast_result.reforecast_json)

        if reforecast_data.get("success"):
            logger.info("Reforecast Agent executed Bayesian reforecast successfully!")
            logger.info(f"  - Original total: {forecast.total_demand}")
            logger.info(f"  - Updated total: {reforecast_data['total_demand']}")
            logger.info(f"  - Adjustment: {reforecast_data['adjustment_applied']:.2%}")

            # Create updated ForecastResult from the Bayesian reforecast
            forecast = ForecastResult(
                total_demand=reforecast_data["total_demand"],
                forecast_by_week=reforecast_data["forecast_by_week"],
                safety_stock_pct=forecast.safety_stock_pct,
                confidence=reforecast_data["confidence"],
                model_used="Bayesian-Reforecast (Agent-Executed)",
                lower_bound=reforecast_data["lower_bound"],
                upper_bound=reforecast_data["upper_bound"],
                weekly_average=reforecast_data["total_demand"] // forecast_horizon,
            )

            # Update context with reforecast - this is critical for subsequent weeks!
            context.forecast_by_week = forecast.forecast_by_week
            context.forecast_result = forecast
        else:
            logger.error(f"Reforecast Agent failed: {reforecast_data.get('error', 'Unknown error')}")
    else:
        logger.info(f"Variance agent recommends: {analysis.recommended_action}")
        logger.info("No reforecast needed - using original forecast")

    return forecast, analysis_history


async def check_forecast_variance(
    context: ForecastingContext,
    hooks: Optional[RunHooks] = None,
) -> Optional[VarianceAnalysis]:
    """
    Run standalone agentic variance analysis.

    Use this when you want the agent's analysis without triggering
    a full reforecast loop.

    Args:
        context: ForecastingContext with forecast_by_week and actual_sales
        hooks: Optional RunHooks for UI updates

    Returns:
        VarianceAnalysis with agent's recommendations, or None if no actual sales
    """
    if not context.has_actual_sales:
        return None

    result = await Runner.run(
        starting_agent=variance_agent,
        input=f"Analyze variance for week {context.current_week}.",
        context=context,
        hooks=hooks,
        max_turns=25,  # Increased to allow tool calling
    )

    return result.final_output
