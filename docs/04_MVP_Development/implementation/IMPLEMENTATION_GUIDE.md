# Implementation Guide

**Project:** Multi-Agent Retail Demand Forecasting System (v3.3 Parameter-Driven)
**Status:** Ready to Start - Phase 1 (Data Generation)
**Last Updated:** 2025-10-17
**BMad Agent:** Use as specified per phase

---

## Overview

This guide provides comprehensive instructions for executing the **4-phase implementation process** for the parameter-driven multi-agent retail forecasting system. All v3.3 planning documents are complete - we are now **ready to code**.

**Purpose:** This is the single source of truth for all implementation activities. It covers workflows, best practices, troubleshooting, and daily routines for successful phase execution.

### Implementation Philosophy

- **Strategic order: Data → Frontend → Backend Architecture → Individual Agents**
  - Rationale: Requirements may change, but architecture remains stable
  - Frontend mockup validates UX before agent logic implementation
  - Architecture provides scaffolding for all agents

- **One phase at a time** - Complete before moving to next
- **Document as you build** - Update docs during implementation, not after
- **All requirements from planning docs** - Single source of truth in `docs/04_MVP_Development/planning/`
- **Learn and adapt** - Retrospectives inform next phase

---

## Phase Status Tracker

| Phase | Status | Duration | Agent | Start Date | End Date | Docs |
|-------|--------|----------|-------|------------|----------|------|
| **Phase 1: Data Generation** | 🟡 Ready to Start | 1-2 days | `*agent dev` | TBD | TBD | 0/4 |
| **Phase 2: Frontend Mockup** | ⏳ Not Started | 3-4 days | `*agent ux-expert` | TBD | TBD | 0/4 |
| **Phase 3: Backend Architecture** | ⏳ Not Started | 5-7 days | `*agent architect` | TBD | TBD | 0/4 |
| **Phase 4: Orchestrator Agent** | ⏳ Not Started | 2-3 days | `*agent dev` | TBD | TBD | 0/4 |
| **Phase 5: Demand Agent** | ⏳ Not Started | 5-7 days | `*agent dev` | TBD | TBD | 0/4 |
| **Phase 6: Inventory Agent** | ⏳ Not Started | 3-4 days | `*agent dev` | TBD | TBD | 0/4 |
| **Phase 7: Pricing Agent** | ⏳ Not Started | 2-3 days | `*agent dev` | TBD | TBD | 0/4 |
| **Phase 8: Integration & Testing** | ⏳ Not Started | 5-7 days | `*agent qa` | TBD | TBD | 0/4 |

**Legend:**
- ✅ Complete
- 🟡 Ready to Start / In Progress
- ⏳ Not Started
- 🔴 Blocked

**Total Estimated Duration:** 26-39 days (~4-6 weeks)

---

## Planning Documents Reference (v3.3)

**All implementation requirements come from these documents:**

| Document | Path | Purpose |
|----------|------|---------|
| **Planning Guide** | `planning/0_PLANNING_GUIDE.md` | Documentation navigation and standards |
| **Product Brief v3.3** | `planning/1_product_brief_v3.3.md` | Parameter-driven architecture, core features |
| **Process Workflow v3.3** | `planning/2_process_workflow_v3.3.md` | 5-phase operational workflow with examples |
| **Technical Architecture v3.3** | `planning/3_technical_architecture_v3.3.md` | Tech stack, API structure, data models |
| **PRD v3.3** | `planning/4_prd_v3.3.md` | Product requirements and user stories |
| **Frontend Spec v3.3** | `planning/5_front-end-spec_v3.3.md` | Complete UI/UX design, all 7 sections |
| **Data Specification v3.2** | `planning/6_data_specification_v3.2.md` | CSV formats, validation rules |

**Critical Rule:** If implementation requirements are unclear, reference these planning documents first. Do NOT make assumptions.

---

## Phase Navigation

### Phase 1: Data Generation (CURRENT - READY!)

**Goal:** Generate realistic mock data for 3 scenarios (normal, high demand, low demand)

**Agent:** `*agent dev`

**Requirements Source:**
- `planning/6_data_specification_v3.2.md` - Complete CSV specifications
- `planning/2_process_workflow_v3.3.md` - Scenario definitions

**Key Deliverables:**
1. **Historical Sales Data** (`historical_sales_2022_2024.csv`)
   - 54,750 rows (3 years × 365 days × 50 stores)
   - 3 categories: Women's Dresses, Men's Shirts, Accessories
   - Seasonality patterns, holiday events, weekly patterns
   - Clean data (±10-15% noise) for model training

2. **Store Attributes** (`store_attributes.csv`)
   - 50 stores with 7 K-means features
   - Expected 3 clusters: Fashion_Forward, Mainstream, Value_Conscious
   - Correlation formula for sales multiplier

3. **Weekly Actuals** (12 CSV files, `actuals_week_1.csv` to `actuals_week_12.csv`)
   - 3 scenarios: normal_season, high_demand, low_demand
   - Messier data (±20-25% noise) for testing
   - Week 5 variance >20% in all scenarios (to trigger re-forecast)

