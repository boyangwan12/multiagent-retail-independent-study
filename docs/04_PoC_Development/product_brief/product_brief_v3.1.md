# Product Brief: Demand Forecasting & Inventory Allocation System

**Version:** 3.1
**Date:** 2025-10-11
**Status:** MVP Specification
**Focus:** Category-Level Demand Forecasting & Hierarchical Inventory Allocation for Retail

---

## Executive Summary

We are building a **3-agent system** that helps retailers forecast demand and optimize inventory allocation and replenishment at the **category level**. The system uses a **hierarchical forecasting and allocation architecture** that adapts to different retail business models through configurable parameters, providing category-level forecasts and cluster-based store allocation to support manufacturing decisions and replenishment planning.

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
- Requires accurate forecasting at appropriate granularity
- Manual allocation processes are time-consuming and error-prone

**5. Long Manufacturing Lead Times with High Uncertainty (PP-001)**
- Must commit to quantities 3-6 months before season launch
- No sales history for new products → high forecast error → expensive overproduction or stockouts

### Our Solution: Hierarchical Forecasting & Allocation

**Industry-Aligned Approach**: Based on retail industry best practices, our system uses **top-down/middle-out forecasting** instead of highly granular store-SKU-week predictions.

**Core Prediction Structure**:

```
Category-Level Forecast (e.g., "Women's Dresses")
    ├── Total Season Demand: 8,000 units
    ├── Weekly Demand Curve: [650, 720, 680, 620...]
    └── Store Cluster Distribution:
         ├── Fashion Forward (40%): 3,200 units → 20 stores
         ├── Mainstream (35%): 2,800 units → 18 stores
         └── Value Conscious (25%): 2,000 units → 12 stores
```

**Why This Approach:**
- ✅ **Industry-standard practice**: Retailers forecast at category level, then allocate
- ✅ **More accurate**: Aggregate forecasting reduces noise and improves accuracy
- ✅ **Computationally feasible**: Manageable forecast runtime (minutes, not hours)
- ✅ **Actionable**: Supports manufacturing, allocation, and pricing decisions
- ✅ **Professor-validated**: Addresses feedback on granularity concerns

**How We Solve It**:
- **Category-level forecasting** addresses PP-001 (traditional ML limitations), PP-019 (new product uncertainty)
- **Hierarchical cluster-based allocation** addresses PP-002, PP-015 (location-specific allocation)
- **Periodic re-forecasts** address PP-016 (timely markdown decisions)
- **DC holdback optimization** addresses PP-028 (inventory balance)
- **Advance forecasting** addresses PP-001 (manufacturing lead time decisions)

**3 Agents**:
1. **Demand Agent** - Forecasts category-level demand with cluster distribution
2. **Inventory Agent** - Hierarchical allocation (cluster → store) + replenishment
3. **Pricing Agent** - Markdown timing/depth based on category sell-through

**Orchestrator** - Coordinates agents, triggers re-forecasts based on variance

---

## Business Value

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Reduce Overstock** | Avoid over-manufacturing products that won't sell | 15-25% reduction in excess inventory |
| **Reduce Stockouts** | Allocate the right amount to high-demand stores | 20-30% reduction in stockouts |
| **Optimize Manufacturing Orders** | Commit to the right quantity months before launch | Reduce markdown costs by 15% |
| **Improve Replenishment** | Periodic DC-to-store replenishment based on actuals | 10-15% improvement in inventory turnover |
| **Data-Driven Markdowns** | Trigger price reductions at the right time | Maximize revenue, minimize leftover inventory |

---

## Product Scope: What Exactly Are We Predicting?

### Forecasting Granularity (Industry-Aligned)

**NOT predicting:**
❌ Store × SKU × Week combinations (e.g., 50 stores × 100 SKUs × 26 weeks = 130,000 predictions)
❌ Individual SKU demand across stores
❌ Daily granularity

**INSTEAD, we predict:**
✅ **Category-level demand** (e.g., "Women's Dresses" category aggregate)
✅ **Weekly temporal distribution** (company-wide demand curve)
✅ **Cluster-level spatial distribution** (% by store cluster)
✅ **Store-level allocation factors** (within each cluster)

### Single Prediction Output Example

