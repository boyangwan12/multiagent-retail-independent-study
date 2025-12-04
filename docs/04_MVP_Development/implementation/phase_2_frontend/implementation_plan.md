# Phase 2: Complete Frontend Implementation - Implementation Plan

**Phase:** 2 of 8
**Goal:** Build fully functional React dashboard with all 8 sections (no backend integration yet)
**Agent:** `*agent ux-expert`
**Duration Estimate:** 5-7 days
**Actual Duration:** TBD
**Status:** Not Started

---

## Requirements Source

- **Primary:** `planning/5_front-end-spec_v3.3.md` - Complete frontend specification
- **Secondary:** `planning/3_technical_architecture_v3.3.md` - Architecture context
- **Reference:** `planning/1_product_brief_v3.3.md` - Product context

---

## Key Deliverables

1. **Vite + React + TypeScript Project**
   - Complete project structure with routing
   - ESLint + Prettier configuration
   - Shadcn/ui component library integrated
   - Linear Dark Theme configured

2. **Section 0: Parameter Gathering**
   - Natural language input textarea
   - Parameter cards with extracted values
   - Edit/confirm workflow
   - Mock LLM extraction logic

3. **Section 1: Fixed Header & Agent Cards**
   - Fixed header with scenario name and forecast range
   - 3 agent cards (Demand, Inventory, Pricing)
   - WebSocket mock for agent status updates
   - Animated status transitions

4. **Section 2: Forecast Summary**
   - 4 metric cards (Total Units, Revenue, Markdowns, Excess Stock)
   - Comparison with baseline scenario
   - Responsive grid layout

5. **Section 3: Cluster Cards with TanStack Table**
   - 3 cluster cards (Fashion Forward, Mainstream, Value Conscious)
   - TanStack Table v8 with sorting/filtering
   - Expandable details view
   - Store-level data tables

6. **Section 4: Weekly Performance Chart**
   - Recharts line chart (Forecast vs Actuals)
   - Week 5 variance annotation
   - Re-forecast trigger UI
   - Interactive tooltips

7. **Section 5: Replenishment Queue**
   - TanStack Table for replenishment recommendations
   - Sorting by urgency/quantity
   - Status indicators (Pending, In Progress, Complete)

8. **Section 6: Markdown Decision**
   - Decision card with recommended markdown %
   - Manual override input
   - Confidence level indicator
   - Apply/reject buttons

9. **Section 7: Performance Metrics**
   - MAPE, Bias, and accuracy metrics
   - Historical performance comparison
   - Agent contribution breakdown

10. **Mock Data Integration**
    - Convert Phase 1 CSV data to JSON fixtures
    - Mock WebSocket client for agent updates
    - Mock API response handlers
    - State management (React Context or Zustand)

11. **Error Handling & Polish**
    - Loading states for all sections
    - Error boundaries
    - Toast notifications
    - Accessibility (WCAG 2.1 AA)

12. **Performance Report Page (/reports/spring-2025)**
    - Executive summary section
    - MAPE by Week/Cluster analysis
    - Variance timeline
    - Business impact metrics
    - Read-only display (no editing)

13. **Documentation**
    - Component documentation
    - Storybook stories (optional)
    - Development guide (README)

---

## Task Breakdown

### Task 1: Project Setup & Configuration
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** None
**Status:** Not Started

**Subtasks:**
- [ ] Initialize Vite + React + TypeScript project
- [ ] Install core dependencies: `@tanstack/react-table@^8.20.0`, `recharts@^2.12.0`, `react-router-dom@^6.27.0`, `lucide-react@latest`
- [ ] Install Shadcn/ui and Tailwind CSS
- [ ] Configure ESLint + Prettier
- [ ] Set up Linear Dark Theme (colors, typography, spacing)
- [ ] Create basic folder structure (components, hooks, utils, types)
- [ ] Configure path aliases (@/ for src/)

### Task 2: Mock Data & State Management
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 1
**Status:** Not Started

**Subtasks:**
- [ ] Install state management: `@tanstack/react-query@^5.59.0`
- [ ] Convert Phase 1 CSV data to JSON fixtures
- [ ] Create TypeScript types for all data structures
- [ ] Implement mock WebSocket client using setTimeout/setInterval (no external library)
- [ ] Set up state management (React Context for global state)
- [ ] Create custom hooks for data fetching (useForecast, useClusters, etc.)
- [ ] Implement mock API delay simulation

