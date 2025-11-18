"""
Unit tests for enhanced parameter-aware mock agents.

Tests verify that mock agents adapt their behavior based on input parameters,
demonstrating the parameter-driven architecture before Phase 6 real agents.
"""

import pytest
from datetime import date
from app.orchestrator.mock_agents import (
    mock_demand_agent,
    mock_inventory_agent,
    mock_pricing_agent
)
from app.schemas.workflow_schemas import SeasonParameters


# ============================================================================
# Demand Agent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_demand_agent_safety_stock_none_replenishment():
    """Test Demand Agent uses 25% safety stock for no replenishment."""
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="none",
        dc_holdback_percentage=0.0
    )

    result = await mock_demand_agent(params)

    assert result["safety_stock_multiplier"] == 1.25  # 25% for no replenishment
    assert "reasoning" in result
    assert "25%" in result["reasoning"]["safety_stock"]


@pytest.mark.asyncio
async def test_demand_agent_safety_stock_weekly_replenishment():
    """Test Demand Agent uses 20% safety stock for weekly replenishment."""
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.45
    )

    result = await mock_demand_agent(params)

    assert result["safety_stock_multiplier"] == 1.20  # 20% for weekly
    assert "reasoning" in result
    assert "20%" in result["reasoning"]["safety_stock"]


@pytest.mark.asyncio
async def test_demand_agent_safety_stock_biweekly_replenishment():
    """Test Demand Agent uses 22% safety stock for bi-weekly replenishment."""
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="bi-weekly",
        dc_holdback_percentage=0.30
    )

    result = await mock_demand_agent(params)

    assert result["safety_stock_multiplier"] == 1.22  # 22% for bi-weekly
    assert "reasoning" in result
    assert "22%" in result["reasoning"]["safety_stock"]


@pytest.mark.asyncio
async def test_demand_agent_forecast_horizon_8_weeks():
    """Test Demand Agent truncates curve for 8-week horizon."""
    params = SeasonParameters(
        forecast_horizon_weeks=8,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 4, 26),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.0
    )

    result = await mock_demand_agent(params)

    assert len(result["weekly_curve"]) == 8
    assert result["total_forecast"] == sum(result["weekly_curve"])
    assert "Truncated" in result["reasoning"]["forecast_horizon"]


@pytest.mark.asyncio
async def test_demand_agent_forecast_horizon_12_weeks():
    """Test Demand Agent uses standard curve for 12-week horizon."""
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.0
    )

    result = await mock_demand_agent(params)

    assert len(result["weekly_curve"]) == 12
    assert result["total_forecast"] == sum(result["weekly_curve"])
    assert "standard" in result["reasoning"]["forecast_horizon"].lower()


@pytest.mark.asyncio
async def test_demand_agent_forecast_horizon_16_weeks():
    """Test Demand Agent extends curve for 16-week horizon."""
    params = SeasonParameters(
        forecast_horizon_weeks=16,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 6, 20),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.0
    )

    result = await mock_demand_agent(params)

    assert len(result["weekly_curve"]) == 16
    assert result["total_forecast"] == sum(result["weekly_curve"])
    assert "Extended" in result["reasoning"]["forecast_horizon"]


# ============================================================================
# Inventory Agent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_inventory_agent_dc_holdback_calculation():
    """Test Inventory Agent calculates DC holdback correctly."""
    # Create forecast result with 45% holdback
    forecast_result = {
        "agent": "demand",
        "total_forecast": 8000,
        "safety_stock_multiplier": 1.20,
        "_context": {
            "replenishment_strategy": "weekly",
            "dc_holdback_percentage": 0.45,
            "markdown_checkpoint_week": 8,
            "markdown_threshold": 0.6
        }
    }

    result = await mock_inventory_agent(forecast_result)

    manufacturing_qty = int(8000 * 1.20)  # 9600
    expected_holdback = int(manufacturing_qty * 0.45)  # 4320

    assert result["dc_holdback"]["percentage"] == 0.45
    assert result["dc_holdback"]["units"] == expected_holdback
    assert result["dc_holdback"]["store_allocation"] == manufacturing_qty - expected_holdback


@pytest.mark.asyncio
async def test_inventory_agent_no_replenishment_single_order():
    """Test Inventory Agent creates single order for no replenishment."""
    forecast_result = {
        "agent": "demand",
        "total_forecast": 8000,
        "safety_stock_multiplier": 1.25,
        "_context": {
            "replenishment_strategy": "none",
            "dc_holdback_percentage": 0.0,
            "markdown_checkpoint_week": 6,
            "markdown_threshold": 0.6
        }
    }

    result = await mock_inventory_agent(forecast_result)

    assert len(result["manufacturing_orders"]) == 1
    assert result["manufacturing_orders"][0]["week"] == 1
    assert result["manufacturing_orders"][0]["type"] == "Single Allocation"
    assert "Single upfront order" in result["reasoning"]["order_strategy"]


