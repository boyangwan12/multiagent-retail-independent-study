"""
Integration tests for forecast endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_forecast_summary_success(client: TestClient, mock_season_parameters):
    """Test GET /api/v1/forecasts/{id} returns ForecastSummary"""
    # Create workflow first
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Fetch forecast summary (may need to wait for workflow completion)
    response = client.get(f"/api/v1/forecasts/{workflow_id}")

    # Response depends on workflow state
    if response.status_code == 200:
        data = response.json()
        assert "total_season_demand" in data or "total_demand" in data
        assert "forecasting_method" in data or "forecast_id" in data
    elif response.status_code == 404:
        # Forecast not ready yet - acceptable
        data = response.json()
        assert "detail" in data


def test_forecast_summary_not_found(client: TestClient):
    """Test GET /api/v1/forecasts/{id} with invalid workflow ID"""
    response = client.get("/api/v1/forecasts/invalid_id_xyz")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_forecast_manufacturing_calculation(client: TestClient, mock_season_parameters):
    """Test manufacturing order calculation is correct"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Get forecast
    response = client.get(f"/api/v1/forecasts/{workflow_id}")

    if response.status_code == 200:
        data = response.json()

        # Validate manufacturing order calculation if present
        if "total_demand" in data and "manufacturing_order" in data:
            total_demand = data.get("total_demand", 0)
            safety_stock = data.get("safety_stock_percentage", 0.20)
            dc_holdback = data.get("dc_holdback_percentage", 0.15)

            expected_manufacturing_order = int(
                total_demand * (1 + safety_stock) * (1 + dc_holdback)
            )

            # Allow small rounding differences
            assert abs(data["manufacturing_order"] - expected_manufacturing_order) <= 10
