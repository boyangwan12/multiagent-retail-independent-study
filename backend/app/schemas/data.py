"""Data Management Schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional


class CategorySummary(BaseModel):
    """Category summary for list view."""

    category_id: str
    category_name: str
    row_count: int = Field(..., ge=0)


class StoreDetail(BaseModel):
    """Store detail with all attributes."""

    store_id: str
    store_name: str
    cluster_id: str
    store_size_sqft: int = Field(..., ge=0)
    location_tier: str
    fashion_tier: str
    store_format: str
    region: str
    median_income: int = Field(..., ge=0)
    avg_weekly_sales_12mo: Optional[float] = None


class ClusterSummary(BaseModel):
    """Cluster summary with store assignments."""

    cluster_id: str
    cluster_name: str
    fashion_tier: str
    store_count: int = Field(..., ge=0)
    stores: List[str] = Field(..., description="List of store IDs in cluster")
