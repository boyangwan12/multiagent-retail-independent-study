# Story: Integration Testing for Inventory Agent

**Epic:** Phase 7 - Inventory Agent
**Story ID:** PHASE7-004
**Status:** ✅ Complete
**Estimate:** 6 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE7-001, PHASE7-002, PHASE7-003 complete

**Planning References:**
- PRD v3.3: Section 5 (Inventory Agent Integration)
- Technical Architecture v3.3: Section 6 (Inventory Agent)
- technical_decisions.md: TD-7.10 (InventoryAgentOutput Contract)

---

## Story

As a backend developer,
I want to create comprehensive integration tests for the Inventory Agent,
So that I can verify end-to-end functionality with Phase 6 Demand Agent and Phase 5 orchestrator, and ensure parameter-driven behavior works correctly.

**Business Value:** Integration testing validates that all Phase 7 components work together correctly and integrate seamlessly with existing Phase 5/6 infrastructure. This ensures production readiness and prevents regressions.

**Epic Context:** This is Story 4 of 4 in Phase 7 (final story). This story validates all previous work (Stories 1-3) and ensures Phase 7 is ready for Phase 8 handoff.

---

## Acceptance Criteria

### Functional Requirements

1. ☐ End-to-end test: Phase 6 forecast → Phase 7 allocation
2. ☐ Parameter-driven test: 0% holdback (Zara) scenario
3. ☐ Parameter-driven test: 45% holdback (Standard retail) scenario
4. ☐ Output contract validation (InventoryAgentOutput schema)
5. ☐ Performance test: <15 seconds (Phase 6 + Phase 7 combined)
6. ☐ Unit conservation verification (no loss/gain)

### Quality Requirements

7. ☐ 3+ integration tests passing
8. ☐ End-to-end workflow validated
9. ☐ Parameter adaptation verified
10. ☐ Performance target met
11. ☐ All docstrings complete
12. ☐ Test coverage report generated

---

## Prerequisites

**Stories 1-3 Complete:**
- [x] PHASE7-001 (K-means clustering) complete
- [x] PHASE7-002 (Allocation logic) complete
- [x] PHASE7-003 (Replenishment scheduling) complete

**Phase 6 Complete:**
- [x] Demand Agent operational
- [x] Forecast output available

**Phase 5 Complete:**
- [x] AgentHandoffManager operational
- [x] ContextAssembler available

---

## Tasks

### Task 1: Create Integration Test File

**Goal:** Set up integration test infrastructure

**Subtasks:**
- [ ] Create file: `backend/tests/integration/test_inventory_agent_integration.py`
- [ ] Import dependencies:
  ```python
  import pytest
  import pandas as pd
  import time
  from app.agents.demand_agent import DemandAgent
  from app.agents.inventory_agent import InventoryAgent
  from app.schemas.workflow_schemas import SeasonParameters, InventoryAgentOutput
  from app.ml.store_clustering import StoreClusterer
  ```
- [ ] Create test fixtures:
  - `historical_data`: 52 weeks of sales data
  - `stores_data`: 50 stores with 7 features
  - `season_parameters_zara`: 0% holdback, replenishment="none"
  - `season_parameters_standard`: 45% holdback, replenishment="weekly"

---

### Task 2: Test End-to-End Phase 6 → Phase 7 Workflow

**Goal:** Verify Demand Agent → Inventory Agent handoff

