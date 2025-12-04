# Phase 5: Orchestrator Foundation - Implementation Plan

**Phase:** 5 of 8
**Goal:** Build orchestrator infrastructure for parameter-driven multi-agent coordination
**Agent:** `*agent dev` (BMad Dev Agent)
**Duration Estimate:** 3.5 days (28 hours)
**Actual Duration:** TBD
**Status:** Ready to Start - All Stories Planned

---

## Requirements Source

- **Primary:** `planning/4_prd_v3.3.md` - PRD with FR section 5.11 (Orchestrator Infrastructure)
- **Primary:** `planning/3_technical_architecture_v3.3.md` - Orchestrator design and API contracts
- **Reference:** `planning/2_product_brief_v3.3.md` - Product vision and parameter-driven approach
- **Reference:** `PHASE5_OVERVIEW.md` - Phase 5 complete architecture and flows

---

## Key Deliverables

1. **Parameter Extraction Service**
   - Azure OpenAI gpt-4o-mini integration
   - Natural language → SeasonParameters conversion
   - Pydantic validation (5 required fields + 2 optional)
   - POST /api/orchestrator/extract-parameters endpoint

2. **Agent Handoff Framework**
   - AgentHandoffManager class
   - Agent registration mechanism
   - Single agent execution with timeout (30s default)
   - Agent chaining (sequential execution with result passing)
   - Execution logging

3. **WebSocket Streaming Infrastructure**
   - ConnectionManager class
   - WebSocket /ws/orchestrator/{session_id} endpoint
   - 5 message types (agent_status, progress, complete, error, heartbeat)
   - POST /api/orchestrator/run-workflow endpoint
   - Heartbeat mechanism (30-second keepalive)

4. **Context Assembly Pipeline**
   - Historical data loader (CSV files from Phase 1)
   - Stores data loader (CSV files from Phase 1)
   - ContextAssembler class
   - Three context types (Demand, Inventory, Pricing)
   - Caching for performance (<2 seconds assembly)

5. **Error Handling System**
   - 7 custom exception classes
   - FastAPI exception handlers
   - Standardized ErrorResponse schema
   - Request ID middleware for tracing
   - WebSocket error notifications
   - Logging configuration

6. **Integration Testing**
   - 29+ integration tests
   - pytest-asyncio for async tests
   - WebSocket client testing
   - Performance testing (<10s workflow, <2s context)
   - Coverage >90% for orchestrator module

---

## Phase 5 Stories

### Story 1: Parameter Extraction ✅ STORY READY
**File:** `stories/PHASE5-001-parameter-extraction.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** None
**Status:** ⏳ Not Started

**Summary:**
- Create SeasonParameters Pydantic schema (5 required + 2 optional fields)
- Create LLM prompt template with few-shot examples
- Implement extract_parameters_from_text() service function
- Create POST /api/orchestrator/extract-parameters endpoint
- Add error handling (400, 422, 503)
- Write 5 unit tests (Zara, Standard, Luxury, Incomplete, Invalid)

**Key Tasks:**
- [ ] Define SeasonParameters schema in backend/app/schemas/parameters.py
- [ ] Create prompts.py with few-shot LLM prompt template
- [ ] Implement parameter_extraction.py service with OpenAI call
- [ ] Create FastAPI endpoint in backend/app/orchestrator/routes.py
- [ ] Add validation for business rules (4-52 weeks, 0-1 holdback, etc.)
- [ ] Write 5 unit tests with different scenarios
- [ ] Test with Postman

---

### Story 2: Agent Handoff Framework ✅ STORY READY
**File:** `stories/PHASE5-002-agent-handoff-framework.md`
**Estimate:** 5 hours
**Actual:** TBD
**Dependencies:** Story 1
**Status:** ⏳ Not Started

**Summary:**
- Create AgentHandoffManager class
- Implement agent registration (name → handler mapping)
- Implement single agent execution with timeout enforcement
- Implement agent chaining (sequential execution)
- Add execution logging (agent_name, duration, status)
- Create mock agents for testing
- Write 7 unit tests

**Key Tasks:**
- [ ] Create AgentHandoffManager class in backend/app/orchestrator/agent_handoff.py
- [ ] Implement register_agent(name, handler) method
- [ ] Implement call_agent(name, context, timeout) method with asyncio.wait_for
- [ ] Implement handoff_chain(agents[], context) method
- [ ] Add ExecutionLogEntry data model
- [ ] Create mock_demand_agent and mock_inventory_agent for testing
- [ ] Write 7 comprehensive unit tests
- [ ] Test timeout enforcement (30-second default)

---

### Story 3: WebSocket Streaming ✅ STORY READY
**File:** `stories/PHASE5-003-websocket-streaming.md`
**Estimate:** 6 hours
**Actual:** TBD
**Dependencies:** Stories 1, 2
**Status:** ⏳ Not Started

**Summary:**
- Define 5 WebSocket message schemas (Pydantic)
- Create ConnectionManager class for managing WebSocket connections
- Implement WebSocket /ws/orchestrator/{session_id} endpoint
- Integrate WebSocket with AgentHandoffManager (send updates)
- Create orchestrator workflow endpoint (POST /api/orchestrator/run-workflow)
- Add heartbeat mechanism (30-second keepalive)
- Write integration tests with real WebSocket client

**Key Tasks:**
- [ ] Define message schemas (AgentStatusMessage, ProgressMessage, etc.)
- [ ] Create ConnectionManager class in backend/app/orchestrator/websocket.py
- [ ] Implement connect(), disconnect(), send_message(), broadcast() methods
- [ ] Create WebSocket endpoint in routes.py
- [ ] Integrate with AgentHandoffManager to send progress updates
- [ ] Create POST /api/orchestrator/run-workflow endpoint
- [ ] Add heartbeat task (asyncio background task, 30s interval)
- [ ] Write 3 integration tests (connection, messages, heartbeat)
- [ ] Test with wscat (npm install -g wscat)

---

### Story 4: Context-Rich Handoffs ✅ STORY READY
**File:** `stories/PHASE5-004-context-rich-handoffs.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Stories 1, 2
**Status:** ⏳ Not Started

