# PHASE4-006: Sections 6-7 - Markdown Decision + Performance Metrics

**Story ID:** PHASE4-006
**Story Name:** Integrate Sections 6-7 - Markdown Decision Analysis + Performance Metrics Dashboard
**Phase:** Phase 4 - Frontend/Backend Integration
**Dependencies:** PHASE4-001, PHASE4-002, PHASE4-003, PHASE4-005
**Estimated Effort:** 6 hours
**Assigned To:** Developer (Frontend + Backend Integration)
**Status:** Not Started

---

## User Story

**As a** retail planner using the Multi-Agent Forecasting System,
**I want** to see markdown recommendations and performance metrics displayed in Sections 6 and 7,
**So that** I can evaluate end-of-season pricing strategies and monitor overall forecast accuracy.

---

## Context & Background

### What This Story Covers

This story integrates the final two analytical sections of the dashboard:

1. **Section 6: Markdown Decision** - Displays Pricing Agent's markdown recommendations
   - Only visible when `markdown_checkpoint_week` parameter is set
   - Shows Gap × Elasticity formula results
   - Provides markdown decision with justification
   - Displays expected impact and risk assessment

2. **Section 7: Performance Metrics** - Aggregates system-wide performance indicators
   - MAPE (Mean Absolute Percentage Error) from forecast accuracy
   - Average variance across all stores
   - Sell-through percentage at checkpoint week
   - System health indicators

### Why Section 6 is Conditional

Markdown analysis only applies when:
- User specified a `markdown_checkpoint_week` (e.g., week 6 of 12)
- User specified a `markdown_threshold` (e.g., 0.40)
- System has reached that checkpoint week in simulation

If `markdown_checkpoint_week === null`, Section 6 should not display at all.

### Backend Endpoints

**Section 6: Markdown Decision**
- **Endpoint:** `GET /api/markdowns/{workflow_id}`
- **Returns:** MarkdownAnalysis model with gap analysis and recommendation

**Section 7: Performance Metrics**
- **Aggregation from multiple endpoints:**
  - `GET /api/forecasts/{workflow_id}` → total_demand MAPE
  - `GET /api/variance/{workflow_id}/summary` → average variance
  - `GET /api/allocations/{workflow_id}` → sell-through calculation
  - `GET /api/markdowns/{workflow_id}` → markdown success rate (if applicable)

### Mock Agent Behavior (Phase 4)

Since we haven't built the Pricing Agent yet, mock responses must:
1. Return parameter-aware markdown recommendations
2. Calculate Gap × Elasticity with realistic values
3. Provide justification based on sell-through vs. threshold
4. Return null for Section 6 if `markdown_checkpoint_week` is null

---

## Acceptance Criteria

### Section 6: Markdown Decision

- [ ] **AC1:** Section 6 only displays when `markdown_checkpoint_week !== null`
- [ ] **AC2:** GET /api/markdowns/{id} is called successfully when markdown applies
- [ ] **AC3:** Gap × Elasticity formula is displayed:
  - Gap = (markdown_threshold - actual_sell_through) e.g., (0.40 - 0.35 = 0.05)
  - Elasticity coefficient displayed (e.g., -1.5)
  - Impact calculation shown (e.g., 0.05 × -1.5 = -0.075 → -7.5% sales impact)
- [ ] **AC4:** Markdown recommendation is displayed:
  - Recommended markdown percentage (e.g., 20%)
  - Expected outcome (e.g., "Boost sell-through from 35% to 48%")
  - Risk assessment (e.g., "Margin reduction: $15,000")
- [ ] **AC5:** Justification text adapts to sell-through vs. threshold comparison
- [ ] **AC6:** Section 6 is hidden/collapsed if markdown_checkpoint_week is null
- [ ] **AC7:** Frontend handles 404 gracefully if markdown endpoint returns no data

### Section 7: Performance Metrics

- [ ] **AC8:** GET /api/forecasts/{id} is called to extract MAPE
- [ ] **AC9:** GET /api/variance/{id}/summary is called to get average variance
- [ ] **AC10:** Sell-through percentage is calculated from allocations data
- [ ] **AC11:** Four key metrics are displayed:
  - Forecast MAPE (e.g., "12.5%") with color coding (green <15%, yellow 15-25%, red >25%)
  - Average Variance (e.g., "8.2%") with color coding (green <10%, yellow 10-20%, red >20%)
  - Sell-Through % (e.g., "65%") with color coding (green >60%, yellow 40-60%, red <40%)
  - System Status (e.g., "Healthy" or "Needs Attention")
- [ ] **AC12:** System Status badge aggregates all metrics:
  - "Healthy" (green) if MAPE <15%, variance <10%, sell-through >60%
  - "Moderate" (yellow) if 1-2 metrics in yellow range
  - "Needs Attention" (red) if any metric in red range
- [ ] **AC13:** Each metric has a tooltip explaining what it measures
- [ ] **AC14:** Section 7 displays even if markdown is not applicable

### Mock Agent Integration

- [ ] **AC15:** Mock Pricing Agent returns parameter-aware markdown data:
  - Gap calculation based on actual sell-through from allocations
  - Realistic elasticity coefficient (-1.2 to -2.0 range)
  - Markdown recommendation adapts to gap size
- [ ] **AC16:** Mock returns null/404 if markdown_checkpoint_week is null
- [ ] **AC17:** Performance metrics aggregate real data from Forecast/Inventory Agents

### Testing

- [ ] **AC18:** Backend markdown endpoint tested in Postman:
  - Test Case 1: workflow_id with markdown_checkpoint_week set
  - Test Case 2: workflow_id with markdown_checkpoint_week = null
  - Test Case 3: Invalid workflow_id (should return 404)
