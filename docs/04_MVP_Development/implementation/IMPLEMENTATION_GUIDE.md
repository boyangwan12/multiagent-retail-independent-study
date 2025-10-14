# Implementation Guide

**Project:** Fashion Retail Demand Forecasting & Inventory Allocation PoC
**Status:** Phase 1 - Data Generation (Ready to Start)
**Last Updated:** 2025-10-14
**BMad Agent:** `*agent dev`

---

## Overview

This guide provides comprehensive instructions for executing the 4-phase implementation process. All planning documents (v3.2) are complete - we are now **ready to code**.

**Purpose:** This is the single source of truth for all implementation activities. It covers workflows, best practices, troubleshooting, and daily routines for successful phase execution.

### Implementation Philosophy

- **One phase at a time** - Complete before moving to next
- **Single agent continuity** - Use `*agent dev` for Phases 1-3 (data + backend + frontend)
- **Document as you build** - Update docs during implementation, not after
- **Learn and adapt** - Retrospectives inform next phase

---

## Phase Status Tracker

| Phase | Status | Duration | Agent | Start Date | End Date | Docs |
|-------|--------|----------|-------|------------|----------|------|
| **Phase 1: Data Generation** | 🟡 Ready to Start | 1-2 days | `*agent dev` | TBD | TBD | 4/4 created |
| **Phase 2: Backend** | ⏳ Not Started | 3-4 weeks | `*agent dev` | TBD | TBD | 0/4 |
| **Phase 3: Frontend** | ⏳ Not Started | 3-4 weeks | `*agent dev` | TBD | TBD | 0/4 |
| **Phase 4: Testing** | ⏳ Not Started | 1-2 weeks | `*agent qa` | TBD | TBD | 0/4 |

**Legend:**
- ✅ Complete
- 🟡 Ready to Start / In Progress
- ⏳ Not Started
- 🔴 Blocked

---

## Phase Navigation

### Phase 1: Mock Data Generation (CURRENT - READY!)

**Goal:** Generate 38 CSV files with realistic sales data (MAPE 12-18%)

**Agent:** `*agent dev`

**Documents:**
- [Implementation Plan](./phase_1_data_generation/implementation_plan.md) ✅ Complete (12 tasks, 2-day timeline)
- [Technical Decisions](./phase_1_data_generation/technical_decisions.md) ✅ Created (update during coding)
- [Checklist](./phase_1_data_generation/checklist.md) ✅ Created (0/12 tasks)
- [Retrospective](./phase_1_data_generation/retrospective.md) ⏳ Complete after phase

**Quick Start:**
```bash
*agent dev

Task: Implement mock data generation script for Fashion Retail PoC

Reference: docs/04_PoC_Development/implementation/phase_1_data_generation/implementation_plan.md

Key deliverables:
- 38 CSV files (1 historical + 1 store attributes + 36 weekly actuals)
- 6 realism strategies for MAPE 12-18%
- 3 scenarios: normal_season, high_demand, low_demand
- Complete validation suite
- README.md with data dictionary
```

---

### Phase 2: Backend Implementation

**Goal:** Build 3-agent system with OpenAI Agents SDK + FastAPI

**Agent:** `*agent dev` (same agent, continuous work)

**Documents:**
- [Implementation Plan](./phase_2_backend/implementation_plan.md) ⏳ Create when Phase 1 complete
- [Technical Decisions](./phase_2_backend/technical_decisions.md) ⏳ Not Started
- [Checklist](./phase_2_backend/checklist.md) ⏳ Not Started
- [Retrospective](./phase_2_backend/retrospective.md) ⏳ Post-completion

**Prerequisites:**
- ✅ Phase 1 complete (training data available)
- ⏳ Azure OpenAI API keys configured
- ⏳ UV package manager installed

---

### Phase 3: Frontend Implementation

**Goal:** Build React dashboard with Linear Dark Theme

**Agent:** `*agent dev` (same agent, full-stack)

**Documents:**
- [Implementation Plan](./phase_3_frontend/implementation_plan.md) ⏳ Create when Phase 2 complete
- [Technical Decisions](./phase_3_frontend/technical_decisions.md) ⏳ Not Started
- [Checklist](./phase_3_frontend/checklist.md) ⏳ Not Started
- [Retrospective](./phase_3_frontend/retrospective.md) ⏳ Post-completion

**Prerequisites:**
- ✅ Phase 2 complete (backend API available)
- ⏳ Node.js 18+ installed
- ⏳ API contracts tested

---

### Phase 4: Testing & Validation

**Goal:** Validate system with 3 scenarios, confirm MAPE 12-18%

**Agent:** `*agent qa` (switch to QA specialist)

**Documents:**
- [Implementation Plan](./phase_4_testing/implementation_plan.md) ⏳ Create when Phase 3 complete
- [Technical Decisions](./phase_4_testing/technical_decisions.md) ⏳ Not Started
- [Checklist](./phase_4_testing/checklist.md) ⏳ Not Started
- [Retrospective](./phase_4_testing/retrospective.md) ⏳ Post-completion

**Prerequisites:**
- ✅ Phases 1-3 complete (full system functional)
- ⏳ All 3 scenario CSVs generated
- ⏳ E2E test framework setup

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
   - Review all planning documents (v3.2)
   - Read retrospective from previous phase (if applicable)
   - Verify prerequisites are met

2. **Review Phase Documents**
   - Read `implementation_plan.md` completely
   - Understand task dependencies
   - Note risk items and validation checkpoints

