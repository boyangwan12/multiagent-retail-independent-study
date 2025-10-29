"""Pydantic schemas for approval endpoints."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional


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
