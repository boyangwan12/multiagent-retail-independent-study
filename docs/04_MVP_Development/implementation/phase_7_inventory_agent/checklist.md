# Phase 7 Implementation Checklist: Inventory Agent

**Epic:** Phase 7 - Inventory Agent
**Status:** Not Started
**Last Updated:** 2025-11-11

---

## Pre-Implementation Setup

### Dependencies Verified
- [ ] Phase 6 (Demand Agent) complete and merged to master
- [ ] Phase 5 orchestrator infrastructure operational
- [ ] Store attributes CSV available (50 stores × 7 features)
- [ ] Historical sales data available
- [ ] Season parameters schema defined

### Python Libraries
- [ ] scikit-learn installed (`uv add scikit-learn`)
- [ ] pandas installed (already available from Phase 6)
- [ ] numpy installed (already available from Phase 6)
- [ ] Test imports:
  ```bash
  python -c "from sklearn.cluster import KMeans; from sklearn.preprocessing import StandardScaler; print('OK')"
  ```

### Documentation Review
- [ ] Read PRD v3.3 Section 5 (Inventory Agent requirements)
- [ ] Read Technical Architecture v3.3 Section 6 (Inventory Agent)
- [ ] Review Phase 6 DemandAgentOutput contract
- [ ] Review technical_decisions.md for Phase 7

---

## Story 1: K-means Store Clustering (PHASE7-001)

### Implementation Tasks
- [ ] Create file: `backend/app/ml/store_clustering.py`
- [ ] Implement `StoreClusterer` class skeleton
- [ ] Add `__init__(self, n_clusters=3, random_state=42)` method
- [ ] Implement `fit(self, store_features: pd.DataFrame) -> None` method
  - [ ] Load 7 features from DataFrame
  - [ ] Apply StandardScaler normalization
  - [ ] Run K-means++ clustering
  - [ ] Calculate silhouette score
  - [ ] Store cluster assignments
- [ ] Implement `predict_cluster(self, store_features: pd.DataFrame) -> np.ndarray` method
- [ ] Implement `get_cluster_labels(self) -> Dict[int, str]` method
  - [ ] Sort clusters by avg_weekly_sales
  - [ ] Assign labels: Fashion_Forward, Mainstream, Value_Conscious
- [ ] Implement `get_cluster_stats(self) -> pd.DataFrame` method
  - [ ] Calculate cluster means for all features
  - [ ] Calculate cluster sizes (store counts)
  - [ ] Calculate cluster allocation percentages
- [ ] Add type hints and docstrings

### Testing Tasks
- [ ] Create file: `backend/tests/unit/ml/test_store_clustering.py`
- [ ] Test 1: `test_clustering_produces_3_clusters()`
- [ ] Test 2: `test_standardscaler_normalization()`
- [ ] Test 3: `test_cluster_labels_assigned_correctly()`
- [ ] Test 4: `test_silhouette_score_above_threshold()` (>0.4)
- [ ] Test 5: `test_cluster_percentages_sum_to_100()`
- [ ] All tests passing
- [ ] Test coverage >90% for StoreClusterer

### Quality Checks
- [ ] Type hints on all methods
- [ ] Docstrings complete (Google style)
- [ ] Logging statements added
- [ ] No print statements
- [ ] Error handling for invalid inputs

### Story Complete
- [ ] All acceptance criteria met
- [ ] Code reviewed (self-review or peer review)
- [ ] Ready for Story 2

---

## Story 2: Inventory Allocation Logic (PHASE7-002)

### Implementation Tasks
- [ ] Create file: `backend/app/agents/inventory_agent.py` (if not exists)
- [ ] Define `InventoryAgent` class
- [ ] Add `__init__(self, config: AgentConfig = None)` method
- [ ] Implement `calculate_manufacturing(self, total_demand: int, safety_stock_pct: float) -> int` method
  - [ ] Formula: `manufacturing = total_demand × (1 + safety_stock_pct)`
  - [ ] Return integer result