4. **Validation Suite**
   - 6 validation types: Completeness, Quality, Format, Statistical, Pattern, Weekly Actuals
   - MAPE target: 12-18% across all scenarios

**Documents:**
- [Implementation Plan](./phase_1_data_generation/implementation_plan.md) ⏳ Create before starting
- [Technical Decisions](./phase_1_data_generation/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_1_data_generation/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_1_data_generation/retrospective.md) ⏳ Complete after phase

**Quick Start:**
```bash
*agent dev

Task: Implement mock data generation script for parameter-driven retail forecasting system

Reference: docs/04_MVP_Development/planning/6_data_specification_v3.2.md

Key deliverables:
- historical_sales_2022_2024.csv (54,750 rows, 3 categories)
- store_attributes.csv (50 stores, 7 features)
- 36 weekly actuals CSVs (3 scenarios × 12 weeks)
- Validation suite (6 types)
- README.md with data dictionary

MAPE target: 12-18%
```

**Prerequisites:**
- ✅ Planning documents complete (v3.3)
- ⏳ Python 3.11+ environment
- ⏳ Required libraries: pandas, numpy, prophet, pmdarima, scikit-learn

---

### Phase 2: Frontend Mockup

**Goal:** Build fully functional React dashboard UI (no backend integration yet)

**Agent:** `*agent ux-expert`

**Why Before Backend:** Validate UX flow and parameter gathering interface with stakeholders before implementing complex agent logic. Frontend changes are cheaper than backend refactoring.

**Requirements Source:**
- `planning/5_front-end-spec_v3.3.md` - Complete UI specification (ALL 7 sections)
- `planning/1_product_brief_v3.3.md` - Parameter-driven features

**Key Deliverables:**
1. **Section 0: Parameter Gathering** (NEW in v3.3)
   - Free-form textarea (500 char limit)
   - "Extract Parameters" button → LLM extraction (mock for now)
   - Confirmation modal with 5 parameters
   - Collapsible banner after confirmation

2. **Section 1: Fixed Header with Agent Cards**
   - 3 agent cards (Demand, Inventory, Pricing)
   - Progress bars, WebSocket log messages (mock streaming)
   - Auto-collapse after 5 seconds

3. **Section 2: Forecast Summary**
   - Category display, total forecast, Prophet/ARIMA/Ensemble
   - Manufacturing order with approval status
   - Mini chart (Recharts 400x60px)

4. **Section 3: Cluster Cards**
   - 3 stacked cluster cards (Fashion_Forward, Mainstream, Value_Conscious)
   - Expandable store table (TanStack Table)
   - Export CSV button

5. **Section 4: Weekly Performance Chart**
   - Recharts ComposedChart (forecast line + actual bars)
   - Interactive table with variance highlighting
   - Row expansion for store-level breakdown

6. **Section 5: Replenishment Queue**
   - Current week's shipments
   - DC inventory warnings
   - Approve button (no confirmation modal)

7. **Section 6: Markdown Decision**
   - Countdown timer before Week 6
   - Sell-through analysis at Week 6
   - Elasticity slider with real-time preview
   - Apply button triggers re-forecast

8. **Section 7: Performance Metrics**
   - 3 metric cards (Forecast Accuracy, Business Impact, System Performance)
   - Export buttons

9. **Mock Data Integration**
   - Use JSON fixtures from Phase 1 CSV outputs
   - Simulate WebSocket streaming with setTimeout
   - All interactions functional (buttons, sliders, tables)

**Documents:**
- [Implementation Plan](./phase_2_frontend/implementation_plan.md) ⏳ Create when Phase 1 complete
- [Technical Decisions](./phase_2_frontend/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_2_frontend/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_2_frontend/retrospective.md) ⏳ Complete after phase

**Prerequisites:**
- ✅ Phase 1 complete (mock data available as JSON fixtures)
- ⏳ Node.js 18+ installed
- ⏳ Tech stack: React 18 + TypeScript + Vite + Shadcn/ui + Tailwind CSS

---

### Phase 3: Backend Architecture Setup

**Goal:** Set up FastAPI backend with data models, database schema, REST API scaffolding (no agent logic yet)

**Agent:** `*agent architect`

**Why This Order:** Architecture provides stable foundation. Requirements may evolve, but infrastructure (DB, API structure, WebSocket) remains constant. This allows parallel agent development later.

**Requirements Source:**
- `planning/3_technical_architecture_v3.3.md` - Complete architecture specification
- `planning/4_prd_v3.3.md` - API endpoint requirements

**Key Deliverables:**
1. **Environment Setup**
   - Python 3.11+ with UV package manager
   - FastAPI 0.115+
   - OpenAI Agents SDK 0.3.3+
   - Database: SQLite 3.45+

2. **Data Models (Pydantic)**
   - SeasonParameters (NEW in v3.3)
   - Category, Store, StoreCluster
   - Forecast, Allocation
   - All 9 models from technical architecture

3. **Database Schema (SQLite)**
   - 4 normalized tables: categories, stores, store_clusters, parameters
   - 4 JSON array field tables: forecasts, allocations, actual_sales, workflow_logs
   - Migration scripts

