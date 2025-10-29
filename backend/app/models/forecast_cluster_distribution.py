from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from app.database.db import Base

class ForecastClusterDistribution(Base):
    __tablename__ = "forecast_cluster_distribution"

    distribution_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    cluster_id = Column(String, ForeignKey("store_clusters.cluster_id"), nullable=False)
    allocation_percentage = Column(Float, nullable=False)
    total_units = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "allocation_percentage >= 0 AND allocation_percentage <= 1",
            name="check_allocation_pct"
        ),
        CheckConstraint("total_units >= 0", name="check_total_units"),
    )
