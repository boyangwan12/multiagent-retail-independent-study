# Phase 7 Technical Decisions: Inventory Agent

**Epic:** Phase 7 - Inventory Agent
**Last Updated:** 2025-11-11
**Status:** Ready for Implementation

---

## Overview

This document records all technical decisions made during Phase 7 (Inventory Agent) implementation. Each decision includes rationale, alternatives considered, and impact on the system.

---

## TD-7.1: K-means Clustering with K=3

### Decision
Use K-means++ clustering with K=3 (fixed) to segment 50 stores into 3 clusters.

### Rationale
- **Business Understanding:** Retail typically operates with 3 tiers (High/Medium/Low, A/B/C, Premium/Mainstream/Value)
- **Silhouette Score:** K=3 produces silhouette score >0.4 on test data (good separation)
- **Interpretability:** 3 clusters are easy to explain to business users
- **Scalability:** K-means performs well on 50 stores (< 1 second runtime)

### Alternatives Considered
- **Hierarchical Clustering:** Slower, less interpretable dendrograms
- **DBSCAN:** Requires density tuning, may produce uneven cluster sizes
- **K=5:** Too granular for MVP, harder to interpret
- **K=2:** Too coarse, misses medium tier

### Implementation Details
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Normalize features (mean=0, std=1)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(store_features)

# K-means++ for better initialization
kmeans = KMeans(n_clusters=3, init='k-means++', random_state=42, n_init=10)
clusters = kmeans.fit_predict(features_scaled)
```

### Impact
- **Positive:** Fast, interpretable, good separation
- **Negative:** Fixed K (no dynamic cluster count)
- **Mitigation:** If silhouette <0.4, flag for manual review

### Reference
- PRD v3.3: Section 5.2 (K-means Clustering)
- Technical Architecture v3.3: Section 4.5 (ML Pipeline)

---

## TD-7.2: 7-Feature Clustering Model

### Decision
Use 7 features for clustering (not more, not less):
1. `avg_weekly_sales_12mo` (most important)
2. `store_size_sqft`
3. `median_income`
4. `location_tier` (ordinal: A=3, B=2, C=1)
5. `fashion_tier` (ordinal: Premium=3, Mainstream=2, Value=1)
6. `store_format` (ordinal: Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1)
7. `region` (ordinal: Northeast=1, Southeast=2, Midwest=3, West=4)

### Rationale
- **Feature Selection:** Combines performance (sales), capacity (size), demand driver (income), and attributes (tier/format/region)
- **Balance:** Not too many (overfitting), not too few (underfitting)
- **Data Availability:** All features present in store attributes CSV

### Alternatives Considered
- **More Features:** Add inventory turnover, distance to DC, store age → Data not available
- **Fewer Features:** Only sales + size → Misses demographic/location signals
- **PCA Dimensionality Reduction:** Loses interpretability

### Ordinal Encoding Rationale
- **Location Tier:** A > B > C (clear ordinal relationship)
- **Fashion Tier:** Premium > Mainstream > Value (clear ordinal relationship)
- **Store Format:** Mall > Standalone > ShoppingCenter > Outlet (based on foot traffic/sales potential)
- **Region:** Arbitrary encoding (no natural order) - captures regional patterns

### Impact
- **Positive:** Captures multiple dimensions of store performance
- **Negative:** Manual ordinal encoding (risk of incorrect ordering)
- **Mitigation:** Validate cluster assignments with business team

### Reference
- PRD v3.3: Section 10.1.2 (Store Attributes)
- Data Specification v3.2: Store attributes schema

---

## TD-7.3: StandardScaler Normalization

### Decision
Use StandardScaler (z-score normalization) to normalize features before clustering.

### Rationale
- **Feature Scale Differences:** avg_weekly_sales (100s) vs location_tier (1-3) → K-means sensitive to scale
- **StandardScaler Formula:** `z = (x - mean) / std` → mean=0, std=1
- **Industry Standard:** Most common preprocessing for K-means

### Alternatives Considered
- **MinMaxScaler:** Range [0,1] → Sensitive to outliers
- **RobustScaler:** Median/IQR → Better for outliers, but unnecessary for clean data
- **No Normalization:** Would bias clustering toward high-value features (sales)

### Implementation Details
```python
scaler = StandardScaler()
scaler.fit(store_features)  # Learn mean/std from training data
features_scaled = scaler.transform(store_features)  # Apply normalization
```

### Impact
- **Positive:** Equal feature importance, improves clustering quality
- **Negative:** Requires storing scaler object for new stores (future)
- **Mitigation:** Save scaler to database/file for reproducibility

### Reference
- scikit-learn StandardScaler documentation

---

## TD-7.4: Cluster Labeling Algorithm

### Decision
Automatically label clusters as Fashion_Forward, Mainstream, Value_Conscious based on cluster characteristics.

### Rationale
- **Business Interpretation:** Generic "Cluster 0/1/2" not meaningful to users
- **Automatic Labeling:** Based on avg_weekly_sales + fashion_tier + median_income

### Algorithm
```python
# Calculate cluster means for key features
cluster_means = df.groupby('cluster')[['avg_weekly_sales_12mo', 'fashion_tier', 'median_income']].mean()

