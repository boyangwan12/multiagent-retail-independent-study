"""Prophet Forecasting Model (Placeholder for Phase 3)"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any


def run_prophet_forecast(
    historical_sales: pd.DataFrame,
    weeks: int = 12,
    season_start_date: str = None
) -> Dict[str, Any]:
    """Run Prophet forecasting model (PLACEHOLDER)."""
    if season_start_date is None:
        today = datetime.now()
        days_ahead = 7 - today.weekday()
        season_start_date = (today + timedelta(days=days_ahead)).date().isoformat()

    total_demand = 8000
    percentages = [0.17, 0.14, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05, 0.04, 0.03]
    weekly_curve = []
    start_date = datetime.fromisoformat(season_start_date)

    for week_num in range(1, weeks + 1):
        week_start = start_date + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6)
        weekly_units = int(total_demand * percentages[week_num - 1])

        weekly_curve.append({
            "week_number": week_num,
            "week_start_date": week_start.strftime("%Y-%m-%d"),
            "week_end_date": week_end.strftime("%Y-%m-%d"),
            "forecasted_units": weekly_units,
            "confidence_lower": int(weekly_units * 0.85),
            "confidence_upper": int(weekly_units * 1.15)
        })

    return {
        "total_season_demand": total_demand,
        "weekly_demand_curve": weekly_curve,
        "confidence_interval": {"lower": int(total_demand * 0.85), "upper": int(total_demand * 1.15)},
        "model_metadata": {
            "model": "prophet_placeholder",
            "seasonality": "weekly",
            "growth": "linear",
            "note": "Mock data for Phase 3. Actual Prophet model in Phase 5."
        }
    }
