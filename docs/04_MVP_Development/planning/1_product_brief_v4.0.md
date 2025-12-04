# Product Brief: Agentic Retail Forecasting System

**Version:** 4.0
**Date:** 2025-12-04
**Status:** Active Implementation (SDK Branch)
**Focus:** Deterministic Orchestration with Agentic Reasoning for Self-Correcting Forecasts

---

## Executive Summary

We have built a **6-agent retail forecasting system** that combines deterministic Python workflow orchestration with LLM-powered reasoning. The system forecasts demand, allocates inventory, monitors variance, and self-corrects through Bayesian reforecasting - all with transparent reasoning that users can understand and trust.

### What Makes v4.0 Different

| Aspect | v3.x (Agent-as-Tool) | v4.0 (Deterministic + Agentic) |
|--------|---------------------|-------------------------------|
| **Architecture** | Agents call agents via handoffs | Python workflows control agents |
| **Agents** | 3 agents | 6 specialized agents |
| **Type Safety** | String outputs | Pydantic schemas enforced by SDK |
| **Variance Handling** | Simple threshold `if > 20%` | Agent reasons holistically |
| **Reforecasting** | Re-run forecast from scratch | Bayesian update with prior + likelihood |
| **Replenishment** | Fixed cadence | Strategic analysis by Reallocation Agent |
| **Frontend** | React + TypeScript | Streamlit |
| **Explainability** | Basic explanations | Reasoning traces, key factors, seasonality insights |

### The Core Innovation: Three-Layer Separation

```
WORKFLOWS (Python)      →  Control WHEN agents run
AGENTS (LLM)            →  Decide HOW to reason and what to recommend
TOOLS (Pure Functions)  →  Execute WHAT computations to perform
```

This separation provides:
- **Reliability**: Python `if/while` statements, not fragile string parsing
- **Type Safety**: Pydantic schemas validate every output
- **Debuggability**: Clear control flow you can trace
- **Agentic Intelligence**: LLMs reason about complex decisions

---

## The Problem We Solve

Based on interviews with 5 retail practitioners (furniture, mass retail, fashion):

### 1. Inaccurate Demand Forecasting (PP-001, PP-019)
> *"Traditional numerical ML models don't provide enough accuracy and agility to predict demand"* - Furniture Retailer

**Impact**: 20% forecast error on product launches → poor allocation → expensive redistribution

### 2. Location-Specific Allocation Failures (PP-002, PP-015)
> *"When forecasts are off, they must quickly reallocate inventory"* - Furniture Retailer

**Impact**: 5 hrs/week firefighting + ongoing stockout/overstock costs

### 3. Late Markdown Decisions (PP-016)
> *"3-day data lag prevents timely action"* - Fashion Retailer

**Impact**: **$500K lost margin annually** from missed markdown timing

### 4. Rigid Systems Can't Self-Correct
> *"By the time we realize forecast is wrong, it's too late to fix allocation"*

**Impact**: Entire season runs on bad forecast → systematic over/understock

---

## Our Solution: 6-Agent System with Self-Correction

### The 6 Agents

| Agent | Purpose | Key Innovation |
|-------|---------|----------------|
| **Demand Agent** | Forecast total demand | Prophet + ARIMA ensemble with seasonality insights |
| **Inventory Agent** | Allocate to stores | K-means clustering + 3-layer hierarchical allocation |
| **Pricing Agent** | Calculate markdowns | Gap × Elasticity formula with guardrails |
| **Variance Agent** | Analyze forecast accuracy | **Agentic reasoning** (not simple threshold) |
| **Reforecast Agent** | Update forecast with actuals | **Bayesian inference** with prior/likelihood |
| **Reallocation Agent** | Strategic replenishment | Store performance analysis + transfer recommendations |

### How Self-Correction Works

**v3.x Approach** (Simple Threshold):
```python
if variance > 0.20:
    reforecast()  # Always triggers, no reasoning
```

**v4.0 Approach** (Agentic Reasoning):
```python
variance_result = await Runner.run(variance_agent, ...)

# Agent considers: magnitude, trend, remaining weeks, likely cause
# Agent decides: should_reforecast = true/false with explanation

if variance_result.final_output.should_reforecast:
    reforecast_result = await Runner.run(reforecast_agent, ...)
```

