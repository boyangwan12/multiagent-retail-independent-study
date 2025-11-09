"""
Mock agents for testing handoff framework.

These mock agents simulate the behavior of real demand, inventory, and pricing agents
without requiring actual ML models or complex business logic.
"""

import asyncio
import logging
from typing import Dict, Any
from app.schemas.workflow_schemas import SeasonParameters

logger = logging.getLogger("fashion_forecast")


async def mock_demand_agent(context: SeasonParameters) -> Dict[str, Any]:
    """
    Mock Demand Agent for testing handoff framework.

    Args:
        context: Season parameters from parameter extraction

    Returns:
        Dictionary mimicking forecast result structure
    """
    await asyncio.sleep(0.5)  # Simulate processing time

    # Adapt safety stock based on replenishment strategy (demonstrates parameter awareness)
    if context.replenishment_strategy == "none":
        safety_stock = 1.25  # 25% for no replenishment
        safety_stock_reasoning = "25% safety stock for no replenishment (need full buffer upfront)"
    elif context.replenishment_strategy == "weekly":
        safety_stock = 1.20  # 20% for weekly
        safety_stock_reasoning = "20% safety stock for weekly replenishment (can restock frequently)"
    else:  # bi-weekly
        safety_stock = 1.22  # 22% for bi-weekly
        safety_stock_reasoning = "22% safety stock for bi-weekly replenishment (moderate buffer)"

    logger.info(f"[MOCK] Demand Agent: Using {(safety_stock - 1) * 100}% safety stock for '{context.replenishment_strategy}' strategy")

    # Adapt forecast horizon to match user input
    baseline_curve = [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480]

    if context.forecast_horizon_weeks < 12:
        weekly_curve = baseline_curve[:context.forecast_horizon_weeks]
        horizon_reasoning = f"Truncated baseline curve to {context.forecast_horizon_weeks} weeks"
    elif context.forecast_horizon_weeks > 12:
        # Extend with average
        avg = sum(baseline_curve) // len(baseline_curve)
        weekly_curve = baseline_curve + [avg] * (context.forecast_horizon_weeks - 12)
        horizon_reasoning = f"Extended baseline curve to {context.forecast_horizon_weeks} weeks using average weekly demand"
    else:
        weekly_curve = baseline_curve
        horizon_reasoning = "Using standard 12-week baseline curve"

    total_forecast = sum(weekly_curve)

    return {
        "agent": "demand",
        "total_forecast": total_forecast,
        "safety_stock_multiplier": safety_stock,
        "weekly_curve": weekly_curve,
        "clusters": ["Fashion_Forward", "Mainstream", "Value_Conscious"],
        "reasoning": {
            "safety_stock": safety_stock_reasoning,
            "forecast_horizon": horizon_reasoning,
            "replenishment_strategy": context.replenishment_strategy
        },
        "message": f"Mock forecast for {context.forecast_horizon_weeks}-week season",
        # Pass context to downstream agents
        "_context": {
            "replenishment_strategy": context.replenishment_strategy,
            "dc_holdback_percentage": context.dc_holdback_percentage,
            "markdown_checkpoint_week": context.markdown_checkpoint_week,
            "markdown_threshold": context.markdown_threshold
        }
    }


