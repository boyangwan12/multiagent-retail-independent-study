# Story: Build Section 5 - Replenishment Queue

**Epic:** Phase 2
**Story ID:** PHASE2-008
**Estimate:** 3 hours
**Dependencies:** PHASE2-002, PHASE2-006

---

## Story

As a user, I want to see replenishment recommendations in a sortable table, So that I can approve or reject restocking decisions.

---

## Acceptance Criteria

1. ✅ TanStack Table for replenishment recommendations
2. ✅ Columns: Store, SKU, Quantity, Urgency, Status
3. ✅ Sorting by urgency (High/Medium/Low)
4. ✅ Status badges (Pending, In Progress, Complete)
5. ✅ Action buttons (Approve, Reject)
6. ✅ Search/filter functionality

---

## Tasks

- [ ] Create ReplenishmentTable component
- [ ] Define columns (Store, SKU, Quantity, Urgency, Status)
- [ ] Add sorting by urgency
- [ ] Create status badges
- [ ] Add Approve/Reject buttons
- [ ] Implement search/filter

---

## Dev Notes

**Urgency Levels:**
- High: Red badge (#ef4444)
- Medium: Yellow badge (#f59e0b)
- Low: Green badge (#10b981)

**Reference:** `planning/5_front-end-spec_v3.3.md` lines 900-950

---

## File List

_Dev Agent populates_

---

**Created:** 2025-10-17
**Story Points:** 3
