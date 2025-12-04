# Phase 2: Complete Frontend Implementation - Technical Decisions

**Phase:** 2 of 8
**Agent:** `*agent ux-expert`
**Date:** 2025-10-17
**Status:** Not Started

---

## Key Decisions Summary

1. Vite as build tool (fast HMR, optimized builds)
2. React 18 + TypeScript for type safety
3. Shadcn/ui + Tailwind CSS for component library
4. TanStack Table v8 for data tables
5. Recharts for data visualization
6. React Context for state management (avoid Zustand complexity for MVP)
7. Mock WebSocket with setTimeout/setInterval
8. Linear Dark Theme as design system
9. JSON fixtures for mock data (converted from Phase 1 CSVs)
10. Monorepo structure for future backend integration

---

## Decision Log

### Decision 1: Vite vs Create React App
**Date:** TBD
**Context:** Need fast development experience for React + TypeScript project

**Options Considered:**
1. **Create React App (CRA)**
   - Pros: Official React tooling, widely adopted
   - Cons: Slow build times, deprecated since React 18, webpack overhead

2. **Vite**
   - Pros: Lightning-fast HMR (<50ms), optimized builds, native ESM
   - Cons: Newer tooling, smaller ecosystem

**Decision:** Vite

**Rationale:** CRA is no longer maintained. Vite provides significantly faster development experience (10x faster HMR) and is recommended by React team for new projects.

**Implementation Notes:** Use `npm create vite@latest` with `react-ts` template

---

### Decision 2: Component Library Choice
**Date:** TBD
**Context:** Need pre-built, accessible UI components for dashboard

**Options Considered:**
1. **Material-UI (MUI)**
   - Pros: Mature, comprehensive, good docs
   - Cons: Heavy bundle size (300KB+), opinionated design, hard to customize

2. **Ant Design**
   - Pros: Enterprise-ready, rich components
   - Cons: Large bundle, Chinese design aesthetic, hard to theme

3. **Shadcn/ui + Tailwind CSS**
   - Pros: Copy-paste components (no dependency), full control, tiny bundle
   - Cons: Manual component setup, smaller ecosystem

**Decision:** Shadcn/ui + Tailwind CSS

**Rationale:** Frontend spec v3.3 specifically requires Linear Dark Theme, which is easiest to implement with Tailwind. Shadcn/ui provides accessible components without the bundle size penalty.

**Implementation Notes:** Use `npx shadcn-ui@latest init` with Linear Dark Theme colors

---

### Decision 3: State Management Approach
**Date:** TBD
**Context:** Need to manage forecast data, agent status, user interactions

**Options Considered:**
1. **Redux Toolkit**
   - Pros: Predictable, time-travel debugging, DevTools
   - Cons: Boilerplate, overkill for MVP, steep learning curve

2. **Zustand**
   - Pros: Simple API, small bundle (1KB), hooks-based
   - Cons: Less structure, no DevTools (without plugin)

3. **React Context + useReducer**
   - Pros: Built-in, no dependencies, sufficient for MVP
   - Cons: Less performant for large apps, manual optimization

**Decision:** React Context + useReducer

**Rationale:** MVP doesn't require complex state management. React Context is sufficient for sharing forecast data and agent status across components. Can migrate to Zustand in Phase 3 if needed.

**Implementation Notes:** Create separate contexts for ForecastContext, AgentContext, ParameterContext

---

### Decision 4: Data Table Library
**Date:** TBD
**Context:** Need powerful, sortable, filterable tables for clusters and replenishment

**Options Considered:**
1. **React Table (TanStack Table v8)**
   - Pros: Headless, full control over UI, powerful features
   - Cons: Requires more setup, no pre-styled components

2. **AG Grid**
   - Pros: Enterprise features, Excel-like, great performance
   - Cons: Heavy bundle, expensive license for commercial use, overkill for MVP

3. **MUI DataGrid**
   - Pros: Pre-styled, integrates with MUI
   - Cons: Locked into MUI ecosystem, limited customization

**Decision:** TanStack Table v8

**Rationale:** Headless design allows full control over Linear Dark Theme styling. Extremely powerful sorting/filtering/pagination without bundle bloat. Frontend spec v3.3 requires custom-styled tables.

**Implementation Notes:** Use with Shadcn/ui Table components for styling

---

### Decision 5: Charting Library
**Date:** TBD
**Context:** Need line chart for weekly forecast vs actuals (Section 4)

**Options Considered:**
1. **Recharts**
   - Pros: React-native, declarative API, good docs
   - Cons: Smaller feature set, slower with large datasets

2. **Chart.js + react-chartjs-2**
   - Pros: Mature, feature-rich, widely adopted
   - Cons: Imperative API, harder to customize in React

3. **D3.js**
   - Pros: Maximum flexibility, powerful
   - Cons: Steep learning curve, overkill for simple line chart

