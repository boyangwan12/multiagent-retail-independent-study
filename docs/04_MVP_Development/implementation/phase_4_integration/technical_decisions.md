# Phase 4 Integration - Technical Decisions

**Phase:** Phase 4 - Frontend/Backend Integration
**Date Range:** [START DATE] - [END DATE]
**Decision Makers:** [Team Members]
**Status:** Planning Complete

---

## Overview

This document records all significant technical decisions made during Phase 4 planning and implementation, including the rationale behind each decision and alternatives that were considered.

---

## Decision Log

### TD-001: Integration-First Approach

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Architecture

**Context:**

Professor feedback indicated that the original implementation plan (agents first, then integration) was backwards. The repository was also too unstructured, and frontend/backend were not connected.

**Decision:**

**Adopt an integration-first approach:** Connect frontend and backend with mock agents BEFORE implementing real AI agents.

**Rationale:**

1. **Validates Full Stack Early:** Ensures communication layer works before adding AI complexity
2. **Reduces Risk:** Detects integration issues early when they're cheaper to fix
3. **Enables Parallel Work:** Once integration is done, multiple developers can work on agents independently
4. **Better Testing:** Can test UI flows with mock data before real agents are ready
5. **Aligns with Professor Feedback:** Explicitly addresses requirement to "hook frontend and backend together first"

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: Build all agents first, then integrate** | Agents fully functional from start | Integration issues discovered too late; high risk of major rework | Original plan that professor rejected |
| **B: Build one agent at a time with integration** | Incremental validation | Takes longer; each agent blocks next one | Slower progress; agents can be built in parallel once integration done |
| **C: Integration-first (CHOSEN)** | Validates stack early; enables parallel work; reduces risk | Mock agents need to be realistic | Best balance of risk reduction and speed |

**Impact:**

- Phase 4 moved from position 8 to position 4 in implementation plan
- Agents (Demand, Inventory, Pricing) moved to Phases 5-7
- All 8 dashboard sections must be integrated in Phase 4
- Mock agents must return dynamic, parameter-driven data

**Related Decisions:** TD-002 (Mock Agent Behavior)

---

### TD-002: Mock Agent Behavior - Dynamic vs. Static

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Implementation

**Context:**

Phase 4 integrates frontend/backend before real AI agents are built. We need mock agents to return data, but should they return static JSON or dynamic, parameter-aware data?

**Decision:**

**Mock agents MUST return dynamic data that adapts to extracted SeasonParameters.**

**Rationale:**

1. **Realistic Testing:** Dynamic mocks simulate real agent behavior more accurately
2. **Parameter Validation:** Tests that parameter-driven architecture (v3.3) works correctly
3. **Better User Experience:** Frontend testers see different results for different inputs
4. **Easier Transition:** Replacing dynamic mocks with real agents is simpler than replacing static mocks
5. **Demonstrates Adaptability:** Shows that system responds to user-specified constraints

**Example:**

```python
# ❌ BAD: Static mock data
def mock_demand_agent():
    return {"total_demand": 8000, "safety_stock": 0.20}

# ✅ GOOD: Dynamic mock data based on parameters
def mock_demand_agent(parameters: SeasonParameters):
    if parameters.replenishment_strategy == "none":
        safety_stock = 0.25  # Higher safety stock
        reasoning = "No replenishment → increased safety stock 20% → 25%"
    else:
        safety_stock = 0.20
        reasoning = f"{parameters.replenishment_strategy} → standard 20% safety stock"

    return {
        "total_demand": 8000,
        "safety_stock": safety_stock,
        "adaptation_reasoning": reasoning
    }
```

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: Static JSON responses** | Simplest to implement; fast | Doesn't test parameter-driven architecture; unrealistic | Doesn't demonstrate v3.3 adaptability |
| **B: Random data** | Different results each time | No relationship to parameters; confusing for testers | Not realistic; doesn't validate parameter extraction |
| **C: Dynamic, parameter-driven (CHOSEN)** | Realistic; tests v3.3 architecture; smooth transition to real agents | Slightly more complex | Best simulates real system behavior |

**Impact:**

- All backend mock agents must accept `SeasonParameters` as input
- Mock responses must include `adaptation_reasoning` explaining decisions
- Frontend can test parameter-driven flows before real agents exist

