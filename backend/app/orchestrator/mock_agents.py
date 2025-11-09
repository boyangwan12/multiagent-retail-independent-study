"""
Mock agents for testing handoff framework.

These mock agents simulate the behavior of real demand, inventory, and pricing agents
without requiring actual ML models or complex business logic.
"""

import asyncio
from typing import Dict, Any
from app.schemas.workflow_schemas import SeasonParameters


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
    elif context.replenishment_strategy == "weekly":
        safety_stock = 1.20  # 20% for weekly
    else:  # bi-weekly
        safety_stock = 1.22  # 22% for bi-weekly

    return {
        "agent": "demand",
        "total_forecast": 8000,
        "safety_stock_multiplier": safety_stock,
        "weekly_curve": [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480],
        "clusters": ["Fashion_Forward", "Mainstream", "Value_Conscious"],
        "message": f"Mock forecast for {context.forecast_horizon_weeks}-week season"
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

    return {
        "agent": "inventory",
        "manufacturing_qty": manufacturing_qty,
        "forecast_received": total_forecast,
        "safety_stock_applied": safety_stock,
        "message": f"Mock manufacturing order: {manufacturing_qty} units"
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
    markdown_recommendation = 0.30  # 30% markdown if needed

    return {
        "agent": "pricing",
        "manufacturing_qty_received": manufacturing_qty,
        "markdown_percentage": markdown_recommendation,
        "checkpoint_week": 6,
        "message": f"Mock pricing: Apply {markdown_recommendation*100}% markdown at week 6 if needed"
    }
