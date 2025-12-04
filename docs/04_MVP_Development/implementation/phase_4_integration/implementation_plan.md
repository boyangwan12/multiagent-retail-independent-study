# Phase 4: Frontend/Backend Integration - Implementation Plan

**Phase:** 4 of 8
**Goal:** Connect React frontend to FastAPI backend with REAL data flow (mock agents OK, no AI yet)
**Agent:** `*agent dev`
**Duration Estimate:** 5-6 days (44-48 hours)
**Actual Duration:** TBD
**Status:** Ready to Start - All Stories Planned

---

## Requirements Source

- **Primary:** `planning/5_front-end-spec_v3.3.md` - UI/UX requirements for all 8 sections
- **Primary:** `planning/3_technical_architecture_v3.3.md` - API contracts and WebSocket specs
- **Reference:** `planning/4_prd_v3.3.md` - Business requirements and user stories
- **Reference:** `IMPLEMENTATION_GUIDE.md` - Phase 4 overview and success criteria

---

## Key Deliverables

1. **Environment Configuration**
   - Frontend `.env` with backend API URL
   - Backend `.env` with OpenAI API keys
   - CORS configuration in FastAPI
   - WebSocket connection settings

2. **All 8 Frontend Sections Integrated (In Order)**
   - Section 0: Parameter Gathering → POST /api/parameters/extract
   - Section 1: Agent Cards + Real WebSocket → ws://localhost:8000/api/workflows/{id}/stream
   - Section 2: Forecast Summary → GET /api/forecasts/{id}
   - Section 3: Cluster Cards → GET /api/stores/clusters
   - Section 4: Weekly Chart → GET /api/variance/{id}/week/{week}
   - Section 5: Replenishment Queue → GET /api/allocations/{id}
   - Section 6: Markdown Decision → GET /api/markdowns/{id}
   - Section 7: Performance Metrics → Multiple endpoints

3. **CSV Upload Workflows**
   - Upload historical sales → POST /api/data/upload-historical-sales
   - Upload weekly actuals → POST /api/data/upload-weekly-sales
   - Database seeded with Phase 1 data

4. **Mock Agents with Dynamic Data**
   - Backend agents return parameter-driven mock data
   - Agents adapt responses based on SeasonParameters
   - Realistic data flow without actual ML models

5. **Integration Tests**
   - Backend tests (pytest) for all endpoints
   - Frontend tests for critical flows
   - End-to-end workflow testing

6. **Documentation**
   - Updated README.md with setup instructions
   - INTEGRATION_TESTING.md checklist
   - Technical decisions documented

---

## Phase 4 Stories

### Story 1: Environment Configuration ✅ STORY READY
**File:** `stories/PHASE4-001-environment-configuration.md`
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** None
**Status:** ⏳ Not Started

**Summary:**
- Create frontend `.env` with VITE_API_URL
- Create backend `.env` with OpenAI keys
- Configure CORS in FastAPI
- Test basic connectivity

**Key Tasks:**
- [ ] Create `frontend/.env` with backend URL
- [ ] Create `backend/.env` with OpenAI API key
- [ ] Configure CORS middleware in FastAPI
- [ ] Test OPTIONS preflight requests
- [ ] Verify frontend can reach backend health endpoint

---

