# Operational Workflow: When to Run the Model & What Decisions to Make

## Overview

Last week, we found that demand forecasting is a complex problem, we need to break down the problem into specific type of retail business model to define what we are forecasting for. In order to do this, we need to define operational cadence and business decisions for each retail business model.

to generalize the business model, there are 3 types:
### Seasonal Fashion Retail
- **Examples**: Zara, H&M, Forever 21
- **Characteristics**:
  - Short seasons (8-12 weeks)
  - 70-80% new products per season
  - Long lead times (3-6 months from Asia)
  - High fashion volatility
- **Forecasting Approach**: Adaptive methods with high similar-item matching usage
- **Inventory Strategy**: Hold 45-55% at DC, aggressive early allocation
- **Pricing Strategy**: Markdown at Week 6 if <60% sell-through

### Stable Catalog Retail ⭐ **[MVP FOCUS]**
- **Examples**: furniture, home décor, kitchenware, lighting, and bedding retailers
- **Characteristics**:
  - Medium seasons (6-12 months, typically 26 weeks)
  - 20-30% new products per season (new colors/materials of existing styles)
  - Medium lead times (2-4 months, often from Asia)
  - Stable demand patterns with predictable seasonality
- **Forecasting Approach**: Adaptive methods (similar-item matching, time-series, hybrid)
- **Inventory Strategy**: Hold 60-70% at DC, conservative initial allocation
- **Pricing Strategy**: Markdown at Week 12 if <50% sell-through

**Why Archetype 2 for MVP:**
- ✅ **Moderate complexity**: Not as volatile as fashion, not as simple as CPG
- ✅ **Clear validation**: 26-week seasons allow full-cycle testing
- ✅ **High business value**: Furniture retail has significant overstock/stockout problems (PP-028)
- ✅ **Addresses key pain points**: PP-001 (inaccurate forecasting), PP-002 (allocation failures), PP-028 (inventory balance)
- ✅ **Professor's guidance**: "Focus on initial allocation" - furniture is classic use case

### Continuous Replenishment Retail
- **Examples**: Walmart (CPG), Costco, grocery chains
- **Characteristics**:
  - No seasons (continuous replenishment)
  - 5-10% new products annually
  - Short lead times (days to weeks)
  - Predictable demand
- **Forecasting Approach**: Adaptive methods with high time-series usage
- **Inventory Strategy**: Hold 80-90% at DC, minimal store allocation
- **Pricing Strategy**: Rare markdowns; focus on stock rotation

---

## Phase 1: Pre-Season Planning (3 Months Before)

### When to Run
- **Timing**: 3 months before season start (e.g., July for October launch)
- **Frequency**: Once initially, optional monthly updates
- **Runtime**: 2-4 hours (first run includes similar-item matching)

### What We Predict
```
SKU: "Mid-Century Sofa - Charcoal"
Prediction Matrix (50 stores × 26 weeks):

         Week1  Week2  Week3  ...  Week26
Store1     5      8      6          1
Store2     3      4      5          0
Store3     8     12     10          2
...
Store50    4      6      5          1

Derived Totals:
- Total Season Demand: 3,200 units
- Weekly Curve: [250, 280, 260, 240, 220, 200, 190, 180, 170, 160, 150, 140, ...]
```

### Decision #1: Manufacturing Order
**Decision**: How many units to manufacture?

**Calculation**:
```python
total_demand = sum(demand_by_store_by_week)  # 3,200 units
safety_stock = total_demand * safety_stock_percentage  # 3,200 * 0.15 = 480
manufacturing_order = total_demand + safety_stock  # 3,680 units
```

**Business Impact**:
- ~$32,000 commitment (3,680 units × $8.70/unit)
- Lead time: 2-4 months from Asian supplier
- Cannot easily adjust once ordered

**Human Review**:
- Merchandiser reviews forecast vs. trend predictions
- Adjusts if market intelligence suggests different demand
- Final approval before placing order

