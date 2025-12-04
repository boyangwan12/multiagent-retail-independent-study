# Product Brief: Demand Forecasting & Inventory Allocation System

**Version:** 4.0
**Date:** 2025-10-16
**Status:** Parameter-Driven MVP Specification
**Focus:** Adaptive Category-Level Demand Forecasting with Agent-Autonomous Reasoning

---

## Executive Summary

We are building a **parameter-driven 3-agent system** that helps retailers forecast demand and optimize inventory allocation using **natural language configuration**. Users describe their season planning approach in free-form text, and the system automatically extracts key parameters. Agents then **autonomously reason** about how to adapt their behavior based on these parameters - no hardcoded logic, no rigid archetypes. The same system works for fast fashion (Zara-style 12-week aggressive allocation), stable catalog retail, or any custom scenario through LLM-powered agent reasoning.

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

### Our Solution: Parameter-Driven Agent System with LLM Reasoning

**Adaptive Approach**: Users describe their planning needs in natural language. The system extracts 5 key parameters via LLM, then agents autonomously reason about how to adapt their behavior - no hardcoded archetype logic.

**The 5 Key Parameters (User-Configurable)**:

1. **Forecast Horizon** - How many weeks to predict (e.g., "12 weeks")
2. **Season Length** - Start/end dates (e.g., "12 weeks starting March 1st")
3. **Replenishment Strategy** - Ongoing shipments or one-shot? (e.g., "No replenishment, allocate 100% upfront")
4. **DC Holdback Strategy** - How much to keep at DC (e.g., "0% holdback, send everything to stores")
5. **Markdown Timing** - When/how to trigger markdowns (e.g., "Week 6 checkpoint, 60% sell-through threshold")

**Example: Zara-Style Fast Fashion**

User input (natural language):
```
"I'm planning a 12-week spring fashion season starting March 1st.
Send all inventory to stores at launch with no DC holdback.
I don't want ongoing replenishment - just one initial allocation.
Check for markdown opportunities at week 6 if we're below 60% sell-through."
```

Extracted parameters:
- Forecast horizon: 12 weeks
- Season length: 12 weeks (2025-03-01 to 2025-05-23)
- Replenishment strategy: None (one-shot allocation)
- DC holdback: 0% (100% initial to stores)
- Markdown checkpoint: Week 6, 60% threshold

**Why This Approach:**
- ✅ **Generic system**: Same architecture adapts to any retail scenario via parameters
- ✅ **Agent autonomy**: Agents reason about parameter implications using LLM intelligence
- ✅ **No hardcoding**: No brittle if/else logic for different business models
- ✅ **Natural language**: Users describe needs conversationally, not through forms
- ✅ **Professor-validated**: Addresses feedback to make system truly adaptable

**How Agents Adapt to Parameters (Autonomous Reasoning)**:

Each agent receives the 5 parameters and uses LLM reasoning to adapt behavior:

**Demand Agent Example:**
- Receives: "No replenishment, 0% DC holdback"
- Reasons: *"Since there's no replenishment capability, I cannot correct forecast errors later. I should increase safety stock from 20% to 25% and use ensemble forecasting for maximum accuracy."*
- Executes: Adjusted forecast with 25% safety stock

**Inventory Agent Example:**
- Receives: "100% initial allocation, no replenishment"
- Reasons: *"No replenishment means no weekly shipment planning needed. I'll allocate entire manufacturing order to stores at Week 0 using hierarchical cluster → store allocation."*
- Executes: One-shot allocation, skips replenishment phase

**Pricing Agent Example:**
- Receives: "Week 6 markdown checkpoint, 60% threshold"
- Reasons: *"I'll monitor until Week 6, then check sell-through. If below 60%, apply Gap × Elasticity markdown and trigger re-forecast."*
- Executes: Markdown logic at specified timing

**3 Agents + Orchestrator**:
1. **Demand Agent** - Forecasts category-level demand, adapts safety stock based on replenishment strategy
2. **Inventory Agent** - Allocates to stores, conditionally plans replenishment based on parameters
3. **Pricing Agent** - Monitors sell-through, triggers markdowns per user-specified timing
4. **Orchestrator** - Coordinates agents, passes parameter context, triggers re-forecasts

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

## Target Users & Retail Scenarios

### Parameter-Driven System (No Hardcoded Archetypes)

The system adapts to **any retail scenario** through natural language parameter configuration. Users describe their planning approach in free-form text, and agents autonomously reason about implications - no predefined archetypes.

### Example Scenario: Zara-Style Fast Fashion ⭐ **[MVP Test Case]**