**Why This Matters**:
- 25% variance in Week 2 with 10 weeks remaining → Agent recommends reforecast
- 25% variance in Week 10 with 2 weeks remaining → Agent says "too late to correct meaningfully"
- 20% one-time spike → Agent identifies as "random noise, not systematic"

---

## Business Value

| Benefit | Description | Expected Impact |
|---------|-------------|-----------------|
| **Self-Correcting Forecasts** | Bayesian reforecasting updates predictions with actual sales | 15-20% improvement in late-season accuracy |
| **Intelligent Variance Analysis** | Agent reasons about cause and timing, not just magnitude | Fewer unnecessary reforecasts, better-timed corrections |
| **Transparent Reasoning** | Every decision includes explanation and key factors | Merchandisers understand and trust recommendations |
| **Strategic Replenishment** | Agent identifies high/low performers and recommends transfers | Reduce stockouts at top stores by 20-30% |
| **Optimized Markdowns** | Gap × Elasticity with automatic validation | 10-15% reduction in markdown costs |

---

## Product Scope: What We Forecast

### Hierarchical Forecasting Approach

**We DO forecast**:
- ✅ **Category-level demand** (e.g., "Women's Dresses" total)
- ✅ **Weekly temporal distribution** (demand curve across season)
- ✅ **Cluster-level spatial distribution** (% by store cluster)
- ✅ **Store-level allocation factors** (within each cluster)

**We DON'T forecast**:
- ❌ Individual SKU demand
- ❌ Store × SKU × Week combinations (too granular, too noisy)
- ❌ Daily granularity

### Forecast Output Example

```python
ForecastResult(
    total_demand=8000,
    forecast_by_week=[600, 650, 700, 750, 800, 850, 700, 650, 600, 550, 500, 450],
    safety_stock_pct=0.20,
    confidence=0.85,
    model_used="ensemble_prophet_arima",
    seasonality=SeasonalityExplanation(
        peak_weeks=[5, 6],
        trough_weeks=[11, 12],
        seasonal_range=0.35,
        monthly_effects={"March": 1.1, "April": 1.2, "May": 0.9},
        insight="Peak demand expected weeks 5-6 aligned with back-to-school preparation"
    ),
    explanation="Forecast based on 3-year historical patterns with strong spring seasonality...",
    lower_bound=[500, 550, 600, ...],
    upper_bound=[700, 750, 800, ...]
)
```

---

## The 6 Agents: Detailed Specifications

### Agent 1: Demand Agent

**Purpose**: Generate demand forecast using Prophet + ARIMA ensemble.

**Key Outputs**:
- Total season demand
- Weekly demand curve (12 weeks)
- Seasonality insights (peak/trough weeks, monthly effects)
- Confidence bounds (upper/lower)

**How It Works**:
1. Load 3 years of historical sales data
2. Train Prophet model (captures seasonality)
3. Train ARIMA model (captures trend)
4. Ensemble weighting based on validation MAPE
5. Extract seasonality insights for explainability
6. Align to `season_start_date` for calendar events

**Output Schema**: `ForecastResult`

**Agent Reasoning Example**:
> *"Historical data shows 35% seasonal variation with peaks in late April. Season starts March 1st, aligning with back-to-school prep. Prophet captures seasonality well (MAPE 12%), ARIMA captures recent trend (MAPE 15%). Ensemble weight: 60% Prophet, 40% ARIMA. Recommend 20% safety stock given moderate forecast uncertainty."*

---

### Agent 2: Inventory Agent

**Purpose**: Cluster stores and allocate inventory hierarchically.

**Key Outputs**:
- Manufacturing quantity (forecast × safety stock)
- DC holdback (reserve for replenishment)
- Cluster allocations (3 clusters)
- Store allocations (all 50 stores)
- Reasoning steps and key factors

**How It Works**:
1. **K-means clustering** on 7 store attributes:
   - avg_weekly_sales_12mo (most important)
   - store_size_sqft
   - median_income
   - location_tier (A/B/C)
   - fashion_tier (Premium/Mid/Value)
   - store_format (Mall/Standalone/Outlet)
   - region