### Story 2: Section 0 - Parameter Gathering Integration ✅ STORY READY
**File:** `stories/PHASE4-002-section-0-parameter-gathering.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Story 1
**Status:** ⏳ Not Started

**Summary:**
- Replace mock parameter extraction with real API call
- Connect frontend Section 0 to POST /api/parameters/extract
- Test natural language → SeasonParameters flow
- Verify parameter confirmation modal displays backend data

**Key Tasks:**
- [ ] Replace mock extraction logic in ParameterGathering component
- [ ] Implement fetch call to POST /api/parameters/extract
- [ ] Test endpoint with Postman first
- [ ] Display extracted parameters in confirmation modal
- [ ] Handle loading states and errors
- [ ] Test with 3-4 different natural language inputs

---

### Story 3: Section 1 - Agent Cards + Real WebSocket ✅ STORY READY
**File:** `stories/PHASE4-003-section-1-agent-cards-websocket.md`
**Estimate:** 6 hours
**Actual:** TBD
**Dependencies:** Story 2
**Status:** ⏳ Not Started

**Summary:**
- Replace setTimeout mock with real WebSocket client
- Connect to ws://localhost:8000/api/workflows/{id}/stream
- Initiate workflow with POST /api/workflows/forecast
- Listen for 6 message types (agent_started, agent_progress, etc.)
- Update agent cards in real-time

**Key Tasks:**
- [ ] Test POST /api/workflows/forecast with Postman
- [ ] Test WebSocket connection independently
- [ ] Implement WebSocket client in frontend
- [ ] Replace mock streaming with real WS messages
- [ ] Update AgentCard components with real status
- [ ] Test reconnection logic
- [ ] Verify all 6 message types display correctly

---

### Story 4: Sections 2-3 - Forecast Summary + Cluster Cards ✅ STORY READY
**File:** `stories/PHASE4-004-sections-2-3-forecast-clusters.md`
**Estimate:** 5 hours
**Actual:** TBD
**Dependencies:** Story 3
**Status:** ⏳ Not Started

**Summary:**
- Section 2: Connect to GET /api/forecasts/{id}
- Section 3: Connect to GET /api/stores/clusters
- Display backend forecast data (from mock agents)
- Display cluster data with allocation factors

**Key Tasks:**
- [ ] Test GET /api/forecasts/{id} with Postman
- [ ] Test GET /api/stores/clusters with Postman
- [ ] Replace mock data in ForecastSummary component
- [ ] Replace mock data in ClusterCards component
- [ ] Verify JSON structure matches TypeScript types
- [ ] Test with different workflow_ids
- [ ] Verify all forecast metrics display correctly

---

### Story 5: Sections 4-5 - Weekly Chart + Replenishment Queue ✅ STORY READY
**File:** `stories/PHASE4-005-sections-4-5-chart-replenishment.md`
**Estimate:** 5 hours
**Actual:** TBD
**Dependencies:** Story 4
**Status:** ⏳ Not Started

**Summary:**
- Section 4: Connect to GET /api/variance/{id}/week/{week}
- Section 5: Connect to GET /api/allocations/{id}
- Display weekly chart with backend data
- Display replenishment queue with backend data

**Key Tasks:**
- [ ] Test GET /api/variance/{id}/week/{week} with Postman
- [ ] Test GET /api/allocations/{id} with Postman
- [ ] Replace mock data in WeeklyChart component
- [ ] Replace mock data in ReplenishmentQueue component
- [ ] Verify chart renders with backend data
- [ ] Test variance highlighting (>20% threshold)
- [ ] Verify replenishment approval flow

---

### Story 6: Sections 6-7 - Markdown Decision + Performance Metrics ✅ STORY READY
**File:** `stories/PHASE4-006-sections-6-7-markdown-metrics.md`
**Estimate:** 5 hours
**Actual:** TBD
**Dependencies:** Story 5
**Status:** ⏳ Not Started

**Summary:**
- Section 6: Connect to GET /api/markdowns/{id}
- Section 7: Aggregate metrics from multiple endpoints
- Display markdown recommendations with backend data
- Display performance metrics with backend data

**Key Tasks:**
- [ ] Test GET /api/markdowns/{id} with Postman
- [ ] Replace mock data in MarkdownDecision component
- [ ] Replace mock data in PerformanceMetrics component
- [ ] Aggregate data from forecasts, allocations, markdowns endpoints
- [ ] Verify markdown slider updates backend
- [ ] Test markdown approval flow
- [ ] Verify all metrics calculate correctly

---

### Story 7: CSV Upload Workflows ✅ STORY READY
**File:** `stories/PHASE4-007-csv-upload-workflows.md`
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Story 1
**Status:** ⏳ Not Started

**Summary:**
- Upload historical sales CSV → POST /api/data/upload-historical-sales
- Upload weekly actuals CSV → POST /api/data/upload-weekly-sales
- Test file parsing and database storage
- Seed database with Phase 1 CSV data

**Key Tasks:**
- [ ] Test POST /api/data/upload-historical-sales with Postman
- [ ] Test POST /api/data/upload-weekly-sales with Postman
- [ ] Implement CSV upload UI component
- [ ] Handle multipart/form-data file upload
- [ ] Display upload progress
- [ ] Verify data stored in database
- [ ] Test with Phase 1 generated CSVs
- [ ] Handle upload errors gracefully

---

### Story 8: Integration Tests (Backend + Frontend) ✅ STORY READY
**File:** `stories/PHASE4-008-integration-tests.md`
**Estimate:** 6 hours
**Actual:** TBD
**Dependencies:** Stories 2-7
**Status:** ⏳ Not Started

**Summary:**
- Write pytest tests for all backend endpoints
- Write frontend tests for critical flows
- Test end-to-end workflows
- Verify mock agents return dynamic data based on parameters

**Key Tasks:**
- [ ] Backend: Test parameter extraction endpoint
- [ ] Backend: Test workflow creation endpoint
- [ ] Backend: Test all resource endpoints (forecasts, allocations, etc.)
- [ ] Backend: Test WebSocket message broadcasting
- [ ] Backend: Test CSV upload endpoints
- [ ] Frontend: Test parameter extraction flow
- [ ] Frontend: Test workflow initiation flow
- [ ] Frontend: Test data display in all 8 sections
- [ ] End-to-end: Test full workflow (params → forecast → display)
- [ ] Verify mock agents adapt to different parameters

---

### Story 9: Documentation & README Updates ✅ STORY READY
**File:** `stories/PHASE4-009-documentation-readme.md`
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Stories 1-8
**Status:** ⏳ Not Started

**Summary:**
- Update root README.md with setup instructions
- Create INTEGRATION_TESTING.md checklist
- Document technical decisions
- Update retrospective

**Key Tasks:**
- [ ] Update README.md with "How to Run Backend"
- [ ] Update README.md with "How to Run Frontend"
- [ ] Document environment variable setup
- [ ] Create INTEGRATION_TESTING.md checklist
- [ ] Update technical_decisions.md with integration choices
- [ ] Document any issues encountered
- [ ] Prepare handoff notes for Phase 5

---

## Total Estimates vs Actuals

- **Total Stories:** 9
- **Estimated Time:** 40 hours (5 days at 8h/day)
  - Story 1: 2h, Story 2: 4h, Story 3: 6h
  - Story 4: 5h, Story 5: 5h, Story 6: 5h
  - Story 7: 4h, Story 8: 6h, Story 9: 3h
- **Actual Time:** TBD
- **Variance:** TBD

---

## Validation Checkpoints

### Checkpoint 1: Environment & Section 0 (After Story 2)
**Verify:**
- [ ] Backend runs without errors (`uvicorn app.main:app --reload`)
- [ ] Frontend runs without errors (`npm run dev`)
- [ ] Frontend can reach backend (CORS working)
- [ ] Section 0 parameter extraction works end-to-end
- [ ] No console errors in browser

### Checkpoint 2: WebSocket & Workflow (After Story 3)
**Verify:**
- [ ] POST /api/workflows/forecast returns workflow_id
- [ ] WebSocket connection establishes successfully
- [ ] Agent cards update in real-time with mock agent progress
- [ ] All 6 message types received and displayed
- [ ] Workflow completes without errors

### Checkpoint 3: All Sections Integrated (After Story 6)
**Verify:**
- [ ] All 8 frontend sections call backend APIs
- [ ] All sections display backend data (mock data OK)
- [ ] No 404 errors, all endpoints return 200 OK
- [ ] JSON structure matches TypeScript types
- [ ] No console errors in browser

### Checkpoint 4: Testing Complete (After Story 8)
**Verify:**
- [ ] All backend tests passing (pytest)
- [ ] Frontend tests passing
- [ ] End-to-end workflow tested manually
- [ ] Mock agents return dynamic data based on parameters
- [ ] CSV uploads working

### Checkpoint 5: Final (After Story 9)
**Verify:**
- [ ] README.md has clear setup instructions
- [ ] Professor can run backend + frontend without errors
- [ ] All documentation updated
- [ ] Repository clean and organized
- [ ] Ready for Phase 5 (Demand Agent implementation)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CORS errors block frontend | Medium | High | Configure CORS early (Story 1), test with browser DevTools |
| WebSocket connection fails | Medium | High | Test WebSocket independently before integration, implement reconnection logic |
| JSON structure mismatch | Medium | Medium | Verify TypeScript types match backend Pydantic models, test with Postman first |
| Mock agents too simple | Low | Medium | Ensure agents return dynamic data based on parameters, not static JSON |
| Backend not seeded with data | Medium | High | Seed database with Phase 1 CSVs before integration testing |
| Tests take too long to write | Low | Low | Focus on critical flows, skip edge cases for Phase 4 |

---

## Mock Agent Behavior Requirements

**Critical:** Mock agents must return **dynamic data based on parameters**, not static JSON.

**Example: Demand Agent Mock**
```python
# ❌ BAD: Static mock data
def mock_demand_agent():
    return {"total_demand": 8000, "safety_stock": 0.20}

