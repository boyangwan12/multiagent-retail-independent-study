"""
Pricing Agent Tools - Markdown Calculation

This module provides tools for the pricing agent:
1. calculate_markdown() - Calculate markdown percentage based on sell-through

STRUCTURE:
  Section 1: Imports & Models
  Section 2: Helper Functions
  Section 3: AGENT TOOL - calculate_markdown()

SDK Pattern:
    @function_tool
    def calculate_markdown(
        ctx: RunContextWrapper[ForecastingContext],
        current_sell_through: float,
        target_sell_through: float,
        elasticity: float
    ) -> MarkdownToolResult:
        ...

Formula:
    Gap = target_sell_through - current_sell_through
    Raw Markdown = Gap × Elasticity
    Final Markdown = round_to_nearest_5%(min(raw, 0.40))
"""

# ============================================================================
# SECTION 1: Imports & Models
# ============================================================================

from typing import Annotated, Optional
import logging

from pydantic import BaseModel, Field, ConfigDict
from agents import function_tool, RunContextWrapper

# Import context type for type hints
from utils.context import ForecastingContext

logger = logging.getLogger("pricing_tools")


# ============================================================================
# SECTION 2: Tool Output Schema
# ============================================================================

class MarkdownToolResult(BaseModel):
    """
    Output from calculate_markdown tool.

    Note: This is the TOOL output, not the AGENT output.
    The agent receives this from the tool, then constructs its own
    MarkdownResult (with output_type) that includes explanation/reasoning.
    """
    model_config = ConfigDict(extra='forbid')

    recommended_markdown_pct: float = Field(
        ...,
        description="Recommended markdown percentage (0.0-0.40, rounded to 0.05)",
        ge=0.0,
        le=0.40,
    )
    current_sell_through: float = Field(
        ...,
        description="Current sell-through rate (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    target_sell_through: float = Field(
        ...,
        description="Target sell-through rate (typically 0.60)",
        ge=0.0,
        le=1.0,
    )
    gap: float = Field(
        ...,
        description="Gap between target and current sell-through",
    )
    elasticity_used: float = Field(
        ...,
        description="Price elasticity factor used in calculation",
        ge=0.0,
    )
    raw_markdown_pct: float = Field(
        default=0.0,
        description="Raw markdown before rounding (gap × elasticity)",
    )
    week_number: int = Field(
        default=6,
        description="Week number when markdown was calculated",
        ge=1,
    )
    markdown_needed: bool = Field(
        default=False,
        description="Whether markdown is needed (sell-through below target)",
    )
    hit_max_cap: bool = Field(
        default=False,
        description="Whether markdown hit the 40% cap",
    )
    total_sold: Optional[int] = Field(
        default=None,
        description="Total units sold so far (if available)",
    )
    total_allocated: Optional[int] = Field(
        default=None,
        description="Total units allocated to stores (if available)",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if calculation failed",
    )


# ============================================================================
# SECTION 3: Helper Functions
# ============================================================================


def round_to_nearest_5_percent(value: float) -> float:
    """
    Round a decimal value to the nearest 5% (0.05).

    Examples:
        0.12 → 0.10
        0.13 → 0.15
        0.27 → 0.25
        0.38 → 0.40

    Args:
        value: Decimal value to round

    Returns:
        Value rounded to nearest 0.05
    """
    return round(value * 20) / 20


def cap_at_40_percent(value: float) -> float:
    """
    Cap markdown at 40% maximum.

    Args:
        value: Markdown percentage

    Returns:
        Value capped at 0.40
    """
    return min(value, 0.40)


def calculate_markdown_formula(
    current_sell_through: float,
    target_sell_through: float,
    elasticity: float,
) -> dict:
    """
    Calculate markdown using Gap × Elasticity formula.

    Formula:
        Gap = target_sell_through - current_sell_through
        Raw Markdown = Gap × Elasticity
        Final = round_to_5%(min(raw, 0.40))

    Args:
        current_sell_through: Current sell-through rate (0.0-1.0)
        target_sell_through: Target sell-through rate (0.0-1.0)
        elasticity: Price elasticity factor (typically 2.0)

    Returns:
        Dictionary with gap, raw_markdown, final_markdown, hit_cap
    """
    # Calculate gap (positive means we're below target)
    gap = target_sell_through - current_sell_through

    # No markdown needed if at or above target
    if gap <= 0:
        return {
            "gap": gap,
            "raw_markdown": 0.0,
            "final_markdown": 0.0,
            "hit_cap": False,
            "markdown_needed": False,
        }

    # Calculate raw markdown
    raw_markdown = gap * elasticity

    # Cap at 40%
    capped_markdown = cap_at_40_percent(raw_markdown)
    hit_cap = raw_markdown > 0.40

    # Round to nearest 5%
    final_markdown = round_to_nearest_5_percent(capped_markdown)

    return {
        "gap": gap,
        "raw_markdown": raw_markdown,
        "final_markdown": final_markdown,
        "hit_cap": hit_cap,
        "markdown_needed": True,
    }


# ============================================================================
# SECTION 4: AGENT TOOL - calculate_markdown
# ============================================================================


