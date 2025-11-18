"""
Integration tests for workflow endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_create_forecast_workflow_success(client: TestClient, mock_season_parameters):
    """Test POST /api/v1/workflows/forecast creates workflow"""
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }

    response = client.post("/api/v1/workflows/forecast", json=request_data)

    assert response.status_code == 201

    data = response.json()
    assert "workflow_id" in data
    assert "status" in data
    assert "websocket_url" in data
    assert data["status"] == "pending"
    assert data["workflow_id"].startswith("wf_")


def test_get_workflow_status(client: TestClient, mock_season_parameters):
    """Test GET /api/v1/workflows/{id} returns workflow status"""
    # First create a workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Get workflow status
    response = client.get(f"/api/v1/workflows/{workflow_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert "status" in data
    assert "workflow_type" in data
    assert data["workflow_type"] == "forecast"


def test_get_workflow_results(client: TestClient, mock_season_parameters):
    """Test GET /api/v1/workflows/{id}/results returns final results"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Get results (may be pending if workflow not complete)
    response = client.get(f"/api/v1/workflows/{workflow_id}/results")

    # Should return 200 (pending) or final results
    assert response.status_code in [200, 404]  # 404 if results not ready yet

    if response.status_code == 200:
        data = response.json()
        assert "workflow_id" in data
        assert "status" in data


def test_get_workflow_invalid_id(client: TestClient):
    """Test GET /api/v1/workflows/{id} with invalid workflow ID"""
    response = client.get("/api/v1/workflows/invalid_id_xyz")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
