# Story: End-to-End Integration Testing for Orchestrator Foundation

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-006
**Status:** Ready for Implementation
**Estimate:** 5 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001, PHASE5-002, PHASE5-003, PHASE5-004, PHASE5-005

**Planning References:**
- PRD v3.3: Section 5.4 (Testing & Validation)
- Technical Architecture v3.3: Section 6.3 (Integration Testing Strategy)
- Product Brief v3.3: Section 3.5 (Quality Assurance)

---

## Story

As a backend developer,
I want to create comprehensive end-to-end integration tests for the orchestrator workflow,
So that I can verify all components work together correctly before integrating real agents in Phase 6.

**Business Value:** Integration tests are the safety net that prevents regressions. Unit tests verify individual components, but integration tests verify the entire workflow from user input → parameters → context → agent execution → results. This catches interface mismatches, race conditions, and state management issues that unit tests miss. Before investing 2-3 weeks building the real Demand Agent (Phase 6), we need confidence that the orchestrator foundation is solid.

**Epic Context:** This is Story 6 of 6 in Phase 5 (Orchestrator Foundation). It's the validation checkpoint before moving to Phase 6. These tests will be run on every code change to ensure the foundation remains stable as we add more agents.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ End-to-end test: User input → Parameters → Mock Demand Agent → Results
2. ✅ Test parameter extraction with 3 scenarios (Zara, Standard, Luxury)
3. ✅ Test historical data loading and context assembly
4. ✅ Test agent handoff with mock agents (Demand → Inventory chain)
5. ✅ Test WebSocket message flow during workflow execution
6. ✅ Test error scenarios (missing data, invalid params, agent timeout)
7. ✅ Test concurrent workflows (multiple users simultaneously)
8. ✅ Performance test: Full workflow completes in <10 seconds
9. ✅ All integration tests pass consistently (no flakiness)
10. ✅ Test coverage >80% for orchestrator module

### Quality Requirements

11. ✅ Tests use realistic data (Phase 1 CSVs or equivalent fixtures)
12. ✅ Tests clean up resources (no connection leaks, no temp files)
13. ✅ Tests can run in CI/CD pipeline
14. ✅ Test failures provide clear diagnostics (what failed, why)
15. ✅ Tests are idempotent (can run multiple times)
16. ✅ Test data is version-controlled (fixtures in repo)
17. ✅ Documentation for running tests locally

---

## Prerequisites

Before implementing this story, ensure the following are ready:

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] PHASE5-002 (Agent Handoff Framework) complete
- [x] PHASE5-003 (WebSocket Streaming) complete
- [x] PHASE5-004 (Context-Rich Handoffs) complete
- [x] PHASE5-005 (Error Handling) complete

**Testing Infrastructure:**
- [ ] pytest installed
- [ ] pytest-asyncio installed for async tests
- [ ] FastAPI TestClient available
- [ ] websockets library for WebSocket testing

**Test Data:**
- [ ] Phase 1 CSV fixtures or mock data available
- [ ] Test database/CSV files in `tests/fixtures/` directory

**Why This Matters:**
Without integration tests, every change risks breaking the workflow. These tests establish a quality baseline and enable confident refactoring as the system grows.

---

## Tasks

### Task 1: Set Up Test Infrastructure

**Goal:** Create testing framework and fixtures

**Subtasks:**
- [ ] Create directory structure:
  ```
  backend/tests/
    integration/
      __init__.py
      test_orchestrator_workflow.py
      test_websocket_integration.py
      test_error_scenarios.py
      test_performance.py
    fixtures/
      historical_sales.csv
      stores.csv
      test_parameters.json
  ```
