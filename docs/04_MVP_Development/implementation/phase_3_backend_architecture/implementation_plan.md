# Phase 3: Backend Architecture - Implementation Plan

**Phase:** 3 of 8
**Goal:** Set up FastAPI backend with database, REST API, parameter extraction, and agent scaffolding
**Agent:** `*agent architect`
**Duration Estimate:** 5-7 days (46 hours)
**Actual Duration:** TBD
**Status:** ✅ Planning Complete - All Stories Ready for Implementation

---

## Requirements Source

- **Primary:** `planning/3_technical_architecture_v3.3.md` - Complete backend architecture
- **Secondary:** `planning/2_process_workflow_v3.3.md` - Agent workflow examples
- **Reference:** `planning/4_prd_v3.3.md` - Business requirements

---

## Key Deliverables

1. **FastAPI Project Setup**
   - UV package manager configuration
   - Project structure with monorepo layout
   - Environment configuration (.env)
   - Logging and error handling middleware

2. **Database Layer (SQLite)**
   - SQLAlchemy models for all entities
   - Hybrid schema (normalized + JSON columns)
   - Migration scripts (Alembic)
   - Seed data from Phase 1 CSVs

3. **Pydantic Models**
   - SeasonParameters model (5 key parameters)
   - Category, Store, StoreCluster models
   - Forecast, Allocation, Markdown models
   - Request/Response DTOs

4. **REST API Endpoints (18 total)**
   - **Parameter Extraction:** POST /api/parameters/extract
   - **Workflow:** POST /api/workflows/forecast, POST /api/workflows/reforecast, GET /api/workflows/{id}
   - **Resource:** GET /api/forecasts, GET /api/forecasts/{id}, GET /api/allocations/{id}, GET /api/markdowns/{id}, GET /api/variance/{id}/week/{week}
   - **Data Management:** POST /api/data/upload-historical-sales, POST /api/data/upload-weekly-sales, GET /api/categories, GET /api/stores, GET /api/stores/clusters
   - **Approvals:** POST /api/approvals/manufacturing, POST /api/approvals/markdown
   - **Agent Debug (optional):** POST /api/agents/demand/forecast, POST /api/agents/inventory/allocate, POST /api/agents/pricing/analyze

5. **WebSocket Server**
   - Real-time agent status updates (WS /api/workflows/{id}/stream)
   - 6 message types (agent_started, agent_progress, agent_completed, human_input_required, workflow_complete, error)
   - Connection management with heartbeat
   - Message broadcasting to all connected clients

6. **OpenAI Agents SDK Integration**
   - Orchestrator agent scaffolding
   - Demand agent scaffolding
   - Inventory agent scaffolding
   - Pricing agent scaffolding
   - Agent handoff configuration

7. **Parameter Extraction Service**
   - LLM prompt for parameter extraction
   - Natural language → SeasonParameters parser
   - Confidence scoring
   - Validation and fallback logic

8. **ML Pipeline Scaffolding**
   - Prophet model placeholder
   - ARIMA model placeholder
   - K-means clustering placeholder
   - Data preprocessing utilities

9. **Configuration & Testing**
   - OpenAI API integration
   - Environment variables (.env.example)
   - Basic health checks
   - API endpoint tests (pytest)

---

## Task Breakdown

### Task 1: Project Setup & UV Configuration ✅ STORY READY
**Story:** `PHASE3-001-project-setup-uv-configuration.md`
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** None
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Install UV package manager (`pip install uv`)
- [ ] Initialize Python project with `uv init`
- [ ] Create `pyproject.toml` with all dependencies
- [ ] Set up monorepo structure (backend/ and frontend/ folders)
- [ ] Configure `.gitignore` for Python/Node
- [ ] Create `backend/.env.example` with required variables

**Dependencies to Add:**
```toml
[project]
name = "fashion-forecast-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "openai-agents-sdk>=0.3.3",
    "openai>=1.54.0",
    "sqlalchemy>=2.0.35",
    "alembic>=1.13.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "pandas>=2.2.0",
    "numpy>=1.26.0",
    "prophet>=1.1.6",
    "pmdarima>=2.0.4",
    "scikit-learn>=1.5.0",
    "python-multipart>=0.0.12",
    "websockets>=13.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "mypy>=1.13.0",
    "ruff>=0.7.0",
]
```

