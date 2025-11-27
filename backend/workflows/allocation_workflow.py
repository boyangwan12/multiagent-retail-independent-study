"""
Allocation Workflow - Store Clustering and Inventory Allocation

This workflow orchestrates the inventory agent to perform:
1. K-means store clustering (3 tiers)
2. Hierarchical inventory allocation
3. Unit conservation validation

Usage:
    allocation = await run_allocation(
        context=context,
        forecast=forecast_result,
        dc_holdback_pct=0.45,
        replenishment_strategy="weekly"
    )
"""

import logging
from typing import Optional

from agents import Runner, RunHooks

from my_agents.inventory_agent import inventory_agent
from schemas.forecast_schemas import ForecastResult
from schemas.allocation_schemas import AllocationResult
from utils.context import ForecastingContext

logger = logging.getLogger("allocation_workflow")


async def run_allocation(
    context: ForecastingContext,
    forecast: ForecastResult,
    dc_holdback_pct: float = 0.45,
    replenishment_strategy: str = "weekly",
    hooks: Optional[RunHooks] = None,
) -> AllocationResult:
    """
    Run inventory allocation with store clustering.

    This workflow:
    1. Passes forecast data to inventory agent
    2. Agent calls cluster_stores() for K-means segmentation
    3. Agent calls allocate_inventory() for hierarchical allocation
    4. Returns AllocationResult with complete allocation plan

    The inventory agent controls the details (which tools to call, how to
    interpret results), but the workflow controls WHEN it runs.

    Args:
        context: ForecastingContext with data_loader for store data
        forecast: ForecastResult from demand workflow
        dc_holdback_pct: Percentage held at DC (default: 0.45 = 45%)
        replenishment_strategy: "none", "weekly", or "bi-weekly"

    Returns:
        AllocationResult with manufacturing qty, DC holdback, and store allocations
    """
    logger.info("=" * 80)
    logger.info("WORKFLOW: Inventory Allocation")
    logger.info(f"Forecast: {forecast.total_demand} units, safety_stock={forecast.safety_stock_pct:.0%}")
    logger.info(f"DC Holdback: {dc_holdback_pct:.0%}, Replenishment: {replenishment_strategy}")
    logger.info("=" * 80)

    # Build input prompt with forecast data
    input_prompt = f"""Allocate inventory based on the following forecast:

Forecast Data:
- Total Demand: {forecast.total_demand} units
- Safety Stock: {forecast.safety_stock_pct:.0%}
- Weekly Forecast: {forecast.forecast_by_week}
- Confidence: {forecast.confidence:.0%}

Allocation Parameters:
- DC Holdback: {dc_holdback_pct:.0%}
- Replenishment Strategy: {replenishment_strategy}

Steps:
1. First, call cluster_stores() to segment stores into 3 tiers
2. Then call allocate_inventory() with the forecast data and cluster stats
3. Validate unit conservation
4. Return the allocation plan with explanation"""

    logger.info("Running inventory agent...")

    result = await Runner.run(
        starting_agent=inventory_agent,
        input=input_prompt,
        context=context,
        hooks=hooks,
    )

    allocation: AllocationResult = result.final_output

    # Log allocation summary
    logger.info(
        f"Allocation complete: manufacturing={allocation.manufacturing_qty}, "
        f"dc_holdback={allocation.dc_holdback}, "
        f"initial_allocation={allocation.initial_store_allocation}"
    )
    logger.info(f"Clusters: {len(allocation.cluster_allocations)}")
    logger.info(f"Stores: {len(allocation.store_allocations)}")

    # Validate unit conservation
    if not allocation.validate_unit_conservation():
        logger.error("UNIT CONSERVATION FAILED!")
        logger.error(
            f"DC ({allocation.dc_holdback}) + Stores ({allocation.initial_store_allocation}) "
            f"!= Manufacturing ({allocation.manufacturing_qty})"
        )
    else:
        logger.info("Unit conservation validated successfully")

    # Update context with allocation data
    context.total_allocated = allocation.initial_store_allocation

    return allocation


async def run_clustering_only(
    context: ForecastingContext,
    n_clusters: int = 3,
) -> dict:
    """
    Run store clustering without full allocation.

    Useful for analysis and visualization of store segments.

    Args:
        context: ForecastingContext with data_loader
        n_clusters: Number of clusters (default: 3)

    Returns:
        Dictionary with cluster statistics
    """
    logger.info("Running store clustering analysis...")

    # Import tool directly for standalone clustering
    from agent_tools.inventory_tools import cluster_stores
    from agents import RunContextWrapper

    # Create a minimal wrapper for the context
    class MinimalWrapper:
        def __init__(self, ctx):
            self.context = ctx

    wrapper = MinimalWrapper(context)

    # Call clustering tool directly (not via agent)
    result = cluster_stores(wrapper, n_clusters=n_clusters)

    if result.error:
        logger.error(f"Clustering failed: {result.error}")
        return {"error": result.error}

    logger.info(f"Clustering complete: {result.total_stores} stores in {n_clusters} clusters")
    logger.info(f"Silhouette score: {result.quality_metrics.silhouette_score:.4f}")

    return {
        "total_stores": result.total_stores,
        "clusters": [
            {
                "cluster_id": s.cluster_id,
                "label": s.cluster_label,
                "store_count": s.store_count,
                "allocation_pct": s.allocation_percentage,
                "avg_weekly_sales": s.avg_weekly_sales,
            }
            for s in result.cluster_stats
        ],
        "quality": {
            "silhouette_score": result.quality_metrics.silhouette_score,
            "inertia": result.quality_metrics.inertia,
        },
    }