2. **3-layer hierarchical allocation**:
   - Layer 1: Manufacturing qty = forecast × (1 + safety_stock_pct)
   - Layer 2: DC holdback vs initial store allocation
   - Layer 3: Store allocation = 70% historical + 30% attributes

**Output Schema**: `AllocationResult`

**Agent Reasoning Example**:
> *"K-means clustering on 7 features yields 3 distinct segments. Fashion_Forward stores (15 stores) show 2.3x average velocity and should receive 40% of initial allocation. NYC-001 specifically has highest historical performance - allocating 488 units (9.2% of initial). DC holdback at 45% provides buffer for weekly replenishment."*

---

### Agent 3: Pricing Agent

**Purpose**: Calculate markdown when sell-through is below target.

**Key Outputs**:
- Recommended markdown percentage (0-40%)
- Gap analysis (target vs current)
- Elasticity used
- Explanation of recommendation

**How It Works**:
```
gap = target_sell_through - current_sell_through
raw_markdown = gap × elasticity (default 2.0)
final_markdown = round_to_5%(raw_markdown), cap at 40%
```

**Output Schema**: `MarkdownResult`

**Guardrails**:
- Maximum 40% markdown (hard cap)
- Round to nearest 5%
- Validate inputs are in valid ranges

**Agent Reasoning Example**:
> *"Week 6 checkpoint shows 52% sell-through, 8 percentage points below 60% target. With 6 weeks remaining and 48% inventory on hand, markdown intervention warranted. Gap × Elasticity: 8% × 2.0 = 16% → rounds to 15%. Historical data suggests 15% markdown drives 12-15% sell-through improvement."*

---

### Agent 4: Variance Agent (NEW in v4.0)

**Purpose**: Reason holistically about forecast variance and decide if reforecasting is needed.

**Key Innovation**: Agent decides `should_reforecast` based on reasoning, not simple threshold.

**Key Outputs**:
- Variance percentage and severity
- Trend direction (increasing/decreasing/stable)
- Likely cause (systematic underforecast, random noise, one-time event)
- **Decision: should_reforecast** (boolean with reasoning)
- Recommended adjustments

**What the Agent Considers**:
1. **Magnitude**: How large is the variance?
2. **Trend**: Is it getting better or worse?
3. **Remaining Season**: How many weeks left to correct?
4. **Likely Cause**: Random noise vs systematic error?
5. **Business Impact**: What's the cost of not reforecasting?

**Output Schema**: `VarianceAnalysis`

**Agent Reasoning Example**:
> *"Three-week variance of 22% exceeds typical threshold, but more importantly, the trend is increasing (20% → 20% → 25%). This pattern suggests systematic underforecast rather than random volatility. Given 9 weeks remaining, we have time to correct. Recommending Bayesian reforecast to update remaining weeks."*

**Contrast with Simple Threshold**:
| Scenario | Simple `if > 20%` | Variance Agent |
|----------|------------------|----------------|
| 22% variance, Week 2, increasing trend | Reforecast | Reforecast (correct) |
| 22% variance, Week 10, stable trend | Reforecast | **No reforecast** (too late to matter) |
| 25% one-time spike, Week 3 | Reforecast | **No reforecast** (identifies as noise) |

---

### Agent 5: Reforecast Agent (NEW in v4.0)

**Purpose**: Update forecast using Bayesian inference with actual sales data.

**Key Innovation**: Bayesian update combines prior (original forecast) with likelihood (observed actuals).

**Key Outputs**:
- Updated forecast by week
- Adjustment factor
- Posterior confidence
- Prior vs likelihood weights

**How It Works**:
```
Prior: Original forecast (mean, variance from historical MAPE)
Likelihood: Observed actual sales (observed mean, std)
Posterior: Weighted combination via conjugate Gaussian update

posterior_mean = (prior_var × likelihood_mean + likelihood_var × prior_mean)
                 / (prior_var + likelihood_var)
```

**Output Schema**: `ReforecastResult`

