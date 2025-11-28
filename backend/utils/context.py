"""
Context classes for OpenAI Agents SDK

This module defines the local context objects passed to agents and tools.
Context objects contain dependencies and runtime data but are NOT sent to the LLM.

SDK Pattern:
    @dataclass
    class UserInfo:
        name: str
        uid: int

    @function_tool
    async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:
        return f"The user {wrapper.context.name} is 47 years old"

    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,  # Pass context here
    )
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Any, Dict
from .data_loader import TrainingDataLoader


@dataclass
class ForecastingContext:
    """
    Local context for forecasting agents and tools.

    This context is passed to all agents and tools in a run but is NOT sent to the LLM.
    It provides access to:
    - data_loader: For fetching training data and historical sales
    - session_id: Unique identifier for the current user session
    - forecast_by_week: Weekly forecast values (for variance checking)
    - variance_file_path: Path to uploaded actual sales CSV
    - current_week: Current week number in the season
    - Pricing state: total_allocated, total_sold for sell-through calculation

    Usage:
        context = ForecastingContext(
            data_loader=my_data_loader,
            session_id="abc123"
        )

        result = await Runner.run(
            starting_agent=agent,
            input="user message",
            context=context  # ← Provides dependencies to tools
        )

    Access in tools via RunContextWrapper:
        @function_tool
        def my_tool(ctx: RunContextWrapper[ForecastingContext], param: str) -> str:
            data = ctx.context.data_loader.get_historical_sales("Women's Dresses")
            return f"Found {len(data['date'])} days of data"
    """

    # Required fields
    data_loader: TrainingDataLoader
    session_id: str

    # Season configuration
    season_start_date: Optional[date] = None  # For aligning forecast to calendar seasonality

    # Workflow state
    current_week: int = 0
    forecast_by_week: List[int] = field(default_factory=list)

    # Variance checking state
    variance_file_path: Optional[str] = None
    actual_sales: Optional[List[int]] = None
    variance_week: Optional[int] = None
    variance_threshold: float = 0.20

    # Pricing state (for sell-through calculation)
    total_allocated: int = 0
    total_sold: int = 0

    # Allocation state
    manufacturing_qty: int = 0
    dc_holdback: int = 0
    allocation_result: Optional[Any] = None  # AllocationResult - stored for reallocation agent

    # Store-level sales tracking (for Strategic Replenishment)
    # Maps store_id -> list of weekly sales [week1, week2, ...]
    store_actual_sales: Dict[str, List[int]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate context after initialization."""
        if self.data_loader is None:
            raise ValueError("data_loader cannot be None")
        if not self.session_id:
            raise ValueError("session_id cannot be empty")

    @property
    def has_actual_sales(self) -> bool:
        """Check if actual sales data is available for variance checking."""
        return self.actual_sales is not None and len(self.actual_sales) > 0

    @property
    def has_forecast(self) -> bool:
        """Check if forecast data is available."""
        return len(self.forecast_by_week) > 0

    def calculate_sell_through(self) -> float:
        """
        Calculate current sell-through rate.

        Returns:
            Sell-through as a fraction (0.0-1.0)
        """
        if self.total_allocated == 0:
            return 0.0
        return self.total_sold / self.total_allocated

    def add_actual_sales_to_history(self) -> None:
        """
        Add current actual sales to historical data for re-forecasting.

        This enriches the training data with recent actuals before
        generating a new forecast.
        """
        # This would update the data_loader's cached data
        # Implementation depends on how we want to handle in-memory updates
        pass

    def update_forecast(self, new_forecast: List[int]) -> None:
        """Update the stored forecast with new values."""
        self.forecast_by_week = new_forecast

    def update_allocation(self, manufacturing_qty: int, dc_holdback: int) -> None:
        """Update allocation state after inventory allocation completes."""
        self.manufacturing_qty = manufacturing_qty
        self.dc_holdback = dc_holdback
        self.total_allocated = manufacturing_qty - dc_holdback

    def record_sales(self, units_sold: int) -> None:
        """Record units sold (for sell-through tracking)."""
        self.total_sold += units_sold

    def advance_week(self) -> None:
        """Advance to the next week in the season."""
        self.current_week += 1

    # =========================================================================
    # Store-level sales methods (for Strategic Replenishment)
    # =========================================================================

    def add_store_weekly_sales(self, store_id: str, week: int, units_sold: int) -> None:
        """
        Add weekly sales data for a specific store.

        Args:
            store_id: Store identifier (e.g., "S001")
            week: Week number (1-indexed)
            units_sold: Units sold that week
        """
        if store_id not in self.store_actual_sales:
            self.store_actual_sales[store_id] = []

        # Extend list if needed to accommodate the week
        while len(self.store_actual_sales[store_id]) < week:
            self.store_actual_sales[store_id].append(0)

        # Set the value (week is 1-indexed, list is 0-indexed)
        self.store_actual_sales[store_id][week - 1] = units_sold

    def set_store_sales_from_csv(self, week: int, store_sales: Dict[str, int]) -> None:
        """
        Set store sales for a specific week from parsed CSV data.

        Args:
            week: Week number (1-indexed)
            store_sales: Dict mapping store_id -> units_sold for that week
        """
        for store_id, units_sold in store_sales.items():
            self.add_store_weekly_sales(store_id, week, units_sold)

    def get_store_cumulative_sales(self, store_id: str) -> int:
        """Get total sales for a store across all recorded weeks."""
        if store_id not in self.store_actual_sales:
            return 0
        return sum(self.store_actual_sales[store_id])

    def get_store_sales_up_to_week(self, store_id: str, week: int) -> int:
        """Get cumulative sales for a store up to (and including) a specific week."""
        if store_id not in self.store_actual_sales:
            return 0
        sales_list = self.store_actual_sales[store_id]
        return sum(sales_list[:week])

    def calculate_store_velocity(
        self,
        store_id: str,
        allocated_units: int,
        current_week: int,
        total_weeks: int = 12,
    ) -> float:
        """
        Calculate sales velocity for a store.

        Velocity = (actual_sold / allocated) / (weeks_elapsed / total_weeks)
        - velocity > 1.0 means selling faster than expected
        - velocity < 1.0 means selling slower than expected

        Args:
            store_id: Store identifier
            allocated_units: Units initially allocated to this store
            current_week: Current week number
            total_weeks: Total season length

        Returns:
            Velocity index (1.0 = on target)
        """
        if allocated_units == 0 or current_week == 0:
            return 1.0

        cumulative_sold = self.get_store_sales_up_to_week(store_id, current_week)
        expected_fraction = current_week / total_weeks
        expected_sold = allocated_units * expected_fraction

        if expected_sold == 0:
            return 1.0

        return cumulative_sold / expected_sold

    def get_all_store_velocities(self, current_week: int, total_weeks: int = 12) -> Dict[str, float]:
        """
        Calculate velocities for all stores with allocation data.

        Returns:
            Dict mapping store_id -> velocity
        """
        velocities = {}

        if self.allocation_result is None:
            return velocities

        for store_alloc in self.allocation_result.store_allocations:
            velocity = self.calculate_store_velocity(
                store_id=store_alloc.store_id,
                allocated_units=store_alloc.allocation_units,
                current_week=current_week,
                total_weeks=total_weeks,
            )
            velocities[store_alloc.store_id] = velocity

        return velocities

    @property
    def has_store_sales(self) -> bool:
        """Check if per-store sales data is available."""
        return len(self.store_actual_sales) > 0
