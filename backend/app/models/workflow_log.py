from sqlalchemy import Column, String, JSON, Float, Text, DateTime, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database.db import Base

class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    log_id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('started', 'completed', 'failed')", name="check_status"),
        Index("idx_workflow_logs_workflow", "workflow_id"),
    )