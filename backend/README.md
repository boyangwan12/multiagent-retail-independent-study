This README helps you navigate the backend folder.

# Backend - Agentic Retail Forecasting System

6-agent retail forecasting system built with **OpenAI Agents SDK** and **Streamlit**.

**Version**: v4.0
**Last Updated**: 2025-12-04

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the application
streamlit run streamlit_app.py
```

---

## Folder Structure

```
backend/
├── streamlit_app.py          # Main Streamlit UI (entry point)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your local environment (not committed)
│
├── my_agents/                # Agent definitions (OpenAI Agents SDK)
│   ├── demand_agent.py       # Demand forecasting agent
│   ├── inventory_agent.py    # Inventory allocation agent
│   ├── pricing_agent.py      # Markdown pricing agent
│   ├── variance_agent.py     # Variance analysis agent
│   ├── reforecast_agent.py   # Bayesian reforecast agent
│   └── reallocation_agent.py # Inter-store transfer agent
│
├── agent_tools/              # Tools available to agents
│   ├── demand_tools.py       # Prophet + ARIMA forecasting
│   ├── inventory_tools.py    # K-means clustering, allocation
│   ├── pricing_tools.py      # Markdown calculation
│   ├── variance_tools.py     # Variance checking
│   ├── reallocation_tools.py # Transfer optimization
│   └── bayesian_reforecast.py # Bayesian forecast updates
│
├── schemas/                  # Pydantic output schemas
│   ├── forecast_schemas.py   # ForecastResult, WeeklyForecast
│   ├── allocation_schemas.py # AllocationResult, StoreAllocation
│   ├── pricing_schemas.py    # MarkdownResult
│   ├── variance_schemas.py   # VarianceResult
│   ├── reallocation_schemas.py # ReallocationAnalysis, TransferOrder
│   └── workflow_schemas.py   # WorkflowParams, SeasonResult
│
├── guardrails/               # Output validation guardrails
│   ├── allocation_guardrails.py  # Unit conservation validation
│   ├── forecast_guardrails.py    # Forecast reasonableness
│   └── pricing_guardrails.py     # Markdown cap enforcement
│
├── workflows/                # Workflow orchestration
│   ├── season_workflow.py    # Main entry point (full season)
│   ├── forecast_workflow.py  # Forecast + variance loop
│   ├── allocation_workflow.py # Inventory allocation
│   ├── pricing_workflow.py   # Markdown decisions
│   └── reallocation_workflow.py # Inter-store transfers
│
├── utils/                    # Utilities
│   ├── context.py            # ForecastingContext (RunContextWrapper)
│   ├── data_loader.py        # CSV data loading
│   ├── agent_status_hooks.py # Agent execution hooks
│   └── sidebar_status.py     # Streamlit sidebar rendering
│
└── config/                   # Configuration
    └── settings.py           # Environment variables, defaults
```

---

## Architecture

### 6-Agent System

| Agent | File | Purpose | Output Schema |
|-------|------|---------|---------------|
| **Demand** | `demand_agent.py` | Prophet + ARIMA ensemble forecasting | `ForecastResult` |
| **Inventory** | `inventory_agent.py` | K-means clustering, store allocation | `AllocationResult` |
| **Pricing** | `pricing_agent.py` | Markdown recommendations | `MarkdownResult` |
| **Variance** | `variance_agent.py` | Analyze forecast vs actuals | `VarianceAnalysis` |
| **Reforecast** | `reforecast_agent.py` | Bayesian forecast updates | `ForecastResult` |
| **Reallocation** | `reallocation_agent.py` | Inter-store transfers | `ReallocationAnalysis` |

### Key Design Patterns

**1. Deterministic Workflow Orchestration**
- Python controls WHEN agents run
- Agents control HOW they reason
- Workflows in `workflows/` orchestrate agent execution

**2. Typed Outputs (Pydantic)**
```python
demand_agent = Agent(
    name="Demand Agent",
    output_type=ForecastResult,  # Enforced by SDK
)
result = await Runner.run(demand_agent, input, context=context)
forecast: ForecastResult = result.final_output  # Typed!
```

**3. Output Guardrails**
```python
@output_guardrail
async def validate_allocation_output(ctx, agent, output: AllocationResult):
    if not output.validate_unit_conservation():
        return GuardrailFunctionOutput(tripwire_triggered=True)
    return GuardrailFunctionOutput(tripwire_triggered=False)
