from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional
from app.schemas.enums import ReplenishmentStrategy

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
            "markdown_threshold": 0.60,
            "extraction_confidence": "high",
            "extraction_reasoning": "User explicitly specified all 5 parameters"
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

    # Extraction metadata
    extraction_confidence: str = Field(
        default="medium",
        description="LLM confidence in extraction (high/medium/low)"
    )
    extraction_reasoning: str = Field(
        default="",
        description="LLM explanation of how parameters were extracted"
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
    success: bool = Field(..., description="Whether extraction succeeded")
    error_message: Optional[str] = Field(None, description="Error if extraction failed")