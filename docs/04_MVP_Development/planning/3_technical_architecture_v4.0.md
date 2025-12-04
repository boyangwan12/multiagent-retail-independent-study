# Architecture Document v4.0
## Agentic Retail Forecasting System

**Version**: 4.0
**Date**: December 4, 2025
**Status**: Active Development (SDK Branch)

---

## 1. Executive Summary

This document describes the architecture of an agentic retail demand forecasting and inventory management system built on the OpenAI Agents SDK. The system combines deterministic Python workflow orchestration with LLM-powered reasoning agents to provide intelligent, self-correcting forecasting and allocation decisions.

### Key Architectural Principles

1. **Deterministic Orchestration**: Python controls WHEN agents run; agents control HOW they reason
2. **Typed Data Flow**: Pydantic schemas enforce structured output at every layer
3. **Guardrails Validation**: Critical business rules validated on structured data, not strings
4. **Agentic Reasoning**: LLMs reason about variance, causes, and recommendations holistically
5. **Tool Separation**: Pure computation functions isolated from LLM reasoning

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│                    Streamlit UI (streamlit_app.py)               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐  │
│  │   Sidebar    │ │  Main Tabs   │ │    Plotly Charts         │  │
│  │  Dashboard   │ │  (Planning,  │ │  (Forecast, Variance,    │  │
│  │  + Metrics   │ │  In-Season)  │ │   Allocation)            │  │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                           │
│                  Python Workflow Controllers                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│  │ season_workflow │ │forecast_workflow│ │allocation_wrkflw│     │
│  │  (12-week loop) │ │ (demand+var.)   │ │  (clustering)   │     │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘     │
│  ┌─────────────────┐ ┌─────────────────┐                         │
│  │ pricing_workflow│ │realloc_workflow │                         │
│  │  (markdown)     │ │ (replenishment) │                         │
│  └─────────────────┘ └─────────────────┘                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT LAYER                                │
│              OpenAI Agents SDK (LLM Reasoning)                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  │  Demand    │ │ Inventory  │ │  Pricing   │ │  Variance  │    │
│  │   Agent    │ │   Agent    │ │   Agent    │ │   Agent    │    │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │
│  ┌────────────┐ ┌────────────┐                                   │
│  │ Reforecast │ │Reallocation│                                   │
│  │   Agent    │ │   Agent    │                                   │
│  └────────────┘ └────────────┘                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       TOOLS LAYER                                │
│              Pure Computation (No LLM Calls)                     │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐       │
│  │  demand_tools  │ │inventory_tools │ │ pricing_tools  │       │
│  │ (Prophet+ARIMA)│ │ (K-means,alloc)│ │(Gap×Elasticity)│       │
│  └────────────────┘ └────────────────┘ └────────────────┘       │
│  ┌────────────────┐ ┌────────────────┐                          │
│  │variance_tools  │ │realloc_tools   │                          │
│  │(MAPE, Bayesian)│ │(performance)   │                          │
│  └────────────────┘ └────────────────┘                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌────────────────────────┐ ┌────────────────────────────────┐  │
│  │   ForecastingContext   │ │      TrainingDataLoader        │  │
│  │   (Shared State)       │ │   (Historical Sales, Stores)   │  │
│  └────────────────────────┘ └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit 1.28+ | Interactive web UI |
| **Visualization** | Plotly 5.18+ | Charts and graphs |
| **Agent Framework** | OpenAI Agents SDK 0.2+ | Agent orchestration |
| **LLM** | GPT-4o-mini | Reasoning and generation |
| **Forecasting** | Prophet 1.1+, statsmodels | Time series models |
| **ML** | scikit-learn 1.3+ | K-means clustering |
| **Validation** | Pydantic 2.0+ | Schema enforcement |
| **Data** | Pandas 2.0+, NumPy | Data manipulation |

---

## 3. Core Architectural Patterns

### 3.1 Deterministic Workflow Orchestration

The system uses Python-controlled workflow orchestration rather than agent-to-agent handoffs. This pattern emerged from v2.0 pivot after discovering fragility in agent-as-tool chaining.