---

## Phase 2: Season Start - Initial Allocation (Week -1)

### When to Run
- **Timing**: 1 week before season launch
- **Purpose**: Confirm forecast hasn't changed significantly
- **Runtime**: 30 minutes (similar-items already matched)

### Decision #2: Week 0 Initial Allocation
**Decision**: How many units to send to each store for Weeks 1-2?

**Strategy**: **Conservative Allocation** (hold back 65% inventory at DC)

**Calculation**:
```python
# For each store, send first 2 weeks forecasted demand (bi-weekly cadence)
for store in stores:
    week_1_2_allocation[store] = sum(demand_by_store_by_week[store][0:2])

total_allocated_week_1_2 = sum(week_1_2_allocation)  # e.g., 530 units (35%)
inventory_held_at_dc = manufacturing_order - total_allocated_week_1_2  # 3,150 units (65%)
```

**Why Hold Back?**
- Stable catalog retail: **60-70% held at DC** (longer selling window than fashion)
- Bi-weekly replenishment means stores need 2 weeks of inventory
- Avoids expensive store-to-store transfers later

**Example**:
```
Initial Allocation (Week 0):
- Store 1: 13 units (weeks 1-2 forecast: 5+8)
- Store 2: 7 units (weeks 1-2 forecast: 3+4)
- Store 3: 20 units (weeks 1-2 forecast: 8+12)
...
- Total sent to stores: 1,280 units (35%)
- Held at DC: 2,400 units (65%)
```

---

## Phase 3: In-Season Operations (Bi-weekly, Weeks 1-26)

### When to Run
- **Timing**: Every other Monday morning during season (bi-weekly cycle)
- **Trigger**: Automated (scheduled task)
- **Alternative Trigger**: Variance-triggered (if actual sales > 15% off forecast)
- **Runtime**: 30 minutes

### Bi-weekly Monitoring Cycle

**Bi-weekly Monday Morning**:
1. **Ingest actual sales data** from previous 2 weeks
2. **Re-run forecast** for remaining weeks
3. **Compare actuals vs. forecast**
4. **Flag variances** > threshold (e.g., 15%)

**Example (Week 4 Monday - after 2 weeks)**:
```python
# Actual sales Weeks 1-2
actual_weeks_1_2 = get_sales_data(weeks=[1,2])  # {store_1: 13, store_2: 7, store_3: 20, ...}

# Forecasted Weeks 1-2
forecast_weeks_1_2 = sum(demand_by_store_by_week[:, 0:2])  # {store_1: 13, store_2: 7, store_3: 20, ...}

# Calculate variance
variance = (actual_weeks_1_2 - forecast_weeks_1_2) / forecast_weeks_1_2
# Store 1: (15-13)/13 = +15% ⚠️ (selling faster than expected)
# Store 2: (6-7)/7 = -14% (slight under-performance)
# Store 3: (23-20)/20 = +15% ⚠️
```

### Decision #3: Bi-weekly Replenishment
**Decision**: How many units to replenish each store from DC?

**Calculation**:
```python
for store in stores:
    # Check current inventory
    current_inventory = get_store_inventory(store)

    # Forecasted demand for next 2 weeks
    next_2_weeks_forecast = sum(demand_by_store_by_week[store][current_week:current_week+2])

    # Replenishment need
    replenishment_qty = max(0, next_2_weeks_forecast - current_inventory)

    # Safety stock buffer (optional)
    safety_buffer = next_2_weeks_forecast * 0.15
    replenishment_qty += safety_buffer

    # Ship from DC
    replenish_from_dc(store, replenishment_qty)
```

