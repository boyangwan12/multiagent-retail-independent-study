# Product Requirements Document
## Demand Forecasting & Inventory Allocation System

---

**Version:** 1.0
**Date:** 2025-10-10
**Status:** Draft
**Archetype Focus:** Archetype 2 - Stable Catalog Retail (MVP)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Goals & Success Metrics](#2-goals--success-metrics)
3. [User Personas](#3-user-personas)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [User Stories](#6-user-stories)
7. [Data Requirements](#7-data-requirements)
8. [Technical Architecture](#8-technical-architecture)
9. [Milestones & Timeline](#9-milestones--timeline)
10. [Risks & Mitigation](#10-risks--mitigation)
11. [Assumptions & Dependencies](#11-assumptions--dependencies)
12. [Appendix](#12-appendix)

---

# 1. Executive Summary

## 1.1 Product Vision

Build a **3-agent demand forecasting and inventory allocation system** that predicts store-week granular demand and optimizes inventory decisions for retailers. The system addresses critical pain points identified in user research: inaccurate forecasting (PP-001), location-specific allocation failures (PP-002, PP-015), and late markdown decisions causing margin loss (PP-016).

## 1.2 Problem Statement

Based on interviews with 5 retail practitioners, retailers face:

- **Inaccurate demand forecasting**: Traditional ML models lack accuracy and agility (PP-001)
- **Location-specific allocation failures**: Store-level demand patterns not captured → inventory misallocation (PP-002, PP-015)
- **Late markdown decisions**: Data lag and inaccurate forecasts → $500K annual margin loss (PP-016)
- **Inventory optimization challenges**: Balancing overstock vs understock requires accurate store-week forecasting (PP-028)
- **Long lead times with uncertainty**: Must commit to manufacturing quantities 3-6 months in advance

## 1.3 Solution Overview

A **parameter-driven 3-agent system** that:

- **Predicts**: `demand_by_store_by_week` matrix (e.g., 50 stores × 26 weeks = 1,300 predictions per SKU)
- **Decides**: Manufacturing orders, initial allocation, bi-weekly replenishment, markdown timing
- **Adapts**: Configurable for different retail archetypes (fashion, furniture, CPG) via parameters

**MVP Validation**: Archetype 2 - Stable Catalog Retail (furniture, 26-week season, 50 stores, 50 SKUs)

---

# 2. Goals & Success Metrics

## 2.1 Business Goals

| Goal | Description | Target |
|------|-------------|--------|
| **Reduce forecast error** | Improve MAPE vs baseline methods | <20% MAPE |
| **Reduce stockouts** | Better store-level allocation | 15-25% reduction |
| **Reduce overstock** | Optimize manufacturing orders | 10-20% reduction |
| **Improve markdown timing** | Timely sell-through checkpoints | 10-15% margin improvement |
| **Support manufacturing decisions** | 3-month advance forecasting | 95%+ planner confidence |

## 2.2 Success Metrics (MVP)

| Metric | MVP Target | Measurement Method |
|--------|-----------|-------------------|
| **MAPE (Store-Week)** | <20% | Hindcast on Fall/Winter 2024 data |
| **Bias** | ±5% | Check for systematic over/under-forecasting |
| **Confidence Calibration** | 80%+ | When agent says 80% confident, error ≤20% |
| **System Performance** | <4 hours initial, <30 min updates | Runtime measurement |
| **Completeness** | 100% SKUs forecasted | No failures on 50-SKU test set |

## 2.3 Out of Scope for MVP

❌ Multi-archetype support (only Archetype 2)
❌ Real-time integration with retail systems
❌ Advanced ML models (deep learning, ensemble methods)
❌ Multi-season overlap handling
❌ Store-to-store transfer optimization
❌ Dynamic pricing optimization
❌ Promotional calendar integration

---

# 3. User Personas

## 3.1 Primary User: Demand Planner

**Profile:**
- **Role:** Demand Planning Manager at furniture retailer
- **Responsibilities:** Forecast demand, plan manufacturing orders, allocate inventory
- **Pain Points:** Inaccurate forecasts, manual Excel processes, late data availability
- **Goals:** Minimize stockouts/overstock, optimize markdown timing, reduce manual work

**Key Tasks:**
1. Input new SKU attributes (style, color, material, price)
2. Review forecasted `demand_by_store_by_week` matrix
3. Approve manufacturing order quantity
4. Monitor bi-weekly actuals vs forecast
5. Approve markdown recommendations

## 3.2 Secondary User: Merchandiser

**Profile:**
- **Role:** Merchandise Planning Manager
- **Responsibilities:** Product assortment, pricing, markdown strategy
- **Pain Points:** Data lag prevents timely markdown decisions (PP-016)
- **Goals:** Maximize sell-through, minimize end-of-season inventory

**Key Tasks:**
1. Review sell-through checkpoints (Week 12)
2. Approve markdown depth recommendations
3. Adjust pricing based on forecast updates

## 3.3 Secondary User: Operations Manager

**Profile:**
- **Role:** DC/Store Operations Manager
- **Responsibilities:** Inventory allocation, replenishment planning
- **Pain Points:** Store allocation mismatches (PP-015), manual replenishment planning
- **Goals:** Minimize transfer costs, optimize DC inventory levels

**Key Tasks:**
1. Review initial allocation recommendations
2. Approve bi-weekly replenishment plans
3. Monitor DC inventory levels

---

# 4. Functional Requirements

## 4.1 Agent 1: Demand Forecasting Agent

### Overview: What the Demand Agent Can Do

The Demand Agent can:

- **Accept product information** (SKU attributes like style, color, material, price)
- **Find similar historical products** to use as forecasting templates
- **Generate store-week demand predictions** (e.g., 50 stores × 26 weeks = 1,300 predictions per SKU)
- **Calculate confidence scores** to indicate forecast reliability
- **Update forecasts** automatically based on actual sales data (bi-weekly or when variance is high)
- **Adapt forecasting methods** based on available data (similar-item matching, time-series, or hybrid)

---

### Core Requirements

#### FR-1.1 SKU Attribute Input

- **Description**: Accept SKU attributes (category, style, color, material, dimensions, price)
- **What this means**: User inputs product details so the system knows what to forecast
- **Example**: "Mid-Century Sofa - Charcoal, Fabric, 84"W, $1,299"
- **Inputs**: Structured product data (CSV, JSON, or form input)
- **Outputs**: Validated SKU profile
- **Priority**: P0 (must have - can't forecast without knowing the product!)

#### FR-1.2 Adaptive Forecasting

- **Description**: Generate `demand_by_store_by_week` matrix using adaptive methods (similar-item matching, time-series)
- **Inputs**: SKU attributes, historical sales data (2-3 years), store attributes
- **Outputs**: 50 stores × 26 weeks matrix
- **Priority**: P0

#### FR-1.3 Similar-Item Matching

- **Description**: Find top 5-10 similar historical SKUs based on attribute similarity
- **Inputs**: SKU attributes
- **Outputs**: Ranked list of similar SKUs with similarity scores
- **Priority**: P0

#### FR-1.4 Confidence Scoring

- **Description**: Calculate forecast confidence (0-100%)
- **Inputs**: Similar-item match quality, historical data availability
- **Outputs**: Confidence score, method used
- **Priority**: P0

#### FR-1.5 Forecast Updates

- **Description**: Re-forecast based on actual sales (bi-weekly or variance-triggered)
- **Inputs**: Actual sales data, remaining weeks
- **Outputs**: Updated `demand_by_store_by_week` matrix
- **Priority**: P0

---

### 4.1.1 ML Methods for Demand Forecasting Agent

#### Similar-Item Matching (Embedding-Based Retrieval)

**Method**: Use OpenAI text-embedding-3-small to embed SKU attributes

**Process**:
1. Create text description: "Mid-Century Sofa, Charcoal, Fabric, 84"W, $1,299"
2. Generate embedding vector (1536 dimensions)
3. Calculate cosine similarity with historical SKU embeddings
4. Retrieve top 5-10 similar SKUs (similarity score >0.75)

**Cost**: ~$0.02/1M tokens (very cheap for 50 SKUs)

**Alternative**: TF-IDF + cosine similarity (free, but less semantic understanding)

---

#### Time-Series Forecasting Methods

| Method | When to Use | Library | Complexity |
|--------|------------|---------|-----------|
| **Prophet** | New SKUs with <6 months data | fbprophet | Simple |
| **ARIMA/SARIMA** | Existing SKUs with 1+ years data | statsmodels | Medium |
| **Exponential Smoothing (ETS)** | Stable demand patterns | statsmodels | Simple |
| **Weighted Average** | Very new SKUs (<3 months) | pandas/NumPy | Very Simple |

---

#### Adaptive Forecasting Logic (LLM-Assisted)

- **LLM Role**: gpt-4o-mini decides which forecasting method to use
- **Input to LLM**: SKU age, data availability, similar-item match quality
- **Output from LLM**: Recommended method (Prophet/ARIMA/Hybrid)
- **Cost per SKU**: ~$0.0001 (100 tokens × $0.15/1M)

---

#### Hybrid Approach (MVP Default)

```python
IF historical_data_weeks < 12:
    base_forecast = average(top_5_similar_items)
    adjustment = LLM reasoning on seasonality/trends
ELSE:
    base_forecast = ARIMA(historical_sales)
    similar_item_check = compare with similar items
    IF deviation > 20%:
        forecast = weighted_average(ARIMA, similar_items)
```

---

#### Store-Level Disaggregation

**Method**: Use store attributes (size, region, demographics) to split total demand

**Approach**:
1. Historical store penetration rates (Store A = 2.5% of total)
2. Adjust by similar-item store performance
3. Normalize to ensure sum(all stores) = total demand

**Library**: pandas, NumPy (no ML needed)

---

## 4.2 Agent 2: Inventory Allocation & Replenishment Agent

### Overview: What the Inventory Agent Can Do

The Inventory Agent can:

- **Calculate manufacturing orders** (how many units to produce 3 months before season start)
- **Allocate initial inventory** to stores (first 2 weeks of demand for each store)
- **Generate bi-weekly replenishment plans** (how much to ship from DC to each store every 2 weeks)
- **Optimize DC holdback** (keep 60-70% of inventory at DC to react to actual sales)
- **Balance inventory** across stores based on store-specific forecasts

---

### Core Requirements

#### FR-2.1 Manufacturing Order Calculation

- **Description**: Calculate total manufacturing quantity (3 months before season)
- **What this means**: Tells you how many units to order from supplier before season starts
- **Example**: Forecast shows 3,200 units needed + 15% safety stock = order 3,680 units
- **Inputs**: `demand_by_store_by_week`, safety stock %
- **Outputs**: Manufacturing order quantity
- **Priority**: P0 (must have - core manufacturing decision!)

#### FR-2.2 Initial Allocation

- **Description**: Allocate first 2 weeks of inventory to stores (week 0)
- **Inputs**: `demand_by_store_by_week`, holdback %
- **Outputs**: Store-level allocation quantities
- **Priority**: P0

#### FR-2.3 Bi-weekly Replenishment Planning

- **Description**: Calculate replenishment quantities every 2 weeks
- **Inputs**: Current store inventory, `demand_by_store_by_week`, DC inventory
- **Outputs**: Replenishment plan by store
- **Priority**: P0

#### FR-2.4 DC Holdback Optimization

- **Description**: Maintain 60-70% inventory at DC
- **Inputs**: Total manufactured, initial allocation
- **Outputs**: DC holdback quantity
- **Priority**: P0

---

### 4.2.1 ML/Optimization Methods for Inventory Agent

#### Manufacturing Order Calculation (Rule-Based)

**Method**: Simple formula-based calculation

**Formula**:
```
manufacturing_order = total_demand + (total_demand × safety_stock_pct)
```

**Safety Stock**: 15% for Archetype 2 (configurable in YAML)

**No ML needed**: Pure arithmetic based on forecast output

---

#### Initial Allocation (Proportional Allocation)

**Method**: Allocate based on store-specific forecast proportions

**Formula**:
```python
store_allocation = demand_by_store[weeks 0-1] × (1 + safety_buffer)
dc_holdback = total_manufactured - sum(store_allocations)
```

**Constraint**: Ensure DC holdback ≥ 60% (Archetype 2 parameter)

**Library**: pandas, NumPy (no ML needed)

---

#### Bi-weekly Replenishment (Inventory Optimization)

**Method**: Periodic review (s, S) policy

**Approach**:
1. Calculate target inventory: `next_2_weeks_demand + safety_stock`
2. Check current inventory: `on_hand + in_transit`
3. Replenishment: `max(0, target - current)`

**Optimization** (Optional P2): Linear programming for multi-store transfer optimization
- Library: PuLP or scipy.optimize (free)
- Minimize: Transfer costs between stores
- Constraints: DC capacity, store capacity

**MVP**: Simple rule-based, no optimization

---

#### LLM Role in Inventory Agent

- **Use case**: Explain allocation decisions, handle edge cases
- **Example**: "Why is Store A getting more than forecast?" → LLM explains based on historical performance
- **Cost**: Minimal (~$0.0001 per explanation)

---

## 4.3 Agent 3: Pricing Agent

### Overview: What the Pricing Agent Can Do

The Pricing Agent can:

- **Monitor sell-through performance** at key checkpoints (Week 12 for Archetype 2)
- **Detect underperformance** by comparing actual sales vs targets
- **Recommend markdown actions** when inventory is at risk of not selling through
- **Calculate markdown depth** (10%, 20%, or 30%) based on how far behind target you are
- **Trigger demand re-forecasts** after markdown to update remaining weeks with price-sensitive demand

---

### Core Requirements

#### FR-3.1 Sell-Through Monitoring

- **Description**: Calculate sell-through rate at Week 12
- **What this means**: Tracks what % of your inventory has sold by mid-season to catch problems early
- **Example**: By Week 12, you've sold 1,400 out of 3,680 units = 38% sell-through (target: 50%)
- **Inputs**: Actual sales (weeks 1-12), manufacturing order
- **Outputs**: Sell-through % vs target
- **Priority**: P0 (must have - prevents margin loss!)

#### FR-3.2 Markdown Trigger

- **Description**: Recommend markdown if sell-through <50% at Week 12
- **What this means**: Automatic alert to reduce prices before it's too late
- **Example**: 38% sold by Week 12 → trigger markdown recommendation
- **Inputs**: Sell-through rate, markdown threshold
- **Outputs**: Markdown recommendation (yes/no)
- **Priority**: P0

#### FR-3.3 Markdown Depth Calculation

- **Description**: Calculate recommended markdown depth (10%, 20%, 30%)
- **What this means**: Suggests how much to discount based on severity of underperformance
- **Example**: 12% gap from target → recommend 20% markdown
- **Inputs**: Sell-through gap, remaining weeks
- **Outputs**: Markdown depth %
- **Priority**: P1 (should have)

#### FR-3.4 Post-Markdown Re-forecast

- **Description**: Trigger Demand Agent to re-forecast weeks 13-26 with new price
- **What this means**: Updates forecast to reflect demand lift from discounted price
- **Example**: After 20% markdown, re-forecast shows 15% demand increase for weeks 13-26
- **Inputs**: Markdown depth, remaining weeks
- **Outputs**: Updated forecast request
- **Priority**: P1

---

### 4.3.1 ML/Analytics Methods for Pricing Agent

#### Sell-Through Monitoring (Rule-Based Analytics)

**Method**: Simple percentage calculation

**Formula**:
```
sell_through_pct = (cumulative_sales / manufacturing_order) × 100
```

**No ML needed**: Pure arithmetic

**Library**: pandas

---

#### Markdown Trigger (Threshold-Based)

**Method**: Rule-based decision

**Logic**:
```python
IF sell_through_pct < 50% AND current_week == 12:
    trigger_markdown = True
```

**Threshold**: 50% for Archetype 2 (configurable in YAML)

**No ML needed**: Simple if/else logic

---

#### Markdown Depth Calculation (Rule-Based with LLM Reasoning)

**Method**: Tiered approach based on gap severity

**Rules**:
```python
gap = target_sell_through - actual_sell_through
IF gap < 5%:  markdown_depth = 10%
ELIF gap < 15%: markdown_depth = 20%
ELSE: markdown_depth = 30%
```

**LLM Enhancement** (Optional): gpt-4o-mini provides reasoning
- Input: gap, remaining weeks, competitive landscape (if available)
- Output: Recommended depth + rationale
- Cost: ~$0.0002 per recommendation

**MVP**: Use rule-based, LLM for explanation only

---

#### Price Elasticity Estimation (Optional P2)

**Method**: Log-log regression if historical markdown data available

**Formula**:
```
log(quantity) = β₀ + β₁ × log(price) + ε
```

**Use**: Predict demand lift from markdown

**Library**: statsmodels (OLS regression)

**MVP**: Use industry benchmark (10% markdown → 5-10% demand lift)

**Data Requirement**: Historical markdown events (not always available)

---

#### Post-Markdown Demand Adjustment

**Method**: Apply elasticity multiplier to remaining weeks

**Formula**:
```python
elasticity_factor = 1 + (markdown_depth × demand_lift_rate)
updated_forecast[weeks 13-26] = original_forecast × elasticity_factor
```

**Default**: 20% markdown → 10% demand lift (configurable)

**Library**: pandas, NumPy

---

#### LLM Role in Pricing Agent

- **Use case**: Explain markdown recommendations, provide context
- **Example**: "Recommend 20% markdown because sell-through is 12% below target with 14 weeks remaining"
- **Cost**: ~$0.0002 per markdown event

---

## 4.4 Orchestrator

### Overview: What the Orchestrator Does

The Orchestrator:

- **Coordinates the 3 agents** (Demand, Inventory, Pricing) through the 5-phase seasonal workflow
- **Automatically triggers workflows** at the right times (3 months before season, bi-weekly, Week 12)
- **Detects forecast problems** (when actuals differ significantly from forecast >15%)
- **Triggers emergency re-forecasts** when variance is too high
- **Monitors system performance** (tracks accuracy, bias, confidence calibration)
- **Alerts you** when human intervention is needed (low confidence, high variance)

---

### Core Requirements

#### FR-4.1 Workflow Coordination

- **Description**: Execute 5-phase workflow (pre-season, season start, in-season, mid-season pricing, season end)
- **What this means**: Acts as the "project manager" that tells each agent when to run and passes data between them
- **Example**: Pre-season (Week -12): Run Demand Agent → pass forecast to Inventory Agent → calculate manufacturing order
- **Inputs**: Configuration, trigger events
- **Outputs**: Orchestrated agent execution
- **Priority**: P0 (must have - nothing works without coordination!)

#### FR-4.2 Variance-Triggered Re-forecast

- **Description**: Trigger emergency re-forecast if variance >15%
- **What this means**: Automatic safety check - if reality is very different from forecast, re-run the forecast immediately
- **Example**: Week 4 actual sales = 120 units, forecast was 80 units → 50% variance → trigger re-forecast
- **Inputs**: Actuals vs forecast comparison
- **Outputs**: Re-forecast trigger
- **Priority**: P1 (should have - prevents cascading errors)

#### FR-4.3 Performance Monitoring

- **Description**: Track MAPE, bias, confidence calibration
- **What this means**: Continuously measures how accurate the system is so you can trust it
- **Example**: MAPE = 18% (good!), Bias = -3% (slightly over-forecasting), Confidence calibration = 85% (reliable)
- **Inputs**: Forecasts, actuals
- **Outputs**: Performance metrics
- **Priority**: P1

#### FR-4.4 Human-in-the-Loop Alerts

- **Description**: Alert user when confidence <70% or variance >15%
- **What this means**: Sends you a notification when the system needs your help or attention
- **Example**: "Alert: SKU-12345 forecast confidence only 65% - please review similar-item matches"
- **Inputs**: Confidence scores, variance metrics
- **Outputs**: User notifications
- **Priority**: P2 (nice to have)

---

### 4.4.1 ML/Monitoring Methods for Orchestrator

#### Variance Detection (Statistical Monitoring)

**Method**: Calculate percentage deviation

**Formula**:
```
variance_pct = abs(actual - forecast) / forecast × 100
```

**Trigger**: If variance > 15% → trigger re-forecast

**Library**: pandas, NumPy (no ML needed)

---

#### Performance Monitoring (Forecast Accuracy Metrics)

**Metrics**:

1. **MAPE** (Mean Absolute Percentage Error):
   ```
   mean(abs((actual - forecast) / actual) × 100)
   ```

2. **Bias**:
   ```
   mean(forecast - actual) / mean(actual)
   ```
   (checks over/under-forecasting)

3. **Confidence Calibration**: Compare predicted confidence vs actual error

**Library**: pandas, NumPy, scikit-learn (metrics module)

**No ML training needed**: Pure calculation

---

#### Confidence Calibration Check

**Method**: Compare confidence scores vs actual accuracy

**Example**: If agent says "80% confident" → check if actual error ≤20%

**Metric**: Calibration curve (predicted probability vs observed frequency)

**Library**: scikit-learn (calibration_curve)

**Use**: Validate if confidence scores are reliable

---

#### Workflow Coordination (Rule-Based State Machine)

**Method**: Finite state machine with trigger conditions

**States**: Pre-season → Season Start → In-Season → Mid-Season Pricing → Season End

**Triggers**:
- Time-based: Week 0, Week 2, Week 4, ..., Week 12, Week 26
- Event-based: Variance > 15%, confidence < 70%

**No ML needed**: Pure orchestration logic

**Library**: Python state machine library (e.g., transitions) or custom implementation

---

#### LLM Role in Orchestrator

**Use case**: Agent coordination, decision explanation, anomaly diagnosis

**Examples**:
- "Based on 25% variance in Week 4, recommend emergency re-forecast"
- "Aggregate Demand Agent output → pass to Inventory Agent"
- "Explain why Week 8 forecast updated: variance exceeded threshold"

**Cost**: ~$0.001 per orchestration event (very minimal)

---

**No ML Training Required for Orchestrator**: All methods are rule-based, statistical calculations, or LLM reasoning. No model training needed.

---

## 4.5 Agentic Features

### What Makes This System "Agentic"?

This system uses **LLM-powered agents** rather than traditional scripted ML pipelines. The key agentic capabilities include:

---

### 4.5.1 Autonomous Decision-Making

Each agent makes decisions independently based on context:

| Agent | Autonomous Decisions |
|-------|---------------------|
| **Demand Agent** | Chooses forecasting method (Prophet, ARIMA, hybrid) based on data availability and SKU characteristics |
| **Inventory Agent** | Decides allocation quantities dynamically, adjusts DC holdback based on confidence |
| **Pricing Agent** | Decides markdown timing and depth based on sell-through trajectory |
| **Orchestrator** | Decides when to trigger emergency re-forecasts, which agents to invoke |

**Example**: Demand Agent evaluates a new SKU with 8 weeks of data and decides: "Use Prophet (handles short time series) weighted 70% + similar-item average weighted 30%"

---

### 4.5.2 Reasoning & Explanation (LLM-Powered)

All agents provide natural language explanations for their decisions:

```python
# Example agent output with reasoning
{
  "forecast": [...],
  "confidence": 0.82,
  "reasoning": "Used ARIMA for forecasting because 18 months of historical data
                available. Adjusted downward 5% based on similar-item analysis
                showing this color (charcoal) underperforms vs historical beige
                variants by 5-8%."
}
```

**User Value**: Demand planners can understand and trust agent recommendations, not just accept black-box outputs.

---

### 4.5.3 Adaptive Behavior

Agents adapt their approach based on context:

- **Demand Agent**: Switches from similar-item matching to time-series as more data becomes available
- **Pricing Agent**: Adjusts markdown depth based on remaining weeks (more aggressive with less time)
- **Orchestrator**: Increases re-forecast frequency if variance patterns are unstable

**Traditional ML**: Fixed pipeline (same method every time)
**Agentic**: Method selection based on LLM evaluation of context

---

### 4.5.4 Semantic Understanding (Embeddings)

**Demand Agent** uses OpenAI embeddings for semantic similar-item matching:

- **Traditional**: "Sofa" matches only exact keyword "Sofa"
- **Agentic**: "Mid-Century Modern Sofa, Charcoal, 84"W" semantically matches:
  - "Contemporary Sectional, Grey, 90"W" (similar style + color)
  - "Modern Loveseat, Slate, 72"W" (similar style + size category)
  - "Retro Couch, Dark Grey, 86"W" (similar style + color)

**Similarity Score Example**:
- Exact keyword match: 0.65
- Semantic embedding match: 0.88 (understands "charcoal" ≈ "grey", "sofa" ≈ "sectional")

---

### 4.5.5 Multi-Agent Collaboration

Agents coordinate through structured communication:

```
Pricing Agent (Week 12):
  "Sell-through is 38%, target is 50%. Recommend 20% markdown."
    ↓
Orchestrator:
  "Pricing Agent recommends markdown. Triggering Demand Agent to re-forecast."
    ↓
Demand Agent:
  "Applying 20% markdown → 10% demand lift. Updated forecast for weeks 13-26."
    ↓
Inventory Agent:
  "Received updated forecast. Recalculating replenishment plan."
```

**Agentic Feature**: Cascading decisions where one agent's output triggers another agent's action.

---

### 4.5.6 Memory & State Management

The **Orchestrator** maintains conversation history across the entire season:

- Remembers all forecasts, actuals, decisions
- Tracks which forecasting methods performed best
- Calibrates confidence scores over time
- Learns whether to trust Demand Agent confidence or trigger human review

**Example**: "Week 8 variance is high (22%), but Demand Agent was confident (85%). Historical calibration shows this agent over-confident by 10%. Alert user before re-forecasting."

---

### 4.5.7 Human-in-the-Loop Collaboration

Agents know when to escalate to humans:

```python
# Orchestrator logic
if confidence_score < 0.70:
    explanation = demand_agent.explain_low_confidence(sku)
    alert_user(
        message=f"⚠️ Low confidence ({confidence_score:.0%}) for {sku}",
        explanation=explanation,
        action="Please review similar-item matches or provide additional context"
    )
```

**Agentic Feature**: Agents recognize their limitations and request human input.

---

### 4.5.8 Tool Use

Agents use multiple tools dynamically:

| Agent | Tools Used |
|-------|-----------|
| **Demand Agent** | OpenAI Embeddings API, Prophet, ARIMA, Pandas, NumPy |
| **Inventory Agent** | scipy.optimize, PuLP (linear programming), Pandas |
| **Pricing Agent** | statsmodels (elasticity regression), Pandas |
| **Orchestrator** | All other agents (agents as tools) |

**Example**: Demand Agent evaluates SKU, decides "data quality is good, use ARIMA" → invokes statsmodels ARIMA tool.

---

### 4.5.9 Goal-Oriented Behavior

Each agent optimizes for specific goals:

| Agent | Primary Goal | Secondary Goal |
|-------|-------------|---------------|
| **Demand Agent** | Minimize MAPE | Maintain confidence >80% |
| **Inventory Agent** | Minimize stockouts + overstock | Maintain 60-70% DC holdback |
| **Pricing Agent** | Maximize sell-through by Week 26 | Minimize markdown depth |
| **Orchestrator** | Coordinate agents to achieve system MAPE <20% | Minimize API costs |

**Agentic Feature**: Agents balance competing objectives and explain trade-offs.

---

### Why This Matters for MVP

Traditional ML systems require months of model development. **Agentic systems leverage LLM reasoning** to:

- Reduce development time (LLM handles edge cases)
- Improve explainability (natural language reasoning)
- Enable rapid iteration (change prompts vs retrain models)
- Lower cost (<$5 for entire season vs $1000s for cloud ML infrastructure)

**Reference**: See [Agent Coordination Workflow](agent_coordination_workflow.md) for detailed multi-agent orchestration.

---

## 4.6 Data Management

#### FR-6.1 Historical Sales Data Ingestion

- **Description**: Load 2-3 years of daily sales data by SKU and store
- **Inputs**: CSV/database exports
- **Outputs**: Validated historical dataset
- **Priority**: P0

#### FR-6.2 Product Catalog Management

- **Description**: Manage product attributes (historical + new SKUs)
- **Inputs**: Product catalog CSV
- **Outputs**: Searchable product database
- **Priority**: P0

#### FR-6.3 Store Attributes Management

- **Description**: Store location, size, demographics data
- **Inputs**: Store master CSV
- **Outputs**: Store attribute database
- **Priority**: P0

#### FR-6.4 Forecast Output Export

- **Description**: Export forecasts as CSV/JSON
- **Inputs**: `demand_by_store_by_week` matrix
- **Outputs**: Structured forecast file
- **Priority**: P0

---

# 5. Non-Functional Requirements

> **MVP Constraint: Zero/Minimal Cost**
> This is an academic MVP project. All components must use free tiers, open-source tools, or local resources.

---

## 5.1 Performance

| Requirement | Target | Priority |
|-------------|--------|----------|
| **Initial Forecast Runtime** | <4 hours for 50 SKUs (local machine) | P0 |
| **Bi-weekly Update Runtime** | <30 minutes (local machine) | P0 |
| **System Uptime** | N/A (runs on-demand, not 24/7 service) | - |
| **Concurrent Users** | 1 (single-user local execution) | P0 |

---

## 5.2 Scalability

| Requirement | MVP | Future |
|-------------|-----|--------|
| **SKUs** | 50 | 500+ |
| **Stores** | 50 | 200+ |
| **Seasons** | 1 at a time | Multiple overlapping |
| **Forecast Horizon** | 26 weeks | Up to 52 weeks |
| **Infrastructure** | Local machine (8GB RAM min) | Cloud deployment |

---

## 5.3 Cost Constraints (MVP)

| Component | Solution | Cost |
|-----------|----------|------|
| **Compute** | Local development machine | $0 |
| **Storage** | Local filesystem (CSV/Parquet) | $0 |
| **Database** | SQLite (local) | $0 |
| **LLM API** | OpenAI SDK (gpt-4o-mini for cost efficiency) | <$5 |
| **Forecasting Libraries** | Open-source (statsmodels, Prophet, scikit-learn) | $0 |
| **Agent Framework** | Open-source (LangChain with OpenAI) | $0 |
| **Version Control** | GitHub (free) | $0 |

**Total MVP Budget Target**: <$5

---

### Cost Optimization Strategies

- Use **gpt-4o-mini** ($0.15/1M input tokens, $0.60/1M output tokens) for agent reasoning
- Minimize LLM calls: Use only for similar-item matching logic and agent coordination
- Cache similar-item embeddings to avoid repeated API calls
- Use traditional ML (statsmodels, Prophet) for actual forecasting computations
- Limit token usage: structured prompts, avoid verbose outputs

---

## 5.4 Data Quality

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Historical Data Completeness** | ≥80% of store-days have sales data | P0 |
| **Attribute Completeness** | 100% of SKUs have required attributes | P0 |
| **Data Freshness** | Actual sales available within 24 hours (simulated for MVP) | P2 |

---

## 5.5 Usability

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Configuration** | YAML-based parameter configuration | P0 |
| **Interface** | Command-line interface (CLI) | P0 |
| **Transparency** | Show similar-items used, forecasting method | P0 |
| **Error Handling** | Clear error messages for data issues | P1 |
| **Deployment** | Single-machine setup (no cloud required) | P0 |

---

## 5.6 Maintainability

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Architecture** | Parameter-driven, extensible to other archetypes | P0 |
| **Documentation** | Code documentation, README, user guide | P1 |
| **Testing** | Unit tests for core functions (pytest) | P1 |
| **Dependencies** | Python 3.9+, open-source libraries only | P0 |

---

# 6. User Stories

## 6.1 Epic 1: Demand Forecasting

### US-1.1 Generate Initial Forecast

**As a** demand planner
**I want to** input new SKU attributes and get store-week demand forecast
**So that** I can plan manufacturing orders 3 months in advance

**Acceptance Criteria**:
- Input SKU attributes via CSV
- System outputs `demand_by_store_by_week` matrix for 26 weeks
- Forecast completes in <4 hours
- Confidence score provided

---

### US-1.2 Review Similar Items

**As a** demand planner
**I want to** see which historical SKUs were used for forecasting
**So that** I can validate forecast logic

**Acceptance Criteria**:
- System shows top 5 similar SKUs with similarity scores
- Can click to see historical sales patterns of similar items
- Understand attribute matching (style, color, material weights)

---

### US-1.3 Update Forecast Based on Actuals

**As a** demand planner
**I want** the system to automatically update forecasts bi-weekly based on actual sales
**So that** replenishment plans stay accurate

**Acceptance Criteria**:
- System ingests actuals every 2 weeks
- Re-forecast completes in <30 minutes
- Shows variance vs original forecast

---

## 6.2 Epic 2: Inventory Decisions

### US-2.1 Calculate Manufacturing Order

**As a** demand planner
**I want to** get recommended manufacturing quantity
**So that** I can place orders with suppliers 3 months before season

**Acceptance Criteria**:
- System calculates total demand + safety stock
- Shows breakdown: total demand, safety stock %, final order
- Allows manual override with justification

---

### US-2.2 Plan Initial Allocation

**As an** operations manager
**I want to** get store-level allocation recommendations for week 0
**So that** I can ship right quantities to each store

**Acceptance Criteria**:
- System allocates first 2 weeks demand to each store
- Shows DC holdback % (target: 65%)
- Exportable as CSV for WMS integration

---

### US-2.3 Generate Bi-weekly Replenishment Plan

**As an** operations manager
**I want** automatic bi-weekly replenishment recommendations
**So that** stores don't run out of stock

**Acceptance Criteria**:
- System checks current inventory vs next 2-week forecast
- Calculates replenishment quantities by store
- Updates every 2 weeks automatically

---

## 6.3 Epic 3: Pricing Decisions

### US-3.1 Monitor Sell-Through

**As a** merchandiser
**I want to** see sell-through % at Week 12
**So that** I can decide if markdown is needed

**Acceptance Criteria**:
- Dashboard shows sell-through % vs 50% target
- Shows total sold, total manufactured, gap
- Color-coded: green (on track), yellow (close), red (action needed)

---

### US-3.2 Get Markdown Recommendation

**As a** merchandiser
**I want** automatic markdown recommendation at Week 12 if sell-through is low
**So that** I can clear inventory before season end

**Acceptance Criteria**:
- System recommends markdown if <50% sold by Week 12
- Suggests markdown depth (10%, 20%, 30%)
- Shows expected demand lift from markdown

---

## 6.4 Epic 4: System Configuration

### US-4.1 Configure Archetype Parameters

**As a** system administrator
**I want to** configure system for Archetype 2 (Stable Catalog)
**So that** forecasting behavior matches furniture retail patterns

**Acceptance Criteria**:
- YAML config file with all parameters
- Parameters: season_length=26, replenishment_cadence=bi-weekly, markdown_trigger_week=12, holdback=65%
- System validates config on startup

---

# 7. Data Requirements

## 7.1 Input Data

| Dataset | Fields | Granularity | Time Range | Priority |
|---------|--------|-------------|------------|----------|
| **Historical Sales** | date, sku, store_id, quantity_sold, revenue | Daily | 2-3 years | P0 |
| **Product Catalog** | sku, category, style, color, material, dimensions, price, launch_date | SKU-level | Current + historical | P0 |
| **Store Attributes** | store_id, location, region, size_sqft, demographics | Store-level | Current | P0 |
| **External Factors** (Optional) | housing_market_data, macro_trends, seasonality_indicators | Weekly/Monthly | 1-2 years | P2 |

---

## 7.2 Output Data

| Output | Format | Contents | Priority |
|--------|--------|----------|----------|
| **Demand Forecast** | JSON/CSV | `demand_by_store_by_week` matrix, confidence, method used | P0 |
| **Inventory Recommendations** | JSON/CSV | Manufacturing order, initial allocation, replenishment plans | P0 |
| **Pricing Recommendations** | JSON/CSV | Markdown trigger, depth, timing | P1 |
| **Performance Metrics** | JSON | MAPE, bias, confidence calibration by week | P1 |

---

# 8. Technical Architecture

## 8.1 System Components

```
┌─────────────────────────────────────────────────────┐
│                  ORCHESTRATOR                       │
│  • Workflow coordination                           │
│  • Trigger management                              │
│  • Performance monitoring                          │
└─────────────┬───────────────────────────────────────┘
              │
    ┌─────────┴─────────┬───────────────┬─────────────┐
    │                   │               │             │
    ▼                   ▼               ▼             ▼
┌─────────┐      ┌──────────┐   ┌──────────┐   ┌──────────┐
│ DEMAND  │      │INVENTORY │   │  PRICING │   │  CONFIG  │
│  AGENT  │      │  AGENT   │   │  AGENT   │   │ MANAGER  │
└─────────┘      └──────────┘   └──────────┘   └──────────┘
    │                   │               │
    └───────────────────┴───────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │     DATA LAYER        │
            │ • Historical sales    │
            │ • Product catalog     │
            │ • Store attributes    │
            └───────────────────────┘
```

---

## 8.2 Technology Stack

| Component | Technology | Rationale | Cost |
|-----------|-----------|-----------|------|
| **Language** | Python 3.9+ | ML/data science ecosystem | Free |
| **LLM API** | OpenAI SDK (gpt-4o-mini) | Cost-efficient agent reasoning | <$5 |
| **Agents** | LangChain with OpenAI | Agent orchestration framework | Free (library) |
| **Forecasting** | statsmodels, Prophet, scikit-learn | Time-series forecasting | Free |
| **Data Processing** | pandas, NumPy | Data manipulation | Free |
| **Storage** | SQLite + CSV/Parquet | Local storage, no database server needed | Free |
| **Configuration** | YAML | Parameter management | Free |
| **Testing** | pytest | Unit/integration tests | Free |

---

### Why OpenAI SDK with gpt-4o-mini?

- **Cost-efficient**: $0.15/1M input tokens vs gpt-4 at $10/1M
- **Sufficient for MVP**: Similar-item reasoning, agent coordination
- **Easy integration**: LangChain native support
- **Minimal usage**: LLM only for logic, not computation

---

# 9. Milestones & Timeline

## 9.1 MVP Timeline: 12 Weeks

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| **1-2** | Environment setup, data pipeline | • Python environment<br>• Mock historical data (2 years)<br>• Product catalog (50 SKUs)<br>• Store attributes (50 stores) |
| **3-4** | Demand Agent - Similar-item matching | • Attribute similarity algorithm<br>• Top-5 similar SKU retrieval<br>• Validate on 5 test SKUs |
| **5-6** | Demand Agent - Forecast generation | • `demand_by_store_by_week` matrix output<br>• Confidence scoring<br>• Time-series for historical SKUs |
| **7-8** | Inventory Agent | • Manufacturing order calculation<br>• Initial allocation (first 2 weeks)<br>• Bi-weekly replenishment logic |
| **9** | Pricing Agent | • Sell-through monitoring<br>• Markdown trigger (Week 12, <50%)<br>• Markdown depth calculation |
| **10** | Orchestrator | • 5-phase workflow execution<br>• Variance-triggered re-forecasts<br>• Performance monitoring |
| **11** | Validation | • Hindcast Fall/Winter 2024<br>• MAPE measurement<br>• Confidence calibration check |
| **12** | Documentation & Final Report | • User guide<br>• Technical documentation<br>• Performance analysis report |

---

## 9.2 Success Criteria by Milestone

| Milestone | Success Criteria |
|-----------|-----------------|
| **Week 2** | Mock data pipeline loads 2 years of sales data |
| **Week 4** | Similar-item algorithm finds relevant matches (similarity >0.80) |
| **Week 6** | Demand Agent generates 26-week forecast for 10 SKUs |
| **Week 8** | Inventory Agent calculates manufacturing order + replenishment plan |
| **Week 9** | Pricing Agent triggers markdown recommendation correctly |
| **Week 10** | Orchestrator runs full 5-phase workflow end-to-end |
| **Week 11** | MAPE <20% on hindcast validation |
| **Week 12** | Complete documentation, working demo |

---

# 10. Risks & Mitigation

## 10.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Poor similar-item match quality** | Medium | High | • Implement attribute weighting<br>• Allow manual override<br>• Validate on known good matches |
| **Insufficient historical data** | Medium | Medium | • Require minimum 2 years<br>• Fall back to category averages<br>• Flag low-confidence forecasts |
| **High forecast variance** | High | Medium | • Bi-weekly updates<br>• Variance-triggered re-forecasts<br>• Safety stock buffers |
| **Runtime performance issues** | Low | Medium | • Optimize similar-item search<br>• Cache historical data<br>• Parallel processing where possible |

---

## 10.2 Business Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **User adoption resistance** | Medium | High | • Run parallel with existing process<br>• Show accuracy improvement<br>• Involve users early in design |
| **Data quality issues** | High | High | • Implement validation checks<br>• Flag missing/anomalous data<br>• Require minimum data quality thresholds |
| **Mock data not realistic** | Medium | Medium | • Base on real furniture retail patterns<br>• Validate with industry expert<br>• Use publicly available benchmarks |

---

# 11. Assumptions & Dependencies

## 11.1 Assumptions

1. Historical sales data is available for 2-3 years
2. Product attributes are structured and complete
3. Store attributes are consistent and accurate
4. Bi-weekly replenishment cadence is acceptable for furniture retail
5. Users can provide new SKU attributes 3 months before season start
6. 26-week forecast horizon covers full season for Archetype 2

---

## 11.2 Dependencies

| Dependency | Description | Owner |
|------------|-------------|-------|
| **Mock Data Generation** | Realistic synthetic data for furniture retail | Development Team |
| **Historical Data Access** | 2-3 years of sales data (or synthetic equivalent) | Development Team |
| **Domain Expertise** | Validation of furniture retail assumptions | Academic Advisor / Industry Contact |
| **Compute Resources** | 8 vCPU, 32GB RAM for development | Infrastructure |

---

# 12. Appendix

## 12.1 Glossary

| Term | Definition |
|------|------------|
| **MAPE** | Mean Absolute Percentage Error - forecast accuracy metric |
| **Archetype** | Retail business model classification (Fashion, Stable Catalog, CPG) |
| **Holdback** | % of inventory kept at DC instead of allocated to stores |
| **Sell-Through** | % of manufactured inventory sold by a given week |
| **Similar-Item Matching** | Algorithm to find historical SKUs with similar attributes |
| **Variance Threshold** | % deviation from forecast that triggers re-forecast |

---

## 12.2 References

- [Product Brief v2.1](../product_brief/2_demand_forecasting_product_brief.md)
- [Operational Workflow](../../05_Progress_Reports/Weekly_Supervisor_Meetings/operational_workflow.md)
- [Key Parameters](../../05_Progress_Reports/Weekly_Supervisor_Meetings/key_parameter.md)
- [Evidence Pack - Pain Point Inventory](../../03_Evidence_Pack/_extraction/Pain_Point_Inventory.md)

---

## 12.3 Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-10 | Initial PRD draft for MVP | Independent Study Project |

---

**Document Owner**: Independent Study Project
**Last Updated**: 2025-10-10
**Status**: Draft - Awaiting Review
