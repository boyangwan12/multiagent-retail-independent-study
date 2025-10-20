from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from app.schemas.enums import WorkflowStatus
from app.schemas.parameters import SeasonParameters

class AgentStatus(BaseModel):
    """Status update from an agent"""
    agent_name: str = Field(..., description="Agent name (e.g., 'Demand Agent')")
    status: WorkflowStatus = Field(..., description="Current status")
    message: str = Field(..., description="Status message")
    progress_pct: Optional[float] = Field(None, description="Progress percentage (0-100)", ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")

class WorkflowRequest(BaseModel):
    """Request to start a workflow"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "category_id": "CAT_DRESS",
            "parameters": {
                "forecast_horizon_weeks": 12,
                "season_start_date": "2025-03-01",
                "season_end_date": "2025-05-23",
                "replenishment_strategy": "none",
                "dc_holdback_percentage": 0.0,
                "markdown_checkpoint_week": 6,
                "markdown_threshold": 0.60
            }
        }
    })

    category_id: str = Field(..., description="Category to forecast")
    parameters: SeasonParameters = Field(..., description="Season parameters")

class WorkflowResponse(BaseModel):
    """Response from workflow creation"""
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: WorkflowStatus = Field(..., description="Initial status")
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

class WorkflowStatusResponse(BaseModel):
    """Response for workflow status check"""
    workflow_id: str
    status: WorkflowStatus
    current_agent: Optional[str] = Field(None, description="Currently executing agent")
    progress_pct: Optional[float] = Field(None, description="Overall progress", ge=0, le=100)
    forecast_id: Optional[str] = Field(None, description="Generated forecast ID if complete")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime
    completed_at: Optional[datetime] = None

class WorkflowResultResponse(BaseModel):
    """Final workflow results"""
    workflow_id: str
    forecast_id: str = Field(..., description="Generated forecast ID")
    allocation_id: str = Field(..., description="Generated allocation ID")
    markdown_id: Optional[str] = Field(None, description="Markdown decision ID if applicable")
    duration_seconds: float = Field(..., description="Total execution time")
    agents_executed: list[str] = Field(..., description="List of agents that ran")