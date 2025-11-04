"""
Workflow Domain Schemas - Orchestration, Approvals, Parameters, WebSocket
Consolidated from: workflow.py, approval.py, parameters.py, websocket.py
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Literal, Optional, Any
from app.schemas.enums import ReplenishmentStrategy, WorkflowStatus


# ============================================================================
# Parameters Schemas
# ============================================================================

class SeasonParameters(BaseModel):
    """The 5 key parameters extracted from natural language input"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "forecast_horizon_weeks": 12,
            "season_start_date": "2025-03-01",
            "season_end_date": "2025-05-23",
            "replenishment_strategy": "none",
            "dc_holdback_percentage": 0.0,
            "markdown_checkpoint_week": 6,
            "markdown_threshold": 0.60
        }
    })

    # Parameter 1: Forecast Horizon
    forecast_horizon_weeks: int = Field(
        ...,
        description="How many weeks ahead to forecast (e.g., 12, 26)",
        ge=1,
        le=52
    )

    # Parameter 2: Season Dates
    season_start_date: date = Field(
        ...,
        description="Season start date (e.g., 2025-03-01)"
    )
    season_end_date: date = Field(
        ...,
        description="Season end date (calculated from horizon)"
    )

    # Parameter 3: Replenishment Strategy
    replenishment_strategy: ReplenishmentStrategy = Field(
        ...,
        description="How often to replenish from DC to stores"
    )

    # Parameter 4: DC Holdback Strategy
    dc_holdback_percentage: float = Field(
        ...,
        description="% of inventory to hold at DC for replenishment (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    # Parameter 5: Markdown Timing
    markdown_checkpoint_week: Optional[int] = Field(
        None,
        description="Week to check sell-through and apply markdown (null = no markdowns)",
        ge=1
    )
    markdown_threshold: Optional[float] = Field(
        None,
        description="Sell-through % threshold for markdown (e.g., 0.60 = 60%)",
        ge=0.0,
        le=1.0
    )


class ParameterExtractionRequest(BaseModel):
    """Request for natural language parameter extraction"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_input": "I'm planning a 12-week spring fashion season starting March 1st. Send all inventory to stores at launch with no DC holdback."
        }
    })

    user_input: str = Field(
        ...,
        description="Natural language description of season strategy",
        min_length=10,
        max_length=1000
    )


class ParameterExtractionResponse(BaseModel):
    """Response from parameter extraction"""
    parameters: SeasonParameters = Field(..., description="Extracted parameters")
    confidence: str = Field(..., description="Extraction confidence (high/medium/low)")
    reasoning: str = Field(..., description="LLM explanation of extraction logic")
    raw_llm_output: Optional[str] = Field(None, description="Raw JSON output from LLM")


# ============================================================================
# Workflow Schemas
# ============================================================================

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


# ============================================================================
# Approval Schemas
# ============================================================================

class ManufacturingApprovalRequest(BaseModel):
    """Request to approve or modify manufacturing order."""

    workflow_id: str = Field(..., description="Workflow identifier")
    action: Literal["modify", "accept"] = Field(..., description="Approval action")
    safety_stock_pct: float = Field(..., ge=0.10, le=0.30, description="Safety stock percentage (10-30%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "safety_stock_pct": 0.25
            }
        }
    )


class ManufacturingApprovalResponse(BaseModel):
    """Response after manufacturing approval (modify or accept)."""

    workflow_id: str
    action: Literal["modify", "accept"]
    manufacturing_qty: int = Field(..., description="Recalculated manufacturing quantity")
    safety_stock_pct: float
    forecast_total: int = Field(..., description="Original forecast total")
    reasoning: str = Field(..., description="Agent reasoning for safety stock adjustment")
    status: Literal["recalculated", "approved"] = Field(..., description="recalculated if modify, approved if accept")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "manufacturing_qty": 10000,
                "safety_stock_pct": 0.25,
                "forecast_total": 8000,
                "reasoning": "Safety stock increased to 25% to account for no replenishment buffer",
                "status": "recalculated"
            }
        }
    )


class MarkdownApprovalRequest(BaseModel):
    """Request to approve or adjust markdown recommendation."""

    workflow_id: str = Field(..., description="Workflow identifier")
    action: Literal["modify", "accept"] = Field(..., description="Approval action")
    elasticity_coefficient: float = Field(..., ge=1.0, le=3.0, description="Elasticity coefficient (1.0-3.0)")
    actual_sell_through_pct: float = Field(..., ge=0.0, le=1.0, description="Actual sell-through by checkpoint week")
    target_sell_through_pct: float = Field(0.60, ge=0.0, le=1.0, description="Target sell-through (default 60%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "elasticity_coefficient": 2.5,
                "actual_sell_through_pct": 0.55,
                "target_sell_through_pct": 0.60
            }
        }
    )


class MarkdownApprovalResponse(BaseModel):
    """Response after markdown approval (modify or accept)."""

    workflow_id: str
    action: Literal["modify", "accept"]
    recommended_markdown_pct: float = Field(..., ge=0.0, le=0.40, description="Recalculated markdown %")
    elasticity_coefficient: float
    gap_pct: float = Field(..., description="Sell-through gap")
    expected_demand_lift_pct: float = Field(..., description="Expected sales increase")
    reasoning: str = Field(..., description="Markdown calculation explanation")
    status: Literal["recalculated", "approved"] = Field(..., description="recalculated if modify, approved if accept")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "action": "modify",
                "recommended_markdown_pct": 0.125,
                "elasticity_coefficient": 2.5,
                "gap_pct": 0.05,
                "expected_demand_lift_pct": 0.1875,
                "reasoning": "5.0% gap × 2.5 elasticity = 12.5% markdown",
                "status": "recalculated"
            }
        }
    )


# ============================================================================
# WebSocket Message Schemas
# ============================================================================

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


# ============================================================================
# CSV Upload Schemas
# ============================================================================

class ValidationError(BaseModel):
    """Validation error for CSV upload."""

    error_type: Literal["MISSING_COLUMN", "DATA_TYPE_MISMATCH", "EMPTY_FILE", "DUPLICATE_ROWS", "OTHER"]
    row: Optional[int] = Field(None, description="Row number where error occurred (1-indexed, excluding header)")
    column: Optional[str] = Field(None, description="Column name where error occurred")
    expected_type: Optional[str] = Field(None, description="Expected data type")
    actual_value: Optional[str] = Field(None, description="Actual value found")
    message: str = Field(..., description="Human-readable error message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_type": "DATA_TYPE_MISMATCH",
                "row": 3,
                "column": "sales_units",
                "expected_type": "integer",
                "actual_value": "N/A",
                "message": "Row 3, column 'sales_units': expected integer, got 'N/A'"
            }
        }
    )


class UploadResponse(BaseModel):
    """Response after CSV file upload."""

    workflow_id: str = Field(..., description="Workflow identifier")
    file_type: str = Field(..., description="Type of file (e.g., 'sales_data', 'store_profiles')")
    file_name: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    rows_uploaded: int = Field(..., description="Number of data rows (excluding header)")
    columns: list[str] = Field(..., description="Column names from CSV header")
    validation_status: Literal["VALID", "INVALID"] = Field(..., description="Validation result")
    errors: Optional[list[ValidationError]] = Field(None, description="Validation errors (if any)")
    uploaded_at: str = Field(..., description="ISO 8601 timestamp of upload")
    message: str = Field(..., description="Success or error message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "file_type": "sales_data",
                "file_name": "sales_data.csv",
                "file_size_bytes": 2048,
                "rows_uploaded": 50,
                "columns": ["store_id", "week", "sales_units", "sales_revenue", "inventory_on_hand"],
                "validation_status": "VALID",
                "uploaded_at": "2025-01-15T10:30:00Z",
                "message": "File uploaded successfully"
            }
        }
    )


class MultipleUploadResponse(BaseModel):
    """Response after uploading multiple CSV files."""

    workflow_id: str = Field(..., description="Workflow identifier")
    files_uploaded: list[dict] = Field(..., description="List of uploaded files with their status")
    uploaded_at: str = Field(..., description="ISO 8601 timestamp of upload")
    message: str = Field(..., description="Summary message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "wf_abc123",
                "files_uploaded": [
                    {
                        "file_type": "sales_data",
                        "file_name": "sales_data.csv",
                        "rows_uploaded": 50,
                        "validation_status": "VALID"
                    },
                    {
                        "file_type": "store_profiles",
                        "file_name": "store_profiles.csv",
                        "rows_uploaded": 50,
                        "validation_status": "VALID"
                    }
                ],
                "uploaded_at": "2025-01-15T10:30:00Z",
                "message": "2 files uploaded successfully"
            }
        }
    )