# ✅ GOOD: Dynamic mock data based on parameters
def mock_demand_agent(parameters: SeasonParameters):
    # Adapt safety stock based on replenishment strategy
    if parameters.replenishment_strategy == "none":
        safety_stock = 0.25  # Higher safety stock
        reasoning = "No replenishment strategy → increased safety stock 20% → 25%"
    else:
        safety_stock = 0.20
        reasoning = f"{parameters.replenishment_strategy} replenishment → standard 20% safety stock"

    return {
        "total_demand": 8000,
        "safety_stock": safety_stock,
        "adaptation_reasoning": reasoning,
        "forecast_horizon_weeks": parameters.forecast_horizon_weeks
    }
```

**All mock agents (Demand, Inventory, Pricing) must:**
1. Accept SeasonParameters as input
2. Adapt their outputs based on parameters
3. Return reasoning text explaining adaptations
4. Return realistic data structures (not just {"status": "ok"})

---

## Integration Testing Strategy

**For each section integration:**
1. **Test endpoint with Postman FIRST**
   - Verify endpoint returns 200 OK
   - Verify JSON structure is correct
   - Verify mock data is realistic

2. **Then integrate frontend**
   - Replace mock API call with real fetch
   - Verify data displays correctly
   - Check browser console for errors

3. **Test with different inputs**
   - Different parameter combinations
   - Different workflow IDs
   - Different CSV uploads

**Critical Flows to Test:**
1. **Parameter Extraction Flow**
   - User enters natural language
   - Backend extracts parameters
   - Frontend displays in modal
   - User confirms
   - Workflow starts

2. **Workflow Execution Flow**
   - POST /api/workflows/forecast
   - WebSocket connects
   - Mock agents run (Demand → Inventory → Pricing)
   - Agent cards update in real-time
   - Workflow completes
   - All 8 sections display data

3. **CSV Upload Flow**
   - User uploads historical_sales_2022_2024.csv
   - Backend parses and stores in DB
   - GET /api/categories returns detected categories
   - GET /api/stores returns 50 stores

---

## Notes

- **No error handling in Phase 4** (skipped per requirements)
- **Focus on happy path only** - everything works
- **Mock agents OK** - no actual ML models needed yet
- **Frontend components already built** - just connect to backend
- **Backend endpoints already exist** - just need to call them
- **Phase 1 CSV data available** - use for testing

---

## Success Criteria (Recap)

✅ **Phase 4 Complete When:**
1. User can start backend and frontend without errors
2. Frontend calls ALL backend endpoints successfully
3. Parameter extraction works end-to-end
4. WebSocket connection streams real-time messages
5. CSV upload workflows functional
6. All 8 frontend sections display backend data (mock OK)
7. No console errors, all API calls return expected JSON
8. Integration tests passing (backend + frontend)
9. README.md has clear setup instructions
10. **Professor can run the full stack and see it working!**

---

**Created:** 2025-10-29
**Last Updated:** 2025-10-29
**Status:** Ready to Start - All 9 Stories Planned
**Next Step:** Create detailed story files (PHASE4-001 through PHASE4-009)
