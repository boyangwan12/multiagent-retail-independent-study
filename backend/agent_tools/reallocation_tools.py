"""
Strategic Replenishment Tools

Pure functions and @function_tool decorated tools for inventory reallocation analysis.
These tools are used by the Reallocation Agent to analyze store performance
and generate transfer recommendations.
"""

from typing import List, Dict, Optional, Tuple
from agents import function_tool, RunContextWrapper

from utils.context import ForecastingContext
from schemas.reallocation_schemas import StorePerformance, TransferOrder


# =============================================================================
# Constants
# =============================================================================

# Velocity thresholds for categorizing store performance
HIGH_PERFORMER_THRESHOLD = 1.15  # velocity > 1.15 = needs more inventory
UNDERPERFORMER_THRESHOLD = 0.85  # velocity < 0.85 = has excess inventory

# Transfer constraints
MIN_TRANSFER_UNITS = 50  # Minimum units to justify transfer logistics
MAX_STORE_TRANSFER_PCT = 0.30  # Max % of store allocation that can be transferred out
MIN_DC_RESERVE_PCT = 0.20  # Keep at least 20% of original DC holdback


# =============================================================================
# Pure Analysis Functions (no decorator - called by tools or workflow)
# =============================================================================

def calculate_store_velocity(
    allocated: int,
    sold: int,
    current_week: int,
    total_weeks: int,
) -> float:
    """
    Calculate sales velocity index for a store.

    Velocity = (Actual Sales Rate) / (Expected Sales Rate)
    - 1.0 = selling exactly as expected
    - >1.0 = selling faster than expected (needs more inventory)
    - <1.0 = selling slower than expected (has excess)

    Args:
        allocated: Units allocated to store
        sold: Units sold to date
        current_week: Current week number
        total_weeks: Total weeks in season

    Returns:
        Velocity index (float)
    """
    if current_week == 0 or allocated == 0:
        return 1.0

    # Expected sell-through by current week (linear assumption)
    expected_pct = current_week / total_weeks
    expected_sold = allocated * expected_pct

    if expected_sold == 0:
        return 1.0

    return sold / expected_sold


def categorize_store(velocity: float) -> str:
    """Categorize store based on velocity."""
    if velocity > HIGH_PERFORMER_THRESHOLD:
        return "needs_more"
    elif velocity < UNDERPERFORMER_THRESHOLD:
        return "excess"
    else:
        return "on_target"


def calculate_weeks_of_supply(
    remaining: int,
    weekly_sales_rate: float,
) -> float:
    """Calculate estimated weeks until stockout."""
    if weekly_sales_rate <= 0:
        return float('inf')
    return remaining / weekly_sales_rate


def calculate_transfer_priority(
    velocity: float,
    weeks_of_supply: float,
    weeks_remaining: int,
) -> str:
    """
    Determine transfer priority based on urgency.

    High: Store will stockout before season ends
    Medium: Store selling fast but has some buffer
    Low: Optimization transfer, not urgent
    """
    if weeks_of_supply < weeks_remaining * 0.5:
        return "high"
    elif velocity > 1.3 or weeks_of_supply < weeks_remaining * 0.75:
        return "medium"
    else:
        return "low"


