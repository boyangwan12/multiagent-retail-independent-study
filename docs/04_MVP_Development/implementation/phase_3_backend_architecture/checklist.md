# Phase 3: Backend Architecture - Checklist

**Phase:** 3 of 8
**Agent:** `*agent architect`
**Status:** Not Started
**Progress:** 0/14 tasks complete

---

## Task Checklist

### Task 1: Project Setup & UV Configuration
- [ ] Install UV package manager (`pip install uv`)
- [ ] Initialize Python project with `uv init`
- [ ] Create `pyproject.toml` with all dependencies
- [ ] Set up monorepo structure (backend/ and frontend/ folders)
- [ ] Configure `.gitignore` for Python/Node
- [ ] Create `backend/.env.example` with required variables
**Status:** Not Started

### Task 2: Database Schema & Models
- [ ] Install SQLAlchemy + Alembic
- [ ] Create `backend/app/db/base.py` (database connection)
- [ ] Create SQLAlchemy models (8 models: category, store, store_cluster, parameters, forecast, allocation, markdown, actuals)
- [ ] Initialize Alembic (`alembic init migrations`)
- [ ] Generate initial migration (`alembic revision --autogenerate`)
- [ ] Run migration (`alembic upgrade head`)
**Status:** Not Started

### Task 3: Pydantic Models (DTOs)
- [ ] Create `backend/app/schemas/` folder
- [ ] Implement `schemas/parameters.py` (SeasonParameters, ParameterExtractionRequest/Response)
- [ ] Implement `schemas/category.py` (Category model)
- [ ] Implement `schemas/store.py` (Store, StoreCluster models)
- [ ] Implement `schemas/forecast.py` (Forecast, WeeklyDemand, ClusterDistribution)
- [ ] Implement `schemas/allocation.py` (AllocationPlan, StoreAllocation)
- [ ] Implement `schemas/markdown.py` (MarkdownDecision)
- [ ] Implement `schemas/workflow.py` (WorkflowRequest, AgentStatus, WorkflowResponse)
**Status:** Not Started

### Task 4: FastAPI Application Setup
- [ ] Create `backend/app/main.py` (FastAPI app instance)
- [ ] Configure CORS middleware (allow frontend origin)
- [ ] Add logging middleware (request/response logging)
- [ ] Add error handling middleware (500 errors → JSON)
- [ ] Create `backend/app/core/config.py` (Pydantic Settings)
- [ ] Load environment variables (.env)
- [ ] Create health check endpoint (`GET /api/health`)
- [ ] Set up API router structure (`backend/app/api/`)
**Status:** Not Started

### Task 5: Parameter Extraction API
- [ ] Create `backend/app/services/parameter_extractor.py`
- [ ] Implement LLM prompt for parameter extraction
- [ ] Create `POST /api/parameters/extract` endpoint
- [ ] Parse natural language input and call Azure OpenAI
- [ ] Extract 5 parameters to `SeasonParameters` object
- [ ] Add confidence scoring (high/medium/low)
- [ ] Implement fallback logic (default to 12 weeks if unclear)
- [ ] Return JSON response with parameters + reasoning
**Status:** Not Started

### Task 6: Data Seeding & CSV Utilities
- [ ] Create `backend/app/utils/csv_parser.py` (CSV parsing utilities)
- [ ] Implement CSV validation functions (check required columns, data types)
- [ ] Create seed data script to load Phase 1 CSVs into database
- [ ] Load store_attributes.csv → stores table (50 stores)
- [ ] Load historical_sales_2022_2024.csv → historical_sales table
- [ ] Create database backup utility
- [ ] Document CSV format requirements
**Status:** Not Started

### Task 7: Workflow Orchestration API
- [ ] Create `POST /api/workflows/forecast` endpoint (start pre-season forecast)
- [ ] Accept `SeasonParameters` in request body
- [ ] Create workflow session in database
- [ ] Initialize Orchestrator agent (placeholder)
- [ ] Return workflow_id and WebSocket URL
- [ ] Create `POST /api/workflows/reforecast` endpoint (variance-triggered or manual re-forecast)
- [ ] Accept forecast_id, actual_sales_week_1_to_n, remaining_weeks
- [ ] Create `GET /api/workflows/{id}` endpoint (status check via polling)
- [ ] Create `GET /api/workflows/{id}/results` endpoint (final results)
**Status:** Not Started

### Task 8: WebSocket Server
- [ ] Create `backend/app/websocket/manager.py` (connection manager)
- [ ] Implement WebSocket endpoint (`WS /api/workflows/{workflow_id}/stream`)
- [ ] Handle connection lifecycle (connect, disconnect, heartbeat)
- [ ] Implement message broadcasting (agent status updates)
- [ ] Create `backend/app/schemas/websocket.py` with 6 message type schemas
- [ ] Implement `agent_started` message type (agent name, timestamp)
- [ ] Implement `agent_progress` message type (agent name, message, progress_pct, timestamp)
- [ ] Implement `agent_completed` message type (agent name, duration_seconds, result, timestamp)
- [ ] Implement `human_input_required` message type (agent name, action, data, options, timestamp)
- [ ] Implement `workflow_complete` message type (workflow_id, duration_seconds, result, timestamp)
- [ ] Implement `error` message type (agent name, error_message, timestamp)
- [ ] Test with frontend WebSocket client
**Status:** Not Started

