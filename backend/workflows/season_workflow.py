"""
Season Workflow - Full Season Orchestration

This workflow orchestrates all three agents through a complete season:
1. Demand Agent → ForecastResult (with variance loop)
2. Inventory Agent → AllocationResult
3. Pricing Agent → MarkdownResult (if needed)

This is the main entry point for the retail forecasting system.

Usage:
    result = await run_full_season(
        context=context,
        params=WorkflowParams(category="Women's Dresses", ...)
    )
"""

import logging
import time
from typing import Optional

from workflows.forecast_workflow import run_forecast_with_variance_loop
from workflows.allocation_workflow import run_allocation
from workflows.pricing_workflow import run_markdown_if_needed
from schemas.workflow_schemas import WorkflowParams, SeasonResult
from schemas.forecast_schemas import ForecastResult
from schemas.allocation_schemas import AllocationResult
from schemas.pricing_schemas import MarkdownResult
from utils.context import ForecastingContext

logger = logging.getLogger("season_workflow")


async def run_full_season(
    context: ForecastingContext,
    params: WorkflowParams,
) -> SeasonResult:
    """
    Full season workflow with all 3 agents.

    DETERMINISTIC FLOW:
    1. Demand Agent → ForecastResult (with variance loop if actual sales exist)
    2. Inventory Agent → AllocationResult (clustering + allocation)
    3. Pricing Agent → MarkdownResult (only if below sell-through threshold)

    The workflow layer controls WHEN each agent runs (deterministic Python code),
    while agents control HOW they produce results (agentic LLM reasoning).

    Args:
        context: ForecastingContext with data_loader and session state
        params: WorkflowParams with all configuration

    Returns:
        SeasonResult with all phase outputs and metadata
    """
    logger.info("=" * 80)
    logger.info("WORKFLOW: Full Season Orchestration")
    logger.info(f"Category: {params.category}")
    logger.info(f"Horizon: {params.forecast_horizon_weeks} weeks")
    logger.info(f"Variance threshold: {params.variance_threshold:.0%}")
    logger.info(f"Markdown week: {params.markdown_week}, threshold: {params.markdown_threshold:.0%}")
    logger.info("=" * 80)

    start_time = time.time()
    phases_completed = []

    # ==========================================================================
    # PHASE 1: Demand Forecast (with variance loop)
    # ==========================================================================
    logger.info("\n" + "=" * 40)
    logger.info("PHASE 1: Demand Forecasting")
    logger.info("=" * 40)

    forecast, variance_history = await run_forecast_with_variance_loop(
        context=context,
        category=params.category,
        forecast_horizon=params.forecast_horizon_weeks,
        variance_threshold=params.variance_threshold,
        max_reforecasts=params.max_reforecasts,
    )

    phases_completed.append("forecast")
    reforecast_count = len([v for v in variance_history if v.is_high_variance])

    logger.info(f"Forecast complete: {forecast.total_demand} units")
    logger.info(f"Reforecasts triggered: {reforecast_count}")

    # ==========================================================================
    # PHASE 2: Inventory Allocation
    # ==========================================================================
    logger.info("\n" + "=" * 40)
    logger.info("PHASE 2: Inventory Allocation")
    logger.info("=" * 40)

    allocation = await run_allocation(
        context=context,
        forecast=forecast,
        dc_holdback_pct=params.dc_holdback_pct,
        replenishment_strategy=params.replenishment_strategy,
    )

    phases_completed.append("allocation")

    logger.info(f"Allocation complete: {allocation.manufacturing_qty} units manufactured")
    logger.info(f"DC holdback: {allocation.dc_holdback}, Store allocation: {allocation.initial_store_allocation}")

    # ==========================================================================
    # PHASE 3: Markdown Check (if at or past markdown week)
    # ==========================================================================
    logger.info("\n" + "=" * 40)
    logger.info("PHASE 3: Pricing/Markdown Check")
    logger.info("=" * 40)

    markdown: Optional[MarkdownResult] = None

    # DETERMINISTIC: Python decides if pricing agent should run
    if context.current_week >= params.markdown_week:
        markdown = await run_markdown_if_needed(
            context=context,
            markdown_week=params.markdown_week,
            markdown_threshold=params.markdown_threshold,
        )

        if markdown is not None:
            phases_completed.append("pricing")
            logger.info(f"Markdown calculated: {markdown.recommended_markdown_pct:.0%}")
        else:
            logger.info("No markdown needed - sell-through on track")
    else:
        logger.info(
            f"Week {context.current_week} < markdown week {params.markdown_week}, "
            "skipping pricing phase"
        )

    # ==========================================================================
    # BUILD FINAL RESULT
    # ==========================================================================
    end_time = time.time()
    total_duration = end_time - start_time

    result = SeasonResult(
        forecast=forecast,
        allocation=allocation,
        markdown=markdown,
        variance_history=variance_history,
        reforecast_count=reforecast_count,
        total_duration_seconds=total_duration,
        phases_completed=phases_completed,
    )

    logger.info("\n" + "=" * 80)
    logger.info("WORKFLOW COMPLETE")
    logger.info(f"Duration: {total_duration:.2f}s")
    logger.info(f"Phases: {', '.join(phases_completed)}")
    logger.info(f"High variance events: {len([v for v in variance_history if v.is_high_variance])}")
    logger.info(f"Markdown applied: {result.markdown_applied}")
    logger.info("=" * 80)

    return result


async def run_preseason_planning(
    context: ForecastingContext,
    params: WorkflowParams,
) -> SeasonResult:
    """
    Pre-season planning workflow (forecast + allocation only).

    Simplified workflow for pre-season planning when no actual sales
    data exists. Skips variance checking and markdown phases.

    Args:
        context: ForecastingContext with data_loader
        params: WorkflowParams with configuration

    Returns:
        SeasonResult with forecast and allocation (no markdown)
    """
    logger.info("Running pre-season planning (no variance/markdown checks)")

    # Ensure we're in pre-season mode
    context.actual_sales = None
    context.current_week = 0

    return await run_full_season(context, params)


async def run_inseason_update(
    context: ForecastingContext,
    params: WorkflowParams,
    current_week: int,
    actual_sales: list,
    total_sold: int,
) -> SeasonResult:
    """
    In-season update workflow with actual sales data.

    Updates the forecast based on actual performance and checks
    if markdown is needed.

    Args:
        context: ForecastingContext with data_loader
        params: WorkflowParams with configuration
        current_week: Current week number (1-12)
        actual_sales: List of actual weekly sales
        total_sold: Total units sold so far

    Returns:
        SeasonResult with updated forecast and potential markdown
    """
    logger.info(f"Running in-season update at week {current_week}")

    # Update context with actual data
    context.current_week = current_week
    context.actual_sales = actual_sales
    context.total_sold = total_sold

    return await run_full_season(context, params)