### Task 2: Database Schema & Models ✅ STORY READY
**Story:** `PHASE3-002-database-schema-models.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 1
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Install SQLAlchemy + Alembic
- [ ] Create `backend/app/db/base.py` (database connection)
- [ ] Create SQLAlchemy models:
  - [ ] `models/category.py` (categories table)
  - [ ] `models/store.py` (stores table)
  - [ ] `models/store_cluster.py` (store_clusters table)
  - [ ] `models/parameters.py` (season_parameters table) ⭐ NEW
  - [ ] `models/forecast.py` (forecasts table with JSON columns)
  - [ ] `models/allocation.py` (allocations table with JSON columns)
  - [ ] `models/markdown.py` (markdown_decisions table)
  - [ ] `models/actuals.py` (weekly_actuals table)
- [ ] Initialize Alembic (`alembic init migrations`)
- [ ] Generate initial migration (`alembic revision --autogenerate`)
- [ ] Run migration (`alembic upgrade head`)

**Database Schema (Hybrid Design):**
- Normalized tables: categories, stores, store_clusters, season_parameters
- JSON columns: weekly_demand_curve (list), store_allocations (list), cluster_distribution (list)

### Task 3: Pydantic Models (DTOs) ✅ STORY READY
**Story:** `PHASE3-003-pydantic-schemas-dtos.md`
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `backend/app/schemas/` folder
- [ ] Implement `schemas/parameters.py`:
  - [ ] `SeasonParameters` model (5 key parameters)
  - [ ] `ParameterExtractionRequest` (natural language input)
  - [ ] `ParameterExtractionResponse` (extracted parameters + confidence)
- [ ] Implement `schemas/category.py` (Category model)
- [ ] Implement `schemas/store.py` (Store, StoreCluster models)
- [ ] Implement `schemas/forecast.py` (Forecast, WeeklyDemand, ClusterDistribution models)
- [ ] Implement `schemas/allocation.py` (AllocationPlan, StoreAllocation models)
- [ ] Implement `schemas/markdown.py` (MarkdownDecision model)
- [ ] Implement `schemas/workflow.py` (WorkflowRequest, AgentStatus, WorkflowResponse)
- [ ] Add validation and examples to all models

### Task 4: FastAPI Application Setup ✅ STORY READY
**Story:** `PHASE3-004-fastapi-application-setup.md`
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 1
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `backend/app/main.py` (FastAPI app instance)
- [ ] Configure CORS middleware (allow frontend origin)
- [ ] Add logging middleware (request/response logging)
- [ ] Add error handling middleware (500 errors → JSON)
- [ ] Create `backend/app/core/config.py` (Pydantic Settings)
- [ ] Load environment variables (.env)
- [ ] Create health check endpoint (`GET /api/health`)
- [ ] Set up API router structure (`backend/app/api/`)

**Environment Variables (.env):**
```bash
# OpenAI
OPENAI_API_KEY=sk-your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=sqlite:///./fashion_forecast.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Task 5: Parameter Extraction API ✅ STORY READY
**Story:** `PHASE3-005-parameter-extraction-api.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 3, Task 4
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `backend/app/services/parameter_extractor.py`
- [ ] Implement LLM prompt for parameter extraction
- [ ] Create `POST /api/parameters/extract` endpoint
- [ ] Parse natural language input and call OpenAI
- [ ] Extract 5 parameters to `SeasonParameters` object
- [ ] Add confidence scoring (high/medium/low)
- [ ] Implement fallback logic (default to 12 weeks if unclear)
- [ ] Return JSON response with parameters + reasoning

**LLM Prompt Template:**
```
You are a retail season planning assistant. Extract 5 key parameters from user input:

1. forecast_horizon_weeks: How many weeks (default 12)
2. season_start_date: When does season start (default: next Monday)
3. replenishment_strategy: "none", "weekly", or "bi-weekly" (default: "weekly")
4. dc_holdback_percentage: 0.0 to 1.0 (default: 0.45)
5. markdown_checkpoint_week: Week for markdown check (null if no markdowns)

User Input: "{user_input}"

