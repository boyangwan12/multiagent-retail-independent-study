# Story: Enhanced Mock Agents with Parameter-Aware Logic

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-004
**Status:** Review
**Estimate:** 2 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001 (Parameter Extraction), PHASE5-002 (Agent Handoff Framework)

**Planning References:**
- PRD v3.3: Section 4.1 (Parameter-Driven Agent Behavior)
- Technical Architecture v3.3: Section 4.4 (Orchestrator - Agent Reasoning)

---

## Story

As a backend developer,
I want to enhance mock agents to demonstrate parameter-aware decision-making,
So that the orchestrator framework showcases adaptive agent behavior before implementing real ML agents in Phase 6.

**Business Value:** This story bridges Phase 5 (orchestration infrastructure) and Phase 6 (real agents). By enhancing mock agents to adapt their behavior based on input parameters, we demonstrate the parameter-driven architecture working end-to-end. This validates the orchestration framework and provides clear examples for Phase 6 implementation. Mock agents that adapt to different scenarios (Zara vs. traditional retail) prove the system can support diverse business strategies without code changes.

**Epic Context:** This is Story 4 of 6 in Phase 5 (Orchestrator Foundation). Stories 1-3 built the infrastructure (parameter extraction, agent handoffs, polling). This story enhances the mock agents to showcase intelligent behavior within that infrastructure. The enhanced agents will be used in Story 6 (Integration Testing) to validate different workflow scenarios.

**Phase 5 Update:** This story replaces the original PHASE5-004 (Context-Rich Handoffs with Historical Data) which assumed database queries and historical data processing. Since mock agents return hard-coded data and don't perform actual forecasting, we don't need complex context assembly yet. That infrastructure will be built in Phase 6 when implementing real Prophet/ARIMA agents that require historical sales data.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ Mock Demand Agent adapts safety stock based on `replenishment_strategy`
   - "none" → 25% safety stock (no replenishment buffer)
   - "weekly" → 20% safety stock (can restock frequently)
   - "bi-weekly" → 22% safety stock (moderate buffer)

2. ✅ Mock Demand Agent adapts forecast horizon to match user input
   - Uses `forecast_horizon_weeks` to size weekly_curve array
   - Truncates or extends baseline curve (12 weeks) as needed

3. ✅ Mock Inventory Agent adapts DC holdback based on `dc_holdback_percentage`
   - Calculates DC reserve units: `total_forecast × dc_holdback_percentage`
   - Adjusts initial store allocation accordingly

4. ✅ Mock Inventory Agent adapts manufacturing orders based on replenishment strategy
   - "none" → Single large order at week 1
   - "weekly" → Split across 3 orders (weeks 1, 5, 9)
   - "bi-weekly" → Split across 2 orders (weeks 1, 7)

5. ✅ Mock Pricing Agent adapts markdown timing based on `markdown_checkpoint_week`
   - If provided: Check markdown at specified week
   - If null: No markdown strategy (full-price sellthrough)

6. ✅ Mock Pricing Agent adapts markdown percentage based on `markdown_threshold`
   - Threshold < 0.5 → Aggressive 40% markdown
   - Threshold 0.5-0.7 → Standard 30% markdown
   - Threshold > 0.7 → Conservative 20% markdown

### Quality Requirements

7. ✅ Each agent logs its decision-making rationale
8. ✅ Agent outputs include "reasoning" field explaining adaptations
9. ✅ Unit tests for each parameter-driven behavior
10. ✅ Integration test with 3 scenarios:
    - Scenario 1: Zara (no replenishment, 0% holdback)
    - Scenario 2: Traditional (weekly replenishment, 45% holdback)
    - Scenario 3: Luxury (bi-weekly replenishment, 30% holdback)

---

## Prerequisites

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] PHASE5-002 (Agent Handoff Framework) complete
- [x] `SeasonParameters` schema exists
- [x] Mock agents exist in `app/orchestrator/mock_agents.py`

**Why This Matters:**
Mock agents that adapt to parameters prove the architecture works. When we build real agents in Phase 6, they'll use the same parameter-aware pattern. This story establishes that pattern clearly.

---

## Tasks

### Task 1: Enhance Mock Demand Agent

