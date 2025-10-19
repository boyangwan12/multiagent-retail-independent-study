# Story: Build Section 4 - Weekly Performance Chart

**Epic:** Phase 2
**Story ID:** PHASE2-007
**Status:** Ready for Review
**Estimate:** 4 hours
**Agent Model Used:** Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
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

- [x] Create WeeklyChart component with Recharts
- [x] Implement 2 line series (Forecast, Actuals)
- [x] Add Week 5 variance annotation
- [x] Create custom tooltip
- [x] Build re-forecast trigger button (shows when variance >20%)
- [x] Make chart responsive

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

**Data Source:** `frontend/src/mocks/forecast.json` - weekly_demand_curve array

---

## File List

**Files Created:**
- `frontend/src/components/WeeklyChart/CustomTooltip.tsx` - Custom tooltip showing forecast, actual, and variance
- `frontend/src/components/WeeklyChart/WeeklyChart.tsx` - Main chart component with Recharts

**Files Modified:**
- `frontend/src/App.tsx` - Added WeeklyChart component after ClusterCards

---

## Dev Agent Record

### Debug Log

**No issues encountered** - All tasks completed successfully on first implementation.

### Completion Notes

**All Tasks Completed Successfully:**

1. ✅ **CustomTooltip Component**
   - Displays Week number
   - Shows Forecast value (blue)
   - Shows Actual value (green) when available
   - Displays Variance % with color coding:
     - Red: >20% (critical)
     - Yellow: 10-20% (warning)
     - Green: <10% (good)
   - Clean card design with Linear Dark Theme

2. ✅ **WeeklyChart Component with Recharts**
   - **Two Line Series:**
     - Forecast line (blue #5e6ad2)
     - Actuals line (green #10b981)
   - **Chart Features:**
     - CartesianGrid with dark theme
     - Labeled axes (Week / Units)
     - Legend with line icons
     - Responsive container (100% width, 400px height)
     - Smooth monotone curves

3. ✅ **Variance Annotations**
   - Automatic detection of weeks with variance >20%
   - Red dashed vertical lines at high variance weeks
   - Variance percentage labels at top of lines
   - Works for any week (not just Week 5)

4. ✅ **Re-forecast Trigger UI**
   - Yellow alert banner when variance >20% detected
   - Shows count of high variance weeks
   - "Trigger Re-forecast" button with RefreshCw icon
   - Success message after triggering
   - Auto-detects from data (no hardcoding)

5. ✅ **Responsive Design**
   - ResponsiveContainer adapts to screen width
   - Grid layout for footer info (3 columns desktop, 1 column mobile)
   - Proper margins and padding

6. ✅ **Additional Features**
   - Loading skeleton animation
   - Error handling with red alert
   - Chart footer showing:
     - Forecasting method (Ensemble Prophet ARIMA)
     - Peak week
     - Total season demand
   - Uses existing useForecast hook and forecast.json data

**Chart Configuration:**
- Width: 100% responsive
- Height: 400px
- Margins: top 20, right 30, left 20, bottom 20
- Grid: Dashed lines (#2a2a3c)
- Axes: Light gray text (#8b92a7)

**Data Integration:**
- Uses forecast.json weekly_demand_curve (12 weeks)
- Automatically handles null actual values (weeks 9-12)
- Calculates variance from existing data
- Week 5 in mock data has 28% variance (triggers alert)

**Build Results:**
- Bundle size: 796.79 KB (gzipped: 229.43 KB)
- Build time: 1.84s
- TypeScript: ✓ No errors
- Note: Bundle increased due to Recharts library (~400KB addition)

**Time Taken:** ~30 minutes (well under 4-hour estimate)

### Change Log

**2025-10-18:**
- Created CustomTooltip component with color-coded variance display
- Created WeeklyChart component with Recharts LineChart
- Implemented dual line series (Forecast vs Actuals)
- Added variance annotations (red dashed lines for >20%)
- Built re-forecast trigger UI (yellow alert + button)
- Made chart fully responsive
- Integrated WeeklyChart into App.tsx
- All tasks marked complete
- Build successful (no TypeScript errors)

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-18
**Story Points:** 4
**Completed:** 2025-10-18
