# Product Brief: Demand Forecasting & Inventory Allocation System

**Version:** 2.1
**Date:** 2025-10-10
**Status:** MVP Specification
**Focus:** Demand Forecasting & Inventory Allocation for Retail

---

## Executive Summary

We are building a **3-agent system** that helps retailers forecast demand and optimize inventory allocation and replenishment. The system uses a **parameter-driven architecture** that adapts to different retail business models, providing store-week granular forecasts to support manufacturing decisions and replenishment planning.

### The Problem We Solve

Based on interviews with 5 retail practitioners (furniture, mass retail, fashion), we identified critical pain points:

**1. Inaccurate Demand Forecasting (PP-001, PP-019)**
- *"Traditional numerical ML models don't provide enough accuracy and agility to predict demand"* - Furniture Retailer
- Result: Poor allocation → expensive redistribution, lost sales, excess inventory
- Impact: 20% forecast error on product launches

**2. Location-Specific Allocation Failures (PP-002, PP-015)**
- *"When forecasts are off, they must quickly reallocate inventory"* - Furniture Retailer
- Store-level demand patterns not captured → inventory misallocation → stockouts in high-demand stores, overstock in low-demand stores
- Impact: 5 hrs/week firefighting + ongoing stockout/overstock costs

**3. Late Markdown Decisions Causing Margin Loss (PP-016)**
- *"3-day data lag prevents timely action"* - Fashion Retailer
- Inaccurate forecasts delay price reduction decisions
- Impact: **$500K lost margin annually** from missed markdown timing

**4. Inventory Optimization Balance (PP-028)**
- Retailers struggle to avoid both overstock (excess carrying costs) and understock (lost sales)
- Requires accurate forecasting at store-week granularity
- Manual allocation processes are time-consuming and error-prone

**5. Long Manufacturing Lead Times with High Uncertainty (PP-001)**
- Must commit to quantities 3-6 months before season launch
- No sales history for new products → high forecast error → expensive overproduction or stockouts

### Our Solution

**Core Prediction**: `demand_by_store_by_week` matrix (e.g., 50 stores × 26 weeks = 1,300 predictions per SKU)

**How We Solve It**:
- **Store-week granularity** addresses PP-002, PP-015 (location-specific allocation)
- **Adaptive forecasting methods** address PP-001 (traditional ML limitations), PP-019 (new product uncertainty)
- **Bi-weekly re-forecasts** address PP-016 (timely markdown decisions)
- **DC holdback optimization** addresses PP-028 (inventory balance)
- **3-month advance forecasting** addresses PP-001 (manufacturing lead time decisions)

**3 Agents**:
1. **Demand Agent** - Predicts weekly demand by store using adaptive forecasting
2. **Inventory Agent** - Decides initial allocation + replenishment from DC
3. **Pricing Agent** - Recommends markdown timing/depth to prevent margin loss

**Orchestrator** - Coordinates agents, triggers re-forecasts based on variance

---

## Business Value

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Reduce Overstock** | Avoid over-manufacturing products that won't sell | 15-25% reduction in excess inventory |
| **Reduce Stockouts** | Allocate the right amount to high-demand stores | 20-30% reduction in stockouts |
| **Optimize Manufacturing Orders** | Commit to the right quantity 6 months before launch | Reduce markdown costs by 15% |
| **Improve Replenishment** | Weekly DC-to-store replenishment based on actuals | 10-15% improvement in inventory turnover |
| **Data-Driven Markdowns** | Trigger price reductions at the right time | Maximize revenue, minimize leftover inventory |

---

## Product Scope: What Exactly Are We Predicting?

### Single Prediction Output

```python
demand_forecast = {
    "SKU-12345": {  # Mid-Century Sofa - Charcoal (NEW variant)
        "Store_A1": [5, 8, 6, 7, 6, 5, 4, 4, 3, 3, 2, 2, ...],  # Week 1-26
        "Store_A2": [3, 4, 5, 6, 5, 4, 4, 3, 3, 2, 2, 1, ...],
        "Store_B1": [8, 12, 10, 11, 9, 8, 7, 6, 5, 4, 3, 2, ...],
        "Store_C1": [4, 6, 5, 6, 5, 4, 3, 3, 2, 2, 1, 1, ...],
        # ... all 50 stores
    }
}
```

