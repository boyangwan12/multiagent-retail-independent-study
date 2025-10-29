# Implementation Guide

**Project:** Multi-Agent Retail Demand Forecasting System (v3.3 Parameter-Driven)
**Status:** Phase 4 - Frontend/Backend Integration (PRIORITY)
**Last Updated:** 2025-10-29
**Branch:** phase3-backend-henry-yina
**BMad Agent:** Use as specified per phase

---

## ⚠️ CRITICAL: Professor Feedback & New Direction

**Professor's Feedback (2025-10-29):**
1. ❌ **Repository too unstructured** - cleanup needed
2. ❌ **Frontend and backend not connected** - integrate them first
3. ✅ **Complete integration BEFORE building agents**

**Original Plan Issue:** We were planning to build all agents (Orchestrator, Demand, Inventory, Pricing) before connecting frontend to backend. This was backwards!

**NEW PLAN:** Integration-first approach
- ✅ Phases 1-3: COMPLETE (Data, Frontend mockups, Backend scaffolding)
- 🎯 **Phase 4: Frontend/Backend Integration** ← CURRENT PRIORITY
- ⏳ Phases 5-8: Agent implementation (AFTER integration works)

---

## Overview

This guide provides comprehensive instructions for executing the **REVISED 4-phase implementation process** for the parameter-driven multi-agent retail forecasting system.

### Revised Implementation Philosophy

- **Integration-First: Data → Frontend → Backend → INTEGRATION → Agents**
  - Rationale: Validate full stack works before adding complex AI logic
  - Frontend/Backend integration de-risks the project early
  - Agents can be built incrementally once integration is proven

- **Repository Cleanup** - Remove garbage, organize structure
- **One phase at a time** - Complete before moving to next
- **Document as you build** - Update docs during implementation, not after
- **All requirements from planning docs** - Single source of truth in `docs/04_MVP_Development/planning/`

---

## Phase Status Tracker

| Phase | Status | Duration | Agent | Start Date | End Date | Progress |
|-------|--------|----------|-------|------------|----------|----------|
| **Phase 1: Data Generation** | ✅ Complete | <1 day | `*agent dev` | 2025-10-17 | 2025-10-17 | 100% |
| **Phase 2: Frontend Mockup** | ✅ Complete | 3-4 days | `*agent ux-expert` | TBD | 2025-10-19 | 100% |
| **Phase 3: Backend Architecture** | ✅ Complete | 5-7 days | `*agent architect` | TBD | 2025-10-19 | 100% (14/14 stories) |
| **Phase 4: Frontend/Backend Integration** | 🟡 CURRENT PRIORITY | 5-7 days | `*agent dev` | TBD | TBD | 0% |
| **Phase 5: Demand Agent** | ⏳ Not Started | 5-7 days | `*agent dev` | TBD | TBD | 0% |
| **Phase 6: Inventory Agent** | ⏳ Not Started | 3-4 days | `*agent dev` | TBD | TBD | 0% |
| **Phase 7: Pricing Agent** | ⏳ Not Started | 2-3 days | `*agent dev` | TBD | TBD | 0% |
| **Phase 8: End-to-End Testing & Cleanup** | ⏳ Not Started | 5-7 days | `*agent qa` | TBD | TBD | 0% |

**Legend:**
- ✅ Complete
- 🟡 Current Priority / In Progress
- ⏳ Not Started
- 🔴 Blocked

**Total Estimated Duration:** 24-37 days (~3.5-5 weeks remaining)

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
| **Frontend Spec v3.3** | `planning/5_front-end-spec_v3.3.md` | Complete UI/UX design, all 8 sections |
| **Data Specification v3.2** | `planning/6_data_specification_v3.2.md` | CSV formats, validation rules |

**Critical Rule:** If implementation requirements are unclear, reference these planning documents first. Do NOT make assumptions.

---

## Completed Phases (1-3)

