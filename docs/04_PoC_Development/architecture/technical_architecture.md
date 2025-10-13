# Technical Architecture - Retail Demand Forecasting & Allocation System

**Version:** 1.0
**Last Updated:** 2025-10-12
**Status:** Architecture Complete - Ready for Implementation
**Source Documents:** Product Brief v3.1, Operational Workflow v3

---

## Table of Contents

1. [Introduction](#introduction)
2. [Starter Template Decision](#starter-template-decision)
3. [High Level Architecture](#high-level-architecture)
4. [Tech Stack](#tech-stack)
5. [Data Models](#data-models)
6. [Components](#components)
7. [External APIs](#external-apis)
8. [Core Workflows](#core-workflows)
9. [ML Approach](#ml-approach)
10. [Agent Handoff Flow](#agent-handoff-flow)
11. [REST API Specification](#rest-api-specification)
12. [Frontend Flow](#frontend-flow)
13. [Database Schema](#database-schema)
14. [Source Tree Structure](#source-tree-structure)
15. [Infrastructure & Deployment](#infrastructure--deployment)
16. [Error Handling Strategy](#error-handling-strategy)
17. [Coding Standards](#coding-standards)
18. [Test Strategy](#test-strategy)
19. [Security](#security)
20. [Validation Checklist](#validation-checklist)

---

## 1. Introduction

### Purpose

This document defines the technical architecture for a **multi-agent demand forecasting and inventory allocation system** for fashion retail. The system uses OpenAI Agents SDK to orchestrate three specialized agents that collaborate to forecast demand, allocate inventory, and recommend pricing strategies for a 12-week fashion season.

### System Overview

**Business Problem:** Fashion retailers struggle with accurate demand forecasting at granular SKU-store-week levels, leading to overstock (markdowns) and stockouts (lost sales).

**Solution:** Category-level hierarchical forecasting approach:
- **Forecast once** at category level (e.g., "Women's Dresses: 8,000 units over 12 weeks")
- **Allocate with math** using store clustering and historical patterns
- **Adapt dynamically** via variance monitoring and automated re-forecasting

**Key Innovation:**
- Reduces forecast complexity from 600+ granular forecasts (50 stores × 12 weeks) to 1 category forecast
- Uses AI agents for reasoning about allocation, replenishment, and markdown strategies
- Human-in-the-loop for critical decisions (manufacturing orders, markdowns)

### Scope (MVP - Archetype 1)

**In Scope:**
- Single category: Women's Dresses
- 50 stores across 3 clusters (Fashion_Forward, Mainstream, Value_Conscious)
- 12-week season (Spring 2025)
- Mock dataset (CSV uploads)
- Local development environment

**Out of Scope (Post-MVP):**
- Multi-category forecasting
- New stores without historical data
- Production deployment (cloud infrastructure)
- Multi-user authentication
- Real-time POS data integration

---

## 2. Starter Template Decision

### Framework: OpenAI Agents SDK + UV Package Manager

**Decision:** Use OpenAI Agents SDK (v0.3.3+) with UV package manager for Python backend.

**Rationale:**
1. **OpenAI Agents SDK** (production-ready successor to Swarm)
   - Built-in multi-agent orchestration with handoffs
   - Responses API integration (not deprecated Chat Completions)
   - Session management, guardrails, tracing
   - Designed for production agentic workflows

2. **UV Package Manager**
   - 10-100x faster than pip/poetry
   - Built-in virtual environment management
   - Compatible with pyproject.toml
   - Recommended by OpenAI for agent development

3. **Monorepo Structure**
   - Single repository for backend + frontend
   - Easier atomic commits, faster iteration for solo development
   - Academic MVP focus (no need for microservices complexity)

**Alternatives Considered:**
- ❌ LangGraph: More complex, steeper learning curve
- ❌ AutoGen: Less mature, fewer production features
- ❌ Separate repos: Overkill for MVP, slower development

---

## 3. High Level Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │ Agent Flow   │  │ Approval     │      │
│  │              │  │ Visualizer   │  │ Modals       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │ │ │
                    REST API │ │ WebSocket
                            ▼ ▼ ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Agents SDK)             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Orchestrator Agent                      │  │
│  │  - Workflow coordination                             │  │
│  │  - Variance monitoring (>20% triggers re-forecast)   │  │
│  │  - Context-rich handoffs                             │  │
│  │  - Dynamic handoff enabling                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                     │           │           │               │
│                     ▼           ▼           ▼               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Demand    │ │  Inventory  │ │      Pricing        │   │
│  │   Agent     │ │   Agent     │ │      Agent          │   │
│  │             │ │             │ │                     │   │
│  │ - Prophet   │ │ - Mfg calc  │ │ - Markdown formula  │   │
│  │ - ARIMA     │ │ - Allocation│ │ - Variance monitor  │   │
│  │ - K-means   │ │ - Replenish │ │ - Week 6 checkpoint │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           ML Pipeline (Prophet/ARIMA/K-means)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │ │ │
                            ▼ ▼ ▼
┌─────────────────────────────────────────────────────────────┐
│             SQLite Database (Hybrid Schema)                 │
│  - Normalized entities (stores, clusters, categories)       │
│  - JSON arrays (weekly_curve, store_allocations)            │
└─────────────────────────────────────────────────────────────┘
                            │ │ │
                            ▼ ▼ ▼
┌─────────────────────────────────────────────────────────────┐
│                 Azure OpenAI Service                        │
│                    (gpt-4o-mini)                            │
└─────────────────────────────────────────────────────────────┘
```

### Architectural Patterns

**1. Multi-Agent Orchestration**
- Central Orchestrator coordinates 3 specialized agents
- Sequential workflow with context-rich handoffs
- Dynamic handoff enabling based on runtime conditions (variance triggers)

**2. Hierarchical Forecasting**
- Category-level forecast (single prediction: 8,000 units)
- Cluster-level allocation (K-means: 3 clusters)
- Store-level distribution (70% historical + 30% attributes)

**3. Event-Driven Re-Forecasting**
- Orchestrator monitors weekly variance (actual vs forecast)
- Variance >20% → auto-triggers re-forecast workflow
- Demand Agent receives context (actuals, variance reason) and recalculates

**4. Human-in-the-Loop**
- Critical decisions require approval (manufacturing orders, markdowns)
- WebSocket real-time updates show agent reasoning
- User can Modify (agent re-runs with new params) or Accept

---

## 4. Tech Stack

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Backend runtime |
| **Package Manager** | UV | 0.5+ | Dependency management (10-100x faster than pip) |
| **Web Framework** | FastAPI | 0.115+ | REST API + WebSocket server |
| **Agent Framework** | OpenAI Agents SDK | 0.3.3+ | Multi-agent orchestration, handoffs, sessions |
| **LLM** | Azure OpenAI (gpt-4o-mini) | 2024-10-21 API | Agent reasoning (via Responses API) |
| **Time-Series Forecasting** | Prophet | 1.1+ | Meta's forecasting library |
| **Time-Series Forecasting** | pmdarima (auto-arima) | 2.0+ | ARIMA modeling |
| **Clustering** | scikit-learn | 1.5+ | K-means store clustering |
| **Data Validation** | Pydantic | 2.10+ | Runtime data validation |
| **Type Checking** | mypy | 1.13+ | Static type checking |
| **Linting/Formatting** | Ruff | 0.7+ | Fast Python linter + formatter |
| **Database** | SQLite | 3.45+ | Local file-based database |
| **Data Processing** | Pandas + NumPy | Latest | Data manipulation |

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | TypeScript | 5.6+ | Type-safe JavaScript |
| **Framework** | React | 18.3+ | UI library |
| **Build Tool** | Vite | 5.4+ | Fast dev server + bundler |
| **UI Components** | Shadcn/ui | Latest | Accessible component library |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS |
| **State Management** | TanStack Query | 5.59+ | Server state + API calls |
| **Data Tables** | TanStack Table | 8.20+ | Headless table component |
| **Charts** | Recharts | 2.12+ | React charting library |
| **Routing** | React Router | 6.27+ | Client-side routing |
| **Forms** | React Hook Form | 7.53+ | Form state management |
| **Linting** | ESLint | 9.13+ | JavaScript linter |
| **Formatting** | Prettier | 3.3+ | Code formatter |
| **Testing** | Vitest + React Testing Library | Latest | Component testing |
| **E2E Testing** | Playwright | 1.48+ | End-to-end testing |

### Development Tools

| Tool | Purpose |
|------|---------|
| **uv** | Python package management |
| **npm** | Frontend package management |
| **Git** | Version control |
| **VS Code** | IDE (recommended) |

---

## 5. Data Models

### Core Pydantic Models

#### Category Model
```python
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

class RetailArchetype(str, Enum):
    FASHION_RETAIL = "FASHION_RETAIL"
    STABLE_CATALOG = "STABLE_CATALOG"
    CONTINUOUS = "CONTINUOUS"

class Category(BaseModel):
    category_id: str = Field(..., description="Unique category identifier")
    category_name: str = Field(..., description="Display name (e.g., 'Women's Dresses')")
    season_start_date: date = Field(..., description="Season start (e.g., 2025-03-01)")
    season_end_date: date = Field(..., description="Season end (e.g., 2025-05-23)")
    season_length_weeks: int = Field(..., description="Duration in weeks (e.g., 12)")
    archetype: RetailArchetype = Field(..., description="Retail archetype")
    description: str | None = Field(None, description="Optional category description")
```

#### Store Model
```python
class LocationTier(str, Enum):
    A = "A"  # Prime location
    B = "B"  # Standard location
    C = "C"  # Secondary location

class StoreFormat(str, Enum):
    MALL = "MALL"
    STANDALONE = "STANDALONE"
    SHOPPING_CENTER = "SHOPPING_CENTER"
    OUTLET = "OUTLET"

class Region(str, Enum):
    NORTHEAST = "NORTHEAST"
    SOUTHEAST = "SOUTHEAST"
    MIDWEST = "MIDWEST"
    WEST = "WEST"

class Store(BaseModel):
    store_id: str = Field(..., description="Unique store identifier (e.g., 'S01')")
    store_name: str = Field(..., description="Store name")
    cluster_id: str = Field(..., description="FK to store_clusters")
    store_size_sqft: int = Field(..., description="Store size in sq ft")
    location_tier: LocationTier = Field(..., description="A/B/C tier")
    median_income: int = Field(..., description="Area median income ($)")
    store_format: StoreFormat = Field(..., description="Store format type")
    region: Region = Field(..., description="Geographic region")
    avg_weekly_sales_12mo: float = Field(..., description="Historical sales performance")
```

#### StoreCluster Model
```python
class FashionTier(str, Enum):
    PREMIUM = "PREMIUM"
    MAINSTREAM = "MAINSTREAM"
    VALUE = "VALUE"

class StoreCluster(BaseModel):
    cluster_id: str = Field(..., description="Unique cluster ID (e.g., 'fashion_forward')")
    cluster_name: str = Field(..., description="Display name")
    fashion_tier: FashionTier = Field(..., description="Fashion positioning")
    allocation_percentage: float = Field(..., description="% of category demand (e.g., 0.40)")
    description: str | None = Field(None, description="Cluster characteristics")
```

#### Forecast Model
```python
class WeeklyDemand(BaseModel):
    week_number: int = Field(..., ge=1, le=12, description="Week 1-12")
    demand_units: int = Field(..., ge=0, description="Forecasted units")

class ClusterDistribution(BaseModel):
    cluster_id: str
    cluster_name: str
    allocation_percentage: float = Field(..., ge=0, le=1)
    total_units: int = Field(..., ge=0)

class Forecast(BaseModel):
    forecast_id: str = Field(..., description="Unique forecast ID")
    category_id: str = Field(..., description="FK to categories")
    season: str = Field(..., description="Season identifier (e.g., 'Spring 2025')")
    forecast_horizon_weeks: int = Field(..., description="Number of weeks (e.g., 12)")
    total_season_demand: int = Field(..., ge=0, description="Total units for season")
    weekly_demand_curve: list[WeeklyDemand] = Field(..., description="Week-by-week demand")
    peak_week: int = Field(..., ge=1, description="Week with highest demand")
    cluster_distribution: list[ClusterDistribution] = Field(..., description="Cluster allocations")
    forecasting_method: str = Field(default="ensemble_prophet_arima", description="Method used")
    models_used: list[str] = Field(default=["prophet", "arima"], description="Models in ensemble")
    prophet_forecast: int | None = Field(None, description="Prophet result (for analysis)")
    arima_forecast: int | None = Field(None, description="ARIMA result (for analysis)")
    created_at: datetime = Field(default_factory=datetime.now)
```

#### Allocation Model
```python
class StoreAllocation(BaseModel):
    store_id: str
    store_name: str
    cluster_id: str
    initial_allocation: int = Field(..., ge=0, description="55% initial allocation")
    holdback_allocation: int = Field(..., ge=0, description="45% DC holdback")
    total_season_allocation: int = Field(..., ge=0)

class AllocationPlan(BaseModel):
    allocation_id: str
    forecast_id: str = Field(..., description="FK to forecasts")
    manufacturing_qty: int = Field(..., ge=0, description="Total to manufacture (with safety stock)")
    safety_stock_percentage: float = Field(default=0.20, description="Fixed 20% safety stock")
    initial_allocation_total: int = Field(..., description="Total 55% to stores")
    holdback_total: int = Field(..., description="Total 45% at DC")
    store_allocations: list[StoreAllocation] = Field(..., description="Store-level detail")
    created_at: datetime = Field(default_factory=datetime.now)
```

---

## 6. Components

### Component Overview

| Component | Type | Responsibility |
|-----------|------|---------------|
| **Orchestrator** | Agent | Workflow coordination, variance monitoring, dynamic handoff control |
| **Demand Agent** | Agent | Forecasting (Prophet+ARIMA), clustering (K-means), allocation factors |
| **Inventory Agent** | Agent | Manufacturing calculation, store allocation, replenishment planning |
| **Pricing Agent** | Agent | Markdown recommendations, sell-through tracking, Week 6 checkpoint |

### Orchestrator Agent

**Role:** Central coordinator that manages the 3-agent workflow and monitors system health.

**Responsibilities:**
- Trigger pre-season forecast workflow (Week -12)
- Monitor weekly variance (actual vs forecast)
- Enable dynamic re-forecast handoff when variance >20%
- Coordinate human-in-the-loop approvals
- Log all agent interactions to `workflow_logs` table

**Key Features:**
- **Context-Rich Handoffs:** Passes forecast/allocation objects directly between agents (no database queries)
- **Dynamic Handoff Enabling:** Re-forecast handoff only enabled when variance exceeds threshold
- **Session Management:** Maintains conversation history automatically via SDK Sessions

**Handoffs:**
```python
orchestrator = Agent(
    name="Orchestrator",
    instructions="""
    You coordinate the demand forecasting workflow.

    1. Start with Demand Agent for category forecast
    2. Hand off forecast context to Inventory Agent
    3. Hand off allocation context to Pricing Agent
    4. Monitor variance weekly - if >20%, enable re-forecast handoff
    """,
    handoffs=[
        demand_agent,
        inventory_agent,
        pricing_agent,
        handoff(demand_agent, name="reforecast", enabled=False)  # Dynamically enabled
    ]
)
```

### Demand Agent

**Role:** Forecasting specialist that predicts category demand and calculates store allocation factors.

**Responsibilities:**
1. **Time-Series Forecasting:**
   - Run Prophet model on historical sales
   - Run ARIMA model on historical sales
   - Ensemble: Average Prophet + ARIMA results
   - Output: Total season demand (e.g., 8,000 units)

2. **Store Clustering:**
   - K-means clustering (K=3) using 7 features
   - Label clusters as Fashion_Forward, Mainstream, Value_Conscious
   - Calculate cluster allocation percentages

3. **Store Allocation Factors:**
   - 70% weight: Historical sales performance
   - 30% weight: Store attributes (size, demographics, tier)

**Tools:**
- `forecast_category_demand()` - Prophet + ARIMA ensemble
- `cluster_stores()` - K-means clustering
- `calculate_allocation_factors()` - Store-level distribution

**Output:** Forecast object (total_demand, weekly_curve, cluster_distribution)

### Inventory Agent

**Role:** Inventory planning specialist that calculates manufacturing orders and store allocations.

**Responsibilities:**
1. **Manufacturing Calculation:**
   - Formula: `manufacturing_qty = total_demand × (1 + safety_stock_pct)`
   - Safety stock: Fixed 20%
   - Example: 8,000 × 1.20 = 9,600 units

2. **Initial Allocation:**
   - 55% to stores, 45% holdback at DC
   - Minimum: 2-week forecast per store (prevent early stockouts)
   - Distribute across stores using Demand Agent's allocation factors

3. **Replenishment Planning:**
   - Formula: `replenish = next_week_forecast - current_inventory`
   - Simple formula (no adaptive adjustments)
   - If variance >20%, Orchestrator triggers re-forecast instead

**Tools:**
- `calculate_manufacturing()` - Safety stock calculation
- `allocate_to_stores()` - Initial 55/45 split with 2-week minimum
- `plan_replenishment()` - Weekly replenishment calculation

**Output:** Allocation object (manufacturing_qty, store_allocations, holdback)

### Pricing Agent

**Role:** Pricing strategist that recommends markdowns and monitors sell-through performance.

**Responsibilities:**
1. **Week 6 Markdown Checkpoint:**
   - Target: 60% sell-through by Week 6
   - Formula: `markdown = (target - actual_sell_through) × elasticity`
   - Elasticity coefficient: 2.0 (tunable parameter)
   - Max markdown: 40%, round to 5% increments

2. **Markdown Calculation Examples:**
   - 58% sell-through → 2% gap → 2% × 2.0 = 4% → rounds to 5% markdown
   - 50% sell-through → 10% gap → 10% × 2.0 = 20% markdown
   - 40% sell-through → 20% gap → 20% × 2.0 = 40% markdown (capped)

3. **Post-Markdown Monitoring:**
   - After markdown applied, Orchestrator monitors variance
   - If variance still >20% → triggers re-forecast (not additional markdown)
   - Avoids over-markdowning, lets Demand Agent recalculate with new data

4. **Markdown Strategy:**
   - Uniform across all clusters (same % for all stores)
   - No cluster-specific adjustments for MVP

**Tools:**
- `calculate_markdown()` - Gap × elasticity formula
- `evaluate_sellthrough()` - Week 6 checkpoint analysis

**Output:** Markdown recommendation (percentage, reasoning, expected impact)

---

## 7. External APIs

### Azure OpenAI Service

**Endpoint:** `https://<your-resource>.openai.azure.com/`
**API Version:** `2024-10-21`
**Model Deployment:** `gpt-4o-mini`

**Authentication:**
```python
from openai import AzureOpenAI
import os

azure_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
```

**Agent Configuration:**
```python
from openai_agents import Agent

demand_agent = Agent(
    name="Demand Agent",
    model=azure_client,
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # gpt-4o-mini
    instructions="You are a demand forecasting specialist...",
    tools=[forecast_category_demand, cluster_stores]
)
```

**Rate Limits:**
- Tokens per minute (TPM): Check Azure resource quota
- Requests per minute (RPM): Check Azure resource quota
- Handle rate limit errors: Fail fast (no retry for MVP)

**Cost Optimization:**
- Use gpt-4o-mini (cheapest model)
- Target <$5 total for MVP testing
- Estimated: ~10-20 API calls per workflow × $0.0001/call = $0.002/workflow

**Integration Notes:**
- All LLM calls go through Azure (not OpenAI direct)
- Credentials stored in `.env` file (gitignored)
- No frontend exposure of API keys (server-side only)

---

## 8. Core Workflows

### Workflow 1: Pre-Season Forecast Generation (Week -12)

**Trigger:** User clicks "Generate Forecast" in UI

**Sequence:**
```
User (Frontend)
    ↓ POST /api/workflows/forecast
Orchestrator
    ↓ (hands off with context)
Demand Agent
    ├─ Load historical_sales (2-3 years)
    ├─ Run Prophet → 8,200 units
    ├─ Run ARIMA → 7,800 units
    ├─ Ensemble average → 8,000 units
    ├─ Cluster stores (K-means, K=3)
    ├─ Calculate cluster distribution
    └─ Return forecast object
    ↓ (hands off forecast object via context)
Inventory Agent
    ├─ Receive forecast: {total_demand: 8000, clusters: [...]}
    ├─ Calculate manufacturing: 8000 × 1.20 = 9,600 units
    ├─ Initial allocation: 9,600 × 0.55 = 5,280 units (to stores)
    ├─ Holdback: 9,600 × 0.45 = 4,320 units (at DC)
    ├─ Distribute to 50 stores (2-week minimum per store)
    └─ Return allocation object
    ↓ (hands off allocation object)
Pricing Agent
    ├─ Receive allocation plan
    ├─ Schedule Week 6 checkpoint
    └─ Return pricing strategy
    ↓
Orchestrator
    ├─ Aggregate all results
    ├─ Save to database (forecasts, allocations tables)
    └─ Return to user via WebSocket
```

**Human-in-the-Loop Approval:**
```
Inventory Agent completes allocation
    ↓
WebSocket sends: {"type": "human_input_required", "action": "approve_manufacturing"}
    ↓
Frontend shows modal:
    "Manufacturing Order: 9,600 units
     Initial Allocation: 5,280 units (55%)
     Holdback: 4,320 units (45%)

     [Modify] [Accept]"
    ↓
If user clicks "Modify":
    ├─ User adjusts parameters (e.g., change safety stock to 15%)
    ├─ Agent re-runs calculation with new params
    ├─ Returns updated allocation
    └─ User approves revised plan

If user clicks "Accept":
    └─ Workflow continues to Pricing Agent
```

### Workflow 2: In-Season Variance Monitoring & Re-Forecast (Week 4 Example)

**Trigger:** User uploads Week 4 actual sales CSV

**Sequence:**
```
User uploads weekly_sales.csv (Week 4)
    ↓ POST /api/data/upload-weekly-sales
Backend saves to actual_sales table
    ↓
Orchestrator monitors variance
    ├─ Query: SUM(actual_sales) WHERE week <= 4
    ├─ Actual Week 1-4: 3,200 units
    ├─ Forecast Week 1-4: 2,550 units
    ├─ Variance: |3200 - 2550| / 2550 = 25.5% ⚠️
    └─ Threshold exceeded (>20%)
    ↓
Orchestrator enables dynamic handoff
    orchestrator.enable_handoff("reforecast")
    ↓
Orchestrator hands off to Demand Agent with context
    {
        "reason": "variance_exceeds_20_percent",
        "variance": 0.255,
        "actual_week_1_to_4": 3200,
        "forecasted_week_1_to_4": 2550,
        "remaining_weeks": 8
    }
    ↓
Demand Agent (Re-Forecast)
    ├─ Load original historical data + Week 1-4 actuals
    ├─ Re-run Prophet with updated data → 10,200 units
    ├─ Re-run ARIMA with updated data → 9,800 units
    ├─ New ensemble: (10200 + 9800) / 2 = 10,000 units
    ├─ Recalculate weekly curve for remaining 8 weeks
    └─ Return revised forecast object
    ↓
Inventory Agent (Re-Allocation)
    ├─ Original manufacturing: 9,600 units
    ├─ Already allocated to stores: 5,280 units (Week 1-4)
    ├─ Holdback available: 4,320 units
    ├─ New total demand: 10,000 units
    ├─ Still needed: 10,000 - 3,200 (sold) = 6,800 units
    ├─ Shortage: 6,800 - 4,320 (holdback) = 2,480 units
    └─ Recommendation: "Place emergency order for 2,480 units"
    ↓
Orchestrator
    ├─ Log re-forecast event
    ├─ Save revised forecast/allocation
    └─ Notify user via WebSocket
```

### Workflow 3: Week 6 Markdown Checkpoint

**Trigger:** Week 6 arrives (scheduled)

**Sequence:**
```
Week 6 Start
    ↓
Orchestrator triggers Pricing Agent
    ↓
Pricing Agent
    ├─ Query actual_sales: SUM(units_sold) WHERE week <= 6
    ├─ Actual Week 1-6: 4,000 units
    ├─ Forecast total: 8,000 units
    ├─ Sell-through: 4000 / 8000 = 50%
    ├─ Target: 60% by Week 6
    ├─ Gap: 60% - 50% = 10%
    ├─ Markdown formula: gap × elasticity = 10% × 2.0 = 20%
    ├─ Round to 5%: 20% markdown
    └─ Return markdown recommendation
    ↓
WebSocket sends: {"type": "human_input_required", "action": "approve_markdown"}
    ↓
Frontend shows modal:
    "Week 6 Checkpoint - Markdown Recommendation

     Current sell-through: 50% (target: 60%)
     Gap: 10 percentage points

     Recommended markdown: 20%
     Expected demand lift: 30% (20% × 1.5 elasticity)

     Reasoning: 10% gap × 2.0 elasticity = 20% markdown

     [Modify] [Accept]"
    ↓
If user clicks "Modify":
    ├─ User adjusts elasticity coefficient (e.g., 1.8 instead of 2.0)
    ├─ Agent recalculates: 10% × 1.8 = 18% → rounds to 20%
    └─ User approves

If user clicks "Accept":
    ├─ Apply 20% markdown to all stores (uniform across clusters)
    ├─ Log markdown event
    ├─ Orchestrator monitors variance in Week 7-8
    └─ If variance still >20% → trigger re-forecast (not additional markdown)
```

---

## 9. ML Approach

### Demand Agent - Detailed ML Approach

#### 1. Time-Series Forecasting (Ensemble)

**Approach:** Run Prophet + ARIMA in parallel, average results (no confidence scoring).

**Prophet Configuration:**
```python
from prophet import Prophet
import pandas as pd

def run_prophet_forecast(historical_sales: pd.DataFrame, weeks: int = 12) -> int:
    """
    Forecast category demand using Prophet.

    Args:
        historical_sales: DataFrame with columns ['ds', 'y'] (date, units_sold)
        weeks: Forecast horizon (default 12 for Archetype 1)

    Returns:
        Total forecasted units for season
    """
    # Prepare data (Prophet expects 'ds' and 'y' columns)
    df = historical_sales[['week_start_date', 'units_sold']].rename(
        columns={'week_start_date': 'ds', 'units_sold': 'y'}
    )

    # Configure Prophet
    model = Prophet(
        seasonality_mode='multiplicative',  # Fashion retail has multiplicative seasonality
        yearly_seasonality=True,
        weekly_seasonality=False,  # Category-level, not daily
        daily_seasonality=False
    )

    # Fit model
    model.fit(df)

    # Generate future dataframe (12 weeks)
    future = model.make_future_dataframe(periods=weeks, freq='W')

    # Predict
    forecast = model.predict(future)

    # Extract last 12 weeks (forecast period)
    forecast_period = forecast.tail(weeks)

    # Sum to get total season demand
    total_demand = int(forecast_period['yhat'].sum())

    return total_demand
```

**ARIMA Configuration:**
```python
from pmdarima import auto_arima

def run_arima_forecast(historical_sales: pd.DataFrame, weeks: int = 12) -> int:
    """
    Forecast category demand using auto-ARIMA.

    Args:
        historical_sales: DataFrame with 'units_sold' column
        weeks: Forecast horizon

    Returns:
        Total forecasted units for season
    """
    # Extract time series
    ts = historical_sales['units_sold'].values

    # Auto-ARIMA to find best (p,d,q) parameters
    model = auto_arima(
        ts,
        seasonal=True,
        m=52,  # Weekly data, 52 weeks per year
        suppress_warnings=True,
        stepwise=True,
        trace=False
    )

    # Forecast
    forecast, conf_int = model.predict(n_periods=weeks, return_conf_int=True)

    # Sum to get total season demand
    total_demand = int(forecast.sum())

    return total_demand
```

**Ensemble Logic:**
```python
def forecast_category_demand(historical_sales: pd.DataFrame, weeks: int = 12) -> dict:
    """
    Ensemble forecast: Average Prophet + ARIMA results.
    """
    # Run both models
    prophet_total = run_prophet_forecast(historical_sales, weeks)
    arima_total = run_arima_forecast(historical_sales, weeks)

    # Simple average (no confidence weighting)
    ensemble_total = (prophet_total + arima_total) // 2

    return {
        "total_season_demand": ensemble_total,
        "prophet_forecast": prophet_total,  # Save for analysis
        "arima_forecast": arima_total,       # Save for analysis
        "forecasting_method": "ensemble_prophet_arima",
        "models_used": ["prophet", "arima"]
    }
```

**Design Decisions:**
- ❌ **No confidence scoring** (removed for simplicity)
- ✅ **Parallel execution** (Prophet + ARIMA run independently)
- ✅ **Simple averaging** (equal weight to both models)
- ✅ **Store both model outputs** (for post-hoc analysis)

#### 2. Store Clustering (K-Means)

**Approach:** K-means clustering with K=3 using 7 features (research-backed).

**Clustering Features:**
```python
clustering_features = [
    "store_size_sqft",           # Capacity
    "median_income",             # Demographics
    "location_tier_encoded",     # A=3, B=2, C=1
    "fashion_tier_encoded",      # Premium=3, Mainstream=2, Value=1
    "avg_weekly_sales_12mo",     # Historical performance (MOST IMPORTANT per research)
    "store_format_encoded",      # Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1
    "region_encoded"             # Northeast=1, Southeast=2, Midwest=3, West=4
]
```

**Implementation:**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

def cluster_stores(stores_df: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    """
    Cluster stores using K-means.

    Args:
        stores_df: DataFrame with store attributes
        n_clusters: Number of clusters (default 3 for MVP)

    Returns:
        DataFrame with added 'cluster_id' and 'cluster_name' columns
    """
    # Encode categorical features
    stores_df['location_tier_encoded'] = stores_df['location_tier'].map({'A': 3, 'B': 2, 'C': 1})
    stores_df['fashion_tier_encoded'] = stores_df['fashion_tier'].map({'PREMIUM': 3, 'MAINSTREAM': 2, 'VALUE': 1})
    stores_df['store_format_encoded'] = stores_df['store_format'].map({
        'MALL': 4, 'STANDALONE': 3, 'SHOPPING_CENTER': 2, 'OUTLET': 1
    })
    stores_df['region_encoded'] = stores_df['region'].map({
        'NORTHEAST': 1, 'SOUTHEAST': 2, 'MIDWEST': 3, 'WEST': 4
    })

    # Select features
    features = stores_df[clustering_features]

    # Standardize (important for K-means)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # K-means clustering
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',  # Smart initialization
        n_init=10,         # Number of runs with different seeds
        max_iter=300,
        random_state=42    # Reproducibility
    )

    # Assign clusters
    stores_df['cluster_label'] = kmeans.fit_predict(features_scaled)

    # Label clusters based on characteristics
    # (Analyze cluster centers to assign meaningful names)
    cluster_names = assign_cluster_names(stores_df, kmeans.cluster_centers_)
    stores_df['cluster_id'] = stores_df['cluster_label'].map(cluster_names)

    return stores_df

def assign_cluster_names(stores_df: pd.DataFrame, centers: np.ndarray) -> dict:
    """
    Assign meaningful names to clusters based on characteristics.
    """
    # Analyze each cluster's average fashion_tier_encoded
    cluster_profiles = stores_df.groupby('cluster_label')['fashion_tier_encoded'].mean()

    # Sort clusters by fashion tier (high to low)
    sorted_clusters = cluster_profiles.sort_values(ascending=False).index.tolist()

    # Map to names (MVP: hardcoded 3 clusters)
    return {
        sorted_clusters[0]: 'fashion_forward',
        sorted_clusters[1]: 'mainstream',
        sorted_clusters[2]: 'value_conscious'
    }
```

**Cluster Allocation Percentages:**
```python
def calculate_cluster_distribution(stores_df: pd.DataFrame, total_demand: int) -> list[dict]:
    """
    Calculate how demand splits across clusters.
    """
    # Count stores per cluster
    cluster_counts = stores_df.groupby('cluster_id').size()

    # Sum historical sales per cluster (proxy for demand distribution)
    cluster_sales = stores_df.groupby('cluster_id')['avg_weekly_sales_12mo'].sum()

    # Calculate allocation percentage (based on historical sales)
    total_sales = cluster_sales.sum()
    cluster_pcts = cluster_sales / total_sales

    # Apply to total demand
    distribution = []
    for cluster_id, pct in cluster_pcts.items():
        distribution.append({
            'cluster_id': cluster_id,
            'cluster_name': cluster_id.replace('_', ' ').title(),
            'allocation_percentage': float(pct),
            'total_units': int(total_demand * pct)
        })

    return distribution
```

**Design Decisions:**
- ✅ **K=3 clusters** (aligned with Product Brief)
- ✅ **7 features** (research-backed: historical sales is most important)
- ✅ **StandardScaler** (required for K-means)
- ✅ **k-means++** initialization (faster convergence)
- ❌ **No new stores** (all stores have historical data, out of scope for MVP)

#### 3. Store Allocation Factors

**Approach:** 70% historical sales + 30% store attributes.

```python
def calculate_store_allocation_factors(
    stores_df: pd.DataFrame,
    cluster_distribution: list[dict]
) -> pd.DataFrame:
    """
    Calculate allocation factor for each store within its cluster.

    Formula: factor = 0.7 × (store_sales / cluster_sales) + 0.3 × (store_attributes / cluster_avg_attributes)
    """
    stores_df = stores_df.copy()

    for cluster_info in cluster_distribution:
        cluster_id = cluster_info['cluster_id']
        cluster_total_units = cluster_info['total_units']

        # Filter stores in this cluster
        cluster_stores = stores_df[stores_df['cluster_id'] == cluster_id]

        # Historical component (70%)
        cluster_total_sales = cluster_stores['avg_weekly_sales_12mo'].sum()
        historical_factor = cluster_stores['avg_weekly_sales_12mo'] / cluster_total_sales

        # Attribute component (30%)
        # Normalize store size within cluster
        cluster_avg_size = cluster_stores['store_size_sqft'].mean()
        size_factor = cluster_stores['store_size_sqft'] / cluster_avg_size

        # Normalize median income within cluster
        cluster_avg_income = cluster_stores['median_income'].mean()
        income_factor = cluster_stores['median_income'] / cluster_avg_income

        # Average attribute factors
        attribute_factor = (size_factor + income_factor) / 2

        # Combined allocation factor (70% historical + 30% attributes)
        allocation_factor = 0.7 * historical_factor + 0.3 * attribute_factor

        # Normalize to sum to 1 within cluster
        allocation_factor = allocation_factor / allocation_factor.sum()

        # Calculate units for each store
        stores_df.loc[cluster_stores.index, 'allocation_factor'] = allocation_factor
        stores_df.loc[cluster_stores.index, 'season_total_units'] = (
            allocation_factor * cluster_total_units
        ).astype(int)

    return stores_df
```

**Design Decisions:**
- ✅ **70/30 split** (historical sales weighted higher)
- ✅ **Attributes:** Store size + median income (proxy for demand potential)
- ✅ **Normalization within cluster** (each cluster sums to 100%)
- ❌ **No confidence intervals** (removed for simplicity)

---

### Inventory Agent - Detailed Approach

#### 1. Manufacturing Calculation

**Formula:** `manufacturing_qty = total_demand × (1 + safety_stock_pct)`

**Implementation:**
```python
def calculate_manufacturing_order(total_demand: int, safety_stock_pct: float = 0.20) -> dict:
    """
    Calculate total manufacturing quantity with safety stock.

    Args:
        total_demand: Total season demand from Demand Agent
        safety_stock_pct: Fixed 20% safety stock

    Returns:
        Manufacturing order details
    """
    manufacturing_qty = int(total_demand * (1 + safety_stock_pct))
    safety_stock_units = manufacturing_qty - total_demand

    return {
        'total_demand': total_demand,
        'safety_stock_percentage': safety_stock_pct,
        'safety_stock_units': safety_stock_units,
        'manufacturing_qty': manufacturing_qty
    }
```

**Example:**
- Total demand: 8,000 units
- Safety stock: 20%
- Manufacturing: 8,000 × 1.20 = **9,600 units**

**Design Decisions:**
- ✅ **Fixed 20% safety stock** (not variable based on forecast uncertainty)
- ❌ **No dynamic adjustment** (no separate safety stock per cluster/store)

#### 2. Initial Allocation (55% to Stores, 45% Holdback)

**Approach:** Allocate 55% to stores initially, enforce 2-week minimum per store.

```python
def calculate_initial_allocation(
    stores_df: pd.DataFrame,
    manufacturing_qty: int,
    forecast_weekly_curve: list[dict],
    initial_pct: float = 0.55,
    holdback_pct: float = 0.45
) -> dict:
    """
    Calculate initial store allocations with 2-week minimum.

    Args:
        stores_df: DataFrame with 'season_total_units' per store
        manufacturing_qty: Total units manufactured
        forecast_weekly_curve: Weekly demand forecast
        initial_pct: 55% initial allocation
        holdback_pct: 45% holdback at DC

    Returns:
        Allocation plan with store details
    """
    initial_total = int(manufacturing_qty * initial_pct)
    holdback_total = int(manufacturing_qty * holdback_pct)

    # Calculate initial allocation per store
    stores_df['initial_allocation_calculated'] = (
        stores_df['season_total_units'] * initial_pct
    ).astype(int)

    # Enforce 2-week minimum
    week_1_2_demand = forecast_weekly_curve[0]['demand_units'] + forecast_weekly_curve[1]['demand_units']
    min_initial_per_store = week_1_2_demand / len(stores_df)  # Distribute evenly for minimum

    stores_df['initial_allocation'] = stores_df['initial_allocation_calculated'].apply(
        lambda x: max(x, int(min_initial_per_store))
    )

    # Calculate holdback (remaining from season total)
    stores_df['holdback_allocation'] = (
        stores_df['season_total_units'] - stores_df['initial_allocation']
    )

    # Prepare store allocations list
    store_allocations = []
    for _, row in stores_df.iterrows():
        store_allocations.append({
            'store_id': row['store_id'],
            'store_name': row['store_name'],
            'cluster_id': row['cluster_id'],
            'initial_allocation': int(row['initial_allocation']),
            'holdback_allocation': int(row['holdback_allocation']),
            'total_season_allocation': int(row['season_total_units'])
        })

    return {
        'manufacturing_qty': manufacturing_qty,
        'initial_allocation_total': initial_total,
        'holdback_total': holdback_total,
        'store_allocations': store_allocations
    }
```

**Design Decisions:**
- ✅ **2-week minimum** per store (prevents stockouts in Week 1-2)
- ✅ **Simple 55/45 split** (no cluster-specific splits)
- ❌ **No new stores** (all stores have full historical data)

#### 3. Replenishment Planning

**Approach:** Simple formula, rely on re-forecast for adjustments.

```python
def plan_weekly_replenishment(
    store_id: str,
    current_inventory: int,
    next_week_forecast: int
) -> int:
    """
    Calculate replenishment quantity for next week.

    Formula: replenish = next_week_forecast - current_inventory

    Note: No adaptive adjustments. If variance >20%, Orchestrator triggers re-forecast.
    """
    replenish_qty = max(0, next_week_forecast - current_inventory)
    return replenish_qty
```

**Design Decisions:**
- ✅ **Simple formula** (forecast - inventory)
- ❌ **No adaptive adjustments** (no real-time rate tracking)
- ✅ **Re-forecast at 20% variance** (let Demand Agent recalculate instead of micro-adjustments)

---

### Pricing Agent - Detailed Approach

#### 1. Markdown Calculation (Week 6 Checkpoint)

**Formula:** `markdown = (target_sell_through - actual_sell_through) × elasticity_coefficient`

**Implementation:**
```python
def calculate_markdown_recommendation(
    actual_sell_through_pct: float,
    target_sell_through_pct: float = 0.60,
    elasticity_coefficient: float = 2.0,
    max_markdown: float = 0.40
) -> dict:
    """
    Calculate markdown percentage using gap × elasticity formula.

    Args:
        actual_sell_through_pct: Actual sell-through by Week 6 (e.g., 0.50)
        target_sell_through_pct: Target sell-through (default 60%)
        elasticity_coefficient: Demand elasticity (default 2.0, tunable)
        max_markdown: Maximum allowed markdown (40%)

    Returns:
        Markdown recommendation
    """
    # Calculate gap
    gap = target_sell_through_pct - actual_sell_through_pct

    # If no gap or ahead of target, no markdown
    if gap <= 0:
        return {
            'recommended_markdown_pct': 0.0,
            'gap_pct': gap,
            'reasoning': 'On track or ahead of target, no markdown needed'
        }

    # Calculate markdown
    markdown_raw = gap * elasticity_coefficient

    # Cap at maximum
    markdown_capped = min(markdown_raw, max_markdown)

    # Round to nearest 5%
    markdown_rounded = round(markdown_capped * 20) / 20

    # Expected demand lift
    expected_lift = markdown_rounded * 1.5  # Assumes 1% markdown = 1.5% demand increase

    return {
        'recommended_markdown_pct': markdown_rounded,
        'gap_pct': gap,
        'elasticity_coefficient': elasticity_coefficient,
        'expected_demand_lift_pct': expected_lift,
        'reasoning': f'{gap*100:.1f}% gap × {elasticity_coefficient} elasticity = {markdown_rounded*100:.0f}% markdown'
    }
```

**Examples:**
- 58% sell-through → 2% gap → 2% × 2.0 = 4% → rounds to **5% markdown**
- 50% sell-through → 10% gap → 10% × 2.0 = 20% → **20% markdown**
- 40% sell-through → 20% gap → 20% × 2.0 = 40% → capped at **40% markdown**

**Design Decisions:**
- ✅ **Elasticity = 2.0** (tunable parameter, can adjust post-MVP)
- ✅ **5% rounding** (10%, 15%, 20%, not 13.7%)
- ✅ **40% cap** (prevent extreme markdowns)
- ❌ **No cluster-specific markdowns** (uniform across all stores)

#### 2. Post-Markdown Monitoring

**Approach:** Variance-triggered re-forecast (not additional markdown rounds).

```python
def monitor_post_markdown_performance(
    forecast_id: str,
    markdown_week: int,
    current_week: int
) -> dict:
    """
    Monitor performance after markdown applied.

    Note: No explicit success/failure check. Orchestrator monitors variance.
    If variance still >20% after markdown, triggers re-forecast.
    """
    # Query actual sales post-markdown
    actual_sales_post_markdown = db.query("""
        SELECT SUM(units_sold) FROM actual_sales
        WHERE forecast_id = ? AND week_number > ?
    """, [forecast_id, markdown_week])

    forecast_post_markdown = db.query("""
        SELECT SUM(demand_units) FROM forecast_weekly_details
        WHERE forecast_id = ? AND week_number > ?
    """, [forecast_id, markdown_week])

    variance = abs(actual_sales_post_markdown - forecast_post_markdown) / forecast_post_markdown

    return {
        'variance': variance,
        'threshold_exceeded': variance > 0.20,
        'action': 're-forecast' if variance > 0.20 else 'continue monitoring'
    }
```

**Design Decisions:**
- ✅ **Reuse 20% variance threshold** (same as pre-markdown monitoring)
- ✅ **No additional markdown rounds** (avoid over-markdowning)
- ✅ **Re-forecast if markdown doesn't work** (let Demand Agent recalculate with new post-markdown data)

#### 3. Markdown Application (Uniform)

**Approach:** Apply same markdown percentage to all stores (no cluster differentiation).

```python
def apply_markdown(
    markdown_pct: float,
    stores_df: pd.DataFrame
) -> list[dict]:
    """
    Apply uniform markdown across all stores.

    Args:
        markdown_pct: Markdown percentage (e.g., 0.20 for 20%)
        stores_df: All stores

    Returns:
        List of store markdown records
    """
    markdown_records = []

    for _, store in stores_df.iterrows():
        markdown_records.append({
            'store_id': store['store_id'],
            'cluster_id': store['cluster_id'],
            'markdown_pct': markdown_pct,
            'applied_at': datetime.now()
        })

    return markdown_records
```

**Design Decisions:**
- ✅ **Uniform markdown** (same % for all stores)
- ❌ **No cluster-specific adjustments** (Fashion_Forward vs Value_Conscious get same %)
- ✅ **Simplicity for MVP** (can add cluster differentiation post-MVP)

---

## 10. Agent Handoff Flow

### Handoff Patterns

**Sequential Handoffs via Orchestrator (Primary Pattern):**

```
Orchestrator → Demand Agent → Orchestrator → Inventory Agent → Orchestrator → Pricing Agent → Orchestrator
```

**Context-Rich Handoffs (Pass Objects Directly):**

```python
# Demand Agent completes forecast
forecast_result = {
    "forecast_id": "f_spring_2025",
    "total_demand": 8000,
    "weekly_curve": [...],
    "cluster_distribution": [...]
}

# Orchestrator hands off forecast object to Inventory Agent
orchestrator.handoff(
    inventory_agent,
    input={
        "task": "Calculate manufacturing and allocation",
        "forecast": forecast_result  # <-- Full forecast passed in context
    }
)

# Inventory Agent receives forecast directly (no database query needed)
# Agent instructions: "You will receive a forecast object. Use it to calculate manufacturing..."
```

**Benefits:**
- ✅ No database round-trips between agents
- ✅ Faster execution
- ✅ Simpler agent code (no schema knowledge needed)

### Dynamic Handoff Enabling (Variance-Triggered Re-Forecast)

**Normal Flow (Variance <20%):**
```python
# Orchestrator monitors variance
variance = calculate_variance(actual_sales, forecast)

if variance <= 0.20:
    # Keep re-forecast handoff DISABLED
    orchestrator.disable_handoff("reforecast")
    # Continue with normal replenishment
```

**Re-Forecast Flow (Variance >20%):**
```python
# Orchestrator detects high variance
variance = 0.255  # 25.5%

if variance > 0.20:
    # ENABLE re-forecast handoff dynamically
    orchestrator.enable_handoff("reforecast")

    # Prepare context for Demand Agent
    reforecast_context = {
        "reason": "variance_exceeds_20_percent",
        "variance": 0.255,
        "actual_week_1_to_4": 3200,
        "forecasted_week_1_to_4": 2550,
        "remaining_weeks": 8,
        "instruction": "Re-forecast remaining 8 weeks using updated actuals"
    }

    # Hand off to Demand Agent with context
    orchestrator.handoff(demand_agent, input=reforecast_context)
```

**Handoff Configuration:**
```python
from openai_agents import Agent, handoff

orchestrator = Agent(
    name="Orchestrator",
    instructions="...",
    handoffs=[
        demand_agent,      # Always available for initial forecast
        inventory_agent,   # Always available
        pricing_agent,     # Always available

        # Re-forecast handoff (dynamically enabled/disabled)
        handoff(
            demand_agent,
            name="reforecast",
            description="Re-forecast demand based on variance alert",
            enabled=False  # <-- Start disabled, enable at runtime when variance >20%
        )
    ]
)
```

### Sessions & Guardrails

**Session Management (Automatic):**
```python
from openai_agents import Session

# Session automatically maintains conversation history
session = Session()

# Run workflow
result = session.run(
    orchestrator,
    input={"action": "generate_forecast", "category": "womens_dresses"}
)

# All agent handoffs are tracked in session history
# No manual history management needed
```

**Guardrails (Output Validation):**
```python
from openai_agents import Guardrail

def validate_forecast_output(result: dict) -> dict:
    """Validate Demand Agent output."""
    if result.get("total_season_demand", 0) <= 0:
        raise ValueError("Forecast total_season_demand must be positive")

    if result.get("total_season_demand", 0) > 100000:
        raise ValueError("Forecast total_season_demand exceeds reasonable limit (100k)")

    return result

def validate_allocation_output(result: dict) -> dict:
    """Validate Inventory Agent output."""
    if result.get("manufacturing_qty", 0) <= 0:
        raise ValueError("Manufacturing quantity must be positive")

    initial = result.get("initial_allocation_total", 0)
    holdback = result.get("holdback_total", 0)
    total = result.get("manufacturing_qty", 0)

    if initial + holdback != total:
        raise ValueError(f"Allocation mismatch: {initial} + {holdback} ≠ {total}")

    return result

# Attach guardrails to agents
demand_agent = Agent(
    name="Demand Agent",
    instructions="...",
    tools=[...],
    guardrails=[Guardrail(output_validation=validate_forecast_output)]
)

inventory_agent = Agent(
    name="Inventory Agent",
    instructions="...",
    tools=[...],
    guardrails=[Guardrail(output_validation=validate_allocation_output)]
)
```

---

## 11. REST API Specification

### API Base URL
- **Local Development:** `http://localhost:8000/api`
- **WebSocket:** `ws://localhost:8000/api`

### Primary Workflow Endpoints

#### POST /api/workflows/forecast
**Description:** Trigger pre-season forecast workflow (Orchestrator → 3 agents)

**Request:**
```json
{
  "category_id": "womens_dresses",
  "season": "spring_2025",
  "season_start_date": "2025-03-01",
  "season_end_date": "2025-05-23",
  "season_length_weeks": 12
}
```

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "status": "started",
  "websocket_url": "ws://localhost:8000/api/workflows/wf_abc123/stream"
}
```

#### POST /api/workflows/reforecast
**Description:** Manually trigger re-forecast (usually auto-triggered by variance)

**Request:**
```json
{
  "forecast_id": "f_spring_2025",
  "reason": "manual_override",
  "actual_sales_week_1_to_n": 3200,
  "remaining_weeks": 8
}
```

**Response:**
```json
{
  "workflow_id": "wf_def456",
  "status": "started",
  "websocket_url": "ws://localhost:8000/api/workflows/wf_def456/stream"
}
```

#### GET /api/workflows/{workflow_id}/status
**Description:** Get workflow status (polling alternative to WebSocket)

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "status": "running",
  "current_agent": "Inventory Agent",
  "progress_pct": 66,
  "started_at": "2025-10-12T10:30:00Z",
  "updated_at": "2025-10-12T10:30:45Z"
}
```

### Resource Endpoints

#### GET /api/forecasts
**Description:** List all forecasts

**Response:**
```json
{
  "forecasts": [
    {
      "forecast_id": "f_spring_2025",
      "category_name": "Women's Dresses",
      "season": "Spring 2025",
      "total_season_demand": 8000,
      "created_at": "2025-10-12T10:30:00Z"
    }
  ]
}
```

#### GET /api/forecasts/{forecast_id}
**Description:** Get detailed forecast

**Response:**
```json
{
  "forecast_id": "f_spring_2025",
  "category_id": "womens_dresses",
  "total_season_demand": 8000,
  "weekly_demand_curve": [
    {"week_number": 1, "demand_units": 500},
    {"week_number": 2, "demand_units": 600},
    ...
  ],
  "cluster_distribution": [
    {
      "cluster_id": "fashion_forward",
      "cluster_name": "Fashion Forward",
      "allocation_percentage": 0.40,
      "total_units": 3200
    },
    ...
  ],
  "forecasting_method": "ensemble_prophet_arima",
  "prophet_forecast": 8200,
  "arima_forecast": 7800
}
```

#### GET /api/allocations/{forecast_id}
**Description:** Get allocation plan for forecast

**Response:**
```json
{
  "allocation_id": "a_spring_2025",
  "forecast_id": "f_spring_2025",
  "manufacturing_qty": 9600,
  "safety_stock_percentage": 0.20,
  "initial_allocation_total": 5280,
  "holdback_total": 4320,
  "store_allocations": [
    {
      "store_id": "S01",
      "store_name": "NYC Flagship",
      "cluster_id": "fashion_forward",
      "initial_allocation": 176,
      "holdback_allocation": 142,
      "total_season_allocation": 318
    },
    ...
  ]
}
```

#### GET /api/markdowns/{forecast_id}
**Description:** Get markdown recommendations

**Response:**
```json
{
  "markdown_id": "m_spring_2025_week6",
  "forecast_id": "f_spring_2025",
  "week_number": 6,
  "sell_through_pct": 0.50,
  "target_sell_through_pct": 0.60,
  "gap_pct": 0.10,
  "recommended_markdown_pct": 0.20,
  "elasticity_coefficient": 2.0,
  "expected_demand_lift_pct": 0.30,
  "status": "pending_approval",
  "reasoning": "10% gap × 2.0 elasticity = 20% markdown"
}
```

#### GET /api/variance/{forecast_id}/week/{week_number}
**Description:** Get variance for specific week

**Response:**
```json
{
  "forecast_id": "f_spring_2025",
  "week_number": 4,
  "forecasted_cumulative": 2550,
  "actual_cumulative": 3200,
  "variance_pct": 0.255,
  "threshold_exceeded": true,
  "action_taken": "reforecast_triggered"
}
```

### Agent-Specific Endpoints (Debug/Override)

#### POST /api/agents/demand/forecast
**Description:** Directly call Demand Agent (for testing/debugging)

**Request:**
```json
{
  "category_id": "womens_dresses",
  "historical_sales_csv": "path/to/data.csv",
  "forecast_weeks": 12
}
```

**Response:**
```json
{
  "total_season_demand": 8000,
  "weekly_curve": [...],
  "cluster_distribution": [...],
  "forecasting_method": "ensemble_prophet_arima"
}
```

#### POST /api/agents/inventory/allocate
**Description:** Directly call Inventory Agent

#### POST /api/agents/pricing/analyze
**Description:** Directly call Pricing Agent

### Data Management Endpoints

#### GET /api/categories
**Description:** List all categories

#### GET /api/stores
**Description:** List all stores

#### GET /api/stores/clusters
**Description:** List store clusters

#### POST /api/data/upload-historical-sales
**Description:** Upload historical sales CSV for training

**Request:** `multipart/form-data`
- `file`: CSV file with columns `[store_id, category_id, week_start_date, units_sold]`

**Response:**
```json
{
  "rows_imported": 1560,
  "date_range": "2022-01-01 to 2024-12-31",
  "message": "Historical sales data imported successfully"
}
```

#### POST /api/data/upload-weekly-sales
**Description:** Upload actual weekly sales (for variance monitoring)

**Request:** `multipart/form-data`
- `file`: CSV file with columns `[store_id, week_number, units_sold]`
- `forecast_id`: Associated forecast ID

**Response:**
```json
{
  "rows_imported": 50,
  "week_number": 4,
  "variance_check": {
    "variance_pct": 0.255,
    "threshold_exceeded": true,
    "reforecast_triggered": true,
    "workflow_id": "wf_reforecast_789"
  }
}
```

### WebSocket Endpoint

#### WS /api/workflows/{workflow_id}/stream
**Description:** Real-time agent updates

**Message Types:**

**1. Agent Started:**
```json
{
  "type": "agent_started",
  "agent": "Demand Agent",
  "timestamp": "2025-10-12T10:30:15Z"
}
```

**2. Agent Progress:**
```json
{
  "type": "agent_progress",
  "agent": "Demand Agent",
  "message": "Running Prophet forecasting model...",
  "progress_pct": 33,
  "timestamp": "2025-10-12T10:30:20Z"
}
```

**3. Agent Completed:**
```json
{
  "type": "agent_completed",
  "agent": "Demand Agent",
  "duration_seconds": 15.3,
  "result": {
    "total_season_demand": 8000,
    "prophet_forecast": 8200,
    "arima_forecast": 7800
  },
  "timestamp": "2025-10-12T10:30:30Z"
}
```

**4. Human Input Required:**
```json
{
  "type": "human_input_required",
  "agent": "Inventory Agent",
  "action": "approve_manufacturing_order",
  "data": {
    "manufacturing_qty": 9600,
    "initial_allocation": 5280,
    "holdback": 4320,
    "store_allocations": [...]
  },
  "options": ["modify", "accept"],
  "timestamp": "2025-10-12T10:30:45Z"
}
```

**5. Workflow Complete:**
```json
{
  "type": "workflow_complete",
  "workflow_id": "wf_abc123",
  "duration_seconds": 28.5,
  "result": {
    "forecast_id": "f_spring_2025",
    "allocation_id": "a_spring_2025",
    "pricing_strategy_id": "p_spring_2025"
  },
  "timestamp": "2025-10-12T10:30:58Z"
}
```

**6. Error:**
```json
{
  "type": "error",
  "agent": "Demand Agent",
  "error_message": "Insufficient historical data: Need 24+ months, found 18 months",
  "timestamp": "2025-10-12T10:30:25Z"
}
```

---

## 12. Frontend Flow

### Real-Time Agent Visualization (WebSocket)

**Technology:** React + WebSocket

**User Flow:**

1. **User triggers forecast** → POST /api/workflows/forecast
2. **Backend returns workflow_id** → Frontend opens WebSocket connection
3. **Real-time updates** → UI shows agent progress step-by-step
4. **Human approval** → Modal appears when agent needs input
5. **Completion** → Dashboard shows full forecast report

### Human-in-the-Loop (Modify/Accept Only)

**Approval Modal Pattern:**

```typescript
interface ApprovalModalProps {
  agentName: string;
  action: string;
  data: any;
  onModify: (newParams: any) => void;
  onAccept: () => void;
}

function ApprovalModal({ agentName, action, data, onModify, onAccept }: ApprovalModalProps) {
  const [isModifying, setIsModifying] = useState(false);

  return (
    <Modal>
      <h2>⚠️ Approval Required - {action}</h2>

      {/* Show agent reasoning */}
      <AgentReasoningPanel agent={agentName} data={data} />

      {/* Show data preview */}
      <DataPreview data={data} />

      {/* Modify mode */}
      {isModifying && (
        <ParameterEditor
          data={data}
          onSubmit={(newParams) => {
            onModify(newParams);
            setIsModifying(false);
          }}
        />
      )}

      {/* Actions (NO reject button) */}
      <div className="actions">
        <Button onClick={() => setIsModifying(true)}>
          ✏️ Modify
        </Button>
        <Button onClick={onAccept} variant="primary">
          ✅ Accept
        </Button>
      </div>
    </Modal>
  );
}
```

**Modify Flow:**
1. User clicks "Modify"
2. Modal shows parameter editor (e.g., adjust safety stock from 20% to 15%)
3. User submits new parameters
4. Frontend sends via WebSocket: `{"type": "modify_params", "params": {...}}`
5. Agent re-runs with new parameters
6. Returns updated result
7. User approves revised result

**No Reject Option:**
- Only "Modify" (iterative refinement) or "Accept" (approve)
- If user fundamentally disagrees, they can close workflow and start fresh

### Weekly Sales Upload Flow

**Upload Component:**

```typescript
function WeeklySalesUpload({ forecastId, currentWeek }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [varianceResult, setVarianceResult] = useState<any>(null);

  const handleUpload = async () => {
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('forecast_id', forecastId);

    const response = await fetch('/api/data/upload-weekly-sales', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    setVarianceResult(result.variance_check);
    setUploading(false);

    // If re-forecast triggered, show notification
    if (result.variance_check.reforecast_triggered) {
      showNotification({
        type: 'warning',
        title: 'Re-Forecast Triggered',
        message: `Variance ${(result.variance_check.variance_pct * 100).toFixed(1)}% exceeds 20% threshold`,
        action: {
          label: 'View Live Progress',
          onClick: () => openWorkflowMonitor(result.variance_check.workflow_id)
        }
      });
    }
  };

  return (
    <div>
      <h3>📅 Week {currentWeek} - Upload Actual Sales</h3>

      <FileUpload onFileSelect={setFile} accept=".csv" />

      <Button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload Week ' + currentWeek + ' Sales'}
      </Button>

      {varianceResult && (
        <VarianceAlert variance={varianceResult} />
      )}
    </div>
  );
}
```

**Variance Alert Component:**

```typescript
function VarianceAlert({ variance }: { variance: VarianceResult }) {
  if (!variance.threshold_exceeded) {
    return (
      <Alert type="success">
        ✅ Variance {(variance.variance_pct * 100).toFixed(1)}% - Within threshold
      </Alert>
    );
  }

  return (
    <Alert type="warning">
      ⚠️ Variance {(variance.variance_pct * 100).toFixed(1)}% - Threshold exceeded
      <p>Re-forecast workflow automatically triggered</p>
      <Button onClick={() => openWorkflowMonitor(variance.workflow_id)}>
        View Live Progress →
      </Button>
    </Alert>
  );
}
```

### Key Frontend Features

1. **Agent Progress Visualization:**
   - Step-by-step progress bar
   - Real-time status updates (via WebSocket)
   - Execution time per agent

2. **Human-in-the-Loop Modals:**
   - Show agent reasoning
   - Allow parameter modification
   - Iterative refinement (modify → re-run → approve)
   - No reject button (modify or accept only)

3. **Weekly Sales Upload:**
   - CSV file upload
   - Auto-variance check after upload
   - Auto-trigger re-forecast if variance >20%
   - Notification with link to live workflow

4. **Dashboard Components:**
   - Forecast overview (total demand, weekly curve chart)
   - Cluster distribution (pie chart)
   - Store allocation table (sortable, filterable)
   - Markdown recommendations (Week 6 checkpoint card)
   - Variance tracking (weekly line chart)

---

## 13. Database Schema

### Schema Design: Hybrid (Normalized Entities + JSON Arrays)

**Approach:**
- Normalize master data (stores, clusters, categories) for queryability
- Use JSON for variable-length arrays (weekly curves, store allocations)
- Foreign keys for referential integrity

### Tables

#### 1. categories
```sql
CREATE TABLE categories (
    category_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL,
    season_start_date DATE NOT NULL,
    season_end_date DATE NOT NULL,
    season_length_weeks INTEGER NOT NULL,
    archetype TEXT NOT NULL CHECK(archetype IN ('FASHION_RETAIL', 'STABLE_CATALOG', 'CONTINUOUS')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. store_clusters
```sql
CREATE TABLE store_clusters (
    cluster_id TEXT PRIMARY KEY,
    cluster_name TEXT NOT NULL,
    fashion_tier TEXT NOT NULL CHECK(fashion_tier IN ('PREMIUM', 'MAINSTREAM', 'VALUE')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. stores
```sql
CREATE TABLE stores (
    store_id TEXT PRIMARY KEY,
    store_name TEXT NOT NULL,
    cluster_id TEXT NOT NULL REFERENCES store_clusters(cluster_id),
    store_size_sqft INTEGER NOT NULL,
    location_tier TEXT NOT NULL CHECK(location_tier IN ('A', 'B', 'C')),
    median_income INTEGER NOT NULL,
    store_format TEXT NOT NULL CHECK(store_format IN ('MALL', 'STANDALONE', 'SHOPPING_CENTER', 'OUTLET')),
    region TEXT NOT NULL CHECK(region IN ('NORTHEAST', 'SOUTHEAST', 'MIDWEST', 'WEST')),
    avg_weekly_sales_12mo REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. forecasts
```sql
CREATE TABLE forecasts (
    forecast_id TEXT PRIMARY KEY,
    category_id TEXT NOT NULL REFERENCES categories(category_id),
    season TEXT NOT NULL,
    forecast_horizon_weeks INTEGER NOT NULL,
    total_season_demand INTEGER NOT NULL CHECK(total_season_demand >= 0),
    weekly_demand_curve JSON NOT NULL,  -- [{"week_number": 1, "demand_units": 500}, ...]
    peak_week INTEGER NOT NULL,
    forecasting_method TEXT NOT NULL DEFAULT 'ensemble_prophet_arima',
    models_used JSON NOT NULL,  -- ["prophet", "arima"]
    prophet_forecast INTEGER,
    arima_forecast INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. forecast_cluster_distribution
```sql
CREATE TABLE forecast_cluster_distribution (
    distribution_id TEXT PRIMARY KEY,
    forecast_id TEXT NOT NULL REFERENCES forecasts(forecast_id),
    cluster_id TEXT NOT NULL REFERENCES store_clusters(cluster_id),
    allocation_percentage REAL NOT NULL CHECK(allocation_percentage >= 0 AND allocation_percentage <= 1),
    total_units INTEGER NOT NULL CHECK(total_units >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. allocations
```sql
CREATE TABLE allocations (
    allocation_id TEXT PRIMARY KEY,
    forecast_id TEXT NOT NULL REFERENCES forecasts(forecast_id),
    manufacturing_qty INTEGER NOT NULL CHECK(manufacturing_qty >= 0),
    safety_stock_percentage REAL NOT NULL DEFAULT 0.20,
    initial_allocation_total INTEGER NOT NULL CHECK(initial_allocation_total >= 0),
    holdback_total INTEGER NOT NULL CHECK(holdback_total >= 0),
    store_allocations JSON NOT NULL,  -- [{"store_id": "S01", "initial": 176, "holdback": 142}, ...]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. markdowns
```sql
CREATE TABLE markdowns (
    markdown_id TEXT PRIMARY KEY,
    forecast_id TEXT NOT NULL REFERENCES forecasts(forecast_id),
    week_number INTEGER NOT NULL CHECK(week_number >= 1 AND week_number <= 12),
    sell_through_pct REAL NOT NULL CHECK(sell_through_pct >= 0 AND sell_through_pct <= 1),
    target_sell_through_pct REAL NOT NULL DEFAULT 0.60,
    gap_pct REAL NOT NULL,
    recommended_markdown_pct REAL NOT NULL CHECK(recommended_markdown_pct >= 0 AND recommended_markdown_pct <= 0.40),
    elasticity_coefficient REAL NOT NULL DEFAULT 2.0,
    expected_demand_lift_pct REAL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'applied')) DEFAULT 'pending',
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. historical_sales
```sql
CREATE TABLE historical_sales (
    sale_id TEXT PRIMARY KEY,
    store_id TEXT NOT NULL REFERENCES stores(store_id),
    category_id TEXT NOT NULL REFERENCES categories(category_id),
    week_start_date DATE NOT NULL,
    units_sold INTEGER NOT NULL CHECK(units_sold >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historical_sales_store_category ON historical_sales(store_id, category_id);
CREATE INDEX idx_historical_sales_date ON historical_sales(week_start_date);
```

#### 9. actual_sales
```sql
CREATE TABLE actual_sales (
    actual_id TEXT PRIMARY KEY,
    store_id TEXT NOT NULL REFERENCES stores(store_id),
    forecast_id TEXT NOT NULL REFERENCES forecasts(forecast_id),
    week_number INTEGER NOT NULL CHECK(week_number >= 1 AND week_number <= 12),
    units_sold INTEGER NOT NULL CHECK(units_sold >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actual_sales_forecast_week ON actual_sales(forecast_id, week_number);
```

#### 10. workflow_logs
```sql
CREATE TABLE workflow_logs (
    log_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    input_data JSON,
    output_data JSON,
    duration_seconds REAL,
    status TEXT NOT NULL CHECK(status IN ('started', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflow_logs_workflow ON workflow_logs(workflow_id);
```

### Example Queries

**Get complete forecast with clusters:**
```sql
SELECT
    f.forecast_id,
    f.total_season_demand,
    f.weekly_demand_curve,
    fcd.cluster_id,
    sc.cluster_name,
    fcd.allocation_percentage,
    fcd.total_units
FROM forecasts f
LEFT JOIN forecast_cluster_distribution fcd ON f.forecast_id = fcd.forecast_id
LEFT JOIN store_clusters sc ON fcd.cluster_id = sc.cluster_id
WHERE f.forecast_id = 'f_spring_2025';
```

**Calculate variance for Week 4:**
```sql
SELECT
    f.forecast_id,
    SUM(acs.units_sold) as actual_cumulative,
    -- Extract forecasted sum from JSON (SQLite JSON functions)
    (SELECT SUM(json_extract(value, '$.demand_units'))
     FROM json_each(f.weekly_demand_curve)
     WHERE json_extract(value, '$.week_number') <= 4) as forecast_cumulative
FROM forecasts f
JOIN actual_sales acs ON f.forecast_id = acs.forecast_id
WHERE f.forecast_id = 'f_spring_2025'
  AND acs.week_number <= 4
GROUP BY f.forecast_id;
```

**Get all stores in Fashion_Forward cluster:**
```sql
SELECT
    s.store_id,
    s.store_name,
    s.store_size_sqft,
    sc.cluster_name
FROM stores s
JOIN store_clusters sc ON s.cluster_id = sc.cluster_id
WHERE sc.cluster_id = 'fashion_forward';
```

---

## 14. Source Tree Structure

### Monorepo Structure (Backend + Frontend)

```
retail-forecasting/
├── backend/                           # Python backend (FastAPI + Agents SDK)
│   ├── agents/                        # Agent implementations
│   │   ├── __init__.py
│   │   ├── demand_agent.py            # Demand Agent (forecasting, clustering)
│   │   ├── inventory_agent.py         # Inventory Agent (manufacturing, allocation)
│   │   ├── pricing_agent.py           # Pricing Agent (markdown recommendations)
│   │   └── orchestrator.py            # Orchestrator (workflow coordination)
│   │
│   ├── api/                           # FastAPI routes
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── workflows.py           # POST /workflows/forecast, /workflows/reforecast
│   │   │   ├── forecasts.py           # GET /forecasts, /forecasts/{id}
│   │   │   ├── allocations.py         # GET /allocations/{id}
│   │   │   ├── markdowns.py           # GET /markdowns/{id}
│   │   │   ├── data.py                # POST /data/upload-*
│   │   │   └── agents.py              # POST /agents/{agent}/...
│   │   └── websocket.py               # WebSocket handler (WS /workflows/{id}/stream)
│   │
│   ├── models/                        # Pydantic models
│   │   ├── __init__.py
│   │   ├── schemas.py                 # All Pydantic models (Category, Store, Forecast, etc.)
│   │   └── enums.py                   # Enums (RetailArchetype, LocationTier, etc.)
│   │
│   ├── database/                      # Database layer
│   │   ├── __init__.py
│   │   ├── db.py                      # SQLite connection, query helpers
│   │   ├── migrations/                # SQL migration scripts
│   │   │   ├── 001_create_tables.sql
│   │   │   └── 002_add_indexes.sql
│   │   └── seed_data.py               # Seed mock data (50 stores, clusters, etc.)
│   │
│   ├── ml/                            # ML/forecasting logic
│   │   ├── __init__.py
│   │   ├── forecasting.py             # Prophet + ARIMA ensemble
│   │   ├── clustering.py              # K-means store clustering
│   │   └── allocation.py              # Allocation factor calculation
│   │
│   ├── utils/                         # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py                  # Logging configuration
│   │   └── validators.py              # Guardrail validation functions
│   │
│   ├── tests/                         # Backend tests
│   │   ├── __init__.py
│   │   ├── test_agents/
│   │   │   ├── test_demand_agent.py
│   │   │   ├── test_inventory_agent.py
│   │   │   └── test_pricing_agent.py
│   │   ├── test_ml/
│   │   │   ├── test_forecasting.py
│   │   │   └── test_clustering.py
│   │   ├── test_api/
│   │   │   └── test_workflows.py
│   │   └── fixtures/                  # Test data
│   │       └── mock_historical_sales.csv
│   │
│   ├── pyproject.toml                 # UV configuration, dependencies
│   ├── .env.example                   # Environment variables template
│   ├── .env                           # Environment variables (gitignored)
│   └── README.md                      # Backend setup instructions
│
├── frontend/                          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/                # Reusable UI components
│   │   │   ├── AgentProgressBar.tsx   # Agent workflow progress visualization
│   │   │   ├── ApprovalModal.tsx      # Human-in-the-loop approval modal
│   │   │   ├── ForecastChart.tsx      # Weekly demand curve chart (Recharts)
│   │   │   ├── ClusterDistribution.tsx # Pie chart for cluster allocation
│   │   │   ├── StoreAllocationTable.tsx # TanStack Table for store allocations
│   │   │   ├── VarianceAlert.tsx      # Variance threshold alert
│   │   │   └── WeeklySalesUpload.tsx  # CSV upload component
│   │   │
│   │   ├── pages/                     # Page components
│   │   │   ├── Dashboard.tsx          # Main dashboard
│   │   │   ├── ForecastDetail.tsx     # Forecast detail view
│   │   │   ├── WeeklyMonitoring.tsx   # Weekly sales upload & variance tracking
│   │   │   └── MarkdownManager.tsx    # Week 6 markdown checkpoint
│   │   │
│   │   ├── hooks/                     # Custom React hooks
│   │   │   ├── useWebSocket.ts        # WebSocket connection hook
│   │   │   ├── useForecast.ts         # TanStack Query hook for forecasts
│   │   │   ├── useAllocation.ts       # TanStack Query hook for allocations
│   │   │   └── useWorkflow.ts         # Workflow status hook
│   │   │
│   │   ├── api/                       # API client
│   │   │   ├── client.ts              # Axios/fetch client configuration
│   │   │   └── endpoints.ts           # API endpoint functions
│   │   │
│   │   ├── types/                     # TypeScript types
│   │   │   ├── forecast.ts            # Forecast interfaces
│   │   │   ├── allocation.ts          # Allocation interfaces
│   │   │   └── workflow.ts            # Workflow interfaces
│   │   │
│   │   ├── App.tsx                    # Main App component
│   │   ├── main.tsx                   # Entry point (React 18 + React Router)
│   │   └── index.css                  # Global styles (Tailwind imports)
│   │
│   ├── tests/                         # Frontend tests
│   │   ├── components/
│   │   │   └── AgentProgressBar.test.tsx
│   │   └── e2e/                       # Playwright E2E tests
│   │       └── forecast-workflow.spec.ts
│   │
│   ├── package.json                   # npm dependencies
│   ├── vite.config.ts                 # Vite configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   └── README.md                      # Frontend setup instructions
│
├── data/                              # Mock data (CSV files)
│   ├── mock/
│   │   ├── historical_sales.csv       # Historical sales (2-3 years)
│   │   ├── stores.csv                 # 50 stores with attributes
│   │   ├── categories.csv             # Categories (Women's Dresses, etc.)
│   │   └── clusters.csv               # 3 clusters (Fashion_Forward, Mainstream, Value_Conscious)
│   └── README.md                      # Data schema documentation
│
├── docs/                              # Documentation
│   └── 04_PoC_Development/
│       ├── Architecture/
│       │   └── technical_architecture.md  # This document
│       └── product_brief/
│           └── product_brief_v3.1.md
│
├── .gitignore                         # Git ignore (includes .env, node_modules, etc.)
├── README.md                          # Project overview and setup
└── LICENSE                            # License file
```

---

## 15. Infrastructure & Deployment

### Local Development Setup

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- UV package manager (`pip install uv`)
- Git

**Backend Setup:**
```bash
# Navigate to backend
cd backend

# Install dependencies (UV will create virtual environment automatically)
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Run database migrations
uv run python -m database.migrations.run

# Seed mock data (50 stores, 3 clusters, historical sales)
uv run python -m database.seed_data

# Start backend server
uv run uvicorn api.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)

### Environment Variables

**backend/.env:**
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-10-21

# Database
DATABASE_URL=sqlite:///./retail_forecasting.db

# App Configuration
DEBUG=true
LOG_LEVEL=INFO
```

**frontend/.env:**
```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/api
```

### Development Workflow

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Testing:**
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

### Database Management

**SQLite File:** `backend/retail_forecasting.db`

**Migrations:**
```bash
# Run migrations
cd backend
uv run python -m database.migrations.run

# Reset database (for testing)
rm retail_forecasting.db
uv run python -m database.migrations.run
uv run python -m database.seed_data
```

**Database Tools:**
- [DB Browser for SQLite](https://sqlitebrowser.org/) - GUI for viewing/editing SQLite

---

## 16. Error Handling Strategy

### Approach: Fail Fast

**Philosophy:** Errors stop workflow immediately with clear messages. No retries, no fallbacks. User fixes issue and restarts.

### Error Categories

**1. Agent Logic Errors:**
- Insufficient historical data (need 24+ months, found 18)
- Invalid forecast result (negative demand)
- Allocation mismatch (initial + holdback ≠ total)

**Action:** Fail immediately, log error, return clear message to user via WebSocket

**2. API Errors (Azure OpenAI):**
- Rate limit exceeded
- Invalid API key
- Network timeout

**Action:** Fail immediately (no retry for MVP), log error, show user-friendly message

**3. Database Errors:**
- Connection lost
- Constraint violation (foreign key, check constraint)

**Action:** Fail immediately, log error, rollback transaction

**4. WebSocket Errors:**
- Connection dropped
- Client disconnected

**Action:** Log error, allow user to reconnect and view workflow status via REST API

### Error Handling Implementation

**Agent Level (Guardrails):**
```python
from openai_agents import Guardrail

def validate_forecast(result: dict) -> dict:
    if result.get("total_season_demand", 0) <= 0:
        raise ValueError("Forecast must be positive")
    return result

demand_agent = Agent(
    name="Demand Agent",
    guardrails=[Guardrail(output_validation=validate_forecast)]
)
```

**API Level (FastAPI Exception Handlers):**
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "message": str(exc),
            "type": "validation_error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Check logs for details.",
            "type": "server_error"
        }
    )
```

**WebSocket Level:**
```python
@app.websocket("/api/workflows/{workflow_id}/stream")
async def workflow_stream(websocket: WebSocket, workflow_id: str):
    await websocket.accept()

    try:
        # Run workflow
        result = run_workflow(workflow_id)

        await websocket.send_json({
            "type": "workflow_complete",
            "result": result
        })

    except Exception as e:
        logger.error(f"Workflow error: {e}", exc_info=True)

        await websocket.send_json({
            "type": "error",
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        })

    finally:
        await websocket.close()
```

**Workflow Logging:**
```python
def log_workflow_event(
    workflow_id: str,
    agent_name: str,
    action: str,
    status: str,
    error_message: str | None = None
):
    db.execute("""
        INSERT INTO workflow_logs
        (log_id, workflow_id, agent_name, action, status, error_message, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        f"log_{uuid.uuid4()}",
        workflow_id,
        agent_name,
        action,
        status,
        error_message,
        datetime.now()
    ])
```

### User-Facing Error Messages

**Good Error Messages (Actionable):**
- ❌ "Insufficient historical data: Need 24+ months, found 18 months. Please upload additional historical sales data."
- ❌ "Azure OpenAI rate limit exceeded. Please wait 60 seconds and try again."
- ❌ "Forecast validation failed: Total demand cannot be negative. Check historical sales data for anomalies."

**Bad Error Messages (Avoid):**
- ❌ "Error 500"
- ❌ "An error occurred"
- ❌ "NoneType object has no attribute 'total_demand'"

---

## 17. Coding Standards

### Python (Backend)

**Linting & Formatting:**
```bash
# Install Ruff
uv add ruff --dev

# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy backend/
```

**Ruff Configuration (pyproject.toml):**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
]

[tool.mypy]
python_version = "3.11"
strict = true
```

**Type Hints (Required):**
```python
# Good
def forecast_category_demand(
    historical_sales: pd.DataFrame,
    weeks: int = 12
) -> dict:
    ...

# Bad (no type hints)
def forecast_category_demand(historical_sales, weeks=12):
    ...
```

**Pydantic for Validation:**
```python
# Use Pydantic models for all data structures
from pydantic import BaseModel, Field

class Forecast(BaseModel):
    forecast_id: str
    total_demand: int = Field(..., ge=0)
```

### TypeScript (Frontend)

**Linting & Formatting:**
```bash
# Lint
npm run lint

# Format
npm run format
```

**ESLint + Prettier Configuration (.eslintrc.json):**
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

**TypeScript Strict Mode (tsconfig.json):**
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**Interfaces for All Props:**
```typescript
// Good
interface ForecastChartProps {
  forecastId: string;
  weeklyCurve: Array<{week: number, demand: number}>;
}

function ForecastChart({ forecastId, weeklyCurve }: ForecastChartProps) {
  ...
}

// Bad (no interface)
function ForecastChart(props: any) {
  ...
}
```

### General Standards

**Naming Conventions:**
- Python: `snake_case` for functions/variables, `PascalCase` for classes
- TypeScript: `camelCase` for functions/variables, `PascalCase` for components/interfaces
- Constants: `UPPER_SNAKE_CASE`

**File Naming:**
- Python: `demand_agent.py`, `forecasting.py`
- TypeScript: `ForecastChart.tsx`, `useForecast.ts`

**Comments:**
- Prefer self-documenting code (clear naming)
- Add comments for complex logic only
- No commented-out code (use git history)

---

## 18. Test Strategy

### Comprehensive Testing (All Layers)

**Test Coverage Target:** 80%+

### Backend Testing

**1. Unit Tests (pytest):**

**Test ML Functions:**
```python
# backend/tests/test_ml/test_forecasting.py
import pandas as pd
from ml.forecasting import run_prophet_forecast, run_arima_forecast, forecast_category_demand

def test_prophet_forecast():
    # Load fixture data
    historical_sales = pd.read_csv('tests/fixtures/mock_historical_sales.csv')

    # Run forecast
    total = run_prophet_forecast(historical_sales, weeks=12)

    # Assertions
    assert total > 0, "Forecast should be positive"
    assert total < 100000, "Forecast should be reasonable"

def test_ensemble_forecast():
    historical_sales = pd.read_csv('tests/fixtures/mock_historical_sales.csv')

    result = forecast_category_demand(historical_sales, weeks=12)

    assert result['total_season_demand'] > 0
    assert result['forecasting_method'] == 'ensemble_prophet_arima'
    assert 'prophet_forecast' in result
    assert 'arima_forecast' in result
    # Ensemble should be average of both
    assert result['total_season_demand'] == (result['prophet_forecast'] + result['arima_forecast']) // 2
```

**Test Agent Logic:**
```python
# backend/tests/test_agents/test_demand_agent.py
from agents.demand_agent import demand_agent

def test_demand_agent_forecast():
    # Mock input
    input_data = {
        "category_id": "womens_dresses",
        "historical_sales_csv": "tests/fixtures/mock_historical_sales.csv"
    }

    # Run agent
    result = demand_agent.run(input_data)

    # Assertions
    assert 'total_season_demand' in result
    assert result['total_season_demand'] > 0
    assert 'cluster_distribution' in result
```

**2. Integration Tests:**

**Test Full Workflow:**
```python
# backend/tests/test_api/test_workflows.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_forecast_workflow_e2e():
    # Start workflow
    response = client.post('/api/workflows/forecast', json={
        "category_id": "womens_dresses",
        "season": "spring_2025",
        "season_start_date": "2025-03-01",
        "season_end_date": "2025-05-23",
        "season_length_weeks": 12
    })

    assert response.status_code == 200
    workflow_id = response.json()['workflow_id']

    # Poll status until complete
    import time
    for _ in range(30):
        status_response = client.get(f'/api/workflows/{workflow_id}/status')
        if status_response.json()['status'] == 'completed':
            break
        time.sleep(1)

    # Verify forecast created
    forecast_response = client.get('/api/forecasts')
    forecasts = forecast_response.json()['forecasts']
    assert len(forecasts) > 0
    assert forecasts[0]['season'] == 'Spring 2025'
```

### Frontend Testing

**1. Component Tests (Vitest + React Testing Library):**

```typescript
// frontend/tests/components/AgentProgressBar.test.tsx
import { render, screen } from '@testing-library/react';
import { AgentProgressBar } from '@/components/AgentProgressBar';

describe('AgentProgressBar', () => {
  it('renders agent steps', () => {
    const updates = [
      { type: 'agent_started', agent: 'Demand Agent' },
      { type: 'agent_completed', agent: 'Demand Agent' },
      { type: 'agent_started', agent: 'Inventory Agent' }
    ];

    render(<AgentProgressBar updates={updates} />);

    expect(screen.getByText('Demand Agent')).toBeInTheDocument();
    expect(screen.getByText('✅ Complete')).toBeInTheDocument();
    expect(screen.getByText('Inventory Agent')).toBeInTheDocument();
    expect(screen.getByText('🔄 Running')).toBeInTheDocument();
  });
});
```

**2. E2E Tests (Playwright):**

```typescript
// frontend/tests/e2e/forecast-workflow.spec.ts
import { test, expect } from '@playwright/test';

test('complete forecast workflow', async ({ page }) => {
  // Navigate to dashboard
  await page.goto('http://localhost:5173');

  // Click "Generate Forecast"
  await page.click('button:has-text("Generate Forecast")');

  // Fill forecast form
  await page.fill('input[name="category"]', 'Women\'s Dresses');
  await page.fill('input[name="season"]', 'Spring 2025');
  await page.click('button:has-text("Start Workflow")');

  // Wait for agent progress to appear
  await expect(page.locator('text=Demand Agent')).toBeVisible({ timeout: 10000 });

  // Wait for human approval modal
  await expect(page.locator('text=Approval Required')).toBeVisible({ timeout: 60000 });

  // Click "Accept"
  await page.click('button:has-text("Accept")');

  // Wait for workflow completion
  await expect(page.locator('text=Workflow Complete')).toBeVisible({ timeout: 60000 });

  // Verify forecast displayed
  await expect(page.locator('text=Total Season Demand: 8,000')).toBeVisible();
});
```

### Test Data

**Fixtures (backend/tests/fixtures/):**
- `mock_historical_sales.csv` - 2 years of historical sales
- `mock_stores.csv` - 50 stores with attributes
- `mock_forecast.json` - Sample forecast object

### Running Tests

```bash
# Backend unit tests
cd backend
uv run pytest

# Backend with coverage
uv run pytest --cov=. --cov-report=html

# Frontend component tests
cd frontend
npm run test

# Frontend E2E tests
npm run test:e2e

# Run all tests
npm run test:all
```

---

## 19. Security

### Local Development Security (Minimal)

**Approach:** MVP runs locally only, minimal security needed. Focus on preventing credential exposure.

### Security Measures

**1. Environment Variables:**
```bash
# .env file (NEVER commit to git)
AZURE_OPENAI_API_KEY=your_secret_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# .env.example (commit this template)
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

**.gitignore:**
```
# Environment variables
.env
.env.local

# Database
*.db

# Python
__pycache__/
*.pyc

# Node
node_modules/
```

**2. CORS (Local Only):**
```python
# backend/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**3. No Authentication (Local Only):**
- No API keys
- No user login
- Only accessible on localhost

**4. API Key Protection (Server-Side Only):**
```python
# Good: API key stays on backend
from openai import AzureOpenAI
import os

azure_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # From .env, never sent to frontend
    api_version="2024-10-21",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Bad: Never expose API key to frontend
# response = {"api_key": os.getenv("AZURE_OPENAI_API_KEY")}  # ❌
```

**5. Data Privacy:**
- All data stored locally (SQLite file on your machine)
- No external data transmission (except Azure OpenAI API calls)
- Mock data only (no real customer/sales data)

### Security Checklist

- ✅ `.env` file gitignored
- ✅ `.env.example` template committed
- ✅ CORS restricted to localhost:5173
- ✅ Azure OpenAI API key server-side only (never exposed to frontend)
- ✅ SQLite database file gitignored
- ✅ No authentication (local MVP only)
- ✅ No HTTPS (HTTP sufficient for localhost)

### Post-MVP Security (Future)

**If deploying to cloud or sharing with others:**
- [ ] Add API key authentication (shared key or JWT)
- [ ] Enable HTTPS (TLS certificates)
- [ ] Add user roles (admin, merchandiser, viewer)
- [ ] Use Azure Key Vault for secrets
- [ ] Add rate limiting
- [ ] Enable audit logging (track all user actions)

---

## 20. Validation Checklist

### Architecture Completeness ✅

**Business Requirements:**
- ✅ Category-level forecasting (Prophet + ARIMA ensemble)
- ✅ Hierarchical allocation (Category → Cluster → Store)
- ✅ 3-agent system (Demand, Inventory, Pricing)
- ✅ Orchestrator coordination
- ✅ Week 6 markdown checkpoint (60% sell-through target)
- ✅ Variance-triggered re-forecast (>20% threshold)
- ✅ Human-in-the-loop approvals (Modify/Accept, no Reject)
- ✅ Archetype 1 parameters (12 weeks, 55/45 split, 20% safety stock)

**Technical Stack:**
- ✅ Backend: Python 3.11+ + FastAPI + OpenAI Agents SDK + UV
- ✅ Frontend: React 18 + TypeScript + Vite + Shadcn/ui + TanStack Query
- ✅ Database: SQLite (hybrid schema: normalized entities + JSON arrays)
- ✅ LLM: Azure OpenAI Service (gpt-4o-mini via Responses API)
- ✅ ML: Prophet, ARIMA (pmdarima), scikit-learn (K-means)

**Data Architecture:**
- ✅ Pydantic models defined (Category, Store, Forecast, Allocation, Markdown)
- ✅ Database schema (10 tables, hybrid normalized + JSON)
- ✅ Mock data strategy (CSV uploads for historical sales)
- ✅ Weekly sales upload mechanism (variance auto-check)

**Agent Architecture:**
- ✅ Demand Agent: Ensemble forecasting, K-means clustering (7 features), allocation factors
- ✅ Inventory Agent: Manufacturing (20% safety stock), 55/45 allocation, simple replenishment
- ✅ Pricing Agent: Gap × elasticity markdown formula, uniform across clusters
- ✅ Orchestrator: Sequential handoffs, context-rich (pass objects), dynamic enabling (variance trigger)
- ✅ Sessions + Guardrails (output validation)

**API & Integration:**
- ✅ REST API (hybrid: workflows + resources)
- ✅ WebSocket (real-time agent updates)
- ✅ Frontend flow (agent visualization + approval modals)
- ✅ Human-in-the-loop (Modify iterative, Accept approve, no Reject)

**Development & Deployment:**
- ✅ Source tree (backend/frontend monorepo)
- ✅ Local setup (UV + npm, no Docker)
- ✅ Environment variables (.env template)

**Quality & Standards:**
- ✅ Error handling (fail fast, clear messages)
- ✅ Coding standards (Ruff + mypy, ESLint + Prettier, TypeScript strict)
- ✅ Test strategy (comprehensive: unit + integration + component + E2E)
- ✅ Security (local only, .env gitignored, API key server-side)

**Workflows Documented:**
- ✅ Pre-season forecast generation (Week -12)
- ✅ In-season variance monitoring + re-forecast (>20% variance)
- ✅ Week 6 markdown evaluation (gap × elasticity formula)
- ✅ Human approval flows (Modify/Accept)

### Key Decisions Summary

| Decision Point | Choice | Rationale |
|---------------|--------|-----------|
| **Framework** | OpenAI Agents SDK + UV | Production-ready agents SDK, 10-100x faster package manager |
| **Architecture** | Monorepo (backend + frontend) | Solo dev, faster iteration, atomic commits |
| **LLM** | Azure OpenAI (gpt-4o-mini) | Cost-effective ($5 budget), Responses API support |
| **Forecasting** | Prophet + ARIMA ensemble | Parallel execution, simple average, no confidence scoring |
| **Clustering** | K-means (K=3, 7 features) | Research-backed features (historical sales most important) |
| **Allocation** | 70% historical + 30% attributes | Balance past performance with store potential |
| **Safety Stock** | Fixed 20% | Simple, not variable (no confidence intervals) |
| **Initial Split** | 55% stores, 45% holdback | 2-week minimum per store |
| **Replenishment** | Simple formula (forecast - inventory) | No adaptive adjustments, rely on re-forecast |
| **Markdown** | Gap × elasticity (elasticity=2.0) | Tunable parameter, 5% rounding, 40% cap |
| **Markdown Strategy** | Uniform across clusters | No cluster differentiation for MVP |
| **Handoffs** | Context-rich + dynamic enabling | Pass objects directly, enable re-forecast at variance trigger |
| **API** | Hybrid (workflows + resources) | Orchestrator primary, resource endpoints for flexibility |
| **Frontend** | WebSocket real-time updates | Instant agent progress, better UX than polling |
| **Human Approval** | Modify/Accept (no Reject) | Iterative refinement, no workflow termination |
| **Database** | Hybrid (normalized + JSON) | Normalize entities, JSON for arrays |
| **Infrastructure** | Local only (no Docker) | Simplest for MVP, UV + npm |
| **Error Handling** | Fail fast | Clear errors, no retry, user restarts |
| **Testing** | Comprehensive (80%+ coverage) | Unit + integration + component + E2E |
| **Security** | Local only (minimal) | .env gitignored, API key server-side |

---

## Next Steps

### Implementation Phases

**Phase 1: Backend Foundation (Week 1-2)**
1. Set up project structure (UV + FastAPI)
2. Implement Pydantic models
3. Create database schema + migrations
4. Seed mock data (50 stores, 3 clusters, historical sales)
5. Implement ML functions (Prophet, ARIMA, K-means)

**Phase 2: Agent Implementation (Week 3-4)**
6. Implement Demand Agent (forecasting + clustering)
7. Implement Inventory Agent (manufacturing + allocation)
8. Implement Pricing Agent (markdown calculation)
9. Implement Orchestrator (handoffs, variance monitoring)
10. Test agent workflows

**Phase 3: API & Integration (Week 5-6)**
11. Implement REST API endpoints
12. Implement WebSocket handler
13. Test API with Postman/curl
14. Write backend integration tests

**Phase 4: Frontend (Week 7-8)**
15. Set up React + Vite + Shadcn/ui
16. Implement agent progress visualization
17. Implement approval modals (Modify/Accept)
18. Implement weekly sales upload
19. Implement dashboard (forecast charts, allocation table)

**Phase 5: Testing & Validation (Week 9-10)**
20. Write unit tests (80%+ coverage)
21. Write E2E tests (Playwright)
22. Validate with mock dataset (MAPE <20%)
23. Hindcast validation (use historical data to test accuracy)
24. User acceptance testing (demo to stakeholders)

---

## Document Metadata

**Author:** Winston (Architect Agent)
**Created:** 2025-10-12
**Last Updated:** 2025-10-12
**Version:** 1.0
**Status:** Complete - Ready for Implementation

**Source Documents:**
- Product Brief v3.1 (`docs/04_PoC_Development/product_brief/product_brief_v3.1.md`)
- Operational Workflow v3 (`docs/04_PoC_Development/product_brief/3_operational_workflow.md`)

**Related Documents:**
- Next Steps Plan (`docs/04_PoC_Development/next_steps_plan.md`)
- Agent Coordination Workflow (`docs/04_PoC_Development/Architecture/agent_coordination_workflow.md`)

**Approval:**
- [x] All architectural decisions finalized
- [x] All ML approaches defined
- [x] All API specifications complete
- [x] All workflows documented
- [x] Validation checklist passed

---

**Ready for Implementation!** 🚀