- [ ] **AC19:** Backend variance summary endpoint tested in Postman
- [ ] **AC20:** Frontend Section 6 manually tested with markdown enabled/disabled
- [ ] **AC21:** Frontend Section 7 metrics calculation verified with sample data
- [ ] **AC22:** Color coding thresholds validated for all metrics
- [ ] **AC23:** System Status badge logic tested with edge cases

---

## Tasks

### Task 1: Test Backend Markdown Endpoint in Postman

**Objective:** Verify GET /api/markdowns/{workflow_id} returns correct data structure and handles null cases.

**Subtasks:**

1. **Test Case 1: Markdown Analysis with Checkpoint Week Set**
   - User Input: "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback. Markdown checkpoint at week 6 with 40% threshold."
   - Workflow ID: Extract from POST /api/parameters/extract response
   - Request: GET http://localhost:8000/api/markdowns/{workflow_id}
   - Expected Response:
     ```json
     {
       "workflow_id": "wf_abc123",
       "markdown_checkpoint_week": 6,
       "markdown_threshold": 0.40,
       "actual_sell_through": 0.35,
       "gap": 0.05,
       "elasticity_coefficient": -1.5,
       "expected_impact": -0.075,
       "recommended_markdown_percentage": 0.20,
       "expected_sell_through_after_markdown": 0.48,
       "expected_margin_reduction": 15000,
       "decision": "APPLY_MARKDOWN",
       "justification": "Sell-through at 35% is below 40% threshold by 5%. A 20% markdown could boost sell-through to 48%, reducing excess inventory risk.",
       "risk_assessment": "Margin reduction of $15,000 acceptable to avoid deeper clearance costs.",
       "timestamp": "2025-01-15T10:30:00Z"
     }
     ```
   - Validation:
     - gap = markdown_threshold - actual_sell_through
     - expected_impact = gap × elasticity_coefficient
     - recommended_markdown adapts to gap size (gap <0.05 → 10%, 0.05-0.10 → 20%, >0.10 → 30%)
     - justification explains reasoning

2. **Test Case 2: No Markdown Analysis (Checkpoint Week = null)**
   - User Input: "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback."
   - Workflow ID: Extract from response
   - Request: GET http://localhost:8000/api/markdowns/{workflow_id}
   - Expected Response: 404 Not Found or:
     ```json
     {
       "workflow_id": "wf_def456",
       "markdown_checkpoint_week": null,
       "decision": "NOT_APPLICABLE",
       "justification": "No markdown checkpoint week specified in parameters."
     }
     ```
   - Validation:
     - Frontend should handle this gracefully by hiding Section 6

3. **Test Case 3: Markdown Not Needed (Sell-Through Above Threshold)**
   - User Input: "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback. Markdown checkpoint at week 6 with 40% threshold."
   - Mock actual_sell_through to 0.50 (above 0.40 threshold)
   - Request: GET http://localhost:8000/api/markdowns/{workflow_id}
   - Expected Response:
     ```json
     {
       "workflow_id": "wf_ghi789",
       "markdown_checkpoint_week": 6,
       "markdown_threshold": 0.40,
       "actual_sell_through": 0.50,
       "gap": -0.10,
       "elasticity_coefficient": -1.5,
       "recommended_markdown_percentage": 0.0,
       "decision": "NO_MARKDOWN_NEEDED",
       "justification": "Sell-through at 50% exceeds 40% threshold. No markdown required.",
       "risk_assessment": "Continue monitoring. Current pace is healthy.",
       "timestamp": "2025-01-15T10:30:00Z"
     }
     ```
   - Validation:
     - decision = "NO_MARKDOWN_NEEDED"
     - recommended_markdown_percentage = 0
     - Frontend should display "No markdown needed" message

4. **Test Case 4: Invalid Workflow ID**
   - Request: GET http://localhost:8000/api/markdowns/invalid_id_xyz
   - Expected Response: 404 Not Found
     ```json
     {
       "detail": "Workflow with ID 'invalid_id_xyz' not found"
     }
     ```
   - Validation:
     - Frontend displays user-friendly error: "Markdown data not available"

**Postman Collection Setup:**
- Create "PHASE4-006 Markdown Tests" folder
- Save all 4 test cases with assertions
- Export collection to `docs/04_MVP_Development/implementation/phase_4_integration/postman/`

**Validation Checklist:**
- [ ] Test Case 1 returns valid markdown analysis with all fields
- [ ] gap calculation is correct (threshold - actual)
- [ ] elasticity_coefficient is realistic (-1.2 to -2.0)
- [ ] recommended_markdown adapts to gap size
- [ ] Test Case 2 returns 404 or NOT_APPLICABLE when checkpoint week is null
- [ ] Test Case 3 correctly identifies when markdown is not needed
- [ ] Test Case 4 returns 404 for invalid workflow IDs

---

### Task 2: Test Backend Variance Summary Endpoint in Postman

**Objective:** Verify GET /api/variance/{workflow_id}/summary aggregates variance correctly.

**Subtasks:**

1. **Test Case 1: Variance Summary for Valid Workflow**
   - User Input: "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback."
   - Start workflow, extract workflow_id
   - Request: GET http://localhost:8000/api/variance/{workflow_id}/summary
   - Expected Response:
     ```json
     {
       "workflow_id": "wf_abc123",
       "average_variance_percentage": 8.2,
       "max_variance_percentage": 22.5,
       "min_variance_percentage": -5.3,
       "stores_above_threshold": 12,
       "total_stores": 50,
       "high_variance_stores": [
         {
           "store_id": "S023",
           "store_name": "Downtown LA",
           "variance_percentage": 22.5
         },
         {
           "store_id": "S041",
           "store_name": "Brooklyn Center",
           "variance_percentage": 19.8
         }
       ],
       "timestamp": "2025-01-15T10:30:00Z"
     }
     ```
   - Validation:
     - average_variance_percentage is within -50% to +100% range
     - stores_above_threshold counts stores with |variance| > 20%
     - high_variance_stores lists top 3 problem stores