**Goal:** Add parameter-aware logic to demand forecasting

**Subtasks:**
- [x] Update `mock_demand_agent()` in `app/orchestrator/mock_agents.py`
- [x] Add safety stock adaptation logic (already exists, verify it)
- [x] Add forecast horizon adaptation:
  ```python
  # Baseline 12-week curve
  baseline_curve = [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480]

  # Adapt to user's horizon
  if context.forecast_horizon_weeks < 12:
      weekly_curve = baseline_curve[:context.forecast_horizon_weeks]
  elif context.forecast_horizon_weeks > 12:
      # Extend with average
      avg = sum(baseline_curve) // len(baseline_curve)
      weekly_curve = baseline_curve + [avg] * (context.forecast_horizon_weeks - 12)
  else:
      weekly_curve = baseline_curve
  ```
- [x] Add "reasoning" field to output explaining decisions
- [x] Add logging: `logger.info(f"Demand Agent: Using {safety_stock}% safety stock for {replenishment_strategy} strategy")`

**Acceptance:**
- Agent output varies based on input parameters
- Reasoning explains why decisions were made

---

### Task 2: Enhance Mock Inventory Agent

**Goal:** Add parameter-aware manufacturing and holdback logic

**Subtasks:**
- [x] Update `mock_inventory_agent()` in `app/orchestrator/mock_agents.py`
- [x] Add DC holdback calculation:
  ```python
  dc_holdback_pct = context.dc_holdback_percentage  # From workflow
  dc_holdback_units = int(total_forecast * dc_holdback_pct)
  store_allocation_units = total_forecast - dc_holdback_units
  ```
- [x] Add replenishment-aware order splitting:
  ```python
  if context.replenishment_strategy == "none":
      # Single order at week 1
      orders = [{"week": 1, "quantity": total_units, "type": "Single Allocation"}]
  elif context.replenishment_strategy == "weekly":
      # 3 orders across season
      orders = [
          {"week": 1, "quantity": int(total_units * 0.40), "type": "Initial"},
          {"week": 5, "quantity": int(total_units * 0.35), "type": "Replenishment 1"},
          {"week": 9, "quantity": int(total_units * 0.25), "type": "Replenishment 2"}
      ]
  else:  # bi-weekly
      orders = [
          {"week": 1, "quantity": int(total_units * 0.55), "type": "Initial"},
          {"week": 7, "quantity": int(total_units * 0.45), "type": "Replenishment"}
      ]
  ```
- [x] Add "reasoning" field explaining order strategy

**Acceptance:**
- Order count and timing varies by replenishment strategy
- DC holdback calculated correctly from parameters

---

### Task 3: Enhance Mock Pricing Agent

**Goal:** Add parameter-aware markdown logic

**Subtasks:**
- [x] Update `mock_pricing_agent()` in `app/orchestrator/mock_agents.py`
- [x] Add markdown checkpoint logic:
  ```python
  if context.markdown_checkpoint_week is None:
      # No markdown planned
      strategy = "Full price sellthrough"
      markdown_pct = 0
  else:
      # Markdown at specified week
      checkpoint = context.markdown_checkpoint_week

      # Adapt markdown % based on threshold
      if context.markdown_threshold < 0.5:
          markdown_pct = 0.40  # Aggressive
      elif context.markdown_threshold < 0.7:
          markdown_pct = 0.30  # Standard
      else:
          markdown_pct = 0.20  # Conservative

      strategy = f"{markdown_pct*100}% markdown at week {checkpoint} if below {context.markdown_threshold*100}% sellthrough"
  ```
- [x] Add "reasoning" field explaining markdown decision

**Acceptance:**
- Markdown timing and percentage adapt to parameters
- Handles null markdown_checkpoint_week gracefully

---

### Task 4: Add Unit Tests

**Goal:** Test each parameter-driven behavior

**File:** `backend/tests/test_enhanced_mock_agents.py`

**Subtasks:**
- [x] Test Demand Agent safety stock adaptation (3 scenarios)
- [x] Test Demand Agent forecast horizon adaptation (8 weeks, 12 weeks, 16 weeks)
- [x] Test Inventory Agent DC holdback calculation
- [x] Test Inventory Agent order splitting (3 replenishment strategies)
- [x] Test Pricing Agent markdown adaptation (null checkpoint, low threshold, high threshold)

