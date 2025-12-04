# Process Workflow v4.0: Deterministic Orchestration with Agentic Reasoning

**Version:** 4.0
**Date:** 2025-12-04
**Status:** Active Implementation (SDK Branch)
**Scope:** Retail Demand Forecasting with Self-Correcting Variance Analysis

> **Note**: This document describes the operational workflow for the 6-agent system using deterministic Python orchestration with agentic reasoning. For technical architecture details, see [Architecture v4.0](architecture-v4.0.md).

---

## Table of Contents

1. [Key Concept: Deterministic Orchestration with Agentic Reasoning](#key-concept-deterministic-orchestration-with-agentic-reasoning)
2. [The 6 Agents](#the-6-agents)
3. [5-Phase Operational Workflow](#5-phase-operational-workflow)
4. [Variance Analysis & Reforecasting Loop](#variance-analysis--reforecasting-loop)
5. [Data Flow Patterns](#data-flow-patterns)
6. [Example Scenarios](#example-scenarios)
7. [Quick Reference](#quick-reference)

---

## Key Concept: Deterministic Orchestration with Agentic Reasoning

### What's Different in v4.0: Three-Layer Architecture

**v3.3 Approach (Agent-as-Tool)**:
- Agents called other agents directly via handoffs
- String pattern matching controlled flow
- Fragile, hard to debug, no type safety

**v4.0 Approach (Deterministic + Agentic)**:
- Python workflows control WHEN agents run (deterministic)
- Agents control HOW they reason and produce results (agentic)
- Tools handle pure computation (no LLM calls)
- Typed Pydantic schemas enforce data contracts

```
┌─────────────────────────────────────────────────────────────┐
│              WORKFLOW LAYER (Python - Deterministic)         │
│                                                              │
│   if variance_result.should_reforecast:                      │
│       reforecast = await Runner.run(reforecast_agent, ...)   │
│                                                              │
│   Python decides WHEN to run agents based on typed output    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                AGENT LAYER (LLM - Agentic)                   │
│                                                              │
│   variance_agent reasons: "25% variance in Week 2 with 10    │
│   weeks remaining and upward trend suggests systematic       │
│   underforecast. Recommend reforecast."                      │
│                                                              │
│   Agent decides HOW to analyze and what to recommend         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               TOOLS LAYER (Pure Computation)                 │
│                                                              │
│   bayesian_reforecast(prior=forecast, likelihood=actuals)    │
│   → posterior = updated_forecast                             │
│                                                              │
│   Math functions with NO LLM calls                           │
└─────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

| Concern | v3.3 (Agent-as-Tool) | v4.0 (Deterministic + Agentic) |
|---------|---------------------|-------------------------------|
| Control Flow | String pattern matching | Python `if/while` statements |
| Type Safety | None (strings) | Pydantic schemas enforced by SDK |
| Debugging | Hard (LLM black box) | Clear (Python + structured output) |
| Guardrails | String parsing | Validation on typed data |
| Variance Decision | `if variance > 0.20` | Agent reasons holistically |

---

## The 6 Agents

### Agent Overview

| Agent | Role | Key Decision | Output Schema |
|-------|------|--------------|---------------|
| **Demand Agent** | Forecast total demand | Safety stock %, model selection | `ForecastResult` |
| **Inventory Agent** | Allocate to stores | DC holdback %, cluster weights | `AllocationResult` |
| **Pricing Agent** | Calculate markdowns | Markdown %, timing | `MarkdownResult` |
| **Variance Agent** | Analyze forecast accuracy | Should we reforecast? | `VarianceAnalysis` |
| **Reforecast Agent** | Update forecast with actuals | Posterior estimates | `ReforecastResult` |
| **Reallocation Agent** | Strategic replenishment | Transfer strategy | `ReallocationAnalysis` |

### Agent 1: Demand Agent

**Purpose**: Generate demand forecast using Prophet + ARIMA ensemble with seasonality insights.

**Input**:
```json
{
  "category": "Women's Dresses",
  "forecast_horizon_weeks": 12,
  "season_start_date": "2025-03-01"
}
```

**Tool Called**: `run_demand_forecast`
- Loads 3 years of historical sales data
- Trains Prophet (seasonality) + ARIMA (trend)
- Ensemble weighting based on validation MAPE
- Extracts peak/trough weeks, monthly effects

**Output** (`ForecastResult`):
```json
{
  "total_demand": 8000,
  "forecast_by_week": [600, 650, 700, 750, 800, 850, 700, 650, 600, 550, 500, 450],
  "safety_stock_pct": 0.20,
  "confidence": 0.85,
  "model_used": "ensemble_prophet_arima",
  "seasonality": {
    "peak_weeks": [5, 6],
    "trough_weeks": [11, 12],
    "seasonal_range": 0.35,
    "monthly_effects": {"March": 1.1, "April": 1.2, "May": 0.9},
    "insight": "Peak demand expected weeks 5-6 (back-to-school preparation)"
  },
  "explanation": "Forecast based on 3-year historical patterns with strong spring seasonality...",
  "lower_bound": [500, 550, 600, ...],
  "upper_bound": [700, 750, 800, ...]
}
```

**Agent Reasoning Example**:
> *"Historical data shows 35% seasonal variation with peaks in late April. Season starts March 1st, aligning with back-to-school prep. Prophet captures seasonality well (MAPE 12%), ARIMA captures recent trend (MAPE 15%). Ensemble weight: 60% Prophet, 40% ARIMA. Recommend 20% safety stock given moderate forecast uncertainty."*

---

### Agent 2: Inventory Agent

**Purpose**: Cluster stores and allocate inventory using hierarchical method.

**Input**:
```json
{
  "total_forecast": 8000,
  "forecast_by_week": [600, 650, ...],
  "dc_holdback_pct": 0.45,
  "safety_stock_pct": 0.20
}
```

**Tools Called**:
1. `cluster_stores` - K-means on 7 attributes
2. `allocate_inventory` - 3-layer hierarchical allocation

**Output** (`AllocationResult`):
```json
{
  "manufacturing_qty": 9600,
  "dc_holdback": 4320,
  "dc_holdback_percentage": 0.45,
  "initial_store_allocation": 5280,
  "cluster_allocations": [
    {"cluster_name": "Fashion_Forward", "store_count": 15, "total_units": 2112, "percentage": 0.40},
    {"cluster_name": "Mainstream", "store_count": 20, "total_units": 1848, "percentage": 0.35},
    {"cluster_name": "Value_Conscious", "store_count": 15, "total_units": 1320, "percentage": 0.25}
  ],
  "store_allocations": [
    {"store_id": "NYC-001", "cluster": "Fashion_Forward", "units": 488, "percentage": 0.092},
    {"store_id": "LA-002", "cluster": "Fashion_Forward", "units": 445, "percentage": 0.084},
    ...
  ],
  "replenishment_strategy": "weekly_from_dc",
  "explanation": "Allocated based on K-means clustering with 7 features...",
  "reasoning_steps": [
    "Calculated manufacturing qty: 8000 × 1.20 = 9,600 units",
    "Applied 45% DC holdback: 4,320 units reserved for replenishment",
    "K-means identified 3 clusters with silhouette score 0.52",
    "Fashion_Forward stores show 2.3x average velocity - prioritized"
  ],
  "key_factors": [
    "NYC-001 received 488 units (9.2%) due to 2.3x average sales velocity",
    "Value_Conscious cluster received 25% vs historical 28% due to declining trend"
  ]
}
```

**Agent Reasoning Example**:
> *"K-means clustering on 7 features yields 3 distinct segments. Fashion_Forward stores (15 stores) show 2.3x average velocity and should receive 40% of initial allocation despite being 30% of store count. NYC-001 specifically has highest historical performance - allocating 488 units (9.2% of initial). DC holdback at 45% provides buffer for weekly replenishment and variance correction."*

---

### Agent 3: Pricing Agent

**Purpose**: Calculate markdown when sell-through is below target.

**Input**:
```json
{
  "current_sell_through": 0.52,
  "target_sell_through": 0.60,
  "week_number": 6,
  "elasticity": 2.0
}
```

**Tool Called**: `calculate_markdown`
- Gap = target - current
- Raw markdown = gap × elasticity
- Round to nearest 5%, cap at 40%

**Output** (`MarkdownResult`):
```json
{
  "recommended_markdown_pct": 0.15,
  "current_sell_through": 0.52,
  "target_sell_through": 0.60,
  "gap": 0.08,
  "elasticity_used": 2.0,
  "raw_markdown_pct": 0.16,
  "week_number": 6,
  "explanation": "At Week 6, sell-through is 52% vs 60% target. Gap of 8pp × elasticity 2.0 = 16% raw markdown, rounded to 15%. This should accelerate sell-through by approximately 12-15% based on historical price sensitivity."
}
```

**Agent Reasoning Example**:
> *"Week 6 checkpoint shows 52% sell-through, 8 percentage points below target. With 6 weeks remaining and 48% inventory still on hand, markdown intervention is warranted. Gap × Elasticity formula: 8% × 2.0 = 16% → rounds to 15%. Historical data suggests 15% markdown drives 12-15% sell-through improvement. Recommend uniform 15% markdown across all stores."*

---

### Agent 4: Variance Agent (NEW in v4.0)

**Purpose**: Reason holistically about forecast variance and decide if reforecasting is needed.

**Key Innovation**: Agent decides `should_reforecast` based on reasoning, not simple threshold.

**Input**:
```json
{
  "current_week": 3,
  "forecast_by_week": [600, 650, 700, ...],
  "actual_sales": [720, 780, 840],
  "original_forecast_total": 8000,
  "weeks_remaining": 9
}
```

**Tool Called**: `analyze_variance_data`
- Calculates MAPE, directional variance
- Identifies trend (increasing, decreasing, stable)
- Computes cumulative vs weekly variance

**Output** (`VarianceAnalysis`):
```json
{
  "variance_pct": 0.22,
  "is_high_variance": true,
  "severity": "moderate",
  "likely_cause": "systematic_underforecast",
  "trend_direction": "increasing",
  "recommended_action": "reforecast_with_bayesian_update",
  "should_reforecast": true,
  "reforecast_adjustments": "Increase weeks 4-12 by approximately 18-22% based on observed trend",
  "confidence": 0.78,
  "explanation": "Weeks 1-3 show consistent positive variance averaging 22%. Trend is increasing (W1: 20%, W2: 20%, W3: 25%), suggesting systematic underforecast rather than random noise. With 9 weeks remaining, reforecasting now can correct remaining allocation and prevent stockouts."
}
```

**Agent Reasoning Example**:
> *"Three-week variance of 22% exceeds typical threshold, but more importantly, the trend is increasing (20% → 20% → 25%). This pattern suggests systematic underforecast rather than random volatility. Given 9 weeks remaining, we have time to correct. If this were Week 10 with only 2 weeks left, I might recommend no reforecast since correction would have minimal impact. Recommending Bayesian reforecast to update remaining weeks."*

**Key Difference from v3.3**:
- v3.3: `if variance > 0.20: reforecast()` (simple threshold)
- v4.0: Agent considers magnitude, trend, remaining season, likely cause, and impact

---

### Agent 5: Reforecast Agent (NEW in v4.0)

**Purpose**: Update forecast using Bayesian inference with actual sales data.

**Input**:
```json
{
  "original_forecast_by_week": [600, 650, 700, 750, 800, 850, 700, 650, 600, 550, 500, 450],
  "actual_sales": [720, 780, 840],
  "weeks_observed": 3,
  "variance_analysis": { "trend_direction": "increasing", "variance_pct": 0.22 }
}
```

**Tool Called**: `bayesian_reforecast`
- Prior: Original forecast (mean, variance)
- Likelihood: Observed actual sales
- Posterior: Updated forecast via conjugate Gaussian update

**Output** (`ReforecastResult`):
```json
{
  "updated_forecast_by_week": [720, 780, 840, 900, 960, 1020, 840, 780, 720, 660, 600, 540],
  "updated_total": 9360,
  "adjustment_factor": 1.17,
  "posterior_confidence": 0.82,
  "prior_weight": 0.35,
  "likelihood_weight": 0.65,
  "explanation": "Bayesian update applied with 65% weight on observed data (3 weeks of actuals showing consistent +22% trend). Updated forecast increases remaining weeks by 17% on average. Posterior confidence 82% reflects strong signal from actuals."
}
```

**Agent Reasoning Example**:
> *"Applying Bayesian update with conjugate Gaussian prior. Prior: original forecast with variance based on historical MAPE. Likelihood: 3 weeks of actuals with observed variance. Given strong consistent signal (22% positive variance, increasing trend), posterior weights likelihood at 65%. Updated forecast: +17% adjustment for weeks 4-12. This balances historical patterns with observed demand surge."*

---

### Agent 6: Reallocation Agent (NEW in v4.0)

**Purpose**: Analyze store performance and recommend strategic replenishment.

**Input**:
```json
{
  "store_allocations": [...],
  "store_actual_sales": {
    "NYC-001": [120, 135, 145],
    "LA-002": [95, 88, 82],
    ...
  },
  "dc_units_available": 3200,
  "current_week": 3
}
```

**Tools Called**:
1. `analyze_store_performance` - Velocity, sell-through by store
2. `generate_transfer_recommendations` - DC releases + store-to-store

**Output** (`ReallocationAnalysis`):
```json
{
  "should_reallocate": true,
  "strategy": "hybrid",
  "dc_units_available": 3200,
  "dc_units_to_release": 800,
  "high_performers": ["NYC-001", "CHI-005", "SF-008"],
  "underperformers": ["RURAL-025", "RURAL-031"],
  "on_target_stores": ["LA-002", "MIA-012", ...],
  "transfers": [
    {"from": "DC", "to": "NYC-001", "units": 200, "reason": "High velocity, stockout risk in 2 weeks"},
    {"from": "DC", "to": "CHI-005", "units": 180, "reason": "Sell-through 15% above target"},
    {"from": "RURAL-025", "to": "NYC-001", "units": 50, "reason": "Transfer from underperformer"}
  ],
  "expected_sell_through_improvement": 0.08,
  "stockout_risk_reduction": 3,
  "confidence": 0.75,
  "explanation": "Analysis shows 3 high-performing stores at stockout risk within 2 weeks. Recommend hybrid strategy: 800 units from DC to top performers, plus 50-unit transfer from underperforming rural store. Expected to improve overall sell-through by 8% and prevent stockouts at 3 locations."
}
```

---

## 5-Phase Operational Workflow

### Phase Overview

| Phase | Timing | Key Actions | Primary Agents |
|-------|--------|-------------|----------------|
| **0. Pre-Season Planning** | Week -24 to 0 | Forecast, manufacture, allocate | Demand, Inventory |
| **1. Season Launch** | Week 0 | Initial store shipment | Inventory |
| **2. In-Season Monitoring** | Weeks 1-5 | Variance analysis, reforecast, reallocation | Variance, Reforecast, Reallocation |
| **3. Mid-Season Pricing** | Week 6 | Markdown checkpoint | Pricing |
| **4. Late Season & Close** | Weeks 7-12 | Continue monitoring, final analysis | Variance, Reallocation |

---

### PHASE 0: Pre-Season Planning

**Goal**: Generate forecast, commit to manufacturing, prepare allocation plan.

**Workflow Execution**:

```python
# season_workflow.py - Phase 0
async def run_preseason_planning(context: ForecastingContext):
    # Step 1: Generate demand forecast
    forecast_result = await Runner.run(
        demand_agent,
        input=json.dumps({
            "category": context.category,
            "forecast_horizon_weeks": 12,
            "season_start_date": str(context.season_start_date)
        }),
        context=context
    )

    # Step 2: Generate allocation plan
    allocation_result = await Runner.run(
        inventory_agent,
        input=json.dumps({
            "total_forecast": forecast_result.final_output.total_demand,
            "forecast_by_week": forecast_result.final_output.forecast_by_week,
            "dc_holdback_pct": context.dc_holdback_pct,
            "safety_stock_pct": forecast_result.final_output.safety_stock_pct
        }),
        context=context
    )

    # Step 3: Store results in context
    context.forecast_by_week = forecast_result.final_output.forecast_by_week
    context.original_forecast = forecast_result.final_output
    context.allocation_result = allocation_result.final_output
    context.manufacturing_qty = allocation_result.final_output.manufacturing_qty
    context.dc_holdback = allocation_result.final_output.dc_holdback

    return PreseasonResult(
        forecast=forecast_result.final_output,
        allocation=allocation_result.final_output
    )
```

**Output**:
- Manufacturing order committed: 9,600 units
- DC holdback reserved: 4,320 units (45%)
- Store allocations planned: 5,280 units initial
- Seasonality insights captured for UI display

---

### PHASE 1: Season Launch (Week 0)

**Goal**: Execute initial store shipment based on allocation plan.

**Workflow Execution**:

```python
# season_workflow.py - Phase 1
async def execute_season_launch(context: ForecastingContext):
    # Inventory Agent already produced AllocationResult in Phase 0
    allocation = context.allocation_result

    # Ship initial allocation to stores
    for store_alloc in allocation.store_allocations:
        ship_to_store(store_alloc.store_id, store_alloc.units)

    # Update context
    context.current_week = 0
    context.total_allocated = allocation.initial_store_allocation

    return LaunchResult(
        stores_shipped=len(allocation.store_allocations),
        total_units_shipped=allocation.initial_store_allocation,
        dc_reserve=allocation.dc_holdback
    )
```

**Output**:
- 5,280 units shipped to 50 stores
- 4,320 units held at DC for replenishment
- Store-level allocations logged for tracking

---

### PHASE 2: In-Season Monitoring (Weeks 1-5)

**Goal**: Monitor variance, trigger reforecast if needed, manage replenishment.

**Key Innovation**: Variance Agent decides (not threshold).

**Workflow Execution**:

```python
# season_workflow.py - Phase 2
async def run_inseason_monitoring(context: ForecastingContext, actual_sales: List[int]):
    # Update context with actual sales
    context.actual_sales = actual_sales
    context.current_week = len(actual_sales)

    # Step 1: Variance Agent analyzes (AGENTIC DECISION)
    variance_result = await Runner.run(
        variance_agent,
        input=json.dumps({
            "current_week": context.current_week,
            "forecast_by_week": context.forecast_by_week,
            "actual_sales": actual_sales,
            "original_forecast_total": context.original_forecast.total_demand,
            "weeks_remaining": 12 - context.current_week
        }),
        context=context
    )

    # Step 2: Python acts on agent's decision (DETERMINISTIC)
    if variance_result.final_output.should_reforecast:
        # Run Reforecast Agent
        reforecast_result = await Runner.run(
            reforecast_agent,
            input=json.dumps({
                "original_forecast_by_week": context.forecast_by_week,
                "actual_sales": actual_sales,
                "weeks_observed": context.current_week,
                "variance_analysis": variance_result.final_output.model_dump()
            }),
            context=context
        )

        # Update context with reforecast
        context.forecast_by_week = reforecast_result.final_output.updated_forecast_by_week

    # Step 3: Check if reallocation needed
    if should_run_reallocation(context):
        reallocation_result = await Runner.run(
            reallocation_agent,
            input=json.dumps({
                "store_allocations": [s.model_dump() for s in context.allocation_result.store_allocations],
                "store_actual_sales": context.store_actual_sales,
                "dc_units_available": context.dc_holdback,
                "current_week": context.current_week
            }),
            context=context
        )

        # Execute transfers
        for transfer in reallocation_result.final_output.transfers:
            execute_transfer(transfer)

    return InSeasonResult(
        variance=variance_result.final_output,
        reforecast=reforecast_result.final_output if variance_result.final_output.should_reforecast else None,
        reallocation=reallocation_result.final_output if should_run_reallocation(context) else None
    )
```

**Weekly Loop Pattern**:

```
Week 1:
├── Upload actual sales (user action)
├── Variance Agent analyzes
│   └── Output: "18% variance, stable trend, too early to reforecast"
│   └── should_reforecast = false
├── No reforecast triggered
└── Continue monitoring

Week 2:
├── Upload actual sales
├── Variance Agent analyzes
│   └── Output: "20% variance, slight upward trend, borderline"
│   └── should_reforecast = false (agent reasons: "trend unclear, wait for more data")
└── Continue monitoring

Week 3:
├── Upload actual sales
├── Variance Agent analyzes
│   └── Output: "22% variance, clear upward trend, systematic underforecast"
│   └── should_reforecast = true ✓
├── Reforecast Agent executes Bayesian update
│   └── Output: Updated forecast +17% for weeks 4-12
├── Reallocation Agent checks store performance
│   └── Output: Recommend 800 units from DC to high performers
└── Execute replenishment transfers
```

---

### PHASE 3: Mid-Season Pricing (Week 6)

**Goal**: Check sell-through and apply markdown if below target.

**Workflow Execution**:

```python
# pricing_workflow.py
async def run_markdown_if_needed(context: ForecastingContext):
    # Only run at Week 6 checkpoint
    if context.current_week != 6:
        return None

    # Calculate current sell-through
    sell_through = context.total_sold / context.total_allocated

    # Check against threshold
    if sell_through >= context.markdown_threshold:  # 0.60
        return None  # On track, no markdown needed

    # Run Pricing Agent
    markdown_result = await Runner.run(
        pricing_agent,
        input=json.dumps({
            "current_sell_through": sell_through,
            "target_sell_through": context.target_sell_through,
            "week_number": 6,
            "elasticity": context.elasticity
        }),
        context=context
    )

    return markdown_result.final_output
```

**Decision Flow**:

```
Week 6 Checkpoint
        │
        ▼
Calculate sell_through = total_sold / total_allocated
        │
        ├── sell_through >= 0.60 ──→ "On track" ──→ No markdown
        │
        └── sell_through < 0.60 ──→ Run Pricing Agent
                                        │
                                        ▼
                                 Gap × Elasticity
                                        │
                                        ▼
                                 Markdown Result
                                 (5%, 10%, 15%, ...)
```

**Example Scenarios**:

| Sell-Through | vs Target | Action |
|--------------|-----------|--------|
| 63% | Above 60% | No markdown (ahead of plan) |
| 58% | Below 60% | 5% markdown (gap=2%, ×2.0=4%, round to 5%) |
| 52% | Below 60% | 15% markdown (gap=8%, ×2.0=16%, round to 15%) |
| 40% | Below 60% | 40% markdown (gap=20%, ×2.0=40%, capped) |

---

### PHASE 4: Late Season & Close (Weeks 7-12)

**Goal**: Continue monitoring, manage final replenishment, close season.

**Workflow Execution**:

```python
# season_workflow.py - Phase 4
async def run_late_season(context: ForecastingContext):
    results = []

    for week in range(7, 13):
        # Upload actual sales
        actual_sales = get_weekly_actuals(week)
        context.actual_sales.extend(actual_sales)
        context.current_week = week

        # Variance monitoring (less likely to reforecast with few weeks left)
        variance_result = await Runner.run(variance_agent, ...)

        # Agent will reason: "Week 10 with only 2 weeks left -
        # reforecast has minimal impact, recommend no reforecast"

        # Final replenishment decisions
        if week <= 10 and context.dc_holdback > 0:
            reallocation_result = await Runner.run(reallocation_agent, ...)

        results.append(WeekResult(week=week, variance=variance_result, ...))

    # Season end analysis
    return SeasonEndResult(
        final_sell_through=context.total_sold / context.total_allocated,
        final_mape=calculate_mape(context),
        stockout_count=count_stockouts(context),
        overstock_units=context.manufacturing_qty - context.total_sold,
        week_results=results
    )
```

**Variance Agent Reasoning in Late Season**:

> *"Week 10 shows 15% variance, but only 2 weeks remain. Even with accurate reforecast, we cannot meaningfully adjust allocation or manufacturing. Recommend continuing with current forecast. Focus on final replenishment optimization instead."*

---

## Variance Analysis & Reforecasting Loop

### The Core Innovation

**v3.3 (Simple Threshold)**:
```python
if variance > 0.20:
    reforecast()  # Always reforecast above threshold
```

**v4.0 (Agentic Reasoning)**:
```python
variance_result = await Runner.run(variance_agent, ...)
if variance_result.final_output.should_reforecast:
    reforecast()  # Agent decides based on holistic analysis
```

### What the Variance Agent Considers

1. **Magnitude**: How large is the variance?
2. **Trend**: Is it increasing, decreasing, or stable?
3. **Remaining Season**: How many weeks left to correct?
4. **Likely Cause**: Random noise vs systematic error?
5. **Business Impact**: What's the cost of not reforecasting?

### Decision Matrix (Agent's Implicit Logic)

| Variance | Trend | Weeks Left | Likely Cause | Decision |
|----------|-------|------------|--------------|----------|
| 15% | Stable | 10 | Random noise | No reforecast |
| 22% | Increasing | 9 | Systematic | **Reforecast** |
| 25% | Stable | 3 | Unknown | No reforecast (too late) |
| 30% | Increasing | 8 | Demand surge | **Reforecast + alert** |
| 18% | Decreasing | 7 | One-time event | No reforecast |

### Reforecast Flow Diagram

```
Actual Sales Uploaded
        │
        ▼
┌─────────────────────────────────────┐
│         VARIANCE AGENT              │
│  (Analyzes magnitude, trend, cause) │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
  should_reforecast    should_reforecast
      = false              = true
        │                   │
        ▼                   ▼
   Continue with    ┌─────────────────────────┐
   current forecast │    REFORECAST AGENT     │
                    │  (Bayesian update)       │
                    └─────────────┬───────────┘
                                  │
                                  ▼
                    Updated forecast_by_week
                                  │
                                  ▼
                    Context updated for
                    subsequent agents
```

### Bayesian Reforecast Mechanics

**Prior**: Original forecast
```
μ_prior = original_forecast_by_week
σ²_prior = based on historical MAPE
```

**Likelihood**: Observed actuals
```
μ_likelihood = mean(actual_sales)
σ²_likelihood = variance(actual_sales)
```

**Posterior**: Updated forecast
```
μ_posterior = (σ²_likelihood × μ_prior + σ²_prior × μ_likelihood) / (σ²_prior + σ²_likelihood)
```

**Example**:
- Prior: 650 units/week (forecast)
- Likelihood: 780 units/week (observed average)
- Posterior: ~740 units/week (weighted update)

---

## Data Flow Patterns

### Pre-Season Data Flow

```
User Input
├── Category: "Women's Dresses"
├── Horizon: 12 weeks
└── Season Start: "2025-03-01"
        │
        ▼
┌─────────────────────────────────────┐
│  TrainingDataLoader                 │
│  - historical_sales_2022_2024.csv   │
│  - store_attributes.csv             │
└─────────────────┬───────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│         DEMAND AGENT                │
│  Tool: run_demand_forecast          │
│  Output: ForecastResult             │
└─────────────────┬───────────────────┘
        │
        ├── total_demand: 8000
        ├── forecast_by_week: [600, 650, ...]
        ├── seasonality: {...}
        │
        ▼
┌─────────────────────────────────────┐
│        INVENTORY AGENT              │
│  Tools: cluster_stores,             │
│         allocate_inventory          │
│  Output: AllocationResult           │
└─────────────────┬───────────────────┘
        │
        ├── manufacturing_qty: 9600
        ├── dc_holdback: 4320
        ├── store_allocations: [...]
        │
        ▼
    ForecastingContext
    (Shared state for in-season)
```

### In-Season Data Flow

```
Weekly Actual Sales Upload
        │
        ▼
┌─────────────────────────────────────┐
│        VARIANCE AGENT               │
│  Input: forecast + actuals          │
│  Output: VarianceAnalysis           │
└─────────────────┬───────────────────┘
        │
        ├── should_reforecast: true/false
        │
        ├── if true ──────────────────────┐
        │                                  ▼
        │             ┌─────────────────────────────────────┐
        │             │       REFORECAST AGENT              │
        │             │  Input: prior forecast + actuals    │
        │             │  Output: ReforecastResult           │
        │             └─────────────────┬───────────────────┘
        │                               │
        │                               ├── updated_forecast_by_week
        │                               │
        │             ┌─────────────────┴───────────────────┐
        │             │  Context.forecast_by_week updated   │
        │             └─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│      REALLOCATION AGENT             │
│  Input: store performance data      │
│  Output: ReallocationAnalysis       │
└─────────────────┬───────────────────┘
        │
        ├── transfers: [...]
        │
        ▼
    Execute replenishment
```

---

## Example Scenarios

### Scenario 1: Successful Season (No Intervention Needed)

**Setup**:
- Forecast: 8,000 units
- Manufacturing: 9,600 units (20% safety stock)
- DC Holdback: 45%

**Week-by-Week**:

| Week | Forecast | Actual | Variance | Agent Decision |
|------|----------|--------|----------|----------------|
| 1 | 600 | 620 | +3% | "Within normal range, no action" |
| 2 | 650 | 640 | -2% | "Minor negative, stable trend" |
| 3 | 700 | 710 | +1% | "Tracking well, no action" |
| 4 | 750 | 760 | +1% | "Consistent performance" |
| 5 | 800 | 820 | +3% | "Slight positive, peak week expected" |
| 6 | 850 | 870 | +2% | **Checkpoint: 62% sell-through > 60% target → No markdown** |
| 7-12 | ... | ... | ±5% | Continue monitoring |

**Result**:
- Final sell-through: 95%
- MAPE: 8%
- No reforecast needed
- No markdown applied
- Full margin preserved

---

### Scenario 2: High Demand Surge (Reforecast Triggered)

**Setup**: Same as Scenario 1

**Week-by-Week**:

| Week | Forecast | Actual | Variance | Agent Decision |
|------|----------|--------|----------|----------------|
| 1 | 600 | 720 | +20% | "Significant variance, but one week is too early" |
| 2 | 650 | 780 | +20% | "Consistent +20%, trend stable, monitoring" |
| 3 | 700 | 875 | +25% | **"22% avg, increasing trend, systematic underforecast. REFORECAST."** |

**Variance Agent Reasoning (Week 3)**:
> *"Three weeks of consistent positive variance (20%, 20%, 25%) with increasing trend indicates systematic underforecast, not random noise. With 9 weeks remaining, reforecasting now allows meaningful correction. Recommending Bayesian update with 65% weight on observed data."*

**Reforecast Agent Output**:
- Original forecast: 8,000 units
- Updated forecast: 9,360 units (+17%)
- Adjustment applied to weeks 4-12

**Subsequent Actions**:
- Week 4: Reallocation Agent recommends 800 units from DC to high performers
- Week 5: Emergency reorder alert (demand exceeds manufacturing)
- Week 6: 68% sell-through → No markdown needed

**Result**:
- Final sell-through: 98%
- Captured additional demand through reforecast
- 3 stores had brief stockouts before reallocation

---

### Scenario 3: Low Demand (Markdown Applied)

**Setup**: Same as Scenario 1

**Week-by-Week**:

| Week | Forecast | Actual | Variance | Agent Decision |
|------|----------|--------|----------|----------------|
| 1 | 600 | 540 | -10% | "Negative variance, but single week" |
| 2 | 650 | 560 | -14% | "Consistent negative, possible demand softness" |
| 3 | 700 | 580 | -17% | "Trend stable at -15%, not accelerating" |
| 4 | 750 | 620 | -17% | "Holding at -15-17%, systematic overforecast" |
| 5 | 800 | 680 | -15% | "No improvement, but trend not worsening" |

**Variance Agent Reasoning (Week 5)**:
> *"Five weeks of consistent -15% variance with stable trend. This is systematic overforecast, but since trend is not worsening and we're approaching Week 6 markdown checkpoint, recommend NO reforecast. Pricing intervention at Week 6 is more appropriate than forecast adjustment at this point."*

**Week 6 Markdown Checkpoint**:
- Total sold: 2,980 units
- Total allocated: 5,280 units
- Sell-through: 56% (below 60% target)
- Gap: 4%
- Markdown: 4% × 2.0 = 8% → rounds to **10%**

**Pricing Agent Output**:
```json
{
  "recommended_markdown_pct": 0.10,
  "explanation": "56% sell-through at Week 6 is 4pp below target. 10% markdown should accelerate sell-through by 8-10% based on historical elasticity."
}
```

**Result**:
- Markdown applied Week 6
- Weeks 7-12: Sales lift +12%
- Final sell-through: 82%
- Avoided larger overstock

---

## Quick Reference

### Decision Thresholds

| Decision | Mechanism | Notes |
|----------|-----------|-------|
| **Reforecast** | Variance Agent decides | Not simple threshold; considers trend, remaining weeks |
| **Markdown** | Sell-through < 60% at Week 6 | Gap × Elasticity formula |
| **Reallocation** | High performer stockout risk | Agent recommends transfers |
| **Emergency Order** | Variance > 30% + stockout projection | Alert to user |

### Agent Tool Mapping

| Agent | Tools | Output Guardrails |
|-------|-------|-------------------|
| Demand | `run_demand_forecast` | Unit conservation, reasonableness |
| Inventory | `cluster_stores`, `allocate_inventory` | Unit conservation (critical) |
| Pricing | `calculate_markdown` | 40% cap, 5% rounding |
| Variance | `analyze_variance_data` | - |
| Reforecast | `bayesian_reforecast` | - |
| Reallocation | `analyze_store_performance`, `generate_transfer_recommendations` | - |

### Key Formulas

**Manufacturing Qty**:
```
manufacturing_qty = forecast × (1 + safety_stock_pct)
```

**Store Allocation**:
```
store_units = cluster_allocation × (0.70 × historical_factor + 0.30 × attribute_factor)
```

**Markdown**:
```
gap = target_sell_through - current_sell_through
raw_markdown = gap × elasticity (default 2.0)
final_markdown = round_to_5%(raw_markdown), cap at 40%
```

**Bayesian Reforecast**:
```
posterior = (prior_variance × likelihood + likelihood_variance × prior) / (prior_variance + likelihood_variance)
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | OpenAI Agents SDK 0.2+ |
| LLM | GPT-4o-mini |
| Forecasting | Prophet + ARIMA (ensemble) |
| Clustering | K-means (scikit-learn) |
| Validation | Pydantic 2.0+ |
| Frontend | Streamlit 1.28+ |
| Visualization | Plotly 5.18+ |

---

## Summary of Changes from v3.3

### Architectural Changes

| Aspect | v3.3 | v4.0 |
|--------|------|------|
| Orchestration | Agent-as-tool handoffs | Deterministic Python workflows |
| Type Safety | String outputs | Pydantic schemas enforced by SDK |
| Variance Decision | `if variance > 0.20` | Variance Agent reasons holistically |
| Reforecast | Simple re-run of forecast | Bayesian update with prior/likelihood |
| Replenishment | Fixed cadence | Reallocation Agent analyzes performance |
| Frontend | React + TypeScript | Streamlit |

### New Agents

1. **Variance Agent**: Reasons about variance holistically
2. **Reforecast Agent**: Bayesian posterior estimation
3. **Reallocation Agent**: Strategic replenishment analysis

### New Capabilities

1. **Seasonality Insights**: Peak/trough weeks, monthly effects
2. **Reasoning Traces**: `reasoning_steps`, `key_factors` in output
3. **Agent Status Hooks**: Real-time UI updates
4. **Sidebar Dashboard**: Session metrics and agent status

### Removed/Changed

1. **Confidence Scoring**: Removed (was v3.2)
2. **Cluster-specific Markdowns**: Now uniform (simplified)
3. **Hardcoded Thresholds**: Replaced with agentic reasoning

---

**Document Owner**: Independent Study Project
**Last Updated**: 2025-12-04
**Version**: 4.0
**Related Documents**:
- [Architecture v4.0](architecture-v4.0.md) - Technical architecture details
- [Product Brief v3.3](1_product_brief_v3.3.md) - Business context
- [Data Specification v3.2](6_data_specification_v3.2.md) - Data formats

---

*Document generated by BMad Master v4.0*
