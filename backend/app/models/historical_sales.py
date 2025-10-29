from sqlalchemy import Column, String, Date, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database.db import Base

class HistoricalSales(Base):
    __tablename__ = "historical_sales"

    sale_id = Column(String, primary_key=True)
    store_id = Column(String, ForeignKey("stores.store_id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    units_sold = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("units_sold >= 0", name="check_units_sold"),
        Index("idx_historical_sales_store_category", "store_id", "category_id"),
        Index("idx_historical_sales_date", "week_start_date"),
    )