**Example (Week 4 Bi-weekly Replenishment)**:
```
Store 1:
- Current inventory: 3 units (sold 15 over 2 weeks, received 13 initially, sold 5 more)
- Weeks 3-4 forecast: 6+7 = 13 units
- Replenishment: 13 - 3 = 10 units + 2 safety = 12 units shipped from DC

Store 2:
- Current inventory: 5 units (sold 6, received 7, sold 2)
- Weeks 3-4 forecast: 5+6 = 11 units
- Replenishment: 11 - 5 = 6 units + 1.7 safety = 8 units shipped from DC
```

### Decision #4: Optional Model Re-run (Variance-Triggered)
**Decision**: Should we re-run the forecast between bi-weekly cycles?

**Trigger**:
```python
if variance > variance_threshold:  # e.g., 15% for stable catalog
    trigger_emergency_forecast_update()
    alert_merchandiser("High variance detected - forecast updated")
```

**Why?**
- If actuals are significantly different, remaining weeks' forecasts may be wrong
- Re-run uses actual sales as new signal for adaptive forecasting
- Update replenishment plans for future bi-weekly cycles

---

## Phase 4: Mid-Season Pricing Intervention (Week 12)

### When to Run
- **Timing**: Week 12 (46% through 26-week season)
- **Purpose**: Checkpoint for markdown decision
- **Runtime**: 30 minutes

### Decision #5: Markdown Trigger
**Decision**: Should we apply a markdown to accelerate sales?

**Checkpoint**:
```python
# Calculate sell-through rate at Week 12
total_sold_weeks_1_to_12 = sum(actual_sales[weeks_1_to_12])
total_manufactured = manufacturing_order  # 3,680 units

sell_through_rate = total_sold_weeks_1_to_12 / total_manufactured

if sell_through_rate < markdown_trigger_threshold:  # e.g., 50% for stable catalog
    recommend_markdown = True
    suggested_markdown_depth = calculate_markdown_depth(sell_through_rate)
```

**Example**:
```
Week 12 Checkpoint:
- Total sold (Weeks 1-12): 1,600 units
- Total manufactured: 3,680 units
- Sell-through: 1,600 / 3,680 = 43.5%

Target: 50% by Week 12
Status: ⚠️ 6.5% below target

Recommendation: Apply 10% markdown
```

### Decision #6: Re-forecast After Markdown
**Decision**: Update forecast for Weeks 13-26 with markdown effect

**Process**:
1. Pricing Agent recommends markdown depth (e.g., 10%)
2. Apply markdown in system
3. **Re-run Demand Agent** with new price as input
4. Update `demand_by_store_by_week` for Weeks 13-26
5. Adjust bi-weekly replenishment plans

**Example**:
```python
# Original forecast (Weeks 13-26): [140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
# After 10% markdown: [154, 143, 132, 121, 110, 99, 88, 77, 66, 55, 44, 33, 22, 11] (+10% demand)

# Update bi-weekly replenishment for Weeks 13-14:
for store in stores:
    updated_weeks_13_14_forecast = sum(demand_by_store_by_week[store][12:14])
    adjust_replenishment(store, updated_weeks_13_14_forecast)
```

---

## Phase 5: Season End (Week 26+)

### When to Run
- **Timing**: 2 weeks after season ends (Week 28)
- **Purpose**: Performance analysis & model learning
- **Runtime**: 1 hour

### Decision #7: Model Improvement
**Decision**: What model improvements should we make for next season?

**Retrospective Analysis**:
```python
# Compare forecast vs actuals for all 26 weeks
for week in range(1, 27):
    forecast = demand_by_store_by_week[:, week]
    actual = actual_sales[week]

    mape = calculate_mape(forecast, actual)
    bias = calculate_bias(forecast, actual)

    log_performance_metric(week, mape, bias)

# Identify which forecasting methods performed best
analyze_forecasting_method_accuracy()

# Feed learnings back into model
update_adaptive_forecasting_weights()
```

