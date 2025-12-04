# Story: Integrate Sections 2-3 - Forecast Summary + Cluster Cards

**Epic:** Phase 4 - Frontend/Backend Integration
**Story ID:** PHASE4-004
**Status:** Ready for Implementation
**Estimate:** 6 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE4-003 (Section 1 - WebSocket)

**Planning References:**
- PRD v3.3: Section 4.1 (Forecast Display & Manufacturing Order)
- Technical Architecture v3.3: Section 4.4 (Forecast & Cluster APIs)
- Frontend Spec v3.3: Sections 3.3-3.4 (Sections 2-3 Design)

---

## Story

As a user,
I want to view the forecast results and store cluster analysis after the workflow completes,
So that I can understand the demand forecast and how inventory will be allocated across store clusters.

**Business Value:** These two sections display the core outputs of the Demand Agent - the total forecast and the cluster-based allocation strategy. Without this integration, users cannot see the results of the forecasting workflow, making the system useless. This is the first tangible business value delivery after workflow execution.

**Epic Context:** This is Story 4 of 9 in Phase 4. After the WebSocket workflow completes (Story 3), users need to see the results. Sections 2-3 display forecast data and cluster allocations from the mock Demand Agent. This validates that the full data flow works: parameters → workflow → agents → results → UI display.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ GET /api/forecasts/{id} endpoint tested with Postman (returns forecast data)
2. ✅ GET /api/stores/clusters endpoint tested with Postman (returns cluster data)
3. ✅ forecast_id passed from workflow_complete message to ForecastSummary via Context
4. ✅ Section 2 (Forecast Summary) displays backend forecast data
5. ✅ Forecast metrics display correctly (total demand, Prophet/ARIMA values, ensemble)
6. ✅ Manufacturing order displays with approval status
7. ✅ Manufacturing order calculation validated (demand × (1 + safety_stock))
8. ✅ Mini forecast chart renders with backend data
9. ✅ Section 3 (Cluster Cards) displays backend cluster data after workflow completion
10. ✅ All 3 clusters display (Fashion_Forward, Mainstream, Value_Conscious)
11. ✅ Store table expands/collapses correctly
12. ✅ Export CSV button works (downloads cluster data)

### Data Validation & Error Handling

13. ✅ Forecast category matches category selected in Section 0
14. ✅ 404 error handled if forecast_id not found
15. ✅ Peak week array bounds checked before access
16. ✅ Error message displays if forecast fetch fails
17. ✅ Error message displays if clusters fetch fails
18. ✅ ClusterCards waits for workflow completion before fetching

### Quality Requirements

19. ✅ JSON structure matches TypeScript types exactly
20. ✅ No console errors during data display
21. ✅ Data updates reactively when workflow_complete message received
22. ✅ Loading states show while fetching data
23. ✅ Test with different parameter combinations (mock agents return different data)

### Accessibility

24. ✅ Metric cards have descriptive aria-labels
25. ✅ Chart has aria-label and accessible description
26. ✅ Export CSV button has aria-label
27. ✅ Collapsible store tables accessible via keyboard (Enter/Space to expand)

---

## Tasks

### Task 1: Test Backend Forecast Endpoint with Postman

**Goal:** Verify the forecast endpoint returns correct data BEFORE integrating with frontend.

**Subtasks:**
- [ ] Complete a workflow using PHASE4-003 (returns forecast_id)
- [ ] Copy the `forecast_id` from workflow_complete message
- [ ] Open Postman and create new request:
  - Method: GET
  - URL: `http://localhost:8000/api/forecasts/{forecast_id}`
  - Headers: None (GET request)

