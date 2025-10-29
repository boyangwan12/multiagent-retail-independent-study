# Story: Integrate Sections 4-5 - Weekly Performance Chart + Replenishment Queue

**Epic:** Phase 4 - Frontend/Backend Integration
**Story ID:** PHASE4-005
**Status:** Ready for Implementation
**Estimate:** 6 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE4-004 (Sections 2-3)

**Planning References:**
- PRD v3.3: Section 4.2 (Weekly Performance Monitoring & Variance Tracking)
- Technical Architecture v3.3: Section 4.5 (Variance & Allocation APIs)
- Frontend Spec v3.3: Sections 3.5-3.6 (Sections 4-5 Design)

---

## Story

As a user,
I want to view weekly forecast vs actual performance with variance highlighting and see the replenishment queue for upcoming shipments,
So that I can monitor forecast accuracy and manage inventory replenishment.

**Business Value:** These sections enable in-season performance monitoring - the core operational use case. Users can see forecast vs actuals week-by-week, identify when variance exceeds thresholds (>20%), and manage replenishment shipments. Without this, the system is just a static forecast with no operational value.

**Epic Context:** This is Story 5 of 9 in Phase 4. After viewing the forecast (Story 4), users need to monitor weekly performance and manage replenishment. These sections integrate with the Inventory Agent's allocation and replenishment planning outputs.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ GET /api/variance/{id}/week/{week} endpoint tested with Postman
2. ✅ GET /api/allocations/{id} endpoint tested with Postman
3. ✅ Components use forecastId from Context (not props)
4. ✅ Components use parameters from Context for forecast_horizon_weeks
5. ✅ Components wait for workflowComplete before fetching data
6. ✅ Section 4 (Weekly Chart) displays forecast vs actuals
7. ✅ Variance highlighting works (>20% = red, 10-20% = yellow, <10% = green)
8. ✅ Interactive table shows week-by-week breakdown
9. ✅ Row expansion shows store-level variance
10. ✅ Section 5 (Replenishment Queue) displays upcoming shipments
11. ✅ DC inventory warnings display when low
12. ✅ Approve shipment button calls POST /api/approvals/replenishment
13. ✅ Approval success/error feedback displayed
14. ✅ Replenishment section hidden when strategy = "none" (conditional display)

### Data Validation & Error Handling

15. ✅ Allocation replenishment_strategy validated against Context parameters
16. ✅ 404 error handled if variance data not found
17. ✅ 404 error handled if allocation data not found
18. ✅ 500 and network errors handled with user-friendly messages
19. ✅ currentWeek calculated from season_start_date in Context

### Quality Requirements

20. ✅ Chart renders smoothly with Recharts
21. ✅ Variance colors update correctly based on thresholds
22. ✅ No console errors during data display
23. ✅ Test with different replenishment strategies (weekly, bi-weekly, none)
24. ✅ Loading states show while fetching data

### Accessibility

25. ✅ Chart has aria-label describing variance data
26. ✅ Variance color indicators include text labels (not color-only)
27. ✅ Row expansion accessible via keyboard (Enter/Space)
28. ✅ Row expansion has aria-expanded attribute
29. ✅ Approve button has aria-label with week and quantity
30. ✅ DC warnings have role="alert" for screen readers

---

## Tasks

### Task 1: Test Backend Variance Endpoint with Postman

**Goal:** Verify variance endpoint returns correct week-by-week data.

**Subtasks:**
- [ ] Complete workflow (PHASE4-003) to get forecast_id
- [ ] Open Postman and create request:
  - Method: GET
  - URL: `http://localhost:8000/api/variance/{forecast_id}/week/5`
  - (Test with week 5 since mock data has >20% variance there)

- [ ] Verify response (200 OK):
  ```json
  {
    "forecast_id": "fc_abc123",
    "week_number": 5,
    "forecasted_cumulative": 3570,
    "actual_cumulative": 4680,
    "variance_pct": 31.1,
    "threshold_exceeded": true,
    "action_taken": "re-forecast_triggered",
    "store_level_variance": [
      {
        "store_id": "S01",
        "store_name": "Manhattan Flagship",
        "forecasted": 285,
        "actual": 374,
        "variance_pct": 31.2
      },
      // ... 49 more stores
    ]
  }
  ```

