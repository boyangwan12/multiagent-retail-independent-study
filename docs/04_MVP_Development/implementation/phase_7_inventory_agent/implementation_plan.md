# Phase 7 Implementation Plan: Inventory Agent

**Epic:** Phase 7 - Inventory Agent
**Status:** Ready for Implementation
**Estimated Duration:** 32 hours
**Dependencies:** Phase 6 (Demand Agent) complete
**Target Completion:** TBD

---

## Overview

Phase 7 implements the **Inventory Agent**, responsible for intelligent inventory allocation and replenishment planning. This agent consumes the demand forecast from Phase 6 (Demand Agent) and produces:

1. **K-means Store Clustering** (3 clusters using 7 features)
2. **Manufacturing Order Calculation** (demand × safety stock)
3. **Initial Allocation** (hierarchical: cluster → store, with DC holdback)
4. **Weekly Replenishment Planning** (simple forecast-based logic)

**Business Value:** The Inventory Agent transforms category-level forecasts into actionable store-level allocation plans, optimizing inventory distribution across the retail network while maintaining DC reserves for flexibility.

---

## Epic Context

Phase 7 follows Phase 6 (Demand Agent) and precedes Phase 8 (Pricing Agent):
- **Phase 6 Output:** Demand forecast with total_demand, forecast_by_week, confidence
- **Phase 7 Input:** Consumes Phase 6 forecast + store attributes + season parameters
- **Phase 7 Output:** Manufacturing order, cluster allocations, store allocations, replenishment plan
- **Phase 8 Input:** Will consume Phase 7 allocation plan for markdown analysis

---

## Success Criteria

### Functional Success
1. ✅ K-means clustering produces 3 distinct clusters (silhouette score >0.4)
2. ✅ Manufacturing calculation includes configurable safety stock
3. ✅ Initial allocation respects DC holdback percentage (parameter-driven: 0% or 45%)
4. ✅ Store allocations sum to initial allocation total (no unit loss/gain)
5. ✅ Replenishment logic calculates weekly needs based on forecast
6. ✅ All outputs match InventoryAgentOutput contract

### Quality Success
1. ✅ All 4 stories completed with DoD met
2. ✅ Unit test coverage >80%
3. ✅ Integration tests passing (with Phase 6 output)
4. ✅ End-to-end workflow completes in <15 seconds
5. ✅ Zero allocation errors (unit conservation validated)

### Documentation Success
1. ✅ All technical decisions documented
2. ✅ Clustering logic explained (feature selection, normalization)
3. ✅ Allocation algorithm detailed (3-layer hierarchy)
4. ✅ Ready for Phase 8 handoff

---

## Story Breakdown

| Story ID | Title | Est. Hours | Priority | Dependencies |
|----------|-------|------------|----------|--------------|
| **PHASE7-001** | K-means Store Clustering | 8 hours | P0 | Phase 6 complete |
| **PHASE7-002** | Inventory Allocation Logic | 10 hours | P0 | PHASE7-001 |
| **PHASE7-003** | Replenishment Scheduling | 8 hours | P0 | PHASE7-002 |
| **PHASE7-004** | Integration Testing | 6 hours | P0 | PHASE7-001, 002, 003 |

**Total Estimate:** 32 hours

---

## Story Summaries

### PHASE7-001: K-means Store Clustering (8 hours)

**Goal:** Implement K-means clustering (K=3) to segment 50 stores into 3 performance tiers.

**Key Tasks:**
- Load store attributes (7 features: avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region)
- Implement StandardScaler normalization (mean=0, std=1)
- Run K-means++ clustering (K=3, scikit-learn)
- Label clusters (Fashion_Forward, Mainstream, Value_Conscious)
- Calculate cluster allocation percentages based on historical sales
- Validate silhouette score >0.4

**Acceptance Criteria:**
- 3 clusters produced with clear separation
- Cluster labels assigned based on characteristics
- Allocation percentages sum to 100%
- 5 unit tests passing

---

### PHASE7-002: Inventory Allocation Logic (10 hours)

**Goal:** Implement hierarchical allocation logic (category → cluster → store) with DC holdback.

**Key Tasks:**
- Calculate manufacturing order: `total_demand × (1 + safety_stock_pct)`
- Implement parameter-driven DC holdback (0% for Zara, 45% for standard retail)
- Allocate to clusters based on K-means percentages
- Allocate within clusters using hybrid factors (70% historical + 30% attributes)
- Enforce 2-week minimum per store
- Validate unit conservation (no loss/gain)

**Acceptance Criteria:**
- Manufacturing calculation correct
- DC holdback adapts to parameters (0% or 45%)
- Store allocations sum to initial allocation
- 2-week minimum enforced
- 7 unit tests passing

---

### PHASE7-003: Replenishment Scheduling (8 hours)

**Goal:** Implement weekly replenishment logic based on forecast and current inventory.

**Key Tasks:**
- Calculate weekly replenishment needs: `forecast_next_week - current_inventory`
- Conditional execution (skip if replenishment strategy = "none")
- Check DC inventory availability
- Generate replenishment queue (stores needing restock)
- Flag insufficient DC inventory warnings
- Integrate with weekly workflow