- [ ] Send request and verify response (200 OK):
  ```json
  {
    "forecast_id": "fc_abc123",
    "workflow_id": "wf_abc123",
    "category_name": "Women's Dresses",
    "season_parameters": {
      "forecast_horizon_weeks": 12,
      "season_start_date": "2025-11-03",
      "replenishment_strategy": "weekly",
      "dc_holdback_percentage": 0.45,
      "markdown_checkpoint_week": 6,
      "markdown_threshold": 0.60
    },
    "total_season_demand": 8000,
    "prophet_forecast": 8200,
    "arima_forecast": 7800,
    "forecasting_method": "ensemble_prophet_arima",
    "safety_stock_pct": 0.25,
    "adaptation_reasoning": "No replenishment strategy → increased safety stock from 20% to 25%",
    "weekly_demand_curve": [650, 720, 680, 710, 690, 750, 820, 780, 710, 650, 600, 540],
    "peak_week": 7,
    "cluster_distribution": {
      "Fashion_Forward": 0.40,
      "Mainstream": 0.35,
      "Value_Conscious": 0.25
    },
    "created_at": "2025-10-29T10:30:45Z"
  }
  ```

- [ ] Verify all expected fields present
- [ ] Verify weekly_demand_curve has 12 values (matches forecast_horizon_weeks)
- [ ] Verify cluster_distribution sums to 1.0
- [ ] Verify adaptation_reasoning explains parameter-driven changes

**Test with different parameters:**

**Test Case 1: No replenishment (100% allocation)**
- Parameters: `replenishment_strategy: "none"`, `dc_holdback_percentage: 0.0`
- Expected: `safety_stock_pct: 0.25` (higher), `adaptation_reasoning` explains why

**Test Case 2: Weekly replenishment (45% holdback)**
- Parameters: `replenishment_strategy: "weekly"`, `dc_holdback_percentage: 0.45`
- Expected: `safety_stock_pct: 0.20` (standard)

**Validation:**
- All test cases return 200 OK
- Mock agent adapts safety_stock based on replenishment_strategy
- adaptation_reasoning is present and explains changes

---

### Task 2: Test Backend Clusters Endpoint with Postman

**Goal:** Verify the clusters endpoint returns correct data.

**Subtasks:**
- [ ] Open Postman and create new request:
  - Method: GET
  - URL: `http://localhost:8000/api/stores/clusters`
  - Headers: None

- [ ] Send request and verify response (200 OK):
  ```json
  {
    "clusters": [
      {
        "cluster_id": "Fashion_Forward",
        "cluster_name": "Fashion Forward",
        "fashion_tier": "Premium",
        "store_count": 18,
        "avg_weekly_sales": 15200,
        "avg_store_size_sqft": 8500,
        "avg_median_income": 95000,
        "stores": [
          {
            "store_id": "S01",
            "store_name": "Manhattan Flagship",
            "cluster_id": "Fashion_Forward",
            "store_size_sqft": 12000,
            "location_tier": "Tier 1",
            "median_income": 110000,
            "foot_traffic": 8500,
            "competitor_density": "High",
            "online_penetration": 0.35,
            "population_density": 25000,
            "allocation_factor": 0.08
          },
          // ... 17 more stores
        ]
      },
      {
        "cluster_id": "Mainstream",
        "cluster_name": "Mainstream",
        "fashion_tier": "Mid-Market",
        "store_count": 20,
        "avg_weekly_sales": 9800,
        "stores": [/* ... */]
      },
      {
        "cluster_id": "Value_Conscious",
        "cluster_name": "Value Conscious",
        "fashion_tier": "Value",
        "store_count": 12,
        "avg_weekly_sales": 6200,
        "stores": [/* ... */]
      }
    ]
  }
  ```

- [ ] Verify 3 clusters returned
- [ ] Verify store_count totals 50 (18 + 20 + 12)
- [ ] Verify each cluster has stores array
- [ ] Verify allocation_factor present for each store
- [ ] Verify allocation_factors within cluster sum to ~1.0

**Validation:**
- Response returns 200 OK
- All 3 clusters present
- All 50 stores present across clusters
- Data structure matches TypeScript types

---

### Task 3: Create TypeScript Types for Forecast and Clusters

