# Phase 1: Mock Data Generation - Implementation Plan

**Phase:** Phase 1
**Agent:** `*agent dev`
**Duration:** 1-2 days
**Status:** Ready to Start
**Start Date:** 2025-10-14
**Target End Date:** 2025-10-16

---

## Phase Overview

### Goal
Generate 38 realistic CSV files (1 historical sales, 1 store attributes, 36 weekly actuals across 3 scenarios) that produce MAPE 12-18% when used for ML training and testing.

### Success Criteria
- [ ] 38 CSV files generated in correct folder structure
- [ ] All 6 validation types pass
- [ ] MAPE between 12-18% (not <10% = too perfect, not >20% = unusable)
- [ ] Week 5 variance >20% in all 3 scenarios (black swan event)
- [ ] Historical data shows clear seasonality (FFT test)
- [ ] Store attributes produce 3 distinct K-means clusters (silhouette >0.4)

### Dependencies
**Requires:**
- ✅ Data Specification v3.2 complete
- ✅ Python 3.11+ installed
- ✅ numpy + pandas available (pure Python, no Prophet/ARIMA yet)

**Blocks:**
- Phase 2 Backend (cannot train models without data)

---

## Reference Documents

**Primary:**
- [Data Specification v3.2](../../data/data_specification_v3.2.md) - Complete implementation guide (Sections 3, 4, 5, 6)
- [Technical Architecture v3.2](../../architecture/technical_architecture_v3.2.md) - Section 9 (ML Approach), data models

**Secondary:**
- [PRD v3.2](../../prd/prd_v3.2.md) - Acceptance criteria
- [Process Workflow v3.2](../../process_workflow/process_workflow_v3.2.md) - Expected behavior

---

## Task Breakdown

### Task 1: Project Setup & Environment
**Priority:** P0 (Blocker)
**Estimated Time:** 0.5 hours
**Dependencies:** None
**Assigned:** `*agent dev`

**Description:**
Set up Python project structure, install dependencies, create folder structure for data generation.

**Acceptance Criteria:**
- [ ] Folder `data/mock/` created with subfolders:
  - `data/mock/training/`
  - `data/mock/scenarios/normal_season/`
  - `data/mock/scenarios/high_demand/`
  - `data/mock/scenarios/low_demand/`
- [ ] `generate_mock_data.py` file created
- [ ] numpy + pandas installed (verify with `import` test)

**Validation:**
```bash
cd data/mock
python generate_mock_data.py --help
# Should show usage without errors
```

**Risks:**
- Python version mismatch: Ensure 3.11+

---

### Task 2: Implement Core Data Generation Functions
**Priority:** P0 (Blocker)
**Estimated Time:** 3 hours
**Dependencies:** Task 1
**Assigned:** `*agent dev`

**Description:**
Implement 4 core functions for data generation logic (see Data Spec Section 6.2):
1. `calculate_seasonality(date, category)` - Monthly seasonal multipliers
2. `apply_holiday_spike(date, category, base_sales)` - Holiday boost logic
3. `calculate_store_sales_multiplier(store_attributes)` - Store performance formula
4. `inject_black_swan_event(scenario, week, category_sales)` - Week 5 disruptions

**Acceptance Criteria:**
- [ ] All 4 functions implemented with type hints
- [ ] Docstrings with examples
- [ ] Functions return expected data types (float, int, DataFrame)

**Validation:**
```python
# Test seasonality
assert calculate_seasonality(datetime(2023, 5, 1), "Women's Dresses") == 1.5  # Spring peak
```

**Risks:**
- Formula complexity: Reference Data Spec Section 3.2 for exact formulas

---

### Task 3: Generate Store Attributes CSV
**Priority:** P0 (Blocker)
**Estimated Time:** 1 hour
**Dependencies:** Task 2
**Assigned:** `*agent dev`

**Description:**
Generate `store_attributes.csv` with 50 stores, 7 features, correlated with sales performance.

**Acceptance Criteria:**
- [ ] File created: `data/mock/training/store_attributes.csv`
- [ ] 50 rows (S001 to S050)
- [ ] 8 columns: `store_id, size_sqft, income_level, foot_traffic, competitor_density, online_penetration, population_density, mall_location`
- [ ] K-means (K=3) produces silhouette score >0.4 (validation check)