### Task 3: Section 0 - Parameter Gathering
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 1, Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Create ParameterGathering component with textarea input (500 char limit + character counter)
- [ ] Add "Extract Parameters" button with loading indicator (2-5 seconds)
- [ ] Implement mock LLM extraction logic (regex-based parsing for 5 parameters)
- [ ] Build Parameter Confirmation Modal with 5 parameter display
- [ ] Add expandable "Extraction Reasoning" section to modal
- [ ] Create confirmed parameters read-only banner (collapsed state)
- [ ] Build Agent Reasoning Preview section (shows how agents adapt)
- [ ] Implement "Edit Parameters" workflow (returns to textarea)
- [ ] Add error handling for incomplete extractions
- [ ] Add network error handling with retry logic

### Task 4: Section 1 - Fixed Header & Agent Cards
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Create FixedHeader component (scenario name, date range, progress)
- [ ] Build AgentCard component (icon, name, status, progress)
- [ ] Implement WebSocket mock for agent status updates
- [ ] Add animated status transitions (Idle → Thinking → Complete)
- [ ] Create agent icon components (Demand, Inventory, Pricing)
- [ ] Add progress bar with step indicators

### Task 5: Section 2 - Forecast Summary
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Create MetricCard component (title, value, delta, trend)
- [ ] Build responsive grid layout (2x2 on desktop, 1 column on mobile)
- [ ] Implement delta calculation and formatting (+12.5%)
- [ ] Add trend icons (up/down arrows)
- [ ] Style with Linear Dark Theme colors

### Task 6: Section 3 - Cluster Cards with TanStack Table
**Estimate:** 6 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Create ClusterCard component (header, metrics, table)
- [ ] Integrate TanStack Table v8 with sorting/filtering
- [ ] Implement column definitions (Store, Forecast, Confidence, etc.)
- [ ] Add expandable row details for store-level data
- [ ] Create custom cell renderers (confidence bars, status badges)
- [ ] Add pagination for large clusters (>20 stores)

### Task 7: Section 4 - Weekly Performance Chart
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Create WeeklyChart component with Recharts
- [ ] Implement line chart with 2 series (Forecast vs Actuals)
- [ ] Add Week 5 variance annotation (>20% threshold)
- [ ] Create custom tooltip with detailed breakdown
- [ ] Implement re-forecast trigger UI (appears when variance >20%)
- [ ] Add responsive chart sizing

### Task 8: Section 5 - Replenishment Queue
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 2, Task 6 (TanStack Table setup)
**Status:** Not Started

**Subtasks:**
- [ ] Create ReplenishmentTable component
- [ ] Implement column definitions (Store, SKU, Quantity, Urgency, Status)
- [ ] Add sorting by urgency (High/Medium/Low)
- [ ] Create status badges (Pending, In Progress, Complete)
- [ ] Add action buttons (Approve, Reject)
- [ ] Implement search/filter functionality

### Task 9: Section 6 - Markdown Decision
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Create MarkdownDecisionCard component
- [ ] Implement recommended markdown % display
- [ ] Add manual override input with validation (0-50%)
- [ ] Create confidence level indicator (color-coded)
- [ ] Add Apply/Reject buttons with confirmation dialog
- [ ] Show impact preview (revenue loss vs excess stock reduction)

### Task 10: Section 7 - Performance Metrics
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Create MetricsGrid component
- [ ] Display MAPE, Bias, and accuracy metrics
- [ ] Add historical performance comparison chart (last 4 quarters)
- [ ] Show agent contribution breakdown (Demand 40%, Inventory 35%, Pricing 25%)
- [ ] Implement sparklines for trend visualization

### Task 11: Navigation & Layout
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 3-10
**Status:** Not Started

**Subtasks:**
- [ ] Create AppLayout component with sidebar navigation
- [ ] Implement scroll-to-section functionality
- [ ] Add sticky section headers
- [ ] Create breadcrumb navigation
- [ ] Implement keyboard shortcuts (optional)

### Task 12: Error Handling & Polish
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 3-11
**Status:** Not Started

**Subtasks:**
- [ ] Implement error boundaries for all sections
- [ ] Add loading skeletons for data fetching
- [ ] Create toast notification system (success, error, warning)
- [ ] Add form validation and error messages
- [ ] Implement accessibility features (ARIA labels, keyboard nav, focus management)
- [ ] Run accessibility audit using axe DevTools or similar (WCAG 2.1 AA compliance)
- [ ] Test responsive design (mobile, tablet, desktop)

### Task 13: Documentation & Testing
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 12
**Status:** Not Started