**Subtasks:**
- [ ] Create `frontend/src/types/forecast.ts`:
  ```typescript
  import type { SeasonParameters } from './parameters';

  export interface Forecast {
    forecast_id: string;
    workflow_id: string;
    category_name: string;
    season_parameters: SeasonParameters;
    total_season_demand: number;
    prophet_forecast: number;
    arima_forecast: number;
    forecasting_method: string;
    safety_stock_pct: number;
    adaptation_reasoning: string;
    weekly_demand_curve: number[]; // 12 values
    peak_week: number;
    cluster_distribution: {
      Fashion_Forward: number;
      Mainstream: number;
      Value_Conscious: number;
    };
    created_at: string;
  }

  export interface ManufacturingOrder {
    manufacturing_qty: number;
    safety_stock_pct: number;
    approval_status: "pending" | "approved" | "rejected";
  }
  ```

- [ ] Create `frontend/src/types/cluster.ts`:
  ```typescript
  export interface Store {
    store_id: string;
    store_name: string;
    cluster_id: string;
    store_size_sqft: number;
    location_tier: string;
    median_income: number;
    foot_traffic: number;
    competitor_density: string;
    online_penetration: number;
    population_density: number;
    allocation_factor: number;
  }

  export interface Cluster {
    cluster_id: string;
    cluster_name: string;
    fashion_tier: string;
    store_count: number;
    avg_weekly_sales: number;
    avg_store_size_sqft?: number;
    avg_median_income?: number;
    stores: Store[];
  }

  export interface ClustersResponse {
    clusters: Cluster[];
  }
  ```

- [ ] Export types for use in components

**Validation:**
- TypeScript compiles without errors
- Types match backend response exactly

---

### Task 4: Create API Services for Forecast and Clusters

**Subtasks:**
- [ ] Create `frontend/src/services/forecast-service.ts`:
  ```typescript
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';
  import type { Forecast } from '@/types/forecast';

  export class ForecastService {
    /**
     * Get forecast by ID
     */
    static async getForecast(forecastId: string): Promise<Forecast> {
      return ApiClient.get<Forecast>(API_ENDPOINTS.FORECASTS_GET(forecastId));
    }

    /**
     * Get all forecasts
     */
    static async getAllForecasts(): Promise<Forecast[]> {
      return ApiClient.get<Forecast[]>(API_ENDPOINTS.FORECASTS);
    }
  }
  ```

- [ ] Create `frontend/src/services/cluster-service.ts`:
  ```typescript
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';
  import type { ClustersResponse } from '@/types/cluster';

  export class ClusterService {
    /**
     * Get all store clusters
     */
    static async getClusters(): Promise<ClustersResponse> {
      return ApiClient.get<ClustersResponse>(API_ENDPOINTS.STORES_CLUSTERS);
    }
  }
  ```

- [ ] Test services in isolation:
  ```typescript
  // Test in browser console
  import { ForecastService } from '@/services/forecast-service';
  import { ClusterService } from '@/services/cluster-service';

  ForecastService.getForecast('fc_abc123')
    .then(data => console.log('Forecast:', data))
    .catch(err => console.error('Error:', err));

  ClusterService.getClusters()
    .then(data => console.log('Clusters:', data))
    .catch(err => console.error('Error:', err));
  ```

**Validation:**
- Services successfully call backend
- Response structure matches TypeScript types
- Error handling works

---

### Task 5: Extend ParameterContext to Include Workflow Results

**Goal:** Make forecast_id and workflowComplete status available across components via Context.

