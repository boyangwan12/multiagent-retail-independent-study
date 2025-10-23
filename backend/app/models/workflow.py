from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, JSON
from sqlalchemy.sql import func
import enum
from app.database.db import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow status enum."""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    awaiting_approval = "awaiting_approval"


class Workflow(Base):
    """Workflow session model."""
    __tablename__ = "workflows"

    workflow_id = Column(String, primary_key=True, index=True)
    workflow_type = Column(String, nullable=False)  # "forecast" or "reforecast"
    forecast_id = Column(String, nullable=True)  # FK to forecasts (null for initial forecast)
    category_id = Column(String, nullable=False)

    # Status tracking
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.pending, nullable=False)
    current_agent = Column(String, nullable=True)  # "demand", "inventory", "pricing", null
    progress_pct = Column(Integer, default=0)

    # Session parameters (from SeasonParameters)
    forecast_horizon_weeks = Column(Integer, nullable=False)
    season_start_date = Column(String, nullable=False)
    replenishment_strategy = Column(String, nullable=False)
    dc_holdback_percentage = Column(Float, nullable=False)
    markdown_checkpoint_week = Column(Integer, nullable=True)

    # Workflow context (JSON)
    input_data = Column(JSON, nullable=True)  # Original request body
    output_data = Column(JSON, nullable=True)  # Final results
    error_message = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
