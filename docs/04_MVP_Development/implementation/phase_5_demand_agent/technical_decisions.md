# Phase 5: Demand Agent - Technical Decisions

**Phase:** 5 of 8
**Agent:** `*agent dev`
**Date:** 2025-10-17
**Status:** Not Started

---

## Key Decisions Summary

1. Prophet + ARIMA ensemble (parallel execution, simple average)
2. K-means clustering with 7 features (StandardScaler normalization)
3. 3 clusters (Fashion_Forward, Mainstream, Value_Conscious)
4. Hybrid allocation factors (70% historical + 30% attributes)
5. Parameter-driven safety stock (20%-25%)
6. Simple ensemble average (no weighted average)
7. K=3 fixed (no dynamic K selection)
8. Parallel model execution (asyncio.gather)
9. Fallback to single model if one fails
10. LLM reasoning for parameter interpretation (deterministic base logic)

---

## Decision Log

### Decision 1: Ensemble Forecasting Approach
**Date:** TBD
**Context:** Need robust forecast combining multiple models

**Options Considered:**
1. **Prophet + ARIMA Ensemble (Simple Average)**
   - Pros: Complementary strengths, simple to implement, robust
   - Cons: Assumes equal model quality

2. **Weighted Ensemble (Confidence-Based)**
   - Pros: Better accuracy if one model superior
   - Cons: Complex, requires confidence calibration

3. **Single Model (Prophet Only)**
   - Pros: Simpler, faster
   - Cons: Less robust, single point of failure

**Decision:** Prophet + ARIMA Ensemble (Simple Average)

**Rationale:** Prophet handles trend/seasonality well, ARIMA handles stationary patterns. Simple average is robust without over-tuning. Technical architecture v3.3 specifies ensemble approach.

**Implementation Notes:**
- Run both models in parallel (asyncio.gather)
- Average: `(prophet_total + arima_total) / 2`
- Calculate model agreement: `100 * (1 - abs(diff) / max(p, a))`
- Log warning if agreement <80%
- Fallback to single model if one fails

---

### Decision 2: K-means Clustering Features
**Date:** TBD
**Context:** What features to use for store clustering

**Options Considered:**
1. **7 Features (Comprehensive)**
   - Features: avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
   - Pros: Captures multiple dimensions, robust clustering
   - Cons: More complex, requires feature engineering

2. **3 Features (Simple)**
   - Features: avg_weekly_sales_12mo, store_size_sqft, median_income
   - Pros: Simpler, faster
   - Cons: May miss important patterns

3. **Sales Only**
   - Features: avg_weekly_sales_12mo
   - Pros: Very simple
   - Cons: Too simplistic, poor clusters

**Decision:** 7 Features (Comprehensive)

**Rationale:** Process workflow v3.3 specifies 7 features. Comprehensive approach captures store performance, capacity, demographics, and positioning. avg_weekly_sales_12mo is MOST IMPORTANT feature.

**Implementation Notes:**
```python
features = [
    'avg_weekly_sales_12mo',  # MOST IMPORTANT
    'store_size_sqft',
    'median_income',
    'location_tier',          # A=3, B=2, C=1
    'fashion_tier',           # Premium=3, Mainstream=2, Value=1
    'store_format',           # Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1
    'region'                  # Northeast=1, Southeast=2, Midwest=3, West=4
]
```
- Apply StandardScaler (mean=0, std=1)
- K-means++ initialization
- random_state=42 for reproducibility

---

### Decision 3: Number of Clusters (K)
**Date:** TBD
**Context:** How many clusters for store segmentation

**Options Considered:**
1. **K=3 (Fixed)**
   - Pros: Aligns with retail industry (high/mid/low), interpretable
   - Cons: May not be optimal for all scenarios

2. **Elbow Method (Dynamic K)**
   - Pros: Data-driven K selection
   - Cons: Complex, may vary across runs

3. **K=5 (More Granular)**
   - Pros: More detailed segmentation
   - Cons: Too granular for MVP, harder to interpret

**Decision:** K=3 (Fixed)

**Rationale:** Process workflow v3.3 specifies 3 clusters (Fashion_Forward, Mainstream, Value_Conscious). Industry-standard segmentation. Simple, interpretable, sufficient for MVP.

**Implementation Notes:**
- K=3 hardcoded
- Cluster names assigned based on avg_weekly_sales_12mo (high → Fashion_Forward)
- Target silhouette score >0.4