- [ ] Test multiple weeks (1-12):
  ```bash
  GET /api/variance/fc_abc123/week/1  # Should have low variance (<10%)
  GET /api/variance/fc_abc123/week/3  # Should have medium variance (10-20%)
  GET /api/variance/fc_abc123/week/5  # Should have high variance (>20%)
  ```

**Validation:**
- Week 5 has variance >20% (threshold_exceeded: true)
- Other weeks have varying variance levels
- Store-level variance included for all 50 stores
- Cumulative values increase week-over-week

---

### Task 2: Test Backend Allocations Endpoint with Postman

**Goal:** Verify allocation endpoint returns replenishment plan.

**Subtasks:**
- [ ] Open Postman and create request:
  - Method: GET
  - URL: `http://localhost:8000/api/allocations/{forecast_id}`

- [ ] Verify response (200 OK):
  ```json
  {
    "allocation_id": "al_abc123",
    "forecast_id": "fc_abc123",
    "manufacturing_order": 10000,
    "safety_stock_pct": 0.25,
    "dc_holdback_pct": 0.45,
    "replenishment_strategy": "weekly",
    "initial_allocation_total": 5500,
    "dc_holdback_total": 4500,
    "store_allocations": [
      {
        "store_id": "S01",
        "cluster_id": "Fashion_Forward",
        "season_total": 800,
        "initial_allocation": 440,
        "dc_holdback": 360,
        "current_inventory": 120,
        "weeks_of_supply": 1.7
      },
      // ... 49 more stores
    ],
    "replenishment_plan": [
      {
        "week_number": 2,
        "shipments": [
          {
            "store_id": "S01",
            "quantity": 180,
            "reason": "replenish_to_forecast"
          },
          // ... more stores
        ],
        "total_shipped": 1200,
        "dc_remaining": 3300
      },
      // ... weeks 3-12
    ],
    "dc_inventory_warnings": [
      {
        "week_number": 10,
        "dc_remaining": 450,
        "message": "DC inventory low - only 450 units remaining",
        "severity": "warning"
      }
    ]
  }
  ```

- [ ] Test with different replenishment strategies:

  **Test Case 1: replenishment_strategy = "none"**
  - Expected: `replenishment_plan: []` (empty array)
  - Expected: `initial_allocation_total: 10000` (100% allocated)
  - Expected: `dc_holdback_total: 0`

  **Test Case 2: replenishment_strategy = "weekly"**
  - Expected: `replenishment_plan` has entries for weeks 2-12
  - Expected: `dc_holdback_total > 0`

  **Test Case 3: replenishment_strategy = "bi-weekly"**
  - Expected: `replenishment_plan` has entries for weeks 2, 4, 6, 8, 10, 12 only

**Validation:**
- Response matches replenishment_strategy from parameters
- Replenishment plan adapts correctly
- DC warnings appear when inventory low

---

### Task 3: Create TypeScript Types for Variance and Allocation

**Subtasks:**
- [ ] Create `frontend/src/types/variance.ts`:
  ```typescript
  export interface StoreVariance {
    store_id: string;
    store_name: string;
    forecasted: number;
    actual: number;
    variance_pct: number;
  }

  export interface WeeklyVariance {
    forecast_id: string;
    week_number: number;
    forecasted_cumulative: number;
    actual_cumulative: number;
    variance_pct: number;
    threshold_exceeded: boolean;
    action_taken: string | null;
    store_level_variance: StoreVariance[];
  }
  ```

- [ ] Create `frontend/src/types/allocation.ts`:
  ```typescript
  export interface StoreAllocation {
    store_id: string;
    cluster_id: string;
    season_total: number;
    initial_allocation: number;
    dc_holdback: number;
    current_inventory: number;
    weeks_of_supply: number;
  }

  export interface ReplenishmentShipment {
    store_id: string;
    quantity: number;
    reason: string;
  }

  export interface WeeklyReplenishment {
    week_number: number;
    shipments: ReplenishmentShipment[];
    total_shipped: number;
    dc_remaining: number;
  }

  export interface DCInventoryWarning {
    week_number: number;
    dc_remaining: number;
    message: string;
    severity: "info" | "warning" | "critical";
  }

  export interface AllocationPlan {
    allocation_id: string;
    forecast_id: string;
    manufacturing_order: number;
    safety_stock_pct: number;
    dc_holdback_pct: number;
    replenishment_strategy: "none" | "weekly" | "bi-weekly";
    initial_allocation_total: number;
    dc_holdback_total: number;
    store_allocations: StoreAllocation[];
    replenishment_plan: WeeklyReplenishment[];
    dc_inventory_warnings: DCInventoryWarning[];
  }
  ```