- [ ] Implement `allocate_initial(self, manufacturing_qty: int, parameters: SeasonParameters, clusters: List[Cluster]) -> Dict` method
  - [ ] Calculate DC holdback (parameter-driven: 0% or 45%)
  - [ ] Calculate initial allocation to stores
  - [ ] Allocate to clusters based on K-means percentages
  - [ ] Allocate within clusters using hybrid factors (70/30)
  - [ ] Enforce 2-week minimum per store
  - [ ] Validate unit conservation
- [ ] Implement `calculate_allocation_factor(self, store: Store, cluster_avg: Dict) -> float` method
  - [ ] Calculate historical score
  - [ ] Calculate attribute score
  - [ ] Return weighted average (70% hist + 30% attr)
- [ ] Implement `validate_unit_conservation(self, expected: int, actual: int) -> None` method
- [ ] Add type hints and docstrings

### Testing Tasks
- [ ] Create file: `backend/tests/unit/agents/test_inventory_agent.py`
- [ ] Test 1: `test_manufacturing_calculation()`
- [ ] Test 2: `test_dc_holdback_0_percent()` (Zara scenario)
- [ ] Test 3: `test_dc_holdback_45_percent()` (Standard retail)
- [ ] Test 4: `test_cluster_allocation_sums_correct()`
- [ ] Test 5: `test_store_allocation_sums_correct()`
- [ ] Test 6: `test_2_week_minimum_enforced()`
- [ ] Test 7: `test_unit_conservation_validation()`
- [ ] All tests passing
- [ ] Test coverage >80%

### Quality Checks
- [ ] Type hints on all methods
- [ ] Docstrings complete
- [ ] Logging statements added
- [ ] Unit conservation validated at each step
- [ ] Error handling for edge cases

### Story Complete
- [ ] All acceptance criteria met
- [ ] Code reviewed
- [ ] Ready for Story 3

---

## Story 3: Replenishment Scheduling (PHASE7-003)

### Implementation Tasks
- [ ] Extend `InventoryAgent` class with replenishment methods
- [ ] Implement `calculate_replenishment(self, store_id: str, current_week: int, forecast_by_week: List[int], current_inventory: int) -> int` method
  - [ ] Formula: `replenish = forecast[week+1] - current_inventory`
  - [ ] Return max(0, replenish)
- [ ] Implement `generate_replenishment_queue(self, current_week: int, parameters: SeasonParameters, stores: List[Store], dc_inventory: int) -> List[Dict]` method
  - [ ] Check if replenishment enabled (`parameters.replenishment_strategy != "none"`)
  - [ ] Calculate replenishment for each store
  - [ ] Check DC availability
  - [ ] Flag insufficient DC inventory warnings
  - [ ] Return replenishment queue
- [ ] Implement conditional logic (skip if strategy = "none")
- [ ] Add type hints and docstrings

### Testing Tasks
- [ ] Extend: `backend/tests/unit/agents/test_inventory_agent.py`
- [ ] Test 1: `test_replenishment_calculation_basic()`
- [ ] Test 2: `test_replenishment_skipped_when_strategy_none()` (Zara)
- [ ] Test 3: `test_replenishment_enabled_when_strategy_weekly()`
- [ ] Test 4: `test_dc_availability_checked()`
- [ ] Test 5: `test_insufficient_dc_inventory_warning()`
- [ ] All tests passing
- [ ] Test coverage >80%

### Quality Checks
- [ ] Conditional logic correct (parameter-driven)
- [ ] DC availability checks implemented
- [ ] Warning flags set correctly
- [ ] Logging informative

### Story Complete
- [ ] All acceptance criteria met
- [ ] Code reviewed
- [ ] Ready for Story 4

---

## Story 4: Integration Testing (PHASE7-004)