**Related Decisions:** TD-001 (Integration-First), TD-005 (Conditional Sections)

---

### TD-003: WebSocket vs. Polling for Real-Time Updates

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Architecture

**Context:**

Section 1 (Agent Cards) must display real-time agent status updates. Should we use WebSocket (persistent connection) or HTTP polling (repeated GET requests)?

**Decision:**

**Use WebSocket for real-time agent status updates.**

**Rationale:**

1. **Lower Latency:** WebSocket pushes updates instantly (vs. polling every 2-5 seconds)
2. **Less Backend Load:** One persistent connection vs. hundreds of HTTP requests
3. **Better UX:** Users see progress updates in real-time, not delayed
4. **Standard Practice:** WebSocket is industry standard for real-time updates
5. **Scales Better:** Backend can push to many clients efficiently

**WebSocket Message Types:**

1. `agent_started` - Agent begins execution
2. `agent_progress` - Progress update (0-100%)
3. `agent_completed` - Agent finished successfully
4. `human_input_required` - Agent needs user input
5. `workflow_complete` - All agents finished
6. `error` - Error occurred

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: HTTP Polling (every 2s)** | Simpler to implement; no WebSocket infrastructure | High backend load; 2-5s delay; wastes bandwidth | Outdated pattern; poor UX |
| **B: Server-Sent Events (SSE)** | One-way push; simpler than WebSocket | One-way only (no client→server); less browser support | WebSocket more flexible for future bidirectional needs |
| **C: WebSocket (CHOSEN)** | Real-time; bidirectional; low latency; standard practice | Requires WebSocket infrastructure; reconnection logic | Industry standard; best UX |

**Impact:**

- Backend must implement WebSocket endpoint: `ws://localhost:8000/api/workflows/{id}/stream`
- Frontend must create `WebSocketService` class with reconnection logic
- Frontend must create `useWebSocket` React hook for component integration
- AgentCards component updates in real-time (no polling delays)

**Related Decisions:** TD-004 (Reconnection Strategy)

---

### TD-004: WebSocket Reconnection Strategy

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Implementation

**Context:**

WebSocket connections can drop due to network issues, backend restarts, or timeouts. How should the frontend handle reconnection?

**Decision:**

**Implement exponential backoff reconnection with max 5 attempts.**

**Reconnection Logic:**

```typescript
class WebSocketService {
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000; // 2 seconds

  onClose(event: CloseEvent): void {
    if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      setTimeout(() => this.connect(workflowId), delay);
    }
  }
}
```

**Reconnection Delays:**

- Attempt 1: 2 seconds
- Attempt 2: 4 seconds
- Attempt 3: 8 seconds
- Attempt 4: 16 seconds
- Attempt 5: 32 seconds
- After 5 attempts: Show error to user

**Rationale:**

1. **Handles Transient Failures:** Network glitches often resolve in seconds
2. **Exponential Backoff:** Reduces backend load if issue is server-side
3. **User-Friendly:** Reconnects automatically without user intervention
4. **Fail Gracefully:** After 5 attempts, show error and let user retry manually

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: No reconnection (show error immediately)** | Simplest | Poor UX; transient failures require manual refresh | Too brittle for production |
| **B: Infinite reconnection** | Always tries to reconnect | Can spam backend; no user feedback | No exit condition; bad UX |
| **C: Exponential backoff (max 5) (CHOSEN)** | Balances automatic recovery with user control | Slightly more complex | Best balance of UX and resilience |

**Impact:**

- Frontend `WebSocketService` implements reconnection logic
- `useWebSocket` hook exposes `connectionStatus` state to components
- AgentCards component shows "Reconnecting..." status during reconnection
- After 5 failures, user sees "Connection Lost" error with "Retry" button

**Related Decisions:** TD-003 (WebSocket vs. Polling)

---

### TD-005: Conditional Section Display

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** UX/UI

**Context:**

Some dashboard sections only apply in certain scenarios:
- Section 5 (Replenishment Queue) only applies if `replenishment_strategy !== "none"`
- Section 6 (Markdown Decision) only applies if `markdown_checkpoint_week !== null`

Should these sections always display (with "Not Applicable" messages) or should they be hidden entirely?

**Decision:**

**Conditionally display sections based on parameters. Hidden sections do NOT render at all.**

**Rules:**