- [ ] Create `conftest.py` with shared fixtures:
  ```python
  import pytest
  from fastapi.testclient import TestClient
  from app.main import app
  import pandas as pd
  from pathlib import Path

  @pytest.fixture
  def client():
      """FastAPI test client"""
      return TestClient(app)

  @pytest.fixture
  def test_data_dir():
      """Path to test fixtures directory"""
      return Path(__file__).parent / "fixtures"

  @pytest.fixture
  def mock_historical_sales(test_data_dir):
      """Load mock historical sales for testing"""
      return pd.read_csv(test_data_dir / "historical_sales.csv")

  @pytest.fixture
  def mock_stores_data(test_data_dir):
      """Load mock stores data for testing"""
      return pd.read_csv(test_data_dir / "stores.csv")

  @pytest.fixture
  def zara_parameters():
      """Zara-style parameters (no replenishment)"""
      return {
          "forecast_horizon_weeks": 12,
          "season_start_date": "2025-03-01",
          "season_end_date": "2025-05-23",
          "replenishment_strategy": "none",
          "dc_holdback_percentage": 0.0
      }

  @pytest.fixture
  def standard_parameters():
      """Standard retail parameters (weekly replenishment)"""
      return {
          "forecast_horizon_weeks": 26,
          "season_start_date": "2025-05-15",
          "season_end_date": "2025-11-13",
          "replenishment_strategy": "weekly",
          "dc_holdback_percentage": 0.45
      }
  ```
- [ ] Create mock test data files in `fixtures/`
- [ ] Test fixtures load correctly

---

### Task 2: Test Complete Workflow (Happy Path)

**Goal:** Verify end-to-end workflow with mock agents

**Subtasks:**
- [ ] Create file: `backend/tests/integration/test_orchestrator_workflow.py`
- [ ] **Test 1:** Complete workflow with Zara parameters
  ```python
  @pytest.mark.asyncio
  async def test_complete_workflow_zara(client, zara_parameters):
      """
      Test complete workflow: Input → Parameters → Context → Agent → Results

      Flow:
        1. Extract parameters from natural language
        2. Assemble context with historical data
        3. Call mock Demand Agent
        4. Verify results
      """
      from app.orchestrator.agent_handoff import handoff_manager
      from app.orchestrator.context_assembler import ContextAssembler
      from app.schemas.parameters import SeasonParameters

      # Step 1: Create parameters (simulate extraction)
      params = SeasonParameters(**zara_parameters)

      # Step 2: Assemble context
      assembler = ContextAssembler()
      context = await assembler.assemble_demand_context(params, "CAT001")

      # Verify context assembled correctly
      assert context.parameters == params
      assert not context.historical_data.empty
      assert not context.stores_data.empty
      assert context.category_id == "CAT001"

      # Step 3: Call mock Demand Agent
      result = await handoff_manager.call_agent("demand", context)

      # Step 4: Verify results
      assert result["agent"] == "demand"
      assert result["total_forecast"] > 0
      assert result["safety_stock_multiplier"] == 1.25  # 25% for no replenishment
      assert len(result["weekly_curve"]) == 12  # 12-week horizon
      assert "Fashion_Forward" in result["clusters"]

      # Verify execution logged
      log = handoff_manager.get_execution_log()
      assert len(log) > 0
      assert log[-1]["agent_name"] == "demand"
      assert log[-1]["status"] == "success"
  ```
- [ ] **Test 2:** Complete workflow with standard parameters
  ```python
  @pytest.mark.asyncio
  async def test_complete_workflow_standard(client, standard_parameters):
      """Test workflow with weekly replenishment strategy"""
      params = SeasonParameters(**standard_parameters)

      assembler = ContextAssembler()
      context = await assembler.assemble_demand_context(params, "CAT001")

      result = await handoff_manager.call_agent("demand", context)

      # Verify safety stock adjusted for weekly replenishment
      assert result["safety_stock_multiplier"] == 1.20  # 20% for weekly
      assert len(result["weekly_curve"]) == 26  # 26-week horizon
  ```