def generate_dc_transfers(
    high_performers: List[StorePerformance],
    dc_available: int,
    weeks_remaining: int,
    min_dc_reserve: int,
) -> List[TransferOrder]:
    """
    Generate DC-to-Store transfer recommendations.

    Allocates DC inventory to high-performing stores based on:
    - Velocity (faster sellers get more)
    - Weeks of supply (lower WOS = higher priority)

    Args:
        high_performers: List of stores needing more inventory
        dc_available: Units available at DC
        weeks_remaining: Weeks remaining in season
        min_dc_reserve: Minimum units to keep at DC

    Returns:
        List of TransferOrder recommendations
    """
    transfers = []
    available = dc_available - min_dc_reserve

    if available <= 0 or not high_performers:
        return transfers

    # Sort by urgency (lowest weeks_of_supply first)
    sorted_stores = sorted(high_performers, key=lambda s: s.weeks_of_supply)

    # Calculate total "need" for proportional allocation
    total_velocity_excess = sum(max(0, s.velocity - 1.0) for s in sorted_stores)

    if total_velocity_excess == 0:
        return transfers

    for store in sorted_stores:
        if available < MIN_TRANSFER_UNITS:
            break

        # Proportional allocation based on how much they're over-performing
        velocity_excess = max(0, store.velocity - 1.0)
        proportion = velocity_excess / total_velocity_excess

        # Calculate units to send
        units = int(available * proportion)
        units = max(MIN_TRANSFER_UNITS, min(units, available))

        # Determine priority
        priority = calculate_transfer_priority(
            store.velocity,
            store.weeks_of_supply,
            weeks_remaining
        )

        # Create transfer
        transfers.append(TransferOrder(
            from_location="DC",
            to_store=store.store_id,
            units=units,
            priority=priority,
            reason=f"High velocity ({store.velocity:.2f}x), {store.weeks_of_supply:.1f} weeks of supply remaining",
            estimated_transit_days=2,
        ))

        available -= units

    return transfers


def generate_store_to_store_transfers(
    underperformers: List[StorePerformance],
    high_performers: List[StorePerformance],
    weeks_remaining: int,
) -> List[TransferOrder]:
    """
    Generate Store-to-Store transfer recommendations.

    Moves inventory from underperforming stores to high performers.
    Respects MAX_STORE_TRANSFER_PCT constraint.

    Args:
        underperformers: Stores with excess inventory
        high_performers: Stores needing more inventory
        weeks_remaining: Weeks remaining in season

    Returns:
        List of TransferOrder recommendations
    """
    transfers = []

    if not underperformers or not high_performers:
        return transfers

    # Sort underperformers by lowest velocity (most excess first)
    sorted_under = sorted(underperformers, key=lambda s: s.velocity)

    # Sort high performers by urgency (lowest WOS first)
    sorted_high = sorted(high_performers, key=lambda s: s.weeks_of_supply)

    # Track remaining capacity for each high performer
    remaining_need = {s.store_id: int(s.allocated_units * 0.5) for s in sorted_high}

    for under_store in sorted_under:
        # Maximum we can take from this store
        max_transfer = int(under_store.remaining_units * MAX_STORE_TRANSFER_PCT)

        if max_transfer < MIN_TRANSFER_UNITS:
            continue

        available_from_store = max_transfer

        for high_store in sorted_high:
            if available_from_store < MIN_TRANSFER_UNITS:
                break

            need = remaining_need.get(high_store.store_id, 0)
            if need < MIN_TRANSFER_UNITS:
                continue

            # Transfer amount
            units = min(available_from_store, need, 300)  # Cap individual transfers

            if units < MIN_TRANSFER_UNITS:
                continue

            priority = calculate_transfer_priority(
                high_store.velocity,
                high_store.weeks_of_supply,
                weeks_remaining
            )

            transfers.append(TransferOrder(
                from_location=under_store.store_id,
                to_store=high_store.store_id,
                units=units,
                priority=priority,
                reason=f"Velocity differential: {under_store.store_id} ({under_store.velocity:.2f}x) → {high_store.store_id} ({high_store.velocity:.2f}x)",
                estimated_transit_days=3,
            ))

            available_from_store -= units
            remaining_need[high_store.store_id] -= units

    return transfers


# =============================================================================
# Function Tools (decorated - used by agent)
# =============================================================================

