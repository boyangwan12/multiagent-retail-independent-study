# Product Requirements Document (PRD) v4.0
# Agentic Retail Forecasting System with Self-Correcting Workflows

**Version:** 4.0
**Date:** 2025-12-04
**Status:** Active Implementation (SDK Branch)
**Product Owner:** Independent Study Project
**Architecture:** Deterministic Orchestration with Agentic Reasoning

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [Target Users](#3-target-users)
4. [User Stories](#4-user-stories)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Acceptance Criteria](#7-acceptance-criteria)
8. [Success Metrics](#8-success-metrics)
9. [System Features](#9-system-features)
10. [Data Requirements](#10-data-requirements)
11. [Technical Constraints](#11-technical-constraints)
12. [Assumptions & Dependencies](#12-assumptions--dependencies)
13. [Out of Scope](#13-out-of-scope)
14. [Release Plan](#14-release-plan)
15. [Appendix](#15-appendix)

---

## 1. Executive Summary

### 1.1 Product Overview

The Agentic Retail Forecasting System is a **6-agent AI system** built on the OpenAI Agents SDK that combines deterministic Python workflow orchestration with LLM-powered reasoning. The system forecasts demand, allocates inventory, monitors variance with intelligent reasoning, self-corrects through Bayesian reforecasting, and manages strategic replenishment - all with transparent, explainable decision-making.

**Core Innovation (v4.0 - Deterministic + Agentic):**

| Layer | Control | Purpose |
|-------|---------|---------|
| **Workflows** | Python `if/while` | Controls WHEN agents run |
| **Agents** | LLM reasoning | Decides HOW to analyze and recommend |
| **Tools** | Pure functions | Executes WHAT computations |

**Key Differentiators:**
- **Agentic Variance Analysis**: Agent reasons holistically about variance (not simple threshold)
- **Bayesian Reforecasting**: Updates predictions using prior + likelihood → posterior
- **Strategic Replenishment**: Agent analyzes store performance and recommends transfers
- **Typed Data Flow**: Pydantic schemas enforced by SDK at every layer
- **Guardrails Validation**: Business rules validated on structured data
- **Reasoning Traces**: Every decision includes explanation and key factors

### 1.2 Business Problem

Fashion retailers face critical challenges resulting in significant financial losses:

**1. Inaccurate Demand Forecasting (PP-001, PP-019):**
- Traditional ML models achieve only 20%+ forecast error on new product launches
- Result: Poor manufacturing decisions → $500K+ lost margin annually

**2. Location-Specific Allocation Failures (PP-002, PP-015):**
- Store-level demand patterns not captured → inventory misallocation
- Impact: Stockouts in high-demand stores, overstock in low-demand stores

**3. Late Markdown Decisions (PP-016):**
- 3-day data lag prevents timely price reductions
- Impact: **$500K lost margin annually** from missed markdown timing

**4. Rigid Systems Can't Self-Correct:**
- By the time variance is detected, it's too late to meaningfully adjust
- Impact: Entire season runs on bad forecast → systematic over/understock

### 1.3 Solution Overview

A 6-agent system with deterministic orchestration and agentic reasoning:

**Agent 1: Demand Agent**
- Ensemble forecasting (Prophet + ARIMA)
- Seasonality insights (peak/trough weeks, monthly effects)
- Calendar-aligned seasonality for events

**Agent 2: Inventory Agent**
- K-means store clustering (7 features)
- 3-layer hierarchical allocation
- Reasoning traces and key factors

**Agent 3: Pricing Agent**
- Gap × Elasticity markdown formula
- Guardrails (40% cap, 5% rounding)
- Week 6 checkpoint logic

**Agent 4: Variance Agent (NEW)**
- Agentic reasoning about variance (not threshold)
- Considers: magnitude, trend, remaining weeks, likely cause
- Decides: `should_reforecast` with explanation

**Agent 5: Reforecast Agent (NEW)**
- Bayesian inference (prior + likelihood → posterior)
- Automatic weighting based on data quality
- Posterior confidence calibration

**Agent 6: Reallocation Agent (NEW)**
- Store performance analysis (velocity, sell-through)
- Transfer recommendations (DC releases + store-to-store)
- Strategic replenishment decisions

**Workflow Orchestration:**
- Python controls agent execution (deterministic)
- Typed data passing via Pydantic schemas
- Guardrails validation on structured output
- RunContextWrapper for dependency injection

### 1.4 Expected Business Impact

| Benefit | Target | Timeline |
|---------|--------|----------|
| **Self-Correcting Forecasts** | 15-20% late-season accuracy improvement | Immediate |
| **Intelligent Variance Analysis** | Fewer unnecessary reforecasts | Immediate |
| **Transparent Reasoning** | 80%+ user trust in recommendations | 6 months |
| **Strategic Replenishment** | 20-30% stockout reduction at top stores | 6-12 months |
| **Optimized Markdowns** | 10-15% markdown cost reduction | 6-12 months |

---

## 2. Product Vision

### 2.1 Long-Term Vision

Build a self-correcting retail forecasting platform that combines deterministic reliability with agentic intelligence, providing accurate forecasts, optimal allocation, and transparent reasoning that merchandisers can understand and trust.

### 2.2 MVP Vision (v4.0)

Prove the deterministic + agentic architecture using a 12-week fashion season scenario, demonstrating:
- **6-agent coordination** with typed data flow
- **Agentic variance analysis** that reasons (not thresholds)
- **Bayesian reforecasting** that updates intelligently
- **Strategic replenishment** based on store performance
- **MAPE 12-18%** forecast accuracy
- **<60 second** workflow runtime
- **Transparent reasoning** in all outputs

### 2.3 Success Definition

The MVP is successful if:
1. ✅ MAPE 12-18% on Spring 2025 hindcast
2. ✅ Variance Agent correctly identifies when to reforecast (not just threshold)
3. ✅ Bayesian reforecast improves accuracy vs original forecast
4. ✅ Guardrails catch 100% of unit conservation violations
5. ✅ User understands reasoning from displayed explanations
6. ✅ Workflow completes in <60 seconds

---

## 3. Target Users

### 3.1 Primary User: Merchandise Planner

**Profile:**
- **Role:** Forecasts demand and sets inventory targets
- **Technical Proficiency:** Medium (comfortable with dashboards, CSV uploads)
- **Goals:**
  - Fast decision-making (review in <2 minutes)
  - Transparent reasoning (understand WHY)
  - Reduce overstock and stockouts

**Pain Points Addressed:**
- "I don't trust the forecast because I don't understand how it was made"
- "By the time I see variance, it's too late to fix"
- "Manual allocation takes 5+ hours per week"

### 3.2 User Needs

| Need | v4.0 Solution |
|------|---------------|
| Understand forecast reasoning | Seasonality insights, reasoning traces |
| Know when to reforecast | Variance Agent explains decision |
| Trust allocation decisions | Key factors, store-specific insights |
| React to demand changes | Bayesian reforecast, strategic replenishment |

---

## 4. User Stories

### 4.1 Pre-Season Planning

#### Story 1.1: Generate Demand Forecast
**As a** Merchandise Planner
**I want to** generate a category-level demand forecast
**So that** I can plan manufacturing and allocation

**Acceptance Criteria:**
- [ ] Select category from dropdown (auto-detected from CSV)
- [ ] Set season parameters (start date, horizon weeks)
- [ ] Click "Generate Forecast" triggers Demand Agent
- [ ] Agent card shows real-time progress via status hooks
- [ ] Forecast result displays:
  - Total demand with confidence bounds
  - Weekly demand curve (Plotly chart)
  - **Seasonality insights**: peak/trough weeks, monthly effects
  - Prophet vs ARIMA breakdown
  - **Agent explanation** of forecast rationale

**Priority:** P0 (Blocker)

---

#### Story 1.2: Review Allocation Plan
**As a** Merchandise Planner
**I want to** review hierarchical store allocation
**So that** I can validate distribution matches business understanding

**Acceptance Criteria:**
- [ ] Allocation result displays:
  - Manufacturing quantity (forecast × safety stock)
  - DC holdback vs initial store allocation
  - 3 cluster cards (Fashion_Forward, Mainstream, Value_Conscious)
  - All 50 store allocations with percentages
- [ ] **Reasoning traces** show allocation logic:
  - "NYC-001 received 488 units (9.2%) due to 2.3x average velocity"
  - "Value_Conscious cluster reduced to 25% due to declining trend"
- [ ] **Key factors** highlight important decisions
- [ ] Guardrail validation confirms unit conservation

**Priority:** P0 (Blocker)

---

### 4.2 In-Season Monitoring

#### Story 2.1: Upload Weekly Actuals
**As a** Merchandise Planner
**I want to** upload actual sales data
**So that** the system can analyze variance and recommend actions

**Acceptance Criteria:**
- [ ] Upload CSV with weekly actual sales
- [ ] System validates format and store coverage
- [ ] Dashboard updates with actual vs forecast comparison
- [ ] Variance Agent automatically triggered

**Priority:** P0 (Blocker)

---

#### Story 2.2: Review Variance Analysis (Agentic)
**As a** Merchandise Planner
**I want to** understand variance analysis with reasoning
**So that** I can trust the reforecast decision

**Acceptance Criteria:**
- [ ] Variance Agent output displays:
  - Variance percentage and severity
  - **Trend direction** (increasing/decreasing/stable)
  - **Likely cause** (systematic underforecast, random noise, one-time event)
  - **Recommended action** with explanation
  - **should_reforecast** decision with reasoning
- [ ] Agent explains WHY it recommends reforecast (or not):
  - "22% variance with increasing trend suggests systematic underforecast. With 9 weeks remaining, reforecasting now allows meaningful correction."
  - "25% variance in Week 10 with only 2 weeks remaining - reforecast has minimal impact, recommend continuing with current forecast."

**Priority:** P0 (Blocker)

---

#### Story 2.3: Review Bayesian Reforecast
**As a** Merchandise Planner
**I want to** understand how the forecast was updated
**So that** I can trust the new predictions

**Acceptance Criteria:**
- [ ] Reforecast result displays:
  - Updated forecast by week
  - **Adjustment factor** (e.g., +17%)
  - **Prior vs likelihood weights** (e.g., 35% prior, 65% likelihood)
  - **Posterior confidence**
- [ ] Original forecast preserved for comparison
- [ ] Chart shows before/after forecast overlay
- [ ] **Agent explanation** of Bayesian update logic

**Priority:** P0 (Blocker)

---

#### Story 2.4: Review Reallocation Recommendations
**As a** Merchandise Planner
**I want to** see strategic replenishment recommendations
**So that** I can optimize inventory distribution

**Acceptance Criteria:**
- [ ] Reallocation analysis displays:
  - **High performers** (stores at stockout risk)
  - **Underperformers** (stores with excess inventory)
  - **On-target stores**
  - **Transfer orders** with from/to/units/reason
  - **Expected improvement** metrics
- [ ] Strategy recommendation (dc_only vs hybrid)
- [ ] **Agent explanation** of replenishment logic

**Priority:** P1 (High)

---

### 4.3 Mid-Season Pricing

#### Story 3.1: Review Markdown Recommendation
**As a** Merchandise Planner
**I want to** understand markdown calculation
**So that** I can make informed pricing decisions

**Acceptance Criteria:**
- [ ] Week 6 checkpoint automatically evaluates sell-through
- [ ] Markdown result displays:
  - Current vs target sell-through
  - Gap calculation
  - **Gap × Elasticity formula** breakdown
  - Recommended markdown percentage
  - **Guardrail validation** (40% cap, 5% rounding)
- [ ] **Agent explanation** of pricing rationale
- [ ] "Apply Markdown" button triggers update

**Priority:** P0 (Blocker)

---

### 4.4 Analytics & Monitoring

#### Story 4.1: Monitor Agent Status
**As a** Merchandise Planner
**I want to** see real-time agent status
**So that** I know what the system is doing

**Acceptance Criteria:**
- [ ] Sidebar displays:
  - Session ID and metadata
  - Current week tracker
  - **Agent status** (real-time via RunHooks)
  - Key metrics summary
- [ ] Status updates as agents execute:
  - "Running: Demand Forecasting Agent"
  - "Demand Agent: Calling run_demand_forecast"
  - "Completed: Demand Forecasting Agent"

**Priority:** P1 (High)

---

#### Story 4.2: View Performance Analytics
**As a** Merchandise Planner
**I want to** see forecast accuracy and business metrics
**So that** I can evaluate system performance

**Acceptance Criteria:**
- [ ] Analytics tab displays:
  - MAPE by week (Plotly chart)
  - Variance trend over time
  - Reforecast events timeline
  - Markdown impact analysis
- [ ] Metrics update as actuals are uploaded

**Priority:** P1 (High)

---

## 5. Functional Requirements

### 5.1 Agent Orchestration

**FR-1.1:** System shall execute agents using deterministic Python workflows via OpenAI Agents SDK `Runner.run()`.

**FR-1.2:** System shall enforce typed output via Pydantic `output_type` on all agents:
- Demand Agent: `ForecastResult`
- Inventory Agent: `AllocationResult`
- Pricing Agent: `MarkdownResult`
- Variance Agent: `VarianceAnalysis`
- Reforecast Agent: `ReforecastResult`
- Reallocation Agent: `ReallocationAnalysis`

**FR-1.3:** System shall pass shared context via `RunContextWrapper[ForecastingContext]` to all tools.

**FR-1.4:** System shall validate agent output using output guardrails before returning.

**FR-1.5:** System shall track agent status via `RunHooks` (on_agent_start, on_agent_end, on_tool_start).

---

### 5.2 Demand Forecasting

**FR-2.1:** Demand Agent shall generate category-level forecast using ensemble method:
- Train Prophet model on historical data
- Train ARIMA model on historical data
- Ensemble weighting based on validation MAPE

**FR-2.2:** Demand Agent shall extract seasonality insights:
- Peak weeks (highest demand)
- Trough weeks (lowest demand)
- Seasonal range (% variation)
- Monthly effects (multipliers)
- Insight text explaining patterns

**FR-2.3:** Demand Agent shall align seasonality to `season_start_date` for calendar events.

**FR-2.4:** Demand Agent shall produce confidence bounds (upper/lower) for forecast.

---

### 5.3 Inventory Allocation

**FR-3.1:** Inventory Agent shall cluster stores using K-means (K=3) on 7 features:
- avg_weekly_sales_12mo
- store_size_sqft
- median_income
- location_tier
- fashion_tier
- store_format
- region

**FR-3.2:** Inventory Agent shall allocate inventory hierarchically:
- Layer 1: Manufacturing qty = forecast × (1 + safety_stock_pct)
- Layer 2: DC holdback vs initial store allocation
- Layer 3: Store allocation = 70% historical + 30% attributes

**FR-3.3:** Inventory Agent shall include `reasoning_steps` and `key_factors` in output.

**FR-3.4:** Allocation guardrails shall validate unit conservation:
- dc_holdback + initial_store_allocation = manufacturing_qty
- sum(cluster_allocations) = initial_store_allocation
- sum(store_allocations) = initial_store_allocation

---

### 5.4 Variance Analysis (Agentic)

**FR-4.1:** Variance Agent shall analyze forecast accuracy with holistic reasoning:
- Calculate MAPE and directional variance
- Identify trend (increasing, decreasing, stable)
- Determine likely cause (systematic, random, one-time)
- Consider remaining weeks in season
- Decide `should_reforecast` with explanation

**FR-4.2:** Variance Agent shall NOT use simple threshold logic. Agent must reason about:
- Magnitude of variance
- Trend direction over recent weeks
- Business impact of not reforecasting
- Time remaining to correct

**FR-4.3:** Variance Agent output shall include:
- `variance_pct`: Calculated variance percentage
- `severity`: low/moderate/high/critical
- `likely_cause`: Agent's assessment of cause
- `trend_direction`: increasing/decreasing/stable
- `should_reforecast`: Boolean with reasoning
- `explanation`: Full reasoning text

---

### 5.5 Bayesian Reforecasting

**FR-5.1:** Reforecast Agent shall update forecast using Bayesian inference:
- Prior: Original forecast (mean, variance from historical MAPE)
- Likelihood: Observed actual sales (observed mean, std)
- Posterior: Weighted combination via conjugate Gaussian update

**FR-5.2:** Reforecast Agent shall calculate appropriate weights:
- Prior weight based on forecast confidence
- Likelihood weight based on observed data variance
- Total weights sum to 1.0

**FR-5.3:** Reforecast Agent output shall include:
- `updated_forecast_by_week`: New predictions
- `adjustment_factor`: Multiplier applied
- `prior_weight` and `likelihood_weight`: How data was combined
- `posterior_confidence`: Updated confidence

---

### 5.6 Strategic Replenishment

**FR-6.1:** Reallocation Agent shall analyze store performance:
- Calculate velocity per store (units/week)
- Calculate sell-through per store
- Identify stockout risk (high velocity, low inventory)
- Identify excess inventory (low velocity, high inventory)

**FR-6.2:** Reallocation Agent shall generate transfer recommendations:
- DC releases to high-performing stores
- Store-to-store transfers (hybrid strategy)
- Units and reason for each transfer

**FR-6.3:** Reallocation Agent output shall include:
- `should_reallocate`: Boolean
- `strategy`: dc_only or hybrid
- `high_performers`, `underperformers`, `on_target_stores`: Lists
- `transfers`: List of TransferOrder objects
- `expected_sell_through_improvement`: Projected impact

---

### 5.7 Pricing & Markdown

**FR-7.1:** Pricing Agent shall calculate markdown using Gap × Elasticity:
```python
gap = target_sell_through - current_sell_through
raw_markdown = gap × elasticity (default 2.0)
final_markdown = round_to_5%(raw_markdown), cap at 40%
```

**FR-7.2:** Pricing guardrails shall validate:
- Maximum 40% markdown (hard cap)
- Round to nearest 5%
- Valid input ranges

**FR-7.3:** Pricing Agent shall only activate at Week 6 checkpoint when sell_through < 60%.

---

### 5.8 User Interface (Streamlit)

**FR-8.1:** System shall provide Streamlit web interface with:
- Sidebar: Session info, agent status, key metrics
- Tab 1: Pre-Season Planning (forecast, allocation)
- Tab 2: In-Season Updates (variance, reforecast, reallocation)
- Tab 3: Pricing/Markdown
- Tab 4: Analytics

**FR-8.2:** System shall display real-time agent status via RunHooks.

**FR-8.3:** System shall render interactive Plotly charts for:
- Forecast with confidence bands
- Actual vs forecast comparison
- Variance trend over time
- Store allocation distribution

**FR-8.4:** System shall support CSV file upload for weekly actuals.

---

### 5.9 Guardrails & Validation

**FR-9.1:** System shall implement output guardrails for critical business rules:
- `validate_forecast_output`: Unit conservation, reasonableness
- `validate_allocation_output`: Unit conservation across all layers
- `validate_markdown_output`: 40% cap, 5% rounding

**FR-9.2:** Guardrails shall return `GuardrailResult` with:
- `output`: Validated/modified output
- `tripwire_triggered`: Boolean for critical violations
- `message`: Explanation of validation result

**FR-9.3:** Critical guardrail violations shall block workflow (tripwire).

**FR-9.4:** Soft guardrail warnings shall be logged but not block workflow.

---

## 6. Non-Functional Requirements

### 6.1 Performance

**NFR-1.1:** Full 6-agent workflow shall complete in <60 seconds.
- Demand Agent: <30 seconds
- Inventory Agent: <10 seconds
- Variance Agent: <5 seconds
- Reforecast Agent: <5 seconds
- Reallocation Agent: <5 seconds
- Pricing Agent: <5 seconds

**NFR-1.2:** System shall achieve MAPE 12-18% on hindcast testing.

**NFR-1.3:** Streamlit UI shall be responsive (<2 second page loads).

**NFR-1.4:** Agent status updates shall appear within 500ms of backend event.

---

### 6.2 Reliability

**NFR-2.1:** Guardrails shall catch 100% of unit conservation violations.

**NFR-2.2:** System shall handle OpenAI API failures gracefully with retry logic.

**NFR-2.3:** Session state shall persist across Streamlit reruns.

**NFR-2.4:** System shall log all agent executions for debugging.

---

### 6.3 Usability

**NFR-3.1:** User shall understand agent reasoning from displayed explanations.

**NFR-3.2:** All numeric outputs shall include units and context.

**NFR-3.3:** Error messages shall be actionable (what went wrong, how to fix).

**NFR-3.4:** Charts shall be interactive (hover tooltips, zoom).

---

### 6.4 Security

**NFR-4.1:** OpenAI API keys shall be stored in environment variables.

**NFR-4.2:** CSV uploads shall be validated for format and content.

**NFR-4.3:** No sensitive data shall be logged or displayed.

---

### 6.5 Maintainability

**NFR-5.1:** All agents shall have typed output via Pydantic schemas.

**NFR-5.2:** Tools shall be pure functions with no side effects.

**NFR-5.3:** Workflows shall be separate from agent definitions.

**NFR-5.4:** Code shall follow Python style guide (PEP 8).

---

## 7. Acceptance Criteria

### 7.1 Pre-Season Workflow

**AC-1:** Generate demand forecast
- [ ] Demand Agent executes successfully
- [ ] ForecastResult contains all required fields
- [ ] Seasonality insights explain peak/trough weeks
- [ ] Confidence bounds are reasonable

**AC-2:** Generate allocation plan
- [ ] Inventory Agent executes successfully
- [ ] AllocationResult passes unit conservation guardrails
- [ ] 50 stores receive allocations
- [ ] Reasoning traces explain key decisions

---

### 7.2 In-Season Workflow

**AC-3:** Upload and process weekly actuals
- [ ] CSV upload succeeds with validation
- [ ] Variance Agent automatically triggers
- [ ] VarianceAnalysis includes trend and cause

**AC-4:** Agentic variance decision
- [ ] Agent reasons about magnitude, trend, remaining weeks
- [ ] `should_reforecast` decision includes explanation
- [ ] Decision differs from simple 20% threshold in edge cases

**AC-5:** Bayesian reforecast (when triggered)
- [ ] Reforecast Agent executes
- [ ] Prior/likelihood weights are sensible
- [ ] Updated forecast shows improvement

**AC-6:** Strategic reallocation
- [ ] Reallocation Agent identifies high/low performers
- [ ] Transfer recommendations include reasoning
- [ ] Expected improvement is quantified

---

### 7.3 Pricing Workflow

**AC-7:** Week 6 markdown checkpoint
- [ ] Pricing Agent triggers when sell_through < 60%
- [ ] Gap × Elasticity calculation is correct
- [ ] Guardrails enforce 40% cap and 5% rounding

---

### 7.4 System Quality

**AC-8:** Guardrails validation
- [ ] Unit conservation violations are caught
- [ ] Tripwire blocks workflow on critical errors
- [ ] Soft warnings are logged

**AC-9:** Agent status tracking
- [ ] RunHooks fire for agent start/end
- [ ] Status updates appear in Streamlit sidebar
- [ ] Tool calls are tracked

---

## 8. Success Metrics

### 8.1 Forecast Accuracy

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE** | 12-18% | Category-level, weekly |
| **Bias** | ±5% | Systematic over/under |
| **Reforecast Improvement** | >10% | MAPE after vs before |

### 8.2 System Performance

| Metric | Target |
|--------|--------|
| **Workflow Runtime** | <60 seconds |
| **Guardrail Pass Rate** | 95%+ |
| **Agent Status Latency** | <500ms |

### 8.3 User Experience

| Metric | Target |
|--------|--------|
| **Reasoning Clarity** | 80%+ understand explanations |
| **Trust in Recommendations** | 80%+ trust agent decisions |
| **Task Completion** | <5 minutes per workflow |

---

## 9. System Features

### 9.1 Feature Priority Matrix

| Feature | Priority | Status |
|---------|----------|--------|
| **Deterministic Orchestration** | P0 | ✅ Implemented |
| **Typed Output (Pydantic)** | P0 | ✅ Implemented |
| **Demand Agent (Prophet + ARIMA)** | P0 | ✅ Implemented |
| **Inventory Agent (K-means + Allocation)** | P0 | ✅ Implemented |
| **Pricing Agent (Gap × Elasticity)** | P0 | ✅ Implemented |
| **Variance Agent (Agentic)** | P0 | ✅ Implemented |
| **Reforecast Agent (Bayesian)** | P0 | ✅ Implemented |
| **Reallocation Agent** | P1 | ✅ Implemented |
| **Guardrails Validation** | P0 | ✅ Implemented |
| **Agent Status Hooks** | P1 | ✅ Implemented |
| **Streamlit UI** | P0 | ✅ Implemented |
| **Seasonality Insights** | P1 | ✅ Implemented |
| **Reasoning Traces** | P1 | ✅ Implemented |
| **Sidebar Dashboard** | P1 | ✅ Implemented |

---

## 10. Data Requirements

### 10.1 Input Data

**Historical Sales** (`historical_sales_2022_2024.csv`):
- Records: ~164,400 (1,096 days × 50 stores × 3 categories)
- Columns: date, store_id, category, units_sold, revenue
- Date range: 2022-01-01 to 2024-12-31

**Store Attributes** (`store_attributes.csv`):
- Records: 50 stores
- Columns: store_id, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region, avg_weekly_sales_12mo

**Weekly Actuals** (in-season uploads):
- 12 files, one per week
- Columns: store_id, category, week, units_sold

### 10.2 Output Schemas

**ForecastResult:**
```python
class ForecastResult(BaseModel):
    total_demand: int
    forecast_by_week: List[int]
    safety_stock_pct: float
    confidence: float
    model_used: str
    seasonality: SeasonalityExplanation
    explanation: str
    lower_bound: List[int]
    upper_bound: List[int]
```

**AllocationResult:**
```python
class AllocationResult(BaseModel):
    manufacturing_qty: int
    dc_holdback: int
    dc_holdback_percentage: float
    initial_store_allocation: int
    cluster_allocations: List[ClusterAllocation]
    store_allocations: List[StoreAllocation]
    replenishment_strategy: str
    explanation: str
    reasoning_steps: List[str]
    key_factors: List[str]
```

**VarianceAnalysis:**
```python
class VarianceAnalysis(BaseModel):
    variance_pct: float
    is_high_variance: bool
    severity: str
    likely_cause: str
    trend_direction: str
    recommended_action: str
    should_reforecast: bool
    reforecast_adjustments: Optional[str]
    confidence: float
    explanation: str
```

**ReforecastResult:**
```python
class ReforecastResult(BaseModel):
    updated_forecast_by_week: List[int]
    updated_total: int
    adjustment_factor: float
    posterior_confidence: float
    prior_weight: float
    likelihood_weight: float
    explanation: str
```

**ReallocationAnalysis:**
```python
class ReallocationAnalysis(BaseModel):
    should_reallocate: bool
    strategy: str
    dc_units_available: int
    dc_units_to_release: int
    high_performers: List[str]
    underperformers: List[str]
    on_target_stores: List[str]
    transfers: List[TransferOrder]
    expected_sell_through_improvement: float
    stockout_risk_reduction: int
    confidence: float
    explanation: str
```

**MarkdownResult:**
```python
class MarkdownResult(BaseModel):
    recommended_markdown_pct: float
    current_sell_through: float
    target_sell_through: float
    gap: float
    elasticity_used: float
    raw_markdown_pct: float
    week_number: int
    explanation: str
```

---

## 11. Technical Constraints

### 11.1 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Agent Framework** | OpenAI Agents SDK | 0.2+ |
| **LLM** | GPT-4o-mini | - |
| **Frontend** | Streamlit | 1.28+ |
| **Visualization** | Plotly | 5.18+ |
| **Forecasting** | Prophet, statsmodels | 1.1+, 0.14+ |
| **ML** | scikit-learn | 1.3+ |
| **Validation** | Pydantic | 2.0+ |
| **Data** | Pandas, NumPy | 2.0+, 1.24+ |

### 11.2 Performance Constraints

- Full workflow: <60 seconds
- Individual agents: <30 seconds max
- UI responsiveness: <2 seconds

### 11.3 Data Constraints

- Store count: 50 (fixed)
- Forecast horizon: 12 weeks (fixed)
- Clusters: 3 (K-means K=3)

---

## 12. Assumptions & Dependencies

### 12.1 Assumptions

1. Historical data has 2+ years of clean category-level sales
2. Store attributes are accurate and current
3. K-means (K=3) produces meaningful clusters
4. Users understand basic retail terminology
5. Weekly actuals uploaded consistently

### 12.2 Dependencies

1. **OpenAI API**: Availability and rate limits
2. **Prophet/ARIMA**: Model convergence on retail data
3. **Streamlit**: UI framework stability
4. **Training Data**: Quality and completeness

---

## 13. Out of Scope

### 13.1 Not Included in MVP

- ❌ SKU-level forecasting
- ❌ Multi-category parallel forecasting
- ❌ External data integration (weather, social)
- ❌ Production deployment (local dev only)
- ❌ Multi-user authentication
- ❌ Mobile support

### 13.2 Post-MVP Roadmap

**Phase 2:**
- Multi-category support
- External data integration
- Parameter optimization UI

**Phase 3:**
- Production deployment
- API exposure
- Fine-tuned models

---

## 14. Release Plan

### 14.1 Current Status (v4.0)

| Component | Status |
|-----------|--------|
| Demand Agent | ✅ Complete |
| Inventory Agent | ✅ Complete |
| Pricing Agent | ✅ Complete |
| Variance Agent | ✅ Complete |
| Reforecast Agent | ✅ Complete |
| Reallocation Agent | ✅ Complete |
| Guardrails | ✅ Complete |
| Streamlit UI | ✅ Complete |
| Agent Status Hooks | ✅ Complete |
| Seasonality Insights | ✅ Complete |

### 14.2 Validation Tasks

- [ ] Hindcast testing on Spring 2025 data
- [ ] MAPE validation (target 12-18%)
- [ ] Guardrails stress testing
- [ ] User experience testing

---

## 15. Appendix

### 15.1 Glossary

| Term | Definition |
|------|------------|
| **Agentic Reasoning** | LLM-powered decision-making that considers context |
| **Bayesian Reforecast** | Updating forecast using prior + likelihood → posterior |
| **Deterministic Orchestration** | Python code controls workflow, agents handle reasoning |
| **Guardrails** | Validation rules on structured output |
| **Output Schema** | Pydantic model defining agent output structure |
| **RunContextWrapper** | Dependency injection for tools |
| **Variance Analysis** | Assessment of forecast accuracy with trend and cause |

### 15.2 Related Documents

- [Product Brief v4.0](1_product_brief_v4.0.md)
- [Process Workflow v4.0](2_process_workflow_v4.0.md)
- [Architecture v4.0](architecture-v4.0.md)
- [Data Specification v3.2](6_data_specification_v3.2.md)

---

## Summary of Changes from v3.3

### Major Changes

| Aspect | v3.3 | v4.0 |
|--------|------|------|
| **Agents** | 3 | 6 |
| **Orchestration** | Agent-as-tool | Deterministic Python |
| **Output Types** | Strings | Pydantic schemas |
| **Variance Handling** | Threshold | Agentic reasoning |
| **Reforecast** | Re-run | Bayesian update |
| **Replenishment** | Fixed cadence | Strategic analysis |
| **Frontend** | React | Streamlit |
| **Validation** | String parsing | Guardrails on typed data |

### New Features

1. **Variance Agent** with agentic reasoning
2. **Reforecast Agent** with Bayesian inference
3. **Reallocation Agent** for strategic replenishment
4. **Guardrails** for business rule validation
5. **Seasonality insights** in forecast output
6. **Reasoning traces** and key factors
7. **Agent status hooks** for real-time updates

### Removed

1. Agent-as-tool handoff pattern
2. String-based output parsing
3. Simple variance threshold
4. React frontend
5. Parameter extraction from natural language

---

**Document Owner:** Independent Study Project
**Last Updated:** 2025-12-04
**Version:** 4.0
**Status:** Active Implementation

---

*Document generated by BMad Master v4.0*