```typescript
// Section 5: Replenishment Queue
{parameters.replenishment_strategy !== 'none' && (
  <ReplenishmentQueue workflowId={workflowId} />
)}

// Section 6: Markdown Decision
<MarkdownDecision workflowId={workflowId} />
// (Component internally returns null if markdown_checkpoint_week is null)
```

**Rationale:**

1. **Cleaner UI:** Reduces visual clutter by hiding irrelevant sections
2. **Intuitive:** Users don't wonder why section says "Not Applicable"
3. **Validates Parameters:** Tests that parameter-driven architecture works correctly
4. **Easier to Understand:** Dashboard shows only what's relevant to current workflow

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: Always show all sections, display "Not Applicable"** | Consistent layout; users see all possible sections | Visual clutter; confusing UX | Users question why section exists if not applicable |
| **B: Collapse sections with "Expand to see why N/A"** | Educates users on conditions | Extra clicks; clutters UI | Adds unnecessary complexity |
| **C: Hide sections entirely (CHOSEN)** | Clean UI; intuitive; validates parameters | Layout shifts slightly | Best UX; reduces confusion |

**Impact:**

- Section 5 only renders when `replenishment_strategy !== "none"`
- Section 6 only renders when `markdown_checkpoint_week !== null`
- Backend returns 404 for Section 6 endpoint when markdown not applicable
- Frontend handles 404 gracefully (doesn't display section)

**Related Decisions:** TD-002 (Dynamic Mock Agents)

---

### TD-006: CSV Upload Validation - Frontend vs. Backend

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Implementation

**Context:**

CSV uploads must be validated before processing. Should validation happen:
- **Frontend only** (before upload)?
- **Backend only** (after upload)?
- **Both frontend and backend**?

**Decision:**

**Validate on both frontend (basic checks) and backend (comprehensive validation).**

**Frontend Validation (Pre-Upload):**
- File size (max 10MB)
- File extension (.csv only)
- File not empty

**Backend Validation (Post-Upload):**
- CSV headers (required columns present)
- Data types (e.g., sales_units must be integer)
- Row-level validation (with specific error messages)
- Duplicate detection

**Rationale:**

1. **Better UX:** Frontend catches obvious errors before upload (saves time)
2. **Security:** Backend validation prevents malicious uploads
3. **Comprehensive Validation:** Backend can check data integrity, not just format
4. **Detailed Errors:** Backend returns row/column-specific errors for debugging

**Example Backend Error:**

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

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: Frontend validation only** | Fast feedback; no server round-trip for errors | No security; can't validate data integrity | Backend must validate anyway for security |
| **B: Backend validation only** | Single source of truth; comprehensive | Slow feedback (user uploads, then waits for error) | Poor UX; wastes upload time on obvious errors |
| **C: Both frontend and backend (CHOSEN)** | Fast feedback + comprehensive validation + security | Validation logic duplicated | Best balance of UX, security, and data integrity |

**Impact:**

- Frontend `UploadService` validates file size/extension before upload
- Backend validates CSV format and data types after upload
- Backend returns detailed validation errors with row/column information
- Frontend displays validation errors in scrollable list
- Frontend offers "Download Error Report" as .txt file

**Related Decisions:** TD-007 (CSV Upload UI)

---

### TD-007: CSV Upload UI - Drag-and-Drop vs. File Picker Only

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** UX/UI

**Context:**

Users need to upload CSV files for agent workflows. Should the UI support:
- **File picker only** (click to browse)?
- **Drag-and-drop only**?
- **Both**?

**Decision:**

**Support both drag-and-drop AND file picker (click to browse).**

**Rationale:**

1. **User Preference:** Some users prefer drag-and-drop, others prefer file picker
2. **Accessibility:** File picker works better with keyboard navigation
3. **Modern UX:** Drag-and-drop is expected in modern web apps
4. **Flexibility:** Users can choose method that suits their workflow

**UploadZone Component Features:**

- Drag-and-drop zone (highlighted on drag-over)
- "Browse Files" button (opens file picker)
- File preview (name, size)
- Progress bar during upload
- Success state (green checkmark)
- Error state (validation errors + download report button)

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: File picker only** | Simplest; works everywhere | Less modern; slower for power users | Inferior UX; drag-and-drop is standard |
| **B: Drag-and-drop only** | Fastest for power users; modern | Accessibility issues; not obvious to all users | Excludes users who prefer file picker |
| **C: Both drag-and-drop and file picker (CHOSEN)** | Supports all user preferences; accessible; modern | Slightly more code | Best UX; supports all users |

**Impact:**

- Frontend `UploadZone` component implements both methods
- Drag-and-drop zone uses HTML5 drag-and-drop API
- File picker uses hidden `<input type="file">` element
- Both methods share same upload logic

**Related Decisions:** TD-006 (CSV Upload Validation)

---

### TD-008: Testing Strategy - Integration Tests vs. Unit Tests Priority

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Testing

**Context:**

Phase 4 requires comprehensive testing. Should we prioritize:
- **Unit tests** (individual functions/components)?
- **Integration tests** (frontend↔backend communication)?
- **End-to-end tests** (full user workflows)?

**Decision:**

**Prioritize integration tests in Phase 4. Unit tests and E2E tests are secondary.**

**Testing Priorities:**

1. **Integration Tests (PRIMARY):**
   - Backend: API endpoints with TestClient (pytest)
   - Frontend: Services + components with MSW (Vitest)
   - Coverage goal: >80% (backend), >70% (frontend)

2. **Unit Tests (SECONDARY):**
   - Utility functions (formatters, validators)
   - Not required for Phase 4 completion

3. **End-to-End Tests (FUTURE):**
   - Full user workflows with Playwright/Cypress
   - Deferred to Phase 8 (End-to-End Testing & Cleanup)

**Rationale:**

1. **Phase 4 Goal is Integration:** We're validating frontend↔backend communication
2. **Integration Tests Provide Most Value:** Catch contract mismatches between layers
3. **Time Constraint:** 48 hours estimated; integration tests are critical path
4. **Unit Tests Can Wait:** Most business logic is in agents (Phases 5-7)

**Backend Integration Tests:**

- Parameter extraction endpoint (4 test cases)
- WebSocket connection (3 test cases)
- Forecast/cluster/variance endpoints (4 test cases)
- Allocation endpoint (2 test cases)
- Markdown endpoint (2 test cases)
- CSV upload endpoint (2 test cases)

**Frontend Integration Tests:**

- Service layer (API calls with MSW mocks)
- Component integration (user interactions with API)

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: Unit tests only** | Fast to write; high coverage | Doesn't test integration; can miss contract issues | Doesn't validate Phase 4 goal (integration) |
| **B: E2E tests only** | Tests full workflows | Slow; brittle; expensive to maintain | Too slow for Phase 4; better suited for Phase 8 |
| **C: Integration tests (PRIMARY) (CHOSEN)** | Validates frontend↔backend; catches contract issues; good ROI | Doesn't test every function in isolation | Best balance for Phase 4 goal |

**Impact:**

- **Backend:** 17+ integration tests created with pytest
- **Frontend:** 8+ integration tests created with Vitest + MSW
- **Coverage:** Backend >80%, Frontend >70%
- **Unit tests:** Deferred to future phases (not blocking Phase 4 completion)

**Related Decisions:** TD-009 (Test Coverage Thresholds)

---

### TD-009: Test Coverage Thresholds

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Testing

**Context:**

What test coverage percentage should we require for Phase 4 completion?

**Decision:**

- **Backend:** >80% coverage required
- **Frontend:** >70% coverage required

**Rationale:**

1. **Backend is Simpler:** FastAPI endpoints are straightforward; 80% is achievable
2. **Frontend is Complex:** React components have many rendering paths; 70% is realistic
3. **Industry Standard:** 70-80% is common threshold in production systems
4. **Not 100%:** Diminishing returns; edge cases can be covered in later phases

**What Counts Toward Coverage:**

- **Backend:** Lines of code in `app/` directory (excludes `tests/`)
- **Frontend:** Lines of code in `src/` directory (excludes `src/tests/`)

**What to Prioritize:**

- **Backend:** API endpoints, parameter extraction, WebSocket logic
- **Frontend:** Service layer, component integration, error handling

**What Can Skip:**

- **Backend:** Edge cases in utility functions, rare error paths
- **Frontend:** UI styling, animation logic, purely presentational components

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: No coverage requirement** | Fastest implementation | Poor quality; regressions likely | Unacceptable for production system |
| **B: 100% coverage required** | Maximum confidence | Unrealistic; diminishing returns; slows development | Perfectionism is enemy of progress |
| **C: 70-80% coverage (CHOSEN)** | Good balance; industry standard; achievable | Some edge cases not covered | Best balance of quality and speed |

**Impact:**

- **CI/CD Checks:** Coverage reports generated on every commit
- **PR Reviews:** PRs with <70/80% coverage require justification
- **Phase 4 Completion:** Coverage thresholds must be met before moving to Phase 5

**Related Decisions:** TD-008 (Testing Strategy)

---

### TD-010: Story Granularity - 9 Stories vs. 3 Large Stories

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Project Management

**Context:**

How should Phase 4 work be broken down into stories?

**Decision:**

**Create 9 detailed stories (~1000 lines each) instead of 3 large stories.**

**Story Breakdown:**

1. Environment Configuration (4 hours)
2. Section 0 - Parameter Gathering (6 hours)
3. Section 1 - Agent Cards + WebSocket (8 hours)
4. Sections 2-3 - Forecast + Clusters (6 hours)
5. Sections 4-5 - Weekly Chart + Replenishment (6 hours)
6. Sections 6-7 - Markdown + Performance Metrics (6 hours)
7. CSV Upload Workflows (8 hours)
8. Integration Tests (8 hours)
9. Documentation Updates (4 hours)

**Rationale:**

1. **Better Tracking:** Smaller stories enable better progress visibility
2. **Easier Parallelization:** Multiple developers can work on different stories
3. **Clearer Scope:** Each story has clear deliverables and acceptance criteria
4. **Easier Reviews:** Smaller PRs are faster to review
5. **Follows Phase 3 Pattern:** Phase 3 had 14 stories; Phase 4 follows same structure

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: 3 large stories (Frontend, Backend, Testing)** | Fewer stories to manage | Unclear progress; hard to parallelize; huge PRs | Poor visibility; bottleneck on single developer |
| **B: 20+ micro-stories (one per section)** | Maximum granularity | Too much overhead; context switching | Over-engineered; excessive meetings |
| **C: 9 detailed stories (CHOSEN)** | Clear scope; parallelizable; good visibility | Requires upfront planning | Best balance; follows proven Phase 3 pattern |

**Impact:**

- **9 story files created** (~1000 lines each, ~9000 lines total)
- **Each story includes:**
  - User story
  - Acceptance criteria
  - Tasks with subtasks
  - Testing requirements
  - Validation checklists
- **Estimated effort:** 48 hours (6 days) total

**Related Decisions:** TD-011 (Story Detail Level)

---

### TD-011: Story Detail Level - High-Level vs. Detailed

**Decision Date:** [DATE]
**Status:** ✅ Approved
**Category:** Project Management

**Context:**

User confirmed they want stories "as detailed as Phase 3 stories (~1000 lines each)."

**Decision:**

**Create highly detailed stories with ~1000 lines each, following Phase 3 pattern.**

**Each Story Includes:**

1. **User Story** (1 paragraph)
2. **Context & Background** (2-3 paragraphs)
3. **Acceptance Criteria** (20-30 bullet points)
4. **Tasks** (5-10 tasks, each with 5-10 subtasks)
5. **Code Examples** (TypeScript/Python snippets)
6. **Postman Test Cases** (request/response examples)
7. **Validation Checklists** (manual testing steps)
8. **Definition of Done** (10-15 criteria)

**Rationale:**

1. **Reduces Ambiguity:** Detailed stories leave no room for interpretation
2. **Enables Handoff:** Another developer can implement without clarification
3. **Serves as Documentation:** Stories double as implementation guides
4. **Proven Pattern:** Phase 3 stories were detailed and successful
5. **User Preference:** User explicitly requested "as detailed as Phase 3"

**Alternatives Considered:**

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| **A: High-level stories (100-200 lines)** | Faster to write; flexibility for implementer | Ambiguous; requires clarification; risk of misinterpretation | User explicitly requested detailed stories |
| **B: Ultra-detailed (2000+ lines with diagrams)** | Maximum clarity | Takes too long to write; overwhelming | Diminishing returns; 1000 lines is sweet spot |
| **C: Detailed stories ~1000 lines (CHOSEN)** | Clear; comprehensive; proven pattern; user preference | Takes time to write | User explicitly requested this level |

**Impact:**

- **9 stories × 1000 lines ≈ 9000 lines total documentation**
- **Each story is self-contained** (can be implemented independently)
- **Code examples included** (TypeScript, Python, JSON, bash commands)
- **Postman test cases included** (request/response examples)
- **Manual testing checklists included** (step-by-step validation)

**Related Decisions:** TD-010 (Story Granularity)

---

## Summary of Key Decisions

| Decision ID | Decision | Impact |
|-------------|----------|--------|
| **TD-001** | Integration-first approach | Phase 4 moved before agent implementation |
| **TD-002** | Dynamic mock agents | Mock data adapts to parameters |
| **TD-003** | WebSocket for real-time updates | Instant agent status updates |
| **TD-004** | Exponential backoff reconnection | Handles network failures gracefully |
| **TD-005** | Conditional section display | Sections 5 & 6 hidden when not applicable |
| **TD-006** | Frontend + backend validation | CSV uploads validated on both sides |
| **TD-007** | Drag-and-drop + file picker | Supports all user preferences |
| **TD-008** | Integration tests prioritized | >80% backend, >70% frontend coverage |
| **TD-009** | Coverage thresholds | Backend >80%, Frontend >70% |
| **TD-010** | 9 detailed stories | Clear scope; parallelizable work |
| **TD-011** | ~1000 lines per story | Highly detailed, self-contained stories |

---

## Technology Stack Decisions

### Backend

| Technology | Decision | Rationale |
|------------|----------|-----------|
| **Language** | Python 3.11+ | Type hints; async support; team expertise |
| **Framework** | FastAPI 0.115+ | Modern; async; auto-generated OpenAPI docs |
| **Package Manager** | UV | Fastest Python package manager; simpler than poetry |
| **Database** | SQLite 3.45+ | Lightweight; sufficient for MVP; easy local dev |
| **WebSocket** | FastAPI WebSocket | Built-in; no extra dependencies |
| **Testing** | pytest + pytest-asyncio | Industry standard; excellent async support |

### Frontend

| Technology | Decision | Rationale |
|------------|----------|-----------|
| **Language** | TypeScript 5 | Type safety; better IDE support |
| **Framework** | React 18 | Team expertise; large ecosystem |
| **Build Tool** | Vite 5 | Faster than Webpack; modern |
| **UI Library** | Shadcn/ui + Tailwind CSS | Pre-built components; customizable; modern |
| **Charts** | Recharts | React-native; declarative; good docs |
| **Tables** | TanStack Table | Powerful; headless; good TypeScript support |
| **Testing** | Vitest + Testing Library | Vite-native; faster than Jest |
| **API Mocking** | MSW (Mock Service Worker) | Intercepts network requests; realistic tests |

---

## Open Questions

| Question | Status | Resolution | Date Resolved |
|----------|--------|------------|---------------|
| Should we add authentication in Phase 4? | ❌ Deferred | Defer to Phase 8 (not blocking MVP) | [DATE] |
| Should we support .xlsx uploads (not just .csv)? | ❌ No | Backend complexity not justified; .csv is standard | [DATE] |
| Should we add dark mode in Phase 4? | ❌ Deferred | Defer to Phase 8 (UX polish, not critical) | [DATE] |

---

## Decision Review Process

### When to Add a Decision

Add a new decision to this document when:
1. The decision affects multiple stories or the overall architecture
2. The decision involves trade-offs between alternatives
3. The decision might be questioned later ("Why did we do it this way?")
4. The decision affects future phases

### Decision Template

```markdown
### TD-XXX: [Decision Title]

**Decision Date:** [DATE]
**Status:** ⬜ Proposed | 🟡 Under Review | ✅ Approved | ❌ Rejected
**Category:** Architecture | Implementation | Testing | UX/UI | Project Management

**Context:**
[What problem are we solving? What constraints exist?]

**Decision:**
[What did we decide to do?]

**Rationale:**
[Why did we make this decision? What are the benefits?]

**Alternatives Considered:**
| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| A | | | |
| B | | | |

**Impact:**
[What changes because of this decision?]

**Related Decisions:** [List related TD-XXX IDs]
```

---

**Last Updated:** [DATE]
**Updated By:** [NAME]
