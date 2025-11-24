"""
Structured Output Schemas for Agent Responses

Using Pydantic models to define structured outputs for agents.
The OpenAI Agents SDK will automatically enforce these schemas,
eliminating the need for brittle regex parsing.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# =============================================================================
# DEMAND FORECASTING OUTPUT SCHEMA
# =============================================================================

class WeeklyForecast(BaseModel):
    """Forecast data for a single week"""
    week: int = Field(..., description="Week number (1-52)")
    demand: int = Field(..., description="Forecasted demand in units")
    lower_bound: Optional[int] = Field(None, description="Lower confidence bound")
    upper_bound: Optional[int] = Field(None, description="Upper confidence bound")


class DemandForecastOutput(BaseModel):
    """Structured output from the Demand Forecasting Agent"""
    total_demand: int = Field(..., description="Total forecasted demand in units")
    weekly_average: int = Field(..., description="Average weekly demand in units")
    safety_stock_pct: float = Field(..., ge=0.0, le=1.0, description="Safety stock percentage (0.0-1.0)")
    confidence: int = Field(..., ge=0, le=100, description="Forecast confidence percentage (0-100)")
    forecast_by_week: List[WeeklyForecast] = Field(..., description="Weekly breakdown of forecast")
    model_used: str = Field(..., description="Forecasting model used (e.g., 'prophet_arima_ensemble')")
    data_quality: str = Field(..., description="Data quality assessment (excellent/good/poor)")
    summary: str = Field(..., description="Human-readable summary of the forecast")


# =============================================================================
# INVENTORY ALLOCATION OUTPUT SCHEMA
# =============================================================================

class ClusterAllocation(BaseModel):
    """Allocation data for a single cluster"""
    cluster_name: str = Field(..., description="Cluster name (e.g., 'Fashion_Forward')")
    cluster_id: int = Field(..., description="Cluster ID (0, 1, 2)")
    store_count: int = Field(..., description="Number of stores in cluster")
    allocation_units: int = Field(..., description="Total units allocated to cluster")
    allocation_percentage: float = Field(..., description="Percentage of total allocation")
    avg_weekly_sales: Optional[float] = Field(None, description="Average weekly sales for cluster")
    avg_store_size: Optional[float] = Field(None, description="Average store size in sqft")


class StoreAllocation(BaseModel):
    """Allocation data for a single store"""
    store_id: str = Field(..., description="Store identifier (e.g., 'STORE001')")
    allocation_units: int = Field(..., description="Units allocated to this store")
    cluster: str = Field(..., description="Cluster this store belongs to")
    allocation_factor: float = Field(..., description="Store allocation factor/multiplier")


class InventoryAllocationOutput(BaseModel):
    """Structured output from the Inventory Allocation Agent"""
    manufacturing_qty: int = Field(..., description="Total manufacturing quantity in units")
    dc_holdback: int = Field(..., description="Units held back at distribution center")
    dc_holdback_percentage: float = Field(..., description="DC holdback as percentage (0.0-1.0)")
    initial_store_allocation: int = Field(..., description="Initial units allocated to stores")
    cluster_allocations: List[ClusterAllocation] = Field(..., description="Allocation by cluster")
    store_allocations: List[StoreAllocation] = Field(..., description="Allocation by store")
    replenishment_strategy: str = Field(..., description="Replenishment strategy used")
    summary: str = Field(..., description="Human-readable summary of the allocation")


# =============================================================================
# VARIANCE CHECK OUTPUT SCHEMA
# =============================================================================

class VarianceCheckOutput(BaseModel):
    """Structured output from variance checking"""
    week_number: int = Field(..., description="Week number being checked")
    actual_total: int = Field(..., description="Actual sales in units")
    forecast_total: int = Field(..., description="Forecasted sales in units")
    variance_units: int = Field(..., description="Variance in units (actual - forecast)")
    variance_pct: float = Field(..., description="Variance as percentage")
    threshold_pct: float = Field(..., description="Threshold used for high variance detection")
    is_high_variance: bool = Field(..., description="Whether variance exceeds threshold")
    recommendation: str = Field(..., description="Recommended action")
    reforecast_needed: bool = Field(..., description="Whether re-forecasting is recommended")
    summary: str = Field(..., description="Human-readable summary of variance analysis")