**Subtasks:**
- [ ] Update ParameterContext to include workflow results:
  ```typescript
  // frontend/src/contexts/ParameterContext.tsx
  import React, { createContext, useContext, useState, ReactNode } from 'react';
  import type { SeasonParameters } from '@/types/parameters';
  import type { Category } from '@/types/category';

  interface ParameterContextState {
    parameters: SeasonParameters | null;
    category: Category | null;
    isConfirmed: boolean;

    // Workflow results (added)
    workflowId: string | null;
    forecastId: string | null;
    workflowComplete: boolean;

    setParameters: (params: SeasonParameters) => void;
    setCategory: (cat: Category) => void;
    confirmParameters: () => void;
    resetParameters: () => void;

    // Workflow result setters (added)
    setWorkflowId: (id: string) => void;
    setForecastId: (id: string) => void;
    setWorkflowComplete: (complete: boolean) => void;
  }

  const ParameterContext = createContext<ParameterContextState | undefined>(undefined);

  export function ParameterProvider({ children }: { children: ReactNode }) {
    const [parameters, setParametersState] = useState<SeasonParameters | null>(null);
    const [category, setCategoryState] = useState<Category | null>(null);
    const [isConfirmed, setIsConfirmed] = useState(false);

    // Workflow results state
    const [workflowId, setWorkflowIdState] = useState<string | null>(null);
    const [forecastId, setForecastIdState] = useState<string | null>(null);
    const [workflowComplete, setWorkflowCompleteState] = useState(false);

    const setParameters = (params: SeasonParameters) => {
      setParametersState(params);
    };

    const setCategory = (cat: Category) => {
      setCategoryState(cat);
    };

    const confirmParameters = () => {
      setIsConfirmed(true);
    };

    const resetParameters = () => {
      setParametersState(null);
      setCategoryState(null);
      setIsConfirmed(false);
      setWorkflowIdState(null);
      setForecastIdState(null);
      setWorkflowCompleteState(false);
    };

    const setWorkflowId = (id: string) => {
      setWorkflowIdState(id);
    };

    const setForecastId = (id: string) => {
      setForecastIdState(id);
    };

    const setWorkflowComplete = (complete: boolean) => {
      setWorkflowCompleteState(complete);
    };

    return (
      <ParameterContext.Provider
        value={{
          parameters,
          category,
          isConfirmed,
          workflowId,
          forecastId,
          workflowComplete,
          setParameters,
          setCategory,
          confirmParameters,
          resetParameters,
          setWorkflowId,
          setForecastId,
          setWorkflowComplete,
        }}
      >
        {children}
      </ParameterContext.Provider>
    );
  }

  export function useParameters() {
    const context = useContext(ParameterContext);
    if (!context) {
      throw new Error('useParameters must be used within a ParameterProvider');
    }
    return context;
  }
  ```

- [ ] Update useWebSocket hook to set workflow results in Context:
  ```typescript
  // In useWebSocket hook (PHASE4-003)
  import { useParameters } from '@/contexts/ParameterContext';

  export function useWebSocket(workflowId: string | null) {
    const { setForecastId, setWorkflowComplete } = useParameters();

    // ... existing state

    const handleMessage = (message: WebSocketMessageType) => {
      switch (message.type) {
        // ... other cases

        case 'workflow_complete':
          console.log('✅ Workflow complete:', message);
          setWorkflowComplete(true);
          setWorkflowResult(message.result);

          // Extract forecast_id from result and store in Context
          if (message.result?.forecast_id) {
            setForecastId(message.result.forecast_id);
            console.log('📊 Forecast ID set in Context:', message.result.forecast_id);
          }
          break;
      }
    };
  ```

- [ ] Update ParameterGathering to set workflowId in Context:
  ```typescript
  // After workflow creation succeeds
  const { setWorkflowId } = useParameters();

  const response = await WorkflowService.createForecastWorkflow({
    parameters: parameters,
    category_name: category.category_name,
  });

  setWorkflowId(response.workflow_id);
  setWorkflowIdState(response.workflow_id); // Local state for WebSocket
  ```

**Validation:**
- ParameterContext exposes forecastId and workflowComplete
- useWebSocket hook sets forecastId when workflow_complete received
- Components can access forecastId via useParameters()
- ForecastSummary and ClusterCards can react to workflow completion

---

### Task 6: Update ForecastSummary Component (Section 2)

**Subtasks:**
- [ ] Locate `frontend/src/components/ForecastSummary/ForecastSummary.tsx`

