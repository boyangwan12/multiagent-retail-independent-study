from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.enums import LocationTier, FashionTier, StoreFormat, Region

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