**Summary:**
- Define context data models (DemandAgentContext, InventoryAgentContext, PricingAgentContext)
- Create historical data loader (load_historical_sales(), load_stores_data())
- Create ContextAssembler class with assembly methods
- Integrate with orchestrator workflow (pass context to agents)
- Add error handling for missing data files
- Write unit tests for data loading and assembly

**Key Tasks:**
- [ ] Define DemandAgentContext, InventoryAgentContext, PricingAgentContext schemas
- [ ] Create data_loaders.py with load_historical_sales() and load_stores_data()
- [ ] Add caching to data loaders (avoid repeated file reads)
- [ ] Create ContextAssembler class in backend/app/orchestrator/context_assembly.py
- [ ] Implement assemble_demand_context(), assemble_inventory_context(), assemble_pricing_context()
- [ ] Update orchestrator workflow to use context packages
- [ ] Add validation for required CSV columns and data types
- [ ] Write 4 unit tests (data loading, context assembly, caching, errors)
- [ ] Test performance (<2 seconds for context assembly)

---

### Story 5: Error Handling ✅ STORY READY
**File:** `stories/PHASE5-005-error-handling.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Stories 1-4
**Status:** ⏳ Not Started

**Summary:**
- Define 7 custom exception classes (OrchestratorError base class)
- Create ErrorResponse Pydantic schema
- Implement FastAPI exception handlers for all custom exceptions
- Register exception handlers in main FastAPI app
- Add request ID middleware for tracing
- Enhance WebSocket error notifications
- Add logging configuration
- Write unit tests for exception handlers

**Key Tasks:**
- [ ] Define custom exception classes in backend/app/orchestrator/errors.py
- [ ] Create ErrorResponse schema with error_type, message, details, suggestions, request_id
- [ ] Implement exception handlers (parameter_extraction_error_handler, etc.)
- [ ] Register handlers in app.main:app
- [ ] Create RequestIDMiddleware in backend/app/middleware.py
- [ ] Update WebSocket to send error messages on failures
- [ ] Configure logging in backend/app/config/logging.py
- [ ] Write 5 unit tests (one for each exception type)
- [ ] Test error responses with Postman

---

### Story 6: Integration Testing ✅ STORY READY
**File:** `stories/PHASE5-006-integration-testing.md`
**Estimate:** 5 hours
**Actual:** TBD
**Dependencies:** Stories 1-5
**Status:** ⏳ Not Started

**Summary:**
- Set up test infrastructure (fixtures, conftest.py)
- Test complete workflow (parameter extraction → agent execution → WebSocket)
- Test WebSocket message flow during workflow
- Test error scenarios (missing data, timeouts, invalid params)
- Performance testing (<10s workflow, <2s context)
- Test concurrent workflows (multiple sessions)
- Set up CI/CD test execution
- Create testing documentation

**Key Tasks:**
- [ ] Create backend/tests/integration/orchestrator/conftest.py with fixtures
- [ ] Write test_complete_workflow.py (happy path end-to-end)
- [ ] Write test_websocket_integration.py (real WebSocket client)
- [ ] Write test_error_scenarios.py (missing data, timeouts, invalid params)
- [ ] Write test_performance.py (workflow <10s, context <2s)
- [ ] Write test_concurrent_workflows.py (multiple sessions simultaneously)
- [ ] Set up GitHub Actions workflow for tests
- [ ] Create TESTING.md documentation
- [ ] Verify coverage >90% for orchestrator module

---

## Total Estimates vs Actuals

- **Total Stories:** 6
- **Estimated Time:** 28 hours (3.5 days at 8h/day)
  - Story 1: 4h, Story 2: 5h, Story 3: 6h
  - Story 4: 4h, Story 5: 4h, Story 6: 5h
- **Actual Time:** TBD
- **Variance:** TBD

---

## Validation Checkpoints

### Checkpoint 1: Parameter Extraction (After Story 1)
**Verify:**
- [ ] POST /api/orchestrator/extract-parameters endpoint working
- [ ] Natural language input → SeasonParameters conversion successful
- [ ] Business rule validation working (4-52 weeks, 0-1 holdback, etc.)
- [ ] Error handling working (400, 422, 503)
- [ ] 5 unit tests passing
- [ ] Postman tests successful

### Checkpoint 2: Agent Framework (After Story 2)
**Verify:**
- [ ] AgentHandoffManager class working
- [ ] Agent registration successful
- [ ] Single agent execution with timeout working
- [ ] Agent chaining working (Demand → Inventory)
- [ ] Execution logging capturing all attempts
- [ ] 7 unit tests passing
- [ ] Mock agents executing correctly

### Checkpoint 3: WebSocket Streaming (After Story 3)
**Verify:**
- [ ] WebSocket /ws/orchestrator/{session_id} endpoint working
- [ ] ConnectionManager managing multiple connections
- [ ] 5 message types sending correctly
- [ ] POST /api/orchestrator/run-workflow endpoint working
- [ ] Heartbeat keeping connection alive (30s intervals)
- [ ] Integration tests passing
- [ ] wscat connection successful

### Checkpoint 4: Context Assembly (After Story 4)
**Verify:**
- [ ] Historical data loading from CSV files
- [ ] Stores data loading from CSV files
- [ ] DemandAgentContext assembly working
- [ ] InventoryAgentContext assembly working
- [ ] PricingAgentContext assembly working
- [ ] Caching improving performance (<100ms for cached loads)
- [ ] Context assembly completing in <2 seconds
- [ ] 4 unit tests passing

### Checkpoint 5: Error Handling (After Story 5)
**Verify:**
- [ ] All 7 custom exceptions working
- [ ] FastAPI exception handlers returning correct HTTP status codes
- [ ] ErrorResponse schema providing helpful messages
- [ ] Request ID middleware adding IDs to all responses
- [ ] WebSocket error notifications working
- [ ] Logging configuration working
- [ ] 5 unit tests passing

### Checkpoint 6: Final (After Story 6)
**Verify:**
- [ ] All integration tests passing (29+ tests)
- [ ] Coverage >90% for orchestrator module
- [ ] Performance targets met (<10s workflow, <2s context)
- [ ] Concurrent workflows working
- [ ] CI/CD tests passing
- [ ] Documentation complete
- [ ] Ready for Phase 6 (Demand Agent implementation)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Azure OpenAI API rate limits | Medium | High | Implement exponential backoff, use timeout=10s, monitor rate limits |
| CSV data files missing | Medium | High | Validate DATA_DIR env var, provide clear error messages, create mock data if needed |
| WebSocket connections timing out | Low | Medium | Implement heartbeat (30s), handle reconnections gracefully |
| Context assembly too slow | Low | Medium | Implement caching, load data once and reuse, optimize DataFrame operations |
| Agent timeout issues | Medium | Medium | Use asyncio.wait_for with configurable timeout (default 30s), log timeouts clearly |
| Test flakiness (async tests) | Medium | Low | Use pytest-asyncio, add proper cleanup in fixtures, avoid race conditions |

---

## Mock Agent Behavior Requirements

**Critical:** Mock agents must return **dynamic data based on parameters**, not static JSON.

**Example: Mock Demand Agent**
```python
# ✅ GOOD: Dynamic mock data based on parameters
async def mock_demand_agent(context: DemandAgentContext):
    params = context.parameters

    # Adapt safety stock based on replenishment strategy
    if params.replenishment_strategy == "none":
        safety_stock = 0.25  # Higher safety stock (no replenishment)
        reasoning = "No replenishment → increased safety stock 20% → 25%"
    else:
        safety_stock = 0.20  # Standard safety stock
        reasoning = f"{params.replenishment_strategy} replenishment → standard 20%"

    # Simulate processing time
    await asyncio.sleep(2)

    return {
        "total_demand": 8000,
        "safety_stock": safety_stock,
        "adaptation_reasoning": reasoning,
        "forecast_horizon_weeks": params.forecast_horizon_weeks,
        "forecast_by_week": [
            {"week": i, "demand": 667} for i in range(1, params.forecast_horizon_weeks + 1)
        ]
    }
