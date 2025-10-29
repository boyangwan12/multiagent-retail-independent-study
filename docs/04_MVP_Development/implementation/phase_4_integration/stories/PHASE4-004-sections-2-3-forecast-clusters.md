# Story: Integrate Sections 2-3 - Forecast Summary + Cluster Cards

**Epic:** Phase 4 - Frontend/Backend Integration
**Story ID:** PHASE4-004
**Status:** Ready for Implementation
**Estimate:** 5 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE4-003 (Section 1 - WebSocket)

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
3. ✅ Section 2 (Forecast Summary) displays backend forecast data
4. ✅ Forecast metrics display correctly (total demand, Prophet/ARIMA values, ensemble)
5. ✅ Manufacturing order displays with approval status
6. ✅ Mini forecast chart renders with backend data
7. ✅ Section 3 (Cluster Cards) displays backend cluster data
8. ✅ All 3 clusters display (Fashion_Forward, Mainstream, Value_Conscious)
9. ✅ Store table expands/collapses correctly
10. ✅ Export CSV button works (downloads cluster data)

### Quality Requirements

11. ✅ JSON structure matches TypeScript types exactly
12. ✅ No console errors during data display
13. ✅ Data updates when workflow completes (reactive)
14. ✅ Loading states show while fetching data
15. ✅ Test with different parameter combinations (mock agents return different data)

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

### Task 5: Update ForecastSummary Component (Section 2)

**Subtasks:**
- [ ] Locate `frontend/src/components/ForecastSummary/ForecastSummary.tsx`

- [ ] Add state for forecast data:
  ```typescript
  import { ForecastService } from '@/services/forecast-service';
  import type { Forecast } from '@/types/forecast';

  interface ForecastSummaryProps {
    forecastId: string | null;
  }

  export function ForecastSummary({ forecastId }: ForecastSummaryProps) {
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
          setForecast(data);
        } catch (err) {
          console.error('Failed to fetch forecast:', err);
          setError('Failed to load forecast data');
        } finally {
          setIsLoading(false);
        }
      };

      fetchForecast();
    }, [forecastId]);

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
                <LineChart data={forecast.weekly_demand_curve.map((value, week) => ({ week: week + 1, demand: value }))}>
                  <Line type="monotone" dataKey="demand" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  <XAxis dataKey="week" hide />
                  <YAxis hide />
                  <Tooltip />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-xs text-gray-600 mt-2">
                Peak demand at Week {forecast.peak_week}: {forecast.weekly_demand_curve[forecast.peak_week - 1]} units
              </p>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    );
  }
  ```

**Validation:**
- Loading state shows while fetching
- Forecast data displays correctly
- Manufacturing order calculates correctly (demand × (1 + safety_stock))
- Adaptation reasoning displays
- Mini chart renders with weekly data
- Peak week highlighted

---

### Task 6: Update ClusterCards Component (Section 3)

**Subtasks:**
- [ ] Locate `frontend/src/components/ClusterCards/ClusterCards.tsx`

- [ ] Add state for cluster data:
  ```typescript
  import { ClusterService } from '@/services/cluster-service';
  import type { Cluster } from '@/types/cluster';

  export function ClusterCards() {
    const [clusters, setClusters] = useState<Cluster[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      const fetchClusters = async () => {
        setIsLoading(true);
        setError(null);

        try {
          const data = await ClusterService.getClusters();
          setClusters(data.clusters);
        } catch (err) {
          console.error('Failed to fetch clusters:', err);
          setError('Failed to load cluster data');
        } finally {
          setIsLoading(false);
        }
      };

      fetchClusters();
    }, []);

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

- [ ] Update ClusterCard to display cluster data:
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
              <Button variant="outline" size="sm" onClick={handleExportCSV}>
                <Download className="mr-2 h-4 w-4" />
                Export CSV
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? <ChevronUp /> : <ChevronDown />}
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

- [ ] GET /api/forecasts/{id} tested with Postman
- [ ] GET /api/stores/clusters tested with Postman
- [ ] TypeScript types created for forecast and clusters
- [ ] API services created and tested
- [ ] Section 2 (ForecastSummary) updated with real data
- [ ] Section 3 (ClusterCards) updated with real data
- [ ] Loading states work correctly
- [ ] Error handling implemented
- [ ] Manufacturing order calculates correctly
- [ ] Adaptation reasoning displays
- [ ] Mini chart renders
- [ ] All 3 clusters display
- [ ] Store table expands/collapses
- [ ] Export CSV works
- [ ] All manual tests passing
- [ ] No console errors
- [ ] Data updates reactively when workflow completes

---

## Time Tracking

- **Estimated:** 5 hours
- **Actual:** ___ hours
- **Variance:** ___ hours

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