**Validation:**
- TypeScript compiles without errors
- Types match backend responses

---

### Task 4: Create API Services for Variance and Allocation

**Subtasks:**
- [ ] Create `frontend/src/services/variance-service.ts`:
  ```typescript
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';
  import type { WeeklyVariance } from '@/types/variance';

  export class VarianceService {
    static async getWeeklyVariance(
      forecastId: string,
      weekNumber: number
    ): Promise<WeeklyVariance> {
      return ApiClient.get<WeeklyVariance>(
        API_ENDPOINTS.VARIANCE_GET(forecastId, weekNumber)
      );
    }

    static async getAllWeeks(forecastId: string, totalWeeks: number): Promise<WeeklyVariance[]> {
      const promises = Array.from({ length: totalWeeks }, (_, i) =>
        this.getWeeklyVariance(forecastId, i + 1)
      );
      return Promise.all(promises);
    }
  }
  ```

- [ ] Create `frontend/src/services/allocation-service.ts`:
  ```typescript
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';
  import type { AllocationPlan } from '@/types/allocation';

  export class AllocationService {
    static async getAllocation(forecastId: string): Promise<AllocationPlan> {
      return ApiClient.get<AllocationPlan>(
        API_ENDPOINTS.ALLOCATIONS_GET(forecastId)
      );
    }
  }
  ```

**Validation:**
- Services call backend successfully
- Error handling works

---

### Task 5: Create currentWeek Calculation Utility

**Goal:** Calculate current week number from season_start_date for reactive updates.

**Subtasks:**
- [ ] Create utility function to calculate current week:
  ```typescript
  // frontend/src/utils/date-utils.ts
  export function getCurrentWeekNumber(seasonStartDate: string): number {
    const startDate = new Date(seasonStartDate);
    const today = new Date();

    // Calculate days elapsed since season start
    const daysElapsed = Math.floor((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

    // Convert to weeks (1-indexed)
    const weekNumber = Math.floor(daysElapsed / 7) + 1;

    // Clamp to valid range (1 to forecast_horizon_weeks)
    return Math.max(1, weekNumber);
  }
  ```

- [ ] Add currentWeek to ParameterContext (optional, or calculate in components):
  ```typescript
  // Option A: Add to Context
  const currentWeek = parameters?.season_start_date
    ? getCurrentWeekNumber(parameters.season_start_date)
    : 1;

  // Option B: Calculate in each component as needed
  // (Simpler, avoids Context updates)
  ```

**Recommendation:** Calculate in components as needed (Option B) to avoid unnecessary Context complexity.

**Validation:**
- Function returns correct week number based on date math
- Returns 1 if season hasn't started yet
- Used in ReplenishmentQueue to show "current week" context

---

### Task 6: Update WeeklyPerformanceChart Component (Section 4)

**Subtasks:**
- [ ] Locate `frontend/src/components/WeeklyPerformanceChart/WeeklyPerformanceChart.tsx`