2. **Test Case 2: Invalid Workflow ID**
   - Request: GET http://localhost:8000/api/variance/invalid_id_xyz/summary
   - Expected Response: 404 Not Found
   - Validation:
     - Frontend handles gracefully with fallback message

**Postman Collection Setup:**
- Add to "PHASE4-006 Variance Summary Tests"
- Save test cases with assertions

**Validation Checklist:**
- [ ] Average variance is calculated correctly
- [ ] High variance stores are sorted by absolute variance
- [ ] stores_above_threshold count matches threshold of 20%
- [ ] 404 returns for invalid workflow IDs

---

### Task 3: Create Frontend MarkdownService

**Objective:** Create service to fetch markdown analysis from backend.

**File:** `src/services/markdownService.ts`

**Implementation:**

```typescript
import { ApiClient } from './apiClient';
import { API_ENDPOINTS } from '../config/api.config';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface MarkdownAnalysis {
  workflow_id: string;
  markdown_checkpoint_week: number | null;
  markdown_threshold: number | null;
  actual_sell_through: number;
  gap: number;
  elasticity_coefficient: number;
  expected_impact: number;
  recommended_markdown_percentage: number;
  expected_sell_through_after_markdown: number;
  expected_margin_reduction: number;
  decision: 'APPLY_MARKDOWN' | 'NO_MARKDOWN_NEEDED' | 'NOT_APPLICABLE';
  justification: string;
  risk_assessment: string;
  timestamp: string;
}

// ============================================================================
// MARKDOWN SERVICE
// ============================================================================

export class MarkdownService {
  /**
   * Fetch markdown analysis for a specific workflow
   * @param workflowId - The workflow ID to fetch markdown analysis for
   * @returns Promise<MarkdownAnalysis | null>
   * @throws ApiError if request fails (404 means markdown not applicable)
   */
  static async getMarkdownAnalysis(
    workflowId: string
  ): Promise<MarkdownAnalysis | null> {
    try {
      const response = await ApiClient.get<MarkdownAnalysis>(
        API_ENDPOINTS.MARKDOWNS.replace('{id}', workflowId)
      );

      // If decision is NOT_APPLICABLE, return null to hide Section 6
      if (response.decision === 'NOT_APPLICABLE') {
        return null;
      }

      return response;
    } catch (error: any) {
      // 404 means markdown checkpoint week was not set - this is normal
      if (error.status === 404) {
        console.log('Markdown analysis not applicable for this workflow');
        return null;
      }

      // Other errors should be thrown
      throw error;
    }
  }

  /**
   * Format markdown percentage for display
   * @param percentage - Decimal markdown percentage (e.g., 0.20)
   * @returns Formatted string (e.g., "20%")
   */
  static formatMarkdownPercentage(percentage: number): string {
    return `${(percentage * 100).toFixed(0)}%`;
  }

  /**
   * Format sell-through percentage for display
   * @param sellThrough - Decimal sell-through (e.g., 0.35)
   * @returns Formatted string (e.g., "35%")
   */
  static formatSellThrough(sellThrough: number): string {
    return `${(sellThrough * 100).toFixed(1)}%`;
  }

  /**
   * Format currency for display
   * @param amount - Dollar amount (e.g., 15000)
   * @returns Formatted string (e.g., "$15,000")
   */
  static formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  /**
   * Get badge color for markdown decision
   * @param decision - Markdown decision type
   * @returns Tailwind color class
   */
  static getDecisionBadgeColor(
    decision: 'APPLY_MARKDOWN' | 'NO_MARKDOWN_NEEDED' | 'NOT_APPLICABLE'
  ): string {
    switch (decision) {
      case 'APPLY_MARKDOWN':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'NO_MARKDOWN_NEEDED':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'NOT_APPLICABLE':
        return 'bg-gray-100 text-gray-600 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-300';
    }
  }

  /**
   * Get human-readable decision label
   * @param decision - Markdown decision type
   * @returns Display label
   */
  static getDecisionLabel(
    decision: 'APPLY_MARKDOWN' | 'NO_MARKDOWN_NEEDED' | 'NOT_APPLICABLE'
  ): string {
    switch (decision) {
      case 'APPLY_MARKDOWN':
        return 'Markdown Recommended';
      case 'NO_MARKDOWN_NEEDED':
        return 'No Markdown Needed';
      case 'NOT_APPLICABLE':
        return 'Not Applicable';
      default:
        return 'Unknown';
    }
  }
}
```

**Validation:**
- [ ] MarkdownAnalysis interface matches backend model
- [ ] getMarkdownAnalysis handles 404 gracefully (returns null)
- [ ] Formatting utilities return correct display strings
- [ ] Badge colors match decision types

---

### Task 4: Create Frontend PerformanceService

**Objective:** Aggregate performance metrics from multiple backend endpoints.

**File:** `src/services/performanceService.ts`

**Implementation:**