Return JSON only.
```

### Task 6: Data Seeding & CSV Utilities ✅ STORY READY
**Story:** `PHASE3-006-data-seeding-csv-utilities.md`
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `backend/app/utils/csv_parser.py` (CSV parsing utilities)
- [ ] Implement CSV validation functions (check required columns, data types)
- [ ] Create seed data script to load Phase 1 CSVs into database
- [ ] Load store_attributes.csv → stores table (50 stores)
- [ ] Load historical_sales_2022_2024.csv → historical_sales table
- [ ] Create database backup utility
- [ ] Document CSV format requirements

**Note:** Actual CSV upload endpoints (with multipart/form-data) are implemented in Task 14. This task focuses on seeding the database with Phase 1 CSV data for development/testing.

### Task 7: Workflow Orchestration API ✅ STORY READY
**Story:** `PHASE3-007-workflow-orchestration-api.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 4, Task 5
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `POST /api/workflows/forecast` endpoint (start pre-season forecast)
- [ ] Accept `SeasonParameters` in request body
- [ ] Create workflow session in database
- [ ] Initialize Orchestrator agent (placeholder)
- [ ] Return workflow_id and WebSocket URL
- [ ] Create `POST /api/workflows/reforecast` endpoint (variance-triggered or manual re-forecast)
- [ ] Accept forecast_id, actual_sales_week_1_to_n, remaining_weeks
- [ ] Create `GET /api/workflows/{id}` endpoint (status check via polling)
- [ ] Create `GET /api/workflows/{id}/results` endpoint (final results)

### Task 8: WebSocket Server ✅ STORY READY
**Story:** `PHASE3-008-websocket-server.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 4
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `backend/app/websocket/manager.py` (connection manager)
- [ ] Implement WebSocket endpoint (`WS /api/workflows/{workflow_id}/stream`)
- [ ] Handle connection lifecycle (connect, disconnect, heartbeat)
- [ ] Implement message broadcasting (agent status updates)
- [ ] Create `backend/app/schemas/websocket.py` with 6 message type schemas:
  - [ ] `agent_started` (agent name, timestamp)
  - [ ] `agent_progress` (agent name, message, progress_pct, timestamp)
  - [ ] `agent_completed` (agent name, duration_seconds, result, timestamp)
  - [ ] `human_input_required` (agent name, action, data, options, timestamp)
  - [ ] `workflow_complete` (workflow_id, duration_seconds, result, timestamp)
  - [ ] `error` (agent name, error_message, timestamp)
- [ ] Test with frontend WebSocket client

**Message Format Examples:**
```json
// agent_progress
{
  "type": "agent_progress",
  "agent": "Demand Agent",
  "message": "Running Prophet forecasting model...",
  "progress_pct": 33,
  "timestamp": "2025-10-12T10:30:20Z"
}

// human_input_required
{
  "type": "human_input_required",
  "agent": "Inventory Agent",
  "action": "approve_manufacturing_order",
  "data": {
    "manufacturing_qty": 9600,
    "initial_allocation": 5280,
    "holdback": 4320
  },
  "options": ["modify", "accept"],
  "timestamp": "2025-10-12T10:30:45Z"
}
```

### Task 9: OpenAI Agents SDK Integration ✅ STORY READY
**Story:** `PHASE3-009-openai-agents-sdk-integration.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 4, Task 5
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `backend/app/agents/` folder
- [ ] Implement `agents/orchestrator.py` (Orchestrator Agent)
- [ ] Implement `agents/demand.py` (Demand Agent placeholder)
- [ ] Implement `agents/inventory.py` (Inventory Agent placeholder)
- [ ] Implement `agents/pricing.py` (Pricing Agent placeholder)
- [ ] Configure agent handoffs (Orchestrator → Demand → Inventory → Pricing)
- [ ] Pass `SeasonParameters` in handoff context
- [ ] Add LLM reasoning prompts (how parameters affect decisions)
- [ ] Test agent handoff flow with mock data

**Orchestrator Agent Structure:**
```python
from openai_agents import Agent

orchestrator = Agent(
    name="Orchestrator",
    instructions="""
    You coordinate 3 specialized agents based on extracted parameters.
    - If no replenishment: skip replenishment phase
    - If no markdowns: skip pricing agent
    - Monitor variance >20% and trigger re-forecast
    """,
    model="gpt-4o-mini",
    handoffs=["demand", "inventory", "pricing"]
)
```

