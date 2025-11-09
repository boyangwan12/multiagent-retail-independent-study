"""
Integration tests for parameter extraction endpoint
"""

import pytest
from fastapi.testclient import TestClient


def test_parameter_extraction_success(client: TestClient):
    """Test successful parameter extraction with valid input"""
    user_input = {
        "user_input": "I need 8000 units over 12 weeks starting Jan 1, 2025. "
                     "Weekly replenishment. 15% DC holdback. "
                     "Markdown checkpoint at week 6 with 40% threshold."
    }

    response = client.post("/api/v1/parameters/extract", json=user_input)

    assert response.status_code == 200

    data = response.json()
    assert "parameters" in data
    assert "confidence" in data
    assert "reasoning" in data

    params = data["parameters"]
    assert "forecast_horizon_weeks" in params
    assert "season_start_date" in params
    assert "replenishment_strategy" in params


def test_parameter_extraction_missing_information(client: TestClient):
    """Test parameter extraction with incomplete input"""
    user_input = {
        "user_input": "I need forecast over 12 weeks."
        # Missing: start date, units, replenishment strategy
    }

    response = client.post("/api/v1/parameters/extract", json=user_input)

    # Should still return 200 with extracted parameters (LLM makes best guess)
    assert response.status_code in [200, 422]

    if response.status_code == 200:
        data = response.json()
        assert "parameters" in data


def test_parameter_extraction_invalid_json(client: TestClient):
    """Test parameter extraction with malformed JSON"""
    response = client.post(
        "/api/v1/parameters/extract",
        data="not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_parameter_extraction_empty_input(client: TestClient):
    """Test parameter extraction with empty user input"""
    user_input = {"user_input": ""}

    response = client.post("/api/v1/parameters/extract", json=user_input)

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_parameter_extraction_very_short_input(client: TestClient):
    """Test parameter extraction with very short input (< 10 characters)"""
    user_input = {"user_input": "hello"}

    response = client.post("/api/v1/parameters/extract", json=user_input)

    # Should fail validation (min_length=10)
    assert response.status_code == 422
