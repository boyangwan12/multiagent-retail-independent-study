from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database.db import Base

class ActualSales(Base):
    __tablename__ = "actual_sales"

    actual_id = Column(String, primary_key=True)
    store_id = Column(String, ForeignKey("stores.store_id"), nullable=False)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    units_sold = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="check_week_number"),
        CheckConstraint("units_sold >= 0", name="check_units_sold"),
        Index("idx_actual_sales_forecast_week", "forecast_id", "week_number"),
    )