### Task 10: Approval Endpoints ✅ STORY READY
**Story:** `PHASE3-010-approval-endpoints.md`
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 4, Task 7
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `POST /api/approvals/manufacturing` endpoint
- [ ] Accept manufacturing quantity, return confirmation
- [ ] Create `POST /api/approvals/markdown` endpoint
- [ ] Accept markdown %, return confirmation
- [ ] Update workflow status in database
- [ ] Trigger agent continuation via WebSocket

### Task 11: ML Pipeline Scaffolding ✅ STORY READY
**Story:** `PHASE3-011-ml-pipeline-scaffolding.md`
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `backend/app/ml/` folder
- [ ] Implement `ml/prophet_model.py` (placeholder - returns mock forecast)
- [ ] Implement `ml/arima_model.py` (placeholder - returns mock forecast)
- [ ] Implement `ml/clustering.py` (placeholder - returns 3 mock clusters)
- [ ] Create `ml/ensemble.py` (combine Prophet + ARIMA)
- [ ] Add data preprocessing utilities
- [ ] Document interfaces for Phase 5 (Demand Agent) implementation

**Note:** Actual ML implementation happens in Phase 5. This task just creates the structure.

### Task 12: Configuration & Environment Setup ✅ STORY READY
**Story:** `PHASE3-012-configuration-environment-setup.md`
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 4
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `.env.example` with all required variables
- [ ] Configure OpenAI API client
- [ ] Test API connection (list models)
- [ ] Set up logging (file + console)
- [ ] Configure CORS for frontend origin
- [ ] Add request/response validation
- [ ] Create development startup script (`scripts/dev.sh`)

### Task 13: Testing & Documentation ✅ STORY READY
**Story:** `PHASE3-013-testing-documentation.md`
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 1-12, Task 14
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Install pytest + pytest-asyncio
- [ ] Write tests for parameter extraction endpoint
- [ ] Write tests for data upload endpoints
- [ ] Write tests for workflow creation endpoint
- [ ] Write tests for WebSocket connection
- [ ] Write tests for resource endpoints (forecasts, allocations, markdowns, variance)
- [ ] Create API documentation (OpenAPI/Swagger)
- [ ] Write backend README.md with setup instructions
- [ ] Document all environment variables

### Task 14: Resource & Data Management Endpoints ✅ STORY READY
**Story:** `PHASE3-014-resource-data-management-endpoints.md`
**Estimate:** 6 hours
**Actual:** TBD
**Dependencies:** Task 2, Task 3, Task 4
**Status:** ✅ Story Ready for Implementation

**Subtasks:**
- [ ] Create `GET /api/forecasts` endpoint (list all forecasts)
  - [ ] Return forecast_id, category_name, season, total_season_demand, created_at
- [ ] Create `GET /api/forecasts/{forecast_id}` endpoint (detailed forecast)
  - [ ] Return full forecast with weekly_demand_curve, cluster_distribution, forecasting_method, prophet_forecast, arima_forecast
- [ ] Create `GET /api/allocations/{forecast_id}` endpoint (allocation plan)
  - [ ] Return manufacturing_qty, safety_stock_percentage, initial_allocation_total, holdback_total, store_allocations array
- [ ] Create `GET /api/markdowns/{forecast_id}` endpoint (markdown recommendations)
  - [ ] Return week_number, sell_through_pct, recommended_markdown_pct, elasticity_coefficient, reasoning
- [ ] Create `GET /api/variance/{forecast_id}/week/{week_number}` endpoint (variance analysis)
  - [ ] Return forecasted_cumulative, actual_cumulative, variance_pct, threshold_exceeded, action_taken
- [ ] Create `GET /api/categories` endpoint (list all categories auto-detected from CSV)
  - [ ] Return category_id, category_name, row_count
- [ ] Create `GET /api/stores` endpoint (list all 50 stores with attributes)
  - [ ] Return store_id, store_name, cluster_id, store_size_sqft, location_tier, median_income, etc.
- [ ] Create `GET /api/stores/clusters` endpoint (list 3 clusters with store assignments)
  - [ ] Return cluster_id, cluster_name, fashion_tier, store_count
- [ ] Create `POST /api/data/upload-historical-sales` endpoint (CSV import)
  - [ ] Accept multipart/form-data with CSV file
  - [ ] Parse columns: [date, category, store_id, quantity_sold, revenue]
  - [ ] Auto-detect categories and import to historical_sales table
  - [ ] Return rows_imported, date_range, categories_detected