---

### Decision 4: Store Allocation Factor Calculation
**Date:** TBD
**Context:** How to calculate store-level allocation within clusters

**Options Considered:**
1. **Hybrid (70% Historical + 30% Attributes)**
   - Pros: Balances past performance with capacity/potential
   - Cons: Weights somewhat arbitrary

2. **Historical Only (100%)**
   - Pros: Simple, data-driven
   - Cons: No flexibility for new trends

3. **Attributes Only (100%)**
   - Pros: Forward-looking
   - Cons: Ignores past performance

**Decision:** Hybrid (70% Historical + 30% Attributes)

**Rationale:** Process workflow v3.3 specifies 70/30 hybrid. Historical performance is primary indicator, but 30% attribute weight allows flexibility for changing demand patterns or store capacity changes.

**Implementation Notes:**
- Historical factor: `store_sales / cluster_total_sales`
- Attribute factor: `store_size_sqft / cluster_total_size`
- Hybrid: `0.70 × hist + 0.30 × attr`
- Normalize within cluster to sum to 1.0

---

### Decision 5: Safety Stock Adjustment Strategy
**Date:** TBD
**Context:** How to adjust safety stock based on replenishment strategy

**Options Considered:**
1. **Parameter-Driven (20%-25%)**
   - Pros: Adapts to replenishment strategy, logical reasoning
   - Cons: Requires parameter interpretation

2. **Fixed 20%**
   - Pros: Simple, consistent
   - Cons: Not adaptive to different strategies

3. **ML-Predicted**
   - Pros: Data-driven optimization
   - Cons: Too complex for MVP

**Decision:** Parameter-Driven (20%-25%)

**Rationale:** Process workflow v3.3 specifies parameter-driven adjustment. No replenishment → higher buffer (25%). Weekly replenishment → standard buffer (20%). Bi-weekly → moderate (22%).

**Implementation Notes:**
```python
if replenishment_strategy == "none":
    safety_stock = 1.25  # 25%
elif replenishment_strategy == "weekly":
    safety_stock = 1.20  # 20%
elif replenishment_strategy == "bi-weekly":
    safety_stock = 1.22  # 22%
```
- LLM provides reasoning explanation (not decision logic)
- Deterministic base logic ensures consistency

---

### Decision 6: Prophet Configuration
**Date:** TBD
**Context:** Prophet hyperparameters for fashion retail

**Options Considered:**
1. **Default Prophet Settings**
   - Pros: No tuning needed
   - Cons: May not be optimal for fashion

2. **Tuned Settings (changepoint_prior_scale=0.05)**
   - Pros: Better fit for volatile fashion demand
   - Cons: Requires tuning knowledge

**Decision:** Tuned Settings

**Rationale:** Fashion demand is volatile with frequent trend changes. Lower changepoint_prior_scale (0.05 vs default 0.05) allows more flexibility. Weekly seasonality important, yearly not needed (short seasons).

**Implementation Notes:**
```python
Prophet(
    changepoint_prior_scale=0.05,  # Flexibility in trend changes
    seasonality_mode='additive',    # Additive seasonality
    weekly_seasonality=True,
    yearly_seasonality=False,       # Not enough history
    daily_seasonality=False
)
```

---

### Decision 7: ARIMA Configuration
**Date:** TBD
**Context:** ARIMA hyperparameters for automated selection

**Options Considered:**
1. **Manual ARIMA (p, d, q)**
   - Pros: Full control
   - Cons: Requires manual tuning per dataset

2. **auto_arima (Automated)**
   - Pros: Automatic parameter selection, seasonal support
   - Cons: Slower

**Decision:** auto_arima (Automated)

**Rationale:** pmdarima's auto_arima handles parameter selection automatically. Supports seasonal ARIMA (SARIMAX) for weekly patterns (m=52). stepwise=True for faster search.

**Implementation Notes:**
```python
auto_arima(
    ts_weekly,
    seasonal=True,           # Enable seasonal ARIMA
    m=52,                    # Weekly seasonality (52 weeks/year)
    stepwise=True,           # Faster parameter search
    information_criterion='aic',
    max_p=5, max_q=5,        # AR/MA limits
    max_P=2, max_Q=2,        # Seasonal limits
    max_d=2, max_D=1         # Differencing limits
)
```

---

