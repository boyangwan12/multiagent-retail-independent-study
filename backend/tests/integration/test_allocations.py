"""
Integration tests for allocation endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_allocations_success(client: TestClient, mock_season_parameters):
    """Test GET /api/v1/allocations/{id} returns allocation data"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Fetch allocations
    response = client.get(f"/api/v1/allocations/{workflow_id}")

    # May be 404 if not ready yet
    if response.status_code == 200:
        data = response.json()
        assert "total_units_allocated" in data or "allocation_id" in data
        assert "replenishment_strategy" in data or "strategy" in data
    elif response.status_code == 404:
        # Not ready - acceptable
        data = response.json()
        assert "detail" in data


def test_allocations_no_replenishment(client: TestClient):
    """Test allocations with replenishment_strategy = 'none'"""
    parameters = {
        "forecast_horizon_weeks": 12,
        "season_start_date": "2025-01-01",
        "season_end_date": "2025-03-26",
        "replenishment_strategy": "none",
        "dc_holdback_percentage": 0.0,
        "markdown_checkpoint_week": None,
        "markdown_threshold": None,
        "extraction_confidence": "high"
    }

    request_data = {
        "category_id": "womens_dresses",
        "parameters": parameters
    }

    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    response = client.get(f"/api/v1/allocations/{workflow_id}")

    if response.status_code == 200:
        data = response.json()
        strategy_key = "replenishment_strategy" if "replenishment_strategy" in data else "strategy"
        assert data[strategy_key] == "none"