- [ ] **Test 3:** Agent chain (Demand → Inventory)
  ```python
  @pytest.mark.asyncio
  async def test_agent_chain_demand_to_inventory(client, zara_parameters):
      """Test handoff from Demand Agent to Inventory Agent"""
      from app.orchestrator.agent_handoff import handoff_manager

      params = SeasonParameters(**zara_parameters)

      assembler = ContextAssembler()
      demand_context = await assembler.assemble_demand_context(params, "CAT001")

      # Call Demand Agent
      forecast = await handoff_manager.call_agent("demand", demand_context)

      # Assemble Inventory context with forecast result
      inventory_context = await assembler.assemble_inventory_context(
          params,
          forecast,
          demand_context.stores_data
      )

      # Call Inventory Agent (mock)
      inventory_result = await handoff_manager.call_agent("inventory", inventory_context)

      # Verify handoff worked
      assert inventory_result["agent"] == "inventory"
      assert inventory_result["manufacturing_qty"] == 10000  # 8000 * 1.25
      assert inventory_result["forecast_received"] == 8000
  ```

---

### Task 3: Test WebSocket Integration

**Goal:** Verify WebSocket messages sent during workflow

**Subtasks:**
- [ ] Create file: `backend/tests/integration/test_websocket_integration.py`
- [ ] **Test 1:** WebSocket connection and message flow
  ```python
  @pytest.mark.asyncio
  async def test_websocket_message_flow():
      """
      Test WebSocket receives all expected message types during workflow

      Expected messages:
        1. agent_status (demand started)
        2. progress (demand in progress)
        3. complete (demand complete)
      """
      import websockets
      import json
      import asyncio

      session_id = "test_session_123"
      messages_received = []

      # Connect to WebSocket
      async with websockets.connect(
          f"ws://localhost:8000/ws/orchestrator/{session_id}"
      ) as websocket:

          # Trigger workflow in background
          async def run_workflow():
              # Simulate workflow execution
              from app.orchestrator.agent_handoff import handoff_manager

              params = SeasonParameters(
                  forecast_horizon_weeks=12,
                  season_start_date=date(2025, 3, 1),
                  season_end_date=date(2025, 5, 23),
                  replenishment_strategy="none",
                  dc_holdback_percentage=0.0
              )

              assembler = ContextAssembler()
              context = await assembler.assemble_demand_context(params)

              await handoff_manager.call_agent(
                  "demand",
                  context,
                  session_id=session_id  # Enable WebSocket updates
              )

          # Start workflow and listen for messages
          workflow_task = asyncio.create_task(run_workflow())

          # Collect messages
          async for message in websocket:
              data = json.loads(message)
              messages_received.append(data)

              # Stop when we receive complete message
              if data.get("type") == "complete":
                  break

          await workflow_task

      # Verify expected messages received
      assert len(messages_received) >= 2  # At least started + completed

      message_types = [m["type"] for m in messages_received]
      assert "agent_status" in message_types
      assert "complete" in message_types

      # Verify message structure
      for message in messages_received:
          assert "type" in message
          assert "timestamp" in message
          assert "session_id" in message
          assert message["session_id"] == session_id
  ```
- [ ] **Test 2:** Multiple concurrent WebSocket connections
  ```python
  @pytest.mark.asyncio
  async def test_multiple_concurrent_connections():
      """Test multiple users can connect simultaneously"""
      import websockets

      session_ids = ["session_1", "session_2", "session_3"]
      connections = []

      # Connect 3 clients
      for session_id in session_ids:
          ws = await websockets.connect(
              f"ws://localhost:8000/ws/orchestrator/{session_id}"
          )
          connections.append(ws)

      # Verify all connected
      from app.orchestrator.websocket_manager import connection_manager
      assert connection_manager.get_connection_count() == 3

      # Close all
      for ws in connections:
          await ws.close()

      # Verify all disconnected
      assert connection_manager.get_connection_count() == 0
  ```

---

### Task 4: Test Error Scenarios

**Goal:** Verify error handling works correctly

**Subtasks:**
- [ ] Create file: `backend/tests/integration/test_error_scenarios.py`
- [ ] **Test 1:** Missing historical data
  ```python
  @pytest.mark.asyncio
  async def test_missing_historical_data_error():
      """Test workflow fails gracefully when data missing"""
      from app.exceptions import DataNotFoundError

      params = SeasonParameters(
          forecast_horizon_weeks=12,
          season_start_date=date(2025, 3, 1),
          season_end_date=date(2025, 5, 23),
          replenishment_strategy="none",
          dc_holdback_percentage=0.0
      )

      assembler = ContextAssembler()

      with pytest.raises(DataNotFoundError) as exc_info:
          await assembler.assemble_demand_context(params, "INVALID_CATEGORY")

      assert "No historical data" in str(exc_info.value)
  ```
