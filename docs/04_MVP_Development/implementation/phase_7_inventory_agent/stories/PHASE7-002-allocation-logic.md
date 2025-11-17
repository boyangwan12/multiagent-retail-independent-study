# Story: Implement Inventory Allocation Logic

**Epic:** Phase 7 - Inventory Agent
**Story ID:** PHASE7-002
**Status:** Ready for Implementation
**Estimate:** 10 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE7-001 complete

**Planning References:**
- PRD v3.3: Section 5.3 (Inventory Management - Allocation)
- Technical Architecture v3.3: Section 4.5 (Inventory Agent)
- technical_decisions.md: TD-7.5 (Hybrid Allocation), TD-7.6 (DC Holdback), TD-7.7 (2-Week Minimum), TD-7.9 (Unit Conservation)

---

## Story

As a backend developer,
I want to implement hierarchical inventory allocation logic (category → cluster → store) with parameter-driven DC holdback,
So that the system can intelligently distribute forecasted inventory across stores while maintaining DC reserves for flexibility.

**Business Value:** Hierarchical allocation optimizes inventory distribution by considering both cluster-level patterns (K-means) and store-level characteristics (historical performance + attributes). Parameter-driven DC holdback enables the same code to support multiple retail strategies (fast fashion 0%, standard retail 45%) without code changes.

**Epic Context:** This is Story 2 of 4 in Phase 7. This story builds on Story 1 (K-means clustering) to implement the core allocation algorithm. Story 3 will add replenishment logic. This allocation logic is critical for Phase 8 (Pricing Agent) to track sell-through and trigger markdowns.

---

## Acceptance Criteria

### Functional Requirements

1. ☐ InventoryAgent class created in `backend/app/agents/inventory_agent.py`
2. ☐ Manufacturing calculation: `manufacturing_qty = total_demand × (1 + safety_stock_pct)`
3. ☐ Parameter-driven DC holdback:
   - Zara (0%): 100% allocated to stores at Week 0
   - Standard (45%): 55% initial to stores, 45% DC reserve
4. ☐ Hierarchical allocation implemented:
   - **Layer 1 (Category):** Total demand from Phase 6
   - **Layer 2 (Cluster):** K-means percentages (e.g., 40/35/25)
   - **Layer 3 (Store):** Hybrid factors (70% historical + 30% attributes)
5. ☐ 2-week minimum allocation per store enforced
6. ☐ Unit conservation validated at each layer (no unit loss/gain)
7. ☐ Output matches InventoryAgentOutput contract

### Quality Requirements

8. ☐ Allocation completes in <5 seconds (50 stores)
9. ☐ Unit conservation errors = 0 (strict validation)
10. ☐ All docstrings complete (Google style)
11. ☐ 7 unit tests written and passing
12. ☐ Type hints on all methods
13. ☐ Logging informative (allocation steps, unit conservation checks)

---

## Prerequisites

**Story 1 Complete:**
- [x] PHASE7-001 (K-means clustering) complete
- [x] StoreClusterer available
- [x] Cluster percentages calculated

**Phase 6 Complete:**
- [x] Demand Agent operational
- [x] DemandAgentOutput available with:
  - total_demand
  - forecast_by_week
  - safety_stock_pct

**Data Available:**
- [x] Store attributes with historical sales (for allocation factors)
- [x] Season parameters (dc_holdback_percentage, forecast_horizon_weeks)

---

## Tasks

### Task 1: Create InventoryAgent Class Skeleton

**Goal:** Define class structure and method signatures

**Subtasks:**
- [ ] Create file: `backend/app/agents/inventory_agent.py` (if not exists)
- [ ] Define `InventoryAgent` class
- [ ] Add `__init__(self, config: AgentConfig = None)` method
- [ ] Add `execute(self, context: InventoryAgentContext) -> Dict` method stub
- [ ] Add `calculate_manufacturing(self, total_demand: int, safety_stock_pct: float) -> int` method stub
- [ ] Add `allocate_initial(self, manufacturing_qty: int, parameters: SeasonParameters, clusters: List[Cluster]) -> Dict` method stub
- [ ] Add `calculate_allocation_factor(self, store: Store, cluster_avg: Dict) -> float` method stub
- [ ] Add `validate_unit_conservation(self, expected: int, actual: int, step: str) -> None` method stub
- [ ] Add type hints and docstrings

