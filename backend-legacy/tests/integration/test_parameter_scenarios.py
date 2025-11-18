"""
Integration tests for parameter-driven agent workflows.

Tests validate end-to-end workflows with different parameter combinations,
ensuring agents adapt correctly to different business scenarios.
"""

import pytest
from datetime import date
from app.orchestrator.agent_handoff import AgentHandoffManager
from app.orchestrator.mock_agents import (
    mock_demand_agent,
    mock_inventory_agent,
    mock_pricing_agent
)
from app.schemas.workflow_schemas import SeasonParameters


@pytest.fixture
def manager():
    """Create AgentHandoffManager for integration tests."""
    mgr = AgentHandoffManager()
    mgr.register_agent("demand", mock_demand_agent)
    mgr.register_agent("inventory", mock_inventory_agent)
    mgr.register_agent("pricing", mock_pricing_agent)
    return mgr


# ============================================================================
# Scenario 1: Zara-Style Fast Fashion
# ============================================================================

@pytest.mark.asyncio
async def test_scenario_1_zara_workflow(manager):
    """
    Scenario 1: Zara-style fast fashion workflow.

    Parameters:
    - 12 weeks forecast horizon
    - No replenishment (single allocation)
    - 0% DC holdback (all to stores upfront)
    - Markdown at week 6

    Expected Behavior:
    - Demand: 25% safety stock
    - Inventory: 1 manufacturing order at week 1, 0 DC units
    - Pricing: Markdown at week 6
    """
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="none",
        dc_holdback_percentage=0.0,
        markdown_checkpoint_week=6,
        markdown_threshold=0.6
    )

    # Execute agent chain
    final_result = await manager.handoff_chain(
        agents=["demand", "inventory", "pricing"],
        initial_context=params
    )

    # Verify Demand Agent output
    # Note: We need to get the demand result from the chain
    # Let's execute each agent individually to verify
    manager.clear_log()
    demand_result = await manager.call_agent("demand", params)

    assert demand_result["safety_stock_multiplier"] == 1.25  # 25% for no replenishment
    assert len(demand_result["weekly_curve"]) == 12

    # Verify Inventory Agent output
    inventory_result = await manager.call_agent("inventory", demand_result)

    assert len(inventory_result["manufacturing_orders"]) == 1  # Single order
    assert inventory_result["manufacturing_orders"][0]["week"] == 1
    assert inventory_result["dc_holdback"]["percentage"] == 0.0
    assert inventory_result["dc_holdback"]["units"] == 0

    # Verify Pricing Agent output
    pricing_result = await manager.call_agent("pricing", inventory_result)

    assert pricing_result["checkpoint_week"] == 6
    assert pricing_result["markdown_percentage"] == 0.30  # Standard (threshold 0.6)


# ============================================================================
# Scenario 2: Traditional Retail
# ============================================================================

@pytest.mark.asyncio
async def test_scenario_2_traditional_retail_workflow(manager):
    """
    Scenario 2: Traditional retail workflow.

    Parameters:
    - 12 weeks forecast horizon
    - Weekly replenishment capability
    - 45% DC holdback (responsive allocation)
    - Markdown at week 8

    Expected Behavior:
    - Demand: 20% safety stock
    - Inventory: 3 manufacturing orders, 45% held at DC
    - Pricing: Markdown at week 8
    """
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.45,
        markdown_checkpoint_week=8,
        markdown_threshold=0.6
    )

    # Execute agents individually
    manager.clear_log()
    demand_result = await manager.call_agent("demand", params)

    assert demand_result["safety_stock_multiplier"] == 1.20  # 20% for weekly
    assert len(demand_result["weekly_curve"]) == 12

    # Verify Inventory Agent output
    inventory_result = await manager.call_agent("inventory", demand_result)

    assert len(inventory_result["manufacturing_orders"]) == 3  # 3 orders
    assert inventory_result["manufacturing_orders"][0]["week"] == 1
    assert inventory_result["manufacturing_orders"][1]["week"] == 5
    assert inventory_result["manufacturing_orders"][2]["week"] == 9
    assert inventory_result["dc_holdback"]["percentage"] == 0.45

    # Calculate expected DC holdback
    manufacturing_qty = int(demand_result["total_forecast"] * 1.20)
    expected_dc_units = int(manufacturing_qty * 0.45)
    assert inventory_result["dc_holdback"]["units"] == expected_dc_units

    # Verify Pricing Agent output
    pricing_result = await manager.call_agent("pricing", inventory_result)

    assert pricing_result["checkpoint_week"] == 8
    assert pricing_result["markdown_percentage"] == 0.30  # Standard (threshold 0.6)


# ============================================================================
# Scenario 3: Luxury Retail
# ============================================================================

@pytest.mark.asyncio
async def test_scenario_3_luxury_retail_workflow(manager):
    """
    Scenario 3: Luxury retail workflow.

    Parameters:
    - 16 weeks forecast horizon (extended season)
    - Bi-weekly replenishment
    - 30% DC holdback
    - No markdown (full-price sellthrough)

    Expected Behavior:
    - Demand: 22% safety stock, 16-week curve
    - Inventory: 2 manufacturing orders, 30% held at DC
    - Pricing: No markdown strategy
    """
    params = SeasonParameters(
        forecast_horizon_weeks=16,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 6, 20),
        replenishment_strategy="bi-weekly",
        dc_holdback_percentage=0.30,
        markdown_checkpoint_week=None,  # No markdown
        markdown_threshold=0.6
    )

    # Execute agents individually
    manager.clear_log()
    demand_result = await manager.call_agent("demand", params)

    assert demand_result["safety_stock_multiplier"] == 1.22  # 22% for bi-weekly
    assert len(demand_result["weekly_curve"]) == 16  # Extended horizon

    # Verify Inventory Agent output
    inventory_result = await manager.call_agent("inventory", demand_result)

    assert len(inventory_result["manufacturing_orders"]) == 2  # 2 orders
    assert inventory_result["manufacturing_orders"][0]["week"] == 1
    assert inventory_result["manufacturing_orders"][1]["week"] == 7
    assert inventory_result["dc_holdback"]["percentage"] == 0.30

    # Calculate expected DC holdback
    manufacturing_qty = int(demand_result["total_forecast"] * 1.22)
    expected_dc_units = int(manufacturing_qty * 0.30)
    assert inventory_result["dc_holdback"]["units"] == expected_dc_units

    # Verify Pricing Agent output
    pricing_result = await manager.call_agent("pricing", inventory_result)

    assert pricing_result["checkpoint_week"] is None  # No markdown
    assert pricing_result["markdown_percentage"] == 0.0
    assert "Full price sellthrough" in pricing_result["markdown_strategy"]


# ============================================================================
# Additional Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_agent_chain_execution(manager):
    """Test that handoff_chain correctly passes results between agents."""
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.45,
        markdown_checkpoint_week=8,
        markdown_threshold=0.6
    )

    # Execute full chain
    final_result = await manager.handoff_chain(
        agents=["demand", "inventory", "pricing"],
        initial_context=params
    )

    # Final result should be from pricing agent
    assert final_result["agent"] == "pricing"
    assert "markdown_strategy" in final_result
    assert "reasoning" in final_result

    # Verify execution log
    log = manager.get_execution_log()
    assert len(log) == 3
    assert log[0]["agent_name"] == "demand"
    assert log[1]["agent_name"] == "inventory"
    assert log[2]["agent_name"] == "pricing"
    assert all(entry["status"] == "success" for entry in log)