```python
# WORKFLOW LAYER - Python controls flow (deterministic)
async def run_forecast_with_variance_loop(context):
    # Step 1: Generate forecast
    forecast = await Runner.run(demand_agent, input=..., context=context)

    # Step 2: Python decides if variance check needed
    if context.actual_sales:
        # Step 3: Agent reasons about variance
        variance = await Runner.run(variance_agent, input=..., context=context)

        # Step 4: Python acts on agent's decision
        if variance.final_output.should_reforecast:
            reforecast = await Runner.run(reforecast_agent, ...)
            forecast = update_with_reforecast(forecast, reforecast)

    return forecast
```

**Benefits**:
- Clear control flow visible in code
- Typed data passing between agents
- No fragile string pattern matching
- Testable workflow logic

### 3.2 Structured Output with Pydantic

Every agent declares its `output_type` as a Pydantic model:

```python
demand_agent = Agent(
    name="Demand Forecasting Agent",
    output_type=ForecastResult,  # Enforced by SDK
    output_guardrails=[validate_forecast_output],
    tools=[run_demand_forecast],
)
```

The SDK ensures `result.final_output` is always a typed `ForecastResult`, not a string.

### 3.3 RunContextWrapper for Dependency Injection

Tools access shared state without passing it through the LLM:

```python
@function_tool
def run_demand_forecast(
    ctx: RunContextWrapper[ForecastingContext],
    category: str,
    forecast_horizon_weeks: int
) -> ForecastToolResult:
    # Access via context - LLM never sees raw data
    historical = ctx.context.data_loader.get_sales(category)
    return forecaster.predict(historical, forecast_horizon_weeks)
```

### 3.4 Guardrails Validation

Output guardrails validate structured Pydantic models:

```python
@output_guardrail
async def validate_allocation_output(
    ctx: RunContextWrapper[ForecastingContext],
    result: AllocationResult
) -> GuardrailResult:
    # Validate unit conservation
    store_sum = sum(s.units for s in result.store_allocations)
    if store_sum != result.initial_store_allocation:
        return GuardrailResult(
            output=result,
            tripwire_triggered=True,
            message=f"Unit conservation violated: {store_sum} != {result.initial_store_allocation}"
        )
    return GuardrailResult(output=result)
```

---

## 4. Agent Specifications

### 4.1 Agent Overview

| Agent | Input | Output Schema | Key Tools | Purpose |
|-------|-------|---------------|-----------|---------|
| Demand Agent | Category, horizon, season_start | `ForecastResult` | `run_demand_forecast` | Prophet+ARIMA ensemble forecasting with seasonality |
| Inventory Agent | Forecast, DC%, safety% | `AllocationResult` | `cluster_stores`, `allocate_inventory` | K-means clustering + 3-layer allocation |
| Pricing Agent | Sell-through, target | `MarkdownResult` | `calculate_markdown` | Gap × Elasticity markdown optimization |
| Variance Agent | Forecast, actuals | `VarianceAnalysis` | `analyze_variance_data` | Intelligent variance reasoning |
| Reforecast Agent | Actuals, prior forecast | `ReforecastResult` | `bayesian_reforecast` | Bayesian posterior estimation |
| Reallocation Agent | Store performance | `ReallocationAnalysis` | `analyze_performance`, `generate_transfers` | Strategic replenishment |

### 4.2 Demand Agent

**Purpose**: Generate demand forecasts using ensemble modeling with calendar-aligned seasonality.

**Output Schema** (`ForecastResult`):
```python
class ForecastResult(BaseModel):
    total_demand: int
    forecast_by_week: List[int]
    safety_stock_pct: float
    confidence: float  # 0.0-1.0
    model_used: str
    seasonality: SeasonalityExplanation  # Peak/trough weeks, insights
    explanation: str
    lower_bound: List[int]
    upper_bound: List[int]
```

**Tool**: `run_demand_forecast`
- Trains Prophet + ARIMA on historical data
- Ensemble weighting based on validation MAPE
- Extracts seasonality insights (peak weeks, monthly effects)
- Aligns to `season_start_date` for calendar events

### 4.3 Inventory Agent

