# Phase X: [Phase Name] - Implementation Plan

**Phase:** Phase X
**Agent:** `*agent [role]`
**Duration:** [X weeks/days]
**Status:** Not Started | In Progress | Complete
**Start Date:** YYYY-MM-DD
**Target End Date:** YYYY-MM-DD

---

## Phase Overview

### Goal
[One-sentence description of what this phase delivers]

### Success Criteria
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

### Dependencies
**Requires:**
- ✅ [Prerequisite 1]
- ✅ [Prerequisite 2]

**Blocks:**
- Phase Y (cannot start until this completes)

---

## Reference Documents

**Primary:**
- [Document 1](../path/to/doc.md) - [Purpose]
- [Document 2](../path/to/doc.md) - [Purpose]

**Secondary:**
- [Document 3](../path/to/doc.md) - [Purpose]

---

## Task Breakdown

### Task 1: [Task Name]
**Priority:** P0 (Blocker) | P1 (High) | P2 (Nice to Have)
**Estimated Time:** [X hours/days]
**Dependencies:** [Task IDs this depends on]
**Assigned:** [Agent role]

**Description:**
[2-3 sentences describing what needs to be done]

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Validation:**
[How to verify this task is complete]

**Risks:**
- [Risk 1]: [Mitigation]
- [Risk 2]: [Mitigation]

---

### Task 2: [Task Name]
[Repeat structure]

---

## Task Dependencies Graph

```
Task 1 (2h)
  ↓
Task 2 (4h) ← Task 3 (1h)
  ↓
Task 4 (6h)
  ↓
Task 5 (3h)
```

**Critical Path:** Task 1 → Task 2 → Task 4 → Task 5 (15 hours)

---

## Timeline Estimate

| Day | Tasks | Cumulative Progress | Notes |
|-----|-------|---------------------|-------|
| Day 1 | Task 1-2 | 40% | Focus on setup |
| Day 2 | Task 3-4 | 75% | Core implementation |
| Day 3 | Task 5 | 100% | Validation + docs |

---

## Validation Checkpoints

### Checkpoint 1: [Milestone Name] (Day X)
**Exit Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**If Failed:**
[What to do if checkpoint fails]

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] | [Agent] |

---

## Notes for Agent

**Before Starting:**
1. Read all reference documents
2. Verify all dependencies met
3. Set up environment (see technical_decisions.md for requirements)

**During Implementation:**
1. Update checklist.md after each task
2. Document decisions in technical_decisions.md
3. Commit code + docs together

**After Completion:**
1. Validate all acceptance criteria
2. Write retrospective.md
3. Update README.md phase status

---

**Last Updated:** YYYY-MM-DD
**Status:** [Current status]