### Derived Metrics (Not Separately Predicted)

From the `demand_by_store_by_week` matrix, we **derive**:

1. **Total Season Demand** = Sum of all 1,300 predictions (50 stores × 26 weeks)
   - Example: 3,200 units total for the 26-week season
   - **Decision**: How many to manufacture?

2. **Weekly Demand Curve** = Sum across stores for each week
   - Example: [250, 280, 260, 240, 220, 200, 190, 180, 170, 160, 150, 140, ...]
   - **Decisions**: Staffing, marketing timing, markdown triggers

3. **Store-Level Demand** = Sum across weeks for each store
   - Example: Store A1 needs 120 units total, Store C1 needs 50 units
   - **Decision**: How much to allocate to each store initially

---

## Target Users & Retail Archetypes

### User Onboarding: Questionnaire Approach

Users answer **11 questions** (see [key_parameter.md](../../05_Progress_Reports/Weekly_Supervisor_Meetings/key_parameter.md)) to be classified into one of **3 retail archetypes**:

#### Archetype 1: Seasonal Fashion Retail
- **Examples**: Zara, H&M, Forever 21
- **Characteristics**:
  - Short seasons (8-12 weeks)
  - 70-80% new products per season
  - Long lead times (3-6 months from Asia)
  - High fashion volatility
- **Forecasting Approach**: Adaptive methods with high similar-item matching usage
- **Inventory Strategy**: Hold 45-55% at DC, aggressive early allocation
- **Pricing Strategy**: Markdown at Week 6 if <60% sell-through

#### Archetype 2: Stable Catalog Retail ⭐ **[MVP FOCUS]**
- **Examples**: Pottery Barn, Williams Sonoma, West Elm, Crate & Barrel
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

#### Archetype 3: Continuous Replenishment Retail
- **Examples**: Walmart (CPG), Costco, grocery chains
- **Characteristics**:
  - No seasons (continuous replenishment)
  - 5-10% new products annually
  - Short lead times (days to weeks)
  - Predictable demand
- **Forecasting Approach**: Adaptive methods with high time-series usage
- **Inventory Strategy**: Hold 80-90% at DC, minimal store allocation
- **Pricing Strategy**: Rare markdowns; focus on stock rotation

### Future: Classifier Agent (4th Agent)

A **lightweight classifier agent** will route users to the appropriate archetype based on questionnaire responses, then configure system parameters accordingly. **Not included in MVP** - users manually select Archetype 2.

---

## The 3 Core Agents: Responsibilities

### Agent 1: Demand Forecasting Agent

**What It Predicts**: `demand_by_store_by_week` matrix for each SKU

**How It Works**:

The Demand Agent uses **adaptive forecasting methods** that automatically select the best approach based on available data:

1. **Similar-Item Matching**:
   - User provides SKU attributes (e.g., "Mid-Century Sofa, Charcoal, Fabric, $1,299")
   - Agent searches for similar SKUs (e.g., "Mid-Century Sofa - Navy, Fabric, $1,199" from 2024)
   - Uses attribute similarity scores (style > color > material > price)
   - Finds top 5-10 most similar historical SKUs

2. **Demand Pattern Extraction**:
   - For each similar SKU, extract weekly demand curve by store
   - Example: Navy sofa sold [8, 12, 10, 9, 8, 7, 6, 5, 4, 3, 3, 2, ...] in Store A1

3. **Adjustment Factors**:
   - Adjust for attribute differences (e.g., charcoal is trending: +10%)
   - Adjust for price difference (SKU is $100 more expensive: -8%)
   - Adjust for seasonality (Q4 holiday season: +15%)

4. **Forecast Generation**:
   - Combine similar-item patterns with adjustment factors
   - Weight by similarity score
   - Apply time-series models where historical data available
   - Output final `demand_by_store_by_week` matrix

**Inputs**:
- SKU attributes (category, style, color, material, price)
- Historical sales data (2-3 years)
- Store attributes (size, location, demographics)
- External trends (housing market, consumer confidence, seasonality)
- User-configured parameters (season length, lead time, etc.)

**Outputs**:
- `demand_by_store_by_week` matrix
- Confidence score (0-100%)
- Forecasting method used (for transparency)
- Similar-items referenced (if applicable)

