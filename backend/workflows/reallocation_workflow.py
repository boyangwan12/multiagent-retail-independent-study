"""
Strategic Replenishment Workflow

This workflow orchestrates the Strategic Replenishment Agent to analyze
store performance and generate reallocation recommendations.

Strategic replenishment is triggered by variance analysis, not on a schedule.
It provides one-time rebalancing of inventory based on actual performance.

Flow:
1. Check if reallocation conditions are met
2. Run reallocation agent to analyze and recommend
3. Return ReallocationAnalysis with transfer recommendations

Usage:
    analysis = await run_strategic_replenishment(
        context=context,
        current_week=4,
        variance_pct=0.25,
    )
"""

import logging
from typing import Optional

from agents import Runner

from my_agents.reallocation_agent import reallocation_agent
from schemas.reallocation_schemas import ReallocationAnalysis
from schemas.allocation_schemas import AllocationResult
from utils.context import ForecastingContext
from agent_tools.reallocation_tools import should_trigger_reallocation

logger = logging.getLogger("reallocation_workflow")


async def run_strategic_replenishment(
    context: ForecastingContext,
    current_week: int,
    variance_pct: float = 0.0,
    force_run: bool = False,
) -> Optional[ReallocationAnalysis]:
    """
    Run Strategic Replenishment Agent to analyze and recommend reallocation.

    This is triggered after variance analysis detects significant deviation
    between forecast and actual sales, OR when explicitly requested.

    Args:
        context: ForecastingContext with allocation_result and actual_sales
        current_week: Current week number in season
        variance_pct: Overall variance percentage (from variance analysis)
        force_run: If True, skip trigger check and always run analysis

    Returns:
        ReallocationAnalysis with recommendations, or None if not triggered
    """
    logger.info("=" * 80)
    logger.info("WORKFLOW: Strategic Replenishment Analysis")
    logger.info(f"Week: {current_week}, Variance: {variance_pct:.1%}")
    logger.info("=" * 80)

    # Check if we have allocation data
    if not hasattr(context, 'allocation_result') or context.allocation_result is None:
        logger.warning("No allocation data available - skipping reallocation analysis")
        return None

    allocation: AllocationResult = context.allocation_result
    total_weeks = len(context.forecast_by_week) if context.forecast_by_week else 12
    weeks_remaining = total_weeks - current_week

    # Quick performance scan to check trigger conditions
    if not force_run:
        # Count high performers and underperformers
        # (simplified check - agent will do detailed analysis)
        total_sold = context.total_sold or 0
        total_allocated = allocation.initial_store_allocation

        if total_allocated > 0:
            overall_sell_through = total_sold / total_allocated
            expected_sell_through = current_week / total_weeks

            # Rough categorization
            if overall_sell_through > expected_sell_through * 1.15:
                high_performer_estimate = len(allocation.store_allocations) // 3
            else:
                high_performer_estimate = len(allocation.store_allocations) // 6

            underperformer_estimate = len(allocation.store_allocations) // 6
        else:
            high_performer_estimate = 0
            underperformer_estimate = 0

        # Check if we should trigger
        should_trigger, reason = should_trigger_reallocation(
            variance_pct=variance_pct,
            high_performer_count=high_performer_estimate,
            underperformer_count=underperformer_estimate,
            weeks_remaining=weeks_remaining,
            dc_available=allocation.dc_holdback,
        )

        if not should_trigger:
            logger.info(f"Reallocation not triggered: {reason}")
            return None

        logger.info(f"Reallocation triggered: {reason}")

    # Run the Strategic Replenishment Agent
    logger.info("Running Strategic Replenishment Agent...")

    result = await Runner.run(
        starting_agent=reallocation_agent,
        input=(
            f"Analyze store performance and recommend strategic replenishment for week {current_week}. "
            f"Overall variance is {variance_pct:.1%}. "
            f"We have {weeks_remaining} weeks remaining in the season. "
            f"DC holdback is {allocation.dc_holdback} units."
        ),
        context=context,
    )

    analysis: ReallocationAnalysis = result.final_output

    # Log results
    logger.info("Strategic Replenishment Analysis Complete:")
    logger.info(f"  - Should Reallocate: {analysis.should_reallocate}")
    logger.info(f"  - Strategy: {analysis.strategy}")
    logger.info(f"  - High Performers: {len(analysis.high_performers)}")
    logger.info(f"  - Underperformers: {len(analysis.underperformers)}")
    logger.info(f"  - Total Transfers: {len(analysis.transfers)}")
    logger.info(f"  - Units to Move: {analysis.total_units_to_move}")
    logger.info(f"  - Confidence: {analysis.confidence:.0%}")

    return analysis


async def check_reallocation_needed(
    context: ForecastingContext,
    current_week: int,
    variance_pct: float = 0.0,
) -> bool:
    """
    Quick check if reallocation analysis should be triggered.

    Use this for conditional workflow logic without running the full agent.

    Args:
        context: ForecastingContext with allocation data
        current_week: Current week number
        variance_pct: Overall variance percentage

    Returns:
        True if reallocation analysis should be run
    """
    if not hasattr(context, 'allocation_result') or context.allocation_result is None:
        return False

    allocation = context.allocation_result
    total_weeks = len(context.forecast_by_week) if context.forecast_by_week else 12
    weeks_remaining = total_weeks - current_week

    # Quick estimates
    total_sold = context.total_sold or 0
    total_allocated = allocation.initial_store_allocation

    if total_allocated > 0:
        overall_sell_through = total_sold / total_allocated
        expected_sell_through = current_week / total_weeks

        if overall_sell_through > expected_sell_through * 1.15:
            high_performer_estimate = len(allocation.store_allocations) // 3
        else:
            high_performer_estimate = len(allocation.store_allocations) // 6
    else:
        high_performer_estimate = 0

    underperformer_estimate = len(allocation.store_allocations) // 6

    should_trigger, _ = should_trigger_reallocation(
        variance_pct=variance_pct,
        high_performer_count=high_performer_estimate,
        underperformer_count=underperformer_estimate,
        weeks_remaining=weeks_remaining,
        dc_available=allocation.dc_holdback,
    )

    return should_trigger