**Output**: Performance report
```
Season: Fall/Winter 2025 - Mid-Century Sofa (Charcoal)

Forecast Accuracy:
- MAPE (Weeks 1-26): 16.8%
- Bias: -1.5% (slight under-forecast)
- Best weeks: 1-6 (early season, MAPE <12%)
- Worst weeks: 22-26 (late season, MAPE >22%)

Forecasting Method Performance:
- Similar-item matching: 14.2% MAPE
  - Best predictor: "Mid-Century Sofa - Navy" (2024) - 11% MAPE
  - Worst predictor: "Sectional Sofa - Charcoal" (2024) - 28% MAPE
- Time-series (where applicable): 12.5% MAPE

Learnings:
- Color attribute is strong predictor (navy → charcoal worked well)
- Product type less important (sectional ≠ sofa demand pattern)
- Bi-weekly replenishment performed well (minimal stockouts)
- Update similar-item matching: increase weight on style, decrease weight on type
```

---

## Summary: Operational Parameters Users Configure (Archetype 2)

These parameters define **when** and **how often** the model runs:

| Parameter | Archetype 2 Value | Description |
|-----------|-------------------|-------------|
| `forecast_horizon` | 26 weeks | How far ahead to predict |
| `replenishment_cadence` | bi-weekly | How often to replenish stores |
| `forecast_update_cadence` | bi-weekly | How often to re-run forecast in-season |
| `variance_threshold` | 0.15 | Trigger emergency re-forecast if actuals > 15% off |
| `markdown_trigger_week` | 12 | When to check sell-through for markdown |
| `markdown_trigger_sellthrough` | 0.50 | Minimum sell-through to avoid markdown (50%) |
| `safety_stock_percentage` | 0.15 | Extra inventory buffer (15%) |
| `initial_allocation_strategy` | "conservative" | Send first 2 weeks forecast to stores |
| `holdback_percentage` | 0.65 | % of inventory to hold at DC (65% for stable catalog) |

---

## Key Takeaway (Archetype 2: Stable Catalog)

**We predict ONE thing**: `demand_by_store_by_week` matrix

**We make 7 decisions**:
1. Manufacturing order quantity (pre-season, 3 months before)
2. Initial allocation to stores (week 0, first 2 weeks)
3. Bi-weekly replenishment quantities (weeks 1-26)
4. Emergency re-forecast trigger (if variance >15%)
5. Markdown trigger (week 12 checkpoint, <50% sell-through)
6. Updated forecast post-markdown (weeks 13-26)
7. Model improvements for next season (post-season)

**We run the model**:
- **Once** 3 months before (2-4 hours)
- **Optionally** monthly pre-season (if new info)
- **Once** at season start (30 min)
- **Bi-weekly** in-season (30 min × 13 cycles)
- **Once** mid-season after markdown (30 min)
- **Once** post-season analysis (1 hour)
- **Total**: ~16-19 model runs per SKU per season

---

## Comparison: Workflow Across Archetypes

The **5-phase structure remains constant**, but parameters change:

| Phase | Archetype 1 (Fashion) | Archetype 2 (Stable) | Archetype 3 (Continuous) |
|-------|----------------------|---------------------|--------------------------|
| **Pre-Season Planning** | 6 mo before, 12-week horizon | 3 mo before, 26-week horizon | Rolling 52-week forecast |
| **Initial Allocation** | Week -1, Week 1 only | Week -1, Weeks 1-2 | Daily, 1-day needs |
| **In-Season** | Weekly replenishment | Bi-weekly replenishment | Daily replenishment |
| **Markdown Checkpoint** | Week 6, <60% sell-through | Week 12, <50% sell-through | Rare markdowns |
| **Season End** | Post-12-week analysis | Post-26-week analysis | Quarterly rolling analysis |
| **Holdback %** | 45-55% at DC | 60-70% at DC | 80-90% at DC |
| **Variance Threshold** | 20% | 15% | 10% |
| **Total Model Runs** | ~15-18 | ~16-19 | ~52-60 (continuous) |
