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
from typing import List, Optional
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
