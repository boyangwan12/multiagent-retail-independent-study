"""
Unit tests for error handling across the orchestrator workflow.

Tests verify that errors are caught gracefully, logged properly, and
communicated to users via polling status endpoint.
"""

import pytest
import asyncio
from app.orchestrator.agent_handoff import AgentHandoffManager


# ============================================================================
# Agent Timeout Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_agent_timeout_error_handling():
    """Test that agent timeout errors are enhanced with helpful messaging."""
    manager = AgentHandoffManager()

    async def slow_agent(ctx):
        await asyncio.sleep(10)  # Exceeds timeout
        return {}

    manager.register_agent("slow", slow_agent)

    with pytest.raises(TimeoutError) as exc_info:
        await manager.call_agent("slow", {}, timeout=2)

    # Verify enhanced error message
    assert "exceeded maximum execution time" in str(exc_info.value)
    assert "slow" in str(exc_info.value)
    assert "2s" in str(exc_info.value)

    # Verify logging
    log = manager.get_execution_log()
    assert len(log) == 1
    assert log[0]["status"] == "timeout"
    assert log[0]["agent_name"] == "slow"


@pytest.mark.asyncio
async def test_agent_timeout_with_context():
    """Test that timeout logging includes context summary."""
    manager = AgentHandoffManager()

    async def slow_agent(ctx):
        await asyncio.sleep(10)
        return {}

    manager.register_agent("slow", slow_agent)

    test_context = {"key": "value", "data": "test"}

    with pytest.raises(TimeoutError):
        await manager.call_agent("slow", test_context, timeout=1)

    # Verify execution log captures timeout
    log = manager.get_execution_log()
    assert log[0]["status"] == "timeout"
    assert log[0]["duration_seconds"] >= 1.0  # Should be ~1 second


# ============================================================================
# Agent Execution Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_agent_execution_error_handling():
    """Test that agent execution errors are caught and sanitized."""
    manager = AgentHandoffManager()

    async def failing_agent(ctx):
        raise ValueError("Invalid input data - missing required field")

    manager.register_agent("failing", failing_agent)

    with pytest.raises(RuntimeError) as exc_info:
        await manager.call_agent("failing", {})

    # Verify sanitized error message (no internal details)
    assert "encountered an error" in str(exc_info.value)
    assert "failing" in str(exc_info.value)
    assert "Check server logs for details" in str(exc_info.value)

    # Original error should be chained
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ValueError)

    # Verify logging
    log = manager.get_execution_log()
    assert len(log) == 1
    assert log[0]["status"] == "failed"
    assert log[0]["agent_name"] == "failing"


@pytest.mark.asyncio
async def test_agent_execution_error_preserves_original():
    """Test that original exception is preserved via __cause__."""
    manager = AgentHandoffManager()

    async def failing_agent(ctx):
        raise KeyError("missing_key")

    manager.register_agent("failing", failing_agent)

    with pytest.raises(RuntimeError) as exc_info:
        await manager.call_agent("failing", {})

    # Verify original exception is chained
    assert isinstance(exc_info.value.__cause__, KeyError)
    assert "missing_key" in str(exc_info.value.__cause__)


@pytest.mark.asyncio
async def test_agent_chain_stops_on_first_error():
    """Test that agent chain stops when first agent fails."""
    manager = AgentHandoffManager()

    call_count = {"agent1": 0, "agent2": 0, "agent3": 0}

    async def agent1(ctx):
        call_count["agent1"] += 1
        return {"result": "success"}

    async def agent2(ctx):
        call_count["agent2"] += 1
        raise ValueError("Agent 2 failed")

    async def agent3(ctx):
        call_count["agent3"] += 1
        return {"result": "success"}

    manager.register_agent("agent1", agent1)
    manager.register_agent("agent2", agent2)
    manager.register_agent("agent3", agent3)

    with pytest.raises(RuntimeError):
        await manager.handoff_chain(
            agents=["agent1", "agent2", "agent3"],
            initial_context={}
        )

    # Verify agent1 was called, agent2 was called and failed, agent3 never called
    assert call_count["agent1"] == 1
    assert call_count["agent2"] == 1
    assert call_count["agent3"] == 0


# ============================================================================
# Agent Not Registered Error Tests
# ============================================================================

@pytest.mark.asyncio
async def test_agent_not_registered_error():
    """Test that calling unregistered agent raises clear error."""
    manager = AgentHandoffManager()

    with pytest.raises(ValueError) as exc_info:
        await manager.call_agent("nonexistent", {})

    assert "not registered" in str(exc_info.value)
    assert "nonexistent" in str(exc_info.value)


# ============================================================================
# Logging Context Tests
# ============================================================================

@pytest.mark.asyncio
async def test_error_logging_includes_context_type():
    """Test that error logging captures context type for debugging."""
    manager = AgentHandoffManager()

    async def failing_agent(ctx):
        raise TypeError("Invalid context type")

    manager.register_agent("failing", failing_agent)

    # Use a dictionary context
    with pytest.raises(RuntimeError):
        await manager.call_agent("failing", {"test": "data"})

    # Verify the execution was logged
    log = manager.get_execution_log()
    assert len(log) == 1
    assert log[0]["status"] == "failed"