### Implementation Tasks
- [ ] Create file: `backend/tests/integration/test_inventory_agent_integration.py`
- [ ] Implement `test_end_to_end_phase6_to_phase7()` test
  - [ ] Run Phase 6 Demand Agent
  - [ ] Pass output to Phase 7 Inventory Agent
  - [ ] Validate output matches InventoryAgentOutput schema
  - [ ] Assert manufacturing_qty correct
  - [ ] Assert allocation sums correct
- [ ] Implement `test_parameter_driven_0_percent_holdback()` test (Zara)
  - [ ] Set parameters: dc_holdback=0.0, replenishment="none"
  - [ ] Run Inventory Agent
  - [ ] Assert 100% allocated to stores
  - [ ] Assert replenishment phase skipped
- [ ] Implement `test_parameter_driven_45_percent_holdback()` test (Standard)
  - [ ] Set parameters: dc_holdback=0.45, replenishment="weekly"
  - [ ] Run Inventory Agent
  - [ ] Assert 55/45 split
  - [ ] Assert replenishment enabled
- [ ] Implement `test_performance_under_15_seconds()` test
  - [ ] Run full workflow (Phase 6 + Phase 7)
  - [ ] Assert runtime <15 seconds

### Testing Tasks
- [ ] All 3+ integration tests passing
- [ ] End-to-end workflow validated
- [ ] Parameter adaptation verified
- [ ] Performance target met (<15 seconds)

### Quality Checks
- [ ] Output contract validation (Pydantic)
- [ ] Unit conservation verified
- [ ] Parameter-driven behavior tested
- [ ] Performance benchmarked

### Story Complete
- [ ] All acceptance criteria met
- [ ] Code reviewed
- [ ] Phase 7 complete

---

## Phase 7 Definition of Done

### Code Complete
- [ ] All 4 stories implemented
- [ ] InventoryAgent class created
- [ ] StoreClusterer class created
- [ ] K-means clustering implemented
- [ ] Allocation logic implemented (3-layer hierarchy)
- [ ] Replenishment logic implemented
- [ ] Agent registered with AgentHandoffManager

### Testing Complete
- [ ] 17+ unit tests passing
- [ ] 3+ integration tests passing
- [ ] End-to-end workflow test passing
- [ ] Test coverage >80%
- [ ] Performance <15 seconds validated

### Quality Checks
- [ ] Type hints on all methods
- [ ] Docstrings complete (Google style)
- [ ] Error handling integrated with Phase 5
- [ ] Logging informative
- [ ] No print statements
- [ ] Unit conservation validated

### Documentation Complete
- [ ] All technical decisions documented
- [ ] Clustering algorithm explained
- [ ] Allocation hierarchy detailed
- [ ] Replenishment logic documented
- [ ] Ready for Phase 8 handoff

### Integration Ready
- [ ] InventoryAgentOutput schema defined and validated
- [ ] Phase 6 integration working
- [ ] Phase 5 orchestrator integration working
- [ ] WebSocket messages sent correctly
- [ ] Ready for Phase 8 (Pricing Agent) to consume output

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Stories Complete** | 4/4 | 0/4 | ⏳ |
| **Unit Tests Passing** | 17+ | 0 | ⏳ |
| **Integration Tests Passing** | 3+ | 0 | ⏳ |
| **Test Coverage** | >80% | 0% | ⏳ |
| **Performance (Phase 6+7)** | <15s | - | ⏳ |
| **Silhouette Score** | >0.4 | - | ⏳ |
| **Unit Conservation Errors** | 0 | - | ⏳ |

---

## Notes

- **Phase 6 Dependency:** Cannot start Phase 7 until Phase 6 is merged and tested
- **Parameter Testing:** Must test both 0% and 45% holdback scenarios
- **Unit Conservation:** Critical - validate at every step
- **Clustering Quality:** If silhouette <0.4, flag for manual review
- **Performance:** Profile if >15 seconds, optimize clustering or pandas operations

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
