# Phase 2: Complete Frontend Implementation - Checklist

**Phase:** 2 of 8
**Agent:** `*agent ux-expert`
**Status:** Not Started
**Progress:** 0/14 tasks complete (Task 15 deferred to Phase 3)

---

## Task Checklist

### Task 1: Project Setup & Configuration
**Story:** [PHASE2-001](stories/PHASE2-001-project-setup.md)
**Estimate:** 2 hours
**Dependencies:** None

- [ ] Initialize Vite + React + TypeScript project
- [ ] Install core dependencies: `@tanstack/react-table@^8.20.0`, `recharts@^2.12.0`, `react-router-dom@^6.27.0`, `lucide-react@latest`
- [ ] Install Shadcn/ui and Tailwind CSS
- [ ] Configure ESLint + Prettier
- [ ] Set up Linear Dark Theme (colors, typography, spacing)
- [ ] Create basic folder structure (components, hooks, utils, types)
- [ ] Configure path aliases (@/ for src/)

**Status:** Not Started

### Task 2: Mock Data & State Management
**Story:** [PHASE2-002](stories/PHASE2-002-mock-data-state-management.md)
**Estimate:** 3 hours
**Dependencies:** Task 1

- [ ] Install state management: `@tanstack/react-query@^5.59.0`
- [ ] Convert Phase 1 CSV data to JSON fixtures
- [ ] Create TypeScript types for all data structures
- [ ] Implement mock WebSocket client using setTimeout/setInterval (no external library)
- [ ] Set up state management (React Context for global state)
- [ ] Create custom hooks for data fetching (useForecast, useClusters, etc.)
- [ ] Implement mock API delay simulation

**Status:** Not Started

### Task 3: Section 0 - Parameter Gathering
**Story:** [PHASE2-003](stories/PHASE2-003-section-0-parameter-gathering.md)
**Estimate:** 4 hours
**Dependencies:** Task 1, Task 2
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

**Status:** Not Started

### Task 4: Section 1 - Fixed Header & Agent Cards
**Story:** [PHASE2-004](stories/PHASE2-004-section-1-header-agent-cards.md)
**Estimate:** 3 hours
**Dependencies:** Task 2

- [ ] Create FixedHeader component (scenario name, date range, progress)
- [ ] Build AgentCard component (icon, name, status, progress)
- [ ] Implement WebSocket mock for agent status updates
- [ ] Add animated status transitions (Idle → Thinking → Complete)
- [ ] Create agent icon components (Demand, Inventory, Pricing)
- [ ] Add progress bar with step indicators

**Status:** Not Started

### Task 5: Section 2 - Forecast Summary
**Story:** [PHASE2-005](stories/PHASE2-005-section-2-forecast-summary.md)
**Estimate:** 2 hours
**Dependencies:** Task 2
- [ ] Create MetricCard component (title, value, delta, trend)
- [ ] Build responsive grid layout (2x2 on desktop, 1 column on mobile)
- [ ] Implement delta calculation and formatting (+12.5%)
- [ ] Add trend icons (up/down arrows)
- [ ] Style with Linear Dark Theme colors

**Status:** Not Started

### Task 6: Section 3 - Cluster Cards with TanStack Table
**Story:** [PHASE2-006](stories/PHASE2-006-section-3-cluster-cards.md)
**Estimate:** 6 hours
**Dependencies:** Task 2

- [ ] Create ClusterCard component (header, metrics, table)
- [ ] Integrate TanStack Table v8 with sorting/filtering
- [ ] Implement column definitions (Store, Forecast, Confidence, etc.)
- [ ] Add expandable row details for store-level data
- [ ] Create custom cell renderers (confidence bars, status badges)
- [ ] Add pagination for large clusters (>20 stores)

**Status:** Not Started

### Task 7: Section 4 - Weekly Performance Chart
**Story:** [PHASE2-007](stories/PHASE2-007-section-4-weekly-chart.md)
**Estimate:** 4 hours
**Dependencies:** Task 2

- [ ] Create WeeklyChart component with Recharts
- [ ] Implement line chart with 2 series (Forecast vs Actuals)
- [ ] Add Week 5 variance annotation (>20% threshold)
- [ ] Create custom tooltip with detailed breakdown
- [ ] Implement re-forecast trigger UI (appears when variance >20%)
- [ ] Add responsive chart sizing

**Status:** Not Started

### Task 8: Section 5 - Replenishment Queue
**Story:** [PHASE2-008](stories/PHASE2-008-section-5-replenishment-queue.md)
**Estimate:** 3 hours
**Dependencies:** Task 2, Task 6

- [ ] Create ReplenishmentTable component
- [ ] Implement column definitions (Store, SKU, Quantity, Urgency, Status)
- [ ] Add sorting by urgency (High/Medium/Low)
- [ ] Create status badges (Pending, In Progress, Complete)
- [ ] Add action buttons (Approve, Reject)
- [ ] Implement search/filter functionality

**Status:** Not Started

### Task 9: Section 6 - Markdown Decision
**Story:** [PHASE2-009](stories/PHASE2-009-section-6-markdown-decision.md)
**Estimate:** 2 hours
**Dependencies:** Task 2