```

**All mock agents (Demand, Inventory, Pricing) must:**
1. Accept context (DemandAgentContext, InventoryAgentContext, PricingAgentContext)
2. Adapt their outputs based on parameters
3. Return reasoning text explaining adaptations
4. Return realistic data structures (not just {"status": "ok"})
5. Simulate processing time (1-3 seconds)

---

## Integration Testing Strategy

**For each story:**
1. **Write tests FIRST** (Test-Driven Development)
   - Define expected behavior
   - Write failing tests
   - Implement functionality
   - Verify tests pass

2. **Test independently with tools**
   - Postman for HTTP endpoints
   - wscat for WebSocket connections
   - pytest for unit/integration tests

3. **Test with different inputs**
   - Different parameter combinations
   - Different session IDs
   - Different data scenarios (missing files, invalid data, etc.)

**Critical Flows to Test:**

1. **Parameter Extraction Flow**
   - User enters natural language
   - Backend calls Azure OpenAI
   - Backend returns SeasonParameters
   - Validation enforces business rules
   - Errors return helpful messages

2. **Agent Handoff Flow**
   - Register 3 agents (Demand, Inventory, Pricing)
   - Execute chain sequentially
   - Each agent receives context from previous agent
   - Execution log captures all attempts
   - Timeout enforcement works (30s default)

3. **WebSocket Streaming Flow**
   - Frontend connects to WebSocket
   - Backend sends agent_status when agent starts
   - Backend sends progress updates during execution
   - Backend sends complete when agent finishes
   - Heartbeat keeps connection alive
   - Connection closes gracefully

4. **Context Assembly Flow**
   - Load historical_sales.csv from data directory
   - Load stores.csv from data directory
   - Assemble DemandAgentContext with parameters + data
   - Cache data for subsequent assemblies
   - Complete assembly in <2 seconds

5. **Error Handling Flow**
   - Invalid parameters → 422 Unprocessable Entity
   - Missing data files → 404 Not Found with helpful message
   - Agent timeout → 504 Gateway Timeout
   - OpenAI API error → 503 Service Unavailable
   - WebSocket sends error messages on failures

---

## Notes

- **Backend only** - No frontend changes in Phase 5
- **Mock agents OK** - No actual ML models needed yet
- **Focus on infrastructure** - Orchestrator scaffolding for future agents
- **Performance targets** - <10s workflow, <2s context assembly
- **High test coverage** - >90% orchestrator module, >80% overall backend
- **Phase 1 CSV data** - Use existing data from Phase 1 for testing

---

## Success Criteria (Recap)

✅ **Phase 5 Complete When:**
1. Parameter extraction endpoint working (POST /api/orchestrator/extract-parameters)
2. Agent handoff framework operational (AgentHandoffManager)
3. WebSocket streaming real-time updates (ws://orchestrator/{session_id})
4. Context assembly with historical data loading (<2 seconds)
5. Comprehensive error handling across all components
6. All integration tests passing (29+ tests)
7. Coverage >90% for orchestrator module
8. Performance targets met (<10s workflow, <2s context)
9. Documentation complete (PHASE5_OVERVIEW.md, TESTING.md)
10. **Ready for Phase 6 (Demand Agent implementation)**

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
**Status:** Ready to Start - All 6 Stories Planned
**Next Step:** Start PHASE5-001 (Parameter Extraction) - 4 hours
