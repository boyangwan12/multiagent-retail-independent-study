"""
Data & Resources Domain Schemas - Categories, Stores, Uploads, Variance
Consolidated from: category.py, store.py, upload.py, variance.py, data.py
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import List, Optional
from app.schemas.enums import RetailArchetype, LocationTier, FashionTier, StoreFormat, Region


# ============================================================================
# Category Schemas
# ============================================================================

class CategoryBase(BaseModel):
    """Base category fields"""
    category_name: str = Field(..., description="Display name (e.g., 'Women's Dresses')")
    season_start_date: date = Field(..., description="Season start")
    season_end_date: date = Field(..., description="Season end")
    season_length_weeks: int = Field(..., description="Duration in weeks", ge=1, le=52)
    archetype: RetailArchetype = Field(default=RetailArchetype.FASHION_RETAIL, description="Business model archetype")
    description: Optional[str] = Field(None, description="Category description")


class CategoryCreate(CategoryBase):
    """Create new category"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "category_name": "Women's Dresses",
            "season_start_date": "2025-03-01",
            "season_end_date": "2025-05-23",
            "season_length_weeks": 12,
            "archetype": "FASHION_RETAIL",
            "description": "Spring/Summer 2025 women's dresses collection"
        }
    })
    category_id: str = Field(..., description="Unique category ID")


class Category(CategoryBase):
    """Category read model"""
    category_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategorySummary(BaseModel):
    """Category summary for list view."""

    category_id: str
    category_name: str
    row_count: int = Field(..., ge=0)


# ============================================================================
# Store & Cluster Schemas
# ============================================================================

class StoreClusterBase(BaseModel):
    """Base store cluster fields"""
    cluster_name: str = Field(..., description="Cluster name (e.g., 'Premium Urban')")
    fashion_tier: FashionTier = Field(..., description="Fashion-forwardness tier")
    description: Optional[str] = Field(None, description="Cluster description")


class StoreClusterCreate(StoreClusterBase):
    """Create new store cluster"""
    cluster_id: str = Field(..., description="Unique cluster ID")


class StoreCluster(StoreClusterBase):
    """Store cluster read model"""
    cluster_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClusterSummary(BaseModel):
    """Cluster summary with store assignments."""

    cluster_id: str
    cluster_name: str
    fashion_tier: str
    store_count: int = Field(..., ge=0)
    stores: List[str] = Field(..., description="List of store IDs in cluster")


class StoreBase(BaseModel):
    """Base store fields"""
    store_name: str = Field(..., description="Store name")
    cluster_id: str = Field(..., description="Cluster assignment")
    store_size_sqft: int = Field(..., description="Store size in sq ft", ge=1000)
    location_tier: LocationTier = Field(..., description="Location quality tier")
    median_income: int = Field(..., description="Median income in area", ge=20000)
    store_format: StoreFormat = Field(..., description="Physical format")
    region: Region = Field(..., description="Geographic region")
    avg_weekly_sales_12mo: float = Field(..., description="12-month avg weekly sales", ge=0)


class StoreCreate(StoreBase):
    """Create new store"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "store_id": "S001",
            "store_name": "Flagship Manhattan",
            "cluster_id": "CLUSTER_PREMIUM",
            "store_size_sqft": 15000,
            "location_tier": "A",
            "median_income": 95000,
            "store_format": "MALL",
            "region": "NORTHEAST",
            "avg_weekly_sales_12mo": 45000.0
        }
    })
    store_id: str = Field(..., description="Unique store ID")


class Store(StoreBase):
    """Store read model"""
    store_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


# ============================================================================
# Upload Schemas
# ============================================================================

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


# ============================================================================
# Variance Schemas
# ============================================================================

class VarianceAnalysisDetail(BaseModel):
    """Variance analysis between forecast and actuals."""

    forecast_id: str
    week_number: int = Field(..., ge=1, le=52)
    forecasted_cumulative: int = Field(..., ge=0, description="Cumulative forecasted units")
    actual_cumulative: int = Field(..., ge=0, description="Cumulative actual units sold")
    variance_pct: float = Field(..., ge=0.0, le=1.0, description="Variance percentage (0.0-1.0)")
    threshold_exceeded: bool = Field(..., description="True if variance >20%")
    action_taken: str = Field(..., description="'reforecast_triggered' or 'none'")
