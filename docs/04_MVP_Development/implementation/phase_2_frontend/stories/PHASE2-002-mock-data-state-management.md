# Story: Mock Data & State Management Setup

**Epic:** Phase 2 - Complete Frontend Implementation
**Story ID:** PHASE2-002
**Status:** Draft
**Estimate:** 3 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE2-001 (Project Setup)

---

## Story

As a frontend developer,
I want to set up mock data and state management infrastructure,
So that I can build and test all UI components with realistic data without requiring a backend API.

**Business Value:** Enables parallel frontend development while backend is being built in Phase 3. Mock data simulates real-world scenarios (50 stores, 12 weeks of forecasts, 3 clusters) allowing comprehensive UI testing and user flow validation.

**Epic Context:** This is Task 2 of 14 in Phase 2. It creates the data foundation that all subsequent sections (0-7) depend on. The mock WebSocket client simulates real-time agent updates, and React Query provides the state management infrastructure for data fetching.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ TanStack React Query v5.59.0 installed and configured
2. ✅ Phase 1 CSV data converted to JSON fixtures
3. ✅ TypeScript types defined for all data structures
4. ✅ Mock WebSocket client implemented (no external library, uses setTimeout/setInterval)
5. ✅ React Context setup for global state management
6. ✅ Custom hooks created: `useForecast`, `useClusters`, `useStores`, `useAgentStatus`
7. ✅ Mock API delay simulation (500-2000ms)
8. ✅ Mock data includes:
   - 50 stores with attributes
   - 12-week forecast curves
   - 3 store clusters (Fashion_Forward, Mainstream, Value_Conscious)
   - Agent status transitions (Idle → Thinking → Complete)

### Quality Requirements

9. ✅ All TypeScript types compile without errors
10. ✅ Mock data validates against planning spec data models
11. ✅ Custom hooks follow React best practices
12. ✅ Mock WebSocket emits events correctly
13. ✅ No console errors when running dev server

---

## Tasks

### Task 1: Install TanStack React Query
- [ ] Install: `npm install @tanstack/react-query@^5.59.0`
- [ ] Install DevTools: `npm install @tanstack/react-query-devtools`
- [ ] Create `src/lib/react-query.ts`:
```typescript
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
})
```
- [ ] Wrap App with QueryClientProvider in `src/main.tsx`
- [ ] Add React Query DevTools (development only)

**Reference:** https://tanstack.com/query/latest/docs/framework/react/installation

### Task 2: Convert Phase 1 CSV to JSON Fixtures
- [ ] Read `data/phase_1_data_generation/output/store_attributes.csv`
- [ ] Convert to `src/mocks/stores.json`:
```json
[
  {
    "store_id": "Store_01",
    "store_name": "NYC Flagship",
    "cluster_id": "fashion_forward",
    "store_size_sqft": 15000,
    "location_tier": "A",
    "median_income": 95000,
    "store_format": "MALL",
    "region": "NORTHEAST",
    "avg_weekly_sales_12mo": 12500.0
  },
  ...
]
```
- [ ] Read `data/phase_1_data_generation/output/historical_sales_2022_2024.csv`
- [ ] Create aggregated forecast data in `src/mocks/forecast.json`
- [ ] Create `src/mocks/clusters.json` with 3 cluster definitions
- [ ] Verify JSON files are valid (no syntax errors)

**Note:** If Phase 1 CSV files don't exist yet, create mock data based on planning spec examples.

### Task 3: Define TypeScript Types
- [ ] Create `src/types/store.ts`:
```typescript
export interface Store {
  store_id: string
  store_name: string
  cluster_id: string
  store_size_sqft: number
  location_tier: 'A' | 'B' | 'C'
  median_income: number
  store_format: 'MALL' | 'STANDALONE' | 'SHOPPING_CENTER' | 'OUTLET'
  region: 'NORTHEAST' | 'SOUTHEAST' | 'MIDWEST' | 'WEST'
  avg_weekly_sales_12mo: number
}

export interface StoreCluster {
  cluster_id: string
  cluster_name: string
  fashion_tier: 'PREMIUM' | 'MAINSTREAM' | 'VALUE'
  store_count: number
  total_units: number
  allocation_percentage: number
}
```

- [ ] Create `src/types/forecast.ts`:
```typescript
export interface WeeklyDemand {
  week_number: number
  demand_units: number
  forecasted_units?: number
  actual_units?: number
  variance_pct?: number
}

export interface ForecastResult {
  forecast_id: string
  category_id: string
  season: string
  total_season_demand: number
  weekly_demand_curve: WeeklyDemand[]
  peak_week: number
  forecasting_method: 'ensemble_prophet_arima'
  prophet_forecast: number
  arima_forecast: number
  cluster_distribution: StoreCluster[]
}
```

