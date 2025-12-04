# Operational Workflow: 3-Agent System

**Version:** 3.2
**Date:** 2025-10-12
**Status:** Workflow Guide with Concrete Examples (Aligned with Technical Architecture v1.0)
**Scope:** Archetype 1 (Fashion Retail) MVP Focus

> **Note**: For system overview, business value, and agent responsibilities, see [Product Brief v3.2](product_brief_v3.2.md).
> This document focuses on **how the system works operationally** with concrete examples.

---

## Table of Contents

1. [Key Concept: Forecast Once, Allocate with Math](#key-concept-forecast-once-allocate-with-math)
2. [Parameter Configuration](#parameter-configuration)
3. [5-Phase Operational Workflow](#5-phase-operational-workflow)
4. [Example Scenarios](#example-scenarios)
5. [Quick Reference](#quick-reference)

---

## Key Concept: Forecast Once, Allocate with Math

### What Gets Forecasted vs. What Gets Allocated

**❌ We DON'T forecast:**
- Store_01 × Week 1 = 15 dresses ← Too granular
- Store_01 × Week 2 = 18 dresses
- ... (50 stores × 12 weeks = 600 forecasts)

**✅ We DO forecast (just once):**
- **Category total**: "Women's Dresses will sell 8,000 units over 12 weeks"
- **Method**: Ensemble Prophet + ARIMA (parallel, averaged)
- That's it. Only 1 forecast.

**Then we allocate using historical patterns (just math, no forecasting):**

```
8,000 Total Forecast (FORECASTED - Prophet 8,200 + ARIMA 7,800 averaged)
    ↓
    ├─ Fashion_Forward (40% = 3,200) ← Historical % (MATH)
    │       ├─ Store_01: 176 dresses ← Store factor 5.5% (MATH)
    │       ├─ Store_02: 160 dresses ← Store factor 5.0% (MATH)
    │       └─ ... (18 more stores)
    │
    ├─ Mainstream (35% = 2,800) ← Historical % (MATH)
    └─ Value_Conscious (25% = 2,000) ← Historical % (MATH)
```

---

## Concrete Example: Clustering & Allocation

### Setup: 50 Stores, 8,000 Forecasted Dresses

| Store ID | Size (sqft) | Location | Income | Fashion Tier | Store Format | Region | Avg Weekly Sales (12mo) |
|----------|-------------|----------|--------|--------------|--------------|--------|-------------------------|
| Store_01 | 20,000 | Downtown NYC | $95k | Premium | Mall | Northeast | 285 |
| Store_02 | 18,000 | LA Mall | $88k | Premium | Mall | West | 260 |
| Store_03 | 15,000 | Chicago Suburb | $65k | Mid | ShoppingCenter | Midwest | 180 |
| Store_25 | 10,000 | Rural Ohio | $45k | Value | Outlet | Midwest | 95 |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

### Step 1: Store Clustering (K-means with 7 Features)

**K-means++ with StandardScaler normalization (K=3)**

**7 Features (all standardized before clustering):**
1. **avg_weekly_sales_12mo** (MOST IMPORTANT - captures store performance)
2. **store_size_sqft** (physical capacity)
3. **median_income** (customer purchasing power)
4. **location_tier** (A=3, B=2, C=1 - urban/suburban/rural)
5. **fashion_tier** (Premium=3, Mainstream=2, Value=1 - fashion positioning)
6. **store_format** (Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1)
7. **region** (Northeast=1, Southeast=2, Midwest=3, West=4)

**Example: Store_01 features before standardization:**
```python
{
    "avg_weekly_sales_12mo": 285,
    "store_size_sqft": 20000,
    "median_income": 95000,
    "location_tier": 3,  # A-tier urban
    "fashion_tier": 3,   # Premium
    "store_format": 4,   # Mall
    "region": 1          # Northeast
}
```

**After StandardScaler (mean=0, std=1):**
```python
{
    "avg_weekly_sales_12mo": 1.85,   # High performer
    "store_size_sqft": 1.22,
    "median_income": 1.45,
    "location_tier": 0.89,
    "fashion_tier": 1.12,
    "store_format": 0.95,
    "region": -0.34
}
```

**Result: 3 Clusters (K-means++)**

**Cluster 1: Fashion_Forward** (20 stores)
- Stores: 01, 02, 07, 09, 12, ...
- Characteristics: Large, high income, premium, high sales velocity
- **Last year total**: 5,200 dresses

**Cluster 2: Mainstream** (18 stores)
- Stores: 03, 04, 08, 11, 15, ...
- Characteristics: Medium, mid-income, mid-tier
- **Last year total**: 3,150 dresses

**Cluster 3: Value_Conscious** (12 stores)
- Stores: 05, 06, 10, 13, 25, ...
- Characteristics: Smaller, lower income, value, lower sales velocity
- **Last year total**: 1,650 dresses

---

### Step 2: Calculate Cluster Distribution % (Historical Analysis)

```
Total last year = 5,200 + 3,150 + 1,650 = 10,000 dresses

Fashion_Forward:    5,200 / 10,000 = 52% → Adjust to 40%
Mainstream:         3,150 / 10,000 = 32% → Adjust to 35%
Value_Conscious:    1,650 / 10,000 = 17% → Adjust to 25%
```

**Apply to forecast:**
- Fashion_Forward: 8,000 × 40% = **3,200 dresses**
- Mainstream: 8,000 × 35% = **2,800 dresses**
- Value_Conscious: 8,000 × 25% = **2,000 dresses**

---

### Step 3: Calculate Store Allocation Factors (Within Each Cluster)

**Focus on Fashion_Forward cluster (3,200 dresses → 20 stores)**

**For Store_01:**

**A. Historical Factor (70% weight)**
```
Store_01 last year = 285 dresses
Cluster total last year = 5,200 dresses
Historical factor = 285 / 5,200 = 5.48%
```

**B. Attribute Factor (30% weight)**
```
Capacity score = Store_01 size / Avg cluster size
                = 20,000 / 18,000 = 1.11

Cluster total capacity = 2,000 points (all 20 stores)
Attribute factor = 111 / 2,000 = 5.55%
```

**C. Hybrid Allocation Factor**
```
Allocation factor = (0.70 × 5.48%) + (0.30 × 5.55%)
                  = 3.84% + 1.67%
                  = 5.50%
```

**D. Apply to Forecast**
```
Store_01 allocation = 3,200 × 5.50% = 176 dresses (season total)
```

**Repeat for all 20 stores in Fashion_Forward cluster:**
- Store_01: 5.50% → 176 dresses
- Store_02: 5.00% → 160 dresses
- Store_07: 4.30% → 138 dresses
- ... (17 more stores)
- **Total**: 3,200 dresses

---

### Summary: One Forecast, Math-Based Allocation

```
STEP 1: Forecast (Ensemble Prophet + ARIMA)
    Category: Women's Dresses (example - auto-detected from CSV)
    Prophet forecast: 8,200 units
    ARIMA forecast: 7,800 units
    Final forecast (averaged): 8,000 units ← ONLY FORECASTING HAPPENS HERE

STEP 2: Cluster Distribution (Historical %)
    Fashion_Forward: 40% = 3,200 ← MATH
    Mainstream: 35% = 2,800 ← MATH
    Value_Conscious: 25% = 2,000 ← MATH

STEP 3: Store Allocation (Hybrid: 70% hist + 30% attr)
    Store_01: 5.50% of 3,200 = 176 ← MATH
    Store_02: 5.00% of 3,200 = 160 ← MATH
    ...
```

**Key Insight**: We forecast once (category-level using ensemble Prophet + ARIMA), then use K-means clustering (7 features) and historical patterns to allocate. This addresses the professor's concern about "store by week being too granular for forecasting."

---

## Parameter Configuration

### Key Parameters (Archetype 1 - Fashion Retail MVP)

| Category | Parameter | Value | Purpose |
|----------|-----------|-------|---------|
| **Forecasting** | Forecast method | Ensemble Prophet + ARIMA | Robust category-level forecast |
| | Forecast horizon | 12 weeks | Short fashion season |
| | Variance threshold | 20% | When to re-forecast |
| | Clustering method | K-means++ (K=3) | Data-driven store grouping |
| | Clustering features | 7 features | Sales, size, income, tiers, format, region |
| **Inventory** | Safety stock | 20% | Buffer for demand volatility |
| | Holdback % | 45% | Keep at DC for replenishment |
| | Initial allocation | 55% | Ship to stores at launch |
| | Replenishment | Weekly | Fast-moving fashion |
| | Replenishment formula | forecast - inventory | Simple (rely on re-forecast for variance) |
| **Pricing** | Markdown checkpoint | Week 6 | Mid-season review |
| | Target sell-through | 60% by Week 6 | On-track indicator |
| | Markdown formula | Gap × Elasticity | Gap × 2.0, 5% rounding, 40% cap |
| | Markdown differentiation | Uniform | Same % across all stores (no cluster variation) |

> For full parameter matrix across all 3 archetypes, see [Product Brief v3.2](product_brief_v3.2.md).

---

## 5-Phase Operational Workflow

| Phase | Timing | Key Actions | Output |
|-------|--------|-------------|--------|
| **1. Pre-Season** | Week -24 (6 months before) | Ensemble forecast → Calculate manufacturing order | Order 9,600 units |
| **2. Season Start** | Week 0 | K-means clustering → Allocate hierarchically to stores | Ship 55% to stores, hold 45% at DC |
| **3. In-Season** | Weeks 1-12 (weekly) | Monitor actuals → Simple replenishment | Weekly store replenishment |
| **4. Mid-Season** | Week 6 | Check sell-through → Apply Gap × Elasticity markdown | Uniform markdown + re-forecast |
| **5. Season End** | Post-Week 12 | Analyze performance → Tune parameters | Updated parameters for next season |

---

### PHASE 1: Pre-Season Planning (Week -24)

**Goal**: Forecast demand and commit to manufacturing order

**Steps**:
1. **Demand Agent**: Ensemble forecast (Prophet + ARIMA parallel, averaged)
   - Prophet forecast: 8,200 dresses
   - ARIMA forecast: 7,800 dresses
   - Final forecast (averaged): **8,000 dresses**
2. **Demand Agent**: K-means clustering (K=3, 7 features, StandardScaler)
   - Fashion_Forward: 20 stores (40%)
   - Mainstream: 18 stores (35%)
   - Value_Conscious: 12 stores (25%)
3. **Demand Agent**: Calculate store allocation factors (hybrid: 70% hist + 30% attr)
4. **Inventory Agent**: Manufacturing order = 8,000 × 1.20 = **9,600 units**

**Decision**: Manufacturing Order

```
Ensemble forecast: 8,000 dresses (Prophet 8,200 + ARIMA 7,800)
Safety stock: 20% (Archetype 1)
Manufacturing order: 8,000 × 1.20 = 9,600 dresses

→ Human review required (Modify/Accept approval modal)
→ Upon acceptance, send to manufacturer
```

**Note**: No confidence scoring in v3.2 (simplified MVP)

---

### PHASE 2: Season Start (Week 0)

**Goal**: Allocate 9,600 units to 50 stores hierarchically

**Steps**:
1. **Inventory Agent**: Allocate to clusters
   - Fashion_Forward: 9,600 × 40% = **3,840 units**
   - Mainstream: 9,600 × 35% = **3,360 units**
   - Value_Conscious: 9,600 × 25% = **2,400 units**

2. **Inventory Agent**: Allocate within clusters to stores
   - Store_01: 3,840 × 5.5% = **211 units** (season total)
   - Store_02: 3,840 × 5.0% = **192 units**
   - ... (48 more stores)

3. **Inventory Agent**: Split into initial shipment + holdback
   - Store_01 initial: 211 × 55% = **116 units** (ship now)
   - Store_01 holdback: 211 × 45% = **95 units** (keep at DC)

**Result**:
- **5,280 units shipped to stores** (55%)
- **4,320 units held at DC** (45%) for replenishment

---

### PHASE 3: In-Season Replenishment (Weeks 1-12, Weekly)

**Goal**: Top-up stores based on actual sales performance

**Simplified Replenishment Logic (for each store, every week)**:

```python
1. Check variance (Orchestrator level)
   Actual sales vs. forecast: If variance > 20% → Trigger re-forecast

2. Calculate replenishment need (Simple Formula)
   remaining_allocation = season_total - total_shipped_so_far
   weeks_remaining = 12 - current_week
   next_week_forecast = remaining_allocation / weeks_remaining

   current_inventory = get_store_inventory(store)
   replenishment_qty = max(0, next_week_forecast - current_inventory)

3. Ship from DC
   IF dc_inventory ≥ replenishment_qty:
       SHIP replenishment_qty
   ELSE:
       SHIP partial (whatever is available)
```

**Key Change from v3.1**: No variance adjustment in replenishment formula. Simple `forecast - inventory`. If variance >20%, orchestrator triggers re-forecast instead.

**Example (Store_01, Week 2)**:
- Remaining allocation: 95 units
- Weeks remaining: 10
- Next week forecast: 95 / 10 = **9.5 units/week**
- Current inventory: 6 units
- **Replenishment**: max(0, 9.5 - 6) = **3.5 → 4 units**

**If actuals are significantly off**: Orchestrator detects >20% variance and triggers re-forecast, which updates remaining allocations.

---

### PHASE 4: Mid-Season Pricing (Week 6)

**Goal**: Check sell-through and apply uniform markdown if behind target

**Gap × Elasticity Markdown Logic**:

```python
1. Calculate sell-through rate
   Sell-through = Total_Sold / Total_Manufactured

   Example: 5,280 sold / 9,600 manufactured = 55%

2. Calculate gap
   Target (Archetype 1, Week 6): 60%
   Actual: 55%
   Gap = 0.60 - 0.55 = 0.05 (5 percentage points)

3. Apply Gap × Elasticity formula
   elasticity_coefficient = 2.0  # Tunable
   markdown_raw = gap × elasticity_coefficient
   markdown_raw = 0.05 × 2.0 = 0.10 (10%)

   # Round to nearest 5%
   markdown_rounded = round(0.10 × 20) / 20 = 0.10 → 10%

   # Cap at 40%
   markdown_depth = min(markdown_rounded, 0.40) = 10%

4. Apply uniform markdown (no cluster differentiation)
   ALL stores: 10% markdown

   Example scenarios:
   - 58% sell-through → gap=0.02 → 2% × 2.0 = 4% → rounds to 5%
   - 50% sell-through → gap=0.10 → 10% × 2.0 = 20%
   - 40% sell-through → gap=0.20 → 20% × 2.0 = 40% (capped)

5. Trigger re-forecast
   Demand Agent re-forecasts weeks 7-12 with new prices (ensemble Prophet + ARIMA)
   Update replenishment plan
```

**Key Changes from v3.1**:
- **Removed**: Fixed markdown table (15%/30%/50%)
- **Added**: Gap × Elasticity formula (elasticity=2.0, tunable)
- **Removed**: Cluster-specific markdown differentiation (uniform across all stores)

**Example**: 55% sell-through at Week 6 → 10% uniform markdown → Re-forecast remaining weeks

---

### PHASE 5: Season End Analysis (Post-Week 12)

**Goal**: Evaluate performance and tune parameters for next season

**Key Metrics**:

```
Forecast Accuracy:
├─ MAPE (Mean Absolute Percentage Error): Target <20%
├─ Bias: Over/under-forecasting tendency (target ±5%)
└─ Re-forecast Trigger Accuracy: 90%+ (correctly identify >20% variance)

Business Impact:
├─ Stockout events: Count and lost sales estimate
├─ Overstock: Final inventory value
├─ Markdown costs: Total discount impact
└─ Inventory turnover: vs. prior year

System Performance:
├─ Workflow runtime: Target <60 seconds (full 3-agent workflow)
└─ Human approval rate: Track % modify vs. accept
```

**Note**: Confidence calibration removed in v3.2 (no confidence scoring)

**Parameter Tuning Examples**:
- Cluster distribution off? Re-run K-means with updated features
- Too many stockouts? Increase safety stock from 20% to 22%
- Markdown timing late? Move from Week 6 to Week 5
- Holdback too high? Reduce from 45% to 42%
- Elasticity coefficient: Tune from 2.0 to 2.2 if markdowns too aggressive

**Output**: Updated parameter file for next season

---

## Example Scenarios

> These scenarios show how the system behaves in different real-world situations.

---

### Scenario 1: Successful Season (On-Track Performance)

**Setup**: Ensemble forecast 8,000 (Prophet 8,200 + ARIMA 7,800) → 9,600 manufactured → 12-week season

**What Happened**:
- **Week 1**: Actual sales match forecast (±5% variance) ✅
- **Weeks 2-6**: Variance stays below 20% threshold → No re-forecast needed
- **Week 6 checkpoint**: 61% sell-through (target: 60%) → Gap = -0.01 → **No markdown** (negative gap) ✅
- **Weeks 7-12**: Continue simple replenishment (forecast - inventory), inventory depletes as planned
- **Week 12 end**: Sold 7,800 units (97.5% of forecast), MAPE: 12% ✅

**Result**: Full margin preserved, no markdowns, minimal leftover inventory

---

### Scenario 2: High Demand - Re-Forecast Triggered

**Setup**: Ensemble forecast 8,000 (Prophet 8,200 + ARIMA 7,800) → 9,600 manufactured

**What Happened**:
- **Week 1**: Actual sales 850 (forecast: 650) → **+31% variance** ⚠️
- **Orchestrator detects >20% variance**: Triggers re-forecast
- **Re-forecast (ensemble)**: Prophet 10,800 + ARIMA 10,200 = 10,500 units (averaged)
- **Problem**: Only have 9,600 manufactured → Expected stockout by Week 8
- **Action**: Emergency reorder 2,000 units (air freight, 4-week lead time)
- **Week 6**: 68% sell-through (target: 60%) → Gap = -0.08 (negative) → **No markdown** (ahead of target)
- **Emergency units arrive Week 6**: Continue replenishment to high-performing stores
- **Week 12 end**: Sold 10,200 units, leftover 1,400 units

**Result**: System adapted quickly via re-forecast trigger, captured unexpected demand, avoided major stockouts

---

### Scenario 3: Low Demand - Uniform Markdown Applied

**Setup**: Ensemble forecast 8,000 (Prophet 8,200 + ARIMA 7,800) → 9,600 manufactured

**What Happened**:
- **Weeks 1-6**: Actual sales consistently 10-15% below forecast (but <20%, no re-forecast)
- **Week 6 checkpoint**: 52% sell-through (target: 60%) → **Gap = 0.08 (8 percentage points)** ⚠️
- **Gap × Elasticity markdown**:
  - Gap: 0.08
  - Elasticity: 2.0
  - Markdown raw: 0.08 × 2.0 = 0.16 (16%)
  - Rounded to nearest 5%: 15%
  - **Apply 15% uniform markdown to ALL stores** (no cluster differentiation)
- **Re-forecast triggered**: Ensemble re-forecasts weeks 7-12 with new prices
- **Weeks 7-12**: Sales lift +18% post-markdown
- **Week 12 end**: Sold 7,200 units, leftover 2,400 units

**Result**: Uniform 15% markdown accelerated sell-through, recovered margin, avoided larger overstock

**Note**: Unlike v3.1, no cluster-specific markdown differentiation (simplified MVP)

---

## Quick Reference

### Key Decision Thresholds (Archetype 1 - Fashion)

| Decision | Threshold | Action |
|----------|-----------|--------|
| **Re-forecast** | Variance > 20% | Run ensemble forecast (Prophet + ARIMA) |
| **Human review** | All manufacturing orders | Require approval (Modify/Accept modal) |
| **Markdown** | Sell-through < 60% at Week 6 | Apply Gap × Elasticity formula (elasticity=2.0) |
| **Emergency order** | Variance > 30% | Alert + recommend air freight order |

**Note**: No confidence threshold in v3.2 (confidence scoring removed)

### Data Flow Between Agents (Context-Rich Handoffs)

```
DEMAND AGENT
    ↓ (Pass forecast object: 8,000 units, prophet/arima forecasts, cluster %, store factors)
INVENTORY AGENT
    ↓ (Pass allocation object: manufacturing order 9,600, allocations by store)
PRICING AGENT
    ↓ (Pass markdown object: Gap × Elasticity result, sell-through analysis)
DEMAND AGENT (re-forecast if markdown applied OR variance >20%)
```

**Key**: Objects passed directly between agents (context-rich handoffs, no database queries). Orchestrator enables/disables handoffs dynamically.

### Technology Stack

- **Agent Framework**: OpenAI Agents SDK v0.3.3+
- **LLM**: Azure OpenAI Service (gpt-4o-mini via Responses API)
- **Package Manager**: UV (10-100x faster than pip)
- **Backend**: Python 3.11+ + FastAPI + SQLite
- **Frontend**: React 18 + TypeScript + Vite + Shadcn/ui + TanStack Query
- **ML/Forecasting**: Prophet, pmdarima (ARIMA), scikit-learn (K-means, StandardScaler)
- **Real-time**: WebSocket streaming of agent progress
- **Human-in-the-loop**: Modify (iterative) + Accept (approve), no Reject button

---

**Document Owner**: Independent Study Project
**Last Updated**: 2025-10-12
**Version**: 3.2
**Related Documents**:
- [Product Brief v3.2](product_brief_v3.2.md) - System overview, business value, agent details (aligned with architecture)
- [Technical Architecture v1.0](../architecture/technical_architecture.md) - Complete technical specifications

---

## Summary of Changes from v3.1

**Version 3.2 (2025-10-12)** - Updated to align with technical architecture v1.0:

### 1. Updated Forecasting Method
- **Changed**: From generic "hierarchical time-series" to **Ensemble Prophet + ARIMA**
- **Details**: Both models run in parallel, results averaged (no confidence weighting)
- **Example**: Prophet 8,200 + ARIMA 7,800 = 8,000 (averaged)

### 2. Updated Store Clustering to K-means (7 Features)
- **Changed**: From vague "K-means based on size, income, fashion tier" to specific **7-feature K-means++ with StandardScaler**
- **Features**: avg_weekly_sales_12mo (MOST IMPORTANT), store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
- **Example**: Added concrete feature values before/after standardization

### 3. Simplified Replenishment Formula
- **Removed**: Variance adjustment formula (`adjusted_need = base_need × variance_factor`)
- **Changed to**: Simple formula `replenishment = max(0, forecast - inventory)`
- **Rationale**: Rely on orchestrator's 20% variance re-forecast trigger instead of per-store adjustments

### 4. Gap × Elasticity Markdown Formula
- **Removed**: Fixed markdown table (15%/30%/50% based on variance ranges)
- **Changed to**: `Markdown = Gap × Elasticity` where elasticity=2.0 (tunable), 5% rounding, 40% cap
- **Removed**: Cluster-specific markdown differentiation (now uniform across all stores)
- **Examples**:
  - 58% sell-through → 2% gap → 4% → rounds to 5%
  - 50% sell-through → 10% gap → 20%
  - 40% sell-through → 20% gap → 40% (capped)

### 5. Removed Confidence Scoring
- **Removed**: All references to confidence scores, confidence intervals, confidence thresholds
- **Changed**: Human review required for all manufacturing orders (Modify/Accept modal)
- **Removed**: "Confidence calibration" from success metrics

### 6. Added Tech Stack Details
- **Added**: OpenAI Agents SDK, Azure OpenAI Service, UV package manager
- **Added**: FastAPI + SQLite backend, React + TypeScript frontend
- **Added**: Context-rich handoffs, dynamic handoff enabling, WebSocket real-time updates
- **Added**: Human-in-the-loop (Modify/Accept, no Reject)

### 7. Updated Success Metrics
- **Removed**: Confidence calibration metric
- **Added**: Re-forecast Trigger Accuracy (90%+)
- **Added**: Workflow runtime <60 seconds
- **Added**: Human approval rate tracking

### 8. Updated Parameter Table
- **Added**: Forecast method (Ensemble Prophet + ARIMA)
- **Added**: Clustering method (K-means++ with 7 features)
- **Added**: Replenishment formula (forecast - inventory)
- **Added**: Markdown formula (Gap × Elasticity with elasticity=2.0)
- **Added**: Markdown differentiation (Uniform - no cluster variation)

### 9. Updated Scenarios
- **Scenario 1**: Removed confidence scoring, emphasized no markdown when ahead of target
- **Scenario 2**: Updated to show ensemble re-forecast (Prophet + ARIMA), removed confidence language
- **Scenario 3**: Changed from cluster-specific markdowns to **uniform 15% markdown** across all stores

### Overall Impact
- ✅ **Simplified**: Removed confidence scoring, simpler replenishment, uniform markdowns
- ✅ **More robust**: Ensemble forecasting (Prophet + ARIMA)
- ✅ **Data-driven**: K-means with 7 specific features + StandardScaler
- ✅ **Cleaner logic**: Simple replenishment + re-forecast trigger
- ✅ **More flexible**: Gap × Elasticity markdown (tunable elasticity coefficient)
- ✅ **Implementation-ready**: Complete tech stack specified, context-rich handoffs detailed

**Rationale**: All changes align with technical architecture v1.0 decisions made during Week 4 development planning.
