# Phase 5: Orchestrator Foundation - Handoff Document

**Phase:** Phase 5 - Orchestrator Foundation
**Handoff Date:** 2025-11-04
**From:** PM Agent (Product Owner)
**To:** Developer(s) (Implementation)
**Status:** Ready for Implementation

---

## Executive Summary

Phase 5 implements the **Orchestrator Foundation** - the infrastructure that coordinates multi-agent workflows with parameter-driven behavior. This is the backend scaffolding that enables Phase 6-8 agents to plug in seamlessly.

**Why Orchestrator Foundation First?**
- User feedback: "I want to build orchestrator foundation before building individual agents"
- Enables incremental agent integration (Phase 6: Demand, Phase 7: Inventory, Phase 8: Pricing)
- Tests parameter-driven architecture with mock agents before adding AI complexity
- Validates handoff framework, WebSocket streaming, and context assembly early

**What's Included:**
- 6 detailed user stories (~10,000+ lines total)
- **28 hours** estimated effort (3.5 days)
- Parameter extraction via Azure OpenAI gpt-4o-mini
- Agent handoff framework with timeout enforcement
- WebSocket real-time progress streaming
- Context assembly with historical data loading
- Comprehensive error handling
- Integration testing infrastructure

---

## 🚨 COWORKER HANDOVER - START HERE! 🚨

### Welcome to Phase 5!

This section is specifically for **your coworker** taking over this project. Follow these steps carefully to get up and running.

### What Was Just Completed (Before Phase 5)

**Phase 4 Completion (Frontend/Backend Integration):**
✅ All 8 dashboard sections integrated
✅ WebSocket infrastructure working (frontend side)
✅ Backend API endpoints created with mock agents
✅ CSV upload workflows functional
✅ Integration tests passing

**PRD Update (2025-11-04):**
✅ Added FR section 5.11 (Orchestrator Infrastructure)
- FR-11.1 through FR-11.8 define requirements for Phase 5
- Parameter extraction, agent handoff, context assembly formalized

**Phase 5 Stories Created:**
✅ All 6 stories written in Phase 4 format
✅ Stories reference PRD v3.3, Tech Arch v3.3, Product Brief v3.3
✅ Each story has detailed tasks, subtasks, code examples, tests

---

### Step-by-Step Handover Checklist

#### ✅ Step 1: Clone & Branch Setup

```bash
# 1. Clone the repository (if you haven't already)
git clone [REPOSITORY_URL]
cd independent_study

# 2. Checkout or create the phase5-orchestrator branch
git checkout -b phase5-orchestrator

# 3. Verify you're on the correct branch
git branch --show-current
# Should output: phase5-orchestrator
```

---

#### ✅ Step 2: Verify Backend Environment

**Location**: `backend/.env` (should already exist from Phase 4)

**Verify these variables exist:**
```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your_actual_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com

# Database Configuration
DATABASE_URL=sqlite:///./forecast.db

# Data Directory (for Phase 1 CSV files)
DATA_DIR=data

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# WebSocket Configuration
WEBSOCKET_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**⚠️ CRITICAL - New for Phase 5:**
- `AZURE_OPENAI_ENDPOINT` must be set (for parameter extraction)
- `DATA_DIR` must point to directory with Phase 1 CSV files
- If missing, add them to `backend/.env`

---

#### ✅ Step 3: Set Up Test Data Directory

**Create data directory structure:**
```bash
# From project root
mkdir -p data

# Copy Phase 1 CSV files (if available)
# Required files:
#   - data/historical_sales.csv
#   - data/stores.csv
```

**If you don't have Phase 1 data:**
- Phase 5 stories include test data generation
- You'll create mock CSV files during PHASE5-004 (Context Assembly)
- Minimum requirement: 52 weeks of historical data

---

#### ✅ Step 4: Install Dependencies

**Backend Only (No Frontend Work in Phase 5):**
```bash
cd backend

# Install UV (Python package manager) if not already installed
pip install uv

# Install dependencies using UV
uv pip install -r requirements.txt