```typescript
import { ApiClient } from './apiClient';
import { API_ENDPOINTS } from '../config/api.config';
import { ForecastSummary } from './forecastService';
import { AllocationSummary } from './allocationService';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface VarianceSummary {
  workflow_id: string;
  average_variance_percentage: number;
  max_variance_percentage: number;
  min_variance_percentage: number;
  stores_above_threshold: number;
  total_stores: number;
  high_variance_stores: Array<{
    store_id: string;
    store_name: string;
    variance_percentage: number;
  }>;
  timestamp: string;
}

export interface PerformanceMetrics {
  forecast_mape: number; // From ForecastSummary
  average_variance: number; // From VarianceSummary
  sell_through_percentage: number; // Calculated from AllocationSummary
  system_status: 'Healthy' | 'Moderate' | 'Needs Attention';
  timestamp: string;
}

export type MetricStatus = 'healthy' | 'warning' | 'critical';

export interface MetricDetail {
  value: number;
  displayValue: string;
  status: MetricStatus;
  tooltip: string;
}

// ============================================================================
// PERFORMANCE SERVICE
// ============================================================================

export class PerformanceService {
  /**
   * Fetch variance summary from backend
   */
  static async getVarianceSummary(
    workflowId: string
  ): Promise<VarianceSummary> {
    return ApiClient.get<VarianceSummary>(
      API_ENDPOINTS.VARIANCE_SUMMARY.replace('{id}', workflowId)
    );
  }

  /**
   * Aggregate performance metrics from multiple endpoints
   * @param workflowId - The workflow ID
   * @returns Promise<PerformanceMetrics>
   */
  static async getPerformanceMetrics(
    workflowId: string
  ): Promise<PerformanceMetrics> {
    // Fetch data from multiple endpoints in parallel
    const [forecastSummary, varianceSummary, allocationSummary] =
      await Promise.all([
        ApiClient.get<ForecastSummary>(
          API_ENDPOINTS.FORECASTS.replace('{id}', workflowId)
        ),
        PerformanceService.getVarianceSummary(workflowId),
        ApiClient.get<AllocationSummary>(
          API_ENDPOINTS.ALLOCATIONS.replace('{id}', workflowId)
        ),
      ]);

    // Extract MAPE from forecast
    const forecast_mape = forecastSummary.mape_percentage;

    // Extract average variance
    const average_variance = varianceSummary.average_variance_percentage;

    // Calculate sell-through percentage
    const sell_through_percentage = PerformanceService.calculateSellThrough(
      allocationSummary
    );

    // Determine system status
    const system_status = PerformanceService.determineSystemStatus(
      forecast_mape,
      average_variance,
      sell_through_percentage
    );

    return {
      forecast_mape,
      average_variance,
      sell_through_percentage,
      system_status,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Calculate sell-through percentage from allocation data
   * @param allocationSummary - Allocation summary from backend
   * @returns Sell-through percentage (0-100)
   */
  private static calculateSellThrough(
    allocationSummary: AllocationSummary
  ): number {
    const totalAllocated = allocationSummary.total_units_allocated;
    const totalSold = allocationSummary.total_units_sold || 0;

    if (totalAllocated === 0) return 0;

    return (totalSold / totalAllocated) * 100;
  }

  /**
   * Determine overall system status based on metrics
   * @param mape - Forecast MAPE percentage
   * @param variance - Average variance percentage
   * @param sellThrough - Sell-through percentage
   * @returns System status
   */
  private static determineSystemStatus(
    mape: number,
    variance: number,
    sellThrough: number
  ): 'Healthy' | 'Moderate' | 'Needs Attention' {
    let criticalCount = 0;
    let warningCount = 0;

    // Check MAPE
    if (mape > 25) criticalCount++;
    else if (mape >= 15) warningCount++;

    // Check Variance
    if (Math.abs(variance) > 20) criticalCount++;
    else if (Math.abs(variance) >= 10) warningCount++;

    // Check Sell-Through
    if (sellThrough < 40) criticalCount++;
    else if (sellThrough <= 60) warningCount++;

    // Determine status
    if (criticalCount > 0) return 'Needs Attention';
    if (warningCount >= 2) return 'Moderate';
    return 'Healthy';
  }

  /**
   * Get metric status based on value and thresholds
   */
  static getMapeStatus(mape: number): MetricStatus {
    if (mape < 15) return 'healthy';
    if (mape <= 25) return 'warning';
    return 'critical';
  }

  static getVarianceStatus(variance: number): MetricStatus {
    const absVariance = Math.abs(variance);
    if (absVariance < 10) return 'healthy';
    if (absVariance <= 20) return 'warning';
    return 'critical';
  }

  static getSellThroughStatus(sellThrough: number): MetricStatus {
    if (sellThrough > 60) return 'healthy';
    if (sellThrough >= 40) return 'warning';
    return 'critical';
  }

  /**
   * Get badge color for system status
   */
  static getSystemStatusColor(
    status: 'Healthy' | 'Moderate' | 'Needs Attention'
  ): string {
    switch (status) {
      case 'Healthy':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'Moderate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Needs Attention':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-300';
    }
  }

  /**
   * Get metric badge color based on status
   */
  static getMetricStatusColor(status: MetricStatus): string {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50';
      case 'critical':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  }

  /**
   * Format metric details for display
   */
  static formatMetricDetails(
    metrics: PerformanceMetrics
  ): {
    mape: MetricDetail;
    variance: MetricDetail;
    sellThrough: MetricDetail;
  } {
    return {
      mape: {
        value: metrics.forecast_mape,
        displayValue: `${metrics.forecast_mape.toFixed(1)}%`,
        status: PerformanceService.getMapeStatus(metrics.forecast_mape),
        tooltip:
          'Mean Absolute Percentage Error - measures forecast accuracy. Lower is better.',
      },
      variance: {
        value: metrics.average_variance,
        displayValue: `${metrics.average_variance.toFixed(1)}%`,
        status: PerformanceService.getVarianceStatus(
          metrics.average_variance
        ),
        tooltip:
          'Average difference between forecast and actual demand across stores. Lower is better.',
      },
      sellThrough: {
        value: metrics.sell_through_percentage,
        displayValue: `${metrics.sell_through_percentage.toFixed(1)}%`,
        status: PerformanceService.getSellThroughStatus(
          metrics.sell_through_percentage
        ),
        tooltip:
          'Percentage of allocated inventory sold. Higher is better (>60% is healthy).',
      },
    };
  }
}
```

