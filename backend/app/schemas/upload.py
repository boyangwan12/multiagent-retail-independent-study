"""CSV Upload Response Schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional


class HistoricalSalesUploadResponse(BaseModel):
    """Response after uploading historical sales CSV."""

    rows_imported: int = Field(..., ge=0)
    date_range: str = Field(..., description="Date range of uploaded data (e.g., '2024-01-01 to 2024-12-31')")
    categories_detected: List[str] = Field(..., description="List of categories auto-detected")


class VarianceCheckResult(BaseModel):
    """Variance check result."""

    variance_pct: float = Field(..., ge=0.0, le=1.0)
    threshold_exceeded: bool
    reforecast_triggered: bool
    forecasted_cumulative: Optional[int] = None
    actual_cumulative: Optional[int] = None
    error: Optional[str] = None


class WeeklySalesUploadResponse(BaseModel):
    """Response after uploading weekly actual sales."""

    rows_imported: int = Field(..., ge=0)
    week_number: int = Field(..., ge=1, le=52)
    variance_check: VarianceCheckResult