@function_tool
def calculate_markdown(
    ctx: RunContextWrapper[ForecastingContext],
    current_sell_through: Annotated[
        float, "Current sell-through rate (0.0-1.0, e.g., 0.45 for 45%)"
    ],
    target_sell_through: Annotated[
        float, "Target sell-through rate (0.0-1.0, typically 0.60)"
    ] = 0.60,
    elasticity: Annotated[
        float, "Price elasticity factor (typically 2.0, higher = more aggressive markdown)"
    ] = 2.0,
    week_number: Annotated[int, "Current week number for tracking (default: 6)"] = 6,
) -> MarkdownToolResult:
    """
    Calculate markdown percentage based on sell-through performance.

    Uses the Gap × Elasticity formula commonly used in retail markdown optimization:
    - Gap = target_sell_through - current_sell_through
    - Raw Markdown = Gap × Elasticity
    - Final Markdown = round to nearest 5%, capped at 40%

    Example:
        Current sell-through: 45%
        Target sell-through: 60%
        Gap: 15%
        Elasticity: 2.0
        Raw markdown: 30%
        Final markdown: 30% (rounded to nearest 5%)

    The tool can optionally use context data:
    - If context has total_sold and total_allocated, it calculates actual sell-through
    - Otherwise uses the provided current_sell_through parameter

    Args:
        ctx: Run context with optional sales data
        current_sell_through: Current sell-through rate (0.0-1.0)
        target_sell_through: Target sell-through rate (default: 0.60)
        elasticity: Price elasticity factor (default: 2.0)
        week_number: Current week number for tracking

    Returns:
        MarkdownToolResult with recommended markdown and calculation details
    """
    logger.info("=" * 80)
    logger.info("TOOL: calculate_markdown - Markdown Calculation")
    logger.info("=" * 80)

    try:
        # Try to get actual sell-through from context if available
        total_sold = None
        total_allocated = None
        actual_sell_through = current_sell_through

        if ctx.context is not None:
            # Check if context has sales tracking data
            if hasattr(ctx.context, "total_sold") and hasattr(
                ctx.context, "total_allocated"
            ):
                total_sold = ctx.context.total_sold
                total_allocated = ctx.context.total_allocated

                # Calculate actual sell-through if we have allocation data
                if total_allocated and total_allocated > 0:
                    actual_sell_through = total_sold / total_allocated
                    logger.info(
                        f"Using actual sell-through from context: "
                        f"{total_sold}/{total_allocated} = {actual_sell_through:.2%}"
                    )
                else:
                    logger.info(
                        f"Using provided sell-through: {current_sell_through:.2%}"
                    )
            else:
                logger.info(
                    f"Context has no sales tracking data, using provided: {current_sell_through:.2%}"
                )
        else:
            logger.info(f"No context available, using provided: {current_sell_through:.2%}")

        # Validate inputs
        if actual_sell_through < 0 or actual_sell_through > 1:
            return MarkdownToolResult(
                recommended_markdown_pct=0.0,
                current_sell_through=actual_sell_through,
                target_sell_through=target_sell_through,
                gap=0.0,
                elasticity_used=elasticity,
                raw_markdown_pct=0.0,
                week_number=week_number,
                markdown_needed=False,
                hit_max_cap=False,
                total_sold=total_sold,
                total_allocated=total_allocated,
                error=f"Invalid sell-through rate: {actual_sell_through}. Must be 0.0-1.0",
            )

        if target_sell_through < 0 or target_sell_through > 1:
            return MarkdownToolResult(
                recommended_markdown_pct=0.0,
                current_sell_through=actual_sell_through,
                target_sell_through=target_sell_through,
                gap=0.0,
                elasticity_used=elasticity,
                raw_markdown_pct=0.0,
                week_number=week_number,
                markdown_needed=False,
                hit_max_cap=False,
                total_sold=total_sold,
                total_allocated=total_allocated,
                error=f"Invalid target sell-through: {target_sell_through}. Must be 0.0-1.0",
            )

        if elasticity < 0:
            return MarkdownToolResult(
                recommended_markdown_pct=0.0,
                current_sell_through=actual_sell_through,
                target_sell_through=target_sell_through,
                gap=0.0,
                elasticity_used=elasticity,
                raw_markdown_pct=0.0,
                week_number=week_number,
                markdown_needed=False,
                hit_max_cap=False,
                total_sold=total_sold,
                total_allocated=total_allocated,
                error=f"Invalid elasticity: {elasticity}. Must be >= 0",
            )

        # Calculate markdown
        logger.info(
            f"Calculating markdown: current={actual_sell_through:.2%}, "
            f"target={target_sell_through:.2%}, elasticity={elasticity}"
        )

        calc_result = calculate_markdown_formula(
            current_sell_through=actual_sell_through,
            target_sell_through=target_sell_through,
            elasticity=elasticity,
        )

        result = MarkdownToolResult(
            recommended_markdown_pct=calc_result["final_markdown"],
            current_sell_through=actual_sell_through,
            target_sell_through=target_sell_through,
            gap=calc_result["gap"],
            elasticity_used=elasticity,
            raw_markdown_pct=calc_result["raw_markdown"],
            week_number=week_number,
            markdown_needed=calc_result["markdown_needed"],
            hit_max_cap=calc_result["hit_cap"],
            total_sold=total_sold,
            total_allocated=total_allocated,
        )

        if result.markdown_needed:
            logger.info(
                f"Markdown recommended: {result.recommended_markdown_pct:.0%} "
                f"(gap={result.gap:.2%}, raw={result.raw_markdown_pct:.2%})"
            )
            if result.hit_max_cap:
                logger.warning("Markdown hit 40% cap!")
        else:
            logger.info(
                f"No markdown needed: current {actual_sell_through:.2%} >= "
                f"target {target_sell_through:.2%}"
            )

        return result

    except Exception as e:
        logger.error(f"Markdown calculation failed: {e}")
        return MarkdownToolResult(
            recommended_markdown_pct=0.0,
            current_sell_through=current_sell_through,
            target_sell_through=target_sell_through,
            gap=0.0,
            elasticity_used=elasticity,
            raw_markdown_pct=0.0,
            week_number=week_number,
            markdown_needed=False,
            hit_max_cap=False,
            error=f"Calculation failed: {str(e)}",
        )
