# System Architecture Document
**Demand Forecasting & Inventory Allocation System**

**Version:** 1.0
**Date:** 2025-10-10
**Status:** MVP Architecture
**Archetype Focus:** Archetype 2 - Stable Catalog Retail

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Architecture Principles](#3-architecture-principles)
4. [System Context](#4-system-context)
5. [High-Level Architecture](#5-high-level-architecture)
6. [Component Architecture](#6-component-architecture)
7. [Data Architecture](#7-data-architecture)
8. [Agent Architecture](#8-agent-architecture)
9. [Integration Architecture](#9-integration-architecture)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Security Architecture](#11-security-architecture)
12. [Performance & Scalability](#12-performance--scalability)
13. [Technology Stack](#13-technology-stack)
14. [Development Approach](#14-development-approach)
15. [Appendices](#15-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

This document defines the technical architecture for a **3-agent demand forecasting and inventory allocation system** designed to predict store-week granular demand and optimize inventory decisions for retail operations. The system addresses critical pain points identified through user research: inaccurate forecasting, location-specific allocation failures, and late markdown decisions causing margin loss.

### 1.2 Scope

**MVP Scope:**
- **Archetype**: Stable Catalog Retail (furniture, 26-week season)
- **Scale**: 50 stores, 50 SKUs per season
- **Agents**: 3 specialized agents (Demand, Inventory, Pricing) + 1 Orchestrator
- **Deployment**: Local development machine (single-user)
- **Budget**: <$5 total cost (academic MVP)

**Future Scope** (Post-MVP):
- Multi-archetype support (Fashion, CPG)
- Cloud deployment for production scale
- Real-time integration with retail systems
- Advanced ML models and ensemble methods

### 1.3 Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Architecture Pattern** | Multi-Agent System with Central Orchestrator | Enables modular, autonomous decision-making with coordinated workflows |
| **Agent Framework** | LangChain with OpenAI LLMs (gpt-4o-mini) | Cost-efficient ($0.15/1M tokens), mature framework, good documentation |
| **Forecasting Approach** | Adaptive Hybrid (Rule-based + ML + LLM reasoning) | Balances accuracy, explainability, and cost |
| **Data Storage** | SQLite + CSV/Parquet files | Local, zero-cost, sufficient for MVP scale |
| **Deployment Model** | Local CLI application | Academic project, single-user, no cloud infrastructure needed |
| **Parameter Management** | YAML-based configuration | Enables generic architecture across retail archetypes |
| **Programming Language** | Python 3.9+ | Rich ML/data science ecosystem, LangChain compatibility |

---

## 2. System Overview

### 2.1 System Vision

A **parameter-driven, agentic forecasting system** that:
- Predicts demand at store-week granularity (e.g., 50 stores × 26 weeks = 1,300 predictions per SKU)
- Autonomously decides manufacturing quantities, store allocations, and markdown timing
- Adapts to different retail archetypes through configuration (not code changes)
- Provides transparent, explainable recommendations with natural language reasoning

### 2.2 Core Problem Statement

Retailers face inventory allocation challenges due to:
- **Inaccurate demand forecasting** (PP-001): Traditional ML models lack accuracy for new products
- **Location-specific allocation failures** (PP-002, PP-015): Store-level demand patterns not captured
- **Late markdown decisions** (PP-016): Data lag causes $500K annual margin loss
- **Inventory optimization balance** (PP-028): Trade-off between overstock and understock

### 2.3 Solution Approach

**Single Core Prediction**: `demand_by_store_by_week` matrix
**7 Automated Decisions**:
1. Manufacturing order quantity (pre-season, 3 months before)
2. Initial store allocation (week 0, first 2 weeks)
3. Bi-weekly replenishment quantities (weeks 1-26)
4. Emergency re-forecast trigger (if variance >15%)
5. Markdown trigger (week 12 checkpoint, <50% sell-through)
6. Updated forecast post-markdown (weeks 13-26)
7. Model improvements for next season (post-season)

---

## 3. Architecture Principles

### 3.1 Design Principles

#### 3.1.1 Modularity & Separation of Concerns
- Each agent has a single, well-defined responsibility
- Agents are independently testable and replaceable
- Orchestrator manages coordination, agents focus on domain logic

#### 3.1.2 Parameter-Driven Behavior
- System behavior adapts via YAML configuration, not code changes
- Same architecture serves multiple retail archetypes (Fashion, Furniture, CPG)
- Parameters control: season length, replenishment cadence, markdown triggers, holdback percentages

#### 3.1.3 Explainability & Transparency
- All agent decisions include natural language reasoning (LLM-powered)
- Users can review similar-items used, forecasting methods applied
- Confidence scores indicate forecast reliability

#### 3.1.4 Cost Efficiency
- Minimize LLM API calls (use only for reasoning, not computation)
- Cache embeddings to avoid repeated API costs
- Use open-source libraries for forecasting computation (statsmodels, Prophet)
- Total MVP budget: <$5

#### 3.1.5 Pragmatic Over Perfect
- MVP prioritizes working end-to-end system over advanced ML
- Use rule-based methods where appropriate (e.g., safety stock calculation)
- Defer optimization until validation proves value

### 3.2 Quality Attributes

| Attribute | Target | Measurement |
|-----------|--------|-------------|
| **Accuracy** | MAPE <20% | Hindcast validation on 26-week season |
| **Performance** | Initial forecast <4 hours, updates <30 min | Runtime measurement |
| **Maintainability** | Generic architecture, extensible to other archetypes | Code review, parameter configurability |
| **Usability** | CLI interface, YAML configuration | User testing with demand planners |
| **Cost** | <$5 total (LLM API + infrastructure) | Budget tracking |
| **Reliability** | 95%+ SKUs successfully forecasted | Error rate monitoring |

### 3.3 Non-Goals (MVP)

- Real-time forecasting (<1 min latency)
- Multi-user concurrent access
- Web UI or dashboard
- Integration with retail ERP/WMS systems
- Deep learning / neural network models
- Multi-season overlap handling
- Store-to-store transfer optimization

---

## 4. System Context

### 4.1 Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│  Historical  │    │  Product         │    │  Store       │
│  Sales Data  │    │  Catalog         │    │  Attributes  │
│  (CSV)       │    │  (CSV)           │    │  (CSV)       │
└──────┬───────┘    └────────┬─────────┘    └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  DEMAND FORECASTING & INVENTORY ALLOCATION SYSTEM   │
        │  ┌───────────────────────────────────────────────┐  │
        │  │           ORCHESTRATOR                        │  │
        │  ├───────────────────────────────────────────────┤  │
        │  │  Demand Agent  │  Inventory  │  Pricing Agent │  │
        │  │                │  Agent      │                │  │
        │  └───────────────────────────────────────────────┘  │
        └──────────────────────┬──────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────────┐
        │                      │                          │
        ▼                      ▼                          ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│  Forecast    │    │  Manufacturing   │    │  Markdown    │
│  Output      │    │  Orders          │    │  Recommendations│
│  (JSON/CSV)  │    │  (CSV)           │    │  (JSON)      │
└──────────────┘    └──────────────────┘    └──────────────┘
        │                      │                          │
        └──────────────────────┼──────────────────────────┘
                               ▼
                    ┌──────────────────┐
                    │  Demand Planner  │
                    │  (Human User)    │
                    └──────────────────┘
```

### 4.2 User Personas

#### Primary User: Demand Planner
- **Inputs**: New SKU attributes, season configuration
- **Outputs**: Manufacturing order recommendations, allocation plans
- **Interactions**: CLI commands, YAML configuration, CSV file review

#### Secondary User: Merchandiser
- **Inputs**: Sell-through checkpoint review
- **Outputs**: Markdown recommendations
- **Interactions**: Performance dashboard (future), CSV reports

#### Secondary User: Operations Manager
- **Inputs**: Current inventory levels
- **Outputs**: Bi-weekly replenishment plans
- **Interactions**: CSV exports for WMS integration

### 4.3 External System Interfaces

| System | Direction | Format | Frequency | Purpose |
|--------|-----------|--------|-----------|---------|
| **Historical Sales DB** | Input | CSV | Once (pre-season) | Training data for forecasting |
| **Product Catalog** | Input | CSV | Once (pre-season) | SKU attributes for similarity matching |
| **Store Attributes** | Input | CSV | Once (pre-season) | Store clustering, allocation logic |
| **Actual Sales Feed** | Input | CSV | Bi-weekly | Forecast updates, variance detection |
| **Forecast Output** | Output | JSON/CSV | Multiple times/season | Manufacturing, allocation decisions |
| **OpenAI API** | External Service | REST API | Per forecast | LLM reasoning, embeddings |

---

## 5. High-Level Architecture

### 5.1 Architectural Pattern: Multi-Agent System

**Pattern Choice**: **Orchestrated Multi-Agent System**

**Why This Pattern:**
- **Modularity**: Each agent is independently developed, tested, and replaced
- **Autonomy**: Agents make domain-specific decisions (demand, inventory, pricing)
- **Coordination**: Central orchestrator manages workflow, prevents agent conflicts
- **Explainability**: Agents provide reasoning for decisions (LLM-powered)

**Pattern Diagram:**

```
┌────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                            │
│  Responsibilities:                                             │
│  • Workflow coordination (5 phases)                            │
│  • Trigger management (time-based + event-based)               │
│  • Data passing between agents                                 │
│  • Performance monitoring (MAPE, bias, confidence)             │
│  • Human-in-the-loop alerts                                    │
└────────────────┬───────────────────────────────────────────────┘
                 │
        ┌────────┴────────┬──────────────────┬──────────────────┐
        │                 │                  │                  │
        ▼                 ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   DEMAND     │  │  INVENTORY   │  │   PRICING    │  │   CONFIG     │
│   AGENT      │  │   AGENT      │  │   AGENT      │  │   MANAGER    │
├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
│• Similar-item│  │• Mfg order   │  │• Sell-through│  │• YAML config │
│  matching    │  │  calculation │  │  monitoring  │  │• Archetype   │
│• Forecast    │  │• Store       │  │• Markdown    │  │  parameters  │
│  generation  │  │  allocation  │  │  trigger     │  │• Validation  │
│• Confidence  │  │• Bi-weekly   │  │• Depth       │  │              │
│  scoring     │  │  replenishment│ │  calculation │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │                  │
       └─────────────────┴──────────────────┴──────────────────┘
                                  │
                                  ▼
                ┌──────────────────────────────────────┐
                │          DATA LAYER                  │
                ├──────────────────────────────────────┤
                │ • Historical sales (SQLite)          │
                │ • Product catalog (SQLite)           │
                │ • Store attributes (SQLite)          │
                │ • Forecast cache (Parquet)           │
                │ • Performance metrics (CSV)          │
                └──────────────────────────────────────┘
```

### 5.2 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  • CLI Interface (Typer)                                        │
│  • YAML Configuration Loader                                    │
│  • CSV/JSON Output Writers                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION LAYER                             │
│  • Workflow State Machine                                       │
│  • Agent Invocation Manager                                     │
│  • Event Trigger System                                         │
│  • Performance Monitor                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Demand Agent │  │ Inventory    │  │ Pricing      │         │
│  │              │  │ Agent        │  │ Agent        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                │
│  • Similar-Item Matching Service                                │
│  • Time-Series Forecasting Service                              │
│  • Optimization Service (Linear Programming)                    │
│  • LLM Reasoning Service (OpenAI)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                  │
│  • Historical Sales Repository                                  │
│  • Product Catalog Repository                                   │
│  • Forecast Cache Repository                                    │
│  • Configuration Repository                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Component Architecture

### 6.1 Orchestrator Component

**Responsibilities:**
- Coordinate 3 agents through 5-phase seasonal workflow
- Manage workflow state (current week, forecasts, actuals, performance)
- Trigger agents based on time (bi-weekly) or events (variance >15%)
- Pass data between agents (demand forecast → inventory allocation)
- Monitor performance (MAPE, bias, confidence calibration)
- Alert users for low confidence (<70%) or high variance (>15%)

**Key Interfaces:**

```python
class Orchestrator:
    def __init__(self, config: Config, agents: Dict[str, Agent]):
        self.config = config
        self.demand_agent = agents['demand']
        self.inventory_agent = agents['inventory']
        self.pricing_agent = agents['pricing']
        self.state = WorkflowState()

    def execute_phase_1_pre_season(self, skus: List[SKU]) -> Phase1Output:
        """Pre-season planning: Forecast + Manufacturing order"""

    def execute_phase_2_initial_allocation(self) -> Phase2Output:
        """Week 0: Initial store allocation"""

    def execute_phase_3_in_season(self, current_week: int) -> Phase3Output:
        """Bi-weekly: Replenishment planning"""

    def execute_phase_4_mid_season_pricing(self) -> Phase4Output:
        """Week 12: Markdown checkpoint"""

    def execute_phase_5_season_end(self) -> Phase5Output:
        """Post-season: Performance analysis"""

    def detect_variance(self, actual: float, forecast: float) -> bool:
        """Check if variance exceeds threshold"""

    def alert_user(self, message: str, severity: AlertSeverity):
        """Send alert to user"""
```

**State Management:**

```python
@dataclass
class WorkflowState:
    current_week: int
    season_length: int
    forecasts: Dict[str, ForecastOutput]  # SKU → forecast
    actuals: Dict[str, List[float]]  # SKU → weekly actuals
    inventory_plans: Dict[str, InventoryPlan]
    pricing_decisions: Dict[str, PricingDecision]
    performance_metrics: PerformanceMetrics
    next_trigger: Trigger
```

---

### 6.2 Demand Agent Component

**Responsibilities:**
- Accept SKU attributes (style, color, material, price)
- Find top 5-10 similar historical SKUs using embeddings
- Generate `demand_by_store_by_week` matrix (50 stores × 26 weeks)
- Calculate confidence score (0-100%)
- Adaptively select forecasting method (ARIMA, Prophet, hybrid)
- Re-forecast based on actual sales (bi-weekly or variance-triggered)

**Key Interfaces:**

```python
class DemandAgent:
    def __init__(self, llm_client: OpenAI, config: Config):
        self.llm_client = llm_client
        self.config = config
        self.similarity_service = SimilarityMatchingService()
        self.forecasting_service = TimeSeriesForecastingService()

    def forecast_demand(self, sku: SKU, historical_data: pd.DataFrame) -> ForecastOutput:
        """Generate demand forecast for a single SKU"""

    def find_similar_items(self, sku: SKU, catalog: pd.DataFrame) -> List[SimilarItem]:
        """Find top 5-10 similar historical SKUs"""

    def calculate_confidence(self, similar_items: List[SimilarItem],
                           data_availability: DataAvailability) -> float:
        """Calculate forecast confidence score"""

    def select_forecasting_method(self, sku: SKU,
                                 similar_items: List[SimilarItem]) -> ForecastMethod:
        """Adaptively choose ARIMA, Prophet, or hybrid"""

    def disaggregate_to_stores(self, total_demand: List[float],
                              stores: List[Store]) -> np.ndarray:
        """Split total demand across 50 stores"""
```

**Data Flow:**

```
Input (SKU) → Find Similar Items → Select Method → Generate Forecast →
Disaggregate to Stores → Calculate Confidence → Output (demand_by_store_by_week)
```

**ML Methods:**

| Method | When to Use | Library | Complexity |
|--------|------------|---------|-----------|
| **OpenAI Embeddings** | Similar-item matching | openai | Simple API |
| **Prophet** | New SKUs (<6 months data) | fbprophet | Simple |
| **ARIMA/SARIMA** | Existing SKUs (1+ years) | statsmodels | Medium |
| **Hybrid** | Mix historical + similarity | Custom | Medium |

---

### 6.3 Inventory Agent Component

**Responsibilities:**
- Calculate manufacturing order (total demand + 15% safety stock)
- Allocate first 2 weeks demand to stores (week 0)
- Maintain 60-70% inventory at DC (holdback strategy)
- Generate bi-weekly replenishment plans (weeks 1-26)
- Balance inventory across stores based on forecast + actuals

**Key Interfaces:**

```python
class InventoryAgent:
    def __init__(self, config: Config):
        self.config = config
        self.optimization_service = InventoryOptimizationService()

    def calculate_manufacturing_order(self, forecast: ForecastOutput) -> int:
        """Total demand + safety stock"""

    def allocate_initial_inventory(self, forecast: ForecastOutput,
                                   stores: List[Store]) -> Dict[str, int]:
        """Week 0: First 2 weeks to each store"""

    def calculate_dc_holdback(self, total_order: int,
                             allocated: int) -> int:
        """Inventory held at DC (60-70%)"""

    def plan_replenishment(self, current_inventory: Dict[str, int],
                          forecast: ForecastOutput,
                          current_week: int) -> ReplenishmentPlan:
        """Bi-weekly replenishment quantities"""

    def optimize_allocation(self, stores: List[Store],
                           demand: np.ndarray) -> Dict[str, int]:
        """Optimize allocation across stores (future: linear programming)"""
```

**Decision Logic:**

```python
# Manufacturing Order
manufacturing_order = sum(demand_by_store_by_week) * (1 + safety_stock_pct)

# Initial Allocation (Week 0)
for store in stores:
    allocation[store] = sum(demand_by_store_by_week[store][0:2]) * 1.10

# DC Holdback
dc_holdback = manufacturing_order - sum(allocation.values())
assert dc_holdback >= 0.60 * manufacturing_order  # Archetype 2 constraint

# Bi-weekly Replenishment
for store in stores:
    target_inventory = demand_by_store_by_week[store][week:week+2]
    current_inventory = get_inventory(store)
    replenishment = max(0, target_inventory - current_inventory)
```

---

### 6.4 Pricing Agent Component

**Responsibilities:**
- Monitor sell-through % at Week 12 checkpoint
- Detect underperformance (<50% sell-through for Archetype 2)
- Recommend markdown depth (10%, 20%, 30%)
- Trigger Demand Agent re-forecast with price elasticity
- Provide natural language explanation for recommendations

**Key Interfaces:**

```python
class PricingAgent:
    def __init__(self, llm_client: OpenAI, config: Config):
        self.llm_client = llm_client
        self.config = config

    def monitor_sell_through(self, actuals: List[float],
                            manufacturing_order: int,
                            current_week: int) -> float:
        """Calculate sell-through %"""

    def recommend_markdown(self, sell_through: float,
                          current_week: int) -> MarkdownRecommendation:
        """Check if markdown needed"""

    def calculate_markdown_depth(self, sell_through: float,
                                remaining_weeks: int) -> float:
        """Determine 10%, 20%, or 30% markdown"""

    def estimate_demand_lift(self, markdown_depth: float) -> float:
        """Predict demand increase from markdown"""

    def explain_recommendation(self, recommendation: MarkdownRecommendation) -> str:
        """LLM-powered natural language explanation"""
```

**Decision Rules:**

```python
# Sell-Through Monitoring (Week 12)
sell_through = cumulative_sales / manufacturing_order

# Markdown Trigger
if sell_through < markdown_threshold:  # 50% for Archetype 2
    gap = markdown_threshold - sell_through

    # Markdown Depth
    if gap < 0.05:
        markdown_depth = 0.10  # 10% off
    elif gap < 0.15:
        markdown_depth = 0.20  # 20% off
    else:
        markdown_depth = 0.30  # 30% off

    # Demand Lift Estimation
    demand_lift = markdown_depth * elasticity_factor  # e.g., 0.20 * 0.5 = 10% lift

    # Trigger re-forecast
    updated_forecast = demand_forecast * (1 + demand_lift)
```

---

### 6.5 Configuration Manager Component

**Responsibilities:**
- Load and validate YAML configuration
- Provide archetype-specific parameters to agents
- Support parameter overrides for testing
- Validate parameter constraints (e.g., holdback_pct ∈ [0.5, 0.8])

**Configuration Schema:**

```yaml
# config_archetype2.yaml
archetype:
  name: "stable_catalog"
  description: "Furniture retail, 26-week season"

season:
  length_weeks: 26
  start_date: "2025-10-01"

forecasting:
  prediction_horizon_weeks: 26
  update_cadence: "bi-weekly"
  variance_threshold: 0.15  # 15%
  confidence_threshold: 0.70  # 70%
  similar_items_count: 10

inventory:
  safety_stock_pct: 0.15  # 15%
  holdback_pct: 0.65  # 65%
  replenishment_cadence: "bi-weekly"

pricing:
  markdown_trigger_week: 12
  markdown_threshold: 0.50  # 50% sell-through
  markdown_depths: [0.10, 0.20, 0.30]
  elasticity_factor: 0.50  # 20% markdown → 10% demand lift

stores:
  count: 50

skus:
  count: 50

llm:
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 500
```

---

## 7. Data Architecture

### 7.1 Data Models

#### 7.1.1 Core Entities

**SKU (Stock Keeping Unit)**

```python
@dataclass
class SKU:
    sku_id: str
    name: str
    category: str  # e.g., "Sofas"
    style: str  # e.g., "Mid-Century"
    color: str  # e.g., "Charcoal"
    material: str  # e.g., "Fabric"
    dimensions: str  # e.g., "84W x 36D x 32H"
    price: float  # e.g., 1299.00
    cost: float  # e.g., 649.50
    launch_date: date
    is_new_product: bool
    attributes: Dict[str, Any]  # Flexible attributes
```

**Store**

```python
@dataclass
class Store:
    store_id: str
    name: str
    cluster: str  # "A", "B", or "C"
    region: str  # e.g., "Northeast"
    size_sqft: int
    location_type: str  # "urban", "suburban", "rural"
    demographics: Dict[str, Any]
    capacity_units: int
    historical_performance: Dict[str, float]
```

**ForecastOutput**

```python
@dataclass
class ForecastOutput:
    sku_id: str
    forecast_date: datetime
    demand_by_store_by_week: np.ndarray  # Shape: (50 stores, 26 weeks)
    confidence_score: float  # 0-100
    method_used: str  # "ARIMA", "Prophet", "Hybrid"
    similar_items_used: List[SimilarItem]
    metadata: Dict[str, Any]
```

**InventoryPlan**

```python
@dataclass
class InventoryPlan:
    sku_id: str
    manufacturing_order: int
    initial_allocation: Dict[str, int]  # store_id → quantity
    dc_holdback: int
    replenishment_schedule: Dict[int, Dict[str, int]]  # week → {store_id → qty}
```

**MarkdownRecommendation**

```python
@dataclass
class MarkdownRecommendation:
    sku_id: str
    week: int
    sell_through_actual: float
    sell_through_target: float
    markdown_needed: bool
    markdown_depth: float  # 0.10, 0.20, or 0.30
    reasoning: str
    expected_demand_lift: float
```

#### 7.1.2 Database Schema

**SQLite Tables:**

```sql
-- Historical Sales
CREATE TABLE historical_sales (
    sale_id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    sku_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    quantity_sold INTEGER NOT NULL,
    revenue REAL NOT NULL,
    FOREIGN KEY (sku_id) REFERENCES products(sku_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

CREATE INDEX idx_sales_date ON historical_sales(date);
CREATE INDEX idx_sales_sku ON historical_sales(sku_id);
CREATE INDEX idx_sales_store ON historical_sales(store_id);

-- Products
CREATE TABLE products (
    sku_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    style TEXT,
    color TEXT,
    material TEXT,
    dimensions TEXT,
    price REAL NOT NULL,
    cost REAL,
    launch_date DATE,
    is_new_product BOOLEAN,
    attributes_json TEXT  -- JSON blob for flexible attributes
);

-- Stores
CREATE TABLE stores (
    store_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cluster TEXT NOT NULL,
    region TEXT,
    size_sqft INTEGER,
    location_type TEXT,
    capacity_units INTEGER,
    demographics_json TEXT,
    performance_json TEXT
);

-- Forecasts (Cache)
CREATE TABLE forecasts (
    forecast_id INTEGER PRIMARY KEY,
    sku_id TEXT NOT NULL,
    forecast_date DATETIME NOT NULL,
    confidence_score REAL,
    method_used TEXT,
    forecast_data_parquet TEXT,  -- Path to Parquet file
    metadata_json TEXT,
    FOREIGN KEY (sku_id) REFERENCES products(sku_id)
);

-- Performance Metrics
CREATE TABLE performance_metrics (
    metric_id INTEGER PRIMARY KEY,
    sku_id TEXT,
    week INT,
    mape REAL,
    bias REAL,
    actual_sales REAL,
    forecasted_sales REAL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 Data Flow

#### 7.2.1 Phase 1: Pre-Season Data Flow

```
Historical Sales CSV → Load to SQLite → Demand Agent Query
Product Catalog CSV → Load to SQLite → Demand Agent Query
Store Attributes CSV → Load to SQLite → Inventory Agent Query

Demand Agent → ForecastOutput → Save to Parquet + SQLite reference
ForecastOutput → Inventory Agent → InventoryPlan → Save to JSON
```

#### 7.2.2 Phase 3: In-Season Data Flow

```
Actual Sales CSV → Load to SQLite → Orchestrator Query
Orchestrator → Calculate Variance → Check Threshold

IF variance > 15%:
    Orchestrator → Demand Agent → Updated ForecastOutput → Update Parquet
    Updated ForecastOutput → Inventory Agent → Updated ReplenishmentPlan → Save JSON

Orchestrator → Update performance_metrics table (MAPE, bias)
```

### 7.3 Data Storage Strategy

| Data Type | Storage | Format | Rationale |
|-----------|---------|--------|-----------|
| **Historical Sales** | SQLite | Relational table | Queryable, indexed, <100MB |
| **Product Catalog** | SQLite | Relational table | Structured, frequent queries |
| **Store Attributes** | SQLite | Relational table | Structured, small dataset |
| **Forecast Matrices** | Parquet files | Binary columnar | Large (50×26 per SKU), efficient I/O |
| **Configuration** | YAML files | Text | Human-editable, version-controlled |
| **Output Reports** | CSV/JSON | Text | User-friendly, Excel-compatible |
| **LLM Cache** | JSON files | Text | Avoid repeated API calls |

### 7.4 Data Volumes (MVP)

| Dataset | Size | Growth |
|---------|------|--------|
| **Historical Sales** (2 years, 50 SKUs, 50 stores) | ~50 MB | Static (MVP) |
| **Product Catalog** (500 historical + 50 new) | ~1 MB | Grows per season |
| **Forecast Outputs** (50 SKUs × 1,300 values) | ~5 MB | Grows per season |
| **Performance Metrics** (26 weeks × 50 SKUs) | ~1 MB | Grows per season |
| **Total Storage** | ~60 MB | ~10 MB per season |

---

## 8. Agent Architecture

### 8.1 LangChain Agent Implementation

**Architecture Pattern**: LangChain Agents with Tool Calling

**Why LangChain:**
- Mature framework with strong OpenAI integration
- Built-in agent orchestration (ReAct, function calling)
- Tool abstraction for forecasting methods
- Conversation memory for multi-turn reasoning

**Agent Structure:**

```python
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

class DemandAgentLangChain:
    def __init__(self, config: Config):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        # Define tools (forecasting methods as tools)
        self.tools = [
            Tool(
                name="find_similar_items",
                func=self._find_similar_items,
                description="Find top 10 similar historical SKUs using embeddings"
            ),
            Tool(
                name="forecast_arima",
                func=self._forecast_arima,
                description="Use ARIMA for SKUs with 1+ years historical data"
            ),
            Tool(
                name="forecast_prophet",
                func=self._forecast_prophet,
                description="Use Prophet for SKUs with <6 months data"
            ),
            Tool(
                name="calculate_confidence",
                func=self._calculate_confidence,
                description="Calculate confidence score based on data quality"
            )
        ]

        # Initialize agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )

    def forecast_demand(self, sku: SKU) -> ForecastOutput:
        prompt = f"""
        Forecast demand for SKU: {sku.name}
        - Category: {sku.category}
        - Style: {sku.style}
        - Color: {sku.color}
        - Price: ${sku.price}
        - New Product: {sku.is_new_product}

        Steps:
        1. Use 'find_similar_items' to find top 10 similar SKUs
        2. Decide: Use 'forecast_arima' if historical data available,
           else 'forecast_prophet'
        3. Calculate confidence using 'calculate_confidence'
        4. Return forecast with reasoning
        """

        result = self.agent.run(prompt)
        return self._parse_result(result)
```

### 8.2 Agent Communication Protocol

**Message Format** (JSON):

```json
{
  "message_id": "msg-2025-10-10-001",
  "sender": "orchestrator",
  "recipient": "demand_agent",
  "timestamp": "2025-10-10T10:00:00Z",
  "action": "forecast_demand",
  "payload": {
    "sku_id": "SKU-12345",
    "sku_attributes": {
      "name": "Mid-Century Sofa - Charcoal",
      "category": "Sofas",
      "style": "Mid-Century",
      "color": "Charcoal",
      "price": 1299.00
    },
    "historical_data_path": "data/historical_sales.parquet"
  },
  "metadata": {
    "priority": "normal",
    "retry_count": 0
  }
}
```

**Response Format**:

```json
{
  "response_id": "resp-2025-10-10-001",
  "request_id": "msg-2025-10-10-001",
  "sender": "demand_agent",
  "recipient": "orchestrator",
  "timestamp": "2025-10-10T10:15:00Z",
  "status": "success",
  "payload": {
    "sku_id": "SKU-12345",
    "demand_by_store_by_week": "s3://forecasts/SKU-12345.parquet",
    "confidence_score": 0.82,
    "method_used": "hybrid_arima_similarity",
    "similar_items_used": [
      {"sku_id": "SKU-11234", "similarity": 0.92},
      {"sku_id": "SKU-10987", "similarity": 0.88}
    ],
    "reasoning": "Used ARIMA for base forecast (18 months data available). Adjusted -5% based on similar-item analysis showing charcoal underperforms vs beige by 5-8%."
  },
  "metadata": {
    "execution_time_seconds": 892,
    "api_cost_usd": 0.0003
  }
}
```

### 8.3 Agent State Management

Each agent maintains internal state during execution:

```python
@dataclass
class DemandAgentState:
    current_sku: SKU
    historical_data: pd.DataFrame
    similar_items: List[SimilarItem]
    forecast_in_progress: bool
    method_selected: Optional[str]
    intermediate_results: Dict[str, Any]
```

**Orchestrator** maintains global state across all agents:

```python
@dataclass
class GlobalState:
    season_config: Config
    current_week: int
    all_forecasts: Dict[str, ForecastOutput]
    all_inventory_plans: Dict[str, InventoryPlan]
    all_pricing_decisions: Dict[str, MarkdownRecommendation]
    actuals: Dict[str, pd.DataFrame]
    performance_history: List[PerformanceMetrics]
```

---

## 9. Integration Architecture

### 9.1 External API Integration

#### 9.1.1 OpenAI API Integration

**Purpose**: LLM reasoning, embeddings for similarity matching

**Configuration**:

```python
from openai import OpenAI

class OpenAIClient:
    def __init__(self, config: Config):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = config.llm_model  # "gpt-4o-mini"
        self.embedding_model = "text-embedding-3-small"

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for SKU similarity"""
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    def chat_completion(self, messages: List[Dict]) -> str:
        """LLM reasoning for agent decisions"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate API cost"""
        input_cost = (prompt_tokens / 1_000_000) * 0.15  # $0.15/1M tokens
        output_cost = (completion_tokens / 1_000_000) * 0.60  # $0.60/1M tokens
        return input_cost + output_cost
```

**Rate Limiting & Caching**:

```python
from functools import lru_cache
import time

class CachedOpenAIClient(OpenAIClient):
    def __init__(self, config: Config):
        super().__init__(config)
        self.request_times = []

    @lru_cache(maxsize=1000)
    def get_embedding_cached(self, text: str) -> List[float]:
        """Cache embeddings to avoid repeated API calls"""
        return self.get_embedding(text)

    def rate_limit(self):
        """Enforce 60 requests/min limit"""
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        if len(self.request_times) >= 60:
            sleep_time = 60 - (now - self.request_times[0])
            time.sleep(sleep_time)
        self.request_times.append(now)
```

### 9.2 File System Integration

**Input File Processing**:

```python
class DataLoader:
    def load_historical_sales(self, csv_path: str) -> pd.DataFrame:
        """Load historical sales CSV into DataFrame"""
        df = pd.read_csv(csv_path, parse_dates=['date'])
        # Validation
        required_cols = ['date', 'sku_id', 'store_id', 'quantity_sold']
        assert all(col in df.columns for col in required_cols)
        return df

    def load_product_catalog(self, csv_path: str) -> pd.DataFrame:
        """Load product catalog CSV"""
        df = pd.read_csv(csv_path)
        required_cols = ['sku_id', 'name', 'category', 'price']
        assert all(col in df.columns for col in required_cols)
        return df

    def load_to_sqlite(self, df: pd.DataFrame, table_name: str, db_path: str):
        """Load DataFrame to SQLite"""
        import sqlite3
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
```

**Output File Export**:

```python
class OutputWriter:
    def write_forecast_csv(self, forecast: ForecastOutput, path: str):
        """Export forecast as CSV"""
        df = pd.DataFrame(
            forecast.demand_by_store_by_week,
            columns=[f"Week_{i+1}" for i in range(26)]
        )
        df.insert(0, 'Store_ID', [f"Store_{i+1}" for i in range(50)])
        df.to_csv(path, index=False)

    def write_forecast_json(self, forecast: ForecastOutput, path: str):
        """Export forecast as JSON"""
        output = {
            'sku_id': forecast.sku_id,
            'forecast_date': forecast.forecast_date.isoformat(),
            'confidence_score': forecast.confidence_score,
            'method_used': forecast.method_used,
            'demand_by_store_by_week': forecast.demand_by_store_by_week.tolist(),
            'similar_items': [asdict(item) for item in forecast.similar_items_used]
        }
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)
```

---

## 10. Deployment Architecture

### 10.1 MVP Deployment: Local Development Machine

**Target Environment**: Single-user, local execution on development machine

**System Requirements**:
- **OS**: Windows 10/11, macOS, or Linux
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8 GB minimum (16 GB recommended)
- **Storage**: 1 GB free space
- **Python**: 3.9+
- **Internet**: Required for OpenAI API calls

**Deployment Diagram**:

```
┌────────────────────────────────────────────────────────┐
│         LOCAL DEVELOPMENT MACHINE                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Python Virtual Environment (venv)            │    │
│  ├──────────────────────────────────────────────┤    │
│  │  • Python 3.9+                               │    │
│  │  • Dependencies (requirements.txt)           │    │
│  │    - langchain                               │    │
│  │    - openai                                  │    │
│  │    - pandas, numpy                           │    │
│  │    - statsmodels, prophet                    │    │
│  │    - typer (CLI)                             │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Application Code                             │    │
│  ├──────────────────────────────────────────────┤    │
│  │  src/                                         │    │
│  │  ├── agents/                                  │    │
│  │  │   ├── demand_agent.py                     │    │
│  │  │   ├── inventory_agent.py                  │    │
│  │  │   └── pricing_agent.py                    │    │
│  │  ├── orchestrator/                            │    │
│  │  │   └── workflow.py                          │    │
│  │  ├── services/                                │    │
│  │  │   ├── similarity.py                        │    │
│  │  │   └── forecasting.py                       │    │
│  │  └── cli/                                     │    │
│  │      └── main.py                              │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Data Storage (Local Filesystem)              │    │
│  ├──────────────────────────────────────────────┤    │
│  │  data/                                        │    │
│  │  ├── historical_sales.csv                     │    │
│  │  ├── product_catalog.csv                      │    │
│  │  ├── store_attributes.csv                     │    │
│  │  ├── demand_forecasting.db (SQLite)           │    │
│  │  └── forecasts/ (Parquet files)               │    │
│  │                                                │    │
│  │  config/                                       │    │
│  │  └── archetype2_config.yaml                   │    │
│  │                                                │    │
│  │  output/                                       │    │
│  │  ├── forecasts/ (CSV/JSON)                    │    │
│  │  ├── inventory_plans/ (CSV)                   │    │
│  │  └── performance_reports/ (CSV)               │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
└────────────────────────────────────────────────────────┘
                        │
                        │ HTTPS
                        ▼
        ┌────────────────────────────────┐
        │      OpenAI API                │
        │  • gpt-4o-mini                 │
        │  • text-embedding-3-small      │
        └────────────────────────────────┘
```

### 10.2 Installation & Setup

**Installation Steps**:

```bash
# 1. Clone repository
git clone <repo-url>
cd demand-forecasting-system

# 2. Create virtual environment
python3.9 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up configuration
cp config/archetype2_config.example.yaml config/archetype2_config.yaml
# Edit config file with your OpenAI API key

# 5. Initialize database
python scripts/init_db.py

# 6. Load sample data
python scripts/load_sample_data.py

# 7. Verify installation
python -m src.cli.main --version
```

**Requirements.txt**:

```txt
# Core Dependencies
python>=3.9
langchain>=0.1.0
openai>=1.0.0
pandas>=1.5.0
numpy>=1.24.0
scikit-learn>=1.2.0

# Forecasting Libraries
statsmodels>=0.14.0
prophet>=1.1.0

# Data Storage
sqlalchemy>=2.0.0
pyarrow>=12.0.0  # For Parquet

# CLI
typer>=0.9.0
rich>=13.0.0  # For pretty CLI output

# Configuration
pyyaml>=6.0

# Utilities
python-dotenv>=1.0.0
tqdm>=4.65.0  # Progress bars

# Development (optional)
pytest>=7.4.0
black>=23.0.0
mypy>=1.5.0
```

### 10.3 CLI Interface

**Command Structure**:

```bash
# Main command
python -m src.cli.main [COMMAND] [OPTIONS]

# Commands:
forecast      # Run demand forecasting (Phase 1)
allocate      # Calculate initial allocation (Phase 2)
replenish     # Generate replenishment plan (Phase 3)
price         # Run pricing agent (Phase 4)
analyze       # Season-end analysis (Phase 5)
run-season    # Run full season end-to-end

# Global options:
--config PATH      # Path to YAML config (default: config/archetype2_config.yaml)
--data-dir PATH    # Path to data directory (default: ./data)
--output-dir PATH  # Path to output directory (default: ./output)
--verbose         # Enable verbose logging
```

**Example Usage**:

```bash
# Run Phase 1: Pre-Season Forecasting
python -m src.cli.main forecast \
  --config config/archetype2_config.yaml \
  --skus data/new_skus.csv \
  --output output/forecasts/

# Run Phase 2: Initial Allocation
python -m src.cli.main allocate \
  --forecasts output/forecasts/ \
  --output output/allocations/

# Run Full Season (all 5 phases)
python -m src.cli.main run-season \
  --config config/archetype2_config.yaml \
  --data-dir data/ \
  --output-dir output/
```

### 10.4 Future: Cloud Deployment (Post-MVP)

**Target Architecture** (Future):

```
┌─────────────────────────────────────────────────────────┐
│                  CLOUD DEPLOYMENT                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │  Web UI (Streamlit/Gradio)                    │     │
│  └───────────────┬──────────────────────────────┘     │
│                  │ REST API                            │
│  ┌───────────────▼──────────────────────────────┐     │
│  │  API Layer (FastAPI)                          │     │
│  │  • Forecast API                               │     │
│  │  • Allocation API                             │     │
│  │  • Performance Monitoring API                 │     │
│  └───────────────┬──────────────────────────────┘     │
│                  │                                      │
│  ┌───────────────▼──────────────────────────────┐     │
│  │  Agent Layer (Containers)                     │     │
│  │  • Demand Agent (Docker)                      │     │
│  │  • Inventory Agent (Docker)                   │     │
│  │  • Pricing Agent (Docker)                     │     │
│  │  • Orchestrator (Docker)                      │     │
│  └───────────────┬──────────────────────────────┘     │
│                  │                                      │
│  ┌───────────────▼──────────────────────────────┐     │
│  │  Data Layer (Cloud Storage)                   │     │
│  │  • PostgreSQL (historical sales)              │     │
│  │  • S3 (forecast Parquet files)                │     │
│  │  • Redis (cache)                              │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Deployment Options**:
- **AWS**: ECS (containers) + RDS (PostgreSQL) + S3 (Parquet)
- **GCP**: Cloud Run + Cloud SQL + GCS
- **Azure**: Container Instances + Azure SQL + Blob Storage

---

## 11. Security Architecture

### 11.1 MVP Security Considerations

**Threat Model**:
- **Low Risk**: Local deployment, single-user, academic project
- **Primary Concerns**: API key security, data privacy

**Security Controls**:

| Concern | Control | Implementation |
|---------|---------|----------------|
| **API Key Exposure** | Environment variables | `.env` file (not committed to git) |
| **Sensitive Data** | Local filesystem | Data stored locally, not transmitted |
| **Code Injection** | Input validation | Validate all CSV inputs, YAML configs |
| **Dependency Vulnerabilities** | Dependency scanning | `pip-audit` in CI/CD |

**API Key Management**:

```python
# .env (not committed)
OPENAI_API_KEY=sk-proj-...

# Code
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")
```

**.gitignore**:

```
# Secrets
.env
*.key

# Data
data/
output/
*.db

# Caches
__pycache__/
.pytest_cache/
*.pyc
```

### 11.2 Future: Production Security (Post-MVP)

**Additional Controls**:
- **Authentication**: OAuth 2.0 for multi-user access
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS for data in transit, at-rest encryption for database
- **Audit Logging**: Log all agent decisions, user actions
- **Secret Management**: AWS Secrets Manager / Azure Key Vault

---

## 12. Performance & Scalability

### 12.1 MVP Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Initial Forecast (50 SKUs)** | <4 hours | Wall-clock time |
| **Bi-weekly Update (50 SKUs)** | <30 minutes | Wall-clock time |
| **Variance Detection** | <1 minute | Calculation time |
| **Markdown Analysis** | <5 minutes | Agent execution time |
| **Season-End Analysis** | <10 minutes | Report generation time |

### 12.2 Performance Bottlenecks & Optimizations

**Bottleneck 1: Similar-Item Matching (Embeddings)**

**Problem**: Generating embeddings for 50 new SKUs + searching 500 historical SKUs

**Solution**:
- **Pre-compute embeddings** for historical SKUs (one-time cost)
- **Cache embeddings** in local file (JSON/Parquet)
- **Batch API calls** (up to 100 items per request)

```python
# Optimization: Pre-compute historical embeddings
def precompute_embeddings(catalog: pd.DataFrame, output_path: str):
    embeddings = {}
    for _, row in tqdm(catalog.iterrows(), total=len(catalog)):
        text = f"{row['name']} {row['category']} {row['style']} {row['color']}"
        embeddings[row['sku_id']] = openai_client.get_embedding(text)

    with open(output_path, 'w') as f:
        json.dump(embeddings, f)
```

**Bottleneck 2: ARIMA/Prophet Forecasting**

**Problem**: Prophet can take 5-10 minutes per SKU (50 SKUs = 4-8 hours)

**Solution**:
- **Parallel processing**: Use `multiprocessing` to forecast multiple SKUs concurrently
- **Skip Prophet for MVP**: Use faster methods (exponential smoothing, ARIMA)

```python
from multiprocessing import Pool

def forecast_parallel(skus: List[SKU], num_workers: int = 4) -> List[ForecastOutput]:
    with Pool(num_workers) as pool:
        results = pool.map(demand_agent.forecast_demand, skus)
    return results
```

**Bottleneck 3: Database Queries**

**Problem**: Repeated queries for historical sales data

**Solution**:
- **Load once into memory**: Use pandas DataFrame
- **SQLite indexing**: Index on `sku_id`, `store_id`, `date`
- **Parquet for large datasets**: Faster than CSV

### 12.3 Scalability Roadmap

**MVP Scale** (Current):
- 50 SKUs per season
- 50 stores
- 26-week horizon
- 1 user (local)

**Phase 2 Scale** (6 months post-MVP):
- 500 SKUs per season
- 200 stores
- 52-week horizon
- 10 concurrent users (cloud deployment)
- **Changes Needed**:
  - Migrate to PostgreSQL
  - Add Redis caching layer
  - Containerize agents (Docker)
  - Implement job queue (Celery)

**Phase 3 Scale** (1 year post-MVP):
- 5,000 SKUs per season
- 1,000 stores
- Multiple seasons (overlapping)
- 100+ concurrent users
- **Changes Needed**:
  - Kubernetes orchestration
  - Distributed forecasting (Spark/Dask)
  - CDN for forecast outputs
  - Auto-scaling

---

## 13. Technology Stack

### 13.1 Core Technologies

| Layer | Technology | Version | Purpose | License | Cost |
|-------|-----------|---------|---------|---------|------|
| **Language** | Python | 3.9+ | Core development | PSF | Free |
| **Agent Framework** | LangChain | 0.1+ | Multi-agent orchestration | MIT | Free |
| **LLM** | OpenAI (gpt-4o-mini) | - | Reasoning, embeddings | Proprietary | $0.15/1M tokens |
| **ML/Forecasting** | statsmodels | 0.14+ | ARIMA, SARIMA | BSD | Free |
| **ML/Forecasting** | Prophet | 1.1+ | Time-series (optional) | MIT | Free |
| **Data Processing** | pandas | 1.5+ | DataFrames | BSD | Free |
| **Numerical** | NumPy | 1.24+ | Array operations | BSD | Free |
| **Database** | SQLite | 3.x | Local relational DB | Public Domain | Free |
| **File Format** | Parquet (pyarrow) | 12+ | Efficient columnar storage | Apache 2.0 | Free |
| **Configuration** | PyYAML | 6.0+ | YAML parsing | MIT | Free |
| **CLI** | Typer | 0.9+ | Command-line interface | MIT | Free |
| **CLI UI** | Rich | 13+ | Pretty terminal output | MIT | Free |
| **Testing** | pytest | 7.4+ | Unit/integration tests | MIT | Free |
| **Code Quality** | Black | 23+ | Code formatting | MIT | Free |
| **Type Checking** | mypy | 1.5+ | Static type checking | MIT | Free |

### 13.2 Technology Justifications

**Why Python?**
- Rich ML/data science ecosystem (statsmodels, Prophet, pandas)
- LangChain native support
- Fast prototyping for academic MVP
- Wide adoption in data science community

**Why LangChain?**
- Mature agent framework (vs building from scratch)
- OpenAI function calling built-in
- Tool abstraction (forecasting methods as tools)
- Active community, good documentation

**Why gpt-4o-mini?**
- **Cost-efficient**: $0.15/1M input tokens (vs gpt-4: $10/1M)
- **Sufficient for reasoning**: Similar-item selection, method choice
- **Fast**: Lower latency than gpt-4
- **MVP budget**: <$5 total for 50 SKUs

**Why SQLite?**
- **Zero setup**: File-based, no server needed
- **Sufficient for MVP**: <100 MB data
- **Portable**: Single file, easy to share
- **Future migration path**: Compatible SQL dialect (PostgreSQL)

**Why Parquet?**
- **Efficient storage**: 50 stores × 26 weeks × 50 SKUs = 65,000 values
- **Fast I/O**: Columnar format, compression
- **Pandas compatible**: `pd.read_parquet()`, `df.to_parquet()`

### 13.3 Alternatives Considered

| Choice | Alternative | Rejected Because |
|--------|-------------|-----------------|
| **LangChain** | Custom agent implementation | Reinventing the wheel, slower MVP |
| **LangChain** | AutoGPT, CrewAI | Less mature, fewer examples |
| **gpt-4o-mini** | GPT-4 | 66x more expensive ($10 vs $0.15/1M) |
| **gpt-4o-mini** | Open-source LLMs (Llama 3) | Requires GPU, harder deployment |
| **SQLite** | PostgreSQL | Overkill for MVP, requires server setup |
| **SQLite** | MongoDB | Non-relational overkill, less structured |
| **Parquet** | CSV | Slower I/O, larger file sizes |
| **Python** | R | Weaker agent framework support |

---

## 14. Development Approach

### 14.1 Development Phases (12-Week MVP)

| Week | Phase | Deliverables | Success Criteria |
|------|-------|--------------|-----------------|
| **1-2** | Setup & Data Pipeline | • Python environment<br>• Mock data (2 years)<br>• SQLite database | Data loads successfully |
| **3-4** | Demand Agent (Similarity) | • Embedding-based matching<br>• Top-5 retrieval | Similarity >0.80 for test SKUs |
| **5-6** | Demand Agent (Forecasting) | • `demand_by_store_by_week` output<br>• Confidence scoring | Forecasts 10 SKUs end-to-end |
| **7-8** | Inventory Agent | • Manufacturing order calc<br>• Initial allocation<br>• Replenishment logic | Allocations sum correctly |
| **9** | Pricing Agent | • Sell-through monitoring<br>• Markdown trigger | Correctly flags <50% sell-through |
| **10** | Orchestrator | • 5-phase workflow<br>• Variance detection | Full season runs end-to-end |
| **11** | Validation | • Hindcast Fall/Winter 2024<br>• MAPE calculation | MAPE <20% |
| **12** | Documentation | • User guide<br>• Technical docs<br>• Performance report | Complete, working demo |

### 14.2 Development Practices

**Version Control**:
- Git repository (GitHub)
- Feature branches (e.g., `feature/demand-agent-similarity`)
- Pull requests for code review
- Main branch protected (no direct commits)

**Code Quality**:
```bash
# Pre-commit hooks
black src/  # Auto-formatting
mypy src/  # Type checking
pytest tests/  # Run tests
```

**Testing Strategy**:
- **Unit Tests**: Test individual functions (pytest)
- **Integration Tests**: Test agent interactions
- **End-to-End Tests**: Full season simulation
- **Target Coverage**: >70% for MVP

**Documentation**:
- **Code Comments**: Docstrings for all classes/functions
- **README.md**: Installation, usage, examples
- **Architecture.md**: This document
- **API Reference**: Auto-generated (Sphinx)

### 14.3 Project Structure

```
demand-forecasting-system/
├── config/
│   ├── archetype2_config.yaml
│   └── config.schema.json
├── data/
│   ├── historical_sales.csv
│   ├── product_catalog.csv
│   ├── store_attributes.csv
│   └── demand_forecasting.db (SQLite)
├── output/
│   ├── forecasts/
│   ├── allocations/
│   └── reports/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── demand_agent.py
│   │   ├── inventory_agent.py
│   │   └── pricing_agent.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── workflow.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── similarity.py
│   │   ├── forecasting.py
│   │   └── openai_client.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py
│   │   └── repositories.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── metrics.py
├── tests/
│   ├── test_demand_agent.py
│   ├── test_inventory_agent.py
│   ├── test_pricing_agent.py
│   └── test_orchestrator.py
├── docs/
│   ├── user_guide.md
│   ├── architecture.md
│   └── api_reference.md
├── scripts/
│   ├── init_db.py
│   ├── load_sample_data.py
│   └── generate_mock_data.py
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

---

## 15. Appendices

### 15.1 Glossary

| Term | Definition |
|------|------------|
| **Archetype** | Retail business model classification (Fashion, Stable Catalog, CPG) |
| **MAPE** | Mean Absolute Percentage Error - forecast accuracy metric |
| **Holdback** | % of inventory kept at DC instead of allocated to stores |
| **Sell-Through** | % of manufactured inventory sold by a given week |
| **Similar-Item Matching** | Algorithm to find historical SKUs with similar attributes |
| **Variance Threshold** | % deviation from forecast that triggers re-forecast (15% for MVP) |
| **Confidence Score** | 0-100% indicating forecast reliability |
| **Orchestrator** | Central component coordinating agent workflows |
| **Agent** | Autonomous software component making domain-specific decisions |
| **LLM** | Large Language Model (e.g., gpt-4o-mini) |
| **Embedding** | Vector representation of text for semantic similarity (1536-dim) |

### 15.2 References

**Project Documents**:
- [Product Brief v2.1](../product_brief/2_simplified_three_agent_mvp.md)
- [Product Requirements Document](../prd/prd_demand_forecasting_system.md)
- [Operational Workflow](../product_brief/2_operational_workflow.md)
- [Key Parameters Guide](../product_brief/2_key_parameter.md)
- [Agent Coordination Workflow](../prd/agent_coordination_workflow.md)

**External References**:
- LangChain Documentation: https://python.langchain.com/docs/
- OpenAI API Reference: https://platform.openai.com/docs/
- Prophet Documentation: https://facebook.github.io/prophet/
- statsmodels Documentation: https://www.statsmodels.org/

### 15.3 Acronyms

| Acronym | Expansion |
|---------|-----------|
| **API** | Application Programming Interface |
| **ARIMA** | AutoRegressive Integrated Moving Average |
| **CLI** | Command Line Interface |
| **CPG** | Consumer Packaged Goods |
| **CSV** | Comma-Separated Values |
| **DC** | Distribution Center |
| **JSON** | JavaScript Object Notation |
| **LLM** | Large Language Model |
| **MAPE** | Mean Absolute Percentage Error |
| **ML** | Machine Learning |
| **MVP** | Minimum Viable Product |
| **PP** | Pain Point (from user research) |
| **PRD** | Product Requirements Document |
| **REST** | Representational State Transfer |
| **SKU** | Stock Keeping Unit |
| **YAML** | YAML Ain't Markup Language |

### 15.4 Diagram Legend

**Component Diagrams**:
- **Rectangle**: Component/module
- **Arrow**: Data flow / dependency
- **Dashed line**: Optional / future

**Sequence Diagrams**:
- **Solid arrow**: Synchronous call
- **Dashed arrow**: Response
- **Note box**: Explanation

### 15.5 Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-10 | Initial architecture document for MVP | Winston (Architect Agent) |

---

**Document Owner**: Independent Study Project
**Architecture Review**: Pending
**Status**: Draft - Awaiting Technical Review
**Next Review Date**: 2025-10-17

---

## Appendix A: Sample Configuration

**config/archetype2_config.yaml** (Full Example)

```yaml
# Demand Forecasting System Configuration
# Archetype 2: Stable Catalog Retail (Furniture, 26-week season)

archetype:
  name: "stable_catalog"
  description: "Furniture retail with moderate seasonality, 26-week selling period"
  category: "furniture"

season:
  length_weeks: 26
  start_date: "2025-10-01"
  end_date: "2026-03-31"

forecasting:
  prediction_horizon_weeks: 26
  update_cadence: "bi-weekly"  # Options: daily, weekly, bi-weekly, monthly
  variance_threshold: 0.15  # 15% - trigger re-forecast
  confidence_threshold: 0.70  # 70% - alert user if below
  similar_items_count: 10  # Top N similar items for matching

  methods:
    enable_arima: true
    enable_prophet: false  # Disable for MVP (slow)
    enable_hybrid: true
    fallback_method: "exponential_smoothing"

inventory:
  safety_stock_pct: 0.15  # 15% buffer above forecast
  holdback_pct: 0.65  # 65% held at DC
  min_holdback_pct: 0.60  # Minimum constraint
  max_holdback_pct: 0.70  # Maximum constraint
  replenishment_cadence: "bi-weekly"

pricing:
  markdown_trigger_week: 12  # Week 12 checkpoint
  markdown_threshold: 0.50  # 50% sell-through target
  markdown_depths: [0.10, 0.20, 0.30]  # Available discount levels
  elasticity_factor: 0.50  # 20% markdown → 10% demand lift

stores:
  count: 50
  clusters:
    - name: "A"
      count: 15
      description: "High volume stores"
    - name: "B"
      count: 25
      description: "Medium volume stores"
    - name: "C"
      count: 10
      description: "Low volume stores"

skus:
  count: 50
  new_product_ratio: 0.25  # 25% new, 75% existing

llm:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 500
  api_key_env: "OPENAI_API_KEY"  # Read from environment variable

  embeddings:
    model: "text-embedding-3-small"
    similarity_threshold: 0.75  # Minimum similarity score

  cost_tracking:
    enabled: true
    budget_limit_usd: 5.00
    alert_at_pct: 0.80  # Alert at 80% of budget

data:
  historical_sales_path: "data/historical_sales.csv"
  product_catalog_path: "data/product_catalog.csv"
  store_attributes_path: "data/store_attributes.csv"
  database_path: "data/demand_forecasting.db"

output:
  forecasts_dir: "output/forecasts"
  allocations_dir: "output/allocations"
  reports_dir: "output/reports"
  format: "csv"  # Options: csv, json, both

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/system.log"
  console: true
```

---

**End of Architecture Document**