**Business Context:**
- **Retailer**: Fast fashion (Zara, H&M style)
- **Season**: 12-week Spring 2025 (March 1 - May 23)
- **Strategy**: Aggressive sell-through, minimal holdback, single allocation push

**User Input (Natural Language):**
```
"I'm planning a 12-week spring fashion season starting March 1st.
Send all inventory to stores at launch with no DC holdback.
I don't want ongoing replenishment - just one initial allocation.
Check for markdown opportunities at week 6 if we're below 60% sell-through."
```

**Extracted Parameters:**
- Forecast horizon: 12 weeks
- Season length: 2025-03-01 to 2025-05-23
- Replenishment strategy: None (one-shot allocation)
- DC holdback: 0% (100% to stores)
- Markdown checkpoint: Week 6, 60% threshold

**How Agents Adapt:**
- **Demand Agent**: Increases safety stock to 25% (no replenishment correction possible)
- **Inventory Agent**: Allocates 100% at Week 0, skips weekly replenishment phase
- **Pricing Agent**: Monitors until Week 6, applies markdown if <60% sell-through

**Why This Scenario for MVP:**
- ✅ **High business impact**: Fashion retail has critical markdown/overstock problems (PP-016: $500K margin loss)
- ✅ **Fast validation cycle**: 12-week seasons allow rapid testing
- ✅ **Tests agent reasoning**: Agents must adapt to "no replenishment" constraint
- ✅ **Clear success metrics**: Aggressive strategy makes forecast accuracy critical

### Other Supported Scenarios (Same System, Different Parameters)

The system supports diverse retail models through parameter variation:

**Scenario 2: Conservative Furniture Retail**
```
"Planning 26-week summer collection starting May 1st.
Hold 65% at DC for flexibility, replenish stores bi-weekly.
Consider markdowns at week 12 if below 50% sell-through."
```
- Agents adapt: Higher DC holdback, bi-weekly replenishment planning, later markdown timing

**Scenario 3: Custom Boutique Retail**
```
"8-week holiday collection starting November 1st.
Send 80% to stores initially, hold 20% at DC.
Weekly replenishment. No markdowns - premium positioning."
```
- Agents adapt: Balanced allocation, weekly replenishment, Pricing Agent skips markdown phase