**Example Test:**
```python
@pytest.mark.asyncio
async def test_demand_agent_safety_stock_adaptation():
    # Scenario 1: No replenishment
    params_no_replen = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="none",
        dc_holdback_percentage=0.0
    )

    result = await mock_demand_agent(params_no_replen)
    assert result["safety_stock_multiplier"] == 1.25  # 25% for no replenishment

    # Scenario 2: Weekly replenishment
    params_weekly = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date=date(2025, 3, 1),
        season_end_date=date(2025, 5, 23),
        replenishment_strategy="weekly",
        dc_holdback_percentage=0.45
    )

    result = await mock_demand_agent(params_weekly)
    assert result["safety_stock_multiplier"] == 1.20  # 20% for weekly
```

---

### Task 5: Integration Test with 3 Scenarios

**Goal:** Validate end-to-end workflow with different parameter sets

**File:** `backend/tests/integration/test_parameter_scenarios.py`

**Subtasks:**
- [x] Scenario 1: Zara-style workflow
  ```python
  # 12 weeks, no replenishment, 0% holdback, week 6 markdown
  params = {
      "forecast_horizon_weeks": 12,
      "replenishment_strategy": "none",
      "dc_holdback_percentage": 0.0,
      "markdown_checkpoint_week": 6
  }

  # Verify:
  # - Demand: 25% safety stock
  # - Inventory: Single order at week 1, 0 DC units
  # - Pricing: Markdown at week 6
  ```

- [x] Scenario 2: Traditional retail workflow
  ```python
  # 12 weeks, weekly replenishment, 45% holdback, week 8 markdown
  params = {
      "forecast_horizon_weeks": 12,
      "replenishment_strategy": "weekly",
      "dc_holdback_percentage": 0.45,
      "markdown_checkpoint_week": 8
  }

  # Verify:
  # - Demand: 20% safety stock
  # - Inventory: 3 orders, 45% held at DC
  # - Pricing: Markdown at week 8
  ```

- [x] Scenario 3: Luxury retail workflow
  ```python
  # 16 weeks, bi-weekly replenishment, 30% holdback, no markdown
  params = {
      "forecast_horizon_weeks": 16,
      "replenishment_strategy": "bi-weekly",
      "dc_holdback_percentage": 0.30,
      "markdown_checkpoint_week": None  # No markdown
  }

  # Verify:
  # - Demand: 22% safety stock, 16-week curve
  # - Inventory: 2 orders, 30% held at DC
  # - Pricing: No markdown strategy
  ```

---

## Definition of Done

- [x] Mock agents adapt behavior based on all relevant parameters
- [x] Agent outputs include "reasoning" field explaining decisions
- [x] 10+ unit tests pass (3 agents × 3+ scenarios each) - **14 unit tests passing**
- [x] 3 integration tests pass (Zara, Traditional, Luxury scenarios) - **4 integration tests passing**
- [x] Logging shows agent decision-making rationale
- [x] Code reviewed for clarity and documentation
- [ ] Changes committed to phase5-orchestrator-v2 branch

---

## Notes

**Why This Instead of Historical Data Context?**

The original PHASE5-004 focused on loading historical sales data from the database and assembling complex context packages. That infrastructure is needed for **real agents** (Phase 6) that perform actual Prophet/ARIMA forecasting.

For **mock agents** (Phase 5), we don't need historical data because:
- Mock agents return hard-coded forecasts (e.g., always 8000 units)
- They don't run ML models
- Adding database queries would be building infrastructure we won't use yet

**Instead**, this story enhances mock agents to showcase the **parameter-driven architecture**:
- Agents adapt to user input (Zara vs. traditional retail)
- Same agent code, different outputs based on parameters
- Proves the orchestration framework works as designed

**Phase 6 will add:**
- Real Demand Agent with Prophet/ARIMA
- Historical data loading from database (Phase 4.5 uploads)
- Complex context assembly
- Actual forecasting logic

This story sets the pattern that Phase 6 real agents will follow.