4. **REST API Scaffolding (ALL endpoints, placeholder responses)**
   - Phase 0: `/api/parameters/extract`, `/api/parameters/confirm`
   - Phase 1: `/api/data/upload-*`, `/api/categories/list`, `/api/forecast/generate`
   - Phase 2: `/api/data/upload-weekly-actuals`, `/api/variance/{week}`
   - Phase 3: `/api/replenishment/queue/{week}`, `/api/replenishment/approve`
   - Phase 4: `/api/markdown/checkpoint/{week}`, `/api/markdown/apply`
   - General: `/api/forecast/{id}`, `/api/allocation/{id}`, `/api/reports/{season_id}`

5. **WebSocket Server Setup**
   - Endpoint: `ws://localhost:8000/ws/agents`
   - Message format: {agent, status, progress, step, duration, result}
   - Broadcasting mechanism (for later agent integration)

6. **Data Pipeline**
   - CSV upload handlers
   - Historical data ingestion
   - Store attributes import
   - Weekly actuals processing

7. **API Documentation**
   - OpenAPI/Swagger auto-generated
   - Request/response examples
   - Authentication stubs (for future)

**Documents:**
- [Implementation Plan](./phase_3_backend_architecture/implementation_plan.md) ⏳ Create when Phase 2 complete
- [Technical Decisions](./phase_3_backend_architecture/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_3_backend_architecture/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_3_backend_architecture/retrospective.md) ⏳ Complete after phase

**Prerequisites:**
- ✅ Phase 2 complete (frontend mockup validates API contracts)
- ⏳ Azure OpenAI API keys configured
- ⏳ UV package manager installed

---

### Phase 4: Orchestrator Agent

**Goal:** Implement central coordinator for multi-agent workflows

**Agent:** `*agent dev`

**Why First Agent:** Orchestrator defines handoff patterns that all other agents will use. Implement once, then each agent plugs into this framework.

**Requirements Source:**
- `planning/3_technical_architecture_v3.3.md` - Orchestrator responsibilities
- `planning/2_process_workflow_v3.3.md` - Workflow coordination examples

**Key Deliverables:**
1. **Core Orchestrator Logic**
   - OpenAI Agents SDK integration
   - Session management (conversation history)
   - Context-rich handoffs (pass objects, not DB IDs)

2. **Workflow State Machine**
   - 5-phase workflow: Pre-season → Season Start → In-Season → Mid-Season → Post-Season
   - State transitions based on variance, approvals, markdown triggers

3. **Dynamic Handoff Enabling**
   - Normal flow: Demand → Inventory → Pricing
   - Re-forecast flow: Pricing → Demand (enabled only when variance >20%)
   - Parameters-aware: Skip Pricing if no markdown checkpoint

4. **Variance Monitoring**
   - Weekly variance calculation (forecast vs actuals)
   - Threshold detection (>20% triggers re-forecast)
   - Alert system (🟢<10%, 🟡10-20%, 🔴>20%)

5. **Human-in-the-Loop Integration**
   - Approval modals (manufacturing order, replenishment, markdown)
   - Modify iterative + Accept options (no Reject)
   - Approval tracking

6. **WebSocket Event Streaming**
   - Broadcast agent status updates
   - Line-by-line progress messages
   - Duration tracking per step

7. **Workflow Logging**
   - Log all interactions to workflow_logs table
   - Input/output JSON for each handoff
   - Performance metrics (duration_ms)

**Stub Agent Responses (for testing):**
- Demand Agent: Return mock forecast JSON
- Inventory Agent: Return mock allocation JSON
- Pricing Agent: Return mock markdown recommendation

**Documents:**
- [Implementation Plan](./phase_4_orchestrator/implementation_plan.md) ⏳ Create when Phase 3 complete
- [Technical Decisions](./phase_4_orchestrator/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_4_orchestrator/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_4_orchestrator/retrospective.md) ⏳ Complete after phase

**Prerequisites:**
- ✅ Phase 3 complete (backend architecture ready)
- ⏳ OpenAI Agents SDK configured
- ⏳ WebSocket server functional

---

### Phase 5: Demand Agent

**Goal:** Implement ensemble forecasting (Prophet + ARIMA) + K-means clustering + allocation factors

**Agent:** `*agent dev`

**Requirements Source:**
- `planning/3_technical_architecture_v3.3.md` - Demand Agent specifications
- `planning/1_product_brief_v3.3.md` - Parameter-driven adaptations

**Key Deliverables:**
1. **Forecasting Tools**
   - `forecast_category_demand()` - Ensemble Prophet + ARIMA
   - Prophet model: Seasonal decomposition, trend analysis
   - ARIMA model: Auto-ARIMA parameter selection
   - Ensemble: Simple average of both forecasts
   - Duration target: ~15-20s per model

2. **Clustering Tool**
   - `cluster_stores()` - K-means with K=3
   - 7 features: avg_weekly_sales_12mo, store_size_sqft, median_income, foot_traffic, competitor_density, online_penetration, population_density
   - StandardScaler normalization
   - K-means++ initialization
   - Cluster naming: Fashion_Forward, Mainstream, Value_Conscious

3. **Allocation Factors Tool**
   - `calculate_allocation_factors()` - Hierarchical allocation
   - Formula: 0.70 × historical_pct + 0.30 × attribute_score
   - Historical_pct = store's % of cluster sales last season
   - Attribute_score based on size, tier, demographics