# Sort by avg_weekly_sales (descending)
sorted_clusters = cluster_means.sort_values('avg_weekly_sales_12mo', ascending=False)

# Assign labels
labels = {
    sorted_clusters.index[0]: "Fashion_Forward",   # Highest sales
    sorted_clusters.index[1]: "Mainstream",        # Medium sales
    sorted_clusters.index[2]: "Value_Conscious"    # Lowest sales
}
```

### Alternatives Considered
- **Manual Labeling:** Business team assigns labels after review → Too slow for MVP
- **LLM Labeling:** Use GPT to interpret cluster characteristics → Unnecessary cost/complexity
- **Generic Labels:** "Cluster A/B/C" → Not user-friendly

### Impact
- **Positive:** Automatic, interpretable, consistent
- **Negative:** May mislabel if sales not primary differentiator
- **Mitigation:** Display cluster characteristics in UI for validation

### Reference
- Product Brief v3.3: Section 2.3 (Store Clustering)

---

## TD-7.5: Hybrid Allocation Factors (70% Historical + 30% Attributes)

### Decision
Calculate store allocation factors using: `factor = 0.7 × historical_performance + 0.3 × attribute_score`

### Rationale
- **Historical Performance (70%):** Past sales are strongest predictor of future demand
- **Attribute Score (30%):** Accounts for store capacity (size), demographics (income), tier
- **Balance:** Heavy weight on historical, moderate weight on attributes

### Calculation Details
```python
# Historical performance score (normalized within cluster)
historical_score = store_sales_12mo / cluster_avg_sales

# Attribute score (normalized composite)
attribute_score = (
    0.5 × (store_size / cluster_avg_size) +
    0.3 × (median_income / cluster_avg_income) +
    0.2 × (location_tier / 3.0)  # Normalize A=1.0, B=0.67, C=0.33
)

# Allocation factor
allocation_factor = 0.7 × historical_score + 0.3 × attribute_score
```

### Alternatives Considered
- **100% Historical:** Ignores capacity/demographic changes → Too rigid
- **50/50 Split:** Over-weights attributes → Historical is better predictor
- **Machine Learning:** Train regression model → Overkill for MVP

### Impact
- **Positive:** Balances past performance with future potential
- **Negative:** Arbitrary weights (70/30, 50/30/20)
- **Mitigation:** Make weights tunable parameters (post-MVP)

### Reference
- PRD v3.3: Section 5.2 (Store Allocation Factors)

---

## TD-7.6: DC Holdback Strategy (Parameter-Driven: 0% or 45%)

### Decision
DC holdback percentage is parameter-driven (extracted from natural language):
- **Zara-style fast fashion:** `dc_holdback_percentage = 0.0` (100% initial allocation)
- **Standard retail:** `dc_holdback_percentage = 0.45` (55% initial, 45% reserve)

### Rationale
- **Parameter-Driven Architecture:** Same code handles multiple retail strategies
- **0% Holdback:** Fast fashion (Zara) ships all inventory to stores at launch, no replenishment
- **45% Holdback:** Standard retail keeps 45% at DC for weekly replenishment flexibility

### Implementation Details
```python
# Parameter-driven allocation
initial_allocation_pct = 1.0 - parameters.dc_holdback_percentage  # 1.0 or 0.55
dc_holdback_pct = parameters.dc_holdback_percentage  # 0.0 or 0.45