- [ ] Create `src/types/agent.ts`:
```typescript
export type AgentStatus = 'idle' | 'thinking' | 'complete' | 'error'

export interface AgentState {
  agent_name: 'Demand Agent' | 'Inventory Agent' | 'Pricing Agent'
  status: AgentStatus
  progress_pct: number
  message: string
  timestamp: string
}
```

- [ ] Create `src/types/parameters.ts`:
```typescript
export type ReplenishmentStrategy = 'none' | 'weekly' | 'bi-weekly'

export interface SeasonParameters {
  forecast_horizon_weeks: number
  season_start_date: string
  season_end_date: string
  replenishment_strategy: ReplenishmentStrategy
  dc_holdback_percentage: number
  markdown_checkpoint_week?: number
  markdown_threshold?: number
  extraction_confidence: 'high' | 'medium' | 'low'
  extraction_reasoning: string
}
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 284-337 (SeasonParameters)

### Task 4: Implement Mock WebSocket Client
- [ ] Create `src/lib/mock-websocket.ts`:
```typescript
type MessageHandler = (data: AgentState) => void

export class MockWebSocket {
  private handlers: Set<MessageHandler> = new Set()
  private intervalId: NodeJS.Timeout | null = null

  connect() {
    // Simulate agent progression: Demand → Inventory → Pricing
    let step = 0
    const steps = [
      { agent: 'Demand Agent', status: 'thinking', progress: 33, message: 'Running Prophet forecasting...' },
      { agent: 'Demand Agent', status: 'complete', progress: 100, message: 'Forecast complete' },
      { agent: 'Inventory Agent', status: 'thinking', progress: 66, message: 'Calculating allocations...' },
      { agent: 'Inventory Agent', status: 'complete', progress: 100, message: 'Allocations complete' },
      { agent: 'Pricing Agent', status: 'thinking', progress: 90, message: 'Analyzing markdown strategy...' },
      { agent: 'Pricing Agent', status: 'complete', progress: 100, message: 'Workflow complete' },
    ]

    this.intervalId = setInterval(() => {
      if (step < steps.length) {
        const data = {
          ...steps[step],
          timestamp: new Date().toISOString(),
        }
        this.broadcast(data)
        step++
      } else {
        this.disconnect()
      }
    }, 2000) // 2 seconds between updates
  }

  onMessage(handler: MessageHandler) {
    this.handlers.add(handler)
  }

  private broadcast(data: AgentState) {
    this.handlers.forEach(handler => handler(data))
  }

  disconnect() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }
}
```

- [ ] Add simulated network delay function
- [ ] Test WebSocket emits all 6 agent states correctly

### Task 5: Create React Context for Global State
- [ ] Create `src/contexts/ParametersContext.tsx`:
```typescript
import { createContext, useContext, useState } from 'react'
import { SeasonParameters } from '@/types/parameters'

interface ParametersContextType {
  parameters: SeasonParameters | null
  setParameters: (params: SeasonParameters) => void
  clearParameters: () => void
}

const ParametersContext = createContext<ParametersContextType | undefined>(undefined)

export function ParametersProvider({ children }: { children: React.ReactNode }) {
  const [parameters, setParameters] = useState<SeasonParameters | null>(null)

  return (
    <ParametersContext.Provider
      value={{
        parameters,
        setParameters,
        clearParameters: () => setParameters(null),
      }}
    >
      {children}
    </ParametersContext.Provider>
  )
}

export function useParameters() {
  const context = useContext(ParametersContext)
  if (!context) {
    throw new Error('useParameters must be used within ParametersProvider')
  }
  return context
}
```

- [ ] Create similar context for workflow state
- [ ] Wrap App with providers in `src/main.tsx`

### Task 6: Create Custom Hooks for Data Fetching
- [ ] Create `src/hooks/useForecast.ts`:
```typescript
import { useQuery } from '@tanstack/react-query'
import forecastData from '@/mocks/forecast.json'

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export function useForecast(forecastId?: string) {
  return useQuery({
    queryKey: ['forecast', forecastId],
    queryFn: async () => {
      await delay(Math.random() * 1500 + 500) // 500-2000ms
      return forecastData
    },
    enabled: !!forecastId,
  })
}
```

- [ ] Create `src/hooks/useClusters.ts` (fetch cluster data)
- [ ] Create `src/hooks/useStores.ts` (fetch store data)
- [ ] Create `src/hooks/useAgentStatus.ts` (subscribe to WebSocket)
- [ ] Test all hooks return data correctly

### Task 7: Implement Mock API Delay Simulation
- [ ] Create `src/lib/mock-api.ts`:
```typescript
export const mockDelay = () =>
  new Promise(resolve =>
    setTimeout(resolve, Math.random() * 1500 + 500)
  )