**Purpose**: Cluster stores and allocate inventory hierarchically.

**Output Schema** (`AllocationResult`):
```python
class AllocationResult(BaseModel):
    manufacturing_qty: int
    dc_holdback: int
    dc_holdback_percentage: float
    initial_store_allocation: int
    cluster_allocations: List[ClusterAllocation]
    store_allocations: List[StoreAllocation]  # All 50 stores
    replenishment_strategy: str
    explanation: str
    reasoning_steps: List[str]  # Agentic trace
    key_factors: List[str]  # Specific insights
```

**Tools**:
1. `cluster_stores`: K-means on 7 attributes (size, income, traffic, etc.)
2. `allocate_inventory`: 3-layer hierarchical allocation
   - Layer 1: Manufacturing qty = forecast × (1 + safety_stock_pct)
   - Layer 2: DC holdback vs initial store allocation
   - Layer 3: Store allocation = 70% sales history + 30% attributes

**Guardrails**:
- Unit conservation at all levels (critical)
- Cluster balance warnings (soft)

### 4.4 Variance Agent

**Purpose**: Reason holistically about forecast variance and decide if reforecasting is needed.

**Output Schema** (`VarianceAnalysis`):
```python
class VarianceAnalysis(BaseModel):
    variance_pct: float
    is_high_variance: bool
    severity: str  # low, moderate, high, critical
    likely_cause: str
    trend_direction: str  # increasing, decreasing, stable
    recommended_action: str
    should_reforecast: bool  # Agent's decision
    reforecast_adjustments: Optional[str]
    confidence: float
    explanation: str
```

**Key Design Decision**: The agent decides `should_reforecast` based on reasoning, not a simple threshold. The agent considers:
- Variance magnitude
- Trend direction over recent weeks
- Remaining weeks in season
- Likely cause (one-time vs systematic)
- Business impact

### 4.5 Pricing Agent

**Purpose**: Calculate markdown recommendations when sell-through is below target.

**Output Schema** (`MarkdownResult`):
```python
class MarkdownResult(BaseModel):
    recommended_markdown_pct: float  # 0.0-0.40
    current_sell_through: float
    target_sell_through: float
    gap: float
    elasticity_used: float
    raw_markdown_pct: float
    week_number: int
    explanation: str
```

**Tool**: `calculate_markdown`
- Formula: `raw = gap × elasticity`
- Rounding: Nearest 5%
- Cap: Maximum 40%

### 4.6 Reallocation Agent

**Purpose**: Analyze store performance and recommend strategic replenishment.

**Output Schema** (`ReallocationAnalysis`):
```python
class ReallocationAnalysis(BaseModel):
    should_reallocate: bool
    strategy: str  # dc_only, hybrid
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

---

## 5. Workflow Specifications

### 5.1 Season Workflow (Main Entry Point)

`workflows/season_workflow.py::run_full_season()`

**12-Week Season Flow**:

```
Week 0 (Pre-Season Planning):
├── Run Demand Agent → ForecastResult
├── Run Variance Agent (if historical data) → VarianceAnalysis
│   └── If should_reforecast: Run Reforecast Agent
├── Run Inventory Agent → AllocationResult
└── Store results in context

Weeks 1-5 (Early Season):
├── Load actual sales (user upload)
├── Run Variance Agent → VarianceAnalysis
│   └── If should_reforecast: Run Reforecast Agent
├── Check replenishment cadence
│   └── If triggered: Run Reallocation Agent
└── Update context with actuals

Week 6 (Markdown Checkpoint):
├── Calculate sell_through = total_sold / total_allocated
├── If sell_through < 0.60:
│   └── Run Pricing Agent → MarkdownResult
└── Continue monitoring

Weeks 7-12 (Late Season):
├── Continue variance monitoring
├── Reallocation as needed
└── Final reporting
```

### 5.2 Forecast Workflow

**Two Modes**:

1. **`run_forecast()`**: Pre-season only, no variance loop
2. **`run_forecast_with_variance_loop()`**: In-season with agentic variance analysis

```python
async def run_forecast_with_variance_loop(context):
    # Initial forecast
    forecast = await Runner.run(demand_agent, ...)

    # Variance analysis (agentic)
    if context.actual_sales:
        variance = await Runner.run(variance_agent, ...)

        if variance.final_output.should_reforecast:
            reforecast = await Runner.run(reforecast_agent, ...)
            forecast = merge_reforecast(forecast, reforecast)

    return forecast