initial_to_stores = int(manufacturing_qty × initial_allocation_pct)
dc_reserve = int(manufacturing_qty × dc_holdback_pct)

# Conditional replenishment logic
if parameters.replenishment_strategy == "none":
    # Skip replenishment phase entirely
    logger.info("Replenishment disabled - 100% allocated at Week 0")
else:
    # Enable weekly replenishment from DC reserve
    logger.info(f"Weekly replenishment enabled - {dc_holdback_pct*100}% DC reserve")
```

### Alternatives Considered
- **Fixed 45% Holdback:** Not flexible, doesn't support fast fashion
- **User-Tunable Slider:** Too many parameters for MVP
- **LLM-Decided Holdback:** Too unpredictable

### Impact
- **Positive:** Flexible, supports multiple retail models
- **Negative:** Requires accurate parameter extraction
- **Mitigation:** Parameter confirmation modal in UI

### Reference
- PRD v3.3: Section 1.3 (Parameter-Driven Architecture)
- Technical Architecture v3.3: Section 3 (Parameter-Driven Patterns)

---

## TD-7.7: 2-Week Minimum Store Allocation

### Decision
Enforce minimum allocation of 2 weeks' forecast per store.

### Rationale
- **Prevent Early Stockouts:** 1-week allocation too risky (no buffer)
- **Operational Constraint:** Stores need minimum viable inventory to display product
- **Replenishment Frequency:** Weekly replenishment → 2-week minimum provides safety buffer

### Implementation Details
```python
for store in cluster_stores:
    base_allocation = cluster_total × store.allocation_factor
    min_allocation = store.weekly_forecast × 2  # 2-week minimum

    final_allocation = max(base_allocation, min_allocation)

    if final_allocation > base_allocation:
        logger.info(f"Store {store.id}: Bumped to 2-week minimum ({min_allocation} units)")
```

### Alternatives Considered
- **1-Week Minimum:** Too risky, frequent stockouts
- **3-Week Minimum:** Over-allocates, reduces DC flexibility
- **No Minimum:** Some stores get <1 week → guaranteed stockouts

### Impact
- **Positive:** Reduces stockout risk, ensures minimum viable inventory
- **Negative:** May over-allocate to low-demand stores
- **Mitigation:** Monitor stockout rates, adjust minimum if needed

### Reference
- PRD v3.3: Section 5.3 (Initial Allocation)

---

## TD-7.8: Simple Replenishment Formula

### Decision
Use simple replenishment formula: `replenish_qty = next_week_forecast - current_inventory`

### Rationale
- **Simplicity:** Easy to understand, no complex optimization
- **Forecast-Based:** Aligns replenishment with weekly demand forecast
- **Inventory-Aware:** Accounts for current stock levels

### Implementation Details
```python
def calculate_replenishment(store_id, current_week):
    next_week_forecast = forecast_by_week[current_week + 1]
    current_inventory = get_store_inventory(store_id, current_week)

    replenish_qty = max(0, next_week_forecast - current_inventory)

    return replenish_qty