@function_tool
def analyze_store_performance(
    ctx: RunContextWrapper[ForecastingContext],
    current_week: int,
) -> dict:
    """
    Analyze store-level performance for strategic replenishment decisions.

    Gathers allocation, sales, and velocity data for all stores to identify
    which stores need more inventory and which have excess.

    Args:
        ctx: Context with allocation and sales data
        current_week: Current week number

    Returns:
        Dictionary with store performance metrics and categorization
    """
    context = ctx.context

    # Get allocation data
    if not hasattr(context, 'allocation_result') or context.allocation_result is None:
        return {
            "error": "No allocation data available",
            "has_data": False
        }

    allocation = context.allocation_result
    total_weeks = len(context.forecast_by_week) if context.forecast_by_week else 12

    # Build store performance list
    store_performances = []
    high_performers = []
    underperformers = []
    on_target = []

    # Check if we have real per-store sales data
    has_store_data = context.has_store_sales

    for store_alloc in allocation.store_allocations:
        store_id = store_alloc.store_id
        allocated = store_alloc.allocation_units
        cluster = store_alloc.cluster

        # Get actual sales for this store
        if has_store_data:
            # Use real per-store sales data from uploaded CSVs
            store_sold = context.get_store_sales_up_to_week(store_id, current_week)
        else:
            # Fallback: estimate from total sales proportionally
            total_sold = context.total_sold or 0
            total_allocated = allocation.initial_store_allocation

            if total_allocated > 0:
                store_sold = int(total_sold * (allocated / total_allocated))
            else:
                store_sold = 0

        remaining = max(0, allocated - store_sold)

        # Calculate velocity
        velocity = calculate_store_velocity(
            allocated=allocated,
            sold=store_sold,
            current_week=current_week,
            total_weeks=total_weeks,
        )

        # Calculate sell-through and weeks of supply
        sell_through = store_sold / allocated if allocated > 0 else 0
        weekly_rate = store_sold / current_week if current_week > 0 else 0
        wos = calculate_weeks_of_supply(remaining, weekly_rate)

        status = categorize_store(velocity)

        perf = StorePerformance(
            store_id=store_id,
            cluster=cluster,
            allocated_units=allocated,
            sold_units=store_sold,
            remaining_units=remaining,
            velocity=round(velocity, 2),
            sell_through_pct=round(sell_through, 3),
            status=status,
            weeks_of_supply=round(min(wos, 99), 1),
        )

        store_performances.append(perf)

        if status == "needs_more":
            high_performers.append(perf)
        elif status == "excess":
            underperformers.append(perf)
        else:
            on_target.append(perf)

    # DC status
    dc_available = allocation.dc_holdback
    dc_original = allocation.dc_holdback  # Could track original separately

    return {
        "has_data": True,
        "has_real_store_data": has_store_data,
        "current_week": current_week,
        "total_weeks": total_weeks,
        "weeks_remaining": total_weeks - current_week,

        # Store categorization
        "total_stores": len(store_performances),
        "high_performer_count": len(high_performers),
        "underperformer_count": len(underperformers),
        "on_target_count": len(on_target),

        # Store lists (IDs)
        "high_performers": [s.store_id for s in high_performers],
        "underperformers": [s.store_id for s in underperformers],
        "on_target_stores": [s.store_id for s in on_target],

        # Detailed performance data
        "store_performances": [s.model_dump() for s in store_performances],

        # DC status
        "dc_available": dc_available,
        "dc_min_reserve": int(dc_original * MIN_DC_RESERVE_PCT),

        # Thresholds used
        "high_performer_threshold": HIGH_PERFORMER_THRESHOLD,
        "underperformer_threshold": UNDERPERFORMER_THRESHOLD,
    }


