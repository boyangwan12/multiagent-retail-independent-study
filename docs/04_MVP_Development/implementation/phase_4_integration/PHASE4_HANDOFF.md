# Phase 4: Frontend/Backend Integration - Handoff Document

**Phase:** Phase 4 - Frontend/Backend Integration
**Handoff Date:** [DATE]
**From:** PM Agent (Planning)
**To:** Developer(s) (Implementation)
**Status:** Ready for Implementation

---

## Executive Summary

Phase 4 implements an **integration-first approach**, connecting all 8 dashboard sections to backend APIs with mock agents BEFORE implementing real AI agents.

**Why Integration-First?**
- Professor feedback: "Hook frontend and backend together first"
- Validates full stack early (reduces risk)
- Enables parallel agent development in Phases 5-7
- Tests parameter-driven architecture (v3.3)

**What's Included:**
- 9 detailed user stories (~9,000 lines total)
- 48 hours estimated effort (6 days)
- Integration tests (backend + frontend)
- Complete API documentation
- Mock agents with dynamic, parameter-driven behavior

---

## Quick Reference

### Key Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Implementation Plan** | High-level overview of 9 stories | `implementation_plan.md` |
| **Master Checklist** | All tasks and acceptance criteria | `checklist.md` |
| **Technical Decisions** | Architecture decisions with rationale | `technical_decisions.md` |
| **Stories (9)** | Detailed implementation guides | `stories/PHASE4-001.md` through `PHASE4-009.md` |
| **Retrospective (template)** | Post-implementation review | `retrospective.md` |
| **This Handoff** | Getting started guide | `PHASE4_HANDOFF.md` |

### Story Sequence

| Order | Story ID | Story Name | Effort | Dependencies |
|-------|----------|------------|--------|--------------|
| 1 | PHASE4-001 | Environment Configuration | 4h | None |
| 2 | PHASE4-002 | Section 0 - Parameter Gathering | 6h | PHASE4-001 |
| 3 | PHASE4-003 | Section 1 - Agent Cards + WebSocket | 8h | PHASE4-001, PHASE4-002 |
| 4 | PHASE4-004 | Sections 2-3 - Forecast + Clusters | 6h | PHASE4-001 |
| 5 | PHASE4-005 | Sections 4-5 - Weekly Chart + Replenishment | 6h | PHASE4-001 |
| 6 | PHASE4-006 | Sections 6-7 - Markdown + Performance Metrics | 6h | PHASE4-001 |
| 7 | PHASE4-007 | CSV Upload Workflows | 8h | PHASE4-001, PHASE4-002, PHASE4-003 |
| 8 | PHASE4-008 | Integration Tests | 8h | PHASE4-001 through PHASE4-007 |
| 9 | PHASE4-009 | Documentation Updates | 4h | PHASE4-001 through PHASE4-008 |

**Parallelization Opportunities:**
- After PHASE4-001 completes: Stories 2, 4, 5, 6 can run in parallel (different sections)
- After PHASE4-003 completes: PHASE4-007 can start
- PHASE4-008 and PHASE4-009 must run last (depend on all previous stories)

---

## Prerequisites

### Before You Start

✅ **You should have:**
- Read `implementation_plan.md` (high-level overview)
- Read `technical_decisions.md` (understand architecture decisions)
- Access to:
  - GitHub repository (branch: `phase3-backend-henry-yina`)
  - Phase 1-3 completed code
  - Planning documents (`docs/04_MVP_Development/planning/`)

✅ **Required Skills:**
- Python 3.11+ (FastAPI, pytest, async/await)
- TypeScript 5 (React 18, hooks, async)
- REST API design (HTTP methods, status codes)
- WebSocket (connection lifecycle, reconnection)
- Testing (integration tests, MSW, TestClient)

✅ **Tools to Install:**
- Python 3.11+
- Node.js 18+
- UV (Python package manager): `pip install uv`
- Postman (for API testing)
- VS Code with extensions:
  - Python (Microsoft)
  - ESLint (Dirk Baeumer)
  - Prettier (Prettier)
  - REST Client (Huachao Mao) - optional alternative to Postman

