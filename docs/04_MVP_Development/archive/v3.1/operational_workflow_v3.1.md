# Operational Workflow: 3-Agent System

**Version:** 3.1
**Date:** 2025-10-11
**Status:** Workflow Guide with Concrete Examples
**Scope:** Archetype 1 (Fashion Retail) MVP Focus

> **Note**: For system overview, business value, and agent responsibilities, see [Product Brief v3.1](product_brief_v3.1.md).
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
- That's it. Only 1 forecast.

**Then we allocate using historical patterns (just math, no forecasting):**

```
8,000 Total Forecast (FORECASTED)
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

| Store ID | Size (sqft) | Location | Income | Fashion Tier | Last Year Sales |
|----------|-------------|----------|--------|--------------|-----------------|
| Store_01 | 20,000 | Downtown NYC | $95k | Premium | 285 |
| Store_02 | 18,000 | LA Mall | $88k | Premium | 260 |
| Store_03 | 15,000 | Chicago Suburb | $65k | Mid | 180 |
| Store_25 | 10,000 | Rural Ohio | $45k | Value | 95 |
| ... | ... | ... | ... | ... | ... |

---

### Step 1: Store Clustering (Group Similar Stores)

**K-means clustering (k=3)** based on: size, income, fashion tier, historical sales

**Result: 3 Clusters**

**Cluster 1: Fashion_Forward** (20 stores)
- Stores: 01, 02, 07, 09, 12, ...
- Characteristics: Large, high income, premium
- **Last year total**: 5,200 dresses

**Cluster 2: Mainstream** (18 stores)
- Stores: 03, 04, 08, 11, 15, ...
- Characteristics: Medium, mid-income, mid-tier
- **Last year total**: 3,150 dresses

**Cluster 3: Value_Conscious** (12 stores)
- Stores: 05, 06, 10, 13, 25, ...
- Characteristics: Smaller, lower income, value
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
STEP 1: Forecast (Machine Learning)
    Category: Women's Dresses
    Total: 8,000 units ← ONLY FORECASTING HAPPENS HERE

STEP 2: Cluster Distribution (Historical %)
    Fashion_Forward: 40% = 3,200 ← MATH
    Mainstream: 35% = 2,800 ← MATH
    Value_Conscious: 25% = 2,000 ← MATH

STEP 3: Store Allocation (Hybrid: 70% hist + 30% attr)
    Store_01: 5.50% of 3,200 = 176 ← MATH
    Store_02: 5.00% of 3,200 = 160 ← MATH
    ...
```

**Key Insight**: We forecast once (category-level), then use historical patterns and store attributes to allocate. This addresses the professor's concern about "store by week being too granular for forecasting."

---

## Parameter Configuration

### Key Parameters (Archetype 1 - Fashion Retail MVP)

| Category | Parameter | Value | Purpose |
|----------|-----------|-------|---------|
| **Forecasting** | Forecast horizon | 12 weeks | Short fashion season |
| | Variance threshold | 20% | When to re-forecast |
| | Store clusters | 3-5 | Fashion_Forward, Mainstream, Value_Conscious |
| **Inventory** | Safety stock | 20% | Buffer for demand volatility |
| | Holdback % | 45% | Keep at DC for replenishment |
| | Initial allocation | 55% | Ship to stores at launch |
| | Replenishment | Weekly | Fast-moving fashion |
| **Pricing** | Markdown checkpoint | Week 6 | Mid-season review |
| | Target sell-through | 60% by Week 6 | On-track indicator |
| | Markdown depths | 15%, 30%, 50% | Based on variance |

> For full parameter matrix across all 3 archetypes, see [Product Brief v3.1](product_brief_v3.1.md).

---

## 5-Phase Operational Workflow