**Agent Reasoning Example**:
> *"Applying Bayesian update with conjugate Gaussian prior. Prior: original forecast with variance based on historical MAPE. Likelihood: 3 weeks of actuals with observed variance. Given strong consistent signal (22% positive variance, increasing trend), posterior weights likelihood at 65%. Updated forecast: +17% adjustment for weeks 4-12."*

---

### Agent 6: Reallocation Agent (NEW in v4.0)

**Purpose**: Analyze store performance and recommend strategic replenishment.

**Key Outputs**:
- Should reallocate (boolean)
- Strategy (dc_only vs hybrid)
- High performers (list of stores)
- Underperformers (list of stores)
- Transfer orders (from/to/units/reason)
- Expected improvement metrics

**How It Works**:
1. Analyze store-level sales velocity
2. Calculate sell-through by store
3. Identify stockout risk at high performers
4. Identify excess inventory at underperformers
5. Generate transfer recommendations (DC releases + store-to-store)

**Output Schema**: `ReallocationAnalysis`

**Agent Reasoning Example**:
> *"Analysis shows 3 high-performing stores at stockout risk within 2 weeks. Recommend hybrid strategy: 800 units from DC to top performers, plus 50-unit transfer from underperforming rural store. Expected to improve overall sell-through by 8% and prevent stockouts at 3 locations."*

---

## Technology Stack

### Core Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Agent Framework** | OpenAI Agents SDK 0.2+ | Agent orchestration with typed outputs |
| **LLM** | GPT-4o-mini | Reasoning and generation |
| **Frontend** | Streamlit 1.28+ | Interactive web UI |
| **Visualization** | Plotly 5.18+ | Charts and graphs |
| **Forecasting** | Prophet 1.1+, statsmodels | Time series models |
| **ML** | scikit-learn 1.3+ | K-means clustering |
| **Validation** | Pydantic 2.0+ | Schema enforcement |
| **Data** | Pandas 2.0+, NumPy | Data manipulation |

### Key Architectural Patterns

**1. Deterministic Workflow Orchestration**
```python
# Python controls WHEN agents run
async def run_forecast_with_variance_loop(context):
    forecast = await Runner.run(demand_agent, ...)

    if context.actual_sales:
        variance = await Runner.run(variance_agent, ...)

        if variance.final_output.should_reforecast:
            reforecast = await Runner.run(reforecast_agent, ...)
```

**2. Typed Output with Pydantic**
```python
demand_agent = Agent(
    name="Demand Forecasting Agent",
    output_type=ForecastResult,  # SDK enforces schema
    output_guardrails=[validate_forecast_output],
)
```

**3. RunContextWrapper for Dependencies**
```python
@function_tool
def run_demand_forecast(
    ctx: RunContextWrapper[ForecastingContext],  # Injected, not in prompt
    category: str,
    forecast_horizon_weeks: int
) -> ForecastToolResult:
    # ctx.context has data_loader, session_id, etc.
    # LLM never sees raw data
```

**4. Guardrails on Structured Data**
```python
@output_guardrail
async def validate_allocation_output(ctx, result: AllocationResult):
    # Validate unit conservation
    store_sum = sum(s.units for s in result.store_allocations)
    if store_sum != result.initial_store_allocation:
        return GuardrailResult(tripwire_triggered=True, ...)
```

---

## User Interface

