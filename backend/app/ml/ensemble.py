"""Ensemble Forecasting (Prophet + ARIMA Average)"""

import pandas as pd
from typing import Dict, Any
from .prophet_model import run_prophet_forecast
from .arima_model import run_arima_forecast


def forecast_category_demand(
    historical_sales: pd.DataFrame,
    weeks: int = 12,
    season_start_date: str = None
) -> Dict[str, Any]:
    """Ensemble forecast combining Prophet and ARIMA (simple average)."""
    # Run both models
    prophet_result = run_prophet_forecast(historical_sales, weeks, season_start_date)
    arima_result = run_arima_forecast(historical_sales, weeks, season_start_date)

    # Average total demand
    ensemble_total = int((prophet_result["total_season_demand"] + arima_result["total_season_demand"]) / 2)

    # Average weekly curves
    ensemble_weekly = []
    for week_num in range(1, weeks + 1):
        prophet_week = prophet_result["weekly_demand_curve"][week_num - 1]
        arima_week = arima_result["weekly_demand_curve"][week_num - 1]

        ensemble_units = int((prophet_week["forecasted_units"] + arima_week["forecasted_units"]) / 2)

        ensemble_weekly.append({
            "week_number": week_num,
            "week_start_date": prophet_week["week_start_date"],
            "week_end_date": prophet_week["week_end_date"],
            "forecasted_units": ensemble_units,
            "confidence_lower": int(ensemble_units * 0.85),
            "confidence_upper": int(ensemble_units * 1.15)
        })

    return {
        "total_season_demand": ensemble_total,
        "weekly_demand_curve": ensemble_weekly,
        "prophet_forecast": prophet_result["total_season_demand"],
        "arima_forecast": arima_result["total_season_demand"],
        "confidence_interval": {"lower": int(ensemble_total * 0.85), "upper": int(ensemble_total * 1.15)},
        "model_metadata": {
            "ensemble_method": "simple_average",
            "prophet_weight": 0.5,
            "arima_weight": 0.5,
            "note": "Mock ensemble for Phase 3."
        }
    }