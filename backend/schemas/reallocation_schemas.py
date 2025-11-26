"""
Reallocation Schemas

Pydantic models for Strategic Replenishment / Reallocation functionality.
These schemas define the structured output from the reallocation agent.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class StorePerformance(BaseModel):
    """Performance metrics for a single store."""

    store_id: str = Field(description="Store identifier")
    cluster: str = Field(description="Store cluster (e.g., Fashion_Forward, Mainstream)")
    allocated_units: int = Field(description="Initial allocation to this store")
    sold_units: int = Field(description="Units sold to date")
    remaining_units: int = Field(description="Current inventory remaining")
    velocity: float = Field(description="Sales velocity index (1.0 = on target)")
    sell_through_pct: float = Field(description="Sell-through percentage")
    status: str = Field(description="'needs_more', 'on_target', or 'excess'")
    weeks_of_supply: float = Field(description="Estimated weeks until stockout at current rate")


class TransferOrder(BaseModel):
    """A single inventory transfer recommendation."""

    from_location: str = Field(description="Source location: 'DC' or store_id")
    to_store: str = Field(description="Destination store_id")
    units: int = Field(description="Number of units to transfer")
    priority: str = Field(description="Transfer priority: 'high', 'medium', 'low'")
    reason: str = Field(description="Reason for this transfer")

    # Optional: logistics metadata
    estimated_transit_days: Optional[int] = Field(
        default=None,
        description="Estimated days for transfer to complete"
    )


class ReallocationAnalysis(BaseModel):
    """
    Structured output from the Strategic Replenishment Agent.

    This represents the agent's complete analysis and recommendations
    for inventory reallocation based on variance and performance data.
    """

    # Decision
    should_reallocate: bool = Field(
        description="Whether strategic replenishment is recommended"
    )

    # Strategy selection
    strategy: str = Field(
        description="Selected strategy: 'dc_only' or 'hybrid'"
    )
    strategy_reasoning: str = Field(
        description="Why this strategy was selected"
    )

    # DC status
    dc_units_available: int = Field(description="Units currently available at DC")
    dc_units_to_release: int = Field(description="Units recommended to release from DC")
    dc_remaining_after: int = Field(description="DC units remaining after reallocation")

    # Store analysis
    high_performers: List[str] = Field(
        default_factory=list,
        description="Store IDs with velocity > 1.15 (need more inventory)"
    )
    underperformers: List[str] = Field(
        default_factory=list,
        description="Store IDs with velocity < 0.85 (have excess inventory)"
    )
    on_target_stores: List[str] = Field(
        default_factory=list,
        description="Store IDs with velocity 0.85-1.15 (no change needed)"
    )

    # Transfer recommendations
    transfers: List[TransferOrder] = Field(
        default_factory=list,
        description="List of recommended transfers"
    )
    total_units_to_move: int = Field(
        description="Total units across all transfers"
    )

    # Impact projections
    expected_sell_through_improvement: float = Field(
        ge=0.0, le=1.0,
        description="Expected improvement in overall sell-through (0-1)"
    )
    stockout_risk_reduction: int = Field(
        description="Number of stores with reduced stockout risk"
    )

    # Confidence and explanation
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Agent's confidence in this recommendation (0-1)"
    )
    explanation: str = Field(
        description="Full explanation of analysis for the user"
    )

    # Metadata
    analysis_week: int = Field(description="Week number when analysis was performed")
    weeks_remaining: int = Field(description="Weeks remaining in season")


class ReallocationResult(BaseModel):
    """
    Result after applying reallocation transfers.

    This tracks the actual execution of transfers and updated allocations.
    """

    # Original analysis
    analysis: ReallocationAnalysis = Field(
        description="The analysis that triggered this reallocation"
    )

    # Execution status
    transfers_executed: List[TransferOrder] = Field(
        default_factory=list,
        description="Transfers that were executed"
    )
    transfers_skipped: List[TransferOrder] = Field(
        default_factory=list,
        description="Transfers that were skipped (user choice or constraint)"
    )

    # Updated allocations
    updated_store_allocations: Dict[str, int] = Field(
        default_factory=dict,
        description="New allocation by store after transfers"
    )
    updated_dc_holdback: int = Field(
        description="DC holdback after releases"
    )

    # Execution metadata
    executed_at_week: int = Field(description="Week when reallocation was executed")
    total_units_moved: int = Field(description="Actual units moved")