```

### 5.3 Allocation Workflow

```python
async def run_allocation(context, forecast_result):
    input_data = AllocationInput(
        total_forecast=forecast_result.total_demand,
        forecast_by_week=forecast_result.forecast_by_week,
        dc_holdback_pct=context.dc_holdback_pct,
        safety_stock_pct=forecast_result.safety_stock_pct,
    )

    result = await Runner.run(
        inventory_agent,
        input=json.dumps(input_data.model_dump()),
        context=context,
    )

    # Guardrails automatically validated
    return result.final_output  # AllocationResult
```

### 5.4 Pricing Workflow

```python
async def run_markdown_if_needed(context, current_week):
    if current_week < 6:
        return None  # Too early

    sell_through = context.total_sold / context.total_allocated

    if sell_through >= context.markdown_threshold:
        return None  # On track

    result = await Runner.run(
        pricing_agent,
        input=json.dumps({
            "current_sell_through": sell_through,
            "target_sell_through": context.target_sell_through,
            "week_number": current_week,
        }),
        context=context,
    )

    return result.final_output  # MarkdownResult
```

---

## 6. Data Architecture

### 6.1 ForecastingContext (Shared State)

```python
@dataclass
class ForecastingContext:
    # Core dependencies
    data_loader: TrainingDataLoader
    session_id: str

    # Season configuration
    season_start_date: Optional[date]
    current_week: int = 0

    # Forecast state
    forecast_by_week: List[int] = field(default_factory=list)
    original_forecast: Optional[ForecastResult] = None

    # Variance tracking
    actual_sales: Optional[List[int]] = None
    variance_history: List[VarianceAnalysis] = field(default_factory=list)

    # Allocation state
    manufacturing_qty: int = 0
    dc_holdback: int = 0
    allocation_result: Optional[AllocationResult] = None

    # Pricing state
    total_allocated: int = 0
    total_sold: int = 0

    # Store-level tracking
    store_actual_sales: Dict[str, List[int]] = field(default_factory=dict)
