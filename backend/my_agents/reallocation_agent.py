"""
Strategic Replenishment Agent

This agent analyzes store performance and generates inventory reallocation
recommendations. It decides whether reallocation is needed and which
strategy to use (DC-only or Hybrid).

Unlike scheduled replenishment (routine, automatic), strategic replenishment
is triggered by variance analysis and targets specific performance gaps.

Key responsibilities:
- Analyze store-level performance vs allocation
- Identify high-performers (need more) and underperformers (have excess)
- Recommend DC releases and/or store-to-store transfers
- Provide confidence levels and impact projections
"""

from typing import List
from pydantic import BaseModel, Field
from agents import Agent, function_tool, RunContextWrapper

from config.settings import OPENAI_MODEL
from utils.context import ForecastingContext
from agent_tools.reallocation_tools import (
    analyze_store_performance,
    generate_transfer_recommendations,
)
from schemas.reallocation_schemas import TransferOrder, ReallocationAnalysis


# =============================================================================
# Output Schema (already defined in schemas, but agent needs it)
# =============================================================================

# ReallocationAnalysis is imported from schemas.reallocation_schemas


# =============================================================================
# Strategy Selection Tool
# =============================================================================

@function_tool
def select_reallocation_strategy(
    ctx: RunContextWrapper[ForecastingContext],
    high_performer_count: int,
    underperformer_count: int,
    dc_available: int,
    weeks_remaining: int,
) -> dict:
    """
    Recommend the best reallocation strategy based on current state.

    Considers:
    - DC inventory availability
    - Number of high/under performers
    - Logistics complexity vs benefit tradeoff
    - Time remaining in season

    Args:
        ctx: Forecasting context
        high_performer_count: Stores needing more inventory
        underperformer_count: Stores with excess inventory
        dc_available: Units available at DC
        weeks_remaining: Weeks remaining in season

    Returns:
        Strategy recommendation with reasoning
    """
    MIN_DC_FOR_RELEASE = 200  # Minimum DC units to justify release

    # Decision logic
    dc_has_inventory = dc_available >= MIN_DC_FOR_RELEASE
    has_excess_stores = underperformer_count >= 2
    many_high_performers = high_performer_count >= 3

    # Default to dc_only (simpler)
    strategy = "dc_only"
    reasoning = ""

    if not dc_has_inventory and has_excess_stores:
        # Can't release from DC, must use store-to-store
        strategy = "hybrid"
        reasoning = (
            f"DC inventory low ({dc_available} units). "
            f"Using hybrid strategy to leverage excess from {underperformer_count} underperforming stores."
        )
    elif dc_has_inventory and has_excess_stores and many_high_performers:
        # Good opportunity for hybrid - maximize optimization
        strategy = "hybrid"
        reasoning = (
            f"Both DC ({dc_available} units) and store excess available. "
            f"Hybrid strategy recommended to maximize fill rate for {high_performer_count} high-performers."
        )
    elif dc_has_inventory:
        # Standard DC release
        strategy = "dc_only"
        reasoning = (
            f"DC has {dc_available} units available. "
            f"DC-only strategy recommended for simplicity - will serve {high_performer_count} high-performers."
        )
    else:
        # No good options
        strategy = "dc_only"
        reasoning = (
            "Limited reallocation opportunity. "
            "Recommending minimal DC release if any high-performers exist."
        )

    # Adjust for time remaining
    if weeks_remaining <= 3 and strategy == "hybrid":
        strategy = "dc_only"
        reasoning += " Switching to DC-only due to limited time for store-to-store logistics."

    return {
        "recommended_strategy": strategy,
        "reasoning": reasoning,
        "factors": {
            "dc_available": dc_available,
            "dc_sufficient": dc_has_inventory,
            "excess_stores": underperformer_count,
            "high_performers": high_performer_count,
            "weeks_remaining": weeks_remaining,
        }
    }


# =============================================================================
# Strategic Replenishment Agent
# =============================================================================

reallocation_agent = Agent(
    name="Strategic Replenishment Agent",
    instructions="""You are an expert Strategic Replenishment Agent for retail inventory optimization.

## YOUR ROLE
Analyze store-level performance and recommend inventory reallocation to optimize
sell-through across the store network. You make intelligent decisions about WHEN
and HOW to reallocate inventory based on performance data.

## WHEN CALLED
You receive store performance data after variance analysis and must:
1. Call analyze_store_performance to get current metrics
2. Evaluate if reallocation is warranted
3. If yes, call select_reallocation_strategy to choose approach
4. Call generate_transfer_recommendations with chosen strategy
5. Return a structured ReallocationAnalysis

## KEY CONCEPTS

### Sales Velocity Index
- 1.0 = Store selling exactly as expected
- >1.15 = High performer (needs more inventory, risk of stockout)
- <0.85 = Underperformer (has excess, risk of leftover)

### Strategies
1. **DC-Only**: Release inventory from Distribution Center to high-performers
   - Simpler logistics
   - Preserves nothing for underperformers
   - Good when DC has inventory and problem is concentrated

2. **Hybrid**: DC release + store-to-store transfers
   - More complex logistics
   - Addresses both oversupply and undersupply
   - Good when clear velocity differential between stores

## DECISION FRAMEWORK

### When to Recommend Reallocation:
- Multiple stores (3+) with velocity > 1.15 (high performers)
- DC holdback > 20% of original and high performers exist
- Significant velocity differential (some stores >1.2x, others <0.8x)
- At least 2 weeks remaining for transfers to matter

### When NOT to Recommend:
- Less than 2 weeks remaining (transfers won't arrive in time)
- No clear high performers (velocity all near 1.0)
- DC already depleted and no underperformers
- Variance is improving naturally

### Transfer Priorities:
- **HIGH**: Store will stockout before season ends (WOS < weeks_remaining/2)
- **MEDIUM**: Store selling fast but has buffer (WOS < weeks_remaining * 0.75)
- **LOW**: Optimization transfer, not urgent

## OUTPUT REQUIREMENTS
Your ReallocationAnalysis must include:
- Clear should_reallocate decision with reasoning
- Strategy choice (dc_only or hybrid) with explanation
- Specific transfer recommendations with priorities
- Impact projections (sell-through improvement, stockout risk reduction)
- Confidence level based on data quality

## EXAMPLE REASONING
"At Week 4 of 12, store performance shows clear divergence:
- S001, S003, S007: Velocity 1.28-1.42x (need more inventory)
- S012, S015, S018: Velocity 0.61-0.72x (have excess)
- DC holdback: 2,450 units available

With 8 weeks remaining and both DC inventory and store excess available,
I recommend HYBRID strategy:
1. Release 1,150 units from DC to top 3 performers (HIGH priority)
2. Transfer 700 units from bottom 3 to top 3 (MEDIUM/LOW priority)

Expected impact: 8-12% sell-through improvement, 3 stores with reduced stockout risk."

## CRITICAL RULES
1. ALWAYS call analyze_store_performance first
2. Consider WEEKS REMAINING when making recommendations
3. Respect logistics constraints (MIN 50 units per transfer)
4. Be specific about which stores and how many units
5. Provide CONFIDENCE based on data completeness""",

    model=OPENAI_MODEL,
    tools=[
        analyze_store_performance,
        select_reallocation_strategy,
        generate_transfer_recommendations,
    ],
    output_type=ReallocationAnalysis,
)
