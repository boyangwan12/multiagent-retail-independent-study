"""WebSocket message schemas for real-time agent updates."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Any


class AgentStartedMessage(BaseModel):
    """Message sent when agent begins execution."""

    type: Literal["agent_started"] = "agent_started"
    agent: str = Field(..., description="Agent name (e.g., 'Demand Agent', 'Inventory Agent', 'Pricing Agent')")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "agent_started",
                "agent": "Demand Agent",
                "timestamp": "2025-10-12T10:30:15Z"
            }
        }
    )


class AgentProgressMessage(BaseModel):
    """Message sent during agent execution (line-by-line updates)."""

    type: Literal["agent_progress"] = "agent_progress"
    agent: str = Field(..., description="Agent name")
    message: str = Field(..., description="Progress message (e.g., 'Running Prophet forecasting model...')")
    progress_pct: int = Field(..., ge=0, le=100, description="Overall workflow progress (0-100)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "agent_progress",
                "agent": "Demand Agent",
                "message": "Running Prophet forecasting model...",
                "progress_pct": 33,
                "timestamp": "2025-10-12T10:30:20Z"
            }
        }
    )


class AgentCompletedMessage(BaseModel):
    """Message sent when agent finishes execution."""

    type: Literal["agent_completed"] = "agent_completed"
    agent: str = Field(..., description="Agent name")
    duration_seconds: float = Field(..., description="Agent execution time in seconds")
    result: Optional[dict] = Field(None, description="Agent output (optional)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "agent_completed",
                "agent": "Demand Agent",
                "duration_seconds": 15.3,
                "result": {
                    "total_season_demand": 8000,
                    "prophet_forecast": 8200,
                    "arima_forecast": 7800
                },
                "timestamp": "2025-10-12T10:30:30Z"
            }
        }
    )


class HumanInputRequiredMessage(BaseModel):
    """Message sent when agent needs human approval."""

    type: Literal["human_input_required"] = "human_input_required"
    agent: str = Field(..., description="Agent name")
    action: str = Field(..., description="Action identifier (e.g., 'approve_manufacturing_order', 'approve_markdown')")
    data: dict = Field(..., description="Data for approval modal")
    options: list[str] = Field(..., description="Available actions (e.g., ['modify', 'accept'])")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "human_input_required",
                "agent": "Inventory Agent",
                "action": "approve_manufacturing_order",
                "data": {
                    "manufacturing_qty": 9600,
                    "initial_allocation": 5280,
                    "holdback": 4320,
                    "safety_stock_pct": 0.20
                },
                "options": ["modify", "accept"],
                "timestamp": "2025-10-12T10:30:45Z"
            }
        }
    )


class WorkflowCompleteMessage(BaseModel):
    """Message sent when entire workflow finishes."""

    type: Literal["workflow_complete"] = "workflow_complete"
    workflow_id: str = Field(..., description="Workflow identifier")
    duration_seconds: float = Field(..., description="Total workflow execution time")
    result: dict = Field(..., description="Final workflow results")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "workflow_complete",
                "workflow_id": "wf_abc123",
                "duration_seconds": 58.7,
                "result": {
                    "forecast_id": "f_spring_2025",
                    "allocation_id": "a_spring_2025",
                    "total_season_demand": 8000,
                    "manufacturing_qty": 9600
                },
                "timestamp": "2025-10-12T10:30:58Z"
            }
        }
    )


class ErrorMessage(BaseModel):
    """Message sent when agent encounters error."""

    type: Literal["error"] = "error"
    agent: Optional[str] = Field(None, description="Agent name (null if orchestrator error)")
    error_message: str = Field(..., description="Error description")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "error",
                "agent": "Demand Agent",
                "error_message": "Prophet model failed to converge: insufficient historical data",
                "timestamp": "2025-10-12T10:30:25Z"
            }
        }
    )


# Union type for all message types
WebSocketMessage = (
    AgentStartedMessage
    | AgentProgressMessage
    | AgentCompletedMessage
    | HumanInputRequiredMessage
    | WorkflowCompleteMessage
    | ErrorMessage
)