**Decision:** Recharts

**Rationale:** Declarative React API fits well with component architecture. Sufficient features for MVP (line charts, tooltips, annotations). Easy to customize for Linear Dark Theme.

**Implementation Notes:** Use ResponsiveContainer for responsive charts

---

### Decision 6: Mock WebSocket Strategy
**Date:** TBD
**Context:** Need to simulate agent status updates without backend

**Options Considered:**
1. **Real WebSocket server (Node.js)**
   - Pros: Realistic, tests full stack
   - Cons: Requires backend setup, overkill for Phase 2

2. **Mock with setTimeout/setInterval**
   - Pros: Simple, no backend, sufficient for UI testing
   - Cons: Not realistic, doesn't test real WebSocket logic

3. **Mock Service Worker (MSW)**
   - Pros: Intercepts network requests, realistic
   - Cons: Doesn't support WebSocket mocking well

**Decision:** Mock with setTimeout/setInterval

**Rationale:** Phase 2 focuses on frontend only. Real WebSocket integration happens in Phase 3. Simple mock sufficient for testing UI transitions and loading states.

**Implementation Notes:**
```typescript
// Simulate agent status updates
useEffect(() => {
  const interval = setInterval(() => {
    setAgentStatus(prev => getNextStatus(prev))
  }, 2000)
  return () => clearInterval(interval)
}, [])
```

---

### Decision 7: Mock Data Format
**Date:** TBD
**Context:** Phase 1 generated CSV files, need to use in frontend

**Options Considered:**
1. **Use CSV files directly**
   - Pros: No conversion needed
   - Cons: Requires CSV parser, slower, not idiomatic for web

2. **Convert to JSON fixtures**
   - Pros: Native JavaScript format, faster, easier to work with
   - Cons: Requires one-time conversion script

**Decision:** Convert to JSON fixtures

**Rationale:** JSON is the natural format for JavaScript/React. One-time conversion script is trivial. Easier to mock API responses with JSON.

**Implementation Notes:** Create `src/data/fixtures/` with converted data

---

### Decision 8: Folder Structure
**Date:** TBD
**Context:** Need organized, scalable folder structure for React project

**Options Considered:**
1. **Feature-based structure**
   - Pros: Co-locates related files, scales well
   - Cons: More complex, harder to find shared components

2. **Type-based structure (components, hooks, utils)**
   - Pros: Simple, clear separation, easy to find files
   - Cons: Doesn't scale as well, lots of cross-folder imports

**Decision:** Hybrid approach

**Rationale:** Use type-based for shared code, feature-based for sections

**Implementation Notes:**
```
src/
├── components/        # Shared UI components (MetricCard, AgentCard)
├── sections/          # Feature-specific components (Section0, Section1)
├── hooks/             # Custom hooks (useForecast, useMockWebSocket)
├── types/             # TypeScript types
├── utils/             # Helper functions
├── data/              # Mock data and fixtures
└── styles/            # Global styles and theme
```

---

### Decision 9: Linear Dark Theme Implementation
**Date:** TBD
**Context:** Frontend spec v3.3 requires specific Linear-inspired dark theme

**Options Considered:**
1. **Custom CSS variables**
   - Pros: Simple, lightweight
   - Cons: No design system, hard to maintain consistency

2. **Tailwind CSS with custom theme**
   - Pros: Utility-first, great DX, easy to customize
   - Cons: Larger bundle (with PurgeCSS mitigation)

**Decision:** Tailwind CSS with custom theme

**Rationale:** Tailwind provides utility classes that match Linear's design system. Easy to define custom colors, spacing, and typography. Works seamlessly with Shadcn/ui.

**Implementation Notes:** Configure in `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      background: 'hsl(240, 10%, 3.9%)',
      foreground: 'hsl(0, 0%, 98%)',
      primary: 'hsl(263, 70%, 50%)',
      // ... Linear Dark Theme colors
    }
  }
}
```

---

### Decision 10: TypeScript Strictness
**Date:** TBD
**Context:** Balance between type safety and development speed

**Options Considered:**
1. **Strict mode enabled**
   - Pros: Maximum type safety, catches bugs early
   - Cons: More upfront work, slower initial development

2. **Strict mode disabled**
   - Pros: Faster development, more flexible
   - Cons: Less type safety, more runtime errors

**Decision:** Strict mode enabled

**Rationale:** Type safety is critical for dashboard with complex data structures. Strict mode catches bugs at compile time. Worth the upfront investment.

**Implementation Notes:** `tsconfig.json` with `"strict": true`

---

### Decision 11: CSV Upload UI vs Mock Data Only
**Date:** 2025-10-17
**Context:** Planning spec Flow 1 describes CSV upload workflow, but Phase 2 focuses on UI development only