```

### 6.2 Data Files

| File | Records | Purpose |
|------|---------|---------|
| `historical_sales_2022_2024.csv` | 164,400 | 3 years × 50 stores × 3 categories |
| `store_attributes.csv` | 50 | Clustering features (size, income, traffic, etc.) |
| `scenarios/*/week_*.csv` | 12/scenario | Test scenario actual sales |

### 6.3 Data Flow

```
User Input (Category, Horizon)
        │
        ▼
┌─────────────────────────────┐
│    TrainingDataLoader       │
│  - Load historical sales    │
│  - Load store attributes    │
│  - Cache in memory          │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│   ForecastingContext        │
│  - Shared across agents     │
│  - Updated by workflows     │
│  - Session-scoped           │
└─────────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌─────────┐       ┌─────────┐
│  Agent  │ ───▶  │  Tool   │
│  (LLM)  │       │ (Comp.) │
└─────────┘       └─────────┘
    │                   │
    └─────────┬─────────┘
              ▼
┌─────────────────────────────┐
│   Pydantic Output Schema    │
│  - Validated by SDK         │
│  - Checked by guardrails    │
└─────────────────────────────┘
```

---

## 7. Frontend Architecture

### 7.1 Streamlit Application Structure

**File**: `backend/streamlit_app.py` (~170KB)

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│                        Header                                │
│                "Agentic Retail Forecasting"                  │
├─────────────┬───────────────────────────────────────────────┤
│   Sidebar   │                Main Content                    │
│             │                                                │
│ ┌─────────┐ │  ┌─────────────────────────────────────────┐  │
│ │ Session │ │  │  Tab 1: Pre-Season Planning             │  │
│ │ Info    │ │  │  - Category/horizon selection           │  │
│ └─────────┘ │  │  - Forecast generation                  │  │
│             │  │  - Allocation display                   │  │
│ ┌─────────┐ │  └─────────────────────────────────────────┘  │
│ │ Agent   │ │                                                │
│ │ Status  │ │  ┌─────────────────────────────────────────┐  │
│ │ Hooks   │ │  │  Tab 2: In-Season Updates               │  │
│ └─────────┘ │  │  - Actual sales upload                  │  │
│             │  │  - Variance analysis                    │  │
│ ┌─────────┐ │  │  - Reforecast display                   │  │
│ │ Key     │ │  └─────────────────────────────────────────┘  │
│ │ Metrics │ │                                                │
│ └─────────┘ │  ┌─────────────────────────────────────────┐  │
│             │  │  Tab 3: Pricing/Markdown                │  │
│             │  │  - Markdown recommendations             │  │
│             │  └─────────────────────────────────────────┘  │
│             │                                                │
│             │  ┌─────────────────────────────────────────┐  │
│             │  │  Tab 4: Analytics                       │  │
│             │  │  - Plotly charts                        │  │
│             │  │  - Store allocation tables              │  │
│             │  └─────────────────────────────────────────┘  │
└─────────────┴───────────────────────────────────────────────┘
```

### 7.2 State Management

```python
# Session state keys
st.session_state.session_id        # UUID for session
st.session_state.context           # ForecastingContext
st.session_state.forecast_result   # Current ForecastResult
st.session_state.original_forecast # Pre-reforecast baseline
st.session_state.allocation_result # AllocationResult
st.session_state.variance_history  # List[VarianceAnalysis]
st.session_state.agent_status      # Real-time agent updates
```

### 7.3 Agent Status Hooks

```python
class AgentStatusHooks(RunHooks):
    def on_agent_start(self, agent, input_data):
        st.session_state.agent_status = f"Running: {agent.name}"

    def on_agent_end(self, agent, output):
        st.session_state.agent_status = f"Completed: {agent.name}"

    def on_tool_start(self, agent, tool):
        st.session_state.agent_status = f"{agent.name}: Calling {tool.name}"
```

---

## 8. Configuration

### 8.1 Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o-mini

# Workflow Settings
MAX_REFORECASTS=2
VARIANCE_THRESHOLD=0.20

# Pricing
DEFAULT_ELASTICITY=2.0
MAX_MARKDOWN_PCT=0.40
MARKDOWN_ROUNDING=0.05

# Inventory
DEFAULT_DC_HOLDBACK_PCT=0.45
DEFAULT_SAFETY_STOCK_PCT=0.20
```

### 8.2 Settings Module

`config/settings.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    max_reforecasts: int = 2
    variance_threshold: float = 0.20
    default_elasticity: float = 2.0
    max_markdown_pct: float = 0.40
    # ...

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 9. Testing Architecture

### 9.1 Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Unit Tests | `tests/unit/` | Individual tool functions |
| Integration Tests | `tests/integration/` | Agent + tool combinations |
| Workflow Tests | `tests/workflows/` | End-to-end workflow validation |
| Guardrail Tests | `tests/guardrails/` | Validation logic |

### 9.2 Test Data Scenarios

| Scenario | Path | Characteristics |
|----------|------|-----------------|
| Normal | `data/scenarios/normal_season/` | Expected Spring 2025, Week 5 +30% spike |
| High Demand | `data/scenarios/high_demand/` | +25% overall, Week 5 +40% |
| Low Demand | `data/scenarios/low_demand/` | -20% overall, Week 5 -25% |

---

## 10. Architectural Evolution

### 10.1 Version History

| Version | Key Changes |
|---------|-------------|
| **v1.0** | Initial agent-as-tool pattern with string outputs |
| **v2.0** | Pivot to deterministic workflow orchestration |
| **v3.0** | Agentic variance analysis (agent decides, not threshold) |
| **v3.1** | Seasonality insights and reasoning traces |
| **v3.2** | Sidebar dashboard and agent status hooks |
| **v4.0** | Current - unified architecture with full explainability |

### 10.2 Key Pivots Explained

**v1.0 → v2.0 (Agent-as-Tool → Workflows)**

*Problem*: Agent-as-tool chaining used string pattern matching for control flow. Fragile, hard to debug, no type safety.

*Solution*: Python workflows control when agents run. Agents return typed Pydantic models. Guardrails validate structured data.

**v2.0 → v3.0 (Threshold → Agentic Variance)**

*Problem*: `if variance > 0.20: reforecast()` misses context. A 25% variance in Week 1 differs from Week 11.

*Solution*: Variance Agent reasons holistically about magnitude, trend, remaining season, and likely cause. Agent sets `should_reforecast` boolean.

**v3.0 → v4.0 (Unified Explainability)**

*Problem*: Users need to understand WHY forecasts and allocations were made.

*Solution*: Added `reasoning_steps`, `key_factors`, `seasonality` insights to output schemas. Sidebar dashboard shows real-time agent status.

---

## 11. Deployment

### 11.1 Development

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create .env
echo "OPENAI_API_KEY=your-key" > .env

# Run
streamlit run streamlit_app.py
```

### 11.2 Production Considerations

- **Rate Limiting**: Implement backoff for OpenAI API calls
- **Caching**: Cache forecasts and cluster results per session
- **Logging**: Structured logging for all agent calls
- **Monitoring**: Track MAPE, guardrail triggers, reforecast frequency

---

## 12. Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **Data Isolation**: Each session has unique ID; no cross-session data leakage
3. **Input Validation**: Pydantic validates all user inputs
4. **Output Validation**: Guardrails check business rule compliance
5. **No PII**: Training data uses synthetic store IDs

---

## 13. Future Considerations

1. **Multi-tenant Support**: Session isolation for multiple concurrent users
2. **Model Fine-tuning**: Domain-specific fine-tuned models for retail
3. **Real-time Integration**: Connect to actual POS/inventory systems
4. **Advanced Scenarios**: Promotion planning, new store modeling
5. **Feedback Loop**: Learn from actual vs predicted over time

---

## Appendix A: Directory Structure

```
independent_study_agentic/
├── backend/
│   ├── streamlit_app.py          # Main UI
│   ├── requirements.txt
│   ├── config/
│   │   └── settings.py
│   ├── schemas/
│   │   ├── forecast_schemas.py
│   │   ├── allocation_schemas.py
│   │   ├── pricing_schemas.py
│   │   ├── variance_schemas.py
│   │   ├── reallocation_schemas.py
│   │   └── workflow_schemas.py
│   ├── my_agents/
│   │   ├── demand_agent.py
│   │   ├── inventory_agent.py
│   │   ├── pricing_agent.py
│   │   ├── variance_agent.py
│   │   ├── reforecast_agent.py
│   │   └── reallocation_agent.py
│   ├── agent_tools/
│   │   ├── demand_tools.py
│   │   ├── inventory_tools.py
│   │   ├── pricing_tools.py
│   │   ├── variance_tools.py
│   │   ├── bayesian_reforecast.py
│   │   └── reallocation_tools.py
│   ├── guardrails/
│   │   ├── forecast_guardrails.py
│   │   ├── allocation_guardrails.py
│   │   └── pricing_guardrails.py
│   ├── workflows/
│   │   ├── season_workflow.py
│   │   ├── forecast_workflow.py
│   │   ├── allocation_workflow.py
│   │   ├── pricing_workflow.py
│   │   └── reallocation_workflow.py
│   └── utils/
│       ├── context.py
│       ├── data_loader.py
│       ├── agent_status_hooks.py
│       └── sidebar_status.py
├── data/
│   ├── training/
│   │   ├── historical_sales_2022_2024.csv
│   │   └── store_attributes.csv
│   └── scenarios/
│       ├── normal_season/
│       ├── high_demand/
│       └── low_demand/
├── docs/
│   └── planning/
│       └── architecture-v4.0.md   # This document
└── tests/
    ├── unit/
    ├── integration/
    ├── workflows/
    └── guardrails/
```

---

## Appendix B: Schema Reference

See `backend/schemas/` for complete Pydantic model definitions.

---

*Document generated by BMad Master v4.0*