**Code Template:**
```python
from typing import Any, Dict, List, Optional
from app.agents.config import AgentConfig
from app.ml.store_clustering import StoreClusterer
from app.schemas.workflow_schemas import SeasonParameters, InventoryAgentContext
import pandas as pd
import logging

logger = logging.getLogger("fashion_forecast")

class InventoryAgent:
    """
    Inventory Agent for allocation and replenishment planning.

    Implements hierarchical allocation (category → cluster → store) with
    parameter-driven DC holdback. Integrates with Phase 6 Demand Agent output
    and Phase 5 orchestrator infrastructure.

    Phase 7 Implementation: Core allocation logic with K-means clustering
    Phase 8 Handoff: Provides allocation plan for Pricing Agent
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize Inventory Agent.

        Args:
            config: Agent configuration with OpenAI client (optional for Phase 7)
        """
        self.config = config
        self.client = config.openai_client if config else None
        self.clusterer = StoreClusterer(n_clusters=3, random_state=42)
        logger.info("InventoryAgent initialized with StoreClusterer")

    async def execute(
        self,
        forecast_result: Dict[str, Any],
        parameters: SeasonParameters,
        stores_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Execute inventory allocation workflow.

        Args:
            forecast_result: Demand Agent output (total_demand, forecast_by_week, etc.)
            parameters: Season parameters (dc_holdback_percentage, etc.)
            stores_data: Store attributes DataFrame

        Returns:
            Dictionary with allocation results:
            - manufacturing_qty: int
            - safety_stock_pct: float
            - initial_allocation_total: int
            - dc_holdback_total: int
            - clusters: List[ClusterAllocation]

        Raises:
            ValueError: If unit conservation fails
        """
        pass

    def calculate_manufacturing(
        self,
        total_demand: int,
        safety_stock_pct: float
    ) -> int:
        """Calculate manufacturing order quantity.

        Args:
            total_demand: Total season demand from forecast
            safety_stock_pct: Safety stock percentage (0.1-0.5)

        Returns:
            Manufacturing quantity
        """
        pass

    def allocate_initial(
        self,
        manufacturing_qty: int,
        parameters: SeasonParameters,
        clusters: List[Dict]
    ) -> Dict:
        """Allocate initial inventory to stores.

        Args:
            manufacturing_qty: Total units to manufacture
            parameters: Season parameters
            clusters: K-means cluster results

        Returns:
            Allocation dictionary
        """
        pass

    def calculate_allocation_factor(
        self,
        store: pd.Series,
        cluster_avg: Dict
    ) -> float:
        """Calculate store allocation factor (70% historical + 30% attributes).

        Args:
            store: Store row with features
            cluster_avg: Cluster average features

        Returns:
            Allocation factor (normalized score)
        """
        pass

    def validate_unit_conservation(
        self,
        expected: int,
        actual: int,
        step: str
    ) -> None:
        """Validate unit conservation at allocation step.

        Args:
            expected: Expected total units
            actual: Actual total units
            step: Step name for error message

        Raises:
            ValueError: If units don't match
        """
        pass
```

---

### Task 2: Implement calculate_manufacturing() Method

**Goal:** Calculate manufacturing order quantity with safety stock

**Subtasks:**
- [ ] Validate inputs (total_demand >0, safety_stock_pct in [0.1, 0.5])
- [ ] Calculate manufacturing:
  ```python
  manufacturing_qty = int(total_demand × (1 + safety_stock_pct))
  ```
- [ ] Log calculation:
  ```python
  logger.info(
      f"Manufacturing: {total_demand} × (1 + {safety_stock_pct}) = {manufacturing_qty}"
  )
  ```
- [ ] Return manufacturing quantity