**Options Considered:**
1. **Build CSV Upload UI (Story PHASE2-015)**
   - Pros: Realistic data loading, tests CSV validation, allows custom data testing
   - Cons: 2 hours additional dev time, requires PapaParse library, complexity without backend

2. **Mock Data Only (Deferred)**
   - Pros: Faster Phase 2 completion, JSON fixtures sufficient for UI testing, reduces scope
   - Cons: No CSV upload testing, manual JSON editing for data changes

3. **Hybrid Approach**
   - Pros: "Use Sample Data" button for mock data, optional CSV upload for advanced users
   - Cons: Most complex, adds conditional logic

**Decision:** **Mock Data Only for Phase 2 MVP** (Option 2)

**Rationale:**
- Phase 1 CSV data already converted to JSON fixtures (`src/data/fixtures/`)
- UI components can be fully tested with mock data
- CSV upload is a backend integration concern (Phase 3)
- Planning spec Flow 1 Steps 2-7 (CSV upload) deferred to Phase 3
- Section 0 (Parameter Gathering) becomes true entry point for MVP
- Saves 2 hours development time without impacting UI quality

**Implementation Notes:**
- Use JSON fixtures from Phase 1 for all testing scenarios
- Create `src/data/fixtures/` with 3 data sets:
  1. `historical_sales.json` (54,750 rows)
  2. `store_attributes.json` (50 stores)
  3. `weekly_actuals.json` (12 weeks × 50 stores)
- Section 0 (Parameter Gathering) is the workflow entry point
- No "Upload CSV" buttons in Phase 2 UI

**Gap Documentation:**
- **Gap 2 (CSV Upload):** Planning spec lines 274-283 describe CSV upload. Deferred to Phase 3.
- **Gap 3 (Weekly Actuals Upload):** Planning spec lines 319-364 describe weekly actuals upload modal. Handled via time-based mock simulation.

**Weekly Actuals Strategy for Phase 2:**
Instead of upload modal, use time-based mock data advancement:
```typescript
// Simulate week progression for testing
const advanceWeek = () => {
  const currentWeek = getCurrentWeek() // 1-12
  const nextWeek = currentWeek + 1
  if (nextWeek <= 12) {
    loadActualsFromFixtures(nextWeek) // Load from weekly_actuals.json
    calculateVariance(nextWeek)
  }
}
```

**Story PHASE2-015 Status:** Created as optional reference, marked as "Deferred to Phase 3"

**For Phase 3 Backend Integration:**
- Implement POST /api/data/upload-historical-sales
- Implement POST /api/data/upload-weekly-sales
- Build CSV upload UI from Story PHASE2-015
- Connect to backend endpoints

---

## Performance Considerations

### Bundle Size Optimization
- Use dynamic imports for large sections (`React.lazy`)
- Tree-shaking with Vite (automatic)
- PurgeCSS for Tailwind (removes unused utilities)
- Target: <500KB initial bundle, <2s load time on 3G

### Rendering Performance
- Memoize expensive computations with `useMemo`
- Prevent unnecessary re-renders with `React.memo`
- Virtualize long lists in TanStack Table (>100 rows)
- Debounce search/filter inputs (300ms delay)

### Accessibility (WCAG 2.1 AA)
- All interactive elements keyboard accessible
- Proper ARIA labels for screen readers
- Color contrast ratios >4.5:1 for text
- Focus indicators visible and clear

---

## Key Metrics (TBD after implementation)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Bundle Size (Initial) | <500KB | TBD | TBD |
| Time to Interactive | <2s (3G) | TBD | TBD |
| Lighthouse Score | >90 | TBD | TBD |
| WCAG Compliance | AA | TBD | TBD |
| Component Count | ~30 | TBD | TBD |
| Lines of Code | <5,000 | TBD | TBD |

---

## Future Enhancements

### Enhancement 1: Real-time Collaboration
**Description:** Multiple users can view the same forecast simultaneously
**Benefit:** Better for team decision-making
**Effort:** Medium (requires WebSocket server in Phase 3)
**Priority:** Low (nice-to-have for v2.0)

### Enhancement 2: Storybook Integration
**Description:** Component documentation with visual examples
**Benefit:** Easier component discovery and testing
**Effort:** Low (add Storybook, write stories)
**Priority:** Medium (helpful for Phase 3 backend integration)

### Enhancement 3: Dark/Light Mode Toggle
**Description:** Allow users to switch between dark and light themes
**Benefit:** Accessibility for light-sensitive users
**Effort:** Medium (requires full light theme design)
**Priority:** Low (MVP focuses on dark theme only)

---

## Key Takeaways (to be filled after implementation)

### What Worked Well
- TBD

### Lessons Learned
- TBD

### For Next Phase (Phase 3: Backend Architecture)
- TBD

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Phase 2 Not Started
