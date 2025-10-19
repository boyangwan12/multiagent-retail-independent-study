# Testing Checklist - Multi-Agent Retail Forecasting Dashboard

Comprehensive manual testing checklist for the Multi-Agent Retail Forecasting Dashboard. All tests should be performed before production deployment.

---

## Table of Contents

1. [Functional Tests](#functional-tests)
2. [UI/Visual Tests](#uivisual-tests)
3. [Interaction Tests](#interaction-tests)
4. [Error Handling Tests](#error-handling-tests)
5. [Accessibility Tests](#accessibility-tests)
6. [Performance Tests](#performance-tests)
7. [Responsiveness Tests](#responsiveness-tests)
8. [Cross-Browser Tests](#cross-browser-tests)

---

## Functional Tests

### Section 0: Parameter Gathering

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F0-01 | Character counter updates | 1. Type in textarea<br>2. Observe counter | Counter shows "X/500" and updates in real-time | ☐ Pass ☐ Fail |
| F0-02 | Extract button disabled when empty | 1. Clear textarea<br>2. Check button state | "Extract Parameters" button is disabled | ☐ Pass ☐ Fail |
| F0-03 | Extract parameters (valid input) | 1. Enter: "12-week spring season starting March 1st. No replenishment, 0% holdback."<br>2. Click "Extract Parameters"<br>3. Wait 2-5s | Modal appears with extracted parameters | ☐ Pass ☐ Fail |
| F0-04 | Extraction reasoning visible | 1. Complete F0-03<br>2. Expand "Extraction Reasoning" accordion | Shows how each parameter was extracted | ☐ Pass ☐ Fail |
| F0-05 | Edit workflow | 1. Complete F0-03<br>2. Click "Edit Parameters" | Modal closes, returns to textarea with original text | ☐ Pass ☐ Fail |
| F0-06 | Confirm workflow | 1. Complete F0-03<br>2. Click "Confirm & Continue" | Parameters saved, dashboard appears | ☐ Pass ☐ Fail |
| F0-07 | Confirmed banner shows parameters | 1. Complete F0-06<br>2. Scroll to top | Collapsed banner shows all 5 parameters inline | ☐ Pass ☐ Fail |
| F0-08 | Edit from banner | 1. Complete F0-07<br>2. Click "Edit" in banner | Parameters cleared, textarea reappears | ☐ Pass ☐ Fail |
| F0-09 | Incomplete extraction error | 1. Enter: "12 weeks"<br>2. Click "Extract Parameters" | Error message: "Could not extract all required parameters. Missing: [list]" | ☐ Pass ☐ Fail |

---

### Section 1: Agent Workflow

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F1-01 | Agent cards display | 1. Confirm parameters<br>2. Scroll to Section 1 | 3 agent cards visible: Demand, Inventory, Pricing | ☐ Pass ☐ Fail |
| F1-02 | Demand Agent execution | 1. Wait for Demand Agent to start<br>2. Observe status changes | Status: Idle → Running → Success<br>Progress: 0% → 100%<br>Messages update 4 times | ☐ Pass ☐ Fail |
| F1-03 | Inventory Agent execution | 1. Wait for Demand Agent to complete<br>2. Observe Inventory Agent | Starts automatically after Demand Agent<br>Completes with "Success" | ☐ Pass ☐ Fail |
| F1-04 | Pricing Agent execution | 1. Wait for Inventory Agent to complete<br>2. Observe Pricing Agent | Starts automatically after Inventory Agent<br>Completes with "Success" | ☐ Pass ☐ Fail |
| F1-05 | Overall progress calculation | 1. Watch fixed header during workflow | Overall progress increases from 0% to 100% | ☐ Pass ☐ Fail |
| F1-06 | Workflow completion banner | 1. Wait for all agents to complete | Green success banner appears: "Workflow Complete!" | ☐ Pass ☐ Fail |
| F1-07 | Fixed header shows season info | 1. Observe fixed header at top | Shows season name, dates, and progress | ☐ Pass ☐ Fail |

---

### Section 2: Forecast Summary

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F2-01 | Metric cards display | 1. Scroll to Section 2 | 4 metric cards visible:<br>- Total Units<br>- Projected Revenue<br>- Markdown Cost<br>- Excess Stock Risk | ☐ Pass ☐ Fail |
| F2-02 | Delta calculations | 1. Check each metric card | Each shows:<br>- Current value<br>- % change vs baseline<br>- Color-coded (green/red) | ☐ Pass ☐ Fail |
| F2-03 | Forecast insight panel | 1. Scroll below metric cards | Panel shows:<br>- Forecasting method<br>- Prophet & ARIMA values<br>- Peak week | ☐ Pass ☐ Fail |
| F2-04 | Loading skeleton | 1. Refresh page<br>2. Observe Section 2 during load | Shows pulsing skeleton boxes while loading | ☐ Pass ☐ Fail |

---

### Section 3: Cluster Distribution

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F3-01 | Cluster tables display | 1. Scroll to Section 3 | 3 tables visible:<br>- High Volume<br>- Medium Volume<br>- Low Volume | ☐ Pass ☐ Fail |
| F3-02 | Table sorting (ascending) | 1. Click "Store" column header once | Table sorts by store name A→Z | ☐ Pass ☐ Fail |
| F3-03 | Table sorting (descending) | 1. Click "Store" column header twice | Table sorts by store name Z→A | ☐ Pass ☐ Fail |
| F3-04 | Sort by allocated units | 1. Click "Allocated Units" header | Table sorts by units (high→low or low→high) | ☐ Pass ☐ Fail |
| F3-05 | Confidence bars display | 1. Observe "Confidence" column | Each row has colored progress bar (90-95%) | ☐ Pass ☐ Fail |
| F3-06 | Status badges display | 1. Observe "Status" column | Green "Allocated" badges on all rows | ☐ Pass ☐ Fail |

---

### Section 4: Weekly Performance

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F4-01 | Chart renders | 1. Scroll to Section 4 | Recharts AreaChart visible with:<br>- Purple forecast line<br>- Green/red bars for actuals<br>- Gray bars for future weeks | ☐ Pass ☐ Fail |
| F4-02 | Chart tooltip (on track week) | 1. Hover over green bar (e.g., Week 2) | Tooltip shows:<br>- Week number<br>- Forecast value<br>- Actual value<br>- Variance % (green) | ☐ Pass ☐ Fail |
| F4-03 | Chart tooltip (high variance week) | 1. Hover over red bar (if exists) | Tooltip shows variance >20% (red) | ☐ Pass ☐ Fail |
| F4-04 | Reference line visible | 1. Observe chart | Dashed horizontal line at 10% threshold | ☐ Pass ☐ Fail |
| F4-05 | X-axis labels | 1. Observe bottom of chart | Shows "Week 1" through "Week 12" | ☐ Pass ☐ Fail |
| F4-06 | Y-axis labels | 1. Observe left side of chart | Shows unit values (0, 200, 400, ...) | ☐ Pass ☐ Fail |

---

### Section 5: Replenishment Queue

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F5-01 | Table displays | 1. Scroll to Section 5 | Table with 10 rows visible | ☐ Pass ☐ Fail |
| F5-02 | Column sorting | 1. Click "Store" header | Table sorts by store name | ☐ Pass ☐ Fail |
| F5-03 | Urgency badges | 1. Observe "Urgency" column | Color-coded badges:<br>- 🔴 High<br>- 🟡 Medium<br>- 🟢 Low | ☐ Pass ☐ Fail |
| F5-04 | Status badges | 1. Observe "Status" column | Badges show:<br>- Pending (gray)<br>- Approved (green)<br>- Executed (blue) | ☐ Pass ☐ Fail |
| F5-05 | Approve action | 1. Click "Approve" on a Pending row | Status changes to "Approved"<br>Toast notification appears | ☐ Pass ☐ Fail |
| F5-06 | Reject action | 1. Click "Reject" on a Pending row | Status changes to "Rejected"<br>Toast notification appears | ☐ Pass ☐ Fail |
| F5-07 | Export CSV | 1. Click "Export CSV" button | Downloads `replenishment_queue_YYYY-MM-DD.csv` | ☐ Pass ☐ Fail |

---

### Section 6: Markdown Decision

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F6-01 | Scenario tabs display | 1. Scroll to Section 6 | 3 tabs visible:<br>- Conservative (20%)<br>- Moderate (30%)<br>- Aggressive (40%) | ☐ Pass ☐ Fail |
| F6-02 | Default scenario (Moderate) | 1. Observe default tab | Moderate (30%) is active<br>Impact preview shows 30% metrics | ☐ Pass ☐ Fail |
| F6-03 | Switch to Conservative | 1. Click "Conservative (20%)" tab | Impact preview updates to 20% metrics | ☐ Pass ☐ Fail |
| F6-04 | Switch to Aggressive | 1. Click "Aggressive (40%)" tab | Impact preview updates to 40% metrics | ☐ Pass ☐ Fail |
| F6-05 | Custom slider (increase) | 1. Drag slider to 35% | Impact preview updates in real-time<br>Shows 35% discount metrics | ☐ Pass ☐ Fail |
| F6-06 | Custom slider (decrease) | 1. Drag slider to 15% | Impact preview updates to 15% metrics | ☐ Pass ☐ Fail |
| F6-07 | Confidence indicator | 1. Observe confidence badge | Shows "High", "Medium", or "Low" with color | ☐ Pass ☐ Fail |
| F6-08 | Apply markdown | 1. Set slider to 25%<br>2. Click "Apply Markdown Strategy" | Toast notification: "Markdown strategy applied"<br>Sections 2 & 4 update | ☐ Pass ☐ Fail |
| F6-09 | Reset to defaults | 1. After F6-08, click "Reset" | Slider returns to 30% (Moderate) | ☐ Pass ☐ Fail |

---

### Section 7: Performance Metrics

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| F7-01 | Metric cards display | 1. Scroll to Section 7 | 3 metric cards visible with MAPE, accuracy, variance | ☐ Pass ☐ Fail |
| F7-02 | Historical chart renders | 1. Observe chart below metric cards | AreaChart shows 4 quarters of MAPE trend | ☐ Pass ☐ Fail |
| F7-03 | Agent contribution section | 1. Scroll below chart | Shows 3 agent bars:<br>- Demand Agent (%)<br>- Inventory Agent (%)<br>- Pricing Agent (%) | ☐ Pass ☐ Fail |
| F7-04 | Sparklines display | 1. Observe agent contribution bars | Each has mini sparkline chart (trend) | ☐ Pass ☐ Fail |
| F7-05 | Export report | 1. Click "Export Report" button | Downloads `performance_report_YYYY-MM-DD.pdf` | ☐ Pass ☐ Fail |

---

## UI/Visual Tests

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| UI-01 | Linear Dark Theme applied | 1. View entire dashboard | Background: #0D0D0D (near-black)<br>Cards: #1A1A1A (dark gray)<br>Primary: #5E6AD2 (purple-blue) | ☐ Pass ☐ Fail |
| UI-02 | Text contrast | 1. Read all text elements | White text on dark background<br>Contrast ratio ≥21:1 | ☐ Pass ☐ Fail |
| UI-03 | Agent colors consistent | 1. View Section 1 (agents)<br>2. View Section 7 (agent contribution) | Demand: #5B8DEF (blue)<br>Inventory: #00D084 (green)<br>Pricing: #F59E0B (amber) | ☐ Pass ☐ Fail |
| UI-04 | Status colors consistent | 1. Observe all status badges | Success: #00D084 (green)<br>Warning: #F5A623 (amber)<br>Error: #F97066 (red) | ☐ Pass ☐ Fail |
| UI-05 | Card styling consistent | 1. View all sections | All cards have:<br>- Rounded corners (rounded-lg)<br>- Border (#2A2A2A)<br>- Padding (p-6) | ☐ Pass ☐ Fail |
| UI-06 | Typography consistent | 1. View all text | Headings: text-2xl/3xl/4xl<br>Body: text-sm/base<br>Font: Inter (sans) | ☐ Pass ☐ Fail |
| UI-07 | Icon consistency | 1. View all icons | All icons from Lucide React<br>Same size within sections | ☐ Pass ☐ Fail |
| UI-08 | Loading states | 1. Refresh page<br>2. Observe sections during load | Skeleton loaders with pulsing animation | ☐ Pass ☐ Fail |
| UI-09 | Hover states | 1. Hover over buttons, cards, table rows | Subtle background change to #1F1F1F | ☐ Pass ☐ Fail |
| UI-10 | Focus indicators | 1. Tab through interactive elements | Blue ring (focus:ring-2 focus:ring-primary) visible | ☐ Pass ☐ Fail |

---

## Interaction Tests

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| INT-01 | Sidebar navigation (click) | 1. Click "Agent Workflow" in sidebar | Smooth scroll to Section 1 | ☐ Pass ☐ Fail |
| INT-02 | Sidebar navigation (all sections) | 1. Click each section in sidebar | Each scrolls to correct section | ☐ Pass ☐ Fail |
| INT-03 | Sidebar active state | 1. Scroll through dashboard | Active section highlights in sidebar with purple accent | ☐ Pass ☐ Fail |
| INT-04 | Keyboard shortcut Alt+1 | 1. Press Alt+1 | Scrolls to Section 1 (Agents) | ☐ Pass ☐ Fail |
| INT-05 | Keyboard shortcut Alt+2 | 1. Press Alt+2 | Scrolls to Section 2 (Forecast) | ☐ Pass ☐ Fail |
| INT-06 | Keyboard shortcut Alt+3-8 | 1. Press Alt+3 through Alt+8 | Each scrolls to corresponding section | ☐ Pass ☐ Fail |
| INT-07 | Keyboard shortcut Alt+H | 1. Scroll to bottom<br>2. Press Alt+H | Scrolls to top of page | ☐ Pass ☐ Fail |
| INT-08 | Modal open/close (ESC) | 1. Open parameter confirmation modal<br>2. Press ESC | Modal closes | ☐ Pass ☐ Fail |
| INT-09 | Modal open/close (click outside) | 1. Open modal<br>2. Click background overlay | Modal closes | ☐ Pass ☐ Fail |
| INT-10 | Accordion expand/collapse | 1. Click "Extraction Reasoning"<br>2. Click again | First click: expands<br>Second click: collapses | ☐ Pass ☐ Fail |
| INT-11 | Tab navigation | 1. Press Tab repeatedly | Focus moves through all interactive elements in order | ☐ Pass ☐ Fail |
| INT-12 | Button activation (Enter) | 1. Tab to a button<br>2. Press Enter | Button action triggers | ☐ Pass ☐ Fail |
| INT-13 | Button activation (Space) | 1. Tab to a button<br>2. Press Space | Button action triggers | ☐ Pass ☐ Fail |

---

## Error Handling Tests

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| ERR-01 | Error boundary (section level) | 1. Simulate error in Section 2 (modify code to throw error)<br>2. Observe | Section 2 shows error fallback<br>Other sections still work | ☐ Pass ☐ Fail |
| ERR-02 | Error boundary retry | 1. After ERR-01<br>2. Click "Try again" button | Page reloads or section retries | ☐ Pass ☐ Fail |
| ERR-03 | Error boundary details | 1. After ERR-01<br>2. Expand "Error details" | Shows error message and stack trace | ☐ Pass ☐ Fail |
| ERR-04 | Toast notification (success) | 1. Trigger success action (e.g., approve replenishment)<br>2. Observe | Green toast appears bottom-right<br>Auto-dismisses after 5s | ☐ Pass ☐ Fail |
| ERR-05 | Toast notification (error) | 1. Trigger error action<br>2. Observe | Red toast appears with error message | ☐ Pass ☐ Fail |
| ERR-06 | Toast notification (close button) | 1. Trigger toast<br>2. Click X button | Toast disappears immediately | ☐ Pass ☐ Fail |
| ERR-07 | Network error (forecast fetch) | 1. Block network in DevTools<br>2. Refresh page | Error message: "Failed to fetch forecast data" | ☐ Pass ☐ Fail |
| ERR-08 | Network error (replenishment fetch) | 1. Block network<br>2. Navigate to Section 5 | Error message in Section 5 only | ☐ Pass ☐ Fail |
| ERR-09 | Invalid parameter extraction | 1. Enter gibberish in textarea<br>2. Click "Extract Parameters" | Error: "Could not extract all required parameters" | ☐ Pass ☐ Fail |

---

## Accessibility Tests

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| A11Y-01 | Sidebar ARIA labels | 1. Inspect sidebar with screen reader | role="navigation"<br>aria-label="Main navigation" | ☐ Pass ☐ Fail |
| A11Y-02 | Navigation buttons ARIA | 1. Inspect sidebar buttons | Each has aria-label="Navigate to [Section]"<br>Active has aria-current="page" | ☐ Pass ☐ Fail |
| A11Y-03 | Section headers semantic HTML | 1. Inspect section headers | Uses `<section>` and `<h2>` tags | ☐ Pass ☐ Fail |
| A11Y-04 | Toast notifications ARIA | 1. Trigger toast<br>2. Inspect with screen reader | Container has aria-live="polite"<br>Toast has role="status" | ☐ Pass ☐ Fail |
| A11Y-05 | Modal ARIA | 1. Open parameter modal<br>2. Inspect | role="dialog"<br>aria-labelledby="title" | ☐ Pass ☐ Fail |
| A11Y-06 | Button labels | 1. Tab through all buttons<br>2. Check screen reader | All buttons have accessible names | ☐ Pass ☐ Fail |
| A11Y-07 | Image alt text | 1. Inspect all images/icons | Decorative icons: aria-hidden="true"<br>Meaningful images: alt text present | ☐ Pass ☐ Fail |
| A11Y-08 | Focus indicators visible | 1. Tab through interactive elements | Blue focus ring visible on all elements | ☐ Pass ☐ Fail |
| A11Y-09 | Color contrast (text) | 1. Use axe DevTools<br>2. Check contrast | All text meets WCAG AA (≥4.5:1) | ☐ Pass ☐ Fail |
| A11Y-10 | Color contrast (interactive) | 1. Check buttons, links | All meet WCAG AA (≥4.5:1) | ☐ Pass ☐ Fail |
| A11Y-11 | Keyboard navigation (no traps) | 1. Tab through entire dashboard<br>2. Ensure can Tab out of all elements | No keyboard traps | ☐ Pass ☐ Fail |
| A11Y-12 | Screen reader (headings) | 1. Use screen reader heading navigation | Can navigate by headings (H1, H2, H3) | ☐ Pass ☐ Fail |
| A11Y-13 | Screen reader (landmarks) | 1. Use screen reader landmark navigation | Can navigate by landmarks (nav, main, section) | ☐ Pass ☐ Fail |
| A11Y-14 | axe DevTools audit | 1. Run axe DevTools on dashboard | 0 violations (or all documented) | ☐ Pass ☐ Fail |

---

## Performance Tests

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| PERF-01 | Initial page load | 1. Open dashboard in incognito<br>2. Measure with DevTools Performance | First Contentful Paint: <1.5s<br>Time to Interactive: <3s | ☐ Pass ☐ Fail |
| PERF-02 | Bundle size | 1. Run `npm run build`<br>2. Check dist/ size | Total: <1 MB<br>Gzipped: <250 KB | ☐ Pass ☐ Fail |
| PERF-03 | Lighthouse score | 1. Run Lighthouse audit | Performance: ≥90<br>Accessibility: 100<br>Best Practices: ≥90 | ☐ Pass ☐ Fail |
| PERF-04 | Chart rendering | 1. Navigate to Section 4 (chart)<br>2. Measure render time | Chart renders in <500ms | ☐ Pass ☐ Fail |
| PERF-05 | Table sorting performance | 1. Sort large table (100+ rows)<br>2. Measure time | Sort completes in <200ms | ☐ Pass ☐ Fail |
| PERF-06 | Memory usage | 1. Open dashboard<br>2. Use DevTools Memory profiler | No memory leaks during 5 min usage | ☐ Pass ☐ Fail |
| PERF-07 | React Query caching | 1. Navigate between sections<br>2. Check Network tab | Data fetched only once (cached on repeat) | ☐ Pass ☐ Fail |

---

## Responsiveness Tests

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| RESP-01 | Desktop (1920x1080) | 1. Set viewport to 1920x1080<br>2. View dashboard | All sections visible, no horizontal scroll | ☐ Pass ☐ Fail |
| RESP-02 | Desktop (1280x720) | 1. Set viewport to 1280x720 | Dashboard functional, readable | ☐ Pass ☐ Fail |
| RESP-03 | Tablet landscape (1024x768) | 1. Set viewport to 1024x768 | Grid adjusts (2 columns instead of 3) | ☐ Pass ☐ Fail |
| RESP-04 | Tablet portrait (768x1024) | 1. Set viewport to 768x1024 | Mobile warning appears | ☐ Pass ☐ Fail |
| RESP-05 | Mobile (375x667) | 1. Set viewport to 375x667 | Mobile warning appears:<br>"Desktop Required" message | ☐ Pass ☐ Fail |
| RESP-06 | Mobile warning content | 1. On mobile<br>2. Read warning | Shows minimum requirements:<br>- Screen width: 1280px<br>- Modern browser<br>- JavaScript enabled | ☐ Pass ☐ Fail |
| RESP-07 | Keyboard shortcuts hidden on mobile | 1. Set viewport to <768px<br>2. Observe bottom-right corner | Keyboard shortcuts hint hidden (md:block) | ☐ Pass ☐ Fail |

---

## Cross-Browser Tests

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|----------------|--------|
| BROWSER-01 | Chrome (latest) | 1. Open in Chrome | Dashboard fully functional | ☐ Pass ☐ Fail |
| BROWSER-02 | Firefox (latest) | 1. Open in Firefox | Dashboard fully functional | ☐ Pass ☐ Fail |
| BROWSER-03 | Safari (latest) | 1. Open in Safari | Dashboard fully functional | ☐ Pass ☐ Fail |
| BROWSER-04 | Edge (latest) | 1. Open in Edge | Dashboard fully functional | ☐ Pass ☐ Fail |
| BROWSER-05 | Chrome (1 version old) | 1. Open in Chrome (previous version) | Dashboard fully functional | ☐ Pass ☐ Fail |

---

## Summary Report Template

After completing all tests, fill out this summary:

### Test Execution Summary

**Test Date**: _____________
**Tester Name**: _____________
**Environment**: _____________

| Category | Total Tests | Passed | Failed | Pass Rate |
|----------|------------|--------|--------|-----------|
| Functional Tests | 48 | ___ | ___ | ___% |
| UI/Visual Tests | 10 | ___ | ___ | ___% |
| Interaction Tests | 13 | ___ | ___ | ___% |
| Error Handling Tests | 9 | ___ | ___ | ___% |
| Accessibility Tests | 14 | ___ | ___ | ___% |
| Performance Tests | 7 | ___ | ___ | ___% |
| Responsiveness Tests | 7 | ___ | ___ | ___% |
| Cross-Browser Tests | 5 | ___ | ___ | ___% |
| **TOTAL** | **113** | ___ | ___ | ___% |

### Critical Issues Found

| Issue ID | Severity | Description | Steps to Reproduce | Status |
|----------|----------|-------------|-------------------|--------|
| ISSUE-01 | High/Medium/Low | _description_ | _steps_ | Open/Fixed |

### Recommendations

_List any recommendations for improvements or fixes_

### Sign-off

**Tested by**: _____________
**Date**: _____________
**Status**: ☐ Approved for Production ☐ Requires Fixes

---

**Last Updated**: October 18, 2025
**Version**: 1.0.0
**Total Test Cases**: 113