**Acceptance:**
- Manufacturing calculation correct
- Safety stock applied correctly
- Edge cases handled (zero demand, high safety stock)

---

### Task 3: Implement allocate_initial() with Parameter-Driven Holdback

**Goal:** Allocate manufactured inventory with parameter-driven DC holdback

**Subtasks:**
- [ ] Extract DC holdback from parameters:
  ```python
  dc_holdback_pct = parameters.dc_holdback_percentage  # 0.0 or 0.45
  initial_allocation_pct = 1.0 - dc_holdback_pct  # 1.0 or 0.55
  ```
- [ ] Calculate initial and holdback totals:
  ```python
  initial_allocation_total = int(manufacturing_qty × initial_allocation_pct)
  dc_holdback_total = manufacturing_qty - initial_allocation_total
  ```
- [ ] Validate unit conservation:
  ```python
  self.validate_unit_conservation(
      expected=manufacturing_qty,
      actual=initial_allocation_total + dc_holdback_total,
      step="manufacturing_split"
  )
  ```
- [ ] Log allocation strategy:
  ```python
  if dc_holdback_pct == 0.0:
      logger.info("Zara strategy: 100% allocated to stores at Week 0")
  else:
      logger.info(f"Standard strategy: {initial_allocation_pct*100}% to stores, {dc_holdback_pct*100}% DC reserve")
  ```
- [ ] Allocate to clusters (call _allocate_to_clusters helper)
- [ ] Return allocation dictionary

**Acceptance:**
- DC holdback adapts to parameters (0% or 45%)
- Unit conservation validated
- Logging clear

---

### Task 4: Implement _allocate_to_clusters() Helper

**Goal:** Distribute initial allocation across clusters

**Subtasks:**
- [ ] Get cluster percentages from K-means:
  ```python
  cluster_stats = clusterer.get_cluster_stats()
  cluster_percentages = cluster_stats['allocation_percentage'].to_dict()
  ```
- [ ] Allocate to each cluster:
  ```python
  cluster_allocations = []
  for cluster_id, percentage in cluster_percentages.items():
      cluster_total = int(initial_allocation_total × (percentage / 100.0))
      cluster_allocations.append({
          "cluster_id": cluster_id,
          "cluster_label": cluster_labels[cluster_id],
          "percentage": percentage,
          "total_units": cluster_total
      })
  ```
- [ ] Validate cluster allocations sum to initial_allocation_total:
  ```python
  actual_sum = sum(c['total_units'] for c in cluster_allocations)
  self.validate_unit_conservation(
      expected=initial_allocation_total,
      actual=actual_sum,
      step="cluster_allocation"
  )
  ```
- [ ] Handle rounding errors (distribute remainder to largest cluster):
  ```python
  remainder = initial_allocation_total - actual_sum
  if remainder > 0:
      largest_cluster = max(cluster_allocations, key=lambda c: c['total_units'])
      largest_cluster['total_units'] += remainder
      logger.info(f"Adjusted {largest_cluster['cluster_label']} by {remainder} for rounding")
  ```
- [ ] Return cluster allocations

**Acceptance:**
- Cluster allocations sum to initial_allocation_total
- Rounding errors handled
- Unit conservation validated

---

### Task 5: Implement calculate_allocation_factor() with Hybrid Formula

**Goal:** Calculate store allocation factor (70% historical + 30% attributes)

**Subtasks:**
- [ ] Calculate historical performance score:
  ```python
  historical_score = store['avg_weekly_sales_12mo'] / cluster_avg['avg_weekly_sales_12mo']
  # Normalize: 1.0 = cluster average, >1.0 = above average, <1.0 = below average
  ```
- [ ] Calculate attribute score:
  ```python
  size_score = store['store_size_sqft'] / cluster_avg['store_size_sqft']
  income_score = store['median_income'] / cluster_avg['median_income']
  tier_score = store['location_tier'] / 3.0  # Normalize A=1.0, B=0.67, C=0.33

  attribute_score = (
      0.5 × size_score +
      0.3 × income_score +
      0.2 × tier_score
  )
  ```