**Step 2: Start Phase**
```bash
*agent dev
Task: Begin Phase X implementation
Reference: docs/04_MVP_Development/implementation/phase_X/implementation_plan.md

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

**During Coding:**
- [ ] Work on tasks in dependency order
- [ ] Document decisions as they happen in `technical_decisions.md`
- [ ] Update `checklist.md` immediately after completing each task
- [ ] Commit code + updated docs together (small, frequent commits)

**End of Day:**
- [ ] Update implementation plan with actual time spent
- [ ] Note any blockers or risks discovered
- [ ] Update phase status if needed
- [ ] Plan next day's tasks

**Best Practices:**
- **Document decisions immediately** - Don't wait until end of phase
- **Commit frequently** - Code + docs together, small changes
- **Ask questions early** - Reference planning docs or ask user
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
   - [ ] Update "Docs" count to 4/4

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

## Reference Documents

**Planning Documents (v3.2):**
- [Product Brief](../product_brief/product_brief_v3.2.md)
- [Operational Workflow](../product_brief/operational_workflow_v3.2.md)
- [Technical Architecture](../architecture/technical_architecture_v3.2.md)
- [Frontend Spec](../design/front-end-spec_v3.2.md)
- [Data Specification](../data/data_specification_v3.2.md)
- [PRD](../prd/prd_v3.2.md)

**Next Steps Plan:**
- [Next Steps](../next_steps_plan.md) - High-level roadmap

---

## Document Templates

Each phase uses 4 standard documents:

1. **Implementation Plan** - Detailed task breakdown with dependencies and estimates
2. **Technical Decisions** - Design choices, alternatives considered, and rationale
3. **Checklist** - Granular task tracking with completion status
4. **Retrospective** - Lessons learned, what worked/didn't work

These documents are created fresh for each phase based on the specific work being done.

---

## Key Principles

### For BMad Agents

1. **Read before you code** - Always read implementation_plan.md first
2. **Document decisions** - Write technical_decisions.md as you code, not after
3. **Update checklists** - Check off tasks immediately after completion
4. **Learn from retrospectives** - Read previous phase retrospectives before starting new phase
5. **Ask for clarification** - If requirements unclear, reference planning docs or ask user

### For Developers

1. **Single source of truth** - This IMPLEMENTATION_GUIDE.md is the entry point
2. **Phase isolation** - Complete one phase before starting next
3. **Continuous documentation** - Docs and code evolve together
4. **Validate assumptions** - If planning docs contradict, ask before proceeding

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

---

## Tips for Effective Implementation

### Do ✅

- **Start each day by reading the implementation plan**
- **Update checklist immediately after completing tasks**
- **Commit code + docs together in small batches**
- **Write technical decisions while context is fresh**
- **Ask questions early when requirements are unclear**
- **Track actual time vs estimates for learning**
- **Run validation checkpoints at defined milestones**
- **Write retrospective immediately after phase completion**

### Don't ❌

- **Don't skip reading previous phase retrospectives**
- **Don't wait until end of phase to write all docs**
- **Don't add unplanned features without user approval**
- **Don't ignore validation checkpoint failures**
- **Don't commit code without updating docs**
- **Don't guess when planning docs are unclear**
- **Don't mark tasks complete before they're truly done**
- **Don't rush through retrospectives**

---

## Workflow Summary Diagram

```
┌─────────────────────────────────────────────────────────┐
│  BEFORE PHASE START                                     │
│  - Read planning docs (v3.2)                            │
│  - Review previous retrospective                        │
│  - Read implementation plan                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE START                                            │
│  - Activate BMad agent with handoff message             │
│  - Review all 4 phase documents                         │
│  - Set up environment/prerequisites                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  DAILY WORK LOOP (Repeat until phase complete)         │
│                                                         │
│  Morning:                                               │
│  └─ Review plan → Check tasks → Verify dependencies    │
│                                                         │
│  During Work:                                           │
│  └─ Code → Document decisions → Update checklist       │
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
│  3. Update README status                                │
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
- [ ] Phase 1: 38 CSV files generated, MAPE 12-18% validated
- [ ] Phase 2: 3-agent workflow <60s runtime
- [ ] Phase 3: Dashboard functional on 1280px+ screens
- [ ] Phase 4: All 3 scenarios pass, MAPE confirmed

---

## Current Priority: Phase 1

✅ **All Phase 1 documentation is ready!**

**Next Step:** Copy the handoff message above and start implementation:

```
*agent dev

Task: Implement mock data generation script for Fashion Retail PoC
Reference: docs/04_PoC_Development/implementation/phase_1_data_generation/implementation_plan.md
```

---

---

## Quick Reference Cheat Sheet

### Daily Checklist

**Every Morning:**
- [ ] Read implementation plan for today's tasks
- [ ] Check task dependencies
- [ ] Review yesterday's progress

**During Work:**
- [ ] Update checklist as tasks complete
- [ ] Document decisions in technical_decisions.md
- [ ] Commit code + docs together frequently

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

### File Quick Links

**Current Phase (Phase 1):**
- Implementation Plan: `./phase_1_data_generation/implementation_plan.md`
- Technical Decisions: `./phase_1_data_generation/technical_decisions.md`
- Checklist: `./phase_1_data_generation/checklist.md`
- Retrospective: `./phase_1_data_generation/retrospective.md`

**Planning Docs:**
- Product Brief: `../product_brief/product_brief_v3.2.md`
- Architecture: `../architecture/technical_architecture_v3.2.md`
- PRD: `../prd/prd_v3.2.md`
- Data Spec: `../data/data_specification_v3.2.md`
- Frontend Spec: `../design/front-end-spec_v3.2.md`

**Templates:**
- Templates are located in the company standard: `docs/00_template/implementation/templates/`

### Git Commit Template

```bash
git commit -m "[Phase X]: [Action] - [Description]

[Detailed notes]
- [Bullet 1]
- [Bullet 2]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

**Last Updated:** 2025-10-14
**Next Review:** After Phase 1 completion
**Status:** Ready for Phase 1 Implementation ✅
