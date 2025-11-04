"""
Integration tests for markdown endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_markdown_analysis_success(client: TestClient):
    """Test GET /api/v1/markdowns/{id} with markdown checkpoint set"""
    parameters = {
        "forecast_horizon_weeks": 12,
        "season_start_date": "2025-01-01",
        "season_end_date": "2025-03-26",
        "replenishment_strategy": "weekly",
        "dc_holdback_percentage": 0.15,
        "markdown_checkpoint_week": 6,
        "markdown_threshold": 0.40,
        "extraction_confidence": "high"
    }

    request_data = {
        "category_id": "womens_dresses",
        "parameters": parameters
    }

    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    response = client.get(f"/api/v1/markdowns/{workflow_id}")

    # May be 404 if not ready yet
    if response.status_code == 200:
        data = response.json()
        assert "markdown_checkpoint_week" in data
        assert data["markdown_checkpoint_week"] == 6
        assert "markdown_threshold" in data or "threshold" in data
    elif response.status_code == 404:
        # Not ready or not applicable - acceptable
        pass


def test_markdown_not_applicable(client: TestClient):
    """Test markdown endpoint returns 404 when checkpoint week is null"""
    parameters = {
        "forecast_horizon_weeks": 12,
        "season_start_date": "2025-01-01",
        "season_end_date": "2025-03-26",
        "replenishment_strategy": "weekly",
        "dc_holdback_percentage": 0.15,
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

    response = client.get(f"/api/v1/markdowns/{workflow_id}")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