- [ ] Update to use Context instead of props:
  ```typescript
  import { VarianceService } from '@/services/variance-service';
  import { useParameters } from '@/contexts/ParameterContext';
  import type { WeeklyVariance } from '@/types/variance';

  export function WeeklyPerformanceChart() {
    const { forecastId, parameters, workflowComplete } = useParameters();
    const [weeklyData, setWeeklyData] = useState<WeeklyVariance[]>([]);
    const [selectedWeek, setSelectedWeek] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      // Wait for workflow completion and validate parameters
      if (!workflowComplete || !forecastId || !parameters) return;

      const fetchVarianceData = async () => {
        setIsLoading(true);
        setError(null);

        try {
          const data = await VarianceService.getAllWeeks(
            forecastId,
            parameters.forecast_horizon_weeks
          );
          setWeeklyData(data);
        } catch (err) {
          console.error('Failed to fetch variance data:', err);

          // Handle specific error types
          let errorMessage = 'Failed to load variance data';
          if (err.status === 404) {
            errorMessage = 'Variance data not found. Workflow may not have completed.';
          } else if (err.status === 500) {
            errorMessage = 'Server error loading variance data.';
          } else if (err.status === 0) {
            errorMessage = 'Cannot connect to backend.';
          }

          setError(errorMessage);
        } finally {
          setIsLoading(false);
        }
      };

      fetchVarianceData();
    }, [workflowComplete, forecastId, parameters]);

    if (!forecastId) {
      return (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-gray-500">
              Complete workflow to view weekly performance
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
              <p>Loading variance data...</p>
            </div>
          </CardContent>
        </Card>
      );
    }

    if (error || weeklyData.length === 0) {
      return (
        <Card>
          <CardContent className="py-8">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error || 'No variance data available'}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      );
    }

    // Chart data preparation
    const chartData = weeklyData.map(week => ({
      week: week.week_number,
      forecast: week.forecasted_cumulative,
      actual: week.actual_cumulative,
      variance_pct: week.variance_pct,
    }));

    return (
      <Card>
        <CardHeader>
          <CardTitle>Weekly Performance - Forecast vs Actuals</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Recharts ComposedChart */}
          <div role="img" aria-label={`Weekly performance chart showing forecast vs actual sales over ${parameters.forecast_horizon_weeks} weeks`}>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" label={{ value: 'Week', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Units', angle: -90, position: 'insideLeft' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="forecast"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Forecast (Cumulative)"
                />
                <Bar
                  dataKey="actual"
                  fill="#10b981"
                  name="Actual (Cumulative)"
                  opacity={0.8}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Interactive Variance Table */}
          <div className="mt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Week</TableHead>
                  <TableHead>Forecast</TableHead>
                  <TableHead>Actual</TableHead>
                  <TableHead>Variance</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {weeklyData.map(week => (
                  <>
                    <TableRow key={week.week_number}>
                      <TableCell className="font-medium">Week {week.week_number}</TableCell>
                      <TableCell>{week.forecasted_cumulative.toLocaleString()}</TableCell>
                      <TableCell>{week.actual_cumulative.toLocaleString()}</TableCell>
                      <TableCell>
                        <span className={
                          week.variance_pct > 20 ? 'text-red-600 font-semibold' :
                          week.variance_pct > 10 ? 'text-yellow-600 font-semibold' :
                          'text-green-600'
                        }>
                          {week.variance_pct > 0 ? '+' : ''}{week.variance_pct.toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={
                          week.variance_pct > 20 ? 'destructive' :
                          week.variance_pct > 10 ? 'warning' : 'success'
                        }>
                          {/* Include text labels, not just color indicators */}
                          {week.variance_pct > 20 ? 'High Variance' :
                           week.variance_pct > 10 ? 'Medium Variance' : 'Low Variance'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedWeek(
                            selectedWeek === week.week_number ? null : week.week_number
                          )}
                          aria-expanded={selectedWeek === week.week_number}
                          aria-controls={`week-${week.week_number}-details`}
                          aria-label={`${selectedWeek === week.week_number ? 'Collapse' : 'Expand'} store-level variance for Week ${week.week_number}`}
                        >
                          {selectedWeek === week.week_number ? <ChevronUp /> : <ChevronDown />}
                        </Button>
                      </TableCell>
                    </TableRow>

                    {/* Store-Level Variance (Expandable) */}
                    {selectedWeek === week.week_number && (
                      <TableRow>
                        <TableCell colSpan={6} className="bg-gray-50">
                          <div className="py-4" id={`week-${week.week_number}-details`}>
                            <h4 className="font-semibold mb-2">Store-Level Variance - Week {week.week_number}</h4>
                            <div className="max-h-60 overflow-y-auto">
                              <Table>
                                <TableHeader>
                                  <TableRow>
                                    <TableHead>Store</TableHead>
                                    <TableHead>Forecast</TableHead>
                                    <TableHead>Actual</TableHead>
                                    <TableHead>Variance</TableHead>
                                  </TableRow>
                                </TableHeader>
                                <TableBody>
                                  {week.store_level_variance.map(store => (
                                    <TableRow key={store.store_id}>
                                      <TableCell>{store.store_name}</TableCell>
                                      <TableCell>{store.forecasted}</TableCell>
                                      <TableCell>{store.actual}</TableCell>
                                      <TableCell className={
                                        store.variance_pct > 20 ? 'text-red-600' :
                                        store.variance_pct > 10 ? 'text-yellow-600' : 'text-green-600'
                                      }>
                                        {store.variance_pct > 0 ? '+' : ''}{store.variance_pct.toFixed(1)}%
                                      </TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    );
  }
  ```