4. **Parameter-Driven Adaptation (v3.3)**
   - Input: `ReplenishmentStrategy` from SeasonParameters
   - Logic: IF replenishment_strategy == "none" THEN safety_stock_pct = 0.25 ELSE 0.20
   - Reasoning: "No replenishment means I cannot correct forecast errors later. Increase safety stock from 20% to 25%."
   - LLM generates explanation text for user

5. **Re-Forecast Logic**
   - Triggered by Orchestrator when variance >20%
   - Receives: {reason, variance, actual_week_1_to_N, remaining_weeks}
   - Re-runs Prophet + ARIMA with combined historical + new actuals
   - Returns updated forecast for remaining weeks only

6. **Output JSON Structure**
   ```json
   {
     "total_season_demand": 8000,
     "prophet_forecast": 8200,
     "arima_forecast": 7800,
     "forecasting_method": "ensemble_prophet_arima",
     "weekly_demand_curve": [650, 720, 680, ...],
     "peak_week": 2,
     "cluster_distribution": {"Fashion_Forward": 0.40, ...},
     "store_allocation_factors": {"S01": 0.08, ...},
     "adapted_safety_stock_pct": 0.25,
     "adaptation_reasoning": "No replenishment strategy specified..."
   }
   ```

7. **Integration with Orchestrator**
   - Register with Orchestrator handoff system
   - Receive parameters context from Orchestrator
   - Return forecast object (no DB write, Orchestrator handles)

**Documents:**
- [Implementation Plan](./phase_5_demand_agent/implementation_plan.md) ⏳ Create when Phase 4 complete
- [Technical Decisions](./phase_5_demand_agent/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_5_demand_agent/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_5_demand_agent/retrospective.md) ⏳ Complete after phase

**Prerequisites:**
- ✅ Phase 4 complete (Orchestrator ready)
- ✅ Phase 1 complete (historical data available)
- ⏳ Prophet, pmdarima, scikit-learn installed

---

### Phase 6: Inventory Agent

**Goal:** Implement manufacturing order calculation + hierarchical allocation + replenishment planning

**Agent:** `*agent dev`

**Requirements Source:**
- `planning/3_technical_architecture_v3.3.md` - Inventory Agent specifications
- `planning/1_product_brief_v3.3.md` - Parameter-driven adaptations

**Key Deliverables:**
1. **Manufacturing Tool**
   - `calculate_manufacturing_order()` - Add safety stock
   - Formula: manufacturing_qty = total_demand × (1 + safety_stock_pct)
   - Receives safety_stock_pct from Demand Agent (parameter-adapted)
   - Duration target: <1s

2. **Allocation Tool**
   - `allocate_to_stores()` - Hierarchical allocation
   - Input: dc_holdback_pct from SeasonParameters
   - Calculate initial_allocation_pct = 1 - dc_holdback_pct
   - For each cluster: cluster_qty = manufacturing_qty × cluster_distribution
   - For each store: store_qty = cluster_qty × store_allocation_factors
   - Constraint: Minimum 2-week forecast per store
   - Duration target: <2s

3. **Replenishment Tool**
   - `plan_replenishment()` - Weekly shipment planning
   - Formula: replenish = max(0, next_week_forecast - current_inventory)
   - Constraint: Don't exceed available DC inventory
   - Duration target: <1s

4. **Parameter-Driven Adaptation (v3.3)**
   - Input 1: `replenishment_strategy` (none, weekly, bi-weekly)
     - IF "none" THEN skip `plan_replenishment()`, allocate 100% at Week 0
     - Reasoning: "No replenishment means no weekly shipment planning needed."

   - Input 2: `dc_holdback_percentage` (0.0, 0.45, 0.65, etc.)
     - Adjust initial_allocation_pct dynamically
     - Reasoning: "High holdback (65%) gives flexibility for replenishment."

5. **Re-Allocation Logic**
   - Triggered by re-forecast from Demand Agent
   - Recalculates manufacturing, allocation, replenishment
   - Compares to original: flag shortage, recommend emergency order

6. **Output JSON Structure**
   ```json
   {
     "manufacturing_order": 9600,
     "safety_stock_pct": 0.20,
     "dc_holdback_pct": 0.45,
     "replenishment_strategy": "none",
     "store_allocations": [
       {"store_id": "S01", "cluster_id": "Fashion_Forward",
        "season_total": 256, "initial_allocation": 141, "dc_holdback": 115}
     ],
     "replenishment_plan": [],
     "adaptation_reasoning": "No replenishment strategy - allocated 100% at Week 0"
   }
   ```

7. **Integration with Orchestrator**
   - Register with Orchestrator handoff system
   - Receive forecast object from Demand Agent (context-rich handoff)
   - Return allocation object

**Documents:**
- [Implementation Plan](./phase_6_inventory_agent/implementation_plan.md) ⏳ Create when Phase 5 complete
- [Technical Decisions](./phase_6_inventory_agent/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_6_inventory_agent/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_6_inventory_agent/retrospective.md) ⏳ Complete after phase