**Re-run Triggers**:
- **Pre-season**: 3 months before (initial forecast)
- **Bi-weekly in-season**: Update based on actual sales
- **Variance-triggered**: If actuals deviate >15% from forecast

---

### Agent 2: Inventory Allocation & Replenishment Agent

**What It Decides**:
1. **Manufacturing Order Quantity** (pre-season, 3 months before)
2. **Initial Allocation** (week 0: how much to each store)
3. **Bi-weekly Replenishment** (weeks 1-26: how much to ship from DC to stores)

**How It Works** (Archetype 2: Stable Catalog):

**Decision 1: Manufacturing Order (3 Months Before)**
```python
total_demand = sum(demand_by_store_by_week)  # 3,200 units (26-week season)
safety_stock = total_demand * safety_stock_percentage  # 3,200 * 0.15 = 480
manufacturing_order = total_demand + safety_stock  # 3,680 units
```

**Decision 2: Initial Allocation (Week 0)**
```python
# Strategy: Conservative Allocation (hold 65% inventory at DC)
for store in stores:
    # Allocate first 2 weeks of demand (bi-weekly cadence)
    week_1_2_allocation[store] = sum(demand_by_store_by_week[store][0:2])

# Example:
# Store A1: 13 units (weeks 1-2 forecast)
# Store A2: 7 units
# Store B1: 20 units
# ...
# Total allocated: 1,280 units (35%)
# Held at DC: 2,400 units (65%)
```

**Decision 3: Bi-weekly Replenishment (Weeks 1-26)**
```python
for store in stores:
    current_inventory = get_store_inventory(store)
    next_2_weeks_forecast = sum(demand_by_store_by_week[store][current_week:current_week+2])
    replenishment_qty = max(0, next_2_weeks_forecast - current_inventory)
    replenish_from_dc(store, replenishment_qty)
```

**Inputs**:
- `demand_by_store_by_week` from Demand Agent
- Current store inventory levels
- DC inventory levels
- User-configured parameters (safety stock %, holdback %, replenishment cadence)

**Outputs**:
- Manufacturing order quantity
- Week 0 allocation by store
- Weekly replenishment plan by store

---

### Agent 3: Pricing Agent

**What It Decides**:
1. **Markdown Trigger** (should we apply a price reduction?)
2. **Markdown Depth** (how much to discount: 15%, 30%, 50%?)
3. **Markdown Timing** (which week to apply it?)

**How It Works**:

**Week 12 Checkpoint** (mid-season for Archetype 2):
```python
total_sold = sum(actual_sales[weeks_1_to_12])
sell_through_rate = total_sold / manufacturing_order

if sell_through_rate < markdown_trigger_threshold:  # e.g., 50%
    recommend_markdown = True
    suggested_markdown_depth = calculate_markdown_depth(sell_through_rate)

# Example:
# Sold 1,600 units of 3,680 manufactured = 43.5% sell-through
# Target: 50% by week 12
# Status: 6.5% below target
# Recommendation: Apply 10% markdown
```

**Post-Markdown**: Trigger Demand Agent to re-forecast weeks 13-26 with new price

**Inputs**:
- Actual sales data (weeks 1-12)
- Manufacturing order quantity
- Current inventory levels
- User-configured parameters (markdown trigger week, markdown threshold, target margin)

**Outputs**:
- Markdown recommendation (yes/no)
- Suggested markdown depth (%)
- Updated forecast request to Demand Agent

---

### Orchestrator

**Responsibilities**:
- **Coordinate workflow**: Demand Agent → Inventory Agent → Pricing Agent
- **Trigger re-forecasts**: Based on variance threshold or scheduled cadence
- **Monitor performance**: Track actuals vs. forecast, flag high-variance scenarios
- **Human-in-the-loop**: Alert merchandiser when confidence is low or variance is high

---

## Operational Workflow (When & How to Run)

See detailed workflow in [operational_workflow.md](../../05_Progress_Reports/Weekly_Supervisor_Meetings/operational_workflow.md)

**Note**: The operational workflow **structure is the same** for all 3 archetypes - only the **timing and cadence parameters differ**.

### Summary: 5 Phases (Archetype 2: Stable Catalog)