- [ ] Update to use forecast_id from Context with validation:
  ```typescript
  import { ForecastService } from '@/services/forecast-service';
  import { useParameters } from '@/contexts/ParameterContext';
  import type { Forecast } from '@/types/forecast';

  export function ForecastSummary() {
    const { forecastId, category, parameters } = useParameters();
    const [forecast, setForecast] = useState<Forecast | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      if (!forecastId) return;

      const fetchForecast = async () => {
        setIsLoading(true);
        setError(null);

        try {
          const data = await ForecastService.getForecast(forecastId);

          // Validate forecast category matches selected category
          if (category && data.category_name !== category.category_name) {
            console.warn(
              `Forecast category (${data.category_name}) doesn't match selected category (${category.category_name})`
            );
          }

          setForecast(data);
        } catch (err) {
          console.error('Failed to fetch forecast:', err);

          // Handle specific error types
          let errorMessage = 'Failed to load forecast data';
          if (err.status === 404) {
            errorMessage = 'Forecast not found. Please restart the workflow.';
          } else if (err.status === 500) {
            errorMessage = 'Server error loading forecast. Please try again.';
          } else if (err.status === 0) {
            errorMessage = 'Cannot connect to backend. Is the server running?';
          }

          setError(errorMessage);
        } finally {
          setIsLoading(false);
        }
      };

      fetchForecast();
    }, [forecastId, category]);

    if (!forecastId) {
      return (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-gray-500">
              No forecast available. Please complete workflow first.
            </p>
          </CardContent>
        </Card>
      );
    }

    if (isLoading) {
      return (
        <Card>
          <CardContent className="py-8">
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="h-5 w-5 animate-spin" />
              <p className="text-gray-600">Loading forecast...</p>
            </div>
          </CardContent>
        </Card>
      );
    }

    if (error || !forecast) {
      return (
        <Card>
          <CardContent className="py-8">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error || 'Forecast not found'}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      );
    }

    // Display forecast data...
    return (
      <Card>
        <CardHeader>
          <CardTitle>Forecast Summary - {forecast.category_name}</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Forecast Metrics */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <MetricCard
              label="Total Season Demand"
              value={forecast.total_season_demand.toLocaleString()}
              icon={<TrendingUp />}
            />
            <MetricCard
              label="Prophet Forecast"
              value={forecast.prophet_forecast.toLocaleString()}
              icon={<Activity />}
            />
            <MetricCard
              label="ARIMA Forecast"
              value={forecast.arima_forecast.toLocaleString()}
              icon={<BarChart3 />}
            />
          </div>

          {/* Manufacturing Order */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-base">Manufacturing Order</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold">
                    {Math.round(forecast.total_season_demand * (1 + forecast.safety_stock_pct)).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    {forecast.total_season_demand.toLocaleString()} demand +{' '}
                    {(forecast.safety_stock_pct * 100).toFixed(0)}% safety stock
                  </p>
                </div>
                <Badge variant="outline">Pending Approval</Badge>
              </div>

              {/* Adaptation Reasoning */}
              {forecast.adaptation_reasoning && (
                <Alert className="mt-4">
                  <Info className="h-4 w-4" />
                  <AlertDescription className="text-sm">
                    <strong>Agent Reasoning:</strong> {forecast.adaptation_reasoning}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Mini Forecast Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Weekly Demand Curve</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={60}>
                <LineChart
                  data={forecast.weekly_demand_curve.map((value, week) => ({ week: week + 1, demand: value }))}
                  aria-label={`Weekly demand curve for ${forecast.category_name}`}
                >
                  <Line type="monotone" dataKey="demand" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  <XAxis dataKey="week" hide />
                  <YAxis hide />
                  <Tooltip />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-xs text-gray-600 mt-2">
                {/* Peak week bounds checking */}
                {forecast.peak_week > 0 && forecast.peak_week <= forecast.weekly_demand_curve.length ? (
                  <>
                    Peak demand at Week {forecast.peak_week}:{' '}
                    {forecast.weekly_demand_curve[forecast.peak_week - 1].toLocaleString()} units
                  </>
                ) : (
                  <>Peak demand: {Math.max(...forecast.weekly_demand_curve).toLocaleString()} units</>
                )}
              </p>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    );
  }
  ```

- [ ] Add accessibility attributes to metric cards:
  ```typescript
  <MetricCard
    label="Total Season Demand"
    value={forecast.total_season_demand.toLocaleString()}
    icon={<TrendingUp />}
    ariaLabel={`Total season demand: ${forecast.total_season_demand.toLocaleString()} units`}
  />
  ```

**Validation:**
- Loading state shows while fetching
- Forecast data displays correctly
- Manufacturing order calculates correctly (demand × (1 + safety_stock))
- Adaptation reasoning displays
- Mini chart renders with weekly data
- Peak week highlighted

---

### Task 7: Update ClusterCards Component (Section 3)

**Subtasks:**
- [ ] Locate `frontend/src/components/ClusterCards/ClusterCards.tsx`

- [ ] Update to wait for workflow completion before fetching:
  ```typescript
  import { ClusterService } from '@/services/cluster-service';
  import { useParameters } from '@/contexts/ParameterContext';
  import type { Cluster } from '@/types/cluster';

  export function ClusterCards() {
    const { workflowComplete } = useParameters();
    const [clusters, setClusters] = useState<Cluster[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      // Wait for workflow to complete before fetching clusters
      if (!workflowComplete) {
        return;
      }

      const fetchClusters = async () => {
        setIsLoading(true);
        setError(null);

        try {
          const data = await ClusterService.getClusters();
          setClusters(data.clusters);
        } catch (err) {
          console.error('Failed to fetch clusters:', err);

          // Handle specific error types
          let errorMessage = 'Failed to load cluster data';
          if (err.status === 500) {
            errorMessage = 'Server error loading clusters. Please try again.';
          } else if (err.status === 0) {
            errorMessage = 'Cannot connect to backend. Is the server running?';
          }

          setError(errorMessage);
        } finally {
          setIsLoading(false);
        }
      };

      fetchClusters();
    }, [workflowComplete]);

    if (isLoading) {
      return (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <Card key={i}>
              <CardContent className="py-8">
                <Skeleton className="h-12 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      );
    }

    if (error) {
      return (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      );
    }

    return (
      <div className="space-y-4">
        {clusters.map(cluster => (
          <ClusterCard key={cluster.cluster_id} cluster={cluster} />
        ))}
      </div>
    );
  }
  ```

- [ ] Update ClusterCard to display cluster data with accessibility:
  ```typescript
  function ClusterCard({ cluster }: { cluster: Cluster }) {
    const [isExpanded, setIsExpanded] = useState(false);

    const handleExportCSV = () => {
      // Export cluster stores to CSV
      const csvContent = [
        ['Store ID', 'Store Name', 'Size (sqft)', 'Location Tier', 'Allocation Factor'],
        ...cluster.stores.map(store => [
          store.store_id,
          store.store_name,
          store.store_size_sqft,
          store.location_tier,
          store.allocation_factor.toFixed(4),
        ]),
      ]
        .map(row => row.join(','))
        .join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${cluster.cluster_id}_stores.csv`;
      a.click();
      URL.revokeObjectURL(url);
    };

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{cluster.cluster_name}</CardTitle>
              <p className="text-sm text-gray-600">
                {cluster.store_count} stores • {cluster.fashion_tier}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportCSV}
                aria-label={`Export ${cluster.cluster_name} stores to CSV`}
              >
                <Download className="mr-2 h-4 w-4" aria-hidden="true" />
                Export CSV
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                aria-expanded={isExpanded}
                aria-label={`${isExpanded ? 'Collapse' : 'Expand'} ${cluster.cluster_name} store list`}
                aria-controls={`cluster-${cluster.cluster_id}-stores`}
              >
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4" aria-hidden="true" />
                ) : (
                  <ChevronDown className="h-4 w-4" aria-hidden="true" />
                )}
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* Cluster Metrics */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-600">Avg Weekly Sales</p>
              <p className="text-lg font-semibold">
                ${cluster.avg_weekly_sales.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Store Size</p>
              <p className="text-lg font-semibold">
                {cluster.avg_store_size_sqft?.toLocaleString()} sqft
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Income</p>
              <p className="text-lg font-semibold">
                ${cluster.avg_median_income?.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Store Table (Expandable) */}
          {isExpanded && (
            <div className="mt-4">
              <ClusterTable stores={cluster.stores} />
            </div>
          )}
        </CardContent>
      </Card>
    );
  }
  ```

- [ ] Update ClusterTable to display stores:
  ```typescript
  function ClusterTable({ stores }: { stores: Store[] }) {
    return (
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Store ID</TableHead>
              <TableHead>Store Name</TableHead>
              <TableHead>Size (sqft)</TableHead>
              <TableHead>Location Tier</TableHead>
              <TableHead>Allocation Factor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {stores.map(store => (
              <TableRow key={store.store_id}>
                <TableCell className="font-medium">{store.store_id}</TableCell>
                <TableCell>{store.store_name}</TableCell>
                <TableCell>{store.store_size_sqft.toLocaleString()}</TableCell>
                <TableCell>
                  <Badge variant={store.location_tier === 'Tier 1' ? 'default' : 'secondary'}>
                    {store.location_tier}
                  </Badge>
                </TableCell>
                <TableCell>{(store.allocation_factor * 100).toFixed(2)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  }
  ```

**Validation:**
- All 3 clusters display
- Cluster metrics display correctly
- Store table expands/collapses
- Export CSV button downloads correct data
- Loading skeletons show while fetching

---

### Task 7: Connect Sections to Workflow Results

**Subtasks:**
- [ ] Update main App/Dashboard to pass forecastId from workflow result:
  ```typescript
  // In main component
  const [workflowResult, setWorkflowResult] = useState<any>(null);

  // From PHASE4-003 useWebSocket hook
  const { workflowComplete, workflowResult } = useWebSocket(workflowId);

  useEffect(() => {
    if (workflowComplete && workflowResult) {
      setWorkflowResult(workflowResult);
    }
  }, [workflowComplete, workflowResult]);

  return (
    <>
      <Section0ParameterGathering onWorkflowStart={setWorkflowId} />
      <Section1AgentWorkflow workflowId={workflowId} />
      <Section2ForecastSummary forecastId={workflowResult?.forecast_id} />
      <Section3ClusterCards />
      {/* ... other sections */}
    </>
  );
  ```

**Validation:**
- When workflow completes, forecastId passed to Section 2
- Section 2 automatically fetches forecast data
- Section 3 displays cluster data
- Data appears without manual refresh

---

## Testing Requirements

### Integration Tests
```typescript
describe('ForecastSummary Component', () => {
  it('should display forecast data', async () => {
    render(<ForecastSummary forecastId="fc_test123" />);

    await waitFor(() => {
      expect(screen.getByText(/total season demand/i)).toBeInTheDocument();
      expect(screen.getByText('8,000')).toBeInTheDocument();
    });
  });

  it('should display adaptation reasoning', async () => {
    render(<ForecastSummary forecastId="fc_test123" />);

    await waitFor(() => {
      expect(screen.getByText(/agent reasoning/i)).toBeInTheDocument();
    });
  });
});

describe('ClusterCards Component', () => {
  it('should display all 3 clusters', async () => {
    render(<ClusterCards />);

    await waitFor(() => {
      expect(screen.getByText(/fashion forward/i)).toBeInTheDocument();
      expect(screen.getByText(/mainstream/i)).toBeInTheDocument();
      expect(screen.getByText(/value conscious/i)).toBeInTheDocument();
    });
  });

  it('should export cluster data to CSV', async () => {
    render(<ClusterCards />);

    await waitFor(() => {
      const exportButton = screen.getAllByText(/export csv/i)[0];
      fireEvent.click(exportButton);
      // Assert CSV download triggered
    });
  });
});
```

### Manual Testing Checklist
- [ ] Complete workflow (PHASE4-003)
- [ ] Verify Section 2 appears automatically after workflow complete
- [ ] Verify forecast data displays (total demand, Prophet, ARIMA)
- [ ] Verify manufacturing order calculates correctly
- [ ] Verify adaptation reasoning displays
- [ ] Verify mini chart renders
- [ ] Verify Section 3 displays all 3 clusters
- [ ] Verify cluster metrics correct
- [ ] Click expand button on cluster card
- [ ] Verify store table displays
- [ ] Verify allocation factors sum to 100% within cluster
- [ ] Click "Export CSV" button
- [ ] Verify CSV file downloads with correct data
- [ ] Test with different parameters (mock agents return different data)

---

## Dependencies

**Requires:**
- PHASE4-003 complete (WebSocket workflow completes, returns forecast_id)
- Backend GET /api/forecasts/{id} endpoint functional
- Backend GET /api/stores/clusters endpoint functional
- Mock agents return dynamic data based on parameters

**Enables:**
- PHASE4-005 (Sections 4-5 can display variance/allocation)
- PHASE4-006 (Sections 6-7 can display markdown/metrics)

---

## Definition of Done

**Backend Integration:**
- [ ] GET /api/forecasts/{id} tested with Postman
- [ ] GET /api/stores/clusters tested with Postman
- [ ] TypeScript types created for forecast and clusters
- [ ] API services created and tested

**Context Integration:**
- [ ] ParameterContext extended to include workflowId, forecastId, workflowComplete
- [ ] useWebSocket hook sets forecastId when workflow_complete received
- [ ] ParameterGathering sets workflowId in Context after workflow creation
- [ ] ForecastSummary uses forecastId from Context (not props)
- [ ] ClusterCards uses workflowComplete from Context

**Data Display:**
- [ ] Section 2 (ForecastSummary) displays backend forecast data
- [ ] Section 3 (ClusterCards) displays backend cluster data
- [ ] Loading states work correctly
- [ ] Manufacturing order calculates correctly (demand × (1 + safety_stock))
- [ ] Adaptation reasoning displays
- [ ] Mini chart renders with weekly data
- [ ] All 3 clusters display
- [ ] Store table expands/collapses
- [ ] Export CSV works

**Validation & Error Handling:**
- [ ] Forecast category validated against selected category
- [ ] 404 error handled (forecast not found)
- [ ] 500 and network errors handled
- [ ] Peak week array bounds checked
- [ ] ClusterCards waits for workflow completion before fetching
- [ ] Error messages displayed for failed fetches

**Reactivity:**
- [ ] Data updates reactively when workflow_complete message received
- [ ] ForecastSummary fetches when forecastId changes
- [ ] ClusterCards fetches when workflowComplete becomes true

**Accessibility:**
- [ ] Metric cards have aria-labels
- [ ] Chart has aria-label
- [ ] Export CSV button has aria-label
- [ ] Collapsible toggle has aria-expanded and aria-controls
- [ ] Icons have aria-hidden="true"

**Quality:**
- [ ] All manual tests passing
- [ ] No console errors
- [ ] TypeScript compiles without errors

---

## Time Tracking

- **Estimated:** 6 hours
- **Actual:** ___ hours
- **Variance:** ___ hours

**Breakdown:**
- Task 1 (Postman forecast endpoint): ___ min
- Task 2 (Postman clusters endpoint): ___ min
- Task 3 (TypeScript types): ___ min
- Task 4 (API services): ___ min
- Task 5 (Extend ParameterContext): ___ min
- Task 6 (ForecastSummary with Context): ___ min
- Task 7 (ClusterCards with workflow wait): ___ min
- Additional: Validation and error handling: ___ min
- Additional: Accessibility: ___ min
- Testing: ___ min
- Documentation: ___ min

---

## Related Stories

- **Depends On:** PHASE4-003 (Section 1 - WebSocket)
- **Blocks:** PHASE4-005, PHASE4-006
- **Related:** PHASE4-008 (Integration Tests)

---

**Status:** ⏳ Ready for Implementation
**Assigned To:** Dev Team
**Priority:** P1 (High)
**Created:** 2025-10-29
**Updated:** 2025-10-29