**Prerequisites:**
- ✅ Phase 5 complete (Demand Agent provides forecast)
- ⏳ Allocation algorithms tested

---

### Phase 7: Pricing Agent

**Goal:** Implement sell-through monitoring + markdown calculation + re-forecast trigger

**Agent:** `*agent dev`

**Requirements Source:**
- `planning/3_technical_architecture_v3.3.md` - Pricing Agent specifications
- `planning/1_product_brief_v3.3.md` - Parameter-driven adaptations

**Key Deliverables:**
1. **Sell-Through Tool**
   - `evaluate_sellthrough()` - Compare actual vs target
   - Formula: sell_through_rate = actual_sold / total_manufactured
   - Duration target: <1s

2. **Markdown Tool**
   - `calculate_markdown()` - Gap × Elasticity formula
   - Gap = target_threshold - sell_through_rate
   - Markdown = Gap × elasticity_coefficient
   - Round to nearest 5%, cap at 40%
   - Duration target: <1s

3. **Markdown Application Tool**
   - `apply_markdown()` - Uniform across all stores (MVP)
   - Estimate sales lift: markdown_pct × 1.8
   - Duration target: <1s

4. **Parameter-Driven Adaptation (v3.3)**
   - Input 1: `markdown_checkpoint_week` (int or None)
     - IF None THEN skip entire Week 6 checkpoint, agent remains idle
     - Reasoning: "No markdown parameter specified. Skip pricing adjustments (premium positioning)."

   - Input 2: `markdown_threshold` (float or None)
     - Use as target sell-through % instead of hardcoded 60%
     - Reasoning: "Later checkpoint with lower threshold - less aggressive markdown strategy."

5. **Re-Forecast Trigger**
   - After markdown applied, trigger Orchestrator
   - Orchestrator enables re-forecast handoff to Demand Agent
   - Demand Agent receives: "Markdown applied, re-forecast weeks 7-12 with new price elasticity"

6. **Output JSON Structure**
   ```json
   {
     "week_6_checkpoint": {
       "total_manufactured": 9600,
       "total_sold_w1_to_w6": 5280,
       "sell_through_rate": 0.55,
       "target_sell_through": 0.60,
       "gap": 0.05
     },
     "markdown_recommendation": {
       "apply_markdown": true,
       "markdown_pct": 0.10,
       "formula": "Gap × Elasticity = 0.05 × 2.0 = 0.10",
       "expected_sales_lift": 0.18,
       "elasticity_coefficient": 2.0
     },
     "trigger_reforecast": true,
     "adaptation_reasoning": "Applied 10% markdown at Week 6 checkpoint per strategy parameters"
   }
   ```

7. **Integration with Orchestrator**
   - Register with Orchestrator handoff system
   - Receive allocation object from Inventory Agent
   - Return markdown recommendation
   - Trigger re-forecast via Orchestrator

**Documents:**
- [Implementation Plan](./phase_7_pricing_agent/implementation_plan.md) ⏳ Create when Phase 6 complete
- [Technical Decisions](./phase_7_pricing_agent/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_7_pricing_agent/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_7_pricing_agent/retrospective.md) ⏳ Complete after phase

**Prerequisites:**
- ✅ Phase 6 complete (Inventory Agent provides allocation)
- ⏳ Markdown elasticity formulas validated

---

### Phase 8: Integration & Testing

**Goal:** End-to-end system integration + validation across 3 scenarios + performance testing

**Agent:** `*agent qa`

**Requirements Source:**
- `planning/4_prd_v3.3.md` - Acceptance criteria
- `planning/1_product_brief_v3.3.md` - Success metrics

**Key Deliverables:**
1. **Frontend-Backend Integration**
   - Connect React dashboard to FastAPI endpoints
   - WebSocket streaming (agent progress messages)
   - Parameter extraction via LLM
   - All 7 dashboard sections functional

2. **End-to-End Workflow Testing**
   - Test full workflow: Parameters → Forecast → Allocation → Replenishment → Markdown → Re-forecast
   - Verify context-rich handoffs between agents
   - Validate variance monitoring (>20% triggers re-forecast)
   - Test human-in-the-loop approvals

3. **Scenario Testing (3 scenarios from Phase 1)**
   - **Normal Season:** Viral TikTok +30% Week 5, MAPE 12-15%
   - **High Demand:** Competitor bankruptcy +40% Week 5, MAPE 15-18%
   - **Low Demand:** Supply disruption -25% Week 5, MAPE 15-18%
   - Validate re-forecast triggered in all scenarios at Week 5

4. **Parameter Flexibility Testing**
   - Test 4 parameter combinations:
     1. Fast fashion: 100% allocation, no replenishment, no markdown
     2. Premium retail: 45% holdback, weekly replenishment, no markdown
     3. Mainstream: 55% holdback, bi-weekly replenishment, Week 6 markdown @ 60%
     4. Value: 65% holdback, weekly replenishment, Week 4 markdown @ 50%
   - Verify agent adaptations and reasoning for each

5. **Performance Validation**
   - Workflow runtime <60s (target)
   - Prophet model ~15-20s
   - ARIMA model ~15-20s
   - Allocation + replenishment <3s
   - Markdown calculation <1s

