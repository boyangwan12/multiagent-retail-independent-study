# Story: Build Section 4 - Weekly Performance Chart

**Epic:** Phase 2
**Story ID:** PHASE2-007
**Estimate:** 4 hours
**Dependencies:** PHASE2-002

---

## Story

As a user, I want to see weekly forecast vs actuals chart, So that I can identify variance and trigger re-forecasts.

---

## Acceptance Criteria

1. ✅ Recharts line chart (Forecast vs Actuals)
2. ✅ Week 5 variance annotation (>20% threshold)
3. ✅ Re-forecast trigger UI
4. ✅ Custom tooltip with breakdown
5. ✅ Responsive chart sizing

---

## Tasks

- [ ] Create WeeklyChart component with Recharts
- [ ] Implement 2 line series (Forecast, Actuals)
- [ ] Add Week 5 variance annotation
- [ ] Create custom tooltip
- [ ] Build re-forecast trigger button (shows when variance >20%)
- [ ] Make chart responsive

---

## Dev Notes

**Recharts Example:**
```tsx
<LineChart data={weeklyData}>
  <Line dataKey="forecast" stroke="#5e6ad2" />
  <Line dataKey="actual" stroke="#10b981" />
  <XAxis dataKey="week" />
  <YAxis />
  <Tooltip content={<CustomTooltip />} />
</LineChart>
```

**Reference:** `planning/5_front-end-spec_v3.3.md` lines 800-900

---

## File List

_Dev Agent populates_

---

**Created:** 2025-10-17
**Story Points:** 4