### Streamlit Application

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│                        Header                                │
│                "Agentic Retail Forecasting"                  │
├─────────────┬───────────────────────────────────────────────┤
│   Sidebar   │                Main Content                    │
│             │                                                │
│ • Session   │  Tab 1: Pre-Season Planning                    │
│   Info      │  • Category/horizon selection                  │
│             │  • Forecast generation                         │
│ • Agent     │  • Allocation display                          │
│   Status    │                                                │
│   (live)    │  Tab 2: In-Season Updates                      │
│             │  • Actual sales upload                         │
│ • Key       │  • Variance analysis                           │
│   Metrics   │  • Reforecast display                          │
│             │                                                │
│             │  Tab 3: Pricing/Markdown                       │
│             │  • Markdown recommendations                    │
│             │                                                │
│             │  Tab 4: Analytics                              │
│             │  • Plotly charts                               │
│             │  • Store allocation tables                     │
└─────────────┴───────────────────────────────────────────────┘
```

**Key Features**:
- Real-time agent status updates via RunHooks
- File upload for weekly actual sales CSV
- Interactive Plotly charts (forecast bands, variance trends)
- Store cluster visualization
- Reasoning traces displayed for transparency

---

## Success Metrics

### Forecast Accuracy (Primary)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE** | <20% | Compare forecast vs actuals by week |
| **Bias** | ±5% | Check systematic over/under-forecasting |
| **Reforecast Improvement** | >10% | MAPE after reforecast vs before |

### Business Impact (Secondary)

| Metric | 6-Month Target | 12-Month Target |
|--------|---------------|-----------------|
| **Stockout Reduction** | 15% | 25% |
| **Overstock Reduction** | 10% | 20% |
| **Markdown Cost Reduction** | 10% | 15% |

### System Performance

| Metric | Target |
|--------|--------|
| **Full Workflow Runtime** | <60 seconds |
| **Variance Detection Accuracy** | 90%+ |
| **Guardrail Pass Rate** | 95%+ |

---

## Data Requirements

### Input Data

**1. Historical Sales Data** (2-3 years)
- File: `historical_sales_2022_2024.csv`
- Records: ~164,400 (1,096 days × 50 stores × 3 categories)
- Fields: `date, store_id, category, units_sold, revenue`

**2. Store Attributes**
- File: `store_attributes.csv`
- Records: 50 stores
- Fields: `store_id, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region, avg_weekly_sales_12mo`

**3. Actual Sales (In-Season)**
- Weekly CSV uploads
- Fields: `store_id, category, week, units_sold`

### Test Scenarios

| Scenario | Characteristics | Expected Behavior |
|----------|-----------------|-------------------|
| **Normal** | Standard demand, Week 5 +30% spike | Reforecast triggered Week 5-6 |
| **High Demand** | +25% overall, Week 5 +40% | Early reforecast, potential stockout warning |
| **Low Demand** | -20% overall | Markdown triggered Week 6 |

---

## MVP Scope

### What's Included

✅ **6-Agent System**: Demand, Inventory, Pricing, Variance, Reforecast, Reallocation
✅ **Deterministic Orchestration**: Python workflows control agent execution
✅ **Typed Outputs**: Pydantic schemas for all agent outputs
✅ **Guardrails Validation**: Unit conservation, markdown caps
✅ **Bayesian Reforecasting**: Prior + likelihood → posterior
✅ **Agentic Variance Analysis**: Agent reasons, not threshold
✅ **Seasonality Insights**: Peak/trough weeks, monthly effects
✅ **Reasoning Traces**: `reasoning_steps`, `key_factors` in outputs
✅ **Streamlit UI**: Interactive dashboard with real-time status
✅ **Agent Status Hooks**: Live updates during workflow execution
✅ **Single Category**: User selects from available categories
✅ **12-Week Season**: Spring 2025 test scenario
✅ **50 Stores**: 3 clusters via K-means

### What's NOT Included

❌ **Multi-category parallel forecasting**
❌ **SKU-level granularity**
❌ **Multi-season overlap**
❌ **External data integration** (weather, social trends)
❌ **Automated parameter optimization**
❌ **Production deployment** (local development only)

---

## Workflow Summary

### 12-Week Season Flow

```
Week -24 (Pre-Season):
├── Demand Agent → ForecastResult
├── Inventory Agent → AllocationResult
└── Store initial shipments planned

Week 0 (Launch):
└── Execute initial store allocation

Weeks 1-5 (Early Season):
├── Upload actual sales
├── Variance Agent analyzes
│   └── If should_reforecast: Reforecast Agent runs
├── Reallocation Agent checks performance
└── Execute replenishment transfers

Week 6 (Markdown Checkpoint):
├── Calculate sell_through
└── If < 60%: Pricing Agent → MarkdownResult