**Validation:**
- [ ] getPerformanceMetrics aggregates data from 3 endpoints in parallel
- [ ] calculateSellThrough handles division by zero
- [ ] determineSystemStatus logic is correct (1+ critical → Needs Attention)
- [ ] Status color utilities return correct Tailwind classes
- [ ] formatMetricDetails includes tooltips for all metrics

---

### Task 5: Build Section 6 - Markdown Decision Component

**Objective:** Create MarkdownDecision component to display Pricing Agent's recommendations.

**File:** `src/components/MarkdownDecision.tsx`

**Implementation:**

```typescript
import React, { useEffect, useState } from 'react';
import {
  MarkdownService,
  MarkdownAnalysis,
} from '../services/markdownService';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { AlertCircle, TrendingDown, DollarSign, Target } from 'lucide-react';

interface MarkdownDecisionProps {
  workflowId: string;
}

export const MarkdownDecision: React.FC<MarkdownDecisionProps> = ({
  workflowId,
}) => {
  const [markdownData, setMarkdownData] = useState<MarkdownAnalysis | null>(
    null
  );
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMarkdownAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await MarkdownService.getMarkdownAnalysis(workflowId);
        setMarkdownData(data);
      } catch (err: any) {
        console.error('Error fetching markdown analysis:', err);
        setError(
          err.message || 'Failed to load markdown analysis. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    if (workflowId) {
      fetchMarkdownAnalysis();
    }
  }, [workflowId]);

  // If markdown is not applicable (checkpoint week not set), don't render anything
  if (!loading && !markdownData) {
    return null; // Section 6 hidden
  }

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="w-5 h-5" />
            Section 6: Markdown Decision
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            <span className="ml-3 text-gray-600">
              Loading markdown analysis...
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!markdownData) {
    return null; // Should not reach here, but safety check
  }

  const {
    markdown_checkpoint_week,
    markdown_threshold,
    actual_sell_through,
    gap,
    elasticity_coefficient,
    expected_impact,
    recommended_markdown_percentage,
    expected_sell_through_after_markdown,
    expected_margin_reduction,
    decision,
    justification,
    risk_assessment,
  } = markdownData;

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="w-5 h-5" />
            Section 6: Markdown Decision
          </CardTitle>
          <Badge
            className={MarkdownService.getDecisionBadgeColor(decision)}
            variant="outline"
          >
            {MarkdownService.getDecisionLabel(decision)}
          </Badge>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Analysis at Week {markdown_checkpoint_week} of season (Threshold:{' '}
          {MarkdownService.formatSellThrough(markdown_threshold || 0)})
        </p>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Gap × Elasticity Formula */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <Target className="w-4 h-4" />
            Gap × Elasticity Analysis
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Gap Calculation */}
            <div className="bg-white rounded p-3 border border-blue-100">
              <div className="text-xs text-gray-600 mb-1">Gap</div>
              <div className="text-lg font-bold text-blue-900">
                {MarkdownService.formatSellThrough(gap)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Threshold ({MarkdownService.formatSellThrough(markdown_threshold || 0)}) - Actual (
                {MarkdownService.formatSellThrough(actual_sell_through)})
              </div>
            </div>

            {/* Elasticity Coefficient */}
            <div className="bg-white rounded p-3 border border-blue-100">
              <div className="text-xs text-gray-600 mb-1">
                Elasticity Coefficient
              </div>
              <div className="text-lg font-bold text-blue-900">
                {elasticity_coefficient.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Price sensitivity factor
              </div>
            </div>

            {/* Expected Impact */}
            <div className="bg-white rounded p-3 border border-blue-100">
              <div className="text-xs text-gray-600 mb-1">Expected Impact</div>
              <div className="text-lg font-bold text-blue-900">
                {MarkdownService.formatSellThrough(expected_impact)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Gap × Elasticity = {gap.toFixed(3)} × {elasticity_coefficient.toFixed(2)}
              </div>
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="border-t pt-4">
          <h4 className="font-semibold text-gray-900 mb-3">Recommendation</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Markdown Percentage */}
            <div className="flex items-center gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="bg-orange-100 rounded-full p-2">
                <TrendingDown className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <div className="text-xs text-gray-600">
                  Recommended Markdown
                </div>
                <div className="text-2xl font-bold text-orange-900">
                  {MarkdownService.formatMarkdownPercentage(
                    recommended_markdown_percentage
                  )}
                </div>
              </div>
            </div>

            {/* Expected Outcome */}
            <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="bg-green-100 rounded-full p-2">
                <Target className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <div className="text-xs text-gray-600">
                  Expected Sell-Through
                </div>
                <div className="text-2xl font-bold text-green-900">
                  {MarkdownService.formatSellThrough(
                    expected_sell_through_after_markdown
                  )}
                </div>
                <div className="text-xs text-gray-500">
                  Up from {MarkdownService.formatSellThrough(actual_sell_through)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Justification */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h5 className="font-semibold text-gray-900 mb-2">Justification</h5>
          <p className="text-sm text-gray-700">{justification}</p>
        </div>

        {/* Risk Assessment */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h5 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Risk Assessment
          </h5>
          <div className="text-sm text-yellow-800 mb-2">{risk_assessment}</div>

          {expected_margin_reduction > 0 && (
            <div className="flex items-center gap-2 text-yellow-900 font-semibold mt-3">
              <DollarSign className="w-4 h-4" />
              Estimated Margin Reduction:{' '}
              {MarkdownService.formatCurrency(expected_margin_reduction)}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
```