| Phase | Timing | Key Actions | Output |
|-------|--------|-------------|--------|
| **1. Pre-Season** | Week -24 (6 months before) | Forecast category demand → Calculate manufacturing order | Order 9,600 units |
| **2. Season Start** | Week 0 | Allocate inventory hierarchically to stores | Ship 55% to stores, hold 45% at DC |
| **3. In-Season** | Weeks 1-12 (weekly) | Monitor actuals → Replenish stores | Weekly store replenishment |
| **4. Mid-Season** | Week 6 | Check sell-through → Apply markdowns if needed | Markdown decision + re-forecast |
| **5. Season End** | Post-Week 12 | Analyze performance → Tune parameters | Updated parameters for next season |

---

### PHASE 1: Pre-Season Planning (Week -24)

**Goal**: Forecast demand and commit to manufacturing order

**Steps**:
1. **Demand Agent**: Forecast category total (8,000 dresses)
2. **Demand Agent**: Calculate cluster distribution (40% / 35% / 25%)
3. **Demand Agent**: Calculate store allocation factors (5.5%, 5.0%, 4.3%, ...)
4. **Inventory Agent**: Manufacturing order = 8,000 × 1.20 = **9,600 units**

**Decision**: Manufacturing Order

```
Forecast: 8,000 dresses
Safety stock: 20% (Archetype 1)
Manufacturing order: 8,000 × 1.20 = 9,600 dresses

IF confidence < 70%:
    → Require human review
ELSE:
    → Auto-approve and send to manufacturer
```

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

**Replenishment Logic (for each store, every week)**:

```
1. Check variance
   Actual sales vs. forecast: If variance > 20% → Re-forecast

2. Calculate replenishment need
   remaining_allocation = season_total - total_shipped_so_far
   weeks_remaining = 12 - current_week
   base_need = remaining_allocation / weeks_remaining

   variance_factor = actual_last_week / forecast_last_week
   adjusted_need = base_need × variance_factor

3. Calculate replenishment quantity
   replenishment_qty = max(0, adjusted_need - current_inventory)

4. Ship from DC
   IF dc_inventory ≥ replenishment_qty:
       SHIP replenishment_qty
   ELSE:
       SHIP partial (whatever is available)
```

**Example (Store_01, Week 2)**:
- Remaining allocation: 95 units
- Weeks remaining: 10
- Base need: 95 / 10 = 9.5 units/week
- Actual sales last week: 12 units (forecast: 8 units)
- Variance factor: 12 / 8 = 1.5 (selling 50% faster)
- Adjusted need: 9.5 × 1.5 = **14 units**
- Current inventory: 6 units
- **Replenishment**: 14 - 6 = **8 units**

---

### PHASE 4: Mid-Season Pricing (Week 6)

**Goal**: Check sell-through and apply markdowns if behind target

**Markdown Decision Logic**:

```
1. Calculate sell-through rate
   Sell-through = Total_Sold / Total_Manufactured

   Example: 5,280 sold / 9,600 manufactured = 55%

2. Compare to target
   Target (Archetype 1, Week 6): 60%
   Variance: 55% - 60% = -5% (behind target)

3. Determine markdown depth
   IF variance < -10%: 50% markdown (aggressive)
   ELIF variance < -5%: 30% markdown (moderate)
   ELIF variance < -3%: 15% markdown (light)
   ELSE: No markdown needed

4. Optional: Cluster-specific markdowns
   Fashion_Forward: 58% sell-through → 15% markdown
   Mainstream: 53% sell-through → 30% markdown
   Value_Conscious: 42% sell-through → 50% markdown

5. Trigger re-forecast
   Demand Agent re-forecasts weeks 7-12 with new prices
   Update replenishment plan
```

**Example**: 55% sell-through at Week 6 → 15% category markdown → Re-forecast remaining weeks

---

### PHASE 5: Season End Analysis (Post-Week 12)

**Goal**: Evaluate performance and tune parameters for next season

**Key Metrics**:

```
Forecast Accuracy:
├─ MAPE (Mean Absolute Percentage Error): Target <20%
├─ Bias: Over/under-forecasting tendency (target ±5%)
└─ Confidence calibration: Were confidence scores accurate?

Business Impact:
├─ Stockout events: Count and lost sales estimate
├─ Overstock: Final inventory value
├─ Markdown costs: Total discount impact
└─ Inventory turnover: vs. prior year
```