- [ ] Calculate allocation factor (70/30 weighted average):
  ```python
  allocation_factor = 0.7 × historical_score + 0.3 × attribute_score
  ```
- [ ] Return allocation factor

**Acceptance:**
- Allocation factor calculated correctly
- Weights applied (70% historical, 30% attributes)
- Normalized scores used

---

### Task 6: Implement _allocate_to_stores() with 2-Week Minimum

**Goal:** Distribute cluster allocation to stores with minimum enforcement

**Subtasks:**
- [ ] For each cluster, get stores in cluster:
  ```python
  cluster_stores = stores_data[stores_data['cluster_id'] == cluster_id]
  ```
- [ ] Calculate allocation factor for each store:
  ```python
  cluster_avg = cluster_stores.mean(numeric_only=True).to_dict()
  store_factors = {}
  for _, store in cluster_stores.iterrows():
      factor = self.calculate_allocation_factor(store, cluster_avg)
      store_factors[store['store_id']] = factor
  ```
- [ ] Normalize factors to sum to 1.0:
  ```python
  total_factor = sum(store_factors.values())
  normalized_factors = {sid: f/total_factor for sid, f in store_factors.items()}
  ```
- [ ] Allocate based on normalized factors:
  ```python
  store_allocations = []
  for store_id, factor in normalized_factors.items():
      base_allocation = int(cluster_total × factor)
      store = cluster_stores[cluster_stores['store_id'] == store_id].iloc[0]
      weekly_forecast = forecast_by_week[0]  # Week 1 forecast
      min_allocation = weekly_forecast × 2  # 2-week minimum

      final_allocation = max(base_allocation, min_allocation)

      if final_allocation > base_allocation:
          logger.info(f"Store {store_id}: Bumped to 2-week minimum ({min_allocation} units)")

      store_allocations.append({
          "store_id": store_id,
          "cluster": cluster_label,
          "initial_allocation": final_allocation,
          "dc_reserve": int(final_allocation × dc_holdback_pct / initial_allocation_pct),
          "allocation_factor": factor
      })
  ```
- [ ] Validate store allocations sum to cluster total:
  ```python
  actual_sum = sum(s['initial_allocation'] for s in store_allocations)
  # Note: May exceed cluster_total due to 2-week minimums
  # Adjust largest allocation down if needed
  if actual_sum > cluster_total:
      excess = actual_sum - cluster_total
      largest_store = max(store_allocations, key=lambda s: s['initial_allocation'])
      largest_store['initial_allocation'] -= excess
      logger.warning(f"Reduced {largest_store['store_id']} by {excess} due to 2-week minimum adjustments")
  ```
- [ ] Return store allocations

**Acceptance:**
- 2-week minimum enforced for all stores
- Store allocations sum to cluster total (after adjustments)
- Unit conservation maintained

---

### Task 7: Implement validate_unit_conservation() Method

**Goal:** Strict validation to prevent unit loss/gain

**Subtasks:**
- [ ] Compare expected vs actual:
  ```python
  if expected != actual:
      raise ValueError(
          f"Unit conservation failed at {step}: "
          f"expected {expected}, got {actual} (diff: {actual - expected})"
      )
  ```
- [ ] Log successful validation:
  ```python
  logger.debug(f"Unit conservation OK at {step}: {expected} units")
  ```

**Acceptance:**
- Raises ValueError if units don't match
- Logs validation steps
- Zero tolerance (no rounding errors)

---

### Task 8: Write Unit Tests

**Goal:** Verify InventoryAgent allocation logic

**Subtasks:**
- [ ] Create file: `backend/tests/unit/agents/test_inventory_agent.py`
- [ ] **Test 1:** `test_manufacturing_calculation()`
  - Test: 8000 demand × 1.20 safety = 9600
  - Test: 10000 demand × 1.15 safety = 11500
- [ ] **Test 2:** `test_dc_holdback_0_percent()` (Zara scenario)
  - Parameters: dc_holdback=0.0
  - Assert: 100% allocated to stores
  - Assert: dc_holdback_total = 0