```

### Alternatives Considered
- **Safety Stock Buffer:** Add 10-20% buffer to forecast → Over-allocates
- **Multi-Week Lookahead:** Consider weeks N+1, N+2 → Too complex for MVP
- **Economic Order Quantity (EOQ):** Optimize order sizes → Overkill

### Impact
- **Positive:** Simple, transparent, aligned with forecast
- **Negative:** No safety buffer (risk of stockouts if forecast low)
- **Mitigation:** Re-forecast on variance >20% provides adaptive adjustment

### Reference
- PRD v3.3: Section 5.4 (Weekly Replenishment)
- Technical Architecture v3.3: Section 6 (Inventory Agent)

---

## TD-7.9: Unit Conservation Validation

### Decision
Validate unit conservation at every allocation step to prevent unit loss/gain.

### Rationale
- **Data Integrity:** Units cannot disappear or multiply during allocation
- **Debugging:** Catch allocation bugs early
- **Trust:** Users need to trust allocation sums are correct

### Validation Checks
```python
# Check 1: Manufacturing = Initial + Holdback
assert manufacturing_qty == initial_allocation + dc_holdback

# Check 2: Cluster allocations sum to initial allocation
assert sum(cluster_allocations) == initial_allocation

# Check 3: Store allocations sum to cluster allocation
for cluster in clusters:
    assert sum(cluster.store_allocations) == cluster.total_allocation

# Check 4: Total store allocations = initial allocation
assert sum(all_store_allocations) == initial_allocation
```

### Alternatives Considered
- **No Validation:** Trust the math → Risky, hard to debug
- **Post-Allocation Validation Only:** Catch errors late
- **Floating Point Tolerance:** Allow ±1 unit rounding → Masks real bugs

### Impact
- **Positive:** Early error detection, data integrity guarantee
- **Negative:** Additional compute overhead (~1ms per check)
- **Mitigation:** Assertions only in tests (disabled in production if needed)

### Reference
- Best practice: Data validation in financial/inventory systems

---

## TD-7.10: InventoryAgentOutput Contract

### Decision
Define strict Pydantic schema for Inventory Agent output to ensure contract compliance.

### Schema Definition
```python
from pydantic import BaseModel
from typing import List, Dict

class StoreAllocation(BaseModel):
    store_id: str
    cluster: str  # Fashion_Forward | Mainstream | Value_Conscious
    initial_allocation: int
    dc_reserve: int
    season_total: int  # initial + reserve
    allocation_factor: float

class ClusterAllocation(BaseModel):
    cluster_name: str
    cluster_percentage: float
    total_units: int
    store_count: int
    stores: List[StoreAllocation]

class InventoryAgentOutput(BaseModel):
    manufacturing_qty: int
    safety_stock_pct: float
    initial_allocation_total: int
    dc_holdback_total: int
    clusters: List[ClusterAllocation]
    allocation_timestamp: str
```

### Rationale
- **Contract Validation:** Phase 8 (Pricing Agent) depends on this contract
- **Type Safety:** Pydantic validates at runtime
- **Documentation:** Schema serves as API documentation

### Alternatives Considered
- **Plain Dict:** No validation → Runtime errors
- **TypedDict:** No runtime validation
- **JSON Schema:** Less Pythonic

### Impact
- **Positive:** Type safety, automatic validation, clear contract
- **Negative:** Schema changes require coordination with Phase 8
- **Mitigation:** Freeze contract after Phase 7 DoD

### Reference
- Phase 6 DemandAgentOutput (similar pattern)

---

## Summary

| Decision ID | Topic | Key Choice | Risk Level |
|-------------|-------|------------|------------|
| TD-7.1 | Clustering Algorithm | K-means K=3 | Low |
| TD-7.2 | Clustering Features | 7 features (sales, size, income, tiers) | Low |
| TD-7.3 | Normalization | StandardScaler | Low |
| TD-7.4 | Cluster Labeling | Automatic (sales-based) | Medium |
| TD-7.5 | Allocation Factors | 70% historical + 30% attributes | Medium |
| TD-7.6 | DC Holdback | Parameter-driven (0% or 45%) | Medium |
| TD-7.7 | Store Minimum | 2-week forecast minimum | Low |
| TD-7.8 | Replenishment Formula | Simple forecast - inventory | Low |
| TD-7.9 | Validation | Unit conservation checks | Low |
| TD-7.10 | Output Contract | Pydantic schema | Low |

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
