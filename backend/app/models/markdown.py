from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from app.database.db import Base

class Markdown(Base):
    __tablename__ = "markdowns"

    markdown_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    sell_through_pct = Column(Float, nullable=False)
    target_sell_through_pct = Column(Float, nullable=False, default=0.60)
    gap_pct = Column(Float, nullable=False)
    recommended_markdown_pct = Column(Float, nullable=False)
    elasticity_coefficient = Column(Float, nullable=False, default=2.0)
    expected_demand_lift_pct = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="pending")
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="check_week_number"),
        CheckConstraint("sell_through_pct >= 0 AND sell_through_pct <= 1", name="check_sell_through"),
        CheckConstraint(
            "recommended_markdown_pct >= 0 AND recommended_markdown_pct <= 0.40",
            name="check_markdown_pct"
        ),
        CheckConstraint("status IN ('pending', 'approved', 'applied')", name="check_status"),
    )