**Validation:**
- Chart renders with forecast line and actual bars
- Variance highlighting works (red >20%, yellow 10-20%, green <10%)
- Table rows expand to show store-level variance
- Week 5 shows high variance (>20%)

---

### Task 7: Update ReplenishmentQueue Component (Section 5)

**Subtasks:**
- [ ] Locate `frontend/src/components/ReplenishmentQueue/ReplenishmentQueue.tsx`

- [ ] Update to use Context instead of props:
  ```typescript
  import { AllocationService } from '@/services/allocation-service';
  import { useParameters } from '@/contexts/ParameterContext';
  import { getCurrentWeekNumber } from '@/utils/date-utils';
  import type { AllocationPlan, WeeklyReplenishment } from '@/types/allocation';

  export function ReplenishmentQueue() {
    const { forecastId, parameters, workflowComplete } = useParameters();
    const [allocation, setAllocation] = useState<AllocationPlan | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isApprovingShipments, setIsApprovingShipments] = useState(false);
    const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);

    // Calculate current week from season_start_date
    const currentWeek = parameters?.season_start_date
      ? getCurrentWeekNumber(parameters.season_start_date)
      : 1;

    // Handle approval button click
    const handleApproveShipments = async () => {
      if (!forecastId) return;

      setIsApprovingShipments(true);
      setApprovalSuccess(null);

      try {
        // POST /api/approvals/replenishment
        await ApiClient.post('/api/approvals/replenishment', {
          forecast_id: forecastId,
          week_number: currentWeek,
        });

        setApprovalSuccess(`Week ${currentWeek} shipments approved successfully`);
      } catch (err) {
        console.error('Failed to approve shipments:', err);

        let errorMessage = 'Failed to approve shipments';
        if (err.status === 404) {
          errorMessage = 'Replenishment plan not found.';
        } else if (err.status === 500) {
          errorMessage = 'Server error approving shipments.';
        } else if (err.status === 0) {
          errorMessage = 'Cannot connect to backend.';
        }

        setError(errorMessage);
      } finally {
        setIsApprovingShipments(false);
      }
    };

    useEffect(() => {
      // Wait for workflow completion and validate parameters
      if (!workflowComplete || !forecastId || !parameters) return;

      const fetchAllocation = async () => {
        setIsLoading(true);
        setError(null);

        try {
          const data = await AllocationService.getAllocation(forecastId);

          // Validate replenishment strategy matches parameters
          if (parameters && data.replenishment_strategy !== parameters.replenishment_strategy) {
            console.warn(
              `Replenishment strategy mismatch: expected ${parameters.replenishment_strategy}, got ${data.replenishment_strategy}`
            );
          }

          setAllocation(data);
        } catch (err) {
          console.error('Failed to fetch allocation:', err);

          // Handle specific error types
          let errorMessage = 'Failed to load replenishment data';
          if (err.status === 404) {
            errorMessage = 'Allocation data not found. Workflow may not have completed.';
          } else if (err.status === 500) {
            errorMessage = 'Server error loading allocation data.';
          } else if (err.status === 0) {
            errorMessage = 'Cannot connect to backend.';
          }

          setError(errorMessage);
        } finally {
          setIsLoading(false);
        }
      };

      fetchAllocation();
    }, [workflowComplete, forecastId, parameters]);

    if (!forecastId) {
      return (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-gray-500">
              Complete workflow to view replenishment queue
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
              <p>Loading replenishment data...</p>
            </div>
          </CardContent>
        </Card>
      );
    }

    if (error || !allocation) {
      return (
        <Card>
          <CardContent className="py-8">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error || 'No replenishment data'}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      );
    }

    // Handle "none" replenishment strategy
    if (allocation.replenishment_strategy === 'none') {
      return (
        <Card>
          <CardContent className="py-8">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>No Replenishment</AlertTitle>
              <AlertDescription>
                All {allocation.manufacturing_order.toLocaleString()} units were allocated to stores at Week 0.
                No replenishment shipments planned.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      );
    }

    // Get current week's shipments
    const currentWeekShipments = allocation.replenishment_plan.find(
      plan => plan.week_number === currentWeek
    );

    return (
      <Card>
        <CardHeader>
          <CardTitle>Replenishment Queue - Week {currentWeek}</CardTitle>
          <p className="text-sm text-gray-600">
            Strategy: {allocation.replenishment_strategy} • DC Remaining: {currentWeekShipments?.dc_remaining.toLocaleString() || 0} units
          </p>
        </CardHeader>
        <CardContent>
          {/* Approval Success Message */}
          {approvalSuccess && (
            <Alert variant="success" className="mb-4" role="status">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{approvalSuccess}</AlertDescription>
            </Alert>
          )}

          {/* DC Inventory Warnings */}
          {allocation.dc_inventory_warnings.length > 0 && (
            <Alert variant="warning" className="mb-4" role="alert">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>DC Inventory Warning</AlertTitle>
              <AlertDescription>
                {allocation.dc_inventory_warnings[0].message}
              </AlertDescription>
            </Alert>
          )}

          {/* Current Week Shipments */}
          {currentWeekShipments ? (
            <>
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  Total to ship: <span className="font-semibold">{currentWeekShipments.total_shipped.toLocaleString()}</span> units to{' '}
                  <span className="font-semibold">{currentWeekShipments.shipments.length}</span> stores
                </p>
              </div>

              <div className="max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Store ID</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Reason</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentWeekShipments.shipments.map(shipment => (
                      <TableRow key={shipment.store_id}>
                        <TableCell className="font-medium">{shipment.store_id}</TableCell>
                        <TableCell>{shipment.quantity.toLocaleString()}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{shipment.reason.replace(/_/g, ' ')}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <div className="mt-4">
                <Button
                  onClick={handleApproveShipments}
                  disabled={isApprovingShipments}
                  aria-label={`Approve ${currentWeekShipments.total_shipped} units for Week ${currentWeek}`}
                >
                  {isApprovingShipments ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Approving...
                    </>
                  ) : (
                    'Approve Shipments'
                  )}
                </Button>
              </div>
            </>
          ) : (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                No shipments scheduled for Week {currentWeek}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  }
  ```

