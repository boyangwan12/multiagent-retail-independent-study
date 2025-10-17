# Story: Build Section 3 - Cluster Cards with TanStack Table

**Epic:** Phase 2
**Story ID:** PHASE2-006
**Estimate:** 6 hours
**Dependencies:** PHASE2-002

---

## Story

As a user, I want to see forecast distribution across store clusters with detailed tables, So that I can understand allocation by segment.

---

## Acceptance Criteria

1. ✅ 3 cluster cards (Fashion Forward, Mainstream, Value Conscious)
2. ✅ TanStack Table v8 with sorting/filtering
3. ✅ Column definitions (Store, Forecast, Confidence, etc.)
4. ✅ Expandable row details for store-level data
5. ✅ Custom cell renderers (confidence bars, status badges)
6. ✅ Pagination for large clusters (>20 stores)

---

## Tasks

- [ ] Create ClusterCard component
- [ ] Integrate TanStack Table v8
- [ ] Define columns (Store, Forecast, Confidence, Status)
- [ ] Add expandable rows
- [ ] Create confidence bar cell renderer
- [ ] Create status badge cell renderer
- [ ] Add pagination
- [ ] Test sorting/filtering

---

## Dev Notes

**TanStack Table Example:**
```typescript
const columns = [
  { accessorKey: 'store_name', header: 'Store' },
  { accessorKey: 'forecast_units', header: 'Forecast' },
  { accessorKey: 'confidence', header: 'Confidence', cell: ConfidenceBar },
]
```

**Reference:** `planning/5_front-end-spec_v3.3.md` lines 700-800

---

## File List

_Dev Agent populates_

---

## Dev Agent Record

_Logs here_

---

**Created:** 2025-10-17
**Story Points:** 6