**Subtasks:**
- [ ] Implement `test_end_to_end_phase6_to_phase7()`:
  ```python
  @pytest.mark.asyncio
  async def test_end_to_end_phase6_to_phase7(
      historical_data,
      stores_data,
      season_parameters_standard
  ):
      """Test Phase 6 Demand Agent → Phase 7 Inventory Agent workflow."""
      # Step 1: Run Phase 6 Demand Agent
      demand_agent = DemandAgent()
      forecast_result = await demand_agent.execute(
          category_id="womens_dresses",
          parameters=season_parameters_standard,
          historical_data=historical_data
      )

      # Verify Phase 6 output
      assert "total_demand" in forecast_result
      assert "forecast_by_week" in forecast_result
      assert "safety_stock_pct" in forecast_result
      assert "confidence" in forecast_result

      # Step 2: Run Phase 7 Inventory Agent
      inventory_agent = InventoryAgent()
      allocation_result = await inventory_agent.execute(
          forecast_result=forecast_result,
          parameters=season_parameters_standard,
          stores_data=stores_data
      )

      # Verify Phase 7 output matches contract
      validated_output = InventoryAgentOutput(**allocation_result)

      # Verify manufacturing calculation
      expected_manufacturing = int(
          forecast_result["total_demand"] * (1 + forecast_result["safety_stock_pct"])
      )
      assert allocation_result["manufacturing_qty"] == expected_manufacturing

      # Verify DC holdback (45%)
      assert allocation_result["dc_holdback_total"] == int(expected_manufacturing * 0.45)
      assert allocation_result["initial_allocation_total"] == int(expected_manufacturing * 0.55)

      # Verify unit conservation
      assert (
          allocation_result["initial_allocation_total"] +
          allocation_result["dc_holdback_total"]
      ) == expected_manufacturing

      # Verify clusters present
      assert len(allocation_result["clusters"]) == 3

      # Verify store allocations sum correctly
      total_store_allocation = sum(
          sum(store["initial_allocation"] for store in cluster["stores"])
          for cluster in allocation_result["clusters"]
      )
      assert total_store_allocation == allocation_result["initial_allocation_total"]

      print(f"✅ End-to-end test passed: {expected_manufacturing} units allocated correctly")
  ```

**Acceptance:**
- Test passes
- Phase 6 → Phase 7 handoff working
- Output contract validated
- Unit conservation verified

---

### Task 3: Test Parameter-Driven Behavior (0% Holdback - Zara)

**Goal:** Verify fast fashion scenario

**Subtasks:**
- [ ] Implement `test_parameter_driven_0_percent_holdback()`:
  ```python
  @pytest.mark.asyncio
  async def test_parameter_driven_0_percent_holdback(
      historical_data,
      stores_data,
      season_parameters_zara
  ):
      """Test Zara scenario: 0% holdback, 100% initial allocation, no replenishment."""
      # Run Phase 6
      demand_agent = DemandAgent()
      forecast_result = await demand_agent.execute(
          category_id="womens_dresses",
          parameters=season_parameters_zara,
          historical_data=historical_data
      )

      # Run Phase 7
      inventory_agent = InventoryAgent()
      allocation_result = await inventory_agent.execute(
          forecast_result=forecast_result,
          parameters=season_parameters_zara,
          stores_data=stores_data
      )

      # Verify 0% DC holdback
      assert allocation_result["dc_holdback_total"] == 0
      assert allocation_result["initial_allocation_total"] == allocation_result["manufacturing_qty"]

      # Verify replenishment disabled
      assert allocation_result["replenishment_enabled"] == False
      assert allocation_result["replenishment_queue"] == []

      # Verify 100% allocated to stores
      total_store_allocation = sum(
          sum(store["initial_allocation"] for store in cluster["stores"])
          for cluster in allocation_result["clusters"]
      )
      assert total_store_allocation == allocation_result["manufacturing_qty"]

      print("✅ Zara scenario test passed: 100% allocated, replenishment disabled")
  ```

**Acceptance:**
- Test passes
- 0% holdback verified
- Replenishment disabled
- 100% allocation confirmed

---

### Task 4: Test Parameter-Driven Behavior (45% Holdback - Standard)

**Goal:** Verify standard retail scenario

**Subtasks:**
- [ ] Implement `test_parameter_driven_45_percent_holdback()`:
  ```python
  @pytest.mark.asyncio
  async def test_parameter_driven_45_percent_holdback(
      historical_data,
      stores_data,
      season_parameters_standard
  ):
      """Test Standard retail scenario: 45% holdback, 55% initial allocation, weekly replenishment."""
      # Run Phase 6
      demand_agent = DemandAgent()
      forecast_result = await demand_agent.execute(
          category_id="womens_dresses",
          parameters=season_parameters_standard,
          historical_data=historical_data
      )

      # Run Phase 7
      inventory_agent = InventoryAgent()
      allocation_result = await inventory_agent.execute(
          forecast_result=forecast_result,
          parameters=season_parameters_standard,
          stores_data=stores_data
      )

      # Verify 45% DC holdback
      expected_holdback = int(allocation_result["manufacturing_qty"] * 0.45)
      expected_initial = allocation_result["manufacturing_qty"] - expected_holdback
      assert allocation_result["dc_holdback_total"] == expected_holdback
      assert allocation_result["initial_allocation_total"] == expected_initial

      # Verify replenishment enabled
      assert allocation_result["replenishment_enabled"] == True

      # Verify 55% allocated to stores
      total_store_allocation = sum(
          sum(store["initial_allocation"] for store in cluster["stores"])
          for cluster in allocation_result["clusters"]
      )
      assert total_store_allocation == expected_initial

      print("✅ Standard retail scenario test passed: 55/45 split, replenishment enabled")
  ```

