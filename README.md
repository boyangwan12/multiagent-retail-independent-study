# Agentic Retail Forecasting System

**AI-Powered Demand Forecasting & Inventory Optimization with Multi-Agent Orchestration**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-green.svg)](https://github.com/openai/openai-agents-python)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Overview

This project demonstrates the application of **agentic AI systems** in retail demand forecasting and inventory management. Built on the **OpenAI Agents SDK**, it combines deterministic Python workflow orchestration with LLM-powered reasoning agents to provide intelligent, self-correcting forecasting and allocation decisions.

**Independent Study Project** — McGill University, Desautels Faculty of Management

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Deterministic Orchestration** | Python controls agent execution flow |
| **Typed Data Flow** | Pydantic schemas enforce structured outputs |
| **Agentic Variance Analysis** | LLM reasons about causes, not just thresholds |
| **Bayesian Reforecasting** | Updates predictions with actual sales data |
| **K-Means Store Clustering** | Groups stores by 7 attributes |
| **3-Layer Inventory Allocation** | DC → Cluster → Store distribution |
| **Strategic Replenishment** | AI-driven transfer recommendations |
| **Markdown Optimization** | Gap × Elasticity pricing formula |

---

## Architecture

### High-Level System Architecture

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

### Three-Layer Execution Model

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

---

## The 6 Agents

| Agent | Purpose | Key Tools | Output |
|-------|---------|-----------|--------|
| **🎯 Demand Agent** | Prophet + ARIMA ensemble forecasting with seasonality detection | `run_demand_forecast` | `ForecastResult` |
| **📦 Inventory Agent** | K-means clustering and 3-layer hierarchical allocation | `cluster_stores`, `allocate_inventory` | `AllocationResult` |
| **💰 Pricing Agent** | Markdown optimization using Gap × Elasticity formula | `calculate_markdown` | `MarkdownResult` |
| **📊 Variance Agent** | Intelligent reasoning about forecast vs actual deviations | `analyze_variance_data` | `VarianceAnalysis` |
| **🔄 Reforecast Agent** | Bayesian posterior updates with actual sales data | `bayesian_reforecast` | `ReforecastResult` |
| **🚚 Reallocation Agent** | Strategic replenishment and store transfer planning | `analyze_performance`, `generate_transfers` | `ReallocationAnalysis` |

---

## Tech Stack

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

## Project Structure

> Navigate to each folder, you will find a separate README file helping you navigate folders and files.

---

## Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/boyangwan12/multiagent-retail-independent-study.git
cd multiagent-retail-independent-study

# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Application

```bash
cd backend
streamlit run streamlit_app.py
```

The application will open at `http://localhost:8501`

---

## Example Workflow

### Women's Dresses - Spring Season

1. **Pre-Season Planning**
   - Demand Agent analyzes 3 years of historical data
   - Predicts 15,000 units for 12-week spring season
   - Inventory Agent clusters 50 stores into 3 performance tiers
   - Allocates inventory with 45% DC holdback

2. **Week 3: Variance Detection**
   - Actual sales 25% above forecast
   - Variance Agent *reasons* that warm weather arrived early
   - Recommends reforecasting (not a one-time spike)
   - Reforecast Agent adjusts remaining weeks using Bayesian updates

3. **Week 8: Strategic Replenishment**
   - High-performing stores running low on inventory
   - Reallocation Agent identifies underperforming locations
   - Recommends transferring 500 units to prevent stockouts

4. **Week 10: Markdown Optimization**
   - Sell-through at 62% vs 70% target
   - Pricing Agent calculates 15% markdown
   - Gap × Elasticity formula with 40% cap protection

---

## Key Architectural Decisions

### Why Deterministic Orchestration?

| Concern | Agent-as-Tool (v3.3) | Deterministic + Agentic (v4.0) |
|---------|----------------------|-------------------------------|
| Control Flow | String pattern matching | Python `if/while` statements |
| Type Safety | None (strings) | Pydantic schemas enforced by SDK |
| Debugging | Hard (LLM black box) | Clear (Python + structured output) |
| Guardrails | String parsing | Validation on typed data |
| Variance Decision | `if variance > 0.20` | Agent reasons holistically |

### OpenAI Agents SDK Features Used

- **`Agent`** with `output_type` for typed outputs
- **`@function_tool`** for pure computation functions
- **`Runner.run()`** for async agent execution
- **`RunContextWrapper`** for dependency injection
- **`output_guardrails`** for business rule validation
- **`RunHooks`** for real-time UI status updates

---

## Resources

*Coming soon — documentation, presentation slides, and project report.*

---

## Team

| Name | LinkedIn |
|------|----------|
| **Boyang Wan** | [linkedin.com/in/boyang-wan-2000](https://www.linkedin.com/in/boyang-wan-2000/) |
| **Henry Tang** | [linkedin.com/in/heng-tang-683090251](https://www.linkedin.com/in/heng-tang-683090251/) |
| **Yi Juan (Yina) Liang Li** | [linkedin.com/in/yi-juan-yina-liang-li](https://www.linkedin.com/in/yi-juan-yina-liang-li/) |
| **JaeYoon Lee** | [linkedin.com/in/jaeyoon-lee-277655308](https://www.linkedin.com/in/jaeyoon-lee-277655308/) |
| **Jintao Li** | [linkedin.com/in/jintao-li](https://www.linkedin.com/in/jintao-li/) |

---

## Acknowledgments

**Instructor**: [Fatih Nayebi](https://www.linkedin.com/in/thefatih/)

**Special Thanks**: [Arnav Gupta](https://www.linkedin.com/in/arnavgupta97/)