| Phase | When | Purpose | Model Runtime | Decision |
|-------|------|---------|---------------|----------|
| **Pre-Season Planning** | 3 months before | Initial forecast | 2-4 hours | Manufacturing order |
| **Season Start** | Week -1 | Confirm forecast | 30 min | Initial allocation |
| **In-Season Operations** | Bi-weekly, Weeks 1-26 | Update forecast | 30 min/update | Bi-weekly replenishment |
| **Mid-Season Pricing** | Week 12 | Markdown checkpoint | 30 min | Markdown trigger |
| **Season End** | Post-season | Performance analysis | 1 hour | Model improvements |

### How Workflow Adapts Across Archetypes

The **5-phase structure remains constant**, but parameters change:

| Phase | Archetype 1 (Fashion) | Archetype 2 (Stable) ⭐ MVP | Archetype 3 (Continuous) |
|-------|----------------------|---------------------------|--------------------------|
| **Pre-Season Planning** | 6 mo before, 12-week season | 3 mo before, 26-week season | Rolling 52-week forecast |
| **Initial Allocation** | Week -1, send Week 1 needs | Week -1, send 2-week needs | Daily, send 1-day needs |
| **In-Season** | Weekly replenishment | Bi-weekly replenishment | Daily replenishment |
| **Markdown Checkpoint** | Week 6, <60% sell-through | Week 12, <50% sell-through | Rare markdowns |
| **Season End** | Post-12-week analysis | Post-26-week analysis | Quarterly rolling analysis |

### Key Cadence Parameters

| Parameter | Archetype 1 (Fashion) | Archetype 2 (Stable) | Archetype 3 (Continuous) |
|-----------|----------------------|---------------------|--------------------------|
| `forecast_horizon` | 12 weeks | 26 weeks | 52 weeks |
| `replenishment_cadence` | Weekly | Bi-weekly | Daily |
| `forecast_update_cadence` | Weekly | Bi-weekly | Weekly |
| `variance_threshold` | 20% | 15% | 10% |
| `markdown_trigger_week` | 6 | 12 | N/A |
| `holdback_percentage` | 45% | 65% | 85% |

---

## User Configuration vs. Agent Decisions

See detailed parameters in [key_parameter.md](../../05_Progress_Reports/Weekly_Supervisor_Meetings/key_parameter.md)

### 🔧 USER INPUT (Business Constraints)

Users configure these **before** running the system:

1. **Season length** (e.g., 12 weeks)
2. **Number of stores** (e.g., 50)
3. **New product ratio** (e.g., 80% of SKUs are new)
4. **Lead time** (e.g., 4 months)
5. **Safety stock percentage** (e.g., 15%)
6. **Markdown trigger threshold** (e.g., 60% sell-through)
7. **Replenishment cadence** (e.g., weekly)

### 🤖 AGENT DECISIONS (System Calculates)

Agents **decide** these during operation:

1. **Forecasted demand quantities** (by store, by week)
2. **Manufacturing order quantity** (total demand + safety stock)
3. **Initial allocation by store** (week 0)
4. **Weekly replenishment quantities** (weeks 1-12)
5. **Markdown depth** (15%, 30%, 50%)
6. **Similar-items to use** (which historical SKUs to match)
7. **Confidence scores** (how certain is the forecast?)

### ⚙️ USER OR AGENT (Flexible)

Users can **configure** these OR let agents **decide**:

1. **Holdback percentage** - User sets 45% OR agent optimizes based on season/category
2. **Variance threshold** - User sets 20% OR agent learns optimal threshold over time
3. **Similar-item matching weights** - User prioritizes attributes (color > style) OR agent learns weights

---

## Success Metrics

### Forecast Accuracy (Primary)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE (Mean Absolute Percentage Error)** | <20% | Compare forecast vs. actuals by week |
| **Bias** | ±5% | Check if consistently over/under-forecasting |
| **Confidence Calibration** | 80%+ | When agent says 80% confident, error should be ≤20% |

### Business Impact (Secondary)

| Metric | 6-Month Target | 12-Month Target |
|--------|---------------|-----------------|
| **Stockout Reduction** | 15% | 25% |
| **Overstock Reduction** | 10% | 20% |
| **Markdown Cost Reduction** | 10% | 15% |
| **Inventory Turnover Improvement** | 8% | 15% |

### System Performance

| Metric | Target |
|--------|--------|
| **Initial Forecast Runtime** | <4 hours |
| **Weekly Update Runtime** | <30 minutes |
| **Uptime** | 99%+ |

---

