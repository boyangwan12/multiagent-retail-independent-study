"""Tests for WebSocket endpoint and messaging."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def test_websocket_connection():
    """Test WebSocket connection establishment."""

    workflow_id = "wf_test123"

    with client.websocket_connect(f"/api/v1/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connection_established"
        assert data["workflow_id"] == workflow_id
        assert "timestamp" in data


def test_websocket_disconnect():
    """Test WebSocket graceful disconnection."""

    workflow_id = "wf_test456"

    with client.websocket_connect(f"/api/v1/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Close connection
        websocket.close()

    # Connection should be removed from manager
    # (Manager state is internal, so we just verify no errors)


@pytest.mark.asyncio
async def test_broadcast_agent_progress():
    """Test broadcasting agent progress message."""

    from app.websocket.broadcaster import broadcast_agent_progress

    workflow_id = "wf_test789"

    # Connect WebSocket in background
    with client.websocket_connect(f"/api/v1/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        websocket.receive_json()

        # Broadcast progress message
        await broadcast_agent_progress(
            workflow_id=workflow_id,
            agent_name="Demand Agent",
            progress_message="Running Prophet forecasting model...",
            progress_pct=33
        )

        # Receive broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "agent_progress"
        assert data["agent"] == "Demand Agent"
        assert data["message"] == "Running Prophet forecasting model..."
        assert data["progress_pct"] == 33
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_broadcast_workflow_complete():
    """Test broadcasting workflow complete message."""

    from app.websocket.broadcaster import broadcast_workflow_complete

    workflow_id = "wf_test_complete"

    with client.websocket_connect(f"/api/v1/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        websocket.receive_json()

        # Broadcast workflow complete message
        await broadcast_workflow_complete(
            workflow_id=workflow_id,
            duration_seconds=58.7,
            result={
                "forecast_id": "f_spring_2025",
                "total_season_demand": 8000
            }
        )

        # Receive broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "workflow_complete"
        assert data["workflow_id"] == workflow_id
        assert data["duration_seconds"] == 58.7
        assert data["result"]["forecast_id"] == "f_spring_2025"


@pytest.mark.asyncio
async def test_broadcast_error():
    """Test broadcasting error message."""

    from app.websocket.broadcaster import broadcast_error

    workflow_id = "wf_test_error"

    with client.websocket_connect(f"/api/v1/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        websocket.receive_json()

        # Broadcast error message
        await broadcast_error(
            workflow_id=workflow_id,
            error_message="Prophet model failed to converge",
            agent_name="Demand Agent"
        )

        # Receive broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert data["agent"] == "Demand Agent"
        assert "Prophet model failed to converge" in data["error_message"]
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_broadcast_agent_started():
    """Test broadcasting agent started message."""

    from app.websocket.broadcaster import broadcast_agent_started

    workflow_id = "wf_test_started"

    with client.websocket_connect(f"/api/v1/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        websocket.receive_json()

        # Broadcast agent started message
        await broadcast_agent_started(
            workflow_id=workflow_id,
            agent_name="Demand Agent"
        )

        # Receive broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "agent_started"
        assert data["agent"] == "Demand Agent"
        assert "timestamp" in data
