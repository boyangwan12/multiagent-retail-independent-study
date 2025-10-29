# Phase 4: Frontend/Backend Integration

**Status:** NOT STARTED - Ready to Begin
**Priority:** HIGHEST (Professor's Requirement)
**Duration Estimate:** 5-7 days

---

## Overview

This phase connects the React frontend to the FastAPI backend with **REAL data flow** (NO AI agents yet).

### Why This Phase Exists

**Professor Feedback (2025-10-29):**
- Repository too unstructured → cleanup needed
- Frontend and backend not connected → **integrate them first**
- Complete integration BEFORE building agents

**Old Plan (Wrong):** Build agents first, then integrate
**New Plan (Correct):** Integration first, then build agents

---

## What Changed

### Old Phase Structure
1. Data Generation ✅
2. Frontend Mockup ✅
3. Backend Architecture ✅
4. **Orchestrator Agent** ← OLD
5. **Demand Agent** ← OLD
6. **Inventory Agent** ← OLD
7. **Pricing Agent** ← OLD
8. Integration Testing ← OLD

### NEW Phase Structure
1. Data Generation ✅
2. Frontend Mockup ✅
3. Backend Architecture ✅
4. **Frontend/Backend Integration** ← NEW (THIS PHASE)
5. Demand Agent
6. Inventory Agent
7. Pricing Agent
8. Testing & Cleanup

---

## Goals

**Primary Goal:** Connect React frontend to FastAPI backend with end-to-end data flow

**Sub-Goals:**
1. Repository cleanup (remove garbage, organize structure)
2. Replace frontend mock API calls with real backend calls
3. Connect parameter extraction (Section 0 UI)
4. Implement real WebSocket connection (replace setTimeout mock)
5. Connect CSV upload workflows
6. Display backend responses in all 8 sections
7. End-to-end testing (no AI agents yet, mock data OK)

---

## Success Criteria

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

---

## Current State

### What's Already Built

**Frontend (Phase 2 - COMPLETE):**
- ✅ All 8 sections with mock data
- ✅ Mock WebSocket (setTimeout-based)
- ✅ Linear Dark Theme
- ⚠️ **NOT connected to backend yet**

**Backend (Phase 3 - COMPLETE):**
- ✅ All 18 REST API endpoints
- ✅ WebSocket server
- ✅ Agent scaffolding (returns mock data)
- ⚠️ **Frontend NOT calling these endpoints yet**

### What Needs to Happen

1. **Wire them together** - Frontend calls backend
2. **Real WebSocket** - Replace setTimeout with actual WS
3. **Real data flow** - CSV upload → database → frontend display
4. **Clean up repo** - Remove unused files

---

## Documents to Create

Before starting this phase, create these 4 documents:

1. **implementation_plan.md** - Detailed task breakdown
2. **technical_decisions.md** - Record integration choices
3. **checklist.md** - Granular task tracking
4. **retrospective.md** - Complete AFTER phase is done

---

## Quick Start

**When you're ready to start this phase:**

```bash
*agent dev

Task: Integrate React frontend with FastAPI backend - end-to-end data flow

Reference:
- docs/04_MVP_Development/planning/5_front-end-spec_v3.3.md (UI requirements)
- docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md (API contracts)
- docs/04_MVP_Development/implementation/IMPLEMENTATION_GUIDE.md (this guide)

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

## Next Steps

1. Create `implementation_plan.md` in this folder
2. Start working through integration tasks
3. Document decisions in `technical_decisions.md`
4. Update `checklist.md` as tasks complete
5. Write `retrospective.md` after phase completes

---

**Created:** 2025-10-29
**Status:** Ready to Start
**Priority:** HIGHEST