---

## Getting Started - First Steps

### Step 1: Set Up Local Environment (PHASE4-001)

**Time Estimate:** 4 hours

**Start Here:** `stories/PHASE4-001-environment-configuration.md`

**What You'll Do:**
1. Create `backend/.env` file (9 environment variables)
2. Install backend dependencies with UV
3. Create `frontend/.env` file (1 environment variable)
4. Install frontend dependencies with npm
5. Create `src/config/api.config.ts` (15 API endpoints)
6. Create `src/services/apiClient.ts` (base HTTP client)
7. Test backend and frontend connection

**Validation:**
- Backend runs at http://localhost:8000
- Frontend runs at http://localhost:5173
- API docs accessible at http://localhost:8000/docs
- Frontend can call backend /health endpoint (no CORS errors)

**Common Issues:**
- **CORS errors:** Check `CORS_ORIGINS` in backend `.env` includes `http://localhost:5173`
- **Port conflicts:** Backend uses 8000, frontend uses 5173. Change if needed.
- **UV not found:** Install with `pip install uv`

---

### Step 2: Integrate Section 0 - Parameter Gathering (PHASE4-002)

**Time Estimate:** 6 hours

**Story:** `stories/PHASE4-002-section-0-parameter-gathering.md`

**What You'll Do:**
1. Test backend `POST /api/parameters/extract` in Postman (4 test cases)
2. Create `src/services/parameterService.ts`
3. Create `src/components/ParameterGathering.tsx`
4. Test natural language → SeasonParameters extraction

**Key Deliverable:** User can type "I need 8000 units over 12 weeks..." and see extracted parameters.

**Validation:**
- User input submitted successfully
- workflow_id returned
- Parameters displayed in UI (forecast_horizon_weeks, season_start_date, etc.)
- Error handling works for invalid input

---

### Step 3: Integrate Section 1 - Agent Cards + WebSocket (PHASE4-003)

**Time Estimate:** 8 hours

**Story:** `stories/PHASE4-003-section-1-agent-cards-websocket.md`

**What You'll Do:**
1. Test WebSocket connection with `wscat` (install globally: `npm install -g wscat`)
2. Create `src/services/websocketService.ts`
3. Create `src/hooks/useWebSocket.ts`
4. Create `src/components/AgentCards.tsx`
5. Test real-time agent status updates

**Key Deliverable:** 3 agent cards (Demand, Inventory, Pricing) update in real-time via WebSocket.

**Validation:**
- WebSocket connects successfully
- Agent cards show status (pending → running → completed)
- Progress bars animate (0% → 100%)
- Reconnection works after disconnect

---

### Step 4: Integrate Sections 2-7 (PHASE4-004, 005, 006)

**Time Estimates:** 6 hours each (18 hours total)

**Stories:**
- `PHASE4-004`: Forecast Summary + Cluster Cards
- `PHASE4-005`: Weekly Performance Chart + Replenishment Queue
- `PHASE4-006`: Markdown Decision + Performance Metrics

**Approach:**
- Each story follows same pattern: Test backend → Create service → Create component → Integrate
- These can be done in parallel by different developers (if available)

**Validation:**
- Each section displays data from backend
- Conditional sections (5, 6) show/hide correctly
- No console errors

---

### Step 5: Integrate CSV Upload Workflows (PHASE4-007)

**Time Estimate:** 8 hours

**Story:** `stories/PHASE4-007-csv-upload-workflows.md`

**What You'll Do:**
1. Test CSV upload endpoint in Postman (6 test cases)
2. Create `src/services/uploadService.ts`
3. Create `src/components/UploadZone.tsx` (drag-and-drop)
4. Create `src/components/UploadModal.tsx` (3 agent tabs)
5. Add "Upload Data" button to dashboard

**Key Deliverable:** Users can upload CSV files with drag-and-drop, see validation errors, and download error reports.

**Validation:**
- Drag-and-drop works
- File picker works
- Valid CSV uploads successfully
- Invalid CSV shows validation errors with row/column details
- Error report downloads as .txt file