**Validation:**
- Uses Context instead of props for forecastId, parameters, workflowComplete
- Calculates currentWeek from season_start_date
- Validates replenishment strategy matches parameters
- Displays current week's shipments
- Shows "No replenishment" message when strategy = "none"
- DC warnings appear when inventory low (with role="alert")
- Approve button includes aria-label with week and quantity
- Approval success message displayed with role="status"
- Table scrolls when many shipments

---

### Task 8: Implement Approval Endpoint Service

**Goal:** Add service method for POST /api/approvals/replenishment

**Subtasks:**
- [ ] Create `frontend/src/services/approval-service.ts`:
  ```typescript
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';

  export interface ApprovalRequest {
    forecast_id: string;
    week_number: number;
  }

  export interface ApprovalResponse {
    approval_id: string;
    forecast_id: string;
    week_number: number;
    total_units_approved: number;
    stores_affected: number;
    approved_at: string;
    status: "approved";
  }

  export class ApprovalService {
    static async approveReplenishment(
      request: ApprovalRequest
    ): Promise<ApprovalResponse> {
      return ApiClient.post<ApprovalResponse>(
        API_ENDPOINTS.APPROVALS_REPLENISHMENT,
        request
      );
    }
  }
  ```

- [ ] Add endpoint to API_ENDPOINTS config:
  ```typescript
  // frontend/src/config/api.ts
  export const API_ENDPOINTS = {
    // ... existing endpoints
    APPROVALS_REPLENISHMENT: '/api/approvals/replenishment',
  };
  ```

- [ ] Test endpoint with Postman:
  - Method: POST
  - URL: `http://localhost:8000/api/approvals/replenishment`
  - Body:
    ```json
    {
      "forecast_id": "fc_abc123",
      "week_number": 2
    }
    ```
  - Expected Response (200 OK):
    ```json
    {
      "approval_id": "ap_abc123",
      "forecast_id": "fc_abc123",
      "week_number": 2,
      "total_units_approved": 1200,
      "stores_affected": 15,
      "approved_at": "2025-10-29T10:30:00Z",
      "status": "approved"
    }
    ```

**Validation:**
- POST endpoint returns approval confirmation
- Approval ID generated
- Success response includes approval details

---

## Testing Requirements