- [ ] **Test 3:** `test_dc_holdback_45_percent()` (Standard retail)
  - Parameters: dc_holdback=0.45
  - Assert: 55% allocated to stores
  - Assert: 45% held at DC
- [ ] **Test 4:** `test_cluster_allocation_sums_correct()`
  - Allocate to 3 clusters
  - Assert: sum(cluster allocations) == initial_allocation_total
- [ ] **Test 5:** `test_store_allocation_sums_correct()`
  - Allocate to 50 stores
  - Assert: sum(store allocations) == initial_allocation_total
- [ ] **Test 6:** `test_2_week_minimum_enforced()`
  - Low-demand store with <2 weeks base allocation
  - Assert: final_allocation >= 2 × weekly_forecast
- [ ] **Test 7:** `test_unit_conservation_validation()`
  - Test validation passes when units match
  - Test validation raises ValueError when units don't match

**Acceptance:**
- All 7 tests pass
- Test coverage >80%

---

## Testing Strategy

### Unit Tests (This Story)
- Test manufacturing calculation
- Test DC holdback (0% and 45%)
- Test cluster allocation
- Test store allocation
- Test 2-week minimum
- Test unit conservation validation

### Integration Tests (Story 4)
- Integration with Phase 6 Demand Agent
- Integration with Phase 5 orchestrator

### Performance Tests
- Allocation time: <5 seconds (50 stores)

---

## Definition of Done

**Code Complete:**
- [ ] InventoryAgent class implemented
- [ ] calculate_manufacturing() method working
- [ ] allocate_initial() method with parameter-driven holdback working
- [ ] calculate_allocation_factor() method (70/30 hybrid) working
- [ ] validate_unit_conservation() method working
- [ ] 2-week minimum enforced
- [ ] Type hints and docstrings complete

**Testing Complete:**
- [ ] 7 unit tests passing
- [ ] Unit conservation errors = 0
- [ ] Test coverage >80%

**Quality Checks:**
- [ ] Code follows project style
- [ ] Error handling complete (unit conservation failures)
- [ ] Logging informative (allocation steps, parameter adaptation)
- [ ] No print statements

**Documentation:**
- [ ] Docstrings complete
- [ ] Allocation algorithm explained in code comments
- [ ] Ready for Story 3 (Replenishment)

---

## Notes

**Hierarchical Allocation Flow:**
1. **Manufacturing:** `8000 demand × 1.20 safety = 9600 units`
2. **DC Split (45%):** `9600 × 0.55 = 5280 initial, 9600 × 0.45 = 4320 holdback`
3. **Cluster (K-means):** `5280 × 40% = 2112 Fashion_Forward, 35% = 1848 Mainstream, 25% = 1320 Value_Conscious`
4. **Store (Hybrid):** Each cluster's units distributed by `0.7×historical + 0.3×attributes`

**Parameter-Driven Adaptation Examples:**
- **Zara (Fast Fashion):**
  - `dc_holdback_percentage=0.0` → 100% to stores, 0% DC
  - No replenishment needed, all inventory shipped at Week 0
- **Standard Retail:**
  - `dc_holdback_percentage=0.45` → 55% to stores, 45% DC
  - Weekly replenishment from DC reserve

**Unit Conservation Checkpoints:**
1. Manufacturing split: `manufacturing_qty == initial + holdback`
2. Cluster allocation: `sum(cluster_totals) == initial_allocation_total`
3. Store allocation: `sum(store_totals) == cluster_total`
4. Final check: `sum(all_store_allocations) == initial_allocation_total`

**2-Week Minimum Rationale:**
- Prevents stores from running out in Week 1
- Provides buffer for weekly replenishment delays
- Ensures minimum viable inventory for product display

**Common Issues:**
- **Rounding Errors:** Distribute remainder to largest cluster/store
- **2-Week Minimum Exceeds Cluster Total:** Reduce largest store allocation to compensate
- **Unit Conservation Failure:** Check for floating point errors, ensure integer arithmetic

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
