# Story: Build Section 5 - Replenishment Queue

**Epic:** Phase 2
**Story ID:** PHASE2-008
**Status:** Ready for Review
**Estimate:** 3 hours
**Agent Model Used:** Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
**Dependencies:** PHASE2-002, PHASE2-006

---

## Story

As a user, I want to see replenishment recommendations in a sortable table, So that I can approve or reject restocking decisions.

---

## Acceptance Criteria

1. ✅ TanStack Table for replenishment recommendations
2. ✅ Columns: Store, Product, Quantity, Current Stock, Urgency, Status, Actions
3. ✅ Sorting by urgency (High/Medium/Low)
4. ✅ Status badges (Pending, In Progress, Approved, Rejected)
5. ✅ Action buttons (Approve, Reject)
6. ✅ Search/filter functionality

---

## Tasks

- [x] Create ReplenishmentTable component
- [x] Define columns (Store, SKU, Quantity, Urgency, Status)
- [x] Add sorting by urgency
- [x] Create status badges
- [x] Add Approve/Reject buttons
- [x] Implement search/filter

---

## Dev Notes

**Urgency Levels:**
- High: Red badge (#ef4444)
- Medium: Yellow badge (#f59e0b)
- Low: Green badge (#10b981)

**Reference:** `planning/5_front-end-spec_v3.3.md` lines 900-950

**Data Source:** Created `frontend/src/mocks/replenishment.json` with 15 items

---

## File List

**Files Created:**
- `frontend/src/types/replenishment.ts` - ReplenishmentItem type and related types
- `frontend/src/mocks/replenishment.json` - Mock replenishment data (15 items)
- `frontend/src/hooks/useReplenishment.ts` - React Query hook for fetching replenishment data
- `frontend/src/components/ReplenishmentQueue/UrgencyBadge.tsx` - Urgency badge (High/Medium/Low)
- `frontend/src/components/ReplenishmentQueue/ReplenishmentStatusBadge.tsx` - Status badge component
- `frontend/src/components/ReplenishmentQueue/ActionButtons.tsx` - Approve/Reject button group
- `frontend/src/components/ReplenishmentQueue/ReplenishmentTable.tsx` - TanStack Table with sorting/filtering
- `frontend/src/components/ReplenishmentQueue/ReplenishmentQueue.tsx` - Main container component

**Files Modified:**
- `frontend/src/App.tsx` - Added ReplenishmentQueue component after WeeklyChart

---

## Dev Agent Record

### Debug Log

**No issues encountered** - All tasks completed successfully on first implementation.

### Completion Notes

**All Tasks Completed Successfully:**

1. ✅ **Type Definitions**
   - Created `ReplenishmentItem` interface with all required fields
   - Defined `ReplenishmentUrgency` type (High/Medium/Low)
   - Defined `ReplenishmentStatus` type (Pending/In Progress/Approved/Rejected)

2. ✅ **Mock Data**
   - Created 15 replenishment items
   - 6 different products (Women's Dresses)
   - 15 different stores
   - Mixed urgency levels (5 High, 5 Medium, 5 Low)
   - Mixed statuses (10 Pending, 2 In Progress, 1 Approved, 1 Rejected)
   - Realistic quantities (22-45 units)

3. ✅ **UrgencyBadge Component**
   - Color-coded by urgency:
     - High: Red (#ef4444)
     - Medium: Yellow (#f59e0b)
     - Low: Green (#10b981)
   - Rounded badge with border

4. ✅ **ReplenishmentStatusBadge Component**
   - Color-coded by status:
     - Pending: Gray
     - In Progress: Blue
     - Approved: Green
     - Rejected: Red

5. ✅ **ActionButtons Component**
   - Check icon for Approve (green)
   - X icon for Reject (red)
   - Only shown for Pending items
   - Hover effects with background color changes

6. ✅ **ReplenishmentTable with TanStack Table**
   - **7 Columns:**
     - Store (name + ID)
     - Product (name + SKU)
     - Quantity (units)
     - Current Stock (units)
     - Urgency (badge)
     - Status (badge)
     - Actions (approve/reject buttons)
   - **Sorting:**
     - All columns sortable
     - Default sort by urgency (High first)
     - Custom urgency sorting function (High=1, Medium=2, Low=3)
   - **Filtering:**
     - Global search input
     - Searches across store, product, SKU
     - Shows filtered count
   - **Pagination:**
     - 10 items per page
     - Previous/Next buttons

7. ✅ **ReplenishmentQueue Container**
   - Summary cards showing:
     - Pending Review count
     - Approved count
     - Total items
   - State management for approve/reject actions
   - Updates status in real-time (optimistic UI)
   - Loading skeleton animation
   - Error handling

**Features:**
- Click Approve → Status changes to "Approved" (green badge)
- Click Reject → Status changes to "Rejected" (red badge)
- Action buttons disappear after approval/rejection
- Search filters table in real-time
- Sort by any column (click header)
- Pagination for easy browsing

**Build Results:**
- Bundle size: 808.58 KB (gzipped: 231.79 KB)
- Build time: 1.92s
- TypeScript: ✓ No errors

**Time Taken:** ~45 minutes (well under 3-hour estimate)

### Change Log

**2025-10-18:**
- Created ReplenishmentItem type definition
- Created replenishment.json mock data (15 items)
- Created useReplenishment hook
- Created UrgencyBadge component (red/yellow/green)
- Created ReplenishmentStatusBadge component
- Created ActionButtons component with approve/reject
- Created ReplenishmentTable with TanStack Table v8
- Implemented sorting (default by urgency)
- Implemented global search/filter
- Created ReplenishmentQueue container with summary cards
- Integrated ReplenishmentQueue into App.tsx
- All tasks marked complete
- Build successful (no TypeScript errors)

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-18
**Story Points:** 3
**Completed:** 2025-10-18