- [ ] **Test 2:** Agent timeout
  ```python
  @pytest.mark.asyncio
  async def test_agent_timeout_handling():
      """Test workflow handles agent timeout gracefully"""
      from app.exceptions import AgentTimeoutError

      # Register slow agent
      async def slow_agent(context):
          await asyncio.sleep(10)  # Exceeds timeout
          return {}

      handoff_manager.register_agent("slow_agent", slow_agent)

      with pytest.raises(AgentTimeoutError) as exc_info:
          await handoff_manager.call_agent("slow_agent", {}, timeout=2)

      assert exc_info.value.agent_name == "slow_agent"
      assert exc_info.value.timeout == 2
  ```
- [ ] **Test 3:** Invalid parameters
  ```python
  def test_invalid_parameters_validation():
      """Test parameter validation catches invalid values"""
      from pydantic import ValidationError

      with pytest.raises(ValidationError):
          SeasonParameters(
              forecast_horizon_weeks=100,  # Exceeds 52 week limit
              season_start_date=date(2025, 3, 1),
              season_end_date=date(2025, 5, 23),
              replenishment_strategy="none",
              dc_holdback_percentage=0.0
          )
  ```
- [ ] **Test 4:** API endpoint error responses
  ```python
  def test_api_error_responses(client):
      """Test API returns correct error responses"""
      # Test 404 for missing data
      response = client.post(
          "/api/orchestrator/run-workflow",
          json={
              "strategy_description": "12-week season",
              "session_id": "test123",
              "category_id": "INVALID"
          }
      )

      assert response.status_code == 404
      data = response.json()
      assert data["error"] == "DataNotFoundError"
      assert "request_id" in data
  ```

---

### Task 5: Performance Testing

**Goal:** Verify workflow meets performance requirements

**Subtasks:**
- [ ] Create file: `backend/tests/integration/test_performance.py`
- [ ] **Test 1:** Full workflow execution time
  ```python
  @pytest.mark.asyncio
  async def test_workflow_performance():
      """Test complete workflow completes in <10 seconds"""
      import time

      params = SeasonParameters(
          forecast_horizon_weeks=12,
          season_start_date=date(2025, 3, 1),
          season_end_date=date(2025, 5, 23),
          replenishment_strategy="none",
          dc_holdback_percentage=0.0
      )

      start_time = time.time()

      # Run complete workflow
      assembler = ContextAssembler()
      context = await assembler.assemble_demand_context(params, "CAT001")
      result = await handoff_manager.call_agent("demand", context)

      duration = time.time() - start_time

      # Verify performance target met
      assert duration < 10.0, f"Workflow took {duration:.2f}s (target: <10s)"

      print(f"✅ Workflow completed in {duration:.2f}s")
  ```
- [ ] **Test 2:** Context assembly performance
  ```python
  @pytest.mark.asyncio
  async def test_context_assembly_performance():
      """Test context assembly completes in <2 seconds"""
      import time

      params = SeasonParameters(
          forecast_horizon_weeks=12,
          season_start_date=date(2025, 3, 1),
          season_end_date=date(2025, 5, 23),
          replenishment_strategy="none",
          dc_holdback_percentage=0.0
      )

      assembler = ContextAssembler()

      start_time = time.time()
      context = await assembler.assemble_demand_context(params, "CAT001")
      duration = time.time() - start_time

      assert duration < 2.0, f"Context assembly took {duration:.2f}s (target: <2s)"
  ```
