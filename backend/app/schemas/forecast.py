from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional

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