"""
Tests for health check endpoint.
"""

import pytest
from fastapi import status


def test_health_check(client):
    """
    Test health check endpoint returns 200 OK.
    """
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data


def test_health_check_structure(client):
    """
    Test health check response has expected structure.
    """
    response = client.get("/api/v1/health")
    data = response.json()

    # Verify all expected keys
    expected_keys = ["status", "version", "timestamp", "services"]
    for key in expected_keys:
        assert key in data

    # Verify services status
    assert "database" in data["services"]
    assert "api" in data["services"]
    assert data["services"]["database"] == "ok"
    assert data["services"]["api"] == "ok"
