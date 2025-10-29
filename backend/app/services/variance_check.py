"""Variance Check Service"""

from sqlalchemy.orm import Session
import logging

from app.models.forecast import Forecast
from app.models.actual_sales import ActualSales


logger = logging.getLogger(__name__)


def check_variance_and_trigger_reforecast(
    db: Session,
    forecast_id: str,
    week_number: int
) -> dict:
    """Check variance and trigger re-forecast if threshold exceeded."""

    # Get forecast
    forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()

    if not forecast:
        return {
            "variance_pct": 0.0,
            "threshold_exceeded": False,
            "reforecast_triggered": False,
            "error": "Forecast not found"
        }

    # Get cumulative forecasted demand
    weekly_curve = forecast.weekly_demand_curve or []
    if not weekly_curve:
        return {
            "variance_pct": 0.0,
            "threshold_exceeded": False,
            "reforecast_triggered": False,
            "error": "No weekly demand curve found"
        }

    forecasted_cumulative = sum(
        week.get("forecasted_units", 0)
        for week in weekly_curve[:week_number]
    )

    # Get cumulative actual sales
    actuals = db.query(ActualSales).filter(
        ActualSales.forecast_id == forecast_id,
        ActualSales.week_number <= week_number
    ).all()

    if not actuals:
        return {
            "variance_pct": 0.0,
            "threshold_exceeded": False,
            "reforecast_triggered": False,
            "error": "No actual sales data found"
        }

    actual_cumulative = sum(a.units_sold for a in actuals)

    # Calculate variance
    if forecasted_cumulative == 0:
        variance_pct = 0.0
    else:
        variance_pct = abs(actual_cumulative - forecasted_cumulative) / forecasted_cumulative

    threshold_exceeded = variance_pct > 0.20

    # Trigger re-forecast if threshold exceeded
    reforecast_triggered = False
    if threshold_exceeded:
        logger.warning(
            f"Variance threshold exceeded for forecast {forecast_id} week {week_number}: "
            f"{variance_pct*100:.1f}% (threshold: 20%)"
        )
        reforecast_triggered = True

    return {
        "variance_pct": variance_pct,
        "threshold_exceeded": threshold_exceeded,
        "reforecast_triggered": reforecast_triggered,
        "forecasted_cumulative": forecasted_cumulative,
        "actual_cumulative": actual_cumulative
    }
