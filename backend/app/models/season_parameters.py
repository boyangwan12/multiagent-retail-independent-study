from sqlalchemy import Column, String, Date, Integer, Float, DateTime, CheckConstraint
from sqlalchemy.sql import func
from app.database.db import Base

class SeasonParameters(Base):
    __tablename__ = "season_parameters"

    parameter_id = Column(String, primary_key=True)
    forecast_horizon_weeks = Column(Integer, nullable=False, default=12)
    season_start_date = Column(Date, nullable=False)
    replenishment_strategy = Column(String, nullable=False, default="weekly")
    dc_holdback_percentage = Column(Float, nullable=False, default=0.45)
    markdown_checkpoint_week = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("forecast_horizon_weeks >= 1 AND forecast_horizon_weeks <= 52", name="check_horizon_weeks"),
        CheckConstraint(
            "replenishment_strategy IN ('none', 'weekly', 'bi-weekly')",
            name="check_replenishment_strategy"
        ),
        CheckConstraint("dc_holdback_percentage >= 0 AND dc_holdback_percentage <= 1", name="check_holdback_pct"),
        CheckConstraint("markdown_checkpoint_week IS NULL OR (markdown_checkpoint_week >= 1 AND markdown_checkpoint_week <= 12)", name="check_markdown_week"),
    )