# Story: Implement Replenishment Scheduling

**Epic:** Phase 7 - Inventory Agent
**Story ID:** PHASE7-003
**Status:** ✅ Complete
**Estimate:** 8 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE7-002 complete

**Planning References:**
- PRD v3.3: Section 5.4 (Weekly Replenishment)
- Technical Architecture v3.3: Section 6 (Inventory Agent - Replenishment)
- technical_decisions.md: TD-7.8 (Simple Replenishment Formula)

---

## Story

As a backend developer,
I want to implement weekly replenishment scheduling based on forecast and current inventory,
So that stores receive timely restocks from DC reserves while supporting parameter-driven replenishment strategies.

**Business Value:** Weekly replenishment ensures stores maintain adequate inventory throughout the season without over-allocating at Week 0. Parameter-driven conditional execution supports both fast fashion (no replenishment) and standard retail (weekly replenishment) strategies.

**Epic Context:** This is Story 3 of 4 in Phase 7. This story builds on Story 2 (Allocation Logic) to add weekly replenishment planning. Story 4 will validate end-to-end integration.

---

## Acceptance Criteria

### Functional Requirements

1. ☐ Replenishment calculation: `replenish_qty = forecast_next_week - current_inventory`
2. ☐ Conditional execution based on `parameters.replenishment_strategy`:
   - "none" → Skip replenishment phase entirely
   - "weekly" → Calculate and apply weekly replenishment
3. ☐ DC availability checking before allocation
4. ☐ Insufficient DC inventory warnings generated
5. ☐ Replenishment queue generated (stores needing restock)
6. ☐ Integration with weekly workflow

### Quality Requirements

7. ☐ Replenishment calculation completes in <2 seconds (50 stores)
8. ☐ All docstrings complete (Google style)
9. ☐ 5 unit tests written and passing
10. ☐ Type hints on all methods
11. ☐ Logging informative (replenishment decisions, DC status)

---

## Prerequisites

**Story 2 Complete:**
- [x] PHASE7-002 (Allocation Logic) complete
- [x] InventoryAgent class with allocation methods

**Data Available:**
- [x] Current store inventory levels
- [x] Weekly forecast data
- [x] DC reserve levels

---

## Tasks

### Task 1: Implement calculate_replenishment() Method

**Goal:** Calculate weekly replenishment needs per store

**Subtasks:**
- [ ] Extend `InventoryAgent` class
- [ ] Add `calculate_replenishment(self, store_id: str, current_week: int, forecast_by_week: List[int], current_inventory: int) -> int` method
- [ ] Implement simple formula:
  ```python
  next_week_forecast = forecast_by_week[current_week + 1]
  replenish_qty = max(0, next_week_forecast - current_inventory)
  return replenish_qty
  ```
- [ ] Log replenishment calculation:
  ```python
  if replenish_qty > 0:
      logger.info(f"Store {store_id}: Replenish {replenish_qty} (forecast: {next_week_forecast}, inventory: {current_inventory})")
  ```

**Acceptance:**
- Replenishment calculated correctly
- Returns 0 if current inventory sufficient
- Handles edge cases (zero inventory, over-stocked)

---

### Task 2: Implement generate_replenishment_queue() Method

**Goal:** Generate queue of stores needing replenishment

**Subtasks:**
- [ ] Add `generate_replenishment_queue(self, current_week: int, parameters: SeasonParameters, stores: List[Store], dc_inventory: int) -> List[Dict]` method
- [ ] Check if replenishment enabled:
  ```python
  if parameters.replenishment_strategy == "none":
      logger.info("Replenishment disabled (strategy='none') - Phase skipped")
      return []
  ```
- [ ] Calculate replenishment for each store:
  ```python
  replenishment_queue = []
  total_needed = 0

  for store in stores:
      replenish_qty = self.calculate_replenishment(
          store_id=store.store_id,
          current_week=current_week,
          forecast_by_week=forecast_by_week,
          current_inventory=store.current_inventory
      )

      if replenish_qty > 0:
          total_needed += replenish_qty
          replenishment_queue.append({
              "store_id": store.store_id,
              "current_inventory": store.current_inventory,
              "forecast_next_week": forecast_by_week[current_week + 1],
              "replenish_needed": replenish_qty,
              "dc_available": "pending"  # Will update after DC check
          })
  ```
- [ ] Check DC availability:
  ```python
  if total_needed > dc_inventory:
      logger.warning(
          f"Insufficient DC inventory: needed {total_needed}, available {dc_inventory} "
          f"(shortfall: {total_needed - dc_inventory})"
      )
      # Flag stores with insufficient inventory
      remaining_dc = dc_inventory
      for item in replenishment_queue:
          if remaining_dc >= item['replenish_needed']:
              item['dc_available'] = "yes"
              remaining_dc -= item['replenish_needed']
          else:
              item['dc_available'] = f"partial ({remaining_dc})"
              remaining_dc = 0
  else:
      logger.info(f"DC inventory sufficient: {dc_inventory} available, {total_needed} needed")
      for item in replenishment_queue:
          item['dc_available'] = "yes"
  ```