async def mock_inventory_agent(forecast_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock Inventory Agent that receives forecast from Demand Agent.

    Args:
        forecast_result: Result from Demand Agent

    Returns:
        Dictionary mimicking manufacturing order
    """
    await asyncio.sleep(0.3)

    total_forecast = forecast_result["total_forecast"]
    safety_stock = forecast_result["safety_stock_multiplier"]
    manufacturing_qty = int(total_forecast * safety_stock)

    # Extract context for parameter-aware decisions
    context = forecast_result.get("_context", {})
    replenishment_strategy = context.get("replenishment_strategy", "weekly")
    dc_holdback_pct = context.get("dc_holdback_percentage", 0.0)

    # Calculate DC holdback
    dc_holdback_units = int(manufacturing_qty * dc_holdback_pct)
    store_allocation_units = manufacturing_qty - dc_holdback_units

    # Adapt manufacturing orders based on replenishment strategy
    if replenishment_strategy == "none":
        # Single order at week 1
        orders = [{
            "order_id": "MO_001",
            "week": 1,
            "quantity": manufacturing_qty,
            "type": "Single Allocation"
        }]
        order_reasoning = "Single upfront order for no-replenishment strategy (Zara model)"
    elif replenishment_strategy == "weekly":
        # 3 orders across season
        orders = [
            {
                "order_id": "MO_001",
                "week": 1,
                "quantity": int(manufacturing_qty * 0.40),
                "type": "Initial"
            },
            {
                "order_id": "MO_002",
                "week": 5,
                "quantity": int(manufacturing_qty * 0.35),
                "type": "Replenishment 1"
            },
            {
                "order_id": "MO_003",
                "week": 9,
                "quantity": int(manufacturing_qty * 0.25),
                "type": "Replenishment 2"
            }
        ]
        order_reasoning = "3 orders split across season for weekly replenishment capability"
    else:  # bi-weekly
        # 2 orders across season
        orders = [
            {
                "order_id": "MO_001",
                "week": 1,
                "quantity": int(manufacturing_qty * 0.55),
                "type": "Initial"
            },
            {
                "order_id": "MO_002",
                "week": 7,
                "quantity": int(manufacturing_qty * 0.45),
                "type": "Replenishment"
            }
        ]
        order_reasoning = "2 orders for bi-weekly replenishment (luxury retail model)"

    logger.info(f"[MOCK] Inventory Agent: {len(orders)} manufacturing order(s) for '{replenishment_strategy}' strategy, {dc_holdback_pct*100}% DC holdback")

    return {
        "agent": "inventory",
        "manufacturing_qty": manufacturing_qty,
        "manufacturing_orders": orders,
        "dc_holdback": {
            "units": dc_holdback_units,
            "percentage": dc_holdback_pct,
            "store_allocation": store_allocation_units
        },
        "forecast_received": total_forecast,
        "safety_stock_applied": safety_stock,
        "reasoning": {
            "order_strategy": order_reasoning,
            "dc_holdback": f"{dc_holdback_pct*100}% held at DC for responsive allocation",
            "replenishment_strategy": replenishment_strategy
        },
        "message": f"Mock manufacturing: {len(orders)} order(s), {manufacturing_qty} total units",
        # Pass context to pricing agent
        "_context": context
    }


async def mock_pricing_agent(inventory_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock Pricing Agent that receives inventory from Inventory Agent.

    Args:
        inventory_result: Result from Inventory Agent

    Returns:
        Dictionary mimicking pricing recommendation
    """
    await asyncio.sleep(0.2)

    manufacturing_qty = inventory_result["manufacturing_qty"]

    # Extract context for parameter-aware decisions
    context = inventory_result.get("_context", {})
    markdown_checkpoint_week = context.get("markdown_checkpoint_week")
    markdown_threshold = context.get("markdown_threshold", 0.6)

    # Adapt markdown strategy based on checkpoint and threshold
    if markdown_checkpoint_week is None:
        # No markdown planned
        strategy = "Full price sellthrough"
        markdown_pct = 0.0
        checkpoint = None
        markdown_reasoning = "No markdown planned - targeting full-price sellthrough"
    else:
        # Markdown at specified week
        checkpoint = markdown_checkpoint_week

        # Adapt markdown % based on threshold
        if markdown_threshold < 0.5:
            markdown_pct = 0.40  # Aggressive
            markdown_reasoning = f"Aggressive 40% markdown at week {checkpoint} (threshold {markdown_threshold*100}% indicates high risk)"
        elif markdown_threshold < 0.7:
            markdown_pct = 0.30  # Standard
            markdown_reasoning = f"Standard 30% markdown at week {checkpoint} (threshold {markdown_threshold*100}% indicates moderate risk)"
        else:
            markdown_pct = 0.20  # Conservative
            markdown_reasoning = f"Conservative 20% markdown at week {checkpoint} (threshold {markdown_threshold*100}% indicates low risk)"

        strategy = f"{markdown_pct*100}% markdown at week {checkpoint} if below {markdown_threshold*100}% sellthrough"

    logger.info(f"[MOCK] Pricing Agent: {strategy}")

    return {
        "agent": "pricing",
        "manufacturing_qty_received": manufacturing_qty,
        "markdown_strategy": strategy,
        "markdown_percentage": markdown_pct,
        "checkpoint_week": checkpoint,
        "markdown_threshold": markdown_threshold,
        "reasoning": {
            "markdown_decision": markdown_reasoning,
            "checkpoint_week": checkpoint,
            "threshold_based": markdown_threshold if checkpoint else None
        },
        "message": f"Mock pricing: {strategy}"
    }