- [ ] **Test 3:** Concurrent workflow execution
  ```python
  @pytest.mark.asyncio
  async def test_concurrent_workflows():
      """Test multiple workflows can run simultaneously"""
      import asyncio

      async def run_single_workflow(session_id: str):
          params = SeasonParameters(
              forecast_horizon_weeks=12,
              season_start_date=date(2025, 3, 1),
              season_end_date=date(2025, 5, 23),
              replenishment_strategy="none",
              dc_holdback_percentage=0.0
          )

          assembler = ContextAssembler()
          context = await assembler.assemble_demand_context(params, "CAT001")
          result = await handoff_manager.call_agent("demand", context, session_id=session_id)
          return result

      # Run 5 workflows concurrently
      tasks = [
          run_single_workflow(f"session_{i}")
          for i in range(5)
      ]

      results = await asyncio.gather(*tasks)

      # Verify all succeeded
      assert len(results) == 5
      for result in results:
          assert result["total_forecast"] == 8000
  ```

---

### Task 6: Set Up CI/CD Test Execution

**Goal:** Configure tests to run automatically

**Subtasks:**
- [ ] Create `.github/workflows/test.yml` (if using GitHub Actions):
  ```yaml
  name: Backend Tests

  on: [push, pull_request]

  jobs:
    test:
      runs-on: ubuntu-latest

      steps:
        - uses: actions/checkout@v3

        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'

        - name: Install dependencies
          run: |
            pip install uv
            uv sync

        - name: Run unit tests
          run: |
            uv run pytest backend/tests/unit -v

        - name: Run integration tests
          run: |
            uv run pytest backend/tests/integration -v

        - name: Generate coverage report
          run: |
            uv run pytest --cov=backend/app --cov-report=html

        - name: Upload coverage
          uses: codecov/codecov-action@v3
  ```
- [ ] Create `pytest.ini` configuration:
  ```ini
  [pytest]
  testpaths = backend/tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  asyncio_mode = auto
  markers =
      integration: Integration tests (require backend running)
      unit: Unit tests (fast, no dependencies)
      performance: Performance tests
  ```
- [ ] Test CI/CD pipeline locally

---

### Task 7: Documentation

**Goal:** Document testing approach and how to run tests

**Subtasks:**
- [ ] Create `backend/tests/README.md`:
  ```markdown
  # Backend Testing Guide

  ## Test Structure

  ```
  tests/
    unit/                    # Fast, isolated unit tests
    integration/             # End-to-end integration tests
    fixtures/                # Test data files
    conftest.py              # Shared fixtures
  ```

  ## Running Tests

  **All tests:**
  ```bash
  uv run pytest backend/tests -v
  ```

  **Unit tests only:**
  ```bash
  uv run pytest backend/tests/unit -v
  ```

  **Integration tests only:**
  ```bash
  uv run pytest backend/tests/integration -v
  ```

  **With coverage:**
  ```bash
  uv run pytest --cov=backend/app --cov-report=html
  ```

  ## Test Data

  Test fixtures are in `tests/fixtures/`:
  - `historical_sales.csv` - Mock historical sales (52 weeks)
  - `stores.csv` - Mock store attributes (50 stores)

  ## Writing Tests

  **Unit tests** test individual functions/classes in isolation.

  **Integration tests** test complete workflows end-to-end.

  See `conftest.py` for available fixtures.
  ```
- [ ] Add testing section to main README

---

## Implementation Notes

**Running Integration Tests:**
```bash
# Start backend server in one terminal
uv run uvicorn app.main:app --reload

# Run integration tests in another terminal
uv run pytest backend/tests/integration -v
```

**Test Coverage Goals:**
- Overall: >80%
- Orchestrator module: >90%
- Agent handoff: >95%
- Critical paths: 100%

**Continuous Integration:**
Tests run automatically on every commit to main branch and all pull requests.

---

## Definition of Done

- [ ] Test infrastructure set up (conftest.py, fixtures)
- [ ] Mock test data created in fixtures directory
- [ ] Complete workflow tests (Zara, Standard, Luxury scenarios)
- [ ] Agent chain tests (Demand → Inventory)
- [ ] WebSocket integration tests
- [ ] Error scenario tests (missing data, timeouts, invalid params)
- [ ] Performance tests (<10s workflow, <2s context assembly)
- [ ] Concurrent workflow tests
- [ ] All tests passing consistently
- [ ] Test coverage >80% for orchestrator module
- [ ] CI/CD pipeline configured
- [ ] Testing documentation written
- [ ] Code reviewed and merged

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