6. **Accuracy Validation**
   - Hindcast Spring 2024 (12-week season)
   - Measure MAPE 12-18% across all 3 scenarios
   - Validate bias ±5%
   - Confirm re-forecast trigger accuracy 90%+

7. **Regression Test Suite**
   - Unit tests for each agent tool
   - Integration tests for API endpoints
   - WebSocket streaming tests
   - Database transaction tests

**Documents:**
- [Implementation Plan](./phase_8_integration_testing/implementation_plan.md) ⏳ Create when Phase 7 complete
- [Technical Decisions](./phase_8_integration_testing/technical_decisions.md) ⏳ Update during testing
- [Checklist](./phase_8_integration_testing/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_8_integration_testing/retrospective.md) ⏳ Complete after phase

**Prerequisites:**
- ✅ Phases 1-7 complete (full system functional)
- ⏳ All 3 scenario CSVs generated
- ⏳ Test framework setup (pytest, React Testing Library)

---

## Document Types Explained

### 1. Implementation Plan
**Purpose:** Detailed task breakdown with dependencies and estimates
**When to create:** Before starting phase
**When to update:** Daily as tasks progress
**Owner:** Phase lead agent

### 2. Technical Decisions
**Purpose:** Record design choices, alternatives considered, rationale
**When to create:** As decisions are made during implementation
**When to update:** Whenever significant decision is made
**Owner:** Phase lead agent

### 3. Checklist
**Purpose:** Granular task tracking with completion status
**When to create:** Extract from implementation plan
**When to update:** Real-time as tasks complete
**Owner:** Phase lead agent

### 4. Retrospective
**Purpose:** Capture lessons learned, what worked/didn't work
**When to create:** Immediately after phase completion
**When to update:** Once (no updates after creation)
**Owner:** Phase lead agent

---

## BMad Agent Workflow

### How to Use This System

**Step 1: Before Starting Phase**

1. **Read Prerequisites**
   - Review all planning documents (v3.3) in `docs/04_MVP_Development/planning/`
   - Read retrospective from previous phase (if applicable)
   - Verify prerequisites are met

2. **Review Phase Documents**
   - Read `implementation_plan.md` completely
   - Understand task dependencies
   - Note risk items and validation checkpoints

**Step 2: Start Phase**
```bash
*agent [dev|architect|ux-expert|qa]

Task: Begin Phase X implementation

Reference: docs/04_MVP_Development/implementation/phase_X/implementation_plan.md

Planning Docs (v3.3):
- Product Brief: docs/04_MVP_Development/planning/1_product_brief_v3.3.md
- Technical Architecture: docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md
- Frontend Spec: docs/04_MVP_Development/planning/5_front-end-spec_v3.3.md
- [Add other relevant docs]

Context:
- Previous phase: [Phase Y] completed [date]
- Key learnings: [From retrospective]
- Prerequisites: [List what's ready]

Key Deliverables:
- [Deliverable 1]
- [Deliverable 2]
```

**Step 3: During Implementation (Daily Workflow)**

**Morning:**
- [ ] Review implementation plan
- [ ] Check today's tasks from checklist
- [ ] Verify dependencies completed
- [ ] Review relevant planning docs if unclear

**During Coding:**
- [ ] Work on tasks in dependency order
- [ ] Document decisions as they happen in `technical_decisions.md`
- [ ] Update `checklist.md` immediately after completing each task
- [ ] Commit code + updated docs together (small, frequent commits)
- [ ] Reference planning docs for requirements (do NOT guess)

**End of Day:**
- [ ] Update implementation plan with actual time spent
- [ ] Note any blockers or risks discovered
- [ ] Update phase status if needed
- [ ] Plan next day's tasks

**Best Practices:**
- **Document decisions immediately** - Don't wait until end of phase
- **Commit frequently** - Code + docs together, small changes
- **Ask questions early** - Reference planning docs or ask user if unclear
- **Track time** - Compare actuals vs estimates for learning

**Step 4: Validation Checkpoints**

Run validation checks at milestones defined in implementation plan:

- [ ] Mid-phase checkpoint (50% complete)
- [ ] Pre-completion checkpoint (all code written)
- [ ] Final checkpoint (all tests passing)

**Step 5: Complete Phase**

1. **Finish All Tasks**
   - [ ] All checklist items marked complete
   - [ ] All code committed
   - [ ] All tests passing

2. **Write Retrospective**
   - [ ] What went well?
   - [ ] What didn't go well?
   - [ ] What would you do differently?
   - [ ] Lessons learned for next phase

3. **Update Documentation**
   - [ ] Update IMPLEMENTATION_GUIDE.md phase status to ✅ Complete
   - [ ] Fill in actual start/end dates
   - [ ] Update "Docs" count to 4/4