```

**4. RunContextWrapper (Dependency Injection)**
```python
@dataclass
class ForecastingContext:
    data_loader: TrainingDataLoader
    session_id: str
    # NOT sent to LLM - just available to tools

result = await Runner.run(agent, input, context=context)
```

---

## Workflows

### Pre-Season Workflow
```
User Input → Demand Agent → Inventory Agent → Display Results
                  ↓               ↓
            ForecastResult   AllocationResult
```

### In-Season Workflow
```
Upload Actuals → Variance Agent → [Significant?]
                      ↓                ↓
                 VarianceAnalysis    No → Display
                      ↓
                    Yes → Reforecast Agent → Reallocation Agent
                               ↓                    ↓
                          ForecastResult    ReallocationAnalysis
                               ↓
                         [Weeks Remaining < 4?]
                               ↓
                            Yes → Pricing Agent → MarkdownResult
```

---

## Schemas

### ForecastResult
```python
class ForecastResult(BaseModel):
    total_forecast: int           # Total units for season
    weekly_forecasts: List[WeeklyForecast]
    confidence_score: float       # 0.0 - 1.0
    seasonality: SeasonalityExplanation
    model_used: str              # "prophet_ets_ensemble"
```

### AllocationResult
```python
class AllocationResult(BaseModel):
    total_units_allocated: int
    store_allocations: List[StoreAllocation]
    cluster_summary: Dict[str, ClusterSummary]
    dc_holdback_units: int
    reasoning: str
```

### VarianceAnalysis
```python
class VarianceAnalysis(BaseModel):
    variance_pct: float
    is_significant: bool
    should_reforecast: bool
    reasoning: str
    trend_direction: str         # "improving" | "stable" | "declining"
```

---

## Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (with defaults)
OPENAI_MODEL=gpt-4o-mini
MAX_REFORECASTS=2
VARIANCE_THRESHOLD=0.20
DEFAULT_ELASTICITY=2.0
MAX_MARKDOWN_PCT=0.40
DEFAULT_DC_HOLDBACK_PCT=0.45
DEFAULT_SAFETY_STOCK_PCT=0.20
```

---

## Dependencies

Key packages from `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| `openai-agents` | >=0.2.0 | OpenAI Agents SDK |
| `streamlit` | >=1.28.0 | Web UI |
| `plotly` | >=5.18.0 | Interactive charts |
| `prophet` | >=1.1.0 | Seasonality forecasting |
| `statsmodels` | >=0.14.0 | ARIMA models |
| `scikit-learn` | >=1.3.0 | K-means clustering |
| `pydantic` | >=2.0.0 | Output schemas |
| `pandas` | >=2.0.0 | Data processing |

---

## Legacy Folders (Can Be Deleted)

These folders are from previous architecture iterations:

| Folder | Description | Status |
|--------|-------------|--------|
| `app/` | Old FastAPI structure | Empty, deprecated |
| `data/` | Old upload storage | Empty, deprecated |

---

## Related Documentation

- `docs/04_MVP_Development/planning/3_technical_architecture_v4.0.md` - Full architecture
- `docs/04_MVP_Development/planning/2_process_workflow_v4.0.md` - Operational workflow
- `docs/04_MVP_Development/planning/5_front-end-spec_v4.0.md` - Streamlit UI spec
- `data/README.md` - Data folder documentation

---

**Document Version**: v4.0
**Last Updated**: 2025-12-04
