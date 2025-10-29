from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List

class StoreAllocation(BaseModel):
    """Allocation for a single store"""
    store_id: str = Field(..., description="Store ID")
    initial_allocation: int = Field(..., description="Initial units to send", ge=0)
    holdback_allocation: int = Field(..., description="Units held at DC", ge=0)

class AllocationBase(BaseModel):
    """Base allocation fields"""
    forecast_id: str = Field(..., description="Associated forecast ID")
    manufacturing_qty: int = Field(..., description="Total manufacturing quantity", ge=0)
    safety_stock_percentage: float = Field(default=0.20, description="Safety stock %", ge=0, le=1)
    initial_allocation_total: int = Field(..., description="Total initial allocation", ge=0)
    holdback_total: int = Field(..., description="Total DC holdback", ge=0)
    store_allocations: List[StoreAllocation] = Field(..., description="Per-store allocation breakdown")

class AllocationCreate(AllocationBase):
    """Create new allocation"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "allocation_id": "ALLOC_001",
            "forecast_id": "FCST_001",
            "manufacturing_qty": 9600,
            "safety_stock_percentage": 0.20,
            "initial_allocation_total": 5280,
            "holdback_total": 4320,
            "store_allocations": [
                {"store_id": "S001", "initial_allocation": 176, "holdback_allocation": 144},
                {"store_id": "S002", "initial_allocation": 88, "holdback_allocation": 72}
            ]
        }
    })
    allocation_id: str = Field(..., description="Unique allocation ID")

class AllocationPlan(AllocationBase):
    """Allocation plan read model"""
    allocation_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)