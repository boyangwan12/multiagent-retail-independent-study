"""Variance Tracking Endpoints"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime

from app.database.db import get_db
from app.database.models import ActualSales, Store, Forecast
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/variance", tags=["Variance"])


@router.get("/{forecast_id}/week/{week_number}")
async def get_weekly_variance(
    forecast_id: str,
    week_number: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get variance data for a specific week.
    Returns cumulative forecast vs actuals with store-level breakdown.
    """
    try:
        # Get the forecast
        forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forecast '{forecast_id}' not found"
            )

        # Get cumulative forecasted demand from weekly_demand_curve
        weekly_curve = forecast.weekly_demand_curve or []
        if not weekly_curve:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No weekly demand curve found"
            )

        # Calculate cumulative forecast for weeks 1 through week_number
        forecasted_cumulative = sum(
            week.get("demand_units", 0)
            for week in weekly_curve[:week_number]
        )

        # Check if actuals exist for THIS specific week (not just previous weeks)
        week_specific_actuals = db.query(ActualSales).filter(
            ActualSales.forecast_id == forecast_id,
            ActualSales.week_number == week_number
        ).first()

        if not week_specific_actuals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No actuals data found for week {week_number}"
            )

        # Get all actual sales up to this week for cumulative calculation
        actuals_list = db.query(ActualSales).filter(
            ActualSales.forecast_id == forecast_id,
            ActualSales.week_number <= week_number
        ).all()

        # Calculate cumulative actuals
        actual_cumulative = sum(a.units_sold for a in actuals_list)

        # Calculate variance percentage
        if forecasted_cumulative > 0:
            variance_pct = ((actual_cumulative - forecasted_cumulative) / forecasted_cumulative) * 100
        else:
            variance_pct = 0.0

        # Get store-level breakdown for this specific week
        week_actuals = db.query(ActualSales, Store).join(
            Store, ActualSales.store_id == Store.store_id
        ).filter(
            ActualSales.forecast_id == forecast_id,
            ActualSales.week_number == week_number
        ).all()

        # Get forecasted units for this specific week
        week_forecasted = weekly_curve[week_number - 1].get("demand_units", 0) if week_number <= len(weekly_curve) else 0

        # Calculate store count and average forecast per store
        store_count = len(week_actuals)
        avg_forecast_per_store = week_forecasted / store_count if store_count > 0 else 0

        store_level_variance = []
        for actual, store in week_actuals:
            store_actual = actual.units_sold

            # Use average forecast per store as the store-level forecast
            store_forecasted = avg_forecast_per_store

            if store_forecasted > 0:
                store_variance_pct = ((store_actual - store_forecasted) / store_forecasted) * 100
            else:
                store_variance_pct = 0.0

            store_level_variance.append({
                "store_id": actual.store_id,
                "store_name": store.store_name,
                "forecasted": int(store_forecasted),
                "actual": store_actual,
                "variance_pct": round(store_variance_pct, 2)
            })

        # Determine if threshold exceeded (using 20% as threshold)
        threshold_exceeded = abs(variance_pct) > 20.0

        return {
            "forecast_id": forecast_id,
            "week_number": week_number,
            "forecasted_cumulative": forecasted_cumulative,
            "actual_cumulative": actual_cumulative,
            "variance_pct": round(variance_pct, 2),
            "threshold_exceeded": threshold_exceeded,
            "action_taken": "Review inventory allocation" if threshold_exceeded else None,
            "store_level_variance": store_level_variance
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating variance for week {week_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating variance: {str(e)}"
        )


@router.get("/{forecast_id}/summary")
async def get_variance_summary(
    forecast_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get variance summary across all weeks.
    """
    try:
        # Get the forecast
        forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()
        if not forecast:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forecast '{forecast_id}' not found"
            )

        # Get weekly demand curve
        weekly_curve = forecast.weekly_demand_curve or []
        if not weekly_curve:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No weekly demand curve found"
            )

        # Get all actual sales
        actuals_list = db.query(ActualSales).filter(
            ActualSales.forecast_id == forecast_id
        ).all()

        if not actuals_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No actuals data found"
            )

        # Get unique weeks with data
        weeks_with_data = sorted(set(a.week_number for a in actuals_list))
        latest_week = max(weeks_with_data) if weeks_with_data else 0

        # Calculate total forecast for weeks with data
        total_forecasted = sum(
            week.get("demand_units", 0)
            for i, week in enumerate(weekly_curve)
            if (i + 1) in weeks_with_data
        )

        # Calculate total actual
        total_actual = sum(a.units_sold for a in actuals_list)

        # Calculate overall variance
        if total_forecasted > 0:
            overall_variance_pct = ((total_actual - total_forecasted) / total_forecasted) * 100
        else:
            overall_variance_pct = 0.0

        return {
            "forecast_id": forecast_id,
            "total_forecasted": total_forecasted,
            "total_actual": total_actual,
            "overall_variance_pct": round(overall_variance_pct, 2),
            "weeks_with_data": len(weeks_with_data),
            "latest_week": latest_week
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating variance summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating variance summary: {str(e)}"
        )
