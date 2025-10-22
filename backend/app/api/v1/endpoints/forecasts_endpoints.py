"""Forecast Resource Endpoints"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.models.forecast import Forecast
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@router.get("", response_model=List[dict])
async def list_forecasts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all forecasts with metadata."""
    forecasts = db.query(Forecast).offset(skip).limit(limit).all()

    return [
        {
            "forecast_id": f.forecast_id,
            "category_name": f.category_id,
            "season": f"{f.season_start_date}",
            "total_season_demand": f.total_season_demand,
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
        for f in forecasts
    ]


@router.get("/{forecast_id}", response_model=dict)
async def get_forecast(
    forecast_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed forecast by ID."""
    forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Forecast '{forecast_id}' not found"
        )

    return {
        "forecast_id": forecast.forecast_id,
        "category_id": forecast.category_id,
        "total_season_demand": forecast.total_season_demand,
        "weekly_demand_curve": forecast.weekly_demand_curve or [],
        "cluster_distribution": forecast.cluster_distribution or [],
        "forecasting_method": forecast.forecasting_method or "ensemble",
        "prophet_forecast": forecast.prophet_forecast,
        "arima_forecast": forecast.arima_forecast,
        "created_at": forecast.created_at.isoformat() if forecast.created_at else None
    }