export async function mockFetch<T>(data: T): Promise<T> {
  await mockDelay()
  return data
}
```
- [ ] Use in all custom hooks
- [ ] Add loading states in React Query

### Task 8: Final Integration & Testing
- [ ] Verify all JSON fixtures load without errors
- [ ] Test React Query DevTools shows cached data
- [ ] Test mock WebSocket connects and emits events
- [ ] Test custom hooks with React Query DevTools
- [ ] Verify TypeScript types are correctly inferred
- [ ] Check console for any errors

---

## Dev Notes

### Mock Data Structure

**Stores (50 total):**
- 20 stores in Fashion_Forward cluster (A-tier locations)
- 18 stores in Mainstream cluster (B-tier locations)
- 12 stores in Value_Conscious cluster (C-tier locations)

**Forecast:**
- 12-week season (Spring 2025)
- Total demand: 8,000 units
- Peak week: Week 3
- Prophet forecast: 8,200 units
- ARIMA forecast: 7,800 units

**Agent Progression:**
1. Demand Agent: 0-33% (2s) → 33-66% (2s) → Complete
2. Inventory Agent: 66-80% (2s) → Complete
3. Pricing Agent: 80-100% (2s) → Complete

### State Management Architecture

```
App Providers:
├── QueryClientProvider (React Query)
├── ParametersProvider (Season parameters)
└── WorkflowProvider (Workflow state)

Custom Hooks:
├── useForecast() → Forecast data
├── useClusters() → Cluster data
├── useStores() → Store data
├── useAgentStatus() → WebSocket agent updates
└── useParameters() → Season parameters context
```

### Critical References

- **Planning Spec:** `planning/3_technical_architecture_v3.3.md` lines 284-400 (Data models)
- **React Query Docs:** https://tanstack.com/query/latest/docs/framework/react/overview
- **Phase 1 Data:** `data/phase_1_data_generation/output/` (CSV files)

### Common Issues & Solutions

**Issue 1: React Query not updating**
- Solution: Check `queryKey` is unique and `enabled` flag is correct

**Issue 2: Mock WebSocket not firing**
- Solution: Verify `connect()` is called and `onMessage` handler is registered

**Issue 3: TypeScript errors on JSON imports**
- Solution: Add `resolveJsonModule: true` to `tsconfig.json`

---

## Testing

### Manual Testing Checklist

- [ ] React Query DevTools visible in dev mode
- [ ] Mock forecast data loads in DevTools cache
- [ ] Custom hooks return data after delay
- [ ] Mock WebSocket emits 6 agent state updates
- [ ] Parameters context stores/retrieves values correctly
- [ ] No TypeScript compilation errors
- [ ] No console errors in browser
- [ ] JSON fixtures parse correctly

### Verification Commands

```bash
# Verify React Query installed
npm list @tanstack/react-query

# Check TypeScript types
npx tsc --noEmit

# Run dev server
npm run dev
```

---

## File List

_Dev Agent will populate this section during implementation_

**Files to Create:**
- `src/lib/react-query.ts`
- `src/lib/mock-websocket.ts`
- `src/lib/mock-api.ts`
- `src/types/store.ts`
- `src/types/forecast.ts`
- `src/types/agent.ts`
- `src/types/parameters.ts`
- `src/contexts/ParametersContext.tsx`
- `src/contexts/WorkflowContext.tsx`
- `src/hooks/useForecast.ts`
- `src/hooks/useClusters.ts`
- `src/hooks/useStores.ts`
- `src/hooks/useAgentStatus.ts`
- `src/hooks/useParameters.ts`
- `src/mocks/stores.json`
- `src/mocks/forecast.json`
- `src/mocks/clusters.json`

**Files to Modify:**
- `src/main.tsx` (add providers)
- `tsconfig.json` (add resolveJsonModule: true)

---

## Dev Agent Record

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

### Change Log

_Dev Agent tracks all file changes here_

---

## Definition of Done

- [x] TanStack React Query installed and configured
- [x] Phase 1 CSV converted to JSON fixtures
- [x] All TypeScript types defined and compiling
- [x] Mock WebSocket client implemented
- [x] React Context providers created
- [x] All custom hooks created and tested
- [x] Mock API delay simulation working
- [x] All manual tests pass
- [x] File List updated

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Story Points:** 3
**Priority:** P0 (Blocker for all UI sections)