**Key Principle**: No scenario requires code changes - agents reason about parameters and adapt.

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
- Method: Ensemble forecasting - Prophet + ARIMA run in parallel, results averaged
- Prophet forecast and ARIMA forecast both generated, then averaged with equal weights (no confidence weighting)
- Adjustment factors: Seasonality, trends, external factors (fashion trends, weather, consumer sentiment)
- Output: Total season demand (e.g., 8,000 women's dresses)

**Step 2: Temporal Distribution (Weekly Demand Curve)**
- Extract typical weekly demand pattern from historical data
- Adjust for known events (holidays, promotions, seasonality)
- Output: Weekly demand curve [250, 280, 260, 240, ...]

**Step 3: Store Clustering**
- Method: K-means clustering (K=3) with StandardScaler normalization
- Features used (7 total):
  1. **avg_weekly_sales_12mo** (MOST IMPORTANT - captures store performance)
  2. **store_size_sqft** (physical capacity)
  3. **median_income** (customer purchasing power)
  4. **location_tier** (A=3, B=2, C=1 - urban/suburban/rural)
  5. **fashion_tier** (Premium=3, Mainstream=2, Value=1 - fashion positioning)
  6. **store_format** (Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1)
  7. **region** (Northeast=1, Southeast=2, Midwest=3, West=4)
- Algorithm: K-means++ initialization with StandardScaler normalization
- All features are standardized (mean=0, std=1) before clustering
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
- **Parameter context** (5 key parameters extracted from user natural language input)

**Parameter-Driven Adaptation Examples**:

*Scenario: "No replenishment" parameter*
- Agent reasoning: *"No replenishment means I cannot correct forecast errors later. Increase safety stock from 20% to 25%."*
- Adjustment: `safety_stock = 0.25` instead of default `0.20`

*Scenario: "Bi-weekly replenishment" parameter*
- Agent reasoning: *"Bi-weekly cadence means slower reaction time. Use 2-week smoothing in demand curve."*
- Adjustment: Apply 2-week moving average to weekly curve

**Outputs**:
```json
{
  "total_season_demand": 8000,
  "prophet_forecast": 8200,
  "arima_forecast": 7800,
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
  "forecasting_method": "ensemble_prophet_arima"
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
    remaining_season_allocation = store_season_total - total_shipped_so_far
    remaining_weeks = 12 - current_week

    # Calculate expected need for next period
    next_week_forecast = remaining_season_allocation / remaining_weeks

    # Simple replenishment formula
    replenishment_qty = max(0, next_week_forecast - current_inventory)

    if replenishment_qty > 0 and dc_inventory > 0:
        ship_from_dc(store, min(replenishment_qty, dc_inventory))

# Note: If variance >20%, Orchestrator triggers re-forecast
```

**Inputs**:
- Category-level forecast from Demand Agent
- Store allocation factors (hierarchical)
- Current store inventory levels
- DC inventory levels
- Actual sales data (for replenishment adjustments)
- **Parameter context** (replenishment strategy, DC holdback %, season length)

**Parameter-Driven Adaptation Examples**:

*Scenario: "No replenishment, 0% DC holdback" (Zara-style)*
- Agent reasoning: *"No replenishment means no weekly shipment planning. Allocate 100% of manufacturing order at Week 0."*
- Adjustment: Skip replenishment phase entirely, send all units to stores at launch

*Scenario: "65% DC holdback, bi-weekly replenishment" (Furniture retail)*
- Agent reasoning: *"High holdback gives flexibility. Plan bi-weekly shipments instead of weekly."*
- Adjustment: Calculate replenishment needs every 2 weeks instead of weekly

**Outputs**:
- Manufacturing order quantity
- Week 0 allocation by store (hierarchical)
- Periodic replenishment plan by store

---

### Agent 3: Pricing Agent

**What It Decides**:
1. **Markdown Trigger** (should we apply a price reduction?)
2. **Markdown Depth** (how much to discount: 5%, 10%, 20%, 40%?)
3. **Markdown Timing** (which week to apply it?)
4. **Uniform across stores** (no cluster-level differentiation in MVP)

**How It Works**:

**Category-Level Sell-Through Tracking**
```python
# Mid-season checkpoint (Week 6 for Archetype 1)
total_manufactured = 9600
total_sold = sum(actual_sales_weeks_1_to_6)  # e.g., 5280
sell_through_rate = total_sold / total_manufactured  # 0.55 (55%)

# Target: 60% by week 6 (Archetype 1 parameter)
target_sell_through = 0.60

# Gap × Elasticity Formula
gap = target_sell_through - sell_through_rate  # 0.05 (5 percentage points)
elasticity_coefficient = 2.0  # Tunable parameter

# Calculate markdown
markdown_raw = gap * elasticity_coefficient  # 0.05 × 2.0 = 0.10 (10%)
markdown_rounded = round(markdown_raw * 20) / 20  # Round to nearest 5%
markdown_depth = min(markdown_rounded, 0.40)  # Cap at 40%

# Examples:
# 58% sell-through → gap=0.02 → 2% × 2.0 = 4% → rounds to 5%
# 50% sell-through → gap=0.10 → 10% × 2.0 = 20% markdown
# 40% sell-through → gap=0.20 → 20% × 2.0 = 40% markdown (capped)

if gap > 0:  # Below target
    recommend_markdown = True
    apply_markdown_to_all_stores(markdown_depth)
```

**Post-Markdown Action**: Trigger Demand Agent to re-forecast weeks 7-12 with new price

**Inputs**:
- Actual sales data (weeks 1-N)
- Manufacturing order quantity
- Current inventory levels (by store/cluster)
- **Parameter context** (markdown timing, sell-through threshold, season length)

**Parameter-Driven Adaptation Examples**:

*Scenario: "Week 6 checkpoint, 60% threshold" (Zara-style)*
- Agent reasoning: *"Check sell-through at Week 6. If <60%, apply Gap × Elasticity markdown."*
- Adjustment: Monitor until Week 6, then evaluate

*Scenario: "Week 12 checkpoint, 50% threshold" (Furniture retail)*
- Agent reasoning: *"Later checkpoint with lower threshold - less aggressive markdown strategy."*
- Adjustment: Wait until Week 12, use 50% as threshold instead of 60%

*Scenario: "No markdowns - premium positioning" (Luxury boutique)*
- Agent reasoning: *"No markdown parameter specified. Skip pricing adjustments entirely."*
- Adjustment: Pricing Agent remains idle, no markdown phase

**Outputs**:
- Markdown recommendation (yes/no)
- Suggested markdown depth (%) - uniform across all stores
- Timing (which week)
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

### Business Impact (Secondary)

| Metric | 6-Month Target | 12-Month Target |
|--------|---------------|-----------------|
| **Stockout Reduction** | 15% | 25% |
| **Overstock Reduction** | 10% | 20% |
| **Markdown Cost Reduction** | 10% | 15% |
| **Inventory Turnover Improvement** | 8% | 15% |

### System Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Workflow Runtime** | <60 seconds | Full 3-agent workflow (Demand → Inventory → Pricing) |
| **Re-forecast Trigger Accuracy** | 90%+ | Correctly identify variance >20% |
| **Human Approval Rate** | Track | % of manufacturing orders approved without modification |
| **Uptime** | 99%+ | System availability |

---

## MVP Scope (Proof of Concept)

### What's Included in MVP

✅ **Parameter-Driven Architecture**: Natural language input → LLM extracts 5 parameters → Agents adapt autonomously
✅ **Zara-Style Test Scenario**: 12-week fast fashion (0% holdback, no replenishment, Week 6 markdown)
✅ **Single Category**: Auto-detected from CSV upload (e.g., Women's Dresses, Men's Shirts, Accessories)
✅ **Single Season**: Spring 2025 (configurable via parameters)
✅ **50 Stores** across 3 clusters (K-means clustering)
✅ **Category-level forecasting** (not SKU-level)
✅ **Hierarchical allocation** (cluster → store)
✅ **3 Agents with LLM Reasoning**: Demand, Inventory, Pricing adapt based on parameter context
✅ **Orchestrator**: Workflow coordination + parameter context passing
✅ **Forecasting Methods**: Ensemble (Prophet + ARIMA parallel, averaged)
✅ **Store Clustering**: K-means clustering (7 features, K=3, StandardScaler normalization)
✅ **Adaptive Cadence**: Re-forecast timing based on parameters (weekly/bi-weekly/etc.)
✅ **Markdown Logic**: Gap × Elasticity formula (elasticity=2.0, tunable, 5% rounding, 40% cap)
✅ **Agentic Features**: Context-rich handoffs, dynamic re-forecast enabling, WebSocket real-time updates, human-in-the-loop (Modify/Accept), **LLM-powered agent reasoning**

### What's NOT Included in MVP

❌ **Multi-scenario parallel testing** (test one parameter set at a time)
❌ **Parameter validation UI** (assumes LLM extracts valid parameters)
❌ **SKU-level forecasting** (category-level only)
❌ **Store-level granular forecasting** (hierarchical allocation instead)
❌ **Multi-season overlap** (one season at a time)
❌ **Store-to-store transfers** (only DC-to-store replenishment)
❌ **Confidence scoring** (removed for simplicity)
❌ **Cluster-specific markdowns** (uniform across stores)
❌ **Parameter optimization** (no automated A/B testing of parameter combinations)

### MVP Timeline: 12 Weeks

| Week | Milestone |
|------|-----------|
| 1-2 | Environment setup, data pipeline, explore historical fashion sales data |
| 3-4 | Demand Agent: Category-level ensemble forecasting (Prophet + ARIMA) |
| 5-6 | Demand Agent: K-means clustering (7 features) + hierarchical allocation factors |
| 7-8 | Inventory Agent: Manufacturing order + hierarchical allocation logic |
| 9 | Inventory Agent: Weekly replenishment logic (simple formula) |
| 10 | Pricing Agent: Markdown trigger logic (Gap × Elasticity) |
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

2. **Category Selection**
   - System auto-detects available categories from historical sales CSV
   - User selects one category from dropdown (e.g., "Women's Dresses", "Men's Shirts", "Accessories")
   - System extracts all historical data for selected category
   - No predefined category catalog required

3. **Store Attributes**
   - Fields: `store_id, location, region, size_sqft, median_income, location_tier, fashion_tier, store_format`
   - Used for: K-means clustering (7 features) and allocation factors

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
   - Prophet and ARIMA forecasts

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
│Ensemble │    │• Hierarch│    │• Gap ×       │    │  arch.   │
│Prophet+ │    │  alloc.  │    │  Elasticity  │    │          │
│ARIMA    │    │• Simple  │    │• Uniform     │    │          │
│K-means  │    │  repl.   │    │  markdowns   │    │          │
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
        │• K-means clustering   │
        │• External APIs        │
        └───────────────────────┘
```

### Technology Stack

**Agent Framework**: OpenAI Agents SDK v0.3.3+ (production-ready)
**LLM**: Azure OpenAI Service (gpt-4o-mini via Responses API)
**Package Manager**: UV (10-100x faster than pip)
**Backend**: Python 3.11+ + FastAPI + SQLite
**Frontend**: React 18 + TypeScript + Vite + Shadcn/ui + TanStack Query
**ML/Forecasting**: Prophet, pmdarima (ARIMA), scikit-learn (K-means, StandardScaler)

### Agentic Features (OpenAI Agents SDK)

- **Context-rich handoffs**: Pass forecast/allocation objects directly between agents (no database queries)
- **Dynamic handoff enabling**: Re-forecast handoff enabled dynamically when variance >20%
- **Human-in-the-loop**: Approval modals (Modify iterative + Accept, no Reject)
- **Real-time updates**: WebSocket streaming of agent progress
- **Guardrails**: Automatic output validation (fail-fast on errors)
- **Sessions**: Automatic conversation history management

---

## Key Assumptions & Constraints

### Assumptions

1. **Historical data quality**: 2-3 years of clean sales data at category-level
2. **Category stability**: Category definitions remain consistent over time
3. **Store clustering**: Stores can be meaningfully clustered by 7 features (K-means)
4. **Weekly cadence is sufficient**: No need for daily re-forecasting (Archetype 1)
5. **DC-based replenishment**: No store-to-store transfers needed
6. **Single currency/country**: No cross-border complexity

### Constraints

1. **Requires historical data**: Only works for categories with 2+ years of sales history
2. **Category-level only**: Does not forecast individual SKUs
3. **K-means clustering**: Requires 7 features (avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region)
4. **Computational cost**: Initial forecast takes <60 seconds for full 3-agent workflow
5. **Human review**: High-value categories still need merchandiser approval
6. **Data latency**: Actuals may lag by 24-48 hours

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Poor store clustering** | Medium | Medium | Validate clusters with historical data; K-means++ initialization |
| **Insufficient historical data** | Medium | Medium | Require minimum 2 years; fall back to similar categories |
| **High forecast variance** | High | Medium | Weekly updates; variance-triggered re-forecasts (>20%) |
| **Low user adoption** | Medium | High | Run parallel forecasts; prove accuracy before full rollout |
| **Data quality issues** | High | High | Implement validation checks; StandardScaler normalization |
| **Category definition ambiguity** | Low | Medium | Provide clear category taxonomy; allow user configuration |

---

## Comparison: Our Approach vs. Alternatives

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| **Our System (Hierarchical)** | ✅ Category-level accuracy<br>✅ Works for NEW + EXISTING<br>✅ Automated allocation<br>✅ Industry-aligned<br>✅ Fast runtime (<60s) | ❌ Requires historical category data<br>❌ No SKU granularity<br>❌ Requires 7 features for clustering | NEW + existing products in stable/seasonal retail |
| **Store-SKU-Week Forecasting** | ✅ Highly granular | ❌ Very noisy data<br>❌ Computationally expensive<br>❌ Lower accuracy<br>❌ Not industry practice | Research only; not practical |
| **Traditional Time-Series** | ✅ Simple<br>✅ Fast | ❌ Needs sales history per SKU<br>❌ No NEW products | Existing SKUs only |
| **Category Averages** | ✅ Very simple | ❌ Very inaccurate<br>❌ No store granularity | Quick rough estimates only |
| **Expert Judgment** | ✅ Incorporates intuition | ❌ Slow<br>❌ Not scalable | High-value, one-off items |

---

## How This System Adapts to Any Retail Scenario

The **core architecture never changes** - agents autonomously adapt based on parameters:

### Parameter Variation Examples

| Parameter | Zara-Style Fast Fashion | Furniture Retail | Luxury Boutique |
|-----------|------------------------|------------------|-----------------|
| **Forecast Horizon** | 12 weeks | 26 weeks | 8 weeks |
| **Replenishment Strategy** | None (one-shot) | Bi-weekly | Weekly |
| **DC Holdback %** | 0% (all to stores) | 65% | 20% |
| **Markdown Checkpoint** | Week 6, <60% | Week 12, <50% | None (no markdowns) |

### How Agents Adapt (Same Code, Different Behavior)

**Zara-Style Parameters → Agent Behavior:**
- Demand Agent: 25% safety stock (no replenishment correction)
- Inventory Agent: Allocates 100% at Week 0, skips replenishment phase
- Pricing Agent: Monitors Week 6, applies markdown if <60%

**Furniture Retail Parameters → Agent Behavior:**
- Demand Agent: 20% safety stock (bi-weekly corrections available)
- Inventory Agent: 35% initial, 65% holdback, plans bi-weekly shipments
- Pricing Agent: Waits until Week 12, uses 50% threshold

**Luxury Boutique Parameters → Agent Behavior:**
- Demand Agent: Standard forecasting
- Inventory Agent: 80% initial, 20% holdback, weekly replenishment
- Pricing Agent: Skips markdown phase entirely (no discount strategy)

**Extension Path:**
1. MVP validates agent reasoning with Zara-style parameters
2. Test other parameter combinations (no code changes needed)
3. Future: Add parameter recommendation engine based on historical performance

---

## Next Steps

### Immediate (Week 1-2)
1. **Secure data access**: Historical sales data (category-level), store attributes (7 features)
2. **Define store clusters**: Use K-means (K=3) with 7 features and StandardScaler normalization
3. **Define validation approach**: Use Fall 2024 data for hindcast testing
4. **Set up environment**: Python 3.11+, UV, OpenAI Agents SDK, FastAPI, React

### Short-Term (Week 3-6)
1. **Build Demand Agent - Ensemble Forecasting**: Prophet + ARIMA implementation, validate on auto-detected category (e.g., "Women's Dresses")
2. **Build Demand Agent - K-means Clustering & Allocation**: Calculate cluster distribution + store factors
3. **Generate first forecasts**: Run hierarchical forecasting end-to-end

### Medium-Term (Week 7-12)
1. **Build Inventory Agent**: Manufacturing order + hierarchical allocation logic
2. **Build Inventory Agent**: Weekly replenishment logic (simple formula)
3. **Build Pricing Agent**: Markdown trigger logic (Gap × Elasticity, Week 6 checkpoint, 60% threshold)
4. **Orchestrator integration**: Connect all 3 agents, implement variance-triggered re-forecasts (>20%)
5. **Validation**: Hindcast Spring 2024 (12 weeks), measure MAPE at category level

---

## Glossary

**Category-Level Forecasting**: Predicting aggregate demand for a product category (e.g., "Women's Dresses") rather than individual SKUs
**Hierarchical Allocation**: Top-down allocation approach (category → cluster → store)
**Store Clustering**: Grouping stores using K-means (K=3) based on 7 features with StandardScaler normalization
**Holdback Percentage**: % of inventory kept at DC instead of allocated to stores
**MAPE**: Mean Absolute Percentage Error - forecast accuracy metric
**Markdown**: Price reduction to accelerate sales (calculated via Gap × Elasticity formula)
**Replenishment**: Periodic shipment from DC to stores to restock inventory (simple formula: forecast - inventory)
**Safety Stock**: Extra inventory buffer to avoid stockouts (e.g., 20% above forecast)
**Sell-Through Rate**: % of manufactured inventory sold by a given week
**Variance Threshold**: % deviation that triggers re-forecasting (e.g., 20%)
**Gap × Elasticity**: Markdown formula where `Markdown = (target - actual) × elasticity_coefficient`
**Ensemble Forecasting**: Prophet + ARIMA run in parallel, results averaged

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
    "prophet_forecast": 8200,
    "arima_forecast": 7800,
    "forecasting_method": "ensemble_prophet_arima"
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
    "method": "ensemble_prophet_arima",
    "models_used": ["prophet", "arima"],
    "clustering_method": "kmeans_7features_standardscaled",
    "clustering_features": [
      "avg_weekly_sales_12mo",
      "store_size_sqft",
      "median_income",
      "location_tier",
      "fashion_tier",
      "store_format",
      "region"
    ],
    "allocation_method": "hybrid_70historical_30attributes",
    "markdown_formula": "gap_x_elasticity_2.0",
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
**Last Updated**: 2025-10-16
**Version**: 4.0
**Related Documents**:
- [Process Workflow v3.3](2_process_workflow_v3.3.md)
- [Technical Architecture v3.3](3_technical_architecture_v3.3.md)
- [PRD v3.3](4_prd_v3.3.md)
- [Frontend Spec v3.3](5_front-end-spec_v3.3.md)

---

## Summary of Changes

### Version 4.0 (2025-10-16) - Parameter-Driven Architecture

**Major Paradigm Shift**: From hardcoded "Archetype 1" to parameter-driven agent-autonomous system

#### 1. Added Parameter-Driven Architecture
- **New**: Natural language input for season planning configuration
- **New**: LLM extraction of 5 key parameters (forecast horizon, season length, replenishment strategy, DC holdback, markdown timing)
- **New**: Agents receive parameter context and autonomously reason about adaptations
- **Removed**: Hardcoded "Archetype 1/2/3" logic
- **Impact**: Single system adapts to any retail scenario via parameters

#### 2. Agent Autonomous Reasoning (LLM-Powered)
- **New**: Each agent uses LLM to reason about parameter implications
- **Example**: Demand Agent sees "no replenishment" → increases safety stock to 25%
- **Example**: Inventory Agent sees "0% holdback" → skips replenishment phase entirely
- **Example**: Pricing Agent sees "no markdowns" → remains idle
- **Impact**: No brittle if/else logic, agents adapt intelligently

#### 3. Updated Primary Example: Zara-Style Fast Fashion
- **Changed**: "Archetype 1" → "Zara-Style Test Scenario"
- **User Input**: "12-week season, send all inventory to stores at launch, no DC holdback, no replenishment, markdown at Week 6 if <60%"
- **Parameters Extracted**: forecast_horizon=12w, season_length=12w, replenishment=none, dc_holdback=0%, markdown_checkpoint=Week6_60%
- **Impact**: Clear, concrete example instead of abstract archetype

#### 4. Removed Archetype Classification System
- **Removed**: "Archetype 1: Fashion", "Archetype 2: Stable Catalog", "Archetype 3: Continuous"
- **Removed**: Archetype comparison table with fixed parameters
- **Removed**: "Classifier Agent (4th Agent)" from future roadmap
- **Replaced With**: Parameter variation examples showing how same system adapts
- **Impact**: More flexible, less prescriptive, truly generic system

#### 5. Added Agent Adaptation Examples Throughout
- **New**: Each agent section includes "Parameter-Driven Adaptation Examples"
- **New**: Shows agent reasoning process (input → reasoning → adjustment → execution)
- **New**: Multiple scenario examples (Zara-style, Furniture, Luxury boutique)
- **Impact**: Clear demonstration of how agent autonomy works

#### 6. Updated MVP Scope
- **Changed**: "Single Retail Archetype" → "Parameter-Driven Architecture"
- **Added**: "LLM-powered agent reasoning" to agentic features
- **Added**: "Zara-Style Test Scenario" as primary test case
- **Added**: "Parameter context passing" to Orchestrator responsibilities
- **Removed**: "Multi-archetype support" from NOT included list
- **Impact**: MVP scope reflects new parameter-driven approach

#### 7. Updated "How System Extends" Section
- **Removed**: Fixed archetype parameter table
- **Added**: Parameter variation examples (Zara vs Furniture vs Boutique)
- **Added**: "How Agents Adapt (Same Code, Different Behavior)" subsection
- **Changed**: Extension path from "add archetype profiles" → "test parameter combinations"
- **Impact**: Emphasizes agent autonomy, not hardcoded profiles

#### 8. Technical Architecture Alignment
- **Added**: Parameter extraction via LLM mentioned throughout
- **Added**: Agent context passing as core mechanism
- **Updated**: Orchestrator now passes parameter context to all agents
- **Impact**: Document reflects implementation reality

### Overall Impact of v3.3

- ✅ **More Generic**: No hardcoded retail scenarios, truly adaptable system
- ✅ **Agent Autonomy**: LLM-powered reasoning replaces brittle conditional logic
- ✅ **Professor Feedback**: Addresses concern about making system truly flexible
- ✅ **Natural Language**: Users describe needs conversationally, not through forms
- ✅ **No Code Changes**: Testing new scenarios requires only parameter changes
- ✅ **Clear Examples**: Zara-style fast fashion as concrete test case
- ✅ **Implementation-Ready**: Specifications align with parameter-driven architecture

### Rationale for v3.3 Update

This version reflects professor feedback: *"The system should be generic, not hardcoded to Archetype 1. Make agents adapt autonomously based on user-provided parameters."* The v3.3 update removes all archetype hardcoding and implements true parameter-driven, agent-autonomous architecture using LLM reasoning.

---

## Summary of Changes from v3.1

**Version 3.2 (2025-10-12)** - Updated to reflect technical architecture decisions:

### 1. Removed Confidence Scoring (Simplified MVP)
- **Removed**: `confidence_score`, `confidence_interval_lower`, `confidence_interval_upper` fields from outputs
- **Removed**: "Confidence Calibration" success metric (was 80%+ target)
- **Rationale**: User decision - "too complicated, I want to just skip this"
- **Impact**: Simplified system, cleaner outputs, reduced complexity

### 2. Updated to Ensemble Forecasting (Prophet + ARIMA)
- **Changed**: Forecasting method from `hierarchical_time_series` to `ensemble_prophet_arima`
- **Added**: Prophet and ARIMA forecasts run in parallel, results averaged (equal weights)
- **Added**: `prophet_forecast` and `arima_forecast` fields in outputs
- **Rationale**: Research-backed approach, architecture document specifies parallel Prophet + ARIMA
- **Impact**: More robust forecasting, reduced single-model bias

### 3. Updated Store Clustering to 7 Features (Research-Backed)
- **Changed**: From pre-defined/vague clustering to K-means with 7 specific features
- **Features**: avg_weekly_sales_12mo (MOST IMPORTANT), store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
- **Algorithm**: K-means++ initialization with StandardScaler normalization
- **Rationale**: User approved research-backed best practices from architecture document
- **Impact**: More accurate, data-driven clustering; reproducible results

### 4. Simplified Replenishment Logic
- **Removed**: Variance-based adjustment formula (`variance × expected_1week_sales`)
- **Changed to**: Simple formula `replenishment = max(0, forecast - inventory)`
- **Note**: Relies on 20% variance re-forecast trigger at orchestrator level
- **Rationale**: User chose "Option C" - simple formula + re-forecast trigger
- **Impact**: Cleaner code, easier to understand, relies on re-forecasting for variance handling

### 5. Gap × Elasticity Markdown Formula
- **Removed**: Fixed markdown table (if/elif/else with 15%/30%/50% depths)
- **Changed to**: `Markdown = Gap × Elasticity` where elasticity=2.0 (tunable)
- **Added**: 5% rounding, 40% cap
- **Removed**: Cluster-specific markdown differentiation (uniform across all stores)
- **Rationale**: User chose simplified Gap × Elasticity formula from architecture
- **Impact**: More flexible, tunable, easier to understand

### 6. Added Tech Stack Details
- **Agent Framework**: OpenAI Agents SDK v0.3.3+ (NOT LangChain)
- **LLM**: Azure OpenAI Service (gpt-4o-mini via Responses API)
- **Package Manager**: UV (10-100x faster than pip)
- **Backend**: Python 3.11+ + FastAPI + SQLite
- **Frontend**: React 18 + TypeScript + Vite + Shadcn/ui + TanStack Query
- **Agentic Features**: Context-rich handoffs, dynamic enabling, WebSocket, human-in-the-loop
- **Rationale**: Reflect all tech decisions from technical architecture document
- **Impact**: Implementation-ready specifications

### 7. Updated Success Metrics
- **Removed**: "Confidence Calibration" metric (was 80%+)
- **Changed**: Runtime from "<30 minutes" to "<60 seconds" for full 3-agent workflow
- **Added**: "Re-forecast Trigger Accuracy" (90%+ - correctly identify variance >20%)
- **Added**: "Human Approval Rate" (track % modify vs accept)
- **Rationale**: Align metrics with architecture decisions and agentic features
- **Impact**: More realistic, measurable, and implementation-focused metrics

### 8. Updated MVP Scope
- **Updated**: "Ensemble (Prophet + ARIMA parallel, averaged)"
- **Updated**: "K-means clustering (7 features, K=3, StandardScaler)"
- **Updated**: "Gap × Elasticity formula (elasticity=2.0, tunable)"
- **Added**: Agentic features (context-rich handoffs, dynamic enabling, WebSocket, HITL)
- **Removed**: "Confidence scoring" from included scope
- **Removed**: "Cluster-specific markdowns" from included scope
- **Rationale**: Reflect actual implementation decisions
- **Impact**: Clear MVP boundaries, realistic expectations

### 9. Updated Sample Output JSON
- **Removed**: All confidence fields (`confidence_score`, `confidence_interval_lower/upper`)
- **Added**: `prophet_forecast`, `arima_forecast`, `forecasting_method: "ensemble_prophet_arima"`
- **Updated**: `models_used: ["prophet", "arima"]`
- **Added**: `clustering_method: "kmeans_7features_standardscaled"`
- **Added**: `clustering_features` array with 7 feature names
- **Added**: `markdown_formula: "gap_x_elasticity_2.0"`
- **Rationale**: Sample output must match actual implementation
- **Impact**: Developers can use sample as reference for implementation

### Overall Impact
- ✅ **Simplified**: Removed confidence scoring complexity
- ✅ **More robust**: Ensemble forecasting (Prophet + ARIMA)
- ✅ **Data-driven**: K-means clustering with 7 research-backed features
- ✅ **Cleaner logic**: Simple replenishment formula + re-forecast trigger
- ✅ **More flexible**: Gap × Elasticity markdown formula (tunable)
- ✅ **Implementation-ready**: Complete tech stack and agentic features specified
- ✅ **Better metrics**: <60 second runtime, re-forecast accuracy, human approval rate
- ✅ **Realistic MVP**: Clear scope with what's included/excluded
- ✅ **Accurate samples**: JSON output matches implementation

---

**Rationale for v3.2 Update**:
All changes reflect technical architecture decisions made during Week 4 development planning session. This version is now **implementation-ready** and fully aligned with the technical architecture document (v1.0).