# Verify installation
python --version  # Should be 3.11+
```

**New Dependencies for Phase 5:**
- `pydantic` - Already installed (for SeasonParameters schema)
- `pytest-asyncio` - For async test support
- `websockets` - For WebSocket testing

---

#### ✅ Step 5: Verify Backend Setup

**Test Backend:**
```bash
cd backend

# Start the backend server
uvicorn app.main:app --reload

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [PID]

# Open browser and visit:
# http://localhost:8000/docs  (OpenAPI docs)
# http://localhost:8000/health  (Health check endpoint)
```

**Verify Phase 4 Endpoints Work:**
- http://localhost:8000/docs should show existing endpoints from Phase 4
- You'll ADD new endpoints in Phase 5 (no breaking changes)

---

#### ✅ Step 6: Read Phase 5 Stories

**⚠️ CRITICAL**: Phase 5 has 6 stories in sequential order.

**Start with these in order**:
1. `stories/PHASE5-001-parameter-extraction.md` (4 hours)
2. `stories/PHASE5-002-agent-handoff-framework.md` (5 hours)
3. `stories/PHASE5-003-websocket-streaming.md` (6 hours)
4. `stories/PHASE5-004-context-rich-handoffs.md` (4 hours)
5. `stories/PHASE5-005-error-handling.md` (4 hours)
6. `stories/PHASE5-006-integration-testing.md` (5 hours)

**Key Points:**
- All stories use Phase 4 format (same structure you're familiar with)
- Each story has Planning References (PRD sections, Architecture sections)
- Tasks are atomic with code examples
- Tests are defined for each story
- **No frontend work** - backend only

---

#### ✅ Step 7: Tools You'll Need

**Required:**
- Python 3.11+ (for backend)
- UV (Python package manager): `pip install uv`
- Git (for version control)
- Azure OpenAI API access (for parameter extraction)

**Highly Recommended:**
- **Postman** (for API testing): https://www.postman.com/downloads/
- **VS Code** with extensions:
  - Python (Microsoft)
  - Pylance (Microsoft)
  - Python Test Explorer (Little Fox Team)
- **wscat** (for WebSocket testing): `npm install -g wscat`

---

#### ✅ Step 8: First Task - Start Here!

**Your first task is PHASE5-001**: Parameter Extraction

**Location**: `stories/PHASE5-001-parameter-extraction.md`

**What you'll do**:
1. Create `backend/app/schemas/parameters.py` (SeasonParameters schema)
2. Create `backend/app/orchestrator/prompts.py` (LLM prompt template)
3. Create `backend/app/orchestrator/parameter_extraction.py` (extraction service)
4. Create `POST /api/orchestrator/extract-parameters` endpoint
5. Add error handling (400 for incomplete, 422 for invalid)
6. Write 5 test scenarios (Zara, Standard, Luxury, Incomplete, Invalid)

**Time estimate**: 4 hours

**Validation**:
- Endpoint returns SeasonParameters with 5 required fields
- Extraction completes in <5 seconds
- Tests passing (5 scenarios)

---

### Common Issues & Fixes

#### Issue: "OPENAI_API_KEY not set"
**Fix**:
1. Check `backend/.env` file exists
2. Check API key starts with `sk-` or `sk-proj-`
3. Restart backend after editing .env

#### Issue: "Azure OpenAI endpoint not configured"
**Fix**:
1. Add `AZURE_OPENAI_ENDPOINT` to `backend/.env`
2. Get endpoint from Azure Portal (OpenAI resource)
3. Format: `https://your-resource.openai.azure.com`

#### Issue: "Historical data not found"
**Fix**:
1. Check `DATA_DIR` environment variable set in `.env`
2. Verify `data/historical_sales.csv` exists
3. Create mock data if needed (see PHASE5-004 story)

#### Issue: "WebSocket test fails"
**Fix**:
1. Install wscat: `npm install -g wscat`
2. Verify backend running at http://localhost:8000
3. Test connection: `wscat -c ws://localhost:8000/ws/orchestrator/test123`

---

### Questions? Need Help?

