# Story: End-to-End Integration Testing for Polling-Based Orchestrator

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-006
**Status:** Ready for Implementation
**Estimate:** 3 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001, PHASE5-002, PHASE5-004, PHASE5-005

**Planning References:**
- PRD v3.3: Section 5.4 (Testing & Validation)
- Technical Architecture v3.3: Section 6.3 (Integration Testing Strategy)

---

## Story

As a backend developer,
I want to create end-to-end integration tests for the orchestrator workflow,
So that I can verify all components (parameter extraction, agent handoffs, polling, error handling) work together correctly.

**Business Value:** Integration tests are the safety net that catches regressions before they reach production. Unit tests verify individual components (AgentHandoffManager, mock agents), but integration tests verify the complete user journey: parameter extraction → workflow creation → agent execution → status polling → results retrieval. This validates the orchestration foundation before building real ML agents in Phase 6, saving weeks of debugging complex integration issues.

**Epic Context:** This is Story 6 of 6 in Phase 5 (Orchestrator Foundation). It's the validation checkpoint - these tests prove that Stories 1-5 work together as a cohesive system. Passing integration tests gives us confidence to merge phase5-orchestrator-v2 to master and begin Phase 6.

**Phase 5 Update:** This story is updated from the original PHASE5-006 which assumed WebSocket testing and real historical data queries. Since we use polling-based status updates and mock agents with hard-coded data, tests focus on: (1) API endpoint integration, (2) polling-based status tracking, (3) agent handoff coordination, (4) error scenario handling, and (5) multi-scenario parameter validation.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ **End-to-end workflow test:** Parameter extraction → workflow creation → agent execution → completion
   - POST /api/v1/parameters/extract returns valid parameters
   - POST /api/v1/workflows/forecast creates workflow
   - POST /api/v1/workflows/{id}/execute starts execution
   - GET /api/v1/workflows/{id} polling shows status progression
   - Final status is "completed" with output_data

2. ✅ **Agent handoff test:** Verify Demand → Inventory → Pricing chain
   - Demand Agent output passed to Inventory Agent
   - Inventory Agent output passed to Pricing Agent
   - Final result contains outputs from all 3 agents

3. ✅ **Polling status test:** Verify status updates correctly
   - Status progresses: pending → running → completed
   - current_agent updates: Demand Agent → Inventory Agent → Pricing Agent
   - progress_pct increases: 0 → 10 → 40 → 50 → 70 → 75 → 95 → 100

4. ✅ **Parameter adaptation test:** Test 3 scenarios with different parameters
   - Scenario 1 (Zara): no replenishment, 0% holdback → 25% safety stock, 1 order
   - Scenario 2 (Traditional): weekly replenishment, 45% holdback → 20% safety stock, 3 orders
   - Scenario 3 (Luxury): bi-weekly replenishment, 30% holdback → 22% safety stock, 2 orders

5. ✅ **Error handling test:** Verify failures are reported correctly
   - Agent timeout scenario → status="failed", error_message populated
   - Invalid workflow ID → 404 response
   - Invalid parameters → 422 response with validation details

6. ✅ **Performance test:** Full workflow completes within expected time
   - Parameter extraction: <5 seconds
   - Workflow execution: <10 seconds (mock agents have delays)
   - Polling response time: <200ms

### Quality Requirements

7. ✅ Tests use realistic data (representative parameter sets)
8. ✅ Tests clean up resources (no orphaned workflows, no DB pollution)
9. ✅ Tests are idempotent (can run multiple times)
10. ✅ Test failures provide clear diagnostics
11. ✅ Test coverage >70% for orchestrator module
12. ✅ All tests pass in CI/CD environment

---

## Prerequisites

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] PHASE5-002 (Agent Handoff Framework) complete
- [x] PHASE5-004 (Enhanced Mock Agents) complete
- [x] PHASE5-005 (Error Handling) complete

**Testing Infrastructure:**
- [x] pytest installed
- [x] pytest-asyncio installed
- [x] FastAPI TestClient available

**Why This Matters:**
Without integration tests, every code change risks breaking the workflow. These tests establish a quality baseline that allows confident iteration.

---

## Tasks

### Task 1: Test End-to-End Workflow Execution

**Goal:** Verify complete user journey works

**File:** `backend/tests/integration/test_orchestrator_e2e.py`

**Implementation:** See full test code in story file

---

### Task 2: Test Agent Handoff Chain

**Goal:** Verify data flows between agents correctly

**File:** `backend/tests/integration/test_agent_handoffs.py`

**Implementation:** See full test code in story file

---

### Task 3-7: Additional Integration Tests

See detailed task breakdowns in full story document.

---

## Definition of Done

- [ ] End-to-end workflow test passes
- [ ] Agent handoff tests pass
- [ ] Polling status test passes
- [ ] 3 parameter scenario tests pass
- [ ] Error handling tests pass
- [ ] Performance tests pass
- [ ] Test helper functions created
- [ ] All tests pass consistently (run 3 times)
- [ ] Test coverage >70% for orchestrator module
- [ ] Changes committed to phase5-orchestrator-v2 branch

---

**Note:** Full implementation details available in complete story document.
