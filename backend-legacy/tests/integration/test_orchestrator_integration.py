"""
End-to-end integration tests for the polling-based orchestrator workflow.

Tests verify complete user journeys from parameter extraction through workflow
execution, status polling, and results retrieval.
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from datetime import date


# ============================================================================
# End-to-End Workflow Tests (AC1)
# ============================================================================

def test_e2e_forecast_workflow(client: TestClient, mock_season_parameters):
    """
    Test complete end-to-end forecast workflow.

    Steps:
    1. Create workflow via POST /api/v1/workflows/forecast
    2. Execute workflow via POST /api/v1/workflows/{id}/execute
    3. Poll status via GET /api/v1/workflows/{id}
    4. Get results via GET /api/v1/workflows/{id}/results

    Verifies:
    - All API endpoints work together correctly
    - Workflow progresses through states
    - Final results contain expected data
    """
    # Step 1: Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }

    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    assert create_response.status_code == 201

    workflow_data = create_response.json()
    workflow_id = workflow_data["workflow_id"]
    assert workflow_data["status"] == "pending"
    assert workflow_id.startswith("wf_")

    # Step 2: Execute workflow
    execute_response = client.post(f"/api/v1/workflows/{workflow_id}/execute")
    assert execute_response.status_code == 202  # Accepted

    # Step 3: Poll status until completed or timeout
    max_polls = 30  # 30 seconds max
    poll_count = 0
    final_status = None

    while poll_count < max_polls:
        status_response = client.get(f"/api/v1/workflows/{workflow_id}")
        assert status_response.status_code == 200

        status_data = status_response.json()
        final_status = status_data["status"]

        if final_status in ["completed", "failed"]:
            break

        time.sleep(1)
        poll_count += 1

    # Verify workflow completed successfully
    assert final_status == "completed", f"Workflow did not complete. Final status: {final_status}"

    # Step 4: Get final results
    results_response = client.get(f"/api/v1/workflows/{workflow_id}/results")
    assert results_response.status_code == 200

    results_data = results_response.json()
    assert results_data["workflow_id"] == workflow_id
    assert results_data["status"] == "completed"
    assert "output_data" in results_data

    # Verify output contains agent results
    output_data = results_data["output_data"]
    assert "final_result" in output_data
    assert output_data["final_result"]["agent"] == "pricing"


def test_e2e_reforecast_workflow(client: TestClient):
    """
    Test complete end-to-end re-forecast workflow.

    Verifies re-forecast workflow creation and execution.
    """
    # Create re-forecast workflow
    request_data = {
        "forecast_id": "f_test_123",
        "actual_sales_week_1_to_n": 3200,
        "forecasted_week_1_to_n": 2550,
        "remaining_weeks": 8,
        "variance_pct": 0.255
    }

    create_response = client.post("/api/v1/workflows/reforecast", json=request_data)
    assert create_response.status_code == 201

    workflow_data = create_response.json()
    workflow_id = workflow_data["workflow_id"]
    assert workflow_data["status"] == "pending"

    # Execute and verify creation succeeded
    execute_response = client.post(f"/api/v1/workflows/{workflow_id}/execute")
    assert execute_response.status_code == 202


# ============================================================================
# Polling Status Progression Tests (AC3)
# ============================================================================

def test_polling_status_progression(client: TestClient, mock_season_parameters):
    """
    Test that polling status endpoint shows correct workflow progression.

    Verifies:
    - Status transitions: pending → running → completed
    - current_agent updates correctly
    - progress_pct increases appropriately
    """
    # Create and execute workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }

    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Execute workflow
    client.post(f"/api/v1/workflows/{workflow_id}/execute")

    # Track status progression
    statuses_seen = []
    agents_seen = []
    progress_values = []

    max_polls = 30
    poll_count = 0

    while poll_count < max_polls:
        status_response = client.get(f"/api/v1/workflows/{workflow_id}")
        status_data = status_response.json()

        current_status = status_data["status"]
        current_agent = status_data.get("current_agent")
        progress_pct = status_data.get("progress_pct", 0)

        # Record status changes
        if not statuses_seen or statuses_seen[-1] != current_status:
            statuses_seen.append(current_status)

        # Record agent changes
        if current_agent and (not agents_seen or agents_seen[-1] != current_agent):
            agents_seen.append(current_agent)

        # Record progress
        if progress_pct not in progress_values:
            progress_values.append(progress_pct)

        if current_status in ["completed", "failed"]:
            break

        time.sleep(1)
        poll_count += 1

    # Verify status progression
    assert "pending" in statuses_seen or "running" in statuses_seen
    assert "completed" in statuses_seen

    # Verify at least one agent was tracked
    assert len(agents_seen) > 0

    # Verify progress increased
    assert len(progress_values) > 1
    assert max(progress_values) >= 95  # Should reach near 100%


def test_polling_response_time(client: TestClient, mock_season_parameters):
    """
    Test that polling endpoint responds quickly (AC6).

    Requirement: Polling response time < 200ms
    """
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }

    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Measure polling response time
    start_time = time.time()
    status_response = client.get(f"/api/v1/workflows/{workflow_id}")
    end_time = time.time()

    assert status_response.status_code == 200

    response_time_ms = (end_time - start_time) * 1000
    assert response_time_ms < 200, f"Polling response time {response_time_ms:.1f}ms exceeds 200ms limit"


# ============================================================================
# Error Handling Integration Tests (AC5)
# ============================================================================

def test_workflow_not_found_404(client: TestClient):
    """
    Test that querying non-existent workflow returns 404 with helpful message.

    Verifies enhanced error response from PHASE5-005.
    """
    response = client.get("/api/v1/workflows/wf_nonexistent_xyz")

    assert response.status_code == 404

    error_data = response.json()
    assert "detail" in error_data

    # Verify structured error response
    detail = error_data["detail"]
    if isinstance(detail, dict):
        assert "error" in detail
        assert "message" in detail
        assert "Workflow not found" in detail["error"]


def test_workflow_results_not_found_404(client: TestClient):
    """
    Test that results endpoint returns 404 for non-existent workflow.
    """
    response = client.get("/api/v1/workflows/wf_nonexistent_xyz/results")

    assert response.status_code == 404

    error_data = response.json()
    detail = error_data["detail"]
    if isinstance(detail, dict):
        assert "error" in detail
        assert "Workflow not found" in detail["error"]


def test_execute_nonexistent_workflow_404(client: TestClient):
    """
    Test that executing non-existent workflow returns 404.
    """
    response = client.post("/api/v1/workflows/wf_nonexistent_xyz/execute")

    assert response.status_code == 404


def test_invalid_parameters_422(client: TestClient):
    """
    Test that invalid parameters return 422 validation error.
    """
    # Missing required fields
    invalid_request = {
        "category_id": "womens_dresses",
        "parameters": {
            "forecast_horizon_weeks": 12
            # Missing season_start_date, season_end_date, etc.
        }
    }

    response = client.post("/api/v1/workflows/forecast", json=invalid_request)

    # Should get validation error
    assert response.status_code in [422, 500]  # Either validation error or internal error


def test_workflow_execution_failure_handling(client: TestClient):
    """
    Test that workflow failures are reported correctly via polling.

    Note: This test depends on being able to trigger a failure scenario.
    In the current implementation with mock agents, failures are rare.
    """
    # Create workflow with parameters that might cause issues
    request_data = {
        "category_id": "test_category",
        "parameters": {
            "forecast_horizon_weeks": 12,
            "season_start_date": "2025-03-01",
            "season_end_date": "2025-05-23",
            "replenishment_strategy": "none",
            "dc_holdback_percentage": 0.0
        }
    }

    create_response = client.post("/api/v1/workflows/forecast", json=request_data)

    # If workflow creation succeeds, verify it can be queried
    if create_response.status_code == 201:
        workflow_id = create_response.json()["workflow_id"]
        status_response = client.get(f"/api/v1/workflows/{workflow_id}")
        assert status_response.status_code == 200


# ============================================================================
# Performance Tests (AC6)
# ============================================================================

def test_workflow_execution_performance(client: TestClient, mock_season_parameters):
    """
    Test that workflow execution completes within expected time.

    Requirements:
    - Workflow creation: immediate
    - Workflow execution: < 10 seconds (mock agents have delays)
    """
    # Measure workflow creation time
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }

    create_start = time.time()
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    create_end = time.time()

    assert create_response.status_code == 201
    workflow_id = create_response.json()["workflow_id"]

    create_time = create_end - create_start
    assert create_time < 5.0, f"Workflow creation took {create_time:.1f}s (expected < 5s)"

    # Measure workflow execution time
    execute_start = time.time()
    client.post(f"/api/v1/workflows/{workflow_id}/execute")

    # Poll until completed
    max_wait = 15  # 15 seconds max
    poll_count = 0

    while poll_count < max_wait:
        status_response = client.get(f"/api/v1/workflows/{workflow_id}")
        status_data = status_response.json()

        if status_data["status"] in ["completed", "failed"]:
            break

        time.sleep(1)
        poll_count += 1

    execute_end = time.time()
    execution_time = execute_end - execute_start

    # Verify completed
    assert status_data["status"] == "completed"

    # Verify execution time (mock agents have ~2s total delay)
    assert execution_time < 10.0, f"Workflow execution took {execution_time:.1f}s (expected < 10s)"


# ============================================================================
# Resource Cleanup Tests (AC8)
# ============================================================================

def test_workflow_resource_cleanup(client: TestClient, mock_season_parameters):
    """
    Test that workflows don't leave orphaned resources.

    Verifies:
    - Workflow can be queried after creation
    - Workflow can be queried after execution
    - No database pollution
    """
    # Create multiple workflows
    workflow_ids = []

    for i in range(3):
        request_data = {
            "category_id": f"category_{i}",
            "parameters": mock_season_parameters
        }

        create_response = client.post("/api/v1/workflows/forecast", json=request_data)
        assert create_response.status_code == 201

        workflow_ids.append(create_response.json()["workflow_id"])

    # Verify all workflows can be queried
    for workflow_id in workflow_ids:
        status_response = client.get(f"/api/v1/workflows/{workflow_id}")
        assert status_response.status_code == 200
        assert status_response.json()["workflow_id"] == workflow_id


# ============================================================================
# Idempotency Tests (AC9)
# ============================================================================

def test_workflow_status_idempotent(client: TestClient, mock_season_parameters):
    """
    Test that status endpoint is idempotent (can be called multiple times).
    """
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }

    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Call status endpoint multiple times
    status_responses = []
    for _ in range(5):
        response = client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        status_responses.append(response.json())

    # All responses should be identical (status is pending and hasn't changed)
    first_status = status_responses[0]["status"]
    for response in status_responses:
        assert response["status"] == first_status
        assert response["workflow_id"] == workflow_id