@pytest.mark.asyncio
async def test_inventory_agent_weekly_replenishment_three_orders():
    """Test Inventory Agent creates 3 orders for weekly replenishment."""
    forecast_result = {
        "agent": "demand",
        "total_forecast": 8000,
        "safety_stock_multiplier": 1.20,
        "_context": {
            "replenishment_strategy": "weekly",
            "dc_holdback_percentage": 0.45,
            "markdown_checkpoint_week": 8,
            "markdown_threshold": 0.6
        }
    }

    result = await mock_inventory_agent(forecast_result)

    assert len(result["manufacturing_orders"]) == 3
    assert result["manufacturing_orders"][0]["week"] == 1
    assert result["manufacturing_orders"][1]["week"] == 5
    assert result["manufacturing_orders"][2]["week"] == 9
    assert "3 orders" in result["reasoning"]["order_strategy"]


@pytest.mark.asyncio
async def test_inventory_agent_biweekly_replenishment_two_orders():
    """Test Inventory Agent creates 2 orders for bi-weekly replenishment."""
    forecast_result = {
        "agent": "demand",
        "total_forecast": 8000,
        "safety_stock_multiplier": 1.22,
        "_context": {
            "replenishment_strategy": "bi-weekly",
            "dc_holdback_percentage": 0.30,
            "markdown_checkpoint_week": None,
            "markdown_threshold": 0.6
        }
    }

    result = await mock_inventory_agent(forecast_result)

    assert len(result["manufacturing_orders"]) == 2
    assert result["manufacturing_orders"][0]["week"] == 1
    assert result["manufacturing_orders"][1]["week"] == 7
    assert "2 orders" in result["reasoning"]["order_strategy"]


# ============================================================================
# Pricing Agent Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pricing_agent_no_markdown_checkpoint():
    """Test Pricing Agent handles null markdown checkpoint (full price)."""
    inventory_result = {
        "agent": "inventory",
        "manufacturing_qty": 10000,
        "_context": {
            "markdown_checkpoint_week": None,
            "markdown_threshold": 0.6
        }
    }

    result = await mock_pricing_agent(inventory_result)

    assert result["checkpoint_week"] is None
    assert result["markdown_percentage"] == 0.0
    assert "Full price sellthrough" in result["markdown_strategy"]
    assert "No markdown planned" in result["reasoning"]["markdown_decision"]


@pytest.mark.asyncio
async def test_pricing_agent_low_threshold_aggressive_markdown():
    """Test Pricing Agent uses 40% markdown for low threshold (<0.5)."""
    inventory_result = {
        "agent": "inventory",
        "manufacturing_qty": 10000,
        "_context": {
            "markdown_checkpoint_week": 6,
            "markdown_threshold": 0.4
        }
    }

    result = await mock_pricing_agent(inventory_result)

    assert result["checkpoint_week"] == 6
    assert result["markdown_percentage"] == 0.40  # Aggressive
    assert "40.0%" in result["markdown_strategy"]
    assert "Aggressive" in result["reasoning"]["markdown_decision"]


@pytest.mark.asyncio
async def test_pricing_agent_medium_threshold_standard_markdown():
    """Test Pricing Agent uses 30% markdown for medium threshold (0.5-0.7)."""
    inventory_result = {
        "agent": "inventory",
        "manufacturing_qty": 10000,
        "_context": {
            "markdown_checkpoint_week": 8,
            "markdown_threshold": 0.6
        }
    }

    result = await mock_pricing_agent(inventory_result)

    assert result["checkpoint_week"] == 8
    assert result["markdown_percentage"] == 0.30  # Standard
    assert "30.0%" in result["markdown_strategy"]
    assert "Standard" in result["reasoning"]["markdown_decision"]


@pytest.mark.asyncio
async def test_pricing_agent_high_threshold_conservative_markdown():
    """Test Pricing Agent uses 20% markdown for high threshold (>0.7)."""
    inventory_result = {
        "agent": "inventory",
        "manufacturing_qty": 10000,
        "_context": {
            "markdown_checkpoint_week": 10,
            "markdown_threshold": 0.8
        }
    }

    result = await mock_pricing_agent(inventory_result)

    assert result["checkpoint_week"] == 10
    assert result["markdown_percentage"] == 0.20  # Conservative
    assert "20.0%" in result["markdown_strategy"]
    assert "Conservative" in result["reasoning"]["markdown_decision"]