**During setup:**
- Check this handoff document first
- Check story files (they're very detailed!)
- Check `implementation_plan.md` for high-level overview
- Check `PHASE5_OVERVIEW.md` for complete architecture

**During implementation:**
- Each story has detailed tasks with code examples
- Test scenarios included in stories
- Manual testing checklists at end of each story

**If something doesn't work:**
1. Document the issue
2. Check "Common Issues & Fixes" section above
3. Ask for clarification (create issue or PR comment)

---

### Ready to Start?

Once you've completed Steps 1-7 above:

✅ You have the code
✅ You have .env files configured
✅ Dependencies installed
✅ Backend running
✅ Test data available

**→ You're ready to start PHASE5-001!**

Good luck! 🚀

---

## Quick Reference

### Key Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Implementation Plan** | High-level overview of 6 stories | `implementation_plan.md` |
| **Phase 5 Overview** | Complete feature and architecture mapping | `PHASE5_OVERVIEW.md` |
| **Stories (6)** | Detailed implementation guides | `stories/PHASE5-001.md` through `PHASE5-006.md` |
| **This Handoff** | Getting started guide | `PHASE5_HANDOFF.md` |

### Story Sequence

| Order | Story ID | Story Name | Effort | Dependencies |
|-------|----------|------------|--------|--------------|
| 1 | PHASE5-001 | Parameter Extraction | **4h** | None |
| 2 | PHASE5-002 | Agent Handoff Framework | **5h** | PHASE5-001 |
| 3 | PHASE5-003 | WebSocket Streaming | **6h** | PHASE5-001, PHASE5-002 |
| 4 | PHASE5-004 | Context-Rich Handoffs | **4h** | PHASE5-001, PHASE5-002 |
| 5 | PHASE5-005 | Error Handling | **4h** | PHASE5-001 through PHASE5-004 |
| 6 | PHASE5-006 | Integration Testing | **5h** | PHASE5-001 through PHASE5-005 |

**Total: 28 hours** (3.5 days)

**Parallelization Opportunities:**
- After PHASE5-002 completes: Stories 3 and 4 can run in parallel (WebSocket + Context)
- PHASE5-005 must wait for 1-4 (wraps all with error handling)
- PHASE5-006 must run last (integration testing)

---

## Prerequisites

### Before You Start

✅ **You should have:**
- Read `implementation_plan.md` (high-level overview)
- Read `PHASE5_OVERVIEW.md` (architecture details)
- Access to:
  - GitHub repository (branch: `phase5-orchestrator`)
  - Phase 4 completed code (backend + frontend integration)
  - Planning documents (`docs/04_MVP_Development/planning/`)
  - Updated PRD v3.3 with FR section 5.11

✅ **Required Skills:**
- Python 3.11+ (FastAPI, pytest, async/await)
- Pydantic (data validation)
- WebSocket (connection lifecycle, message broadcasting)
- REST API design (HTTP methods, status codes)
- Testing (integration tests, pytest-asyncio)

✅ **Tools to Install:**
- Python 3.11+
- UV (Python package manager): `pip install uv`
- Postman (for API testing)
- wscat (for WebSocket testing): `npm install -g wscat`
- VS Code with extensions:
  - Python (Microsoft)
  - Pylance (Microsoft)
  - Python Test Explorer (Little Fox Team)

---

## Getting Started - First Steps

### Step 1: Parameter Extraction (PHASE5-001)

**Time Estimate:** 4 hours

**Start Here:** `stories/PHASE5-001-parameter-extraction.md`

**What You'll Do:**
1. Define `SeasonParameters` Pydantic schema (5 required fields + 2 optional)
2. Create LLM prompt template with few-shot examples
3. Implement `extract_parameters_from_text()` service function
4. Create `POST /api/orchestrator/extract-parameters` endpoint
5. Add error handling (400 for incomplete, 422 for invalid, 503 for OpenAI errors)
6. Write 5 unit tests (Zara, Standard, Luxury, Incomplete, Invalid)

**Validation:**
- Endpoint returns SeasonParameters object
- Extraction completes in <5 seconds
- Tests passing for all 5 scenarios
- Postman test successful

**Common Issues:**
- **OpenAI timeout:** Increase timeout to 10 seconds
- **Invalid JSON from LLM:** Use `response_format={"type": "json_object"}`
- **Missing parameters:** Return 400 with list of missing fields

---

### Step 2: Agent Handoff Framework (PHASE5-002)

**Time Estimate:** 5 hours

**Story:** `stories/PHASE5-002-agent-handoff-framework.md`

**What You'll Do:**
1. Create `AgentHandoffManager` class with agent registry
2. Implement `register_agent(name, handler)` method
3. Implement `call_agent(name, context, timeout)` method with timeout enforcement
4. Implement `handoff_chain(agents[], context)` for sequential execution
5. Add execution logging (agent_name, duration, status)
6. Create mock Demand Agent and mock Inventory Agent for testing
7. Write 7 unit tests (registration, single call, chain, timeout, errors, logging)

**Key Deliverable:** Framework that coordinates multi-agent workflows with result passing.

**Validation:**
- Agent registry works
- Single agent execution works with timeout
- Agent chaining works (Demand → Inventory)
- Execution log captures all attempts

---

### Step 3: WebSocket Streaming (PHASE5-003)

**Time Estimate:** 6 hours

**Story:** `stories/PHASE5-003-websocket-streaming.md`

**What You'll Do:**
1. Define 5 WebSocket message schemas (agent_status, progress, complete, error, heartbeat)
2. Create `ConnectionManager` class for managing multiple connections
3. Implement `WebSocket /ws/orchestrator/{session_id}` endpoint
4. Integrate WebSocket with AgentHandoffManager (send updates during execution)
5. Create orchestrator workflow endpoint (`POST /api/orchestrator/run-workflow`)
6. Add heartbeat mechanism (30-second keepalive)
7. Write integration tests with real WebSocket client

**Key Deliverable:** Real-time progress updates during agent execution.

**Validation:**
- WebSocket connects successfully
- Messages sent during agent execution
- Multiple concurrent connections supported
- Heartbeat keeps connection alive

---

### Step 4: Context-Rich Handoffs (PHASE5-004)

**Time Estimate:** 4 hours

**Story:** `stories/PHASE5-004-context-rich-handoffs.md`

**What You'll Do:**
1. Define context data models (DemandAgentContext, InventoryAgentContext, PricingAgentContext)
2. Create historical data loader (`load_historical_sales()`, `load_stores_data()`)
3. Create `ContextAssembler` class with context assembly methods
4. Integrate with orchestrator workflow (pass context to agents instead of just parameters)
5. Add error handling for missing data
6. Write unit tests for data loading and context assembly

**Key Deliverable:** Agents receive parameters + historical data + stores data in context packages.

**Validation:**
- Historical data loads from CSV files
- Context assembly completes in <2 seconds
- Context objects validated with Pydantic
- Tests passing for all scenarios

---

### Step 5: Error Handling (PHASE5-005)

**Time Estimate:** 4 hours

**Story:** `stories/PHASE5-005-error-handling.md`

**What You'll Do:**
1. Define custom exception classes (ParameterExtractionError, DataNotFoundError, AgentTimeoutError, etc.)
2. Create standardized `ErrorResponse` schema
3. Implement FastAPI exception handlers for all custom exceptions
4. Register exception handlers in main FastAPI app
5. Add request ID middleware for tracing
6. Enhance WebSocket error notifications
7. Add logging configuration
8. Write unit tests for each exception handler

**Key Deliverable:** Comprehensive error handling across orchestrator.

**Validation:**
- All error scenarios return appropriate HTTP status codes
- Error responses include helpful messages and suggestions
- WebSocket sends error messages when workflow fails
- Request IDs included in all error responses

---

### Step 6: Integration Testing (PHASE5-006)

**Time Estimate:** 5 hours

**Story:** `stories/PHASE5-006-integration-testing.md`

**What You'll Do:**
1. Set up test infrastructure (fixtures, conftest.py)
2. Test complete workflow (parameter extraction → context assembly → agent execution)
3. Test WebSocket message flow during workflow execution
4. Test error scenarios (missing data, timeouts, invalid params)
5. Performance testing (<10s workflow, <2s context assembly)
6. Test concurrent workflows (multiple users simultaneously)
7. Set up CI/CD test execution
8. Create testing documentation

**Key Deliverable:** Full integration test suite with >80% coverage.

**Validation:**
- All tests passing consistently
- Coverage >80% for orchestrator module
- Performance targets met
- CI/CD pipeline configured

---

## Key Concepts & Architecture

### Parameter-Driven Architecture (v3.3)

**Core Idea:** Agents receive parameters and autonomously reason about behavior.

**5 Key Parameters:**
1. `forecast_horizon_weeks` (int): Number of weeks to forecast (4-52)
2. `season_start_date` (date): Season start date in YYYY-MM-DD format
3. `season_end_date` (date): Calculated from start + horizon
4. `replenishment_strategy` (enum): "none" | "weekly" | "bi-weekly"
5. `dc_holdback_percentage` (float): Percentage kept at DC (0.0-1.0)

**Example Adaptation:**
```python
# Mock Demand Agent adapts safety stock based on replenishment_strategy
if parameters.replenishment_strategy == "none":
    safety_stock = 0.25  # Higher safety stock (no replenishment)
    reasoning = "No replenishment → increased safety stock 20% → 25%"
else:
    safety_stock = 0.20  # Standard safety stock
    reasoning = f"{parameters.replenishment_strategy} replenishment → standard 20%"
```

---

### Agent Handoff Framework

**Flow:**
```
1. Register agents: handoff_manager.register_agent("demand", demand_handler)
2. Call single agent: result = await handoff_manager.call_agent("demand", context)
3. Chain agents: result = await handoff_manager.handoff_chain(["demand", "inventory"], context)
```

**Result Passing:**
- Agent N's result becomes Agent N+1's context
- Example: Demand forecast → Inventory allocation → Pricing markdown

---

### WebSocket Message Types

**5 Message Types:**
1. **agent_status**: Agent started/running
2. **progress**: Progress percentage (0-100%)
3. **complete**: Agent completed successfully
4. **error**: Agent failed
5. **heartbeat**: Keep-alive ping (every 30 seconds)

**Connection Lifecycle:**
1. Frontend connects to `/ws/orchestrator/{session_id}`
2. Backend sends `agent_status` when agent starts
3. Backend sends `progress` updates during execution
4. Backend sends `complete` when agent finishes
5. Connection closes after workflow completion

---

### Context Assembly

**Three Context Types:**

**1. Demand Agent Context:**
- `parameters`: SeasonParameters
- `historical_data`: DataFrame (52+ weeks of sales)
- `stores_data`: DataFrame (50 stores, 7 features)
- `category_id`: Category identifier

**2. Inventory Agent Context:**
- `parameters`: Forwarded from Demand
- `forecast_result`: Demand Agent's output
- `stores_data`: Forwarded from Demand

**3. Pricing Agent Context:**
- `parameters`: Forwarded from previous agents
- `forecast_result`: Demand Agent's output
- `inventory_plan`: Inventory Agent's output
- `actuals_data`: Optional actual sales to date

---

## Testing Strategy

### Integration Tests (PRIMARY)

**Backend (pytest):**
- 17+ integration tests covering all orchestrator functionality
- Use `TestClient` for HTTP requests
- Use `websockets` library for WebSocket tests
- Mock Azure OpenAI API calls

**Coverage Goals:**
- Orchestrator module: >90%
- Overall backend: >80%

**Run Tests:**
```bash
# Backend
cd backend
pytest tests/integration/ -v --cov=app.orchestrator --cov-report=html
```

---

## Common Issues & Troubleshooting

### Azure OpenAI API Errors

**Symptom:** "OpenAI API key not configured" or timeout errors.

**Fix:**
1. Check `OPENAI_API_KEY` in `backend/.env`
2. Check `AZURE_OPENAI_ENDPOINT` in `backend/.env`
3. Verify API key is valid in Azure Portal
4. Increase timeout if requests slow: `timeout=10`

---

### WebSocket Connection Fails

**Symptom:** "WebSocket connection failed" in wscat.

**Fix:**
1. Ensure backend running at http://localhost:8000
2. Check WebSocket URL: `ws://localhost:8000/ws/orchestrator/{session_id}`
3. Verify session_id is valid (not empty)
4. Check firewall allows WebSocket connections

---

### Historical Data Not Found

**Symptom:** "File not found" error when loading CSV.

**Fix:**
1. Check `DATA_DIR` environment variable set
2. Verify `data/historical_sales.csv` exists
3. Create mock data if needed:
   ```python
   # Create mock CSV with 52 weeks of data
   df = pd.DataFrame({
       'date': pd.date_range('2024-01-01', periods=52, freq='W'),
       'category_id': ['CAT001'] * 52,
       'units_sold': [100, 120, 110, ...],  # 52 values
   })
   df.to_csv('data/historical_sales.csv', index=False)
   ```

---

### Tests Failing

**Symptom:** Integration tests fail unexpectedly.

**Fix:**
1. Check backend is NOT running (tests start their own server)
2. Check test database is clean (delete `test.db` if exists)
3. Check mock fixtures match expected data shapes
4. Run tests individually to isolate failures

---

## Success Criteria - Phase 5 Complete

✅ **Phase 5 is complete when ALL of the following are true:**

### Functionality
- [ ] Parameter extraction endpoint working
- [ ] Agent handoff framework operational
- [ ] WebSocket streaming real-time updates
- [ ] Context assembly with historical data loading
- [ ] Error handling across all components
- [ ] No console errors during normal operation

### Testing
- [ ] All integration tests pass (17+ tests)
- [ ] Orchestrator coverage >90%
- [ ] Overall backend coverage >80%
- [ ] Performance targets met (<10s workflow, <2s context)

### Code Quality
- [ ] Backend follows PEP 8
- [ ] All type hints added
- [ ] No linting errors
- [ ] Code reviewed

### Deliverables
- [ ] All 6 stories completed and validated
- [ ] Master checklist 100% complete
- [ ] Testing documentation complete

---

## After Phase 5 - What's Next?

### Phase 6: Demand Agent Implementation

**Goal:** Replace mock Demand Agent with real forecasting logic (Prophet + ARIMA).

**Prerequisites from Phase 5:**
- Parameter extraction working (provides forecast_horizon_weeks)
- Agent handoff framework working (coordinates agent execution)
- Context assembly working (provides historical data to Demand Agent)
- WebSocket streaming working (real-time progress updates)

**What Changes:**
- Backend: Implement Prophet + ARIMA forecasting
- Backend: Replace mock forecast with real ensemble forecast
- Frontend: No changes needed (already integrated in Phase 4)

---

## Questions & Support

### During Implementation

**If you have questions:**
1. Check story details (most questions answered in detailed stories)
2. Check `PHASE5_OVERVIEW.md` (architecture explanations)
3. Check existing Phase 4 code (similar patterns)
4. Ask PM agent (create issue or tag in PR comments)

**If you find issues with planning:**
1. Document the issue
2. Make necessary adjustments (planning is not perfect!)
3. Update this handoff document for future phases

---

## Handoff Checklist

Before starting implementation, confirm:

- [ ] Read `implementation_plan.md`
- [ ] Read `PHASE5_OVERVIEW.md`
- [ ] Read this handoff document (PHASE5_HANDOFF.md)
- [ ] Have access to GitHub repository
- [ ] Have required tools installed (Python, UV, Postman, wscat)
- [ ] Understand parameter-driven architecture (v3.3)
- [ ] Understand agent handoff framework concept
- [ ] Understand WebSocket message flow
- [ ] Understand context assembly pipeline
- [ ] Know where to find help (story details, overview)

---

## Final Notes

### Phase 5 is a Critical Foundation

Phase 5 builds the orchestrator infrastructure that ALL future agents will use. Take time to:
- **Test thoroughly** - Integration tests catch issues early
- **Follow patterns** - Stories provide code examples
- **Ask questions** - Better to clarify now than refactor later

### You Have Detailed Stories

Each story is ~1000+ lines with:
- Step-by-step tasks
- Code examples
- Test scenarios
- Validation criteria

**Trust the stories.** They're designed to guide you through implementation without ambiguity.

### Good Luck! 🚀

You're building the foundation that enables all agent development. This is important work!

---

**Handoff Date:** 2025-11-04
**Prepared By:** PM Agent (Product Owner)
**For:** Developer(s) implementing Phase 5
**Questions?** See "Questions & Support" section above.