**Validation:**
- [ ] Component fetches markdown data on mount
- [ ] Section 6 is hidden when markdown_checkpoint_week is null
- [ ] Gap × Elasticity formula is displayed correctly
- [ ] Recommendation shows markdown percentage and expected sell-through
- [ ] Badge color adapts to decision type
- [ ] Loading and error states are handled
- [ ] Responsive layout works on mobile and desktop

---

### Task 6: Build Section 7 - Performance Metrics Component

**Objective:** Create PerformanceMetrics component to display system-wide KPIs.

**File:** `src/components/PerformanceMetrics.tsx`

**Implementation:**

```typescript
import React, { useEffect, useState } from 'react';
import {
  PerformanceService,
  PerformanceMetrics as PerformanceMetricsType,
  MetricDetail,
} from '../services/performanceService';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import {
  Activity,
  TrendingUp,
  BarChart3,
  CheckCircle2,
  AlertCircle,
  Info,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip';

interface PerformanceMetricsProps {
  workflowId: string;
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  workflowId,
}) => {
  const [metricsData, setMetricsData] =
    useState<PerformanceMetricsType | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPerformanceMetrics = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await PerformanceService.getPerformanceMetrics(
          workflowId
        );
        setMetricsData(data);
      } catch (err: any) {
        console.error('Error fetching performance metrics:', err);
        setError(
          err.message ||
            'Failed to load performance metrics. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    if (workflowId) {
      fetchPerformanceMetrics();
    }
  }, [workflowId]);

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Section 7: Performance Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            <span className="ml-3 text-gray-600">
              Loading performance metrics...
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!metricsData) {
    return null;
  }

  const { forecast_mape, average_variance, sell_through_percentage, system_status } =
    metricsData;

  const metricDetails =
    PerformanceService.formatMetricDetails(metricsData);

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Section 7: Performance Metrics
          </CardTitle>
          <Badge
            className={PerformanceService.getSystemStatusColor(system_status)}
            variant="outline"
          >
            System Status: {system_status}
          </Badge>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Overall system performance indicators
        </p>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Metric 1: Forecast MAPE */}
          <MetricCard
            icon={<BarChart3 className="w-5 h-5" />}
            label="Forecast MAPE"
            detail={metricDetails.mape}
          />

          {/* Metric 2: Average Variance */}
          <MetricCard
            icon={<TrendingUp className="w-5 h-5" />}
            label="Average Variance"
            detail={metricDetails.variance}
          />

          {/* Metric 3: Sell-Through % */}
          <MetricCard
            icon={<CheckCircle2 className="w-5 h-5" />}
            label="Sell-Through %"
            detail={metricDetails.sellThrough}
          />
        </div>

        {/* System Health Summary */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h5 className="font-semibold text-gray-900 mb-2">
            System Health Summary
          </h5>
          <div className="text-sm text-gray-700">
            {system_status === 'Healthy' && (
              <p>
                All metrics are within acceptable ranges. The forecasting
                system is performing well.
              </p>
            )}
            {system_status === 'Moderate' && (
              <p>
                Some metrics are showing moderate deviation. Monitor closely
                and consider adjustments.
              </p>
            )}
            {system_status === 'Needs Attention' && (
              <p>
                One or more metrics are outside acceptable ranges. Review
                forecast parameters and agent configurations.
              </p>
            )}
          </div>

          {/* Detailed Metric Thresholds */}
          <div className="mt-4 text-xs text-gray-600 space-y-1">
            <div>
              <strong>MAPE Thresholds:</strong> Green &lt;15% | Yellow 15-25% |
              Red &gt;25%
            </div>
            <div>
              <strong>Variance Thresholds:</strong> Green &lt;10% | Yellow
              10-20% | Red &gt;20%
            </div>
            <div>
              <strong>Sell-Through Thresholds:</strong> Green &gt;60% | Yellow
              40-60% | Red &lt;40%
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================================================
// METRIC CARD COMPONENT
// ============================================================================

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  detail: MetricDetail;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, detail }) => {
  const statusColorClass = PerformanceService.getMetricStatusColor(
    detail.status
  );

  return (
    <div
      className={`rounded-lg border p-4 transition-colors ${statusColorClass}`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium">{label}</span>
        </div>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <Info className="w-4 h-4 text-gray-400 hover:text-gray-600" />
            </TooltipTrigger>
            <TooltipContent>
              <p className="max-w-xs">{detail.tooltip}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <div className="text-3xl font-bold">{detail.displayValue}</div>

      <div className="mt-2 text-xs font-semibold uppercase">
        {detail.status === 'healthy' && 'Healthy'}
        {detail.status === 'warning' && 'Moderate'}
        {detail.status === 'critical' && 'Critical'}
      </div>
    </div>
  );
};
```

**Validation:**
- [ ] Component fetches performance metrics from 3 endpoints
- [ ] MAPE, Variance, and Sell-Through displayed correctly
- [ ] Color coding matches thresholds (green/yellow/red)
- [ ] System Status badge updates based on aggregation logic
- [ ] Tooltips explain each metric
- [ ] Responsive grid layout works on all screen sizes

