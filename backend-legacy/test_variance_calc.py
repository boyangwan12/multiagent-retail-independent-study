"""Test variance calculation logic"""
from app.database.db import SessionLocal
from app.database.models import Forecast, ActualSales

db = SessionLocal()

forecast_id = "f_wf_4e7a56129115"
week_number = 1

# Get forecast
forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()

print(f"Forecast ID: {forecast.forecast_id}")
print(f"Weekly demand curve type: {type(forecast.weekly_demand_curve)}")
print(f"Weekly demand curve: {forecast.weekly_demand_curve}")

# Calculate cumulative forecast
weekly_curve = forecast.weekly_demand_curve or []
forecasted_cumulative = sum(
    week.get("demand_units", 0)
    for week in weekly_curve[:week_number]
)

print(f"\nWeek {week_number} forecasted cumulative: {forecasted_cumulative}")

# Get actuals
actuals = db.query(ActualSales).filter(
    ActualSales.forecast_id == forecast_id,
    ActualSales.week_number <= week_number
).all()

actual_cumulative = sum(a.units_sold for a in actuals)

print(f"Week {week_number} actual cumulative: {actual_cumulative}")

if forecasted_cumulative > 0:
    variance_pct = ((actual_cumulative - forecasted_cumulative) / forecasted_cumulative) * 100
else:
    variance_pct = 0.0

print(f"Variance: {variance_pct:.2f}%")

db.close()