- [ ] Create MarkdownDecisionCard component
- [ ] Implement recommended markdown % display
- [ ] Add manual override input with validation (0-50%)
- [ ] Create confidence level indicator (color-coded)
- [ ] Add Apply/Reject buttons with confirmation dialog
- [ ] Show impact preview (revenue loss vs excess stock reduction)

**Status:** Not Started

### Task 10: Section 7 - Performance Metrics
**Story:** [PHASE2-010](stories/PHASE2-010-section-7-performance-metrics.md)
**Estimate:** 2 hours
**Dependencies:** Task 2

- [ ] Create MetricsGrid component
- [ ] Display MAPE, Bias, and accuracy metrics
- [ ] Add historical performance comparison chart (last 4 quarters)
- [ ] Show agent contribution breakdown (Demand 40%, Inventory 35%, Pricing 25%)
- [ ] Implement sparklines for trend visualization

**Status:** Not Started

### Task 11: Navigation & Layout
**Story:** [PHASE2-011](stories/PHASE2-011-navigation-layout.md)
**Estimate:** 2 hours
**Dependencies:** Task 3-10

- [ ] Create AppLayout component with sidebar navigation
- [ ] Implement scroll-to-section functionality
- [ ] Add sticky section headers
- [ ] Create breadcrumb navigation
- [ ] Implement keyboard shortcuts (optional)

**Status:** Not Started

### Task 12: Error Handling & Polish
**Story:** [PHASE2-012](stories/PHASE2-012-error-handling-polish.md)
**Estimate:** 3 hours
**Dependencies:** Task 3-11

- [ ] Implement error boundaries for all sections
- [ ] Add loading skeletons for data fetching
- [ ] Create toast notification system (success, error, warning)
- [ ] Add form validation and error messages
- [ ] Implement accessibility features (ARIA labels, keyboard nav, focus management)
- [ ] Run accessibility audit using axe DevTools or similar (WCAG 2.1 AA compliance)
- [ ] Test responsive design (mobile, tablet, desktop)

**Status:** Not Started

### Task 13: Documentation & Testing
**Story:** [PHASE2-013](stories/PHASE2-013-documentation-testing.md)
**Estimate:** 2 hours
**Dependencies:** Task 12

- [ ] Write component documentation (JSDoc comments)
- [ ] Create development guide (README.md)
- [ ] Document Linear Dark Theme usage
- [ ] Add setup instructions (dependencies, env variables)
- [ ] Create user flow documentation with screenshots
- [ ] Manual testing checklist for all 5 user flows

**Status:** Not Started

### Task 14: Performance Report Page (/reports/spring-2025)
**Story:** [PHASE2-014](stories/PHASE2-014-performance-report-page.md)
**Estimate:** 3 hours
**Dependencies:** Task 2, Task 11

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

**Status:** Not Started

### Task 15: CSV Upload UI (Optional - Deferred to Phase 3)
**Story:** [PHASE2-015](stories/PHASE2-015-csv-upload-ui.md)
**Estimate:** 2 hours
**Dependencies:** Task 1, Task 2
**Status:** Deferred (Mock Data Only for Phase 2)

- [ ] ~~Build CSV upload buttons (Historical Sales + Store Attributes)~~
- [ ] ~~Implement CSV parser (PapaParse)~~
- [ ] ~~Create CSV preview modal~~
- [ ] ~~Build category selector (auto-populated)~~
- [ ] ~~Build season date picker~~
- [ ] ~~Build "Run Forecast" button~~
- [ ] ~~Error handling and validation~~

**Note:** CSV upload UI deferred to Phase 3. Phase 2 uses JSON fixtures only. See Decision 11 in `technical_decisions.md`.

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (40% complete)
- [ ] Project builds without errors
- [ ] Linear Dark Theme applied consistently
- [ ] Sections 0-3 functional with mock data
- [ ] Responsive design works on mobile/tablet/desktop
**Status:** Not Started

### Checkpoint 2: Pre-Completion (80% complete)
- [ ] All 8 sections rendered with mock data
- [ ] WebSocket mock shows agent status updates
- [ ] TanStack Tables support sorting/filtering
- [ ] Recharts displays variance correctly
- [ ] Navigation and layout complete
**Status:** Not Started

### Checkpoint 3: Final
- [ ] All 5 user flows tested manually
- [ ] Performance report page accessible via Section 7 link
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] Error handling works (network errors, invalid data)
- [ ] Documentation complete
- [ ] Ready for handoff to Phase 3 (Backend Architecture)
**Status:** Not Started

---

## Notes

- Update this checklist in real-time as tasks complete
- Mark subtasks with [x] when done
- Update task status: Not Started → In Progress → Complete
- Do not mark task complete until ALL subtasks are done
- This builds the COMPLETE frontend (not just mockups)
- Focus on production-ready quality (animations, loading states, errors)

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17 (Added Task 15 - Deferred)
**Progress:** 0/14 tasks (0%) | Task 15 deferred to Phase 3
