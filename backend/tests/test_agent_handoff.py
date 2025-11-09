"""
Tests for Agent Handoff Manager.

This module tests the core orchestration logic for multi-agent workflows.
"""

import pytest
import asyncio
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
    """Create a fresh AgentHandoffManager for each test."""
    return AgentHandoffManager()


@pytest.fixture
def mock_parameters():
    """Create mock season parameters for testing."""
    return SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="none",
        dc_holdback_percentage=0.0
    )


def test_agent_registration(manager):
    """Test agent registration."""
    async def test_handler(ctx):
        return {"result": "test"}

    manager.register_agent("test", test_handler)

    assert "test" in manager._agents
    assert manager._agents["test"] == test_handler


def test_agent_registration_not_callable(manager):
    """Test that non-callable handlers raise TypeError."""
    with pytest.raises(TypeError, match="must be callable"):
        manager.register_agent("test", "not_callable")


@pytest.mark.asyncio
async def test_single_agent_call(manager, mock_parameters):
    """Test single agent execution (success case)."""
    manager.register_agent("demand", mock_demand_agent)

    result = await manager.call_agent("demand", mock_parameters)

    assert result["total_forecast"] == 8000
    assert result["safety_stock_multiplier"] == 1.25  # 25% for no replenishment
    assert result["agent"] == "demand"


@pytest.mark.asyncio
async def test_agent_chain_two_agents(manager, mock_parameters):
    """Test agent chain with 2 agents (Demand → Inventory)."""
    manager.register_agent("demand", mock_demand_agent)
    manager.register_agent("inventory", mock_inventory_agent)

    result = await manager.handoff_chain(
        agents=["demand", "inventory"],
        initial_context=mock_parameters
    )

    assert result["agent"] == "inventory"
    assert result["manufacturing_qty"] == 10000  # 8000 * 1.25


@pytest.mark.asyncio
async def test_agent_chain_three_agents(manager, mock_parameters):
    """Test agent chain with 3 agents (Demand → Inventory → Pricing)."""
    manager.register_agent("demand", mock_demand_agent)
    manager.register_agent("inventory", mock_inventory_agent)
    manager.register_agent("pricing", mock_pricing_agent)

    result = await manager.handoff_chain(
        agents=["demand", "inventory", "pricing"],
        initial_context=mock_parameters
    )

    assert result["agent"] == "pricing"
    assert result["manufacturing_qty_received"] == 10000
    assert result["markdown_percentage"] == 0.30


@pytest.mark.asyncio
async def test_agent_timeout(manager):
    """Test timeout handling."""
    async def slow_agent(ctx):
        await asyncio.sleep(5)  # Exceeds timeout
        return {}

    manager.register_agent("slow", slow_agent)

    with pytest.raises(asyncio.TimeoutError):
        await manager.call_agent("slow", {}, timeout=2)

    # Verify timeout logged
    log = manager.get_execution_log()
    assert len(log) == 1
    assert log[0]["status"] == "timeout"


@pytest.mark.asyncio
async def test_agent_not_registered(manager):
    """Test error when agent not registered."""
    with pytest.raises(ValueError, match="Agent 'unknown' not registered"):
        await manager.call_agent("unknown", {})


@pytest.mark.asyncio
async def test_agent_failure(manager):
    """Test agent failure propagation."""
    async def failing_agent(ctx):
        raise RuntimeError("Agent internal error")

    manager.register_agent("failing", failing_agent)

    with pytest.raises(RuntimeError, match="Agent internal error"):
        await manager.call_agent("failing", {})

    # Verify failure logged
    log = manager.get_execution_log()
    assert len(log) == 1
    assert log[0]["status"] == "failed"


@pytest.mark.asyncio
async def test_execution_log(manager, mock_parameters):
    """Test execution log tracking."""
    manager.register_agent("demand", mock_demand_agent)

    await manager.call_agent("demand", mock_parameters)

    log = manager.get_execution_log()
    assert len(log) == 1
    assert log[0]["agent_name"] == "demand"
    assert log[0]["status"] == "success"
    assert log[0]["duration_seconds"] > 0


def test_clear_log(manager):
    """Test log clearing."""
    manager._execution_log.append({"test": "entry"})
    assert len(manager._execution_log) == 1

    manager.clear_log()
    assert len(manager._execution_log) == 0


@pytest.mark.asyncio
async def test_result_passing_between_agents(manager, mock_parameters):
    """Test that result from Agent N becomes context for Agent N+1."""
    manager.register_agent("demand", mock_demand_agent)
    manager.register_agent("inventory", mock_inventory_agent)

    # Execute chain
    result = await manager.handoff_chain(
        agents=["demand", "inventory"],
        initial_context=mock_parameters
    )

    # Verify Inventory Agent received Demand Agent's forecast
    assert result["forecast_received"] == 8000  # From demand agent
    assert result["safety_stock_applied"] == 1.25  # From demand agent