---

### Task 7: Integrate Sections 6 & 7 into Dashboard

**Objective:** Add MarkdownDecision and PerformanceMetrics to main dashboard.

**File:** `src/pages/Dashboard.tsx` (or equivalent main page)

**Implementation:**

```typescript
import React from 'react';
import { ParameterGathering } from '../components/ParameterGathering';
import { AgentCards } from '../components/AgentCards';
import { ForecastSummary } from '../components/ForecastSummary';
import { ClusterCards } from '../components/ClusterCards';
import { WeeklyPerformanceChart } from '../components/WeeklyPerformanceChart';
import { ReplenishmentQueue } from '../components/ReplenishmentQueue';
import { MarkdownDecision } from '../components/MarkdownDecision'; // NEW
import { PerformanceMetrics } from '../components/PerformanceMetrics'; // NEW

export const Dashboard: React.FC = () => {
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [parameters, setParameters] = useState<SeasonParameters | null>(null);

  // ... existing state management logic ...

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Section 0: Parameter Gathering */}
      <ParameterGathering
        onParametersExtracted={(params, wfId) => {
          setParameters(params);
          setWorkflowId(wfId);
        }}
      />

      {workflowId && parameters && (
        <>
          {/* Section 1: Agent Cards */}
          <AgentCards workflowId={workflowId} />

          {/* Section 2: Forecast Summary */}
          <ForecastSummary workflowId={workflowId} />

          {/* Section 3: Cluster Cards */}
          <ClusterCards workflowId={workflowId} />

          {/* Section 4: Weekly Performance Chart */}
          <WeeklyPerformanceChart
            workflowId={workflowId}
            forecastHorizonWeeks={parameters.forecast_horizon_weeks}
          />

          {/* Section 5: Replenishment Queue */}
          {parameters.replenishment_strategy !== 'none' && (
            <ReplenishmentQueue workflowId={workflowId} />
          )}

          {/* Section 6: Markdown Decision (Conditional) */}
          <MarkdownDecision workflowId={workflowId} />

          {/* Section 7: Performance Metrics */}
          <PerformanceMetrics workflowId={workflowId} />
        </>
      )}
    </div>
  );
};
```

**Validation:**
- [ ] MarkdownDecision renders after ReplenishmentQueue
- [ ] MarkdownDecision hidden when markdown_checkpoint_week is null
- [ ] PerformanceMetrics always displays (last section)
- [ ] All sections receive correct workflowId prop
- [ ] Dashboard layout is responsive

---

### Task 8: Manual Testing - Section 6 Conditional Display

**Objective:** Verify Section 6 hides/shows correctly based on markdown_checkpoint_week.

**Test Cases:**

1. **Test Case 1: Markdown Enabled**
   - User Input: "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback. Markdown checkpoint at week 6 with 40% threshold."
   - Expected: Section 6 displays with markdown analysis
   - Validation:
     - [ ] Section 6 visible on dashboard
     - [ ] Gap × Elasticity formula displayed
     - [ ] Markdown recommendation shown
     - [ ] Badge says "Markdown Recommended" or "No Markdown Needed"

2. **Test Case 2: Markdown Disabled**
   - User Input: "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback."
   - Expected: Section 6 hidden (not rendered at all)
   - Validation:
     - [ ] Section 6 does not appear on dashboard
     - [ ] No error messages related to markdown
     - [ ] Other sections display normally

3. **Test Case 3: No Markdown Needed (Sell-Through Above Threshold)**
   - User Input: "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback. Markdown checkpoint at week 6 with 40% threshold."
   - Backend Mock: Set actual_sell_through to 0.50 (above 0.40)
   - Expected: Section 6 displays with "No Markdown Needed" badge
   - Validation:
     - [ ] Section 6 visible
     - [ ] Badge is green with "No Markdown Needed"
     - [ ] Justification says sell-through exceeds threshold
     - [ ] Recommended markdown is 0%

---

### Task 9: Manual Testing - Section 7 Metrics Aggregation

**Objective:** Verify Section 7 correctly aggregates data from multiple endpoints.

**Test Cases:**

1. **Test Case 1: All Metrics Healthy**
   - Backend Mock:
     - MAPE = 12.5% (< 15%)
     - Average Variance = 8.2% (< 10%)
     - Sell-Through = 65% (> 60%)
   - Expected: System Status = "Healthy" (green badge)
   - Validation:
     - [ ] MAPE card is green with "12.5%"
     - [ ] Variance card is green with "8.2%"
     - [ ] Sell-Through card is green with "65%"
     - [ ] System Status badge is green "Healthy"
     - [ ] Summary says "performing well"

2. **Test Case 2: Moderate Performance**
   - Backend Mock:
     - MAPE = 18.0% (15-25%)
     - Average Variance = 12.5% (10-20%)
     - Sell-Through = 55% (40-60%)
   - Expected: System Status = "Moderate" (yellow badge)
   - Validation:
     - [ ] All three cards are yellow
     - [ ] System Status badge is yellow "Moderate"
     - [ ] Summary says "showing moderate deviation"

3. **Test Case 3: Critical Performance**
   - Backend Mock:
     - MAPE = 28.0% (> 25%)
     - Average Variance = 22.0% (> 20%)
     - Sell-Through = 35% (< 40%)
   - Expected: System Status = "Needs Attention" (red badge)
   - Validation:
     - [ ] All three cards are red
     - [ ] System Status badge is red "Needs Attention"
     - [ ] Summary says "outside acceptable ranges"

---

### Task 10: End-to-End Testing - Sections 6 & 7 Integration

**Objective:** Validate complete workflow from parameter extraction to Sections 6 & 7 display.

