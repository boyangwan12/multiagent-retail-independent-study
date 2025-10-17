# Operational Workflow: 3-Agent Parameter-Driven System

**Version:** 3.3
**Date:** 2025-10-16
**Status:** Parameter-Driven Workflow Guide with Agent Reasoning Examples
**Scope:** Zara-Style Fast Fashion Test Scenario (Parameter-Driven MVP)

> **Note**: For system overview, business value, and agent responsibilities, see [Product Brief v3.3](product_brief_v3.3.md).
> This document focuses on **how the system adapts operationally** based on user-provided parameters with concrete agent reasoning examples.

---

## Table of Contents

1. [Key Concept: Parameter-Driven Agent Adaptation](#key-concept-parameter-driven-agent-adaptation)
2. [The 5 Key Parameters](#the-5-key-parameters)
3. [6-Phase Operational Workflow](#6-phase-operational-workflow)
   - [Phase 0: Parameter Gathering](#phase-0-parameter-gathering-new-in-v33)
   - [Phase 1-5: Forecast & Execution](#phases-1-5-forecast--execution)
4. [Example Scenarios](#example-scenarios)
5. [Quick Reference](#quick-reference)

---

## Key Concept: Parameter-Driven Agent Adaptation

### What's Different in v3.3: No Hardcoded Archetypes

**v3.2 Approach (Hardcoded):**
- Fixed "Archetype 1" parameters (12 weeks, 45% holdback, weekly replenishment, Week 6 markdown)
- Agents followed predefined logic paths
- Changing behavior required code modifications

**v3.3 Approach (Parameter-Driven):**
- User describes season planning in natural language
- LLM extracts 5 key parameters
- Agents autonomously reason about how parameters affect their behavior
- Same code adapts to any retail scenario

**Example: Zara-Style Fast Fashion (Test Scenario)**

User input:
```
"I'm planning a 12-week spring fashion season starting March 1st.
Send all inventory to stores at launch with no DC holdback.
I don't want ongoing replenishment - just one initial allocation.
Check for markdown opportunities at week 6 if we're below 60% sell-through."
```

System extracts parameters:
- Forecast horizon: 12 weeks
- Season length: 2025-03-01 to 2025-05-23
- Replenishment strategy: None (one-shot allocation)
- DC holdback: 0% (100% initial to stores)
- Markdown checkpoint: Week 6, 60% threshold

Agents adapt:
- **Demand Agent**: *"No replenishment means I can't correct errors later. Increase safety stock to 25%."*
- **Inventory Agent**: *"0% holdback means allocate everything at Week 0. Skip replenishment phase."*
- **Pricing Agent**: *"Monitor until Week 6, apply Gap × Elasticity if <60%."*

---

## Forecast Once, Allocate with Math (Technical Approach)

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

## The 5 Key Parameters

### How Parameters Drive Agent Behavior

Instead of hardcoded "Archetype 1" logic, users describe their season planning in natural language. The system extracts 5 parameters, and agents reason about how to adapt.

### Parameter 1: Forecast Horizon
**What it is**: How many weeks ahead to predict demand

**Zara Example**: "12 weeks"
- Agent reasoning: *"12-week horizon is short. Use weekly granularity for demand curve. Focus on recent historical trends (last 12 months)."*

**Alternative Example (Furniture)**: "26 weeks"
- Agent reasoning: *"26-week horizon is longer. Use bi-weekly granularity for smoother demand curve. Include 24-month historical trends."*

### Parameter 2: Season Length
**What it is**: Start and end dates for the planning period

**Zara Example**: "2025-03-01 to 2025-05-23 (12 weeks)"
- Agent reasoning: *"Spring season starts March 1st. Check historical spring trends. Manufacturing order needs to be placed by September 1st (6 months prior)."*

### Parameter 3: Replenishment Strategy
**What it is**: How often (if at all) to send additional inventory from DC to stores

**Zara Example**: "No replenishment - one-shot allocation"
- **Demand Agent** reasoning: *"No replenishment means I can't correct forecast errors later. Increase safety stock from default 20% to 25%."*
- **Inventory Agent** reasoning: *"No replenishment phase needed. Allocate 100% of manufacturing order at Week 0. Skip weekly replenishment loop entirely."*

**Alternative (Standard Retail)**: "Weekly replenishment"
- **Demand Agent**: *"Weekly corrections available. Use default 20% safety stock."*
- **Inventory Agent**: *"Plan for weekly shipments. Keep holdback at DC for flexibility."*

### Parameter 4: DC Holdback Strategy
**What it is**: What percentage of inventory to keep at DC vs. send to stores initially

**Zara Example**: "0% holdback - send 100% to stores at launch"
- **Inventory Agent** reasoning: *"0% holdback combined with no replenishment means aggressive push to stores. Calculate precise store allocations using hierarchical method (cluster → store). Ship everything at Week 0."*

**Alternative (Conservative)**: "65% DC holdback"
- **Inventory Agent**: *"High holdback gives flexibility for reallocation. Send only 35% initially. Plan bi-weekly replenishments from DC reserve."*

### Parameter 5: Markdown Timing
**What it is**: When to check sell-through and potentially apply markdowns

**Zara Example**: "Week 6 checkpoint, 60% sell-through threshold"
- **Pricing Agent** reasoning: *"Monitor until Week 6. At Week 6, check: (actual / manufactured). If <60%, calculate Gap × Elasticity markdown. If ≥60%, no action needed."*

**Alternative (Luxury)**: "No markdowns - premium positioning"
- **Pricing Agent**: *"No markdown parameter specified. Remain idle throughout season. No pricing adjustments."*

**Alternative (Furniture)**: "Week 12 checkpoint, 50% threshold"
- **Pricing Agent**: *"Later checkpoint with lower threshold. Conservative markdown strategy. Wait until Week 12 to evaluate."*

---

## Parameter Configuration (Old Archetype 1 Reference - Deprecated)

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

## 6-Phase Operational Workflow

| Phase | Timing | Key Actions | Output |
|-------|--------|-------------|--------|
| **0. Parameter Gathering** ⭐ NEW | Before workflow starts | User describes planning approach → LLM extracts parameters → Agents receive context | 5 parameters extracted |
| **1. Pre-Season** | Week -24 (6 months before) | Agents reason about parameters → Ensemble forecast → Calculate manufacturing order | Order quantity (parameter-adjusted) |
| **2. Season Start** | Week 0 | K-means clustering → Hierarchical allocation (adjusted for DC holdback parameter) | Initial shipment (varies by parameters) |
| **3. In-Season** | Weeks 1-N (cadence varies) | Monitor actuals → Conditional replenishment (may be skipped if parameter says "none") | Replenishment (if configured) |
| **4. Mid-Season** | Week N (parameter-driven) | Check sell-through → Conditional markdown (may be skipped) | Markdown (if configured) + re-forecast |
| **5. Season End** | Post-season | Analyze performance → Tune parameters for next run | Updated parameters |

---

### PHASE 0: Parameter Gathering (NEW in v3.3)

**Goal**: Extract 5 key parameters from user's natural language input

**User Experience**:

1. **User inputs free-form text**:
   ```
   "I'm planning a 12-week spring fashion season starting March 1st.
   Send all inventory to stores at launch with no DC holdback.
   I don't want ongoing replenishment - just one initial allocation.
   Check for markdown opportunities at week 6 if we're below 60% sell-through."
   ```

2. **System processes via LLM** (backend API):
   - Endpoint: `POST /api/parameters/extract`
   - LLM: Azure OpenAI gpt-4o-mini
   - Prompt: Extract structured parameters from natural language

3. **Extracted parameters**:
   ```json
   {
     "forecast_horizon_weeks": 12,
     "season_start_date": "2025-03-01",
     "season_end_date": "2025-05-23",
     "replenishment_strategy": "none",
     "dc_holdback_percentage": 0.0,
     "markdown_checkpoint_week": 6,
     "markdown_threshold": 0.60
   }
   ```

4. **Confirmation modal** (frontend):
   - User reviews extracted parameters
   - Can edit if needed
   - Clicks "Confirm & Start Workflow"

5. **Parameter distribution**:
   - Orchestrator receives parameters
   - Passes parameter context to each agent via handoff objects
   - Agents receive full parameter context when invoked

**Agent Reasoning Based on Parameters**:

**Demand Agent receives:**
```json
{
  "forecast_horizon_weeks": 12,
  "replenishment_strategy": "none"
}
```
**Agent reasons**: *"No replenishment means I can't correct errors later. Increase safety stock to 25% (from default 20%)."*

**Inventory Agent receives:**
```json
{
  "dc_holdback_percentage": 0.0,
  "replenishment_strategy": "none"
}
```
**Agent reasons**: *"0% holdback + no replenishment = allocate everything at Week 0. Skip replenishment phase entirely."*

**Pricing Agent receives:**
```json
{
  "markdown_checkpoint_week": 6,
  "markdown_threshold": 0.60
}
```
**Agent reasons**: *"Monitor until Week 6. If sell-through <60%, apply Gap × Elasticity markdown."*

**Output**: All agents have parameter context for autonomous reasoning

---

### PHASE 1: Pre-Season Planning (Week -24)

**Goal**: Forecast demand and commit to manufacturing order (with parameter-driven adjustments)

**Agent Reasoning (Zara Example)**:

**Demand Agent receives parameters:**
- `replenishment_strategy`: "none"
- `forecast_horizon_weeks`: 12

**Agent LLM reasoning**:
*"User specified no replenishment strategy. This means I cannot correct forecast errors through periodic restocking. To compensate, I should increase safety stock buffer from the default 20% to 25% to reduce stockout risk."*

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

4. **Inventory Agent** receives parameters:
   - `replenishment_strategy`: "none"
   - `dc_holdback_percentage`: 0.0

**Inventory Agent LLM reasoning**:
*"No replenishment configured and 0% DC holdback. This is an aggressive all-in strategy. I'll use increased safety stock (25% from Demand Agent). Manufacturing order = 8,000 × 1.25 = 10,000 units. All inventory will be allocated to stores at Week 0."*

**Decision**: Manufacturing Order (Parameter-Adjusted)

```
Ensemble forecast: 8,000 dresses (Prophet 8,200 + ARIMA 7,800)
Safety stock: 25% (adjusted from 20% due to no replenishment)
Manufacturing order: 8,000 × 1.25 = 10,000 dresses

→ Human review required (Modify/Accept approval modal)
→ Upon acceptance, send to manufacturer
```

**Comparison to Standard Retail Parameters**:
```
IF replenishment_strategy = "weekly" AND dc_holdback_percentage = 0.45:
  Safety stock: 20% (default)
  Manufacturing order: 8,000 × 1.20 = 9,600 units
  Initial shipment: 9,600 × 0.55 = 5,280 units
  DC holdback: 9,600 × 0.45 = 4,320 units
```

---

### PHASE 2: Season Start (Week 0)

**Goal**: Allocate manufacturing order to 50 stores (parameter-driven)

**Inventory Agent receives parameters:**
- `dc_holdback_percentage`: 0.0
- `replenishment_strategy`: "none"
- Manufacturing order from Phase 1: **10,000 units**

**Agent LLM reasoning**:
*"DC holdback is 0% and no replenishment configured. This means 100% of inventory goes to stores immediately. I'll use hierarchical allocation (cluster → store) to distribute all 10,000 units at Week 0. No DC reserve needed since there's no replenishment phase."*

**Steps**:
1. **Inventory Agent**: Allocate to clusters
   - Fashion_Forward: 10,000 × 40% = **4,000 units**
   - Mainstream: 10,000 × 35% = **3,500 units**
   - Value_Conscious: 10,000 × 25% = **2,500 units**

2. **Inventory Agent**: Allocate within clusters to stores
   - Store_01: 4,000 × 5.5% = **220 units** (season total)
   - Store_02: 4,000 × 5.0% = **200 units**
   - ... (48 more stores)

3. **Inventory Agent**: Apply holdback parameter (Zara: 0%)
   - Store_01 initial: 220 × 100% = **220 units** (ship everything now)
   - Store_01 DC holdback: 220 × 0% = **0 units** (no DC reserve)

**Result (Zara Parameters)**:
- **10,000 units shipped to stores** (100%)
- **0 units held at DC** (0%) - no replenishment reserve

**Comparison to Standard Retail Parameters**:
```
IF dc_holdback_percentage = 0.45 (45% holdback):
  Manufacturing order: 9,600 units (20% safety stock)
  Initial shipment: 9,600 × 0.55 = 5,280 units to stores
  DC holdback: 9,600 × 0.45 = 4,320 units for replenishment
```

---

### PHASE 3: In-Season Monitoring & Conditional Replenishment

**Goal**: Monitor sales performance and conditionally top-up stores (parameter-driven)

**⚡ Parameter Check (Phase May Be Skipped Entirely)**

**Inventory Agent receives parameters:**
- `replenishment_strategy`: "none" OR "weekly" OR "bi-weekly"
- `dc_holdback_percentage`: 0.0 (Zara) OR 0.45 (Standard)

**Agent LLM reasoning (Zara Example - NO REPLENISHMENT)**:
*"Replenishment strategy is 'none' and DC holdback is 0%. All inventory was shipped to stores at Week 0. There is no DC reserve to draw from, and user explicitly requested no replenishment. Skip this phase entirely. Move directly to Phase 4 (Markdown checkpoint at Week 6)."*

**Result for Zara Parameters**:
- ❌ **Phase 3 skipped entirely**
- 0 units available at DC for replenishment
- Stores operate with initial allocation only (10,000 units total)
- No weekly replenishment loops executed

---

**Alternative: Standard Retail with Weekly Replenishment**

**IF replenishment_strategy = "weekly" AND dc_holdback_percentage = 0.45:**

**Agent LLM reasoning**:
*"Weekly replenishment configured with 45% DC holdback. I have 4,320 units at DC (from Phase 2). Monitor store inventory weekly and ship top-ups from DC reserve using simple forecast - inventory formula."*

**Replenishment Logic (for each store, every week)**:

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

**Example (Store_01, Week 2 - Standard Retail)**:
- Season total allocation: 105 units
- Initial shipment (Week 0): 105 × 55% = **58 units**
- DC holdback: 105 × 45% = **47 units**
- Week 2 calculation:
  - Remaining allocation: 105 - 58 = 47 units
  - Weeks remaining: 10
  - Next week forecast: 47 / 10 = **4.7 units/week**
  - Current inventory: 2 units
  - **Replenishment**: max(0, 4.7 - 2) = **2.7 → 3 units**

**If actuals are significantly off**: Orchestrator detects >20% variance and triggers re-forecast, which updates remaining allocations.

---

**Comparison Summary**:

| Parameter Set | Phase 3 Behavior | DC Reserve | Weekly Actions |
|---------------|------------------|------------|----------------|
| **Zara** (no replenishment, 0% holdback) | ❌ Skip phase entirely | 0 units | None - stores use initial allocation only |
| **Standard Retail** (weekly, 45% holdback) | ✅ Execute weekly loops | 4,320 units | Monitor + calculate + ship top-ups |

---

### PHASE 4: Mid-Season Pricing & Conditional Markdown

**Goal**: Check sell-through at parameter-driven checkpoint and conditionally apply markdown

**⚡ Parameter Check (Phase May Be Skipped)**

**Pricing Agent receives parameters:**
- `markdown_checkpoint_week`: 6 (Zara) OR null (Luxury - no markdowns)
- `markdown_threshold`: 0.60 (60% target)

**Agent LLM reasoning (Zara Example - CONDITIONAL MARKDOWN)**:
*"Markdown checkpoint configured for Week 6 with 60% threshold. At Week 6, I'll calculate actual sell-through: (Total_Sold / Total_Manufactured). If <60%, apply Gap × Elasticity formula (elasticity=2.0). If ≥60%, no markdown needed - system is on track."*

---

**Scenario A: Zara Parameters - Week 6, Sell-Through 58% (Below Target)**

**Pricing Agent calculates:**
```python
1. Calculate sell-through rate
   Total manufactured: 10,000 units
   Total sold (Weeks 0-6): 5,800 units
   Sell-through: 5,800 / 10,000 = 58%

2. Check against threshold
   Target: 60% (from parameters)
   Actual: 58%
   Result: ⚠️ Below target by 2 percentage points

3. Calculate gap
   Gap = 0.60 - 0.58 = 0.02 (2 percentage points)

4. Apply Gap × Elasticity formula
   elasticity_coefficient = 2.0  # Tunable
   markdown_raw = gap × elasticity_coefficient
   markdown_raw = 0.02 × 2.0 = 0.04 (4%)

   # Round to nearest 5%
   markdown_rounded = round(0.04 × 20) / 20 = 0.05 → 5%

   # Cap at 40%
   markdown_depth = min(0.05, 0.40) = 5%

5. Apply uniform markdown (no cluster differentiation)
   ALL 50 stores: 5% markdown

6. Trigger re-forecast
   Hand off to Demand Agent: Re-forecast weeks 7-12 with new prices
   Update remaining weeks' demand curve based on 5% price reduction
```

**Pricing Agent LLM reasoning**:
*"58% sell-through at Week 6 is below 60% target. Gap = 2 percentage points. Apply Gap × Elasticity: 2% × 2.0 = 4% → rounds to 5%. Apply 5% uniform markdown to all stores. Hand off to Demand Agent for re-forecast of remaining weeks with new pricing."*

**Result**: 5% markdown applied uniformly, re-forecast triggered for weeks 7-12

---

**Scenario B: Zara Parameters - Week 6, Sell-Through 63% (Above Target)**

**Pricing Agent calculates:**
```python
1. Calculate sell-through rate
   Total manufactured: 10,000 units
   Total sold (Weeks 0-6): 6,300 units
   Sell-through: 6,300 / 10,000 = 63%

2. Check against threshold
   Target: 60% (from parameters)
   Actual: 63%
   Result: ✅ Above target (negative gap)

3. Calculate gap
   Gap = 0.60 - 0.63 = -0.03 (negative gap)

4. Agent decision
   IF gap < 0:
       NO MARKDOWN NEEDED (ahead of target)
       SKIP Gap × Elasticity formula
       SKIP re-forecast
```

**Pricing Agent LLM reasoning**:
*"63% sell-through at Week 6 exceeds 60% target. Negative gap means we're ahead of plan. No markdown action needed. Continue monitoring through end of season. No re-forecast required."*

**Result**: ❌ No markdown applied, system continues with original forecast

---

**Scenario C: Alternative Parameters - Luxury Brand (No Markdowns)**

**Pricing Agent receives parameters:**
```json
{
  "markdown_checkpoint_week": null,
  "markdown_threshold": null
}
```

**Agent LLM reasoning**:
*"No markdown checkpoint configured. User specified luxury positioning with no markdowns. Remain idle throughout season - skip Phase 4 entirely. No pricing adjustments."*

**Result**: ❌ **Phase 4 skipped entirely** - premium pricing maintained

---

**Additional Markdown Examples (Different Gaps)**:

| Sell-Through | Target | Gap | Markdown Raw | Rounded | Final Markdown |
|--------------|--------|-----|--------------|---------|----------------|
| 58% | 60% | 2pp | 4% | 5% | **5%** |
| 55% | 60% | 5pp | 10% | 10% | **10%** |
| 50% | 60% | 10pp | 20% | 20% | **20%** |
| 40% | 60% | 20pp | 40% | 40% | **40% (capped)** |
| 63% | 60% | -3pp (negative) | N/A | N/A | **No markdown** ✅ |

**Key Changes from v3.1**:
- **Added**: Parameter-driven checkpoint timing (not hardcoded to Week 6)
- **Added**: Conditional phase execution (may be skipped if no markdown configured)
- **Removed**: Fixed markdown table (15%/30%/50%)
- **Added**: Gap × Elasticity formula (elasticity=2.0, tunable)
- **Removed**: Cluster-specific markdown differentiation (uniform across all stores)

---

**Comparison Summary**:

| Parameter Set | Phase 4 Behavior | Checkpoint Week | Action if Below Target |
|---------------|------------------|-----------------|------------------------|
| **Zara** (Week 6, 60% threshold) | ✅ Execute conditional markdown | Week 6 | Apply Gap × Elasticity (5%-40%) |
| **Luxury** (no markdown configured) | ❌ Skip phase entirely | N/A | None - maintain premium pricing |
| **Furniture** (Week 12, 50% threshold) | ✅ Execute at Week 12 | Week 12 | Later checkpoint, lower threshold |

---

### PHASE 5: Season End Analysis & Parameter Tuning

**Goal**: Evaluate performance against the 5 key parameters and tune for next season

**Key Metrics (Parameter-Aware)**:

```
Forecast Accuracy:
├─ MAPE (Mean Absolute Percentage Error): Target <20%
├─ Bias: Over/under-forecasting tendency (target ±5%)
└─ Re-forecast Trigger Accuracy: 90%+ (correctly identify >20% variance)

Business Impact (Parameter-Dependent):
├─ Stockout events: Count and lost sales estimate (critical for no-replenishment strategies)
├─ Overstock: Final inventory value (affected by safety stock % and holdback strategy)
├─ Markdown costs: Total discount impact (dependent on markdown threshold)
└─ Inventory turnover: vs. prior year (varies by replenishment + holdback parameters)

System Performance:
├─ Workflow runtime: Target <60 seconds (full 3-agent workflow)
├─ Human approval rate: Track % modify vs. accept
└─ Agent reasoning quality: Manual review of LLM decision logs
```

**Note**: Confidence calibration removed in v3.2 (no confidence scoring)

---

**Parameter Tuning Framework (v3.3 - Parameter-Driven)**

Instead of hardcoded parameter adjustments, the system now analyzes performance relative to the 5 key parameters and suggests data-driven refinements.

---

**Tuning Example 1: Zara Parameters - Excessive Stockouts**

**Performance Data**:
- **Forecast MAPE**: 18% (acceptable)
- **Stockout events**: 12 stores ran out by Week 8 (❌ problematic)
- **Lost sales estimate**: ~850 units (~8.5% of forecast)
- **Overstock**: Minimal (only 200 units remaining)

**Analysis by Parameter**:

| Parameter | Current Value | Performance Impact | Tuning Recommendation |
|-----------|---------------|-------------------|----------------------|
| **Safety Stock** | 25% (already elevated due to no replenishment) | Stockouts occurred despite elevated safety stock | ⬆️ Increase to 28% for next season |
| **Replenishment Strategy** | "none" (one-shot allocation) | No ability to correct after Week 0 | Consider "bi-weekly light replenishment" OR maintain "none" with higher safety stock |
| **DC Holdback** | 0% | All inventory shipped at Week 0, no flexibility | IF switching to replenishment: Increase to 15-20% holdback |
| **Forecast Horizon** | 12 weeks | Adequate (MAPE 18%) | No change needed |
| **Markdown Timing** | Week 6, 60% threshold | Not triggered (63% sell-through) | No change needed |

**Recommended Parameter Set for Next Season**:
```json
{
  "forecast_horizon_weeks": 12,
  "replenishment_strategy": "none",
  "dc_holdback_percentage": 0.0,
  "safety_stock_multiplier": 1.28,  // ⬆️ Increased from 1.25
  "markdown_checkpoint_week": 6,
  "markdown_threshold": 0.60
}
```

**Alternative: Shift to Light Replenishment**:
```json
{
  "replenishment_strategy": "bi-weekly",  // Changed from "none"
  "dc_holdback_percentage": 0.20,          // Changed from 0.0
  "safety_stock_multiplier": 1.20          // ⬇️ Reduced from 1.25
}
```

---

**Tuning Example 2: Zara Parameters - Excessive Overstock**

**Performance Data**:
- **Forecast MAPE**: 22% (⚠️ above target)
- **Overstock**: 2,800 units remaining (28% of manufactured)
- **Markdown costs**: 15% applied at Week 6, recovered some sales
- **Stockout events**: 0 (good, but over-compensated)

**Analysis by Parameter**:

| Parameter | Current Value | Performance Impact | Tuning Recommendation |
|-----------|---------------|-------------------|----------------------|
| **Safety Stock** | 25% | Too conservative, contributed to overstock | ⬇️ Reduce to 22% for next season |
| **Markdown Timing** | Week 6, 60% threshold | Applied 15% markdown, but too late | ⬆️ Move checkpoint to Week 5 OR ⬆️ raise threshold to 65% |
| **Markdown Threshold** | 60% | Triggered markdown when at 52% sell-through | Consider 65% threshold for earlier intervention |
| **Replenishment Strategy** | "none" | No ability to reduce allocation mid-season | No change (consistent with Zara model) |
| **Forecast Method** | Ensemble Prophet + ARIMA | MAPE 22% suggests model drift | Re-train models with recent data, check seasonality |

**Recommended Parameter Set for Next Season**:
```json
{
  "safety_stock_multiplier": 1.22,     // ⬇️ Reduced from 1.25
  "markdown_checkpoint_week": 5,        // ⬆️ Earlier from Week 6
  "markdown_threshold": 0.65            // ⬆️ Higher threshold from 0.60
}
```

---

**Tuning Example 3: Standard Retail Parameters - Replenishment Underutilized**

**Performance Data**:
- **DC holdback**: 45% (4,320 units reserved)
- **Replenishment execution**: Only 1,850 units shipped from DC over 12 weeks (43% utilization)
- **DC overstock**: 2,470 units left at DC (57% wasted)

**Analysis by Parameter**:

| Parameter | Current Value | Performance Impact | Tuning Recommendation |
|-----------|---------------|-------------------|----------------------|
| **DC Holdback** | 45% | Too high, DC inventory underutilized | ⬇️ Reduce to 30-35% |
| **Initial Allocation** | 55% | Too conservative, stores could handle more upfront | ⬆️ Increase to 65-70% |
| **Replenishment Strategy** | "weekly" | Frequency appropriate, but volume too low | No change to cadence |
| **Replenishment Formula** | `forecast - inventory` | Formula is fine, but initial allocation was too low | Adjust initial % instead of formula |

**Recommended Parameter Set for Next Season**:
```json
{
  "dc_holdback_percentage": 0.35,   // ⬇️ Reduced from 0.45
  "initial_allocation": 0.65,        // ⬆️ Increased from 0.55
  "replenishment_strategy": "weekly" // No change
}
```

---

**Tuning Example 4: Luxury Brand - Consider Adding Markdown Capability**

**Performance Data**:
- **Markdown strategy**: "none" (luxury positioning)
- **Season end overstock**: 3,200 units (32% of manufactured)
- **Final inventory value**: $480,000 at cost
- **Lost margin**: Holding costs + clearance sales offline

**Analysis by Parameter**:

| Parameter | Current Value | Performance Impact | Tuning Recommendation |
|-----------|---------------|-------------------|----------------------|
| **Markdown Timing** | null (no markdowns) | 32% overstock with no mechanism to accelerate sales | Consider **Week 10 checkpoint, 40% threshold** (late + conservative) |
| **Safety Stock** | 20% (default) | Appropriate for forecast accuracy | No change |
| **Replenishment Strategy** | "bi-weekly" | Worked well, minimal stockouts | No change |

**Recommended Parameter Set for Next Season**:
```json
{
  "markdown_checkpoint_week": 10,        // NEW - late checkpoint
  "markdown_threshold": 0.40,            // NEW - low threshold (conservative)
  "markdown_elasticity": 1.5,            // NEW - gentler markdowns than default 2.0
  "markdown_cap": 0.20                   // NEW - cap at 20% (vs. default 40%)
}
```

---

**Parameter Tuning Output for Next Season**:

The system generates a JSON file with recommended parameter updates:

```json
{
  "season_id": "2025_spring_zara",
  "performance_summary": {
    "forecast_mape": 18.2,
    "stockout_count": 12,
    "overstock_units": 200,
    "markdown_triggered": false
  },
  "recommended_parameters": {
    "forecast_horizon_weeks": 12,
    "season_start_date": "2026-03-01",
    "season_end_date": "2026-05-23",
    "replenishment_strategy": "none",
    "dc_holdback_percentage": 0.0,
    "safety_stock_multiplier": 1.28,
    "markdown_checkpoint_week": 6,
    "markdown_threshold": 0.60
  },
  "tuning_rationale": {
    "safety_stock": "Increased from 1.25 to 1.28 due to 12 stockout events",
    "replenishment_strategy": "Maintained 'none' (consistent with Zara model)",
    "dc_holdback": "Maintained 0% (no replenishment configured)"
  }
}
```

**User reviews recommendations** → **Confirms or adjusts** → **Saves for next season**

---

**Key Insight for v3.3**:

Parameter tuning is now **data-driven and parameter-aware**. Instead of ad-hoc adjustments, the system:
1. Measures performance relative to the 5 key parameters
2. Identifies which parameters contributed to issues
3. Suggests targeted adjustments with reasoning
4. Allows user to accept/modify/reject recommendations

This closes the loop: **Parameter-driven execution** → **Performance analysis** → **Parameter refinement** → **Next season**

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
