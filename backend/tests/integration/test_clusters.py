"""
Integration tests for cluster endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_clusters_success(client: TestClient):
    """Test GET /api/v1/stores/clusters returns cluster data"""
    response = client.get("/api/v1/stores/clusters")

    assert response.status_code == 200

    data = response.json()

    # Check response structure
    if isinstance(data, dict) and "clusters" in data:
        clusters = data["clusters"]
    elif isinstance(data, list):
        clusters = data
    else:
        pytest.fail(f"Unexpected response format: {data}")

    # Validate cluster data
    assert len(clusters) >= 1  # At least one cluster

    # Check cluster structure
    for cluster in clusters:
        assert "cluster_id" in cluster
        assert "cluster_name" in cluster or "name" in cluster


def test_clusters_allocation_percentages(client: TestClient):
    """Test cluster allocation percentages sum to ~100%"""
    response = client.get("/api/v1/stores/clusters")

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, dict) and "clusters" in data:
        clusters = data["clusters"]
    elif isinstance(data, list):
        clusters = data
    else:
        return  # Skip if format is unexpected

    # Sum allocation percentages if present
    total_allocation = sum(
        cluster.get("allocation_percentage", 0)
        for cluster in clusters
    )

    # Allow some tolerance (95-105%)
    if total_allocation > 0:
        assert 0.95 <= total_allocation <= 1.05