Weeks 7-12 (Late Season):
├── Continue variance monitoring
├── Final replenishment decisions
└── Season close analysis
```

---

## Key Decisions Made in v4.0

### Why Deterministic Orchestration?

**Problem with Agent-as-Tool (v3.x)**:
- String pattern matching for control flow
- Fragile, hard to debug
- No type safety between agents

**Solution (v4.0)**:
- Python `if/while` controls when agents run
- Agents return typed Pydantic models
- Clear separation of concerns

### Why Agentic Variance Analysis?

**Problem with Simple Threshold**:
- `if variance > 0.20: reforecast()` ignores context
- Week 2 variance ≠ Week 10 variance
- Random spike ≠ systematic error

**Solution (v4.0)**:
- Variance Agent reasons about magnitude, trend, timing, cause
- Agent decides with explanation
- Better, more targeted reforecasts

### Why Bayesian Reforecast?

**Problem with Re-running Forecast**:
- Throws away original forecast entirely
- Doesn't weight observed data appropriately
- No confidence calibration

**Solution (v4.0)**:
- Bayesian update combines prior (forecast) + likelihood (actuals)
- Automatic weighting based on variance
- Posterior confidence reflects data quality

### Why Streamlit Instead of React?

**Problem with React**:
- Separate backend/frontend development
- More complex deployment
- Longer development cycle

**Solution (v4.0)**:
- Streamlit enables rapid iteration
- Python-native integration with agents
- Single-language development
- Suitable for PoC/MVP stage

---

## Future Considerations

1. **Multi-Category Support**: Parallel forecasting across categories
2. **External Data Integration**: Weather, social trends, competitor pricing
3. **Feedback Loop**: Learn from actual vs predicted over time
4. **Fine-tuned Models**: Domain-specific LLMs for retail
5. **Production Deployment**: Cloud hosting with authentication
6. **API Exposure**: RESTful API for integration with existing systems

---

## Glossary

| Term | Definition |
|------|------------|
| **Agentic Reasoning** | LLM-powered decision-making that considers context, not just rules |
| **Bayesian Reforecast** | Updating forecast using prior + likelihood → posterior |
| **Deterministic Orchestration** | Python code controls workflow, agents handle reasoning |
| **Guardrails** | Validation rules on structured output (e.g., unit conservation) |
| **Output Schema** | Pydantic model that defines agent output structure |
| **RunContextWrapper** | Dependency injection for tools without sending to LLM |
| **Variance Analysis** | Assessment of forecast accuracy with trend and cause |

---

## Related Documents

- [Architecture v4.0](architecture-v4.0.md) - Technical architecture details
- [Process Workflow v4.0](2_process_workflow_v4.0.md) - Operational workflow
- [Data Specification v3.2](6_data_specification_v3.2.md) - Data formats

---

## Summary of Changes from v3.3

### Major Changes

| Aspect | v3.3 | v4.0 |
|--------|------|------|
| **Agents** | 3 (Demand, Inventory, Pricing) | 6 (+ Variance, Reforecast, Reallocation) |
| **Orchestration** | Agent-as-tool handoffs | Deterministic Python workflows |
| **Type Safety** | String outputs | Pydantic schemas enforced by SDK |
| **Variance Handling** | Simple threshold | Agentic reasoning |
| **Reforecast Method** | Re-run forecast | Bayesian update |
| **Replenishment** | Fixed cadence | Strategic analysis |
| **Frontend** | React + TypeScript | Streamlit |
| **Explainability** | Basic | Reasoning traces, key factors, seasonality |

### New Capabilities

1. **Variance Agent**: Reasons about variance holistically
2. **Reforecast Agent**: Bayesian posterior estimation
3. **Reallocation Agent**: Strategic replenishment with transfers
4. **Seasonality Insights**: Peak/trough weeks, monthly effects
5. **Reasoning Traces**: Step-by-step reasoning in outputs
6. **Agent Status Hooks**: Real-time UI updates
7. **Guardrails**: Validation on structured data

### Removed

1. Parameter-driven natural language input (simplified to direct configuration)
2. React frontend (replaced with Streamlit)
3. Hardcoded archetype references

---

**Document Owner**: Independent Study Project
**Last Updated**: 2025-12-04
**Version**: 4.0

---

*Document generated by BMad Master v4.0*
