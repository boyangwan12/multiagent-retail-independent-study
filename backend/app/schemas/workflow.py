from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from app.schemas.enums import WorkflowStatus
from app.schemas.parameters import SeasonParameters


class WorkflowCreateRequest(BaseModel):
    """Request to create new pre-season forecast workflow."""

    category_id: str = Field(..., description="Category to forecast (e.g., 'womens_dresses')")
    parameters: SeasonParameters = Field(..., description="Extracted season parameters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": "womens_dresses",
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
        }
    )


class ReforecastRequest(BaseModel):
    """Request to re-forecast remaining weeks due to variance."""

    forecast_id: str = Field(..., description="Original forecast ID to re-forecast")
    actual_sales_week_1_to_n: int = Field(..., description="Actual sales through week N")
    forecasted_week_1_to_n: int = Field(..., description="Original forecast through week N")
    remaining_weeks: int = Field(..., ge=1, le=12, description="Weeks remaining in season")
    variance_pct: float = Field(..., description="Variance percentage (e.g., 0.255 = 25.5%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "forecast_id": "f_spring_2025",
                "actual_sales_week_1_to_n": 3200,
                "forecasted_week_1_to_n": 2550,
                "remaining_weeks": 8,
                "variance_pct": 0.255
            }
        }
    )


class WorkflowResponse(BaseModel):
    """Response after workflow creation."""

    workflow_id: str = Field(..., description="Unique workflow identifier")
    status: Literal["pending", "running", "completed", "failed", "awaiting_approval"]
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "status": "pending",
                "websocket_url": "ws://localhost:8000/api/workflows/wf_abc123/stream"
            }
        }
    )


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status polling."""

    workflow_id: str
    workflow_type: Literal["forecast", "reforecast"]
    status: Literal["pending", "running", "completed", "failed", "awaiting_approval"]
    current_agent: Optional[str] = None
    progress_pct: int = Field(0, ge=0, le=100)
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "workflow_type": "forecast",
                "status": "running",
                "current_agent": "Inventory Agent",
                "progress_pct": 66,
                "started_at": "2025-10-12T10:30:00Z",
                "updated_at": "2025-10-12T10:30:45Z",
                "completed_at": None,
                "error_message": None
            }
        }
    )


class WorkflowResultsResponse(BaseModel):
    """Response for completed workflow results."""

    workflow_id: str
    status: Literal["completed", "failed"]
    forecast_id: Optional[str] = None
    allocation_id: Optional[str] = None
    markdown_id: Optional[str] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "status": "completed",
                "forecast_id": "f_spring_2025",
                "allocation_id": "a_spring_2025",
                "markdown_id": None,
                "output_data": {
                    "total_season_demand": 8000,
                    "manufacturing_qty": 9600,
                    "workflow_duration_seconds": 58
                },
                "error_message": None
            }
        }
    )