### Integration Tests
```typescript
describe('WeeklyPerformanceChart', () => {
  it('should display variance data for all weeks', async () => {
    render(<WeeklyPerformanceChart forecastId="fc_test" forecastHorizonWeeks={12} />);

    await waitFor(() => {
      expect(screen.getByText(/week 1/i)).toBeInTheDocument();
      expect(screen.getByText(/week 12/i)).toBeInTheDocument();
    });
  });

  it('should highlight high variance (>20%) in red', async () => {
    render(<WeeklyPerformanceChart forecastId="fc_test" forecastHorizonWeeks={12} />);

    await waitFor(() => {
      const week5Variance = screen.getByText('+31.1%');
      expect(week5Variance).toHaveClass('text-red-600');
    });
  });

  it('should expand store-level variance on click', async () => {
    render(<WeeklyPerformanceChart forecastId="fc_test" forecastHorizonWeeks={12} />);

    await waitFor(() => {
      const expandButton = screen.getAllByRole('button', { name: /chevron/i })[0];
      fireEvent.click(expandButton);
      expect(screen.getByText(/store-level variance/i)).toBeInTheDocument();
    });
  });
});

describe('ReplenishmentQueue', () => {
  it('should display current week shipments', async () => {
    render(<ReplenishmentQueue forecastId="fc_test" currentWeek={2} />);

    await waitFor(() => {
      expect(screen.getByText(/total to ship/i)).toBeInTheDocument();
    });
  });

  it('should show no replenishment message when strategy is none', async () => {
    render(<ReplenishmentQueue forecastId="fc_test_none" currentWeek={2} />);

    await waitFor(() => {
      expect(screen.getByText(/no replenishment/i)).toBeInTheDocument();
    });
  });
});
```

### Manual Testing Checklist
- [ ] Complete workflow to get forecast_id
- [ ] Verify Section 4 displays weekly performance chart
- [ ] Verify forecast line and actual bars render
- [ ] Verify Week 5 shows high variance (>20%, red)
- [ ] Verify other weeks show correct variance colors
- [ ] Click expand button on Week 5
- [ ] Verify store-level variance table displays
- [ ] Verify 50 stores listed with individual variances
- [ ] Verify Section 5 displays replenishment queue
- [ ] Test with replenishment_strategy = "weekly"
  - Verify shipments display for weeks 2-12
- [ ] Test with replenishment_strategy = "none"
  - Verify "No replenishment" message displays
- [ ] Verify DC warnings appear when inventory low
- [ ] Click "Approve Shipments" button
- [ ] Verify no console errors

---

## Dependencies

**Requires:**
- PHASE4-004 complete (forecast data available)
- Backend GET /api/variance/{id}/week/{week} functional
- Backend GET /api/allocations/{id} functional
- Mock agents return variance and allocation data

**Enables:**
- PHASE4-006 (Sections 6-7 need allocation data)

---

## Definition of Done

- [ ] GET /api/variance tested with Postman (all 12 weeks)
- [ ] GET /api/allocations tested with Postman
- [ ] POST /api/approvals/replenishment tested with Postman
- [ ] TypeScript types created (variance, allocation, approval)
- [ ] API services created (VarianceService, AllocationService, ApprovalService)
- [ ] currentWeek utility function created
- [ ] Components use Context (forecastId, parameters, workflowComplete) instead of props
- [ ] Components wait for workflowComplete before fetching data
- [ ] Category and strategy validation implemented
- [ ] Section 4 displays chart and table with data from Context
- [ ] Chart has aria-label for accessibility
- [ ] Variance highlighting works correctly (red >20%, yellow 10-20%, green <10%)
- [ ] Variance badges include text labels (not color-only)
- [ ] Store-level expansion works with aria-expanded and aria-controls
- [ ] Section 5 displays replenishment queue using Context
- [ ] currentWeek calculated from season_start_date
- [ ] Conditional display for "none" strategy works
- [ ] DC warnings display with role="alert"
- [ ] Approve button includes aria-label
- [ ] Approval success/error feedback displayed
- [ ] Approval button calls POST /api/approvals/replenishment
- [ ] 404, 500, and network errors handled
- [ ] All manual tests passing
- [ ] No console errors
- [ ] Accessibility requirements met (WCAG compliance)

---

## Time Tracking

- **Estimated:** 6 hours (updated from 5 hours)
  - +1 hour for Context integration, accessibility, and approval endpoint
- **Actual:** ___ hours

---

## Related Stories

- **Depends On:** PHASE4-004
- **Blocks:** PHASE4-006
- **Related:** PHASE4-008 (Integration Tests)

---

**Status:** ⏳ Ready for Implementation
**Assigned To:** Dev Team
**Priority:** P1 (High)
**Created:** 2025-10-29
**Updated:** 2025-10-29
