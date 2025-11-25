"""
Pricing Workflow - Markdown Checkpoint Logic

This workflow orchestrates the pricing agent for markdown decisions.
It's called at a checkpoint week (e.g., week 6) to evaluate if markdown
is needed based on sell-through performance.

Key insight: The WORKFLOW decides IF the pricing agent runs (deterministic),
while the AGENT decides HOW much markdown to recommend (agentic).

Usage:
    markdown = await run_markdown_check(
        context=context,
        current_sell_through=0.45,
        target_sell_through=0.60,
        week_number=6
    )
"""

import logging
from typing import Optional

from agents import Runner

from my_agents.pricing_agent import pricing_agent
from schemas.pricing_schemas import MarkdownResult
from utils.context import ForecastingContext

logger = logging.getLogger("pricing_workflow")


async def run_markdown_check(
    context: ForecastingContext,
    current_sell_through: float,
    target_sell_through: float = 0.60,
    week_number: Optional[int] = None,
) -> MarkdownResult:
    """
    Run markdown calculation based on sell-through performance.

    This workflow:
    1. Validates sell-through data
    2. Calls pricing agent if markdown may be needed
    3. Returns MarkdownResult with recommendation

    Args:
        context: ForecastingContext with sales tracking
        current_sell_through: Current sell-through rate (0.0-1.0)
        target_sell_through: Target rate (default: 0.60)
        week_number: Current week (uses context.current_week if not provided)

    Returns:
        MarkdownResult with markdown recommendation and explanation
    """
    week = week_number or context.current_week

    logger.info("=" * 80)
    logger.info("WORKFLOW: Markdown Check")
    logger.info(f"Week: {week}, Current sell-through: {current_sell_through:.1%}")
    logger.info(f"Target sell-through: {target_sell_through:.1%}")
    logger.info("=" * 80)

    # Build input prompt
    input_prompt = f"""Calculate markdown for week {week}:

Performance Data:
- Current Sell-Through: {current_sell_through:.1%}
- Target Sell-Through: {target_sell_through:.1%}
- Gap: {(target_sell_through - current_sell_through):.1%}

Context:
- Week Number: {week}
- Total Allocated: {context.total_allocated if hasattr(context, 'total_allocated') else 'N/A'}
- Total Sold: {context.total_sold if hasattr(context, 'total_sold') else 'N/A'}

Calculate the recommended markdown using Gap × Elasticity formula.
Consider the remaining season time when explaining your recommendation."""

    logger.info("Running pricing agent...")

    result = await Runner.run(
        starting_agent=pricing_agent,
        input=input_prompt,
        context=context,
    )

    markdown: MarkdownResult = result.final_output

    # Log result
    if markdown.recommended_markdown_pct > 0:
        logger.info(
            f"Markdown recommended: {markdown.recommended_markdown_pct:.0%} "
            f"(gap={markdown.gap:.1%}, raw={markdown.raw_markdown_pct:.1%})"
        )
        if markdown.is_max_markdown:
            logger.warning("Markdown hit 40% cap!")
    else:
        logger.info("No markdown needed - sell-through on track")

    return markdown


async def should_run_markdown_check(
    context: ForecastingContext,
    markdown_week: int = 6,
    markdown_threshold: float = 0.60,
) -> bool:
    """
    Determine if markdown check should run.

    This is a DETERMINISTIC decision made by the workflow, not the agent.
    Markdown check runs if:
    1. Current week >= markdown_week (checkpoint reached)
    2. Sell-through < markdown_threshold (below target)

    Args:
        context: ForecastingContext with current_week and sales tracking
        markdown_week: Week to start checking (default: 6)
        markdown_threshold: Sell-through threshold (default: 0.60)

    Returns:
        True if markdown check should run
    """
    # Check if we've reached the markdown checkpoint week
    if context.current_week < markdown_week:
        logger.debug(
            f"Week {context.current_week} < markdown week {markdown_week}, "
            "skipping markdown check"
        )
        return False

    # Calculate current sell-through
    sell_through = context.calculate_sell_through()

    # Check if below threshold
    if sell_through >= markdown_threshold:
        logger.info(
            f"Sell-through {sell_through:.1%} >= threshold {markdown_threshold:.1%}, "
            "no markdown check needed"
        )
        return False

    logger.info(
        f"Sell-through {sell_through:.1%} < threshold {markdown_threshold:.1%} at week {context.current_week}, "
        "markdown check needed"
    )
    return True


async def run_markdown_if_needed(
    context: ForecastingContext,
    markdown_week: int = 6,
    markdown_threshold: float = 0.60,
) -> Optional[MarkdownResult]:
    """
    Convenience function that checks if markdown is needed and runs if so.

    Combines should_run_markdown_check() and run_markdown_check() into
    a single call for simpler workflow code.

    Args:
        context: ForecastingContext with sales tracking
        markdown_week: Week to start checking (default: 6)
        markdown_threshold: Sell-through threshold (default: 0.60)

    Returns:
        MarkdownResult if markdown was calculated, None otherwise
    """
    # DETERMINISTIC: Python decides if pricing agent runs
    should_run = await should_run_markdown_check(
        context=context,
        markdown_week=markdown_week,
        markdown_threshold=markdown_threshold,
    )

    if not should_run:
        return None

    # AGENTIC: Agent decides the markdown amount
    sell_through = context.calculate_sell_through()
    markdown = await run_markdown_check(
        context=context,
        current_sell_through=sell_through,
        target_sell_through=markdown_threshold,
    )

    return markdown