**Acceptance Criteria:**
- Replenishment calculated for each store weekly
- Skips replenishment when strategy = "none"
- DC availability checked
- Warnings for insufficient stock
- 5 unit tests passing

---

### PHASE7-004: Integration Testing (6 hours)

**Goal:** Verify Inventory Agent integrates correctly with Phase 6 Demand Agent and Phase 5 orchestrator.

**Key Tasks:**
- End-to-end test: Phase 6 forecast → Phase 7 allocation
- Test parameter-driven behavior (0% vs 45% holdback)
- Test replenishment conditional logic (strategy = "none" vs "weekly")
- Validate output contract (InventoryAgentOutput schema)
- Performance test (<15 seconds total)

**Acceptance Criteria:**
- 3 integration tests passing
- End-to-end workflow validated
- Parameter adaptation verified
- Performance target met

---

## Dependencies

### Phase 6 Complete (Blocker)
- ✅ Demand Agent operational
- ✅ DemandAgentOutput contract defined
- ✅ forecast_result available with:
  - total_demand
  - forecast_by_week
  - safety_stock_pct
  - confidence
  - model_used

### Phase 5 Infrastructure
- ✅ AgentHandoffManager operational
- ✅ InventoryAgentContext schema defined
- ✅ ContextAssembler can build context
- ✅ WebSocket streaming functional

### Data Requirements
- ✅ Store attributes CSV available (50 stores × 7 features)
- ✅ Historical sales data available (for clustering validation)
- ✅ Season parameters defined (via Phase 0 extraction)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **K-means clustering poor quality** | Medium | High | Validate silhouette score >0.4, manual cluster review, adjust K if needed |
| **Allocation unit conservation errors** | Low | High | Rigorous unit tests, validation at each step, assert sum == expected |
| **DC holdback logic bugs** | Medium | Medium | Comprehensive tests for 0% and 45% scenarios, parameter-driven validation |
| **Replenishment logic errors** | Low | Medium | Test with various inventory levels, edge cases (zero inventory, over-stocked) |
| **Performance degradation (>15s)** | Low | Medium | Profile clustering algorithm, optimize pandas operations, cache store data |

---

## Definition of Done (Epic Level)

### Code Complete
- [ ] All 4 stories implemented
- [ ] InventoryAgent class created (`backend/app/agents/inventory_agent.py`)
- [ ] K-means clustering implemented
- [ ] Allocation logic implemented (3-layer hierarchy)
- [ ] Replenishment logic implemented
- [ ] Agent registered with AgentHandoffManager

### Testing Complete
- [ ] 17+ unit tests passing (across all stories)
- [ ] 3 integration tests passing
- [ ] End-to-end workflow test passing
- [ ] Test coverage >80%
- [ ] Performance <15 seconds validated

### Quality Checks
- [ ] Type hints on all methods
- [ ] Docstrings complete (Google style)
- [ ] Error handling integrated with Phase 5
- [ ] Logging informative
- [ ] No print statements

### Documentation Complete
- [ ] All technical decisions documented
- [ ] Clustering algorithm explained
- [ ] Allocation hierarchy detailed
- [ ] Replenishment logic documented
- [ ] Ready for Phase 8 handoff

---

## Handoff to Phase 8

After Phase 7 completes, Phase 8 (Pricing Agent) can begin. Phase 8 will:
- Consume inventory_plan from Inventory Agent
- Use store allocations for sell-through tracking
- Apply markdowns based on gap × elasticity formula
- No changes to Phase 7 code required

**Contract Verification:**
Before starting Phase 8, run:
```python
# Verify output matches contract
output = inventory_agent.execute(context)
validated = InventoryAgentOutput(**output)  # Should not raise ValidationError
```

---

## Notes

**Clustering Feature Importance:**
- `avg_weekly_sales_12mo`: Most important feature (direct performance indicator)
- `store_size_sqft`: Capacity constraint
- `median_income`: Demand driver
- `location_tier`, `fashion_tier`, `store_format`, `region`: Secondary attributes

**Allocation Hierarchy:**
1. **Category Level:** Total demand forecast (Phase 6)
2. **Cluster Level:** K-means distribution (e.g., 40% Fashion_Forward, 35% Mainstream, 25% Value_Conscious)
3. **Store Level:** Hybrid factors (70% historical + 30% attributes)

**DC Holdback Strategy:**
- **0% holdback (Zara):** 100% allocated to stores at Week 0, no replenishment
- **45% holdback (Standard):** 55% initial to stores, 45% DC reserve for weekly replenishment

**Parameter-Driven Adaptation:**
- Inventory Agent checks `parameters.dc_holdback_percentage` and `parameters.replenishment_strategy`
- Adapts allocation logic without code changes
- Examples:
  - `dc_holdback_percentage=0.0, replenishment_strategy="none"` → 100% initial allocation, skip replenishment phase
  - `dc_holdback_percentage=0.45, replenishment_strategy="weekly"` → 55/45 split, weekly replenishment enabled

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