**Validation:**
```python
stores = pd.read_csv('data/mock/training/store_attributes.csv')
assert len(stores) == 50
assert stores['size_sqft'].between(3000, 15000).all()
```

**Risks:**
- Poor clustering: If silhouette <0.4, adjust feature distributions

---

### Task 4: Generate Historical Sales CSV
**Priority:** P0 (Blocker)
**Estimated Time:** 4 hours
**Dependencies:** Task 2, Task 3
**Assigned:** `*agent dev`

**Description:**
Generate `historical_sales_2022_2024.csv` with 3 years of daily sales data for 3 categories, 50 stores.

**Acceptance Criteria:**
- [ ] File created: `data/mock/training/historical_sales_2022_2024.csv`
- [ ] ~54,750 rows (3 years × 365 days × 50 stores)
- [ ] 5 columns: `date, category, store_id, quantity_sold, revenue`
- [ ] Date range: 2022-01-01 to 2024-12-31
- [ ] 3 categories: Women's Dresses, Men's Shirts, Accessories
- [ ] Seasonality patterns applied (see Data Spec Section 4.2)
- [ ] Variable pricing: base ± 10% noise
- [ ] Noise level: ±10-15% (cleaner than actuals)

**Validation:**
```python
historical = pd.read_csv('data/mock/training/historical_sales_2022_2024.csv')
assert len(historical) == 54750
assert set(historical['category'].unique()) == {'Women's Dresses', 'Men's Shirts', 'Accessories'}
```

**Risks:**
- File size: ~3-5 MB expected (within limits)

---

### Task 5: Generate Scenario 1 - Normal Season
**Priority:** P0 (Blocker)
**Estimated Time:** 2 hours
**Dependencies:** Task 4
**Assigned:** `*agent dev`

**Description:**
Generate 12 weekly actuals CSVs for normal_season scenario (Week 1-12, Spring 2025).

**Acceptance Criteria:**
- [ ] 12 files created: `data/mock/scenarios/normal_season/actuals_week_01.csv` to `actuals_week_12.csv`
- [ ] ~350 rows per file (50 stores × 7 days)
- [ ] **Week 5 black swan:** Viral TikTok trend → +30% Women's Dresses for 5 days
- [ ] Noise level: ±20-25% (messier than historical)
- [ ] Expected MAPE: 12-15%

**Validation:**
```python
week_5 = pd.read_csv('data/mock/scenarios/normal_season/actuals_week_05.csv')
# Verify variance >20%
```

**Risks:**
- Variance too low: Add more noise

---

### Task 6: Generate Scenario 2 - High Demand
**Priority:** P0 (Blocker)
**Estimated Time:** 1.5 hours
**Dependencies:** Task 5
**Assigned:** `*agent dev`

**Description:**
Generate 12 weekly actuals CSVs for high_demand scenario (economic boom).

**Acceptance Criteria:**
- [ ] 12 files created
- [ ] All categories +25% above baseline
- [ ] **Week 5 black swan:** Competitor bankruptcy → +40% all categories
- [ ] Expected MAPE: 15-18%

---

### Task 7: Generate Scenario 3 - Low Demand
**Priority:** P0 (Blocker)
**Estimated Time:** 1.5 hours
**Dependencies:** Task 5
**Assigned:** `*agent dev`

**Description:**
Generate 12 weekly actuals CSVs for low_demand scenario (economic uncertainty).

**Acceptance Criteria:**
- [ ] 12 files created
- [ ] All categories -20% below baseline
- [ ] **Week 5 black swan:** Supply chain disruption → -25% all categories
- [ ] Expected MAPE: 15-18%

---

### Task 8: Implement Validation Suite
**Priority:** P0 (Blocker)
**Estimated Time:** 2 hours
**Dependencies:** Task 7
**Assigned:** `*agent dev`

**Description:**
Implement all 6 validation types from Data Spec Section 5.1.

**Acceptance Criteria:**
- [ ] Validation Type 1-6 implemented
- [ ] `--validate` flag triggers all checks
- [ ] Clear pass/fail report printed

**Validation:**
```bash
python generate_mock_data.py --validate
# Should show all ✅
```

---

### Task 9: Implement MAPE Validation
**Priority:** P0 (Blocker)
**Estimated Time:** 2 hours
**Dependencies:** Task 8
**Assigned:** `*agent dev`