**Subtasks:**
- [ ] Write component documentation (JSDoc comments)
- [ ] Create development guide (README.md)
- [ ] Document Linear Dark Theme usage
- [ ] Add setup instructions (dependencies, env variables)
- [ ] Create user flow documentation with screenshots
- [ ] Manual testing checklist for all 5 user flows

### Task 14: Performance Report Page (/reports/spring-2025)
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 2, Task 11 (React Router setup)
**Status:** Not Started

**Subtasks:**
- [ ] Create ReportPage component with React Router route
- [ ] Build Executive Summary section (read-only)
- [ ] Add MAPE by Week chart (Recharts line chart)
- [ ] Create MAPE by Cluster table (TanStack Table)
- [ ] Build Variance & Re-forecast Events Timeline
- [ ] Add Stockout/Overstock analysis section
- [ ] Create Markdown impact metrics display
- [ ] Add System performance metrics (runtimes, approval rates)
- [ ] Build Parameter Recommendations section (display only, no editing)
- [ ] Implement "← Back to Dashboard" navigation button
- [ ] Style with Linear Dark Theme consistency

### Task 15: CSV Upload UI (Optional - Deferred to Phase 3)
**Estimate:** 2 hours (deferred)
**Actual:** Deferred
**Dependencies:** Task 1, Task 2
**Status:** Deferred to Phase 3

**Rationale:** Mock data from Phase 1 JSON fixtures is sufficient for Phase 2 UI development. CSV upload is a backend integration concern better suited for Phase 3. See Decision 11 in `technical_decisions.md`.

**Subtasks (Deferred):**
- [ ] Build CSV upload buttons (Historical Sales + Store Attributes)
- [ ] Implement CSV parser (PapaParse library)
- [ ] Create CSV preview modal
- [ ] Build category selector (auto-populated from CSV)
- [ ] Build season date picker
- [ ] Build "Run Forecast" button with validation
- [ ] Error handling and CSV validation

**Story Reference:** See `stories/PHASE2-015-csv-upload-ui.md` for complete specification if implementing in Phase 3.

---

## Total Estimates vs Actuals

- **Total Tasks:** 14 (required) + 1 (deferred to Phase 3)
- **Estimated Time:** 41 hours for required tasks (5-7 days at 6-8h/day)
- **Task 15 (Deferred):** 2 hours (saved by deferring to Phase 3)
- **Actual Time:** TBD
- **Variance:** TBD

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (40% complete)
**After:** Task 6 complete
**Verify:**
- [ ] Project builds without errors
- [ ] Linear Dark Theme applied consistently
- [ ] Sections 0-3 functional with mock data
- [ ] Responsive design works on mobile/tablet/desktop

### Checkpoint 2: Pre-Completion (80% complete)
**After:** Task 11 complete
**Verify:**
- [ ] All 8 sections rendered with mock data
- [ ] WebSocket mock shows agent status updates
- [ ] TanStack Tables support sorting/filtering
- [ ] Recharts displays variance correctly
- [ ] Navigation and layout complete

### Checkpoint 3: Final
**After:** Task 14 complete
**Verify:**
- [ ] All 5 user flows tested manually
- [ ] Performance report page accessible via Section 7 link
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] Error handling works (network errors, invalid data)
- [ ] Documentation complete
- [ ] Ready for handoff to Phase 3 (Backend Architecture)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shadcn/ui component customization too complex | Medium | Medium | Use headless UI components, custom styling with Tailwind |
| TanStack Table v8 learning curve | Medium | Medium | Follow official docs, reference examples, simplify columns if needed |
| Recharts performance with large datasets | Low | Medium | Implement data sampling for >1000 points, use lazy loading |
| Mock WebSocket logic too simplistic | Low | Low | Document limitations, plan for real WebSocket in Phase 3 |
| Linear Dark Theme colors not accessible | Low | High | Use WCAG contrast checker, test with screen readers |

---

## Notes

- This phase builds the **complete frontend** (not just mockups)
- No backend integration yet - all data is mocked via JSON fixtures
- WebSocket is simulated with setTimeout/setInterval
- Focus on component reusability for Phase 3 integration
- Linear Dark Theme uses specific color palette (see frontend spec v3.3 and PHASE2-001)
- All interactions should feel production-ready (animations, loading states, errors)
- **CSV Upload UI (Task 15) deferred to Phase 3** - Mock data only for Phase 2 MVP
- Section 0 (Parameter Gathering) is the workflow entry point (no CSV upload buttons)
- Weekly actuals handled via time-based mock simulation (see Decision 11 in technical_decisions.md)

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17 (Added Task 15 - Deferred, Updated Linear Dark Theme)
**Status:** Not Started