```python
forecast_output = {
    "category": "Women's Dresses",
    "season": "Spring 2025",
    "forecast_horizon_weeks": 12,

    # 1. TOTAL SEASON DEMAND (Aggregate)
    "total_season_demand": 8000,
    "confidence_score": 0.75,

    # 2. WEEKLY DEMAND CURVE (Temporal Distribution)
    "weekly_demand_curve": [
        650, 720, 680, 620, 580, 540, 500, 460,
        420, 380, 340, 310
    ],

    # 3. STORE CLUSTER DISTRIBUTION (Spatial Distribution)
    "cluster_distribution": {
        "Fashion_Forward": {
            "demand_percentage": 0.40,
            "total_demand": 3200,
            "num_stores": 20,
            "stores": {
                "Store_F1": {"factor": 0.08, "season_allocation": 256},
                "Store_F2": {"factor": 0.06, "season_allocation": 192},
                # ... 20 stores
            }
        },
        "Mainstream": {
            "demand_percentage": 0.35,
            "total_demand": 2800,
            "num_stores": 18,
            "stores": {...}
        },
        "Value_Conscious": {
            "demand_percentage": 0.25,
            "total_demand": 2000,
            "num_stores": 12,
            "stores": {...}
        }
    }
}
```

### Derived Decisions (Not Separately Predicted)

From the category-level forecast, we **derive**:

1. **Manufacturing Order Quantity** = Total demand + Safety stock
   - Example: 8,000 + 1,600 (20%) = 9,600 units
   - **Decision**: How many to manufacture?

2. **Initial Store Allocation** = Season allocation × Initial allocation %
   - Example: Store F1 gets 256 total, send 141 initially (55%), hold 115 at DC (45%)
   - **Decision**: How much to each store at launch?

3. **Replenishment Plan** = Based on actual sales vs. remaining allocation
   - Example: Store F1 sold 85 in 1 week, has 56 left, needs 70 more for next week
   - **Decision**: How much to replenish weekly?

---

## Target Users & Retail Archetypes

### Generic Framework, Archetype-Specific Parameters

The system architecture is **generic** and supports multiple retail models through **parameter configuration**. Users are classified into one of **3 retail archetypes** based on business characteristics:

#### Archetype 1: Seasonal Fashion Retail ⭐ **[MVP FOCUS]**
- **Examples**: Zara, H&M, Forever 21
- **Characteristics**:
  - Short seasons (8-12 weeks)
  - 70-80% new products per season
  - Long lead times (3-6 months from Asia)
  - High demand volatility
- **Parameters**:
  - Forecast horizon: 12 weeks
  - Replenishment cadence: Weekly
  - Holdback %: 45%
  - Markdown trigger: Week 6, <60% sell-through

**Why Archetype 1 for MVP:**
- ✅ **High business impact**: Fashion retail has critical markdown/overstock problems (PP-016: $500K margin loss)
- ✅ **Fast validation cycle**: 12-week seasons allow rapid testing and iteration
- ✅ **Addresses key pain points**: PP-001 (high new product ratio), PP-016 (markdown timing), PP-019 (demand volatility)
- ✅ **Tests system adaptability**: High variance scenarios validate re-forecasting capabilities
- ✅ **Industry-aligned granularity**: Category-level forecasting is standard practice for fast fashion

#### Archetype 2: Stable Catalog Retail
- **Examples**: Pottery Barn, Williams Sonoma, West Elm, Crate & Barrel
- **Characteristics**:
  - Medium seasons (6-12 months, typically 26 weeks)
  - 20-30% new products per season (new colors/materials of existing styles)
  - Medium lead times (2-4 months, often from Asia)
  - Stable demand patterns with predictable seasonality
- **Parameters**:
  - Forecast horizon: 26 weeks
  - Replenishment cadence: Bi-weekly
  - Holdback %: 65%
  - Markdown trigger: Week 12, <50% sell-through

#### Archetype 3: Continuous Replenishment Retail
- **Examples**: Walmart (CPG), Costco, grocery chains
- **Characteristics**:
  - No seasons (continuous replenishment)
  - 5-10% new products annually
  - Short lead times (days to weeks)
  - Predictable demand
- **Parameters**:
  - Forecast horizon: 52 weeks (rolling)
  - Replenishment cadence: Daily/Weekly
  - Holdback %: 85%
  - Markdown trigger: Rare

### Future: Classifier Agent (4th Agent)