### Task 9: OpenAI Agents SDK Integration
- [ ] Create `backend/app/agents/` folder
- [ ] Implement `agents/orchestrator.py` (Orchestrator Agent)
- [ ] Implement `agents/demand.py` (Demand Agent placeholder)
- [ ] Implement `agents/inventory.py` (Inventory Agent placeholder)
- [ ] Implement `agents/pricing.py` (Pricing Agent placeholder)
- [ ] Configure agent handoffs (Orchestrator → Demand → Inventory → Pricing)
- [ ] Pass `SeasonParameters` in handoff context
- [ ] Add LLM reasoning prompts (how parameters affect decisions)
- [ ] Test agent handoff flow with mock data
**Status:** Not Started

### Task 10: Approval Endpoints
- [ ] Create `POST /api/approvals/manufacturing` endpoint
- [ ] Accept manufacturing quantity, return confirmation
- [ ] Create `POST /api/approvals/markdown` endpoint
- [ ] Accept markdown %, return confirmation
- [ ] Update workflow status in database
- [ ] Trigger agent continuation via WebSocket
**Status:** Not Started

### Task 11: ML Pipeline Scaffolding
- [ ] Create `backend/app/ml/` folder
- [ ] Implement `ml/prophet_model.py` (placeholder - returns mock forecast)
- [ ] Implement `ml/arima_model.py` (placeholder - returns mock forecast)
- [ ] Implement `ml/clustering.py` (placeholder - returns 3 mock clusters)
- [ ] Create `ml/ensemble.py` (combine Prophet + ARIMA)
- [ ] Add data preprocessing utilities
- [ ] Document interfaces for Phase 5 (Demand Agent) implementation
**Status:** Not Started

### Task 12: Configuration & Environment Setup
- [ ] Create `.env.example` with all required variables
- [ ] Configure Azure OpenAI API client
- [ ] Test API connection (list models)
- [ ] Set up logging (file + console)
- [ ] Configure CORS for frontend origin
- [ ] Add request/response validation
- [ ] Create development startup script (`scripts/dev.sh`)
**Status:** Not Started

### Task 13: Testing & Documentation
- [ ] Install pytest + pytest-asyncio
- [ ] Write tests for parameter extraction endpoint
- [ ] Write tests for data upload endpoints
- [ ] Write tests for workflow creation endpoint
- [ ] Write tests for WebSocket connection
- [ ] Write tests for resource endpoints (forecasts, allocations, markdowns, variance)
- [ ] Create API documentation (OpenAPI/Swagger)
- [ ] Write backend README.md with setup instructions
- [ ] Document all environment variables
**Status:** Not Started

### Task 14: Resource & Data Management Endpoints ⭐ NEW
- [ ] Create `GET /api/forecasts` endpoint (list all forecasts)
- [ ] Create `GET /api/forecasts/{forecast_id}` endpoint (detailed forecast)
- [ ] Create `GET /api/allocations/{forecast_id}` endpoint (allocation plan)
- [ ] Create `GET /api/markdowns/{forecast_id}` endpoint (markdown recommendations)
- [ ] Create `GET /api/variance/{forecast_id}/week/{week_number}` endpoint (variance analysis)
- [ ] Create `GET /api/categories` endpoint (list all categories auto-detected from CSV)
- [ ] Create `GET /api/stores` endpoint (list all 50 stores with attributes)
- [ ] Create `GET /api/stores/clusters` endpoint (list 3 clusters with store assignments)
- [ ] Create `POST /api/data/upload-historical-sales` endpoint (CSV import with multipart/form-data)
- [ ] Create `POST /api/data/upload-weekly-sales` endpoint (actual sales for variance, auto-triggers re-forecast if threshold exceeded)
- [ ] Create `POST /api/agents/demand/forecast` endpoint (direct Demand Agent call - optional for debugging)
- [ ] Create `POST /api/agents/inventory/allocate` endpoint (direct Inventory Agent call - optional)
- [ ] Create `POST /api/agents/pricing/analyze` endpoint (direct Pricing Agent call - optional)
**Status:** Not Started

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (40% complete)
- [ ] FastAPI server runs without errors
- [ ] Database tables created successfully (all 10 tables from planning spec)
- [ ] Parameter extraction endpoint works (test with Zara-style input)
- [ ] Health check endpoint returns 200 OK
- [ ] Environment variables loaded correctly
- [ ] Azure OpenAI connection working
**Status:** Not Started

### Checkpoint 2: Pre-Completion (80% complete)
- [ ] Core workflow endpoints functional (POST /api/workflows/forecast, POST /api/workflows/reforecast)
- [ ] WebSocket connection established with 6 message types broadcasting correctly
- [ ] Agent scaffolding created (4 agents with handoff configuration)
- [ ] Data seeding works (Phase 1 CSVs loaded into SQLite)
- [ ] Workflow creation returns workflow_id and WebSocket URL
**Status:** Not Started

### Checkpoint 3: Final
- [ ] All 18 REST API endpoints functional (workflow, resource, data management)
- [ ] All tests passing (pytest with resource endpoint coverage)
- [ ] OpenAPI docs accessible at /docs with all endpoints documented
- [ ] Backend README complete with setup instructions
- [ ] Frontend can connect and call all endpoints
- [ ] CSV upload endpoints working (historical sales, weekly actuals)
- [ ] Variance auto-triggers re-forecast when threshold exceeded
- [ ] Ready for handoff to Phase 4 (Orchestrator Agent implementation)
**Status:** Not Started

---

## Notes

- Update this checklist in real-time as tasks complete
- Mark subtasks with [x] when done
- Update task status: Not Started → In Progress → Complete
- This builds backend FOUNDATION only (agent logic in Phase 4-7)
- ML models return mock data (actual implementation in Phase 5)
- Focus on API contracts matching frontend expectations

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Progress:** 0/14 tasks (0%)
**Time Estimate:** 46 hours (6-8 days at 6-8h/day)