@function_tool
def generate_transfer_recommendations(
    ctx: RunContextWrapper[ForecastingContext],
    strategy: str,
    current_week: int,
) -> dict:
    """
    Generate transfer recommendations based on selected strategy.

    Supports two strategies:
    - 'dc_only': Only release from DC to high performers
    - 'hybrid': DC release + store-to-store transfers

    Args:
        ctx: Context with allocation and performance data
        strategy: Either 'dc_only' or 'hybrid'
        current_week: Current week number

    Returns:
        Dictionary with transfer recommendations and impact projections
    """
    context = ctx.context

    if not hasattr(context, 'allocation_result') or context.allocation_result is None:
        return {
            "error": "No allocation data available",
            "has_data": False
        }

    allocation = context.allocation_result
    total_weeks = len(context.forecast_by_week) if context.forecast_by_week else 12
    weeks_remaining = total_weeks - current_week

    # First analyze performance
    perf_data = analyze_store_performance.__wrapped__(ctx, current_week)

    if not perf_data.get("has_data"):
        return perf_data

    # Rebuild StorePerformance objects
    high_performers = []
    underperformers = []

    for perf_dict in perf_data["store_performances"]:
        perf = StorePerformance(**perf_dict)
        if perf.status == "needs_more":
            high_performers.append(perf)
        elif perf.status == "excess":
            underperformers.append(perf)

    dc_available = perf_data["dc_available"]
    min_dc_reserve = perf_data["dc_min_reserve"]

    # Generate transfers based on strategy
    transfers = []

    # DC-to-Store transfers (both strategies)
    dc_transfers = generate_dc_transfers(
        high_performers=high_performers,
        dc_available=dc_available,
        weeks_remaining=weeks_remaining,
        min_dc_reserve=min_dc_reserve,
    )
    transfers.extend(dc_transfers)

    dc_released = sum(t.units for t in dc_transfers)

    # Store-to-Store transfers (hybrid only)
    store_transfers = []
    if strategy == "hybrid":
        store_transfers = generate_store_to_store_transfers(
            underperformers=underperformers,
            high_performers=high_performers,
            weeks_remaining=weeks_remaining,
        )
        transfers.extend(store_transfers)

    # Calculate totals
    total_units = sum(t.units for t in transfers)
    dc_remaining = dc_available - dc_released

    # Estimate impact
    if len(high_performers) > 0:
        stockout_risk_reduction = len([t for t in transfers if t.priority == "high"])
        sell_through_improvement = min(0.12, total_units / allocation.initial_store_allocation * 0.5)
    else:
        stockout_risk_reduction = 0
        sell_through_improvement = 0

    return {
        "has_data": True,
        "strategy": strategy,
        "current_week": current_week,
        "weeks_remaining": weeks_remaining,

        # Transfers
        "transfers": [t.model_dump() for t in transfers],
        "dc_transfer_count": len(dc_transfers),
        "store_transfer_count": len(store_transfers),
        "total_transfer_count": len(transfers),
        "total_units_to_move": total_units,

        # DC impact
        "dc_available_before": dc_available,
        "dc_released": dc_released,
        "dc_remaining_after": dc_remaining,

        # Impact projections
        "expected_sell_through_improvement": round(sell_through_improvement, 3),
        "stockout_risk_reduction": stockout_risk_reduction,

        # Stores affected
        "stores_receiving": list(set(t.to_store for t in transfers)),
        "stores_sending": list(set(t.from_location for t in transfers if t.from_location != "DC")),
    }


# =============================================================================
# Utility Functions
# =============================================================================

def should_trigger_reallocation(
    variance_pct: float,
    high_performer_count: int,
    underperformer_count: int,
    weeks_remaining: int,
    dc_available: int,
) -> Tuple[bool, str]:
    """
    Determine if strategic replenishment should be triggered.

    Args:
        variance_pct: Overall variance percentage
        high_performer_count: Number of high-performing stores
        underperformer_count: Number of underperforming stores
        weeks_remaining: Weeks remaining in season
        dc_available: Units available at DC

    Returns:
        Tuple of (should_trigger, reason)
    """
    # Must have time remaining for reallocation to be worthwhile
    if weeks_remaining < 2:
        return False, "Insufficient weeks remaining for reallocation benefit"

    # Must have DC inventory to release or stores to rebalance
    if dc_available < MIN_TRANSFER_UNITS and underperformer_count == 0:
        return False, "No inventory available for reallocation"

    # Must have stores that need inventory
    if high_performer_count == 0:
        return False, "No high-performing stores identified"

    # Trigger conditions
    if abs(variance_pct) > 0.15 and high_performer_count >= 2:
        return True, f"High variance ({variance_pct:.1%}) with {high_performer_count} stores needing inventory"

    if high_performer_count >= 3 and dc_available >= MIN_TRANSFER_UNITS * 3:
        return True, f"Multiple high-performers ({high_performer_count}) with DC inventory available"

    return False, "Reallocation conditions not met"