4. **Final Commit**
   ```bash
   git add docs/04_MVP_Development/implementation/phase_X/
   git commit -m "Complete Phase X: [Phase Name]

   - All tasks completed (X/X)
   - Documentation updated
   - Retrospective written

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

**Step 6: Handoff to Next Phase**

1. **Prepare Handoff**
   - [ ] Ensure retrospective is complete
   - [ ] Update IMPLEMENTATION_GUIDE.md with next phase status to 🟡 Ready to Start
   - [ ] Create any handoff notes

2. **Next Agent Preparation**
   - Read previous phase retrospective
   - Learn from mistakes and successes
   - Apply lessons to new phase planning
   - Start with context from previous work

---

## Key Principles

### For BMad Agents

1. **Read planning docs first** - All requirements are in `docs/04_MVP_Development/planning/` (v3.3)
2. **Do NOT make assumptions** - If requirements are unclear, reference planning docs or ask user
3. **Document decisions** - Write technical_decisions.md as you code, not after
4. **Update checklists** - Check off tasks immediately after completion
5. **Learn from retrospectives** - Read previous phase retrospectives before starting new phase
6. **Strategic order matters** - Data → Frontend → Architecture → Agents (for a reason!)

### For Developers

1. **Single source of truth** - This IMPLEMENTATION_GUIDE.md is the entry point
2. **Phase isolation** - Complete one phase before starting next
3. **Continuous documentation** - Docs and code evolve together
4. **Validate assumptions** - If planning docs contradict, ask before proceeding
5. **Architecture stability** - Requirements may change, but architecture doesn't

---

## Troubleshooting & Common Issues

### Issue 1: Task Taking Longer Than Estimated

**Symptoms:** Task estimate was 2 hours, actual is 6+ hours

**Solutions:**
- Break task into smaller subtasks
- Document why it's taking longer in technical_decisions.md
- Update estimate in implementation plan
- Adjust remaining timeline accordingly
- Flag in daily standup/check-in

### Issue 2: Blocker Discovered

**Symptoms:** Can't proceed with current task due to missing prerequisite or external dependency

**Solutions:**
- Document blocker in implementation plan risk register
- Mark task as 🔴 Blocked in checklist
- Update phase status to 🔴 Blocked if critical
- Identify workaround or alternative approach
- Escalate to user/team lead if blocking >1 day

### Issue 3: Planning Docs Contradict Each Other

**Symptoms:** PRD says X, but Architecture doc says Y

**Solutions:**
- **Do not guess** - Always ask user for clarification
- Document the contradiction in technical_decisions.md
- Reference specific line numbers from both docs
- Wait for clarification before proceeding
- Update planning docs once resolved

### Issue 4: Scope Creep During Implementation

**Symptoms:** Discovering new features/requirements while coding

**Solutions:**
- Log new features in technical_decisions.md under "Future Enhancements"
- **Do not add to current phase** - stick to implementation plan
- Add to backlog or next phase
- Discuss with user if critical for current phase
- Update phase scope only if user approves

### Issue 5: Tests Failing at Checkpoint

**Symptoms:** Validation checkpoint reveals bugs or test failures

**Solutions:**
- **Do not mark phase complete** - fix issues first
- Add debugging tasks to checklist
- Document root cause in technical_decisions.md
- Update timeline if fixes will take significant time
- Run validation checkpoint again after fixes

### Issue 6: Requirements Unclear from Planning Docs

**Symptoms:** Planning doc mentions feature but lacks implementation details

**Solutions:**
- **First:** Re-read ALL relevant planning docs thoroughly
- **Second:** Search for related sections in other planning docs
- **Third:** Document the ambiguity in technical_decisions.md
- **Fourth:** Ask user for clarification with specific questions
- **Never:** Guess or assume intended behavior

---

## Tips for Effective Implementation

### Do ✅

- **Start each day by reading the implementation plan**
- **Reference planning docs (v3.3) for ALL requirements**
- **Update checklist immediately after completing tasks**
- **Commit code + docs together in small batches**
- **Write technical decisions while context is fresh**
- **Ask questions early when requirements are unclear**
- **Track actual time vs estimates for learning**
- **Run validation checkpoints at defined milestones**
- **Write retrospective immediately after phase completion**
- **Follow strategic order: Data → Frontend → Architecture → Agents**

### Don't ❌

- **Don't skip reading previous phase retrospectives**
- **Don't make assumptions about requirements (reference planning docs!)**
- **Don't wait until end of phase to write all docs**
- **Don't add unplanned features without user approval**
- **Don't ignore validation checkpoint failures**
- **Don't commit code without updating docs**
- **Don't guess when planning docs are unclear**
- **Don't mark tasks complete before they're truly done**
- **Don't rush through retrospectives**
- **Don't skip frontend mockup phase (validates UX before backend)**

---

## Workflow Summary Diagram

```
┌─────────────────────────────────────────────────────────┐
│  BEFORE PHASE START                                     │
│  - Read ALL planning docs (v3.3)                        │
│  - Review previous retrospective                        │
│  - Read implementation plan                             │
│  - Verify prerequisites                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE START                                            │
│  - Activate BMad agent with handoff message             │
│  - Review all 4 phase documents                         │
│  - Set up environment/prerequisites                     │
│  - Create implementation plan (reference planning docs) │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  DAILY WORK LOOP (Repeat until phase complete)         │
│                                                         │
│  Morning:                                               │
│  └─ Review plan → Check tasks → Verify dependencies    │
│     → Review planning docs if unclear                   │
│                                                         │
│  During Work:                                           │
│  └─ Code → Document decisions → Update checklist       │
│     └─ Reference planning docs for requirements        │
│     └─ Commit (code + docs together)                   │
│                                                         │
│  End of Day:                                            │
│  └─ Update plan → Note blockers → Plan tomorrow        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  VALIDATION CHECKPOINTS                                 │
│  - Mid-phase (50%)                                      │
│  - Pre-completion (code done)                           │
│  - Final (tests passing)                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE COMPLETION                                       │
│  1. Finish all tasks                                    │
│  2. Write retrospective                                 │
│  3. Update README status                                │
│  4. Final commit                                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  HANDOFF TO NEXT PHASE                                  │
│  - Share retrospective                                  │
│  - Update next phase to "Ready to Start"                │
│  - Brief next phase owner                               │
└─────────────────────────────────────────────────────────┘
```

---

## Success Metrics

**Documentation Quality:**
- [ ] All 4 docs complete per phase
- [ ] Technical decisions have clear rationale
- [ ] Checklists match implementation plan
- [ ] Retrospectives capture lessons learned

**Implementation Progress:**
- [ ] Phase 1: 38 CSV files generated, MAPE 12-18% validated
- [ ] Phase 2: All 7 dashboard sections functional with mock data
- [ ] Phase 3: Backend architecture + API scaffolding complete
- [ ] Phase 4: Orchestrator workflow coordination functional
- [ ] Phase 5: Demand Agent forecast accuracy <20% MAPE
- [ ] Phase 6: Inventory Agent allocation complete in <3s
- [ ] Phase 7: Pricing Agent markdown calculation <1s
- [ ] Phase 8: End-to-end workflow <60s runtime, MAPE 12-18%

---

## Current Priority: Phase 1

✅ **All v3.3 planning documents are ready!**

**Next Step:** Copy the handoff message below and start implementation:

```
*agent dev