**Description:**
Add MAPE validation to ensure generated data produces target MAPE 12-18%.

**Acceptance Criteria:**
- [ ] MAPE calculated for each scenario
- [ ] MAPE between 12-18% for all 3 scenarios
- [ ] Report shows per-scenario MAPE

---

### Task 10: Create README.md
**Priority:** P1 (High)
**Estimated Time:** 1 hour
**Dependencies:** Task 9
**Assigned:** `*agent dev`

**Description:**
Create README.md in data/mock/ folder using template from Data Spec Section 8.

**Acceptance Criteria:**
- [ ] File created: `data/mock/README.md`
- [ ] Includes: Quick Start, File Structure, Data Dictionary, Testing Instructions

---

### Task 11: Test with Fixed Seed + Regenerate Flag
**Priority:** P1 (High)
**Estimated Time:** 0.5 hours
**Dependencies:** Task 10
**Assigned:** `*agent dev`

**Description:**
Run full data generation with fixed seed (42) and test --regenerate flag.

**Acceptance Criteria:**
- [ ] `python generate_mock_data.py` runs successfully
- [ ] All 38 files generated in <60 seconds
- [ ] Fixed seed produces identical data on re-run
- [ ] `--regenerate` flag produces different data

---

### Task 12: Final Cleanup & Documentation
**Priority:** P1 (High)
**Estimated Time:** 1 hour
**Dependencies:** Task 11
**Assigned:** `*agent dev`

**Description:**
Code cleanup, final documentation, prepare for Phase 2 handoff.

**Acceptance Criteria:**
- [ ] Code formatted
- [ ] Type hints complete
- [ ] Technical decisions documented
- [ ] Retrospective drafted

---

## Task Dependencies Graph

```
Task 1 (0.5h) → Task 2 (3h) → Task 3 (1h) → Task 4 (4h) → Task 5 (2h) → Task 8 (2h) → Task 9 (2h) → Task 10 (1h) → Task 11 (0.5h) → Task 12 (1h)
                                                             ↓
                                                        Task 6 (1.5h) → Task 7 (1.5h)
```

**Critical Path:** Task 1 → 2 → 3 → 4 → 5 → 8 → 9 → 10 → 11 → 12 (Total: 17 hours)

---

## Timeline Estimate

### 2-Day Sprint (Recommended)

| Day | Time | Tasks | Progress | Notes |
|-----|------|-------|----------|-------|
| **Day 1** | 0-4h | Task 1-3 | 25% | Foundation |
| **Day 1** | 4-8h | Task 4 | 50% | Historical data |
| **Day 1** | 8-10h | Task 5-7 | 75% | All scenarios |
| **Day 2** | 0-3h | Task 8-9 | 90% | Validation |
| **Day 2** | 3-5h | Task 10-12 | 100% | Docs + cleanup |

---

## Validation Checkpoints

### Checkpoint 1: Foundation Complete (After Task 3)
**Exit Criteria:**
- [ ] 50 store attributes generated
- [ ] K-means produces 3 distinct clusters (silhouette >0.4)

**If Failed:** Adjust feature distributions

---

### Checkpoint 2: Historical Data Complete (After Task 4)
**Exit Criteria:**
- [ ] 54,750 rows generated
- [ ] Seasonality visible

**If Failed:** Debug seasonality calculation

---

### Checkpoint 3: Validation Pass (After Task 9)
**Exit Criteria:**
- [ ] All 6 validation types pass
- [ ] MAPE between 12-18% for all scenarios

**If Failed:** Iterate on noise levels

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MAPE out of range | Medium | High | Iterate on noise levels (6 strategies in Data Spec 4.5) |
| K-means clustering poor | Low | Medium | Adjust store attribute distributions |
| Week 5 variance not triggering | Medium | High | Increase black swan magnitude |

---

## Notes for Agent

### Before Starting
1. Read Data Specification v3.2 (PRIMARY reference)
2. Verify Python 3.11+ installed
3. Create folder structure

### During Implementation
1. Update checklist.md after each task
2. Document decisions in technical_decisions.md
3. Commit code + docs together

### After Completion
1. Validate all acceptance criteria
2. Write retrospective.md
3. Update ../README.md phase status

---

**Last Updated:** 2025-10-14
**Status:** Ready to Start