**Acceptance:**
- Test passes
- 45% holdback verified
- Replenishment enabled
- 55/45 split confirmed

---

### Task 5: Performance Test (<15 Seconds)

**Goal:** Verify Phase 6 + Phase 7 completes within performance target

**Subtasks:**
- [ ] Implement `test_performance_under_15_seconds()`:
  ```python
  @pytest.mark.asyncio
  async def test_performance_under_15_seconds(
      historical_data,
      stores_data,
      season_parameters_standard
  ):
      """Test Phase 6 + Phase 7 workflow completes in <15 seconds."""
      start_time = time.time()

      # Run Phase 6
      demand_agent = DemandAgent()
      forecast_result = await demand_agent.execute(
          category_id="womens_dresses",
          parameters=season_parameters_standard,
          historical_data=historical_data
      )

      # Run Phase 7
      inventory_agent = InventoryAgent()
      allocation_result = await inventory_agent.execute(
          forecast_result=forecast_result,
          parameters=season_parameters_standard,
          stores_data=stores_data
      )

      elapsed_time = time.time() - start_time

      # Verify performance target
      assert elapsed_time < 15.0, f"Workflow took {elapsed_time:.2f}s (target: <15s)"

      print(f"✅ Performance test passed: {elapsed_time:.2f} seconds (target: <15s)")
  ```

**Acceptance:**
- Test passes
- Runtime <15 seconds
- Performance target met

---

## Testing Strategy

### Integration Tests (This Story)
- **Test 1:** End-to-end Phase 6 → Phase 7 workflow
- **Test 2:** Parameter-driven 0% holdback (Zara)
- **Test 3:** Parameter-driven 45% holdback (Standard)
- **Test 4:** Performance test (<15 seconds)

### Validation Checks
- Output contract (Pydantic validation)
- Unit conservation (no loss/gain)
- Parameter adaptation (0% vs 45%)
- Performance benchmarking

---

## Definition of Done

**Code Complete:**
- [ ] All 3+ integration tests implemented
- [ ] Test fixtures created
- [ ] Type hints and docstrings complete

**Testing Complete:**
- [ ] All integration tests passing
- [ ] End-to-end workflow validated
- [ ] Parameter-driven behavior verified
- [ ] Performance target met (<15 seconds)
- [ ] Output contract validated

**Quality Checks:**
- [ ] Test coverage report generated
- [ ] All validation checks passing
- [ ] Performance benchmarked

**Documentation:**
- [ ] Test scenarios documented
- [ ] Integration points explained
- [ ] Ready for Phase 8 handoff

**Phase 7 Complete:**
- [ ] All 4 stories (001-004) complete
- [ ] Inventory Agent operational
- [ ] Ready to hand off allocation_plan to Phase 8 (Pricing Agent)

---

## Notes

**Integration Test Best Practices:**
- Use realistic test data (50 stores, 52 weeks historical)
- Test both parameter scenarios (0% and 45% holdback)
- Validate output contracts explicitly (Pydantic schemas)
- Benchmark performance on every test run

**Performance Breakdown Target:**
- Phase 6 (Demand Agent): <10 seconds
- Phase 7 (Inventory Agent): <5 seconds
- **Total:** <15 seconds

**Common Issues:**
- **Fixture Data Quality:** Ensure test data representative of production
- **Async Test Timeouts:** Use `@pytest.mark.asyncio` and reasonable timeouts
- **Unit Conservation Failures:** Check rounding errors in test assertions

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