Task: Implement mock data generation script for parameter-driven retail forecasting system

Reference: docs/04_MVP_Development/planning/6_data_specification_v3.2.md

Planning Docs (v3.3):
- Data Specification: docs/04_MVP_Development/planning/6_data_specification_v3.2.md
- Process Workflow: docs/04_MVP_Development/planning/2_process_workflow_v3.3.md
- Product Brief: docs/04_MVP_Development/planning/1_product_brief_v3.3.md

Key Deliverables:
- historical_sales_2022_2024.csv (54,750 rows, 3 categories)
- store_attributes.csv (50 stores, 7 K-means features)
- 36 weekly actuals CSVs (3 scenarios × 12 weeks each)
- Validation suite (6 types: Completeness, Quality, Format, Statistical, Pattern, Weekly)
- README.md with data dictionary

Target MAPE: 12-18% across all 3 scenarios
Week 5 Variance: >20% in all scenarios (to trigger re-forecast)
```

---

## Quick Reference Cheat Sheet

### Daily Checklist

**Every Morning:**
- [ ] Read implementation plan for today's tasks
- [ ] Check task dependencies
- [ ] Review yesterday's progress
- [ ] Review relevant planning docs if unclear

**During Work:**
- [ ] Update checklist as tasks complete
- [ ] Document decisions in technical_decisions.md
- [ ] Commit code + docs together frequently
- [ ] Reference planning docs for requirements

**Every Evening:**
- [ ] Update implementation plan with actuals
- [ ] Note any blockers
- [ ] Plan tomorrow's work

### Phase Completion Checklist

- [ ] All tasks in checklist marked ✅
- [ ] All code committed and pushed
- [ ] All tests passing
- [ ] technical_decisions.md updated
- [ ] retrospective.md written
- [ ] IMPLEMENTATION_GUIDE.md phase status updated to ✅
- [ ] Next phase status updated to 🟡

### Planning Documents Quick Links (v3.3)

**All Requirements Source:**
- Planning Guide: `../planning/0_PLANNING_GUIDE.md`
- Product Brief v3.3: `../planning/1_product_brief_v3.3.md`
- Process Workflow v3.3: `../planning/2_process_workflow_v3.3.md`
- Technical Architecture v3.3: `../planning/3_technical_architecture_v3.3.md`
- PRD v3.3: `../planning/4_prd_v3.3.md`
- Frontend Spec v3.3: `../planning/5_front-end-spec_v3.3.md`
- Data Specification v3.2: `../planning/6_data_specification_v3.2.md`

### Implementation Phase Quick Links

**Current Phase (Phase 1):**
- Implementation Plan: `./phase_1_data_generation/implementation_plan.md`
- Technical Decisions: `./phase_1_data_generation/technical_decisions.md`
- Checklist: `./phase_1_data_generation/checklist.md`
- Retrospective: `./phase_1_data_generation/retrospective.md`

### Git Commit Template

```bash
git commit -m "[Phase X]: [Action] - [Description]

[Detailed notes]
- [Bullet 1]
- [Bullet 2]

References planning docs:
- [Doc name]: [Relevant section]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

**Last Updated:** 2025-10-17
**Next Review:** After Phase 1 completion
**Status:** Ready for Phase 1 Implementation ✅
**Strategic Order:** Data → Frontend → Backend Architecture → Agents (for architecture stability)