---

### Step 6: Create Integration Tests (PHASE4-008)

**Time Estimate:** 8 hours

**Story:** `stories/PHASE4-008-integration-tests.md`

**What You'll Do:**
1. Set up pytest for backend (17+ tests)
2. Set up Vitest + MSW for frontend (8+ tests)
3. Run tests and generate coverage reports
4. Ensure coverage >80% (backend) and >70% (frontend)

**Key Deliverable:** Full test suite with integration tests for all API endpoints and frontend components.

**Validation:**
- All tests pass
- Backend coverage >80%
- Frontend coverage >70%
- No failing tests or warnings

---

### Step 7: Update Documentation (PHASE4-009)

**Time Estimate:** 4 hours

**Story:** `stories/PHASE4-009-documentation-updates.md`

**What You'll Do:**
1. Update root README.md (Phase 4 completion badge)
2. Update backend/README.md (all API endpoints)
3. Update frontend/README.md (all components)
4. Verify OpenAPI docs at http://localhost:8000/docs
5. Create architecture documentation
6. Create developer guide

**Key Deliverable:** Comprehensive documentation for all Phase 4 work.

**Validation:**
- All links work
- API examples tested
- Quick start instructions work on fresh machine
- No outdated information

---

## Key Concepts & Architecture

### Parameter-Driven Architecture (v3.3)

**Core Idea:** System behavior adapts based on 5 extracted parameters.

**Parameters:**
1. `forecast_horizon_weeks` (int): Number of weeks to forecast
2. `season_start_date`, `season_end_date` (datetime): Season duration
3. `replenishment_strategy` (enum): "none", "weekly", "bi-weekly"
4. `dc_holdback_percentage` (float 0-1): DC reserve percentage
5. `markdown_checkpoint_week` (int or null): Week to evaluate markdown
6. `markdown_threshold` (float 0-1 or null): Sell-through threshold for markdown

**Example Adaptations:**

```python
# Mock Demand Agent adapts safety stock based on replenishment_strategy
if parameters.replenishment_strategy == "none":
    safety_stock = 0.25  # Higher safety stock (no replenishment)
else:
    safety_stock = 0.20  # Standard safety stock

# Section 5 (Replenishment Queue) only displays if strategy != "none"
{parameters.replenishment_strategy !== 'none' && <ReplenishmentQueue />}

# Section 6 (Markdown Decision) only displays if checkpoint_week set
{parameters.markdown_checkpoint_week !== null && <MarkdownDecision />}
```

---

### WebSocket Message Flow

**6 Message Types:**

1. **agent_started:**
   ```json
   {
     "type": "agent_started",
     "agent_name": "Demand Agent",
     "timestamp": "2025-01-15T10:30:00Z"
   }
   ```

2. **agent_progress:**
   ```json
   {
     "type": "agent_progress",
     "agent_name": "Demand Agent",
     "progress": 45,
     "message": "Processing historical sales data...",
     "timestamp": "2025-01-15T10:30:15Z"
   }
   ```

3. **agent_completed:**
   ```json
   {
     "type": "agent_completed",
     "agent_name": "Demand Agent",
     "result": { "total_demand": 8000 },
     "timestamp": "2025-01-15T10:31:00Z"
   }
   ```

4. **human_input_required:**
   ```json
   {
     "type": "human_input_required",
     "agent_name": "Pricing Agent",
     "message": "Markdown threshold unclear. Please specify percentage.",
     "timestamp": "2025-01-15T10:32:00Z"
   }
   ```

5. **workflow_complete:**
   ```json
   {
     "type": "workflow_complete",
     "workflow_id": "wf_abc123",
     "timestamp": "2025-01-15T10:35:00Z"
   }
   ```

6. **error:**
   ```json
   {
     "type": "error",
     "agent_name": "Inventory Agent",
     "error_message": "Failed to fetch store data",
     "timestamp": "2025-01-15T10:33:00Z"
   }
   ```