A **lightweight classifier agent** will route users to the appropriate archetype based on business characteristics, then configure system parameters accordingly. **Not included in MVP** - users manually select Archetype 1.

---

## The 3 Core Agents: Responsibilities

### Agent 1: Demand Forecasting Agent

**What It Predicts**: Category-level demand with hierarchical distribution

**Core Outputs**:
1. **Total season demand** (aggregate)
2. **Weekly demand curve** (temporal distribution)
3. **Cluster distribution** (spatial distribution)
4. **Store allocation factors** (within clusters)

**How It Works** (Hierarchical Forecasting Approach):

**Step 1: Aggregate Category Forecasting**
- Input: Historical sales data for category (all SKUs combined)
- Method: Time-series forecasting (ARIMA, Prophet, seasonal decomposition)
- Adjustment factors: Seasonality, trends, external factors (fashion trends, weather, consumer sentiment)
- Output: Total season demand (e.g., 8,000 women's dresses)

**Step 2: Temporal Distribution (Weekly Demand Curve)**
- Extract typical weekly demand pattern from historical data
- Adjust for known events (holidays, promotions, seasonality)
- Output: Weekly demand curve [250, 280, 260, 240, ...]

**Step 3: Store Clustering**
- Method: Pre-defined clustering based on:
  - **Demographics**: Income, age, fashion-consciousness
  - **Store attributes**: Size (sqft), location tier (urban/suburban/mall), foot traffic, sales volume
  - **Historical performance**: Category sales history by store
- Clustering approach:
  - K-means or hierarchical clustering on store attributes
  - Typical: 3-5 clusters per retailer
- Output: Store clusters (e.g., Fashion Forward, Mainstream, Value Conscious)

**Step 4: Cluster-Level Demand Distribution**
- Calculate historical cluster performance: % of total category sales
- Apply to new forecast
- Output: Cluster distribution (e.g., 40%/35%/25%)

**Step 5: Store-Level Allocation Factors (Within Clusters)**
- Method: Hybrid approach (70% historical + 30% attribute-based)
- Historical factor: Store's % of cluster sales last season
- Attribute factor: Store capacity score based on size, tier, demographics
- Output: Allocation factor per store (e.g., Store A1 gets 12% of cluster demand)

**Inputs**:
- Historical sales data (2-3 years, category-level)
- Store attributes (size, location, demographics, fashion tier)
- Store clustering (pre-defined or calculated)
- External trends (fashion trends, weather, social media trends, seasonality)
- User-configured parameters (season length, lead time, etc.)

**Outputs**:
```json
{
  "total_season_demand": 8000,
  "weekly_demand_curve": [650, 720, 680, ...],
  "cluster_distribution": {
    "Fashion_Forward": 0.40,
    "Mainstream": 0.35,
    "Value_Conscious": 0.25
  },
  "store_allocation_factors": {
    "Store_F1": 0.08,
    "Store_F2": 0.06,
    ...
  },
  "confidence_score": 0.75,
  "forecasting_method": "hierarchical_time_series"
}
```

**Re-run Triggers**:
- **Pre-season**: 6 months before (initial forecast)
- **In-season**: Weekly or based on variance threshold
- **Variance-triggered**: If actuals deviate >20% from forecast

---

### Agent 2: Inventory Allocation & Replenishment Agent

**What It Decides**:
1. **Manufacturing Order Quantity** (pre-season, 6 months before)
2. **Initial Store Allocation** (week 0: hierarchical cluster → store allocation)
3. **Periodic Replenishment** (weekly: top-up based on actuals)

**How It Works** (Hierarchical Allocation Logic):

**Decision 1: Manufacturing Order (6 Months Before Season)**
```python
total_demand = 8000  # From Demand Agent
safety_stock_percentage = 0.20  # User-configured (Archetype 1)
safety_stock = total_demand * safety_stock_percentage  # 1,600
manufacturing_order = total_demand + safety_stock  # 9,600 units
```

**Decision 2: Initial Allocation (Week 0) - Hierarchical**

**Step 2A: Allocate to Clusters**
```python
# From Demand Agent cluster distribution
Fashion_Forward_total = 8000 × 0.40 = 3,200 dresses
Mainstream_total = 8000 × 0.35 = 2,800 dresses
Value_Conscious_total = 8000 × 0.25 = 2,000 dresses
```

**Step 2B: Allocate Within Clusters to Stores**
```python
# For each cluster, use store allocation factors
for cluster in clusters:
    for store in cluster.stores:
        # Season-total allocation
        store_season_allocation = cluster_total × store_allocation_factor

        # Initial allocation (send X% at launch, hold rest at DC)
        initial_allocation_pct = 0.55  # Archetype 1: Aggressive (55%)
        store_initial = store_season_allocation × initial_allocation_pct
        store_holdback = store_season_allocation × (1 - initial_allocation_pct)

# Example:
# Store F1 (Fashion Forward cluster):
#   Season allocation: 3,200 × 0.08 = 256 dresses
#   Initial allocation: 256 × 0.55 = 141 dresses (week 0)
#   DC holdback: 256 × 0.45 = 115 dresses
```

**Decision 3: Periodic Replenishment (Weekly, Weeks 1-12)**
```python
for store in stores:
    # Get current state
    current_inventory = get_store_inventory(store)
    actual_sales_last_period = get_actual_sales(store, last_1_week)
    remaining_season_allocation = store_season_total - total_shipped_so_far
    remaining_weeks = 12 - current_week

    # Calculate expected need for next period
    expected_1week_sales = remaining_season_allocation / remaining_weeks

    # Adjust based on variance (if selling faster/slower than forecast)
    variance = actual_sales_last_period / expected_1week_sales
    adjusted_need = expected_1week_sales × variance

    # Replenish if needed
    replenishment_qty = max(0, adjusted_need - current_inventory)
    if replenishment_qty > 0 and dc_inventory > 0:
        ship_from_dc(store, min(replenishment_qty, dc_inventory))
```

**Inputs**:
- Category-level forecast from Demand Agent
- Store allocation factors (hierarchical)
- Current store inventory levels
- DC inventory levels
- Actual sales data (for replenishment adjustments)
- User-configured parameters (safety stock %, holdback %, replenishment cadence)

**Outputs**:
- Manufacturing order quantity
- Week 0 allocation by store (hierarchical)
- Periodic replenishment plan by store

---

### Agent 3: Pricing Agent

**What It Decides**:
1. **Markdown Trigger** (should we apply a price reduction?)
2. **Markdown Depth** (how much to discount: 10%, 20%, 30%?)
3. **Markdown Timing** (which week to apply it?)
4. **Optional: Cluster-level differentiation** (different markdowns per cluster)

**How It Works**:

**Category-Level Sell-Through Tracking**
```python
# Mid-season checkpoint (Week 6 for Archetype 1)
total_manufactured = 9600
total_sold = sum(actual_sales_weeks_1_to_6)  # e.g., 5280
sell_through_rate = total_sold / total_manufactured  # 0.55 (55%)

# Target: 60% by week 6 (Archetype 1 parameter)
target_sell_through = 0.60
variance = sell_through_rate - target_sell_through  # -0.05 (-5%)

if variance < 0:  # Below target
    recommend_markdown = True
    # Calculate markdown depth based on variance magnitude
    if abs(variance) < 0.05:
        markdown_depth = 0.15  # 15% markdown
    elif abs(variance) < 0.10:
        markdown_depth = 0.30  # 30% markdown
    else:
        markdown_depth = 0.50  # 50% markdown
```

**Optional: Cluster-Level Differentiation**
```python
# Calculate sell-through by cluster
for cluster in clusters:
    cluster_sell_through = cluster_actual_sales / cluster_allocated

    if cluster_sell_through < target - 0.15:  # 15% below target
        cluster_markdown[cluster] = 0.50  # Aggressive markdown
    elif cluster_sell_through < target - 0.10:
        cluster_markdown[cluster] = 0.30  # Moderate markdown
    else:
        cluster_markdown[cluster] = 0.15  # Light markdown

# Example:
# Value_Conscious: 42% sell-through → 50% markdown
# Mainstream: 53% sell-through → 30% markdown
# Fashion_Forward: 58% sell-through → 15% markdown
```

**Post-Markdown Action**: Trigger Demand Agent to re-forecast weeks 7-12 with new price

**Inputs**:
- Actual sales data (weeks 1-6)
- Manufacturing order quantity
- Current inventory levels (by store/cluster)
- User-configured parameters (markdown trigger week, threshold, target margin)

**Outputs**:
- Markdown recommendation (yes/no)
- Suggested markdown depth (%)
- Timing (which week)
- Optional: Cluster-specific markdown depths
- Updated forecast request to Demand Agent

---

### Orchestrator

**Responsibilities**:
- **Coordinate workflow**: Demand Agent → Inventory Agent → Pricing Agent
- **Trigger re-forecasts**: Based on variance threshold or scheduled cadence
- **Monitor performance**: Track actuals vs. forecast, flag high-variance scenarios
- **Human-in-the-loop**: Alert merchandiser when confidence is low or variance is high

**Variance-Triggered Re-Forecasting**:
```python
# Check variance every period (weekly for Archetype 1)
variance_threshold = 0.20  # Archetype 1 parameter

for period in season:
    actual_demand = sum(actual_sales_last_period)
    forecast_demand = sum(forecast_weeks_last_period)
    variance = abs(actual_demand - forecast_demand) / forecast_demand

    if variance > variance_threshold:
        trigger_demand_agent_reforecast()
        update_replenishment_plan()
```

---

## Success Metrics

### Forecast Accuracy (Primary)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE (Mean Absolute Percentage Error)** | <20% | Compare forecast vs. actuals by week (category-level) |
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
| **Initial Forecast Runtime** | <30 minutes (was 2-4 hours at store-SKU-week level) |
| **Periodic Update Runtime** | <10 minutes |
| **Uptime** | 99%+ |

---

## MVP Scope (Proof of Concept)

### What's Included in MVP

✅ **Single Retail Archetype**: Seasonal Fashion Retail (12-week season)
✅ **Single Category**: Women's Dresses
✅ **Single Season**: Spring 2025 (12 weeks)
✅ **50 Stores** across 3 pre-defined clusters
✅ **Category-level forecasting** (not SKU-level)
✅ **Hierarchical allocation** (cluster → store)
✅ **3 Agents**: Demand, Inventory, Pricing
✅ **Orchestrator**: Basic workflow coordination
✅ **Forecasting Methods**: Hierarchical time-series (category-level)
✅ **Store Clustering**: Pre-defined clusters based on demographics + store attributes + fashion tier
✅ **Weekly Cadence**: Re-forecast weekly based on actuals
✅ **Markdown Logic**: Week 6 checkpoint with optional cluster differentiation

### What's NOT Included in MVP

❌ **Multi-archetype support** (only Archetype 1: Fashion)
❌ **Classifier Agent** (user manually configures for Archetype 1)
❌ **SKU-level forecasting** (category-level only)
❌ **Store-level granular forecasting** (hierarchical allocation instead)
❌ **Machine learning clustering** (use pre-defined clusters)
❌ **Advanced forecasting models** (basic ARIMA/Prophet, not deep learning)
❌ **Multi-season overlap** (one season at a time)
❌ **Store-to-store transfers** (only DC-to-store replenishment)
❌ **Dynamic pricing optimization** (fixed markdown depths: 15%, 30%, 50%)

### MVP Timeline: 12 Weeks

| Week | Milestone |
|------|-----------|
| 1-2 | Environment setup, data pipeline, explore historical fashion sales data |
| 3-4 | Demand Agent: Category-level time-series forecasting |
| 5-6 | Demand Agent: Store clustering + hierarchical allocation factors |
| 7-8 | Inventory Agent: Manufacturing order + hierarchical allocation logic |
| 9 | Inventory Agent: Weekly replenishment logic |
| 10 | Pricing Agent: Markdown trigger logic (Week 6 checkpoint) |
| 11 | Orchestrator: Workflow coordination, variance-triggered re-forecasts |
| 12 | Validation: Hindcast Spring 2024 (12-week season), measure MAPE |

---

## Data Requirements

### Input Data (Provided by User)

1. **Historical Sales Data** (2-3 years)
   - Fields: `date, category, store_id, quantity_sold, revenue`
   - Granularity: Daily (aggregated to category-level)
   - Coverage: All categories across all stores
   - **NOTE**: Category-level data only (not individual SKUs)

2. **Category Catalog**
   - Fields: `category, sub_category, season_start, season_end, typical_season_length`
   - Example: "Women's Dresses, Apparel, 2025-03-01, 2025-05-31, 12 weeks"

3. **Store Attributes**
   - Fields: `store_id, location, region, size_sqft, demographics, climate_zone, tier`
   - Used for: Store clustering and allocation factors

4. **External Factors** (Optional)
   - Fashion trends (runway trends, social media trends, influencer activity)
   - Weather data (temperature, precipitation by region)
   - Macro trends (consumer confidence, unemployment, GDP growth)
   - Seasonality indicators (holidays, promotional calendar, fashion weeks)

### Output Data (Generated by System)

1. **Forecasts**
   - Category-level demand (total + weekly curve)
   - Cluster distribution
   - Store allocation factors
   - Confidence scores

2. **Decisions**
   - Manufacturing orders
   - Store allocations (hierarchical)
   - Replenishment plans
   - Markdown recommendations

3. **Performance Metrics**
   - MAPE by week (category-level)
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
│Category │    │• Mfg     │    │• Markdown    │    │• Route   │
│forecast │    │  order   │    │  trigger     │    │  to      │
│Cluster  │    │• Hierarch│    │• Depth       │    │  arch.   │
│distrib. │    │  alloc.  │    │• Timing      │    │          │
│Store    │    │• Repl.   │    │• Optional    │    │          │
│factors  │    │          │    │  cluster     │    │          │
└─────────┘    └──────────┘    └──────────────┘    └──────────┘
     │              │                  │
     └──────────────┴──────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   DATA LAYER          │
        │• Historical sales DB  │
        │  (category-level)     │
        │• Store attributes     │
        │• Store clustering     │
        │• External APIs        │
        └───────────────────────┘
```

---

## Key Assumptions & Constraints

### Assumptions

1. **Historical data quality**: 2-3 years of clean sales data at category-level
2. **Category stability**: Category definitions remain consistent over time
3. **Store clustering**: Stores can be meaningfully clustered by fashion tier and attributes
4. **Weekly cadence is sufficient**: No need for daily re-forecasting (Archetype 1)
5. **DC-based replenishment**: No store-to-store transfers needed
6. **Single currency/country**: No cross-border complexity

### Constraints

1. **Requires historical data**: Only works for categories with 2+ years of sales history
2. **Category-level only**: Does not forecast individual SKUs
3. **Pre-defined clusters**: Requires upfront store clustering (manual or calculated)
4. **Computational cost**: Initial forecast takes ~30 minutes for large catalogs
5. **Human review**: High-value categories still need merchandiser approval
6. **Data latency**: Actuals may lag by 24-48 hours

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Poor store clustering** | Medium | Medium | Validate clusters with historical data; allow manual adjustment |
| **Insufficient historical data** | Medium | Medium | Require minimum 2 years; fall back to similar categories |
| **High forecast variance** | High | Medium | Weekly updates; variance-triggered re-forecasts |
| **Low user adoption** | Medium | High | Run parallel forecasts; prove accuracy before full rollout |
| **Data quality issues** | High | High | Implement validation checks; flag low-confidence forecasts |
| **Category definition ambiguity** | Low | Medium | Provide clear category taxonomy; allow user configuration |

---

## Comparison: Our Approach vs. Alternatives

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| **Our System (Hierarchical)** | ✅ Category-level accuracy<br>✅ Works for NEW + EXISTING<br>✅ Automated allocation<br>✅ Industry-aligned<br>✅ Fast runtime | ❌ Requires historical category data<br>❌ No SKU granularity<br>❌ Requires clustering | NEW + existing products in stable/seasonal retail |
| **Store-SKU-Week Forecasting** | ✅ Highly granular | ❌ Very noisy data<br>❌ Computationally expensive<br>❌ Lower accuracy<br>❌ Not industry practice | Research only; not practical |
| **Traditional Time-Series** | ✅ Simple<br>✅ Fast | ❌ Needs sales history per SKU<br>❌ No NEW products | Existing SKUs only |
| **Category Averages** | ✅ Very simple | ❌ Very inaccurate<br>❌ No store granularity | Quick rough estimates only |
| **Expert Judgment** | ✅ Incorporates intuition | ❌ Slow<br>❌ Not scalable | High-value, one-off items |

---

## How This System Extends to Other Retail Archetypes

The **core architecture remains the same** across all retail models - only **parameters change**:

| Component | Archetype 1 (Fashion) ⭐ MVP | Archetype 2 (Stable) | Archetype 3 (Continuous) |
|-----------|---------------------------|----------------------|--------------------------|
| **Forecasting Granularity** | Category-level | Category-level | Category-level |
| **Forecast Horizon** | 12 weeks | 26 weeks | 52 weeks (rolling) |
| **Replenishment Cadence** | Weekly | Bi-weekly | Daily/Weekly |
| **Holdback %** | 45% | 65% | 85% |
| **Markdown Trigger** | Week 6, <60% | Week 12, <50% | Rare |
| **Variance Threshold** | 20% | 15% | 10% |
| **Store Clustering** | Yes (3-5 clusters) | Yes (3-5 clusters) | Optional (2-3 clusters) |

**Extension Path:**
1. MVP proves concept with Archetype 1 (Fashion)
2. Post-MVP: Add parameter profiles for Archetypes 2 and 3
3. Future: Add Classifier Agent to auto-select archetype

---

## Next Steps

### Immediate (Week 1-2)
1. **Secure data access**: Historical sales data (category-level), store attributes
2. **Define store clusters**: Use demographics + attributes to create 3-5 clusters
3. **Define validation approach**: Use Fall 2024 data for hindcast testing
4. **Set up environment**: Python, data warehouse connection, compute resources

### Short-Term (Week 3-6)
1. **Build Demand Agent - Category Forecasting**: Time-series implementation, validate on "Women's Dresses" category
2. **Build Demand Agent - Clustering & Allocation**: Calculate cluster distribution + store factors
3. **Generate first forecasts**: Run hierarchical forecasting end-to-end

### Medium-Term (Week 7-12)
1. **Build Inventory Agent**: Manufacturing order + hierarchical allocation logic
2. **Build Inventory Agent**: Weekly replenishment logic
3. **Build Pricing Agent**: Markdown trigger logic (Week 6 checkpoint, 60% threshold)
4. **Orchestrator integration**: Connect all 3 agents, implement variance-triggered re-forecasts
5. **Validation**: Hindcast Spring 2024 (12 weeks), measure MAPE at category level

---

## Glossary

**Category-Level Forecasting**: Predicting aggregate demand for a product category (e.g., "Women's Dresses") rather than individual SKUs
**Hierarchical Allocation**: Top-down allocation approach (category → cluster → store)
**Store Clustering**: Grouping stores by similar characteristics (demographics, size, performance)
**Holdback Percentage**: % of inventory kept at DC instead of allocated to stores
**MAPE**: Mean Absolute Percentage Error - forecast accuracy metric
**Markdown**: Price reduction to accelerate sales (e.g., 15%, 30%, 50% off)
**Replenishment**: Periodic shipment from DC to stores to restock inventory
**Safety Stock**: Extra inventory buffer to avoid stockouts (e.g., 20% above forecast)
**Sell-Through Rate**: % of manufactured inventory sold by a given week
**Variance Threshold**: % deviation that triggers re-forecasting (e.g., 20%)

---

## Appendix: Sample Forecast Output (Complete)

```json
{
  "forecast_id": "DRESS_SP2025_001",
  "category": "Women's Dresses",
  "season": "Spring 2025",
  "forecast_date": "2024-09-15",
  "forecast_horizon_weeks": 12,

  "aggregate_demand": {
    "total_season_demand": 8000,
    "confidence_interval_lower": 7200,
    "confidence_interval_upper": 8800,
    "confidence_score": 0.75
  },

  "temporal_distribution": {
    "weekly_demand_curve": [
      {"week": 1, "demand": 650, "cumulative": 650},
      {"week": 2, "demand": 720, "cumulative": 1370},
      {"week": 3, "demand": 680, "cumulative": 2050},
      {"week": 6, "demand": 540, "cumulative": 3770},
      {"week": 12, "demand": 310, "cumulative": 8000}
    ],
    "peak_week": 2,
    "peak_demand": 720
  },

  "spatial_distribution": {
    "store_clusters": [
      {
        "cluster_id": "Fashion_Forward",
        "cluster_characteristics": {
          "median_income": 95000,
          "avg_store_size_sqft": 18000,
          "location_type": "Urban/High-end mall",
          "demographic_profile": "Fashion-conscious, trend-driven, young professionals"
        },
        "num_stores": 20,
        "demand_percentage": 0.40,
        "total_cluster_demand": 3200,
        "stores": [
          {
            "store_id": "Store_F1",
            "allocation_factor": 0.08,
            "allocation_method": "hybrid_70hist_30attr",
            "season_allocation": 256,
            "initial_allocation": 141,
            "dc_holdback": 115,
            "store_attributes": {
              "size_sqft": 20000,
              "location": "Downtown Mall",
              "tier": "A",
              "fashion_tier": "Premium"
            }
          },
          {
            "store_id": "Store_F2",
            "allocation_factor": 0.06,
            "season_allocation": 192,
            "initial_allocation": 106,
            "dc_holdback": 86
          }
        ]
      },
      {
        "cluster_id": "Mainstream",
        "cluster_characteristics": {
          "median_income": 65000,
          "avg_store_size_sqft": 14000,
          "location_type": "Suburban shopping centers",
          "demographic_profile": "Mid-market, balanced fashion preference"
        },
        "num_stores": 18,
        "demand_percentage": 0.35,
        "total_cluster_demand": 2800,
        "stores": [...]
      },
      {
        "cluster_id": "Value_Conscious",
        "cluster_characteristics": {
          "median_income": 45000,
          "avg_store_size_sqft": 10000,
          "location_type": "Outlet centers, secondary markets",
          "demographic_profile": "Value-conscious, price-driven"
        },
        "num_stores": 12,
        "demand_percentage": 0.25,
        "total_cluster_demand": 2000,
        "stores": [...]
      }
    ]
  },

  "inventory_recommendations": {
    "manufacturing_order": 9600,
    "safety_stock": 1600,
    "safety_stock_percentage": 0.20,
    "initial_allocation_total": 5280,
    "dc_holdback_total": 4320,
    "holdback_percentage": 0.45
  },

  "archetype_parameters": {
    "archetype": "FASHION_RETAIL",
    "season_length_weeks": 12,
    "replenishment_cadence": "weekly",
    "markdown_trigger_week": 6,
    "markdown_threshold": 0.60,
    "variance_threshold": 0.20,
    "holdback_percentage": 0.45
  },

  "forecasting_metadata": {
    "method": "hierarchical_time_series",
    "models_used": ["ARIMA", "seasonal_decomposition"],
    "clustering_method": "kmeans_demographics_fashion_tier",
    "allocation_method": "hybrid_70historical_30attributes",
    "data_sources": [
      "historical_sales_2022_2024_category_level",
      "store_attributes",
      "fashion_trends_social_media",
      "weather_data"
    ],
    "validation_MAPE": 0.22,
    "last_updated": "2024-09-15T14:30:00Z"
  }
}
```

---

**Document Owner**: Independent Study Project
**Last Updated**: 2025-10-11
**Version**: 3.1
**Related Documents**:
- [Operational Workflow v3](3_operational_workflow.md) ← TO BE CREATED
- [Key Parameters](../../05_Progress_Reports/Weekly_Supervisor_Meetings/key_parameter.md)
- [Original Technical Pitch](1_idea.md)

---

## Summary of Changes from v2.1

**Version 3.1 (2025-10-11)** - Industry-aligned hierarchical forecasting approach with Fashion MVP:
- ✅ **Changed to category-level forecasting** (was store-SKU-week) - addresses professor feedback on granularity
- ✅ **Implemented hierarchical allocation** (category → cluster → store) - industry-standard practice
- ✅ **Added store clustering approach** - pre-defined clusters based on demographics + attributes
- ✅ **Updated all 3 agents** to work with category-level forecasting + hierarchical allocation
- ✅ **Simplified computational requirements** - forecast runtime reduced from 2-4 hours to ~30 minutes
- ✅ **Maintained generic framework** - extends to all 3 archetypes with parameter changes only
- ✅ **Added research-backed justification** - aligned with retail industry best practices
- ✅ **Updated examples throughout** - all outputs now show category-level forecasting
- ✅ **Changed MVP focus to Archetype 1** - Fashion Retail (Women's Dresses, 12-week season) with clear extension path

**Rationale**:
- **Professor feedback**: Store-by-week granularity is too fine for retail practice
- **Research findings**: Industry uses top-down/middle-out forecasting, not bottom-up store-SKU-week
- **Accuracy**: Category-level forecasting is more accurate (less noisy data)
- **Computational feasibility**: Manageable runtime for real-world deployment
- **Industry alignment**: Matches how retailers actually forecast and allocate inventory
- **MVP Selection**: Fashion retail offers fast validation cycles (12 weeks), tests high-variance scenarios, and addresses critical markdown/margin pain points
