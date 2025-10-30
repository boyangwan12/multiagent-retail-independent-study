"""
Forecast Domain Schemas - Forecasting, Allocation, and Markdown
Consolidated from: forecast.py, allocation.py, markdown.py
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.schemas.enums import MarkdownStatus


# ============================================================================
# Forecast Schemas
# ============================================================================

class WeeklyDemand(BaseModel):
    """Weekly demand forecast point"""
    week_number: int = Field(..., description="Week number (1-52)", ge=1, le=52)
    demand_units: int = Field(..., description="Forecasted demand in units", ge=0)


class ClusterDistribution(BaseModel):
    """Demand distribution across clusters"""
    cluster_id: str = Field(..., description="Cluster ID")
    allocation_percentage: float = Field(..., description="% of total demand", ge=0, le=1)
    total_units: int = Field(..., description="Total units for cluster", ge=0)


class ForecastBase(BaseModel):
    """Base forecast fields"""
    category_id: str = Field(..., description="Category ID")
    season: str = Field(..., description="Season name (e.g., 'Spring 2025')")
    forecast_horizon_weeks: int = Field(..., description="Forecast horizon", ge=1, le=52)
    total_season_demand: int = Field(..., description="Total forecasted demand", ge=0)
    weekly_demand_curve: List[WeeklyDemand] = Field(..., description="Weekly demand breakdown")
    peak_week: int = Field(..., description="Peak demand week", ge=1, le=52)
    forecasting_method: str = Field(default="ensemble_prophet_arima", description="Forecasting method used")
    models_used: List[str] = Field(default=["prophet", "arima"], description="ML models used")
    prophet_forecast: Optional[int] = Field(None, description="Prophet model forecast", ge=0)
    arima_forecast: Optional[int] = Field(None, description="ARIMA model forecast", ge=0)


class ForecastCreate(ForecastBase):
    """Create new forecast"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "forecast_id": "FCST_001",
            "category_id": "CAT_DRESS",
            "season": "Spring 2025",
            "forecast_horizon_weeks": 12,
            "total_season_demand": 7800,
            "weekly_demand_curve": [
                {"week_number": 1, "demand_units": 450},
                {"week_number": 2, "demand_units": 680}
            ],
            "peak_week": 3,
            "forecasting_method": "ensemble_prophet_arima",
            "models_used": ["prophet", "arima"],
            "prophet_forecast": 8000,
            "arima_forecast": 7600
        }
    })
    forecast_id: str = Field(..., description="Unique forecast ID")


class Forecast(ForecastBase):
    """Forecast read model"""
    forecast_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Allocation Schemas
# ============================================================================

class StoreAllocation(BaseModel):
    """Allocation for a single store"""
    store_id: str = Field(..., description="Store ID")
    initial_allocation: int = Field(..., description="Initial units to send", ge=0)
    holdback_allocation: int = Field(..., description="Units held at DC", ge=0)


class AllocationBase(BaseModel):
    """Base allocation fields"""
    forecast_id: str = Field(..., description="Associated forecast ID")
    manufacturing_qty: int = Field(..., description="Total manufacturing quantity", ge=0)
    safety_stock_percentage: float = Field(default=0.20, description="Safety stock %", ge=0, le=1)
    initial_allocation_total: int = Field(..., description="Total initial allocation", ge=0)
    holdback_total: int = Field(..., description="Total DC holdback", ge=0)
    store_allocations: List[StoreAllocation] = Field(..., description="Per-store allocation breakdown")


class AllocationCreate(AllocationBase):
    """Create new allocation"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "allocation_id": "ALLOC_001",
            "forecast_id": "FCST_001",
            "manufacturing_qty": 9600,
            "safety_stock_percentage": 0.20,
            "initial_allocation_total": 5280,
            "holdback_total": 4320,
            "store_allocations": [
                {"store_id": "S001", "initial_allocation": 176, "holdback_allocation": 144},
                {"store_id": "S002", "initial_allocation": 88, "holdback_allocation": 72}
            ]
        }
    })
    allocation_id: str = Field(..., description="Unique allocation ID")


class AllocationPlan(AllocationBase):
    """Allocation plan read model"""
    allocation_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Markdown Schemas
# ============================================================================

class MarkdownBase(BaseModel):
    """Base markdown fields"""
    forecast_id: str = Field(..., description="Associated forecast ID")
    week_number: int = Field(..., description="Week number", ge=1, le=12)
    sell_through_pct: float = Field(..., description="Current sell-through %", ge=0, le=1)
    target_sell_through_pct: float = Field(default=0.60, description="Target sell-through %", ge=0, le=1)
    gap_pct: float = Field(..., description="Gap between target and actual", ge=-1, le=1)
    recommended_markdown_pct: float = Field(..., description="Recommended markdown %", ge=0, le=0.40)
    elasticity_coefficient: float = Field(default=2.0, description="Price elasticity coefficient", ge=0)
    expected_demand_lift_pct: Optional[float] = Field(None, description="Expected demand lift", ge=0)
    status: MarkdownStatus = Field(default=MarkdownStatus.PENDING, description="Decision status")
    reasoning: Optional[str] = Field(None, description="LLM reasoning for recommendation")


class MarkdownCreate(MarkdownBase):
    """Create new markdown decision"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "markdown_id": "MD_001",
            "forecast_id": "FCST_001",
            "week_number": 6,
            "sell_through_pct": 0.45,
            "target_sell_through_pct": 0.60,
            "gap_pct": 0.15,
            "recommended_markdown_pct": 0.15,
            "elasticity_coefficient": 2.0,
            "expected_demand_lift_pct": 0.30,
            "status": "pending",
            "reasoning": "Sell-through is 15% below target. Recommend 15% markdown to stimulate demand."
        }
    })
    markdown_id: str = Field(..., description="Unique markdown ID")


class MarkdownDecision(MarkdownBase):
    """Markdown decision read model"""
    markdown_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarkdownRequest(BaseModel):
    """Request to apply markdown"""
    markdown_id: str = Field(..., description="Markdown decision ID")
    approved: bool = Field(..., description="Whether markdown is approved")
    modified_markdown_pct: Optional[float] = Field(None, description="Modified markdown % if user changes", ge=0, le=0.40)