**Connection Lifecycle:**
1. User submits parameters → workflow_id returned
2. Frontend connects to `ws://localhost:8000/api/workflows/{id}/stream`
3. Backend sends `agent_started` for each agent
4. Backend sends `agent_progress` updates (0-100%)
5. Backend sends `agent_completed` when agent finishes
6. Backend sends `workflow_complete` when all agents finish
7. Connection closes gracefully

---

### Conditional Section Display

**Rule:** Sections only display if relevant to current workflow.

**Section 5 (Replenishment Queue):**
- **Condition:** `replenishment_strategy !== "none"`
- **Rationale:** If user specified "no replenishment," there's no replenishment queue to display

**Section 6 (Markdown Decision):**
- **Condition:** `markdown_checkpoint_week !== null`
- **Rationale:** If user didn't specify a markdown checkpoint, markdown analysis doesn't apply

**Implementation:**
```typescript
// Section 5
{parameters.replenishment_strategy !== 'none' && (
  <ReplenishmentQueue workflowId={workflowId} />
)}

// Section 6
<MarkdownDecision workflowId={workflowId} />
// (Component internally returns null if markdown_checkpoint_week is null)
```

---

### CSV Upload Validation

**Two-Tier Validation:**

**Frontend (Pre-Upload):**
- File size (max 10MB)
- File extension (.csv only)
- File not empty

**Backend (Post-Upload):**
- CSV headers (required columns present)
- Data types (e.g., sales_units must be integer)
- Row-level validation (specific errors)

**Example Backend Validation Error:**
```json
{
  "validation_status": "INVALID",
  "errors": [
    {
      "error_type": "DATA_TYPE_MISMATCH",
      "row": 23,
      "column": "sales_units",
      "expected_type": "integer",
      "actual_value": "N/A",
      "message": "Row 23, column 'sales_units': expected integer, got 'N/A'"
    }
  ]
}
```

**Frontend displays errors in scrollable list with "Download Error Report" button.**

---

## Testing Strategy

### Integration Tests (PRIMARY)

**Backend (pytest):**
- 17+ integration tests covering all API endpoints
- Use `TestClient` for HTTP requests
- Use `websockets` library for WebSocket tests
- Mock database with in-memory SQLite

**Frontend (Vitest + MSW):**
- 8+ integration tests for services and components
- MSW (Mock Service Worker) intercepts API calls
- Test user interactions with `@testing-library/user-event`

**Coverage Goals:**
- Backend: >80%
- Frontend: >70%

**Run Tests:**
```bash
# Backend
cd backend
pytest tests/integration/ -v --cov=app --cov-report=html

# Frontend
cd frontend
npm run test:coverage
```

---

## Common Issues & Troubleshooting

### CORS Errors

**Symptom:** Frontend API calls fail with CORS error in browser console.

**Fix:**
1. Check `backend/.env` has `CORS_ORIGINS=http://localhost:5173`
2. Restart backend after changing `.env`
3. Clear browser cache (Ctrl+Shift+R)

---

### WebSocket Connection Fails

**Symptom:** "WebSocket connection failed" in console.

**Fix:**
1. Ensure backend is running at http://localhost:8000
2. Check WebSocket URL uses `ws://` (not `wss://` for local dev)
3. Check firewall allows WebSocket connections
4. Verify workflow_id is valid (exists in backend)

---

### CSV Upload Returns 400

**Symptom:** CSV upload fails with 400 Bad Request.

**Fix:**
1. Check CSV has required columns (see story PHASE4-007 for column names)
2. Check data types match expected types (no "N/A" in numeric columns)
3. Check file size <10MB
4. Check file extension is `.csv` (not `.xlsx`)
5. Download error report from UI to see specific validation errors

---

### Tests Failing

**Symptom:** Integration tests fail unexpectedly.

**Fix:**
1. Check backend is running (tests make real API calls in some cases)
2. Check test database is clean (delete `test.db` if exists)
3. Check MSW handlers match actual API endpoints (frontend)
4. Check test fixtures match expected data shapes

---

## Success Criteria - Phase 4 Complete

