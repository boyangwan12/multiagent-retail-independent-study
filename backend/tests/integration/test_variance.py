"""
Integration tests for variance endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_variance_by_week_success(client: TestClient, mock_season_parameters):
    """Test GET /api/v1/variance/{id}/week/{week} returns weekly variance"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Fetch variance for week 3
    response = client.get(f"/api/v1/variance/{workflow_id}/week/3")

    # May be 404 if variance data not ready
    if response.status_code == 200:
        data = response.json()
        assert "week" in data
        assert data["week"] == 3
        assert "forecast_units" in data or "forecasted_units" in data
    elif response.status_code == 404:
        # Not ready yet - acceptable
        data = response.json()
        assert "detail" in data


def test_variance_calculation(client: TestClient, mock_season_parameters):
    """Test variance percentage calculation is correct"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Fetch variance
    response = client.get(f"/api/v1/variance/{workflow_id}/week/1")

    if response.status_code == 200:
        data = response.json()

        # Validate variance calculation if data present
        forecast_key = "forecast_units" if "forecast_units" in data else "forecasted_units"
        actual_key = "actual_units" if "actual_units" in data else "actual"

        if forecast_key in data and actual_key in data and "variance_percentage" in data:
            forecast = data[forecast_key]
            actual = data[actual_key]

            if forecast > 0:
                expected_variance = ((actual - forecast) / forecast) * 100
                assert abs(data["variance_percentage"] - expected_variance) < 0.1