### ✅ Phase 1: Data Generation (COMPLETE)

**Status:** COMPLETE - 2025-10-17
**Agent:** `*agent dev`
**Duration:** <1 day (single session)

**Deliverables:**
- ✅ historical_sales_2022_2024.csv (164,400 rows)
- ✅ store_attributes.csv (50 stores)
- ✅ 36 weekly actuals CSVs (3 scenarios × 12 weeks)
- ✅ Validation suite (6 types - all passing)
- ✅ README.md documentation

**Success Metrics:**
- MAPE: 12-18% achievable ✅
- Week 5 Variance: 31.8%, 37.4%, 24.2% (Target: >20%) ✅
- K-means Silhouette: 0.521 (Target: >0.4) ✅

**Location:** `data/mock/`

**Key Learnings:**
- Comprehensive planning docs eliminated ambiguity
- Validation-driven development caught issues early
- Fixed seed (42) enabled reproducibility
- Cross-platform considerations (Windows encoding)

**Retrospective:** See `phase_1_data_generation/retrospective.md`

---

### ✅ Phase 2: Frontend Mockup (COMPLETE)

**Status:** COMPLETE - 2025-10-19
**Agent:** `*agent ux-expert`
**Duration:** 3-4 days

**Deliverables:**
- ✅ React 18 + TypeScript + Vite project setup
- ✅ Shadcn/ui + Tailwind CSS (Linear Dark Theme)
- ✅ All 8 sections implemented:
  - Section 0: Parameter Gathering with mock LLM extraction
  - Section 1: Fixed Header with Agent Cards
  - Section 2: Forecast Summary
  - Section 3: Cluster Cards (3 clusters, expandable tables)
  - Section 4: Weekly Performance Chart
  - Section 5: Replenishment Queue
  - Section 6: Markdown Decision
  - Section 7: Performance Metrics
- ✅ Mock WebSocket simulation (setTimeout-based)
- ✅ JSON fixtures from Phase 1 CSV data
- ✅ All interactions functional (buttons, sliders, tables)

**Location:** `frontend/src/`

**Components Inventory:**
- AgentWorkflow/ (AgentCard, FixedHeader)
- ClusterCards/ (ClusterCard, ClusterTable, ConfidenceBar)
- ForecastSummary/ (MetricCard)
- MarkdownDecision/ (ConfidenceIndicator, ImpactPreview)
- ParameterGathering/ (AgentReasoningPreview, ConfirmedBanner, ParameterCard)
- Layout/ (AppLayout, Sidebar, Breadcrumb)
- And 20+ more shared components

**Current State:**
- ⚠️ **Frontend uses MOCK data only**
- ⚠️ **NOT connected to backend API**
- ⚠️ **WebSocket is simulated with setTimeout**

**Retrospective:** See `phase_2_frontend/retrospective.md`

---

### ✅ Phase 3: Backend Architecture (COMPLETE)

**Status:** COMPLETE - 2025-10-19 (All 14 stories done)
**Agent:** `*agent architect` + `*agent dev`
**Duration:** 5-7 days

**Deliverables:**
- ✅ FastAPI project with UV package manager
- ✅ SQLite database with hybrid schema (normalized + JSON columns)
- ✅ Pydantic models (SeasonParameters, Forecast, Allocation, etc.)
- ✅ All 18 REST API endpoints implemented:
  - ✅ Parameter Extraction: POST /api/parameters/extract
  - ✅ Workflow: POST /api/workflows/forecast, POST /api/workflows/reforecast, GET /api/workflows/{id}
  - ✅ Resource: GET /api/forecasts, GET /api/forecasts/{id}, GET /api/allocations/{id}, GET /api/markdowns/{id}, GET /api/variance/{id}/week/{week}
  - ✅ Data Management: POST /api/data/upload-historical-sales, POST /api/data/upload-weekly-sales, GET /api/categories, GET /api/stores, GET /api/stores/clusters
  - ✅ Approvals: POST /api/approvals/manufacturing, POST /api/approvals/markdown
  - ✅ Agent Debug: POST /api/agents/demand/forecast, POST /api/agents/inventory/allocate, POST /api/agents/pricing/analyze