### Decision 8: Parallel Execution Strategy
**Date:** TBD
**Context:** How to run Prophet + ARIMA concurrently

**Options Considered:**
1. **asyncio.gather() with to_thread**
   - Pros: True parallelism, built into Python
   - Cons: Requires async/await

2. **multiprocessing.Pool**
   - Pros: True CPU parallelism
   - Cons: Pickle overhead, complex

3. **Sequential Execution**
   - Pros: Simple
   - Cons: 2x slower (~10s vs ~5s)

**Decision:** asyncio.gather() with to_thread

**Rationale:** FastAPI is async-based. asyncio.gather() allows concurrent execution without multiprocessing overhead. to_thread() offloads CPU-bound forecasting to thread pool.

**Implementation Notes:**
```python
prophet_task = asyncio.to_thread(prophet_forecast, data, weeks)
arima_task = asyncio.to_thread(arima_forecast, data, weeks)
prophet_result, arima_result = await asyncio.gather(
    prophet_task,
    arima_task,
    return_exceptions=True
)
```

---

### Decision 9: Model Failure Handling
**Date:** TBD
**Context:** What to do when Prophet or ARIMA fails

**Options Considered:**
1. **Fail Workflow (Strict)**
   - Pros: Forces data quality
   - Cons: Poor UX, no recovery

2. **Fallback to Single Model**
   - Pros: Robust, graceful degradation
   - Cons: Lower accuracy

3. **Use Historical Average**
   - Pros: Always works
   - Cons: Too simple, poor quality

**Decision:** Fallback to Single Model

**Rationale:** Ensemble robustness means one model can fail without breaking workflow. Log warning, use remaining model. Better than failing entirely.

**Implementation Notes:**
- Prophet fails → use ARIMA only
- ARIMA fails → use Prophet only
- Both fail → return error (unrecoverable)
- Log model failures for investigation

---

### Decision 10: Re-Forecast Strategy
**Date:** TBD
**Context:** How to handle variance-triggered re-forecast

**Options Considered:**
1. **Full Re-Forecast (All Weeks)**
   - Pros: Complete recalculation
   - Cons: Wasteful (already sold weeks don't change)

2. **Remaining Weeks Only**
   - Pros: Efficient, logical
   - Cons: Need to preserve already-sold data

3. **Incremental Adjustment**
   - Pros: Fast
   - Cons: May compound errors

**Decision:** Remaining Weeks Only

**Rationale:** Only re-forecast unsold weeks. Append actuals to historical data, forecast remaining weeks. Keep original clustering (don't re-cluster).

**Implementation Notes:**
- Weeks elapsed: `variance_info.week_number`
- Weeks remaining: `horizon - elapsed`
- Updated curve: `original[:elapsed] + new_forecast`
- Keep original clustering, allocations, silhouette score

---

## Key Metrics (TBD after implementation)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Forecast MAPE | <20% | TBD | TBD |
| Clustering silhouette score | >0.4 | TBD | TBD |
| Prophet + ARIMA agreement | Within 10% | TBD | TBD |
| Forecast execution time | <10s | TBD | TBD |
| Model agreement warnings | <20% of forecasts | TBD | TBD |

---

## Future Enhancements

### Enhancement 1: Weighted Ensemble
**Description:** Weight Prophet + ARIMA by historical accuracy
**Benefit:** Better accuracy if one model consistently outperforms
**Effort:** Medium (requires performance tracking)
**Priority:** Low (simple average sufficient for MVP)

### Enhancement 2: Dynamic K Selection
**Description:** Use elbow method or silhouette analysis for optimal K
**Benefit:** Data-driven cluster count
**Effort:** Low (scikit-learn built-in)
**Priority:** Low (K=3 works well)

### Enhancement 3: XGBoost Ensemble Member
**Description:** Add XGBoost as third ensemble member
**Benefit:** Captures non-linear patterns
**Effort:** High (new model, tuning)
**Priority:** Low (post-MVP)

### Enhancement 4: Store-Level Forecasting
**Description:** Forecast each store individually (50 forecasts)
**Benefit:** More granular predictions
**Effort:** High (50x computational cost)
**Priority:** Low (conflicts with category-level philosophy)

---

## Key Takeaways (to be filled after implementation)

### What Worked Well
- TBD

### Lessons Learned
- TBD

### For Next Phase (Phase 6: Inventory Agent)
- TBD

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Phase 5 Not Started