- [ ] Create `POST /api/data/upload-weekly-sales` endpoint (actual sales for variance)
  - [ ] Accept multipart/form-data with CSV file + forecast_id
  - [ ] Parse columns: [store_id, week_number, units_sold]
  - [ ] Check variance_pct > 20% threshold
  - [ ] Auto-trigger re-forecast if threshold exceeded
  - [ ] Return rows_imported, week_number, variance_check result
- [ ] Create `POST /api/agents/demand/forecast` endpoint (direct Demand Agent call - optional for debugging)
- [ ] Create `POST /api/agents/inventory/allocate` endpoint (direct Inventory Agent call - optional)
- [ ] Create `POST /api/agents/pricing/analyze` endpoint (direct Pricing Agent call - optional)

**Note:** This task adds all resource and data management endpoints from planning spec (lines 1727-1903) that were missing in original Task 7. These endpoints are required for frontend Sections 4-7 and Performance Report Page.

---

## Total Estimates vs Actuals

- **Total Tasks:** 14
- **Estimated Time:** 46 hours (6-8 days at 6-8h/day)
  - Task 1: 2h, Task 2: 4h, Task 3: 3h, Task 4: 3h, Task 5: 4h
  - Task 6: 2h (reduced from 3h), Task 7: 4h (increased from 3h)
  - Task 8: 4h (increased from 3h), Task 9: 4h, Task 10: 2h
  - Task 11: 3h, Task 12: 2h, Task 13: 3h, Task 14: 6h (NEW)
- **Actual Time:** TBD
- **Variance:** TBD
- **Change from Original:** +7 hours (39h → 46h) due to missing REST API endpoints

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (40% complete)
**After:** Task 5 complete
**Verify:**
- [ ] FastAPI server runs without errors
- [ ] Database tables created successfully (all 10 tables from planning spec)
- [ ] Parameter extraction endpoint works (test with Zara-style input)
- [ ] Health check endpoint returns 200 OK
- [ ] Environment variables loaded correctly
- [ ] OpenAI connection working

### Checkpoint 2: Pre-Completion (80% complete)
**After:** Task 11 complete
**Verify:**
- [ ] Core workflow endpoints functional (POST /api/workflows/forecast, POST /api/workflows/reforecast)
- [ ] WebSocket connection established with 6 message types broadcasting correctly
- [ ] Agent scaffolding created (4 agents with handoff configuration)
- [ ] Data seeding works (Phase 1 CSVs loaded into SQLite)
- [ ] Workflow creation returns workflow_id and WebSocket URL

### Checkpoint 3: Final
**After:** Task 14 complete
**Verify:**
- [ ] All 18 REST API endpoints functional (workflow, resource, data management)
- [ ] All tests passing (pytest with resource endpoint coverage)
- [ ] OpenAPI docs accessible at /docs with all endpoints documented
- [ ] Backend README complete with setup instructions
- [ ] Frontend can connect and call all endpoints
- [ ] CSV upload endpoints working (historical sales, weekly actuals)
- [ ] Variance auto-triggers re-forecast when threshold exceeded
- [ ] Ready for handoff to Phase 4 (Orchestrator Agent implementation)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI API quota limits | Medium | High | Use exponential backoff, implement rate limiting, fallback to mock responses |
| SQLAlchemy JSON column issues | Low | Medium | Test JSON serialization early, use hybrid approach (normalized + JSON) |
| WebSocket connection drops | Medium | Medium | Implement reconnection logic, heartbeat ping/pong |
| UV package manager unfamiliar | Medium | Low | Follow official docs, fallback to pip if needed |
| Alembic migration conflicts | Low | Medium | Use autogenerate carefully, review migrations before applying |

---

## Notes

- This phase builds the **backend foundation** only
- Agent logic is scaffolded (placeholder prompts, mock outputs)
- ML models return mock data (actual implementation in Phase 5-7)
- Focus on API contracts matching frontend expectations
- WebSocket must work for real-time agent updates
- All 5 parameters must be extractable from natural language
- Database schema must support parameter-driven workflows

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-19
**Status:** ✅ Planning Complete - All Stories Ready for Implementation
**Stories Location:** `stories/PHASE3-001.md` through `stories/PHASE3-014.md`
**Total Story Count:** 14/14 (100%)
