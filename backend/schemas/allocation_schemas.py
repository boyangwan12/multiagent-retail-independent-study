"""
Allocation Schemas - Structured output for Inventory Agent

These Pydantic models define the output_type for the inventory allocation agent.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ClusterAllocation(BaseModel):
    """Allocation data for a single store cluster."""

    cluster_name: str = Field(
        ...,
        description="Cluster name (e.g., 'Fashion_Forward', 'Value_Focused', 'Balanced')",
    )
    cluster_id: int = Field(
        ...,
        description="Cluster ID (0, 1, or 2)",
        ge=0,
        le=2,
    )
    store_count: int = Field(
        ...,
        description="Number of stores in this cluster",
        ge=0,
    )
    allocation_units: int = Field(
        ...,
        description="Total units allocated to this cluster",
        ge=0,
    )
    allocation_percentage: float = Field(
        ...,
        description="Percentage of total allocation (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    avg_weekly_sales: Optional[float] = Field(
        None,
        description="Average weekly sales for this cluster",
    )
    avg_store_size: Optional[float] = Field(
        None,
        description="Average store size in sqft for this cluster",
    )


class StoreAllocation(BaseModel):
    """Allocation data for a single store."""

    store_id: str = Field(
        ...,
        description="Store identifier (e.g., 'STORE001')",
    )
    allocation_units: int = Field(
        ...,
        description="Units allocated to this store",
        ge=0,
    )
    cluster: str = Field(
        ...,
        description="Cluster this store belongs to",
    )
    cluster_id: int = Field(
        ...,
        description="Cluster ID (0, 1, or 2)",
        ge=0,
        le=2,
    )
    allocation_factor: float = Field(
        ...,
        description="Store allocation factor/multiplier (typically 0.5-2.0)",
        ge=0.0,
    )


class AllocationResult(BaseModel):
    """
    Structured output from Inventory Allocation Agent.

    This is used as output_type on the inventory agent, enabling:
    - Typed access via result.final_output
    - Output guardrail validation (unit conservation)
    - Direct data passing to UI for visualization
    """

    manufacturing_qty: int = Field(
        ...,
        description="Total manufacturing quantity in units (forecast + safety stock)",
        ge=0,
    )
    dc_holdback: int = Field(
        ...,
        description="Units held back at distribution center for replenishment",
        ge=0,
    )
    dc_holdback_percentage: float = Field(
        ...,
        description="DC holdback as percentage of total (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    initial_store_allocation: int = Field(
        ...,
        description="Initial units allocated to stores (manufacturing_qty - dc_holdback)",
        ge=0,
    )
    cluster_allocations: List[ClusterAllocation] = Field(
        ...,
        description="Allocation breakdown by cluster",
        min_length=1,
    )
    store_allocations: List[StoreAllocation] = Field(
        ...,
        description="Allocation breakdown by individual store",
        min_length=1,
    )
    replenishment_strategy: str = Field(
        ...,
        description="Replenishment strategy: 'none', 'weekly', or 'bi-weekly'",
    )
    explanation: str = Field(
        ...,
        description="Agent's reasoning about the allocation decisions",
    )

    def validate_unit_conservation(self) -> bool:
        """
        Validate that units are conserved across allocation.

        Returns True if:
        - dc_holdback + initial_store_allocation == manufacturing_qty
        - sum(cluster_allocations) == initial_store_allocation
        - sum(store_allocations) == initial_store_allocation
        """
        # Check DC + stores = total
        if self.dc_holdback + self.initial_store_allocation != self.manufacturing_qty:
            return False

        # Check cluster sum
        cluster_sum = sum(c.allocation_units for c in self.cluster_allocations)
        if cluster_sum != self.initial_store_allocation:
            return False

        # Check store sum
        store_sum = sum(s.allocation_units for s in self.store_allocations)
        if store_sum != self.initial_store_allocation:
            return False

        return True