- [ ] Return replenishment queue

**Acceptance:**
- Queue generated correctly
- DC availability checked
- Warnings for insufficient inventory
- Empty queue returned when strategy = "none"

---

### Task 3: Implement Conditional Logic for Parameter-Driven Execution

**Goal:** Skip replenishment phase when strategy = "none"

**Subtasks:**
- [ ] Update `execute()` method to check strategy:
  ```python
  # After initial allocation...

  if parameters.replenishment_strategy == "none":
      logger.info("Replenishment strategy='none' - All inventory allocated at Week 0, no replenishment phase")
      return {
          **allocation_result,
          "replenishment_enabled": False,
          "replenishment_queue": []
      }
  else:
      logger.info(f"Replenishment strategy='{parameters.replenishment_strategy}' - Weekly replenishment enabled")
      return {
          **allocation_result,
          "replenishment_enabled": True,
          "replenishment_queue": []  # Will be populated weekly
      }
  ```

**Acceptance:**
- Conditional logic works correctly
- Zara scenario (strategy="none") skips replenishment
- Standard retail (strategy="weekly") enables replenishment
- Logging clear

---

### Task 4: Write Unit Tests

**Goal:** Verify replenishment logic

**Subtasks:**
- [ ] Extend: `backend/tests/unit/agents/test_inventory_agent.py`
- [ ] **Test 1:** `test_replenishment_calculation_basic()`
  - Forecast: 100, Inventory: 60 → Replenish: 40
  - Forecast: 100, Inventory: 120 → Replenish: 0
- [ ] **Test 2:** `test_replenishment_skipped_when_strategy_none()` (Zara)
  - Parameters: replenishment_strategy="none"
  - Assert: replenishment_queue = []
  - Assert: replenishment_enabled = False
- [ ] **Test 3:** `test_replenishment_enabled_when_strategy_weekly()`
  - Parameters: replenishment_strategy="weekly"
  - Assert: replenishment_enabled = True
  - Assert: replenishment_queue generated
- [ ] **Test 4:** `test_dc_availability_checked()`
  - Total needed: 500, DC inventory: 600 → All available
  - Total needed: 500, DC inventory: 300 → Partial availability
- [ ] **Test 5:** `test_insufficient_dc_inventory_warning()`
  - Total needed > DC inventory
  - Assert: Warning logged
  - Assert: Stores flagged with "partial" availability

**Acceptance:**
- All 5 tests pass
- Test coverage >80%

---

## Testing Strategy

### Unit Tests (This Story)
- Test replenishment calculation
- Test conditional execution (strategy="none" vs "weekly")
- Test DC availability checking
- Test insufficient inventory warnings

### Integration Tests (Story 4)
- Integration with weekly workflow
- Integration with Phase 5 orchestrator

### Performance Tests
- Replenishment calculation: <2 seconds (50 stores)

---

## Definition of Done

**Code Complete:**
- [ ] calculate_replenishment() method working
- [ ] generate_replenishment_queue() method working
- [ ] Conditional logic implemented (parameter-driven)
- [ ] DC availability checking implemented
- [ ] Type hints and docstrings complete

**Testing Complete:**
- [ ] 5 unit tests passing
- [ ] Test coverage >80%

**Quality Checks:**
- [ ] Conditional logic correct
- [ ] DC availability checks working
- [ ] Warning flags set correctly
- [ ] Logging informative

**Documentation:**
- [ ] Docstrings complete
- [ ] Replenishment logic explained
- [ ] Ready for Story 4 (Integration Testing)

---

## Notes

**Simple Replenishment Formula:**
- `replenish = forecast_next_week - current_inventory`
- No safety buffer (rely on re-forecast for adjustments)
- Straightforward, transparent calculation

**Parameter-Driven Execution:**
- **Zara (Fast Fashion):**
  - `replenishment_strategy="none"` → Skip replenishment phase
  - All inventory shipped at Week 0, no DC reserve
- **Standard Retail:**
  - `replenishment_strategy="weekly"` → Weekly replenishment from DC reserve
  - 45% DC holdback provides flexibility

**DC Availability Scenarios:**
- **Sufficient:** All stores receive full replenishment
- **Partial:** First N stores receive full, remaining stores flagged for manual handling
- **Insufficient:** Warning logged, requires emergency order or store transfers

**Common Issues:**
- **Zero Current Inventory:** Replenishment = forecast_next_week (full restock)
- **Over-Stocked:** Replenishment = 0 (no action needed)
- **Negative Inventory:** Should not occur (data integrity issue) → Log error

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
