from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from app.database.db import Base

class Allocation(Base):
    __tablename__ = "allocations"

    allocation_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    manufacturing_qty = Column(Integer, nullable=False)
    safety_stock_percentage = Column(Float, nullable=False, default=0.20)
    initial_allocation_total = Column(Integer, nullable=False)
    holdback_total = Column(Integer, nullable=False)

    # JSON column for variable-length store allocations
    store_allocations = Column(JSON, nullable=False)  # [{"store_id": "S01", "initial": 176, "holdback": 142}, ...]

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("manufacturing_qty >= 0", name="check_manufacturing_qty"),
        CheckConstraint("safety_stock_percentage >= 0 AND safety_stock_percentage <= 1", name="check_safety_stock"),
    )