## MVP Scope (Proof of Concept)

### What's Included in MVP

✅ **Single Retail Archetype**: Stable Catalog Retail (26-week season)
✅ **Single Category**: Furniture (Sofas)
✅ **Single Season**: Fall/Winter 2025 (26 weeks)
✅ **50 Stores**
✅ **50 SKUs** across furniture catalog (mix of product types, colors, materials)
✅ **3 Agents**: Demand, Inventory, Pricing
✅ **Orchestrator**: Basic workflow coordination
✅ **Forecasting Methods**: Adaptive approach (similar-item matching, time-series where applicable)
✅ **Bi-weekly Cadence**: Re-forecast bi-weekly based on actuals
✅ **Markdown Logic**: Week 12 checkpoint

### What's NOT Included in MVP

❌ **Multi-archetype support** (only Archetype 2: Stable Catalog)
❌ **Classifier Agent** (user manually configures for Archetype 2)
❌ **Machine learning similarity** (use rule-based attribute matching, not ML-based)
❌ **Advanced forecasting models** (basic ARIMA/Prophet, not deep learning)
❌ **Multi-season overlap** (one season at a time)
❌ **Store-to-store transfers** (only DC-to-store replenishment)
❌ **Dynamic pricing optimization** (fixed markdown depths: 10%, 20%, 30%)
❌ **Advanced hybrid methods** (adaptive blending based on early sales data)

### MVP Timeline: 12 Weeks

| Week | Milestone |
|------|-----------|
| 1-2 | Environment setup, data pipeline, explore historical furniture sales data |
| 3-4 | Demand Agent: Similar-item matching algorithm |
| 5-6 | Demand Agent: Time-series forecasting, adaptive method selection |
| 7-8 | Inventory Agent: Allocation + bi-weekly replenishment logic |
| 9 | Pricing Agent: Markdown trigger logic (Week 12 checkpoint) |
| 10 | Orchestrator: Workflow coordination, variance-triggered re-forecasts |
| 11 | Validation: Hindcast Fall/Winter 2024 (26-week season) |
| 12 | Performance analysis, MAPE measurement, final report |

---

## Data Requirements

### Input Data (Provided by User)

1. **Historical Sales Data** (2-3 years)
   - Fields: `date, sku, store_id, quantity_sold, revenue`
   - Granularity: Daily
   - Coverage: All SKUs across all stores

2. **Product Catalog** (Historical + New)
   - Fields: `sku, category, style, color, material, dimensions, price, launch_date`
   - Includes: Both sold SKUs (historical) and new SKUs/variants (to be forecasted)
   - Example: "Mid-Century Sofa - Navy, Fabric, 84"W x 36"D x 32"H, $1,199, 2024-03-01"

3. **Store Attributes**
   - Fields: `store_id, location, region, size_sqft, demographics, climate_zone`

4. **External Factors** (Optional)
   - Housing market data (home sales, mortgage rates by region)
   - Macro trends (consumer confidence, unemployment, GDP growth)
   - Seasonality indicators (holidays, promotional calendar)

### Output Data (Generated by System)

1. **Forecasts**
   - `demand_by_store_by_week` matrix per SKU
   - Confidence scores
   - Similar-items used

2. **Decisions**
   - Manufacturing orders
   - Store allocations
   - Replenishment plans
   - Markdown recommendations

3. **Performance Metrics**
   - MAPE by week
   - Bias
   - Actual vs. forecast comparison

---

## Technical Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                            │
│  • Workflow coordination                                    │
│  • Re-forecast triggers                                     │
│  • Performance monitoring                                   │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬───────────────────┬──────────────────┐
    │                 │                   │                  │
    ▼                 ▼                   ▼                  ▼
┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐
│ DEMAND  │    │INVENTORY │    │   PRICING    │    │CLASSIFIER│
│  AGENT  │    │  AGENT   │    │   AGENT      │    │  AGENT   │
│         │    │          │    │              │    │ (Future) │
│• Similar│    │• Mfg     │    │• Markdown    │    │• Route   │
│  item   │    │  order   │    │  trigger     │    │  to      │
│  match  │    │• Alloc   │    │• Depth       │    │  arch.   │
│• Predict│    │• Repl.   │    │• Timing      │    │          │
└─────────┘    └──────────┘    └──────────────┘    └──────────┘
     │              │                  │
     └──────────────┴──────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   DATA LAYER          │
        │• Historical sales DB  │
        │• Product catalog      │
        │• Store attributes     │
        │• External APIs        │
        └───────────────────────┘