- ✅ WebSocket server (WS /api/workflows/{id}/stream) with 6 message types
- ✅ OpenAI Agents SDK integration (agent scaffolding)
- ✅ Parameter extraction service with OpenAI GPT-4o-mini
- ✅ ML pipeline scaffolding (Prophet, ARIMA, K-means placeholders)

**Location:** `backend/app/`

**Current State:**
- ⚠️ **All agents return MOCK/PLACEHOLDER data**
- ⚠️ **No actual Prophet/ARIMA forecasting implemented**
- ⚠️ **No K-means clustering implemented**
- ⚠️ **Frontend NOT calling these endpoints yet**

**Technical Stack:**
- Python 3.11+ with UV package manager
- FastAPI 0.115+
- OpenAI Agents SDK 0.3.3+
- SQLAlchemy + Alembic
- Pydantic 2.0+
- OpenAI API (migrated from Azure OpenAI)

**Retrospective:** See `phase_3_backend_architecture/retrospective.md` (if exists)

---

## 🎯 CURRENT PRIORITY: Phase 4 - Frontend/Backend Integration

**Goal:** Connect React frontend to FastAPI backend with REAL data flow (NO AI agents yet)

**Agent:** `*agent dev`

**Why This Phase Is Critical:**
1. **Professor's requirement** - Frontend and backend must hook up
2. **De-risk early** - Validate full stack works before complex AI logic
3. **Repository cleanup** - Remove unused files, organize structure
4. **End-to-end validation** - User can upload data, see responses, test WebSocket
5. **Baseline for agents** - Once integration works, agents can be swapped in incrementally

### Phase 4 Deliverables

**1. Repository Cleanup & Organization**
- [ ] Remove duplicate/unused files (identify "garbage")
- [ ] Consolidate documentation
- [ ] Clean up node_modules, Python cache files
- [ ] Update .gitignore to exclude build artifacts
- [ ] Organize folder structure (clear separation: backend/, frontend/, docs/, data/)
- [ ] Document project structure in README.md