✅ **Phase 4 is complete when ALL of the following are true:**

### Functionality
- [ ] All 8 dashboard sections display correctly
- [ ] WebSocket real-time updates work
- [ ] CSV uploads work with validation
- [ ] Error handling works across all components
- [ ] Conditional sections (5, 6) show/hide correctly
- [ ] No console errors or warnings during normal operation

### Testing
- [ ] All backend integration tests pass (17+ tests)
- [ ] All frontend integration tests pass (8+ tests)
- [ ] Backend coverage >80%
- [ ] Frontend coverage >70%

### Documentation
- [ ] Root README updated with Phase 4 completion
- [ ] Backend README documents all API endpoints
- [ ] Frontend README documents all components
- [ ] OpenAPI docs complete and accessible
- [ ] Architecture docs created
- [ ] Developer guide complete

### Code Quality
- [ ] Backend follows PEP 8
- [ ] Frontend follows ESLint rules
- [ ] All type hints/annotations added
- [ ] No linting errors
- [ ] Code reviewed by team member

### Deliverables
- [ ] All 9 stories completed and validated
- [ ] Master checklist 100% complete
- [ ] Retrospective completed
- [ ] Code merged to main branch

---

## After Phase 4 - What's Next?

### Phase 5: Demand Agent Implementation

**Goal:** Replace mock Demand Agent with real forecasting logic (Prophet + ARIMA).

**Prerequisites from Phase 4:**
- `POST /api/parameters/extract` working (provides forecast_horizon_weeks)
- `GET /api/forecasts/{id}` endpoint defined (Phase 4 returns mock data)
- WebSocket connection working (for real-time progress updates)

**What Changes:**
- Backend: Implement Prophet + ARIMA forecasting
- Backend: Replace mock `total_demand` calculation with real forecast
- Frontend: No changes needed (already integrated in Phase 4)

### Phase 6: Inventory Agent Implementation

**Goal:** Replace mock Inventory Agent with real clustering and allocation logic.

### Phase 7: Pricing Agent Implementation

**Goal:** Replace mock Pricing Agent with real markdown optimization logic.

### Phase 8: End-to-End Testing & Cleanup

**Goal:** E2E tests, performance optimization, error handling polish, repository cleanup.

---

## Questions & Support

### During Implementation

**If you have questions:**
1. Check story details (most questions answered in ~1000 line stories)
2. Check `technical_decisions.md` (explains WHY decisions were made)
3. Check existing Phase 3 code (similar patterns)
4. Ask PM agent (create issue or tag in PR comments)

**If you find issues with planning:**
1. Document the issue in retrospective.md
2. Make necessary adjustments (planning is not perfect!)
3. Update this handoff document for future phases

---

## Handoff Checklist

Before starting implementation, confirm:

- [ ] Read `implementation_plan.md`
- [ ] Read `technical_decisions.md`
- [ ] Read this handoff document (PHASE4_HANDOFF.md)
- [ ] Have access to GitHub repository
- [ ] Have required tools installed (Python, Node.js, UV, Postman)
- [ ] Understand parameter-driven architecture (v3.3)
- [ ] Understand WebSocket message flow
- [ ] Understand conditional section display rules
- [ ] Understand CSV validation strategy
- [ ] Know where to find help (story details, technical decisions)

---

## Final Notes

### Phase 4 is a Critical Milestone

Phase 4 is the foundation for all future agent work. Take time to:
- **Test thoroughly** - Integration tests catch issues early
- **Document as you go** - Update docs when making changes
- **Ask questions** - Better to clarify now than refactor later

### You Have Detailed Stories

Each story is ~1000 lines with:
- Step-by-step tasks
- Code examples
- Postman test cases
- Manual testing checklists
- Validation criteria

**Trust the stories.** They're designed to guide you through implementation without ambiguity.

### Good Luck! 🚀

You're building the integration layer that will enable all future agent development. This is important work!

---

**Handoff Date:** [DATE]
**Prepared By:** PM Agent (John)
**For:** Developer(s) implementing Phase 4
**Questions?** See "Questions & Support" section above.
