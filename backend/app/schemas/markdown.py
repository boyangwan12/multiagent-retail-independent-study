from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.enums import MarkdownStatus

class MarkdownBase(BaseModel):
    """Base markdown fields"""
    forecast_id: str = Field(..., description="Associated forecast ID")
    week_number: int = Field(..., description="Week number", ge=1, le=12)
    sell_through_pct: float = Field(..., description="Current sell-through %", ge=0, le=1)
    target_sell_through_pct: float = Field(default=0.60, description="Target sell-through %", ge=0, le=1)
    gap_pct: float = Field(..., description="Gap between target and actual", ge=-1, le=1)
    recommended_markdown_pct: float = Field(..., description="Recommended markdown %", ge=0, le=0.40)
    elasticity_coefficient: float = Field(default=2.0, description="Price elasticity coefficient", ge=0)
    expected_demand_lift_pct: Optional[float] = Field(None, description="Expected demand lift", ge=0)
    status: MarkdownStatus = Field(default=MarkdownStatus.PENDING, description="Decision status")
    reasoning: Optional[str] = Field(None, description="LLM reasoning for recommendation")

class MarkdownCreate(MarkdownBase):
    """Create new markdown decision"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "markdown_id": "MD_001",
            "forecast_id": "FCST_001",
            "week_number": 6,
            "sell_through_pct": 0.45,
            "target_sell_through_pct": 0.60,
            "gap_pct": 0.15,
            "recommended_markdown_pct": 0.15,
            "elasticity_coefficient": 2.0,
            "expected_demand_lift_pct": 0.30,
            "status": "pending",
            "reasoning": "Sell-through is 15% below target. Recommend 15% markdown to stimulate demand."
        }
    })
    markdown_id: str = Field(..., description="Unique markdown ID")

class MarkdownDecision(MarkdownBase):
    """Markdown decision read model"""
    markdown_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MarkdownRequest(BaseModel):
    """Request to apply markdown"""
    markdown_id: str = Field(..., description="Markdown decision ID")
    approved: bool = Field(..., description="Whether markdown is approved")
    modified_markdown_pct: Optional[float] = Field(None, description="Modified markdown % if user changes", ge=0, le=0.40)