**Test Scenarios:**

1. **Scenario 1: Full Workflow with Markdown**
   - Steps:
     1. Enter user input with markdown checkpoint
     2. Wait for agents to complete
     3. Verify Sections 0-7 all display
   - Validation:
     - [ ] Parameter extraction successful
     - [ ] All 8 sections display in correct order
     - [ ] Section 6 shows markdown analysis
     - [ ] Section 7 shows aggregated metrics
     - [ ] No console errors

2. **Scenario 2: Full Workflow without Markdown**
   - Steps:
     1. Enter user input without markdown checkpoint
     2. Wait for agents to complete
     3. Verify Sections 0-5, 7 display (Section 6 hidden)
   - Validation:
     - [ ] Only 7 sections display (Section 6 skipped)
     - [ ] Section 7 still calculates metrics correctly
     - [ ] No broken API calls related to markdown

3. **Scenario 3: Error Handling**
   - Steps:
     1. Simulate backend error for GET /api/markdowns/{id}
     2. Verify Section 6 displays error state gracefully
   - Validation:
     - [ ] Section 6 shows error message (not crashes)
     - [ ] Other sections continue to work
     - [ ] User can retry or refresh

---

## Validation Checklist

### Backend Integration
- [ ] GET /api/markdowns/{id} tested in Postman (4 test cases)
- [ ] GET /api/variance/{id}/summary tested in Postman (2 test cases)
- [ ] Mock Pricing Agent returns parameter-aware markdown data
- [ ] Backend returns 404 when markdown_checkpoint_week is null
- [ ] Backend handles invalid workflow IDs gracefully

### Frontend Services
- [ ] MarkdownService created with all methods
- [ ] PerformanceService created with aggregation logic
- [ ] Services handle 404 responses gracefully
- [ ] Formatting utilities return correct display strings
- [ ] Color coding logic matches acceptance criteria

### Frontend Components
- [ ] MarkdownDecision component displays Gap × Elasticity formula
- [ ] MarkdownDecision hidden when markdown not applicable
- [ ] PerformanceMetrics aggregates data from 3 endpoints
- [ ] Metric cards show correct color coding
- [ ] System Status badge updates based on metrics

### Dashboard Integration
- [ ] Section 6 added to Dashboard after Section 5
- [ ] Section 7 added to Dashboard (last section)
- [ ] Conditional rendering works for markdown
- [ ] All sections receive correct workflowId prop

### Manual Testing
- [ ] Section 6 displays when markdown enabled (Test Case 1)
- [ ] Section 6 hidden when markdown disabled (Test Case 2)
- [ ] Section 6 shows "No Markdown Needed" when appropriate (Test Case 3)
- [ ] Section 7 shows "Healthy" status with good metrics (Test Case 1)
- [ ] Section 7 shows "Moderate" status with mixed metrics (Test Case 2)
- [ ] Section 7 shows "Needs Attention" with poor metrics (Test Case 3)

### End-to-End Testing
- [ ] Full workflow with markdown completes successfully
- [ ] Full workflow without markdown skips Section 6 correctly
- [ ] Error states handled gracefully
- [ ] No console errors during normal operation

---

## Definition of Done

- [ ] All 10 tasks completed and validated
- [ ] Backend endpoints tested in Postman with all test cases passing
- [ ] Frontend services created with complete type definitions
- [ ] MarkdownDecision component displays all required information
- [ ] PerformanceMetrics component aggregates data correctly
- [ ] Conditional display logic works for Section 6
- [ ] Color coding thresholds match acceptance criteria
- [ ] Dashboard integrates both new sections
- [ ] Manual testing completed with all test cases passing
- [ ] End-to-end workflow tested with markdown enabled/disabled
- [ ] No console errors or warnings
- [ ] Code reviewed by team member
- [ ] Documentation updated in README if needed

---

## Notes

### Gap × Elasticity Formula Explanation

The Gap × Elasticity formula calculates the expected sales impact of a markdown:

```
Gap = markdown_threshold - actual_sell_through
Elasticity = price sensitivity coefficient (typically -1.2 to -2.0)
Expected Impact = Gap × Elasticity

Example:
- Threshold = 40%
- Actual Sell-Through = 35%
- Gap = 0.40 - 0.35 = 0.05 (5%)
- Elasticity = -1.5
- Expected Impact = 0.05 × (-1.5) = -0.075 (-7.5%)

Interpretation: A markdown is expected to reduce sales by 7.5%
(negative elasticity means price cuts reduce margins but boost volume).
```

### System Status Aggregation Logic

```typescript
// Healthy: All metrics in green range
// Moderate: 1-2 metrics in yellow range
// Needs Attention: Any metric in red range OR 3 metrics in yellow range

if (criticalCount > 0) return 'Needs Attention';
if (warningCount >= 2) return 'Moderate';
return 'Healthy';
```

### Conditional Display Rules

- **Section 6 displays only when:** `markdown_checkpoint_week !== null`
- **Section 5 displays only when:** `replenishment_strategy !== "none"`
- **Section 7 always displays** (regardless of parameters)

---

## Related Stories

- **PHASE4-001:** Environment Configuration
- **PHASE4-002:** Section 0 - Parameter Gathering
- **PHASE4-003:** Section 1 - Agent Cards + WebSocket
- **PHASE4-004:** Sections 2-3 - Forecast + Clusters
- **PHASE4-005:** Sections 4-5 - Weekly Chart + Replenishment Queue
- **PHASE4-007:** CSV Upload Workflows (next)
- **PHASE4-008:** Integration Tests
- **PHASE4-009:** Documentation & README Updates
