# Phase 1: Data Generation - Implementation Plan

**Phase:** 1 of 8
**Goal:** Generate realistic mock data for 3 scenarios (normal, high demand, low demand)
**Agent:** `*agent dev`
**Duration Estimate:** 1-2 days
**Status:** ⏳ Not Started

---

## Requirements Source

- **Primary:** `planning/6_data_specification_v3.2.md` - Complete CSV specifications
- **Secondary:** `planning/2_process_workflow_v3.3.md` - Scenario definitions
- **Reference:** `planning/1_product_brief_v3.3.md` - Context

---

## Key Deliverables

1. **Historical Sales Data** (`historical_sales_2022_2024.csv`)
   - 54,750 rows (3 years × 365 days × 50 stores)
   - 3 categories: Women's Dresses, Men's Shirts, Accessories
   - Seasonality patterns, holiday events, weekly patterns
   - Clean data (±10-15% noise) for model training

2. **Store Attributes** (`store_attributes.csv`)
   - 50 stores with 7 K-means features
   - Expected 3 clusters: Fashion_Forward, Mainstream, Value_Conscious
   - Correlation formula for sales multiplier

3. **Weekly Actuals** (36 CSV files)
   - 3 scenarios × 12 weeks each
   - Messier data (±20-25% noise) for testing
   - Week 5 variance >20% in all scenarios (to trigger re-forecast)

4. **Validation Suite**
   - 6 validation types: Completeness, Quality, Format, Statistical, Pattern, Weekly Actuals
   - MAPE target: 12-18% across all scenarios

5. **Documentation** (`README.md`)
   - Data dictionary
   - Generation methodology
   - Validation results

---

## Task Breakdown

### Task 1: Environment Setup
**Estimate:** 1 hour
**Dependencies:** None
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Install required libraries (pandas, numpy, scipy, faker)
- [ ] Create project directory structure
- [ ] Set random seed for reproducibility

### Task 2: Historical Sales Data Generation
**Estimate:** 4 hours
**Dependencies:** Task 1
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Implement base sales generator with seasonality
- [ ] Add category-specific patterns (Women's Dresses, Men's Shirts, Accessories)
- [ ] Implement holiday events (Valentine's, Mother's Day, Black Friday, Christmas)
- [ ] Add weekly patterns (weekend peaks)
- [ ] Apply ±10-15% noise
- [ ] Generate 54,750 rows
- [ ] Export to `historical_sales_2022_2024.csv`

### Task 3: Store Attributes Generation
**Estimate:** 2 hours
**Dependencies:** Task 1
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Generate 50 stores with 7 features
- [ ] Implement correlation formula for sales multiplier
- [ ] Ensure 3 distinguishable clusters (Fashion_Forward, Mainstream, Value_Conscious)
- [ ] Export to `store_attributes.csv`

### Task 4: Weekly Actuals Generation (Normal Scenario)
**Estimate:** 3 hours
**Dependencies:** Task 2, Task 3
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Implement baseline weekly actuals generator
- [ ] Add viral TikTok event (+30% Week 5)
- [ ] Apply ±20-25% noise
- [ ] Generate 12 CSV files (actuals_week_1.csv to actuals_week_12.csv)
- [ ] Validate Week 5 variance >20%

### Task 5: Weekly Actuals Generation (High Demand Scenario)
**Estimate:** 2 hours
**Dependencies:** Task 4
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Copy normal scenario baseline
- [ ] Apply +25% to all categories
- [ ] Add competitor bankruptcy event (+40% Week 5)
- [ ] Generate 12 CSV files for high_demand scenario
- [ ] Validate Week 5 variance >20%

### Task 6: Weekly Actuals Generation (Low Demand Scenario)
**Estimate:** 2 hours
**Dependencies:** Task 4
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Copy normal scenario baseline
- [ ] Apply -20% to all categories
- [ ] Add supply chain disruption (-25% Week 5)
- [ ] Generate 12 CSV files for low_demand scenario
- [ ] Validate Week 5 variance >20%

### Task 7: Validation Suite Implementation
**Estimate:** 3 hours
**Dependencies:** Task 2, Task 3, Task 4, Task 5, Task 6
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Implement Completeness validation (row counts, all stores present)
- [ ] Implement Quality validation (no negatives, revenue = qty × price)
- [ ] Implement Format validation (UTF-8, date formats, headers)
- [ ] Implement Statistical validation (mean/std checks, K-means silhouette >0.4)
- [ ] Implement Pattern validation (seasonality FFT test)
- [ ] Implement Weekly Actuals validation (7 consecutive days, all 50 stores)
- [ ] Run all validations and generate report

### Task 8: MAPE Validation
**Estimate:** 2 hours
**Dependencies:** Task 7
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Implement simple forecast baseline (moving average)
- [ ] Calculate MAPE for all 3 scenarios
- [ ] Validate MAPE 12-18% target
- [ ] Document results

### Task 9: Documentation
**Estimate:** 1 hour
**Dependencies:** Task 8
**Status:** ⏳ Not Started

**Subtasks:**
- [ ] Write README.md with data dictionary
- [ ] Document generation methodology
- [ ] Include validation results
- [ ] Add usage examples

---

## Total Estimates

- **Total Tasks:** 9
- **Total Time:** 20 hours
- **Calendar Days:** 1-2 days (assuming 8-10 hours/day)

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (50% complete)
**After:** Task 4 complete
**Verify:**
- [ ] Historical data looks realistic (visual inspection)
- [ ] Store attributes show 3 clusters
- [ ] Normal scenario generated successfully

### Checkpoint 2: Pre-Completion
**After:** Task 8 complete
**Verify:**
- [ ] All 38 CSV files generated
- [ ] All 6 validation types pass
- [ ] MAPE 12-18% confirmed for all 3 scenarios
- [ ] Week 5 variance >20% in all scenarios

### Checkpoint 3: Final
**After:** Task 9 complete
**Verify:**
- [ ] README.md complete and clear
- [ ] All files committed to git
- [ ] Ready for handoff to Phase 2 (Frontend)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MAPE target not met (12-18%) | Medium | High | Tune noise levels and event magnitudes |
| Week 5 variance too low (<20%) | Low | High | Increase event magnitude for Week 5 |
| Clusters not distinguishable | Low | Medium | Adjust store attribute distributions |
| Data generation too slow | Low | Low | Optimize pandas operations, use vectorization |

---

## Notes

- Use fixed random seed (42) for reproducibility
- All dates in YYYY-MM-DD format
- All CSVs UTF-8 encoded
- Follow exact column names from data specification
- Test with small subset first before full generation

---

**Created:** [Date]
**Last Updated:** [Date]
**Status:** ⏳ Not Started