```

---

## Key Assumptions & Constraints

### Assumptions

1. **Historical data quality**: 2-3 years of clean sales data available
2. **Similar items exist**: For every new SKU, there are ≥5 similar historical SKUs
3. **Weekly cadence is sufficient**: No need for daily re-forecasting
4. **DC-based replenishment**: No store-to-store transfers needed
5. **Single currency/country**: No cross-border complexity

### Constraints

1. **Cold-start problem**: Only works for categories with historical data
2. **Attribute dependency**: Requires structured product attributes (color, style, etc.)
3. **Computational cost**: Initial forecast takes 2-4 hours for large catalogs
4. **Human review**: High-value SKUs still need merchandiser approval
5. **Data latency**: Actuals may lag by 24-48 hours

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Poor similar-item matches** | Medium | High | Implement attribute weighting; allow manual override |
| **Insufficient historical data** | Medium | Medium | Require minimum 2 years; fall back to category averages |
| **High forecast variance** | High | Medium | Weekly updates; variance-triggered re-forecasts |
| **Low user adoption** | Medium | High | Run parallel forecasts; prove accuracy before full rollout |
| **Data quality issues** | High | High | Implement validation checks; flag low-confidence forecasts |

---

## Comparison: Our Approach vs. Alternatives

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| **Our System (3-Agent)** | ✅ Store-week granularity<br>✅ NEW + EXISTING products<br>✅ Automated replenishment<br>✅ Cold-start handling | ❌ Requires historical data<br>❌ 2-4 hour runtime<br>❌ Complex setup | NEW variants + existing catalog in stable retail |
| **Traditional Time-Series** | ✅ Simple<br>✅ Fast<br>✅ Well-understood | ❌ Needs sales history per SKU<br>❌ No NEW products<br>❌ No store granularity | Existing SKUs with 2+ years history |
| **Category Averages** | ✅ Very simple<br>✅ No data needed | ❌ Very inaccurate<br>❌ No store/SKU granularity | Quick rough estimates only |
| **Expert Judgment** | ✅ Incorporates intuition<br>✅ Handles novelty | ❌ Slow<br>❌ Not scalable<br>❌ Inconsistent | High-value, one-off custom items |

---

## Next Steps

### Immediate (Week 1-2)
1. **Secure data access**: Historical sales data, product catalog, store attributes
2. **Define validation approach**: Use Fall 2024 data for hindcast testing
3. **Set up environment**: Python, data warehouse connection, compute resources

### Short-Term (Week 3-6)
1. **Build Demand Agent - Similar-Item**: Algorithm implementation, validate on 5 SKUs
2. **Build Demand Agent - Time-Series**: ARIMA/Prophet implementation, validate on 5 SKUs
3. **Generate first forecasts**: Run adaptive method end-to-end for 10 total SKUs

### Medium-Term (Week 7-12)
1. **Build Inventory Agent**: Allocation + bi-weekly replenishment logic (Archetype 2 parameters)
2. **Build Pricing Agent**: Markdown trigger logic (Week 12 checkpoint, 50% threshold)
3. **Orchestrator integration**: Connect all 3 agents, implement variance-triggered re-forecasts
4. **Validation**: Hindcast Fall/Winter 2024 (26 weeks), measure MAPE across SKUs

---

## Glossary

**Cold-Start Problem**: Difficulty forecasting NEW products with no sales history
**Demand Curve**: Weekly demand pattern over the season (e.g., [250, 380, 320, ...])
**Holdback Percentage**: % of inventory kept at DC instead of allocated to stores
**MAPE**: Mean Absolute Percentage Error - forecast accuracy metric
**Markdown**: Price reduction to accelerate sales (e.g., 15% off)
**Replenishment**: Weekly shipment from DC to stores to restock inventory
**Safety Stock**: Extra inventory buffer to avoid stockouts (e.g., 15% above forecast)
**Sell-Through Rate**: % of manufactured inventory sold by a given week
**Similar-Item Matching**: Algorithm to find historical SKUs with similar attributes
**SKU**: Stock Keeping Unit - unique product identifier (e.g., "Red Floral Dress - Size M")

---

## Appendix: Sample Forecast Output

```json
{
  "sku": "SKU-SF-3421",
  "product_name": "Mid-Century Sofa - Charcoal",
  "category": "Furniture - Sofas",
  "season": "Fall/Winter 2025",
  "forecast_date": "2025-07-15",
  "sku_type": "NEW_VARIANT",
  "forecast_method": "similar_item_matching",
  "confidence": 82,
  "similar_items_used": [
    {"sku": "SKU-SF-3420", "name": "Mid-Century Sofa - Navy", "similarity": 0.95},
    {"sku": "SKU-SF-3310", "name": "Mid-Century Sofa - Grey", "similarity": 0.92},
    {"sku": "SKU-SF-3200", "name": "Modern Sofa - Charcoal", "similarity": 0.78}
  ],
  "demand_by_store_by_week": {
    "Store_A1": [5, 8, 6, 7, 6, 5, 4, 4, 3, 3, 2, 2, 2, 3, 4, 5, 6, 5, 4, 3, 3, 2, 2, 1, 1, 1],
    "Store_A2": [3, 4, 5, 6, 5, 4, 4, 3, 3, 2, 2, 1, 1, 2, 3, 4, 5, 4, 3, 2, 2, 1, 1, 1, 0, 0],
    "Store_B1": [8, 12, 10, 11, 9, 8, 7, 6, 5, 4, 3, 2, 3, 5, 7, 8, 9, 8, 6, 5, 4, 3, 2, 2, 1, 1],
    "Store_C1": [4, 6, 5, 6, 5, 4, 3, 3, 2, 2, 1, 1, 1, 2, 3, 4, 5, 4, 3, 2, 2, 1, 1, 0, 0, 0]
  },
  "derived_metrics": {
    "total_season_demand": 3200,
    "weekly_demand_curve": [250, 280, 260, 240, 220, 200, 190, 180, 170, 160, 150, 140, 150, 180, 200, 220, 240, 210, 180, 150, 140, 120, 110, 100, 90, 80],
    "peak_week": 2,
    "peak_demand": 280,
    "secondary_peak_week": 17
  },
  "inventory_recommendations": {
    "manufacturing_order": 3680,
    "safety_stock": 480,
    "initial_allocation_total": 1280,
    "dc_holdback": 2400,
    "holdback_percentage": 65
  },
  "archetype_parameters": {
    "archetype": "STABLE_CATALOG",
    "season_length_weeks": 26,
    "replenishment_cadence": "bi_weekly",
    "markdown_trigger_week": 12,
    "markdown_threshold": 0.50
  }
}
```

---

**Document Owner**: Independent Study Project
**Last Updated**: 2025-10-10
**Version**: 2.1
**Related Documents**:
- [Operational Workflow](../../05_Progress_Reports/Weekly_Supervisor_Meetings/operational_workflow.md)
- [Key Parameters](../../05_Progress_Reports/Weekly_Supervisor_Meetings/key_parameter.md)
- [Original Technical Pitch](1_idea.md)

---

## Summary of Changes from v2.0

**Version 2.1 (2025-10-10)** - Revised MVP scope & problem validation:
- ✅ **Added evidence-based problem validation** - References 5 pain points (PP-001, PP-002, PP-015, PP-016, PP-028) from user interviews
- ✅ **MVP now targets Archetype 2: Stable Catalog Retail** (was Archetype 1: Fashion)
- ✅ **26-week season** (was 12-week)
- ✅ **Furniture category** (sofas) instead of fashion (dresses)
- ✅ **Adaptive forecasting approach** (not specific to new/existing products)
- ✅ **Bi-weekly replenishment** (was weekly)
- ✅ **Week 12 markdown checkpoint** (was week 6)
- ✅ Clarified **operational workflow is same for all archetypes** - only parameters differ
- ✅ Updated examples, timelines, and sample output to reflect Archetype 2
- ✅ De-emphasized new vs existing product language - system is general-purpose

**Rationale**:
- Archetype 2 addresses **moderate complexity** pain points from evidence pack
- **Furniture retail** is a classic use case for initial allocation problems (PP-002, PP-015, PP-028)
- Aligns with professor's guidance: "focus on initial allocation first"
- Evidence pack validates problem severity ($500K margin loss, 5 hrs/week firefighting)