**2. Environment Configuration**
- [ ] Backend `.env` with correct OpenAI API keys
- [ ] Frontend `.env` with backend API URL (e.g., VITE_API_URL=http://localhost:8000)
- [ ] CORS configuration in FastAPI (allow frontend origin)
- [ ] WebSocket connection settings

**3. Frontend Integration**
- [ ] Replace mock API calls with actual fetch/axios calls to backend
- [ ] Integrate parameter extraction (Section 0)
  - Call POST /api/parameters/extract with user input
  - Display extracted SeasonParameters in confirmation modal
- [ ] Connect workflow initiation (Section 1)
  - Call POST /api/workflows/forecast after parameter confirmation
  - Receive workflow_id and WebSocket URL
- [ ] Implement real WebSocket connection
  - Replace setTimeout mock with actual WebSocket client
  - Listen for 6 message types (agent_started, agent_progress, agent_completed, etc.)
  - Update agent cards in real-time
- [ ] Connect data upload workflows
  - Section: Upload historical sales CSV → POST /api/data/upload-historical-sales
  - Section: Upload weekly actuals → POST /api/data/upload-weekly-sales
- [ ] Display backend responses in all 8 sections
  - Forecast Summary: GET /api/forecasts/{id}
  - Cluster Cards: GET /api/stores/clusters
  - Weekly Chart: GET /api/variance/{id}/week/{week}
  - Replenishment: GET /api/allocations/{id}
  - Markdown: GET /api/markdowns/{id}
  - Metrics: Aggregate from multiple endpoints

**4. Backend Integration Points**
- [ ] Ensure all endpoints return correct JSON structure (match TypeScript types)
- [ ] Add error handling and validation
- [ ] Implement proper HTTP status codes (200, 400, 404, 500)
- [ ] Test CORS with frontend origin
- [ ] Verify WebSocket message broadcasting
- [ ] Seed database with Phase 1 CSV data for testing

**5. End-to-End Testing (No AI Yet)**
- [ ] Test parameter extraction flow
  - User enters: "12-week spring season, weekly replenishment, 45% holdback, markdown Week 6 @ 60%"
  - Backend extracts SeasonParameters correctly
  - Frontend displays extracted values
- [ ] Test workflow initiation
  - POST /api/workflows/forecast returns workflow_id
  - WebSocket connection established
  - Agent status cards show "mock agent" progress messages
- [ ] Test data upload
  - Upload historical_sales_2022_2024.csv
  - Backend parses and stores in database
  - Frontend shows success confirmation
- [ ] Test data retrieval
  - GET /api/forecasts returns mock forecast data
  - Frontend displays in Forecast Summary section
  - All 8 sections render without errors

**6. Documentation Updates**
- [ ] Update README.md with:
  - How to run backend (uvicorn)
  - How to run frontend (npm run dev)
  - Environment variable setup
  - API endpoint documentation
- [ ] Create INTEGRATION_TESTING.md checklist
- [ ] Update technical_decisions.md with integration choices

### Requirements Source

- **Primary:** `planning/5_front-end-spec_v3.3.md` - UI/UX requirements
- **Primary:** `planning/3_technical_architecture_v3.3.md` - API contracts
- **Reference:** `planning/4_prd_v3.3.md` - User stories and acceptance criteria

### Success Criteria

✅ **Phase 4 Complete When:**
1. User can start backend and frontend without errors
2. Frontend calls ALL backend endpoints successfully
3. Parameter extraction works end-to-end (natural language → SeasonParameters)
4. WebSocket connection streams real-time messages
5. CSV upload workflows functional (historical + weekly actuals)
6. All 8 frontend sections display backend data (mock/placeholder OK)
7. No console errors, all API calls return expected JSON
8. Repository is clean and organized (no garbage)
9. README.md has clear setup instructions
10. **Professor can run the full stack and see it working!**

### Quick Start for Phase 4

```bash
# 1. Start Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# 2. Start Frontend (separate terminal)
cd frontend
npm install
npm run dev

# 3. Test Integration
# - Open http://localhost:5173
# - Enter parameter text in Section 0
# - Click "Extract Parameters"
# - Verify backend call works and modal shows extracted params
# - Confirm parameters
# - Verify workflow starts and WebSocket connects
# - Check browser console for no errors
```

### Documents for Phase 4

- [Implementation Plan](./phase_4_integration/implementation_plan.md) ⏳ Create before starting
- [Technical Decisions](./phase_4_integration/technical_decisions.md) ⏳ Update during coding
- [Checklist](./phase_4_integration/checklist.md) ⏳ Create from plan
- [Retrospective](./phase_4_integration/retrospective.md) ⏳ Complete after phase

---

## Future Phases (5-8) - Agent Implementation

### Phase 5: Demand Agent Implementation

**Goal:** Replace mock forecast with REAL Prophet + ARIMA ensemble forecasting

**Agent:** `*agent dev`

**Key Deliverables:**
1. **Prophet Forecasting**
   - Implement time series forecasting with seasonal decomposition
   - Train on historical_sales_2022_2024.csv
   - Generate 12-week forecast
   - Duration: ~15-20s per model

2. **ARIMA Forecasting**
   - Auto-ARIMA parameter selection
   - Train on same historical data
   - Generate 12-week forecast
   - Duration: ~15-20s per model

3. **Ensemble Logic**
   - Simple average: (Prophet + ARIMA) / 2
   - Return combined forecast

4. **K-means Clustering**
   - Cluster 50 stores into 3 groups using 7 features
   - Assign cluster names: Fashion_Forward, Mainstream, Value_Conscious
   - Calculate allocation factors per cluster

5. **Parameter-Driven Adaptation**
   - IF replenishment_strategy == "none" THEN safety_stock = 25% ELSE 20%
   - LLM generates reasoning text for user

6. **Replace Placeholder**
   - Update `backend/app/agents/demand_agent.py`
   - Keep agent handoff structure from Phase 3
   - Return actual forecast instead of mock data

**Prerequisites:**
- ✅ Phase 4 complete (integration working)
- ✅ Phase 1 data available (historical sales CSV)
- ⏳ Prophet, pmdarima, scikit-learn installed

**Duration:** 5-7 days

**Documents:**
- [Implementation Plan](./phase_5_demand_agent/implementation_plan.md)
- [Technical Decisions](./phase_5_demand_agent/technical_decisions.md)
- [Checklist](./phase_5_demand_agent/checklist.md)
- [Retrospective](./phase_5_demand_agent/retrospective.md)

---

### Phase 6: Inventory Agent Implementation

**Goal:** Replace mock allocation with REAL manufacturing calculation + hierarchical allocation

**Agent:** `*agent dev`

**Key Deliverables:**
1. **Manufacturing Tool**
   - Formula: manufacturing_qty = total_demand × (1 + safety_stock_pct)
   - Receives safety_stock_pct from Demand Agent output
   - Duration: <1s

2. **Allocation Tool**
   - Input: dc_holdback_pct from SeasonParameters
   - Calculate initial_allocation_pct = 1 - dc_holdback_pct
   - Hierarchical allocation: cluster → store using allocation factors
   - Constraint: Minimum 2-week forecast per store
   - Duration: <2s

3. **Replenishment Tool**
   - Formula: replenish = max(0, next_week_forecast - current_inventory)
   - Constraint: Don't exceed DC inventory
   - Duration: <1s

4. **Parameter-Driven Adaptation**
   - IF replenishment_strategy == "none" THEN skip replenishment, allocate 100% at Week 0
   - LLM generates reasoning: "No replenishment → allocate all inventory upfront"

5. **Replace Placeholder**
   - Update `backend/app/agents/inventory_agent.py`
   - Receive forecast object from Demand Agent via handoff
   - Return actual allocation instead of mock data

**Prerequisites:**
- ✅ Phase 5 complete (Demand Agent working)
- ⏳ Allocation algorithms tested

**Duration:** 3-4 days

**Documents:**
- [Implementation Plan](./phase_6_inventory_agent/implementation_plan.md)
- [Technical Decisions](./phase_6_inventory_agent/technical_decisions.md)
- [Checklist](./phase_6_inventory_agent/checklist.md)
- [Retrospective](./phase_6_inventory_agent/retrospective.md)

---

### Phase 7: Pricing Agent Implementation

**Goal:** Replace mock markdown with REAL sell-through monitoring + Gap × Elasticity formula

**Agent:** `*agent dev`

**Key Deliverables:**
1. **Sell-Through Tool**
   - Formula: sell_through_rate = actual_sold / total_manufactured
   - Compare to target threshold
   - Duration: <1s

2. **Markdown Tool**
   - Formula: markdown = Gap × elasticity_coefficient
   - Gap = target_threshold - sell_through_rate
   - Round to nearest 5%, cap at 40%
   - Duration: <1s

3. **Markdown Application Tool**
   - Uniform across all stores (MVP)
   - Estimate sales lift: markdown_pct × 1.8
   - Duration: <1s

4. **Parameter-Driven Adaptation**
   - IF markdown_checkpoint_week is None THEN skip entire agent
   - Use markdown_threshold from SeasonParameters
   - LLM reasoning: "Week 6 @ 60% threshold → apply 10% markdown"

5. **Re-Forecast Trigger**
   - After markdown applied, trigger Orchestrator
   - Orchestrator enables re-forecast handoff to Demand Agent

6. **Replace Placeholder**
   - Update `backend/app/agents/pricing_agent.py`
   - Receive allocation object from Inventory Agent
   - Return actual markdown recommendation

**Prerequisites:**
- ✅ Phase 6 complete (Inventory Agent working)
- ⏳ Markdown elasticity formulas validated

**Duration:** 2-3 days

**Documents:**
- [Implementation Plan](./phase_7_pricing_agent/implementation_plan.md)
- [Technical Decisions](./phase_7_pricing_agent/technical_decisions.md)
- [Checklist](./phase_7_pricing_agent/checklist.md)
- [Retrospective](./phase_7_pricing_agent/retrospective.md)

---

### Phase 8: End-to-End Testing & Final Cleanup

**Goal:** Validate complete system across 3 scenarios + final repository cleanup

**Agent:** `*agent qa`

**Key Deliverables:**
1. **Scenario Testing** (3 scenarios from Phase 1)
   - **Normal Season:** Viral TikTok +30% Week 5, MAPE 12-15%
   - **High Demand:** Competitor bankruptcy +40% Week 5, MAPE 15-18%
   - **Low Demand:** Supply disruption -25% Week 5, MAPE 15-18%
   - Validate re-forecast triggered at Week 5 in all scenarios

2. **Parameter Flexibility Testing**
   - Test 4 parameter combinations:
     1. Fast fashion: 100% allocation, no replenishment, no markdown
     2. Premium retail: 45% holdback, weekly replenishment, no markdown
     3. Mainstream: 55% holdback, bi-weekly replenishment, Week 6 markdown @ 60%
     4. Value: 65% holdback, weekly replenishment, Week 4 markdown @ 50%
   - Verify agent adaptations and reasoning for each

3. **Performance Validation**
   - Workflow runtime <60s (target)
   - Prophet model ~15-20s
   - ARIMA model ~15-20s
   - Allocation + replenishment <3s
   - Markdown calculation <1s

4. **Accuracy Validation**
   - Hindcast Spring 2024 (12-week season)
   - Measure MAPE 12-18% across all 3 scenarios
   - Validate bias ±5%
   - Confirm re-forecast trigger accuracy 90%+

5. **Final Repository Cleanup**
   - Remove ALL unused files
   - Consolidate documentation
   - Clean up logs, cache, build artifacts
   - Verify .gitignore is comprehensive
   - Final README.md review

6. **Regression Test Suite**
   - Unit tests for each agent tool
   - Integration tests for API endpoints
   - WebSocket streaming tests
   - Database transaction tests

**Prerequisites:**
- ✅ Phases 5-7 complete (all agents implemented)
- ✅ All 3 scenario CSVs generated
- ⏳ Test framework setup (pytest, React Testing Library)

**Duration:** 5-7 days

**Documents:**
- [Implementation Plan](./phase_8_testing_cleanup/implementation_plan.md)
- [Technical Decisions](./phase_8_testing_cleanup/technical_decisions.md)
- [Checklist](./phase_8_testing_cleanup/checklist.md)
- [Retrospective](./phase_8_testing_cleanup/retrospective.md)

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
   - [ ] Update "Progress" percentage to 100%

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
6. **Integration-first** - Connect frontend/backend BEFORE building complex AI agents

### For Developers

1. **Single source of truth** - This IMPLEMENTATION_GUIDE.md is the entry point
2. **Phase isolation** - Complete one phase before starting next
3. **Continuous documentation** - Docs and code evolve together
4. **Validate assumptions** - If planning docs contradict, ask before proceeding
5. **Integration de-risks** - Prove the stack works before adding AI complexity

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

### Issue 7: Frontend/Backend Integration Fails

**Symptoms:** API calls return 404, CORS errors, WebSocket won't connect

**Solutions:**
- Check backend is running (`uvicorn app.main:app --reload`)
- Verify CORS settings in FastAPI (allow frontend origin)
- Check frontend API_URL environment variable
- Use browser DevTools Network tab to inspect requests/responses
- Test backend endpoints with Postman/curl first
- Check WebSocket URL format (ws:// not http://)
- Verify JSON structure matches TypeScript types exactly

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
- **Prioritize integration before complex AI logic**

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
- **Don't build agents before proving integration works**

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
│  3. Update guide status                                 │
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
- [x] Phase 1: 38 CSV files generated, MAPE 12-18% validated ✅
- [x] Phase 2: All 8 dashboard sections functional with mock data ✅
- [x] Phase 3: Backend architecture + API scaffolding complete ✅
- [ ] Phase 4: Frontend/backend integrated, end-to-end data flow working 🎯 CURRENT
- [ ] Phase 5: Demand Agent forecast accuracy <20% MAPE
- [ ] Phase 6: Inventory Agent allocation complete in <3s
- [ ] Phase 7: Pricing Agent markdown calculation <1s
- [ ] Phase 8: End-to-end workflow <60s runtime, MAPE 12-18%

---

## Current Priority: Phase 4 (Integration)

🎯 **All v3.3 planning documents are ready!**
✅ **Phases 1-3 are COMPLETE!**

**Next Step:** Start Phase 4 - Frontend/Backend Integration

**Why This is the Right Next Step:**
1. Professor feedback: Connect frontend and backend first
2. De-risk the project: Validate full stack before AI complexity
3. Incremental value: Users can test the system with mock agents
4. Clean foundation: Repository cleanup before adding more code

**Handoff Message for Phase 4:**

```
*agent dev

Task: Integrate React frontend with FastAPI backend - end-to-end data flow

Reference:
- docs/04_MVP_Development/planning/5_front-end-spec_v3.3.md (UI requirements)
- docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md (API contracts)

Context:
- Phase 1: Data generation COMPLETE
- Phase 2: Frontend mockups COMPLETE (all 8 sections with mock data)
- Phase 3: Backend architecture COMPLETE (18 API endpoints scaffolded)
- Professor feedback: Connect frontend/backend BEFORE building agents

Phase 4 Goals:
1. Repository cleanup (remove garbage, organize structure)
2. Replace frontend mock API calls with real backend calls
3. Connect parameter extraction (Section 0)
4. Implement real WebSocket connection (replace setTimeout mock)
5. Connect CSV upload workflows
6. Display backend responses in all 8 sections
7. End-to-end testing (no AI agents yet, mock data OK)

Success Criteria:
- User can run backend + frontend without errors
- All frontend sections call backend APIs successfully
- WebSocket streams real-time agent status updates
- CSV uploads work (historical sales, weekly actuals)
- Repository is clean and well-organized
- README.md has clear setup instructions

Duration Estimate: 5-7 days

Let's make the full stack work end-to-end! 🚀
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

**Completed Phases:**
- Phase 1: `./phase_1_data_generation/` ✅
- Phase 2: `./phase_2_frontend/` ✅
- Phase 3: `./phase_3_backend_architecture/` ✅

**Current Phase (Phase 4):**
- Implementation Plan: `./phase_4_integration/implementation_plan.md` ⏳ Create
- Technical Decisions: `./phase_4_integration/technical_decisions.md` ⏳ Create
- Checklist: `./phase_4_integration/checklist.md` ⏳ Create
- Retrospective: `./phase_4_integration/retrospective.md` ⏳ After completion

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

**Last Updated:** 2025-10-29 (REVISED - Integration-First Approach)
**Next Review:** After Phase 4 completion
**Status:** Ready for Phase 4 Implementation ✅
**Branch:** phase3-backend-henry-yina
**Strategic Order:** Data → Frontend → Backend → **INTEGRATION** → Agents (for early validation)