**Parameter Tuning Examples**:
- Cluster distribution off? Adjust Fashion_Forward from 40% to 42%
- Too many stockouts? Increase safety stock from 20% to 22%
- Markdown timing late? Move from Week 6 to Week 5
- Holdback too high? Reduce from 45% to 42%

**Output**: Updated parameter file for next season

---

## Example Scenarios

> These scenarios show how the system behaves in different real-world situations.

---

### Scenario 1: Successful Season (On-Track Performance)

**Setup**: 8,000 forecast → 9,600 manufactured → 12-week season

**What Happened**:
- **Week 1**: Actual sales match forecast (±5% variance) ✅
- **Weeks 2-6**: Variance stays below 20% threshold → No re-forecast needed
- **Week 6 checkpoint**: 61% sell-through (target: 60%) → **No markdown** needed ✅
- **Weeks 7-12**: Continue weekly replenishment, inventory depletes as planned
- **Week 12 end**: Sold 7,800 units (97.5% of forecast), MAPE: 12% ✅

**Result**: Full margin preserved, no markdowns, minimal leftover inventory

---

### Scenario 2: High Demand - Re-Forecast Triggered

**Setup**: 8,000 forecast → 9,600 manufactured

**What Happened**:
- **Week 1**: Actual sales 850 (forecast: 650) → **+31% variance** ⚠️
- **Re-forecast triggered**: Updated forecast → 10,500 units
- **Problem**: Only have 9,600 manufactured → Expected stockout by Week 8
- **Action**: Emergency reorder 2,000 units (air freight, 4-week lead time)
- **Week 6**: 68% sell-through (target: 60%) → Ahead of target, no markdown
- **Emergency units arrive Week 6**: Continue replenishment to high-performing stores
- **Week 12 end**: Sold 10,200 units, leftover 1,400 units

**Result**: System adapted quickly, captured unexpected demand, avoided major stockouts

---

### Scenario 3: Low Demand - Markdown Applied

**Setup**: 8,000 forecast → 9,600 manufactured

**What Happened**:
- **Weeks 1-6**: Actual sales consistently 10-15% below forecast
- **Week 6 checkpoint**: 52% sell-through (target: 60%) → **-8% below target** ⚠️
- **Markdown decision**:
  - Fashion_Forward: 58% sell-through → **15% markdown**
  - Mainstream: 50% sell-through → **30% markdown**
  - Value_Conscious: 40% sell-through → **50% markdown**
- **Re-forecast triggered**: Adjust weeks 7-12 with new prices
- **Weeks 7-12**: Sales lift +18% post-markdown
- **Week 12 end**: Sold 7,200 units, leftover 2,400 units

**Result**: Cluster-differentiated markdowns accelerated sell-through, recovered margin, avoided larger overstock

---

## Quick Reference

### Key Decision Thresholds (Archetype 1 - Fashion)

| Decision | Threshold | Action |
|----------|-----------|--------|
| **Re-forecast** | Variance > 20% | Run updated category forecast |
| **Human review** | Confidence < 70% | Require approval before manufacturing |
| **Markdown** | Sell-through < 60% at Week 6 | Apply cluster-specific markdowns |
| **Emergency order** | Variance > 30% | Alert + recommend air freight order |

### Data Flow Between Agents

```
DEMAND AGENT
    ↓ (forecast: 8,000 units, cluster %, store factors)
INVENTORY AGENT
    ↓ (manufacturing order: 9,600, allocations by store)
PRICING AGENT
    ↓ (markdown decisions, sell-through analysis)
DEMAND AGENT (re-forecast if markdown applied)
```

---

**Document Owner**: Independent Study Project
**Last Updated**: 2025-10-11
**Version**: 3.1
**Related Documents**:
- [Product Brief v3.1](product_brief_v3.1.md) - System overview, business value, agent details
- [Key Parameters](../../05_Progress_Reports/Weekly_Supervisor_Meetings/key_parameter.md)
