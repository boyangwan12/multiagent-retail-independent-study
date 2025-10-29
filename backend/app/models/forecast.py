from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base

class Forecast(Base):
    __tablename__ = "forecasts"

    forecast_id = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    season = Column(String, nullable=False)
    forecast_horizon_weeks = Column(Integer, nullable=False)
    total_season_demand = Column(Integer, nullable=False)

    # JSON columns for variable-length arrays
    weekly_demand_curve = Column(JSON, nullable=False)  # [{"week_number": 1, "demand_units": 500}, ...]

    peak_week = Column(Integer, nullable=False)
    forecasting_method = Column(String, nullable=False, default="ensemble_prophet_arima")
    models_used = Column(JSON, nullable=False)  # ["prophet", "arima"]
    prophet_forecast = Column(Integer, nullable=True)
    arima_forecast = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    category = relationship("Category")

    __table_args__ = (
        CheckConstraint("total_season_demand >= 0", name="check_total_demand"),
    )
