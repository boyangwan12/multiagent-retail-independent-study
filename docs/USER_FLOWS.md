# User Flows - Multi-Agent Retail Forecasting Dashboard

This document describes the 5 primary user flows for the Multi-Agent Retail Forecasting Dashboard, detailing the steps, interfaces, and expected outcomes for each workflow.

---

## Table of Contents

1. [Flow 0: Parameter Gathering](#flow-0-parameter-gathering)
2. [Flow 1: Pre-Season Forecast](#flow-1-pre-season-forecast)
3. [Flow 2: Ongoing Performance Monitoring](#flow-2-ongoing-performance-monitoring)
4. [Flow 3: Variance-Triggered Re-Forecast](#flow-3-variance-triggered-re-forecast)
5. [Flow 4: Markdown Decision](#flow-4-markdown-decision)

---

## Flow 0: Parameter Gathering

### User Goal
Extract structured season parameters from a natural language description to configure the forecasting workflow.

### User Persona
**Sarah - Retail Planner**: Needs to quickly input season parameters without filling out lengthy forms.

### Entry Point
First screen when accessing the dashboard (no parameters set yet).

### Steps

1. **View Parameter Input Screen**
   - User sees header: "Multi-Agent Retail Forecasting"
   - Section title: "Section 0: Parameter Gathering"
   - Description: "Describe your season parameters in natural language..."
   - Large textarea (500 character limit) with placeholder text
   - Character counter (e.g., "0/500")
   - "Extract Parameters" button (disabled if empty)

2. **Input Natural Language Description**
   - User types season description:
     ```
     12-week spring season starting March 1st.
     No replenishment, 0% holdback.
     Markdown at week 6 if below 60% sell-through.
     ```
   - Character counter updates in real-time: "157/500"
   - "Extract Parameters" button becomes enabled

3. **Extract Parameters (Mock LLM)**
   - User clicks "Extract Parameters" button
   - Button shows loading state: spinner + "Extracting..."
   - Mock API delay (2-5 seconds) simulates LLM processing
   - System uses regex patterns to extract:
     - `forecast_horizon_weeks`: 12
     - `season_start_date`: "2025-03-01"
     - `season_end_date`: "2025-05-24" (calculated)
     - `replenishment_strategy`: "none"
     - `dc_holdback_percentage`: 0
     - `markdown_checkpoint_week`: 6
     - `markdown_threshold`: 0.60
     - `extraction_confidence`: "high"

4. **Review Confirmation Modal**
   - Modal appears with title: "Confirm Season Parameters"
   - Confidence badge: "High Confidence" (green)
   - 5 parameter cards displayed in 2-column grid:
     - **Forecast Horizon**: 12 weeks (📅 icon)
     - **Season Dates**: Mar 1 - May 24, 2025 (🗓️  icon)
     - **Replenishment**: None (🚚 icon)
     - **DC Holdback**: 0% (🏭 icon)
     - **Markdown Checkpoint**: Week 6 (💰 icon)
   - Expandable "Extraction Reasoning" accordion:
     - Shows how each parameter was extracted
     - Lists any assumptions made
   - Action buttons: "Edit Parameters" | "Confirm & Continue"

5. **Confirm or Edit**
   - **Option A: Edit Parameters**
     - User clicks "Edit Parameters"
     - Modal closes, returns to textarea with original text
     - User can modify input and re-extract
   - **Option B: Confirm**
     - User clicks "Confirm & Continue"
     - Modal closes
     - Parameters saved to global ParametersContext
     - View transitions to dashboard with all 8 sections

6. **View Confirmed Banner**
   - After confirmation, Section 0 collapses to compact banner
   - Shows all 5 parameters inline
   - "Edit" button allows re-opening parameter gathering
   - Agent Reasoning Preview shows how parameters affect each agent

### Interfaces Involved
- **ParameterGathering.tsx**: Main container component
- **ParameterTextarea.tsx**: Input with character counter
- **ParameterConfirmationModal.tsx**: Modal with parameter cards
- **ParameterCard.tsx**: Individual parameter display
- **ConfirmedBanner.tsx**: Collapsed parameter summary
- **AgentReasoningPreview.tsx**: Shows parameter impact

### Expected Outcomes
- ✅ Parameters successfully extracted with high confidence
- ✅ User reviews and confirms parameters
- ✅ System ready to run forecast with confirmed parameters
- ✅ Smooth transition to dashboard view

### Error Scenarios
- **Incomplete Extraction** (<3 parameters found):
  - Error message appears: "Could not extract all required parameters. Missing: [list]. Please provide more information."
  - User revises input with more details
  - Re-extracts parameters
- **Network Error**:
  - Error message: "An error occurred during parameter extraction. Please try again."
  - User can retry extraction

### Success Metrics
- Time to complete: <2 minutes (vs 15 minutes with manual forms)
- Extraction accuracy: >80% first-attempt success rate
- User satisfaction: No need to understand technical parameter names

---

## Flow 1: Pre-Season Forecast

### User Goal
Generate a comprehensive demand forecast for the upcoming season before any sales data is available.

### User Persona
**Mark - Merchandise Manager**: Needs accurate demand forecasts to plan initial inventory buys.

### Entry Point
After completing Flow 0 (parameters confirmed), user scrolls down or uses keyboard shortcut (Alt+1) to view agent workflow.

### Steps

1. **View Agent Workflow Section**
   - User sees "Section 1: Agent Workflow" header
   - Fixed header at top shows:
     - Season: "Spring 2025 (12 weeks)"
     - Status: "Starting Forecast..."
     - Overall Progress: 0%
   - 3 agent cards displayed in row:
     - Demand Agent: Status "Idle" 🔵
     - Inventory Agent: Status "Idle" 🔵
     - Pricing Agent: Status "Idle" 🔵

2. **Monitor Demand Agent Execution**
   - Demand Agent card updates (mock WebSocket):
     - Status changes to "Running" ⚙️
     - Progress bar appears: 0% → 25% → 50% → 75% → 100%
     - Message updates:
       - "Analyzing historical patterns..." (0-25%)
       - "Running Prophet forecast..." (25-50%)
       - "Running ARIMA forecast..." (50-75%)
       - "Ensembling models..." (75-100%)
   - Card shows pulsing animation during execution
   - Estimated time: ~10 seconds (mock delay)

3. **Demand Agent Completes**
   - Status changes to "Success" ✅
   - Final message: "Forecast complete: 8,435 units over 12 weeks"
   - Card shows green checkmark icon
   - Output summary visible:
     - Prophet: 8,520 units
     - ARIMA: 8,350 units
     - Ensemble: 8,435 units (weighted average)

4. **Monitor Inventory Agent Execution**
   - Inventory Agent card activates automatically:
     - Status: "Running" ⚙️
     - Progress: 0% → 100%
     - Messages:
       - "Clustering stores by historical velocity..." (0-33%)
       - "Allocating forecast to 3 clusters..." (33-66%)
       - "Optimizing DC holdback (0%)..." (66-100%)
   - Estimated time: ~8 seconds

5. **Inventory Agent Completes**
   - Status: "Success" ✅
   - Message: "Allocated 8,435 units to 45 stores across 3 clusters"
   - Output summary:
     - High Volume (15 stores): 5,061 units (60%)
     - Medium Volume (18 stores): 2,530 units (30%)
     - Low Volume (12 stores): 844 units (10%)

6. **Monitor Pricing Agent Execution**
   - Pricing Agent card activates:
     - Status: "Running" ⚙️
     - Progress: 0% → 100%
     - Messages:
       - "Analyzing sell-through curves..." (0-40%)
       - "Calculating markdown checkpoint (Week 6)..." (40-70%)
       - "Optimizing clearance strategy..." (70-100%)
   - Estimated time: ~6 seconds

7. **Pricing Agent Completes**
   - Status: "Success" ✅
   - Message: "Markdown strategy optimized: Week 6 checkpoint"
   - Output summary:
     - Checkpoint: Week 6 (50% of season)
     - Threshold: 60% sell-through
     - Recommended discount: 30-40%

8. **View Workflow Completion**
   - Overall progress reaches 100%
   - Success banner appears:
     - Green checkmark icon
     - "Workflow Complete!"
     - "All agents have finished processing. Your forecast is ready."
   - User can now review results in Sections 2-7

9. **Review Forecast Summary (Section 2)**
   - User scrolls down or presses Alt+2
   - Sees 4 metric cards:
     - **Total Units**: 8,435 (+17.1% vs baseline)
     - **Projected Revenue**: $379,575 (+18.5%)
     - **Markdown Cost**: $72,000 (-15.3%)
     - **Excess Stock Risk**: 8.5% (-43.3%)
   - Forecast insight panel shows:
     - Method: "Weighted Ensemble"
     - Prophet: 8,520 units
     - ARIMA: 8,350 units
     - Peak week: Week 4

10. **Review Cluster Allocations (Section 3)**
    - User scrolls to Section 3
    - Sees 3 cluster tables:
      - **High Volume**: 15 stores, 5,061 units (60%)
      - **Medium Volume**: 18 stores, 2,530 units (30%)
      - **Low Volume**: 12 stores, 844 units (10%)
    - Each table sortable by:
      - Store name
      - Allocated units
      - Confidence score
    - Confidence bars show 90-95% accuracy

### Interfaces Involved
- **AgentWorkflow.tsx**: Agent cards and workflow orchestration
- **AgentCard.tsx**: Individual agent status display
- **FixedHeader.tsx**: Sticky header with overall progress
- **ForecastSummary.tsx**: Metric cards (Section 2)
- **MetricCard.tsx**: Individual metric display
- **ClusterCards.tsx**: Cluster tables (Section 3)
- **ClusterTable.tsx**: Sortable data table

### Expected Outcomes
- ✅ All 3 agents execute successfully
- ✅ Forecast generated: 8,435 units over 12 weeks
- ✅ Inventory allocated to 3 clusters (45 stores)
- ✅ Markdown strategy defined (Week 6 checkpoint)
- ✅ User confident in forecast accuracy

### Error Scenarios
- **Agent Execution Failure**:
  - Agent card shows status "Error" ❌
  - Error message: "Model training failed. Insufficient historical data."
  - User can retry workflow from Section 0
  - Error boundary prevents full app crash

### Success Metrics
- Total workflow time: ~24 seconds (vs 2-3 hours manual forecasting)
- Forecast accuracy: MAPE <20%
- User trust: Transparent reasoning increases confidence

---

## Flow 2: Ongoing Performance Monitoring

### User Goal
Track actual sales performance against forecast during the season and identify variance trends.

### User Persona
**Linda - Operations Manager**: Monitors weekly actuals to ensure forecast accuracy and inventory adequacy.

### Entry Point
User accesses dashboard mid-season (e.g., Week 4 of 12).

### Steps

1. **View Dashboard Overview**
   - User logs in and sees confirmed parameters banner (Section 0)
   - Agent workflow shows "Success" status for all 3 agents (Section 1)
   - Forecast summary shows season metrics (Section 2)

2. **Navigate to Weekly Performance (Section 4)**
   - User scrolls down or presses Alt+4
   - Section Header: "Weekly Performance"
   - Description: "Forecast vs actuals with variance analysis"
   - Chart title: "Weekly Demand: Forecast vs Actuals"

3. **View Weekly Chart**
   - **X-axis**: Week 1 through Week 12
   - **Y-axis**: Units (0 to 1,000)
   - **Purple line**: Forecast demand curve
     - Shows bell curve: ramp up (weeks 1-4), peak (week 4), decline (weeks 5-12)
   - **Green bars**: Actual sales for weeks 1-4 (variance <10%)
     - Week 1: Forecast 650, Actual 640 (-1.5%)
     - Week 2: Forecast 780, Actual 790 (+1.3%)
     - Week 3: Forecast 850, Actual 835 (-1.8%)
     - Week 4: Forecast 900, Actual 920 (+2.2%)
   - **Gray bars**: Future weeks (5-12) - no actuals yet
   - **Reference line**: 10% variance threshold (dashed yellow line)

4. **Analyze Variance Indicators**
   - Hover over Week 2 bar:
     - Tooltip appears:
       ```
       Week 2
       Forecast: 780 units
       Actual: 790 units
       Variance: +1.3% ✅
       Status: On Track
       ```
   - Color coding:
     - Green: Variance <10% (good performance)
     - Yellow: Variance 10-20% (moderate concern)
     - Red: Variance >20% (high concern)
   - All weeks 1-4 show green bars (performing well)

5. **Review Cumulative Metrics**
   - Below chart, summary cards show:
     - **Cumulative Forecast**: 3,180 units (weeks 1-4)
     - **Cumulative Actuals**: 3,185 units
     - **Overall Variance**: +0.2% ✅
     - **Forecast Accuracy**: 99.8%
   - Insight panel:
     - "Forecast tracking exceptionally well through Week 4. No adjustments needed."

6. **Check Replenishment Queue (Section 5)**
   - User scrolls to Section 5 or presses Alt+5
   - Table shows 10 store recommendations:
     - **Store 001 (High Volume)**: 120 units, High urgency, "Stock running low"
     - **Store 023 (Medium Volume)**: 45 units, Medium urgency, "Projected stockout Week 7"
     - **Store 037 (Low Volume)**: 15 units, Low urgency, "Preventive replenishment"
   - Urgency badges:
     - 🔴 High: Stockout risk within 2 weeks
     - 🟡 Medium: Stockout risk within 4 weeks
     - 🟢 Low: Preventive (no immediate risk)

7. **Take Action on Recommendations**
   - User reviews Store 001 (high urgency):
     - Current stock: 45 units
     - Forecast demand (next 2 weeks): 180 units
     - Recommendation: Replenish 120 units
     - Expected delivery: 3 days
   - User clicks "Approve" button
   - Status badge changes: "Pending" → "Approved" (green)
   - Toast notification: "Replenishment approved for Store 001"

8. **Export Performance Report**
   - User clicks "Export CSV" button in Section 5
   - Downloads `replenishment_queue_2025-03-22.csv`
   - File contains:
     - All 10 recommendations
     - Store details, forecast demand, current stock, recommendations
     - Urgency level and status

9. **Review Performance Metrics (Section 7)**
   - User scrolls to Section 7 or presses Alt+7
   - Sees 3 metric cards:
     - **MAPE (Overall)**: 8.2% ✅ (target: <20%)
     - **Forecast Accuracy**: 91.8% ✅
     - **Revenue Variance**: +2.1% ✅
   - Historical chart (4 quarters):
     - Q1: MAPE 12.5%
     - Q2: MAPE 10.3%
     - Q3: MAPE 9.1%
     - Q4 (current): MAPE 8.2% (improving trend)
   - Agent contribution:
     - Demand Agent: 40% (forecasting)
     - Inventory Agent: 35% (allocation optimization)
     - Pricing Agent: 25% (markdown strategy)

### Interfaces Involved
- **WeeklyChart.tsx**: Forecast vs actuals chart
- **CustomTooltip.tsx**: Hover tooltip for chart bars
- **ReplenishmentQueue.tsx**: Store recommendations table
- **ReplenishmentTable.tsx**: Sortable/filterable table
- **ActionButtons.tsx**: Approve/Reject buttons
- **UrgencyBadge.tsx**: Color-coded urgency indicators
- **PerformanceMetrics.tsx**: MAPE and accuracy tracking

### Expected Outcomes
- ✅ User sees actuals tracking forecast closely (<10% variance)
- ✅ User confident forecast is accurate
- ✅ User takes action on high-urgency replenishment needs
- ✅ User exports report for sharing with team

### Success Metrics
- Monitoring time: <5 minutes per week (vs 30 minutes manual tracking)
- Stockout prevention: 95%+ of stores adequately stocked
- Forecast accuracy: MAPE <20%

---

## Flow 3: Variance-Triggered Re-Forecast

### User Goal
Detect significant forecast variance, investigate root causes, and trigger a re-forecast if needed.

### User Persona
**David - Analytics Lead**: Monitors forecast accuracy and adjusts models when variance exceeds thresholds.

### Entry Point
User accesses dashboard at Week 6 and notices high variance in recent weeks.

### Steps

1. **Navigate to Weekly Performance**
   - User opens dashboard and scrolls to Section 4 (Weekly Chart)
   - Sees Week 5 bar is **red** (variance >20%)

2. **Identify High Variance Week**
   - Chart shows:
     - Week 5: Forecast 800 units, Actual 600 units, Variance -25% 🔴
     - Week 6 (current): Forecast 750 units, Actual 580 units, Variance -22.7% 🔴
   - Both weeks exceed 20% threshold (red bars)
   - Hover tooltip shows:
     ```
     Week 5
     Forecast: 800 units
     Actual: 600 units
     Variance: -25% ⚠️
     Status: High Variance
     ```

3. **Analyze Variance Root Cause**
   - User scrolls to Section 7 (Performance Metrics)
   - MAPE card shows:
     - Overall MAPE: 18.5% (was 8.2% at Week 4)
     - Trend: Increasing (yellow warning)
   - Agent contribution shows:
     - Demand Agent accuracy dropped from 95% to 82%
     - Potential issue: External shock (e.g., competitor promotion, weather)

4. **Review Cluster Performance**
   - User scrolls to Section 3 (Cluster Cards)
   - Investigates which clusters underperformed:
     - High Volume: Forecast 480 units, Actual 360 units (-25%)
     - Medium Volume: Forecast 240 units, Actual 170 units (-29%)
     - Low Volume: Forecast 80 units, Actual 70 units (-12.5%)
   - Insight: High and Medium clusters both underperforming
   - Hypothesis: Market-wide demand shock, not cluster-specific

5. **Check Replenishment Queue Impact**
   - User scrolls to Section 5
   - Sees increased excess stock warnings:
     - Store 001: "Excess stock: 45 units overstocked"
     - Store 015: "Excess stock: 30 units overstocked"
   - Status badges show "Overstocked" (orange)
   - Urgency: Low (can be cleared via markdowns)

6. **Evaluate Markdown Decision Need**
   - User scrolls to Section 6 (Markdown Decision)
   - Original plan: Week 6 markdown checkpoint (current week)
   - Current sell-through: 48% (below 60% threshold)
   - System recommendation:
     - "Trigger markdown now to clear excess stock"
     - Suggested discount: 40%
     - Expected impact: Clear 80% of excess stock by week 8

7. **Adjust Markdown Strategy**
   - User moves slider to 40% discount
   - Impact preview updates in real-time:
     - **Revenue Impact**: -$45,000 (markdown cost)
     - **Sell-Through Rate**: Increase to 75% by Week 8
     - **Excess Stock**: Reduce from 22% to 8%
     - **Confidence**: Medium (due to variance)
   - User clicks "Apply Markdown Strategy"
   - Toast notification: "Markdown strategy updated to 40% discount"

8. **Decide on Re-Forecast**
   - User scrolls back to Section 0 (Parameters banner)
   - Clicks "Edit" button
   - Parameter gathering screen re-appears
   - User updates input:
     ```
     12-week spring season starting March 1st.
     No replenishment, 0% holdback.
     Markdown NOW at 40% discount (Week 6).
     Reduce forecast by 15% due to market slowdown.
     ```
   - Clicks "Extract Parameters"

9. **Re-Run Forecast Workflow**
   - New parameters extracted:
     - `forecast_horizon_weeks`: 12 (unchanged)
     - `season_start_date`: "2025-03-01" (unchanged)
     - `markdown_checkpoint_week`: 6 (now current week)
     - `markdown_discount`: 40% (new)
     - `demand_adjustment`: -15% (new scalar)
   - User confirms new parameters
   - Agent workflow re-runs (Sections 1-7 update):
     - Demand Agent: Re-forecasts weeks 7-12 with -15% adjustment
     - Inventory Agent: Re-allocates remaining inventory
     - Pricing Agent: Updates markdown strategy to 40%

10. **Review Revised Forecast**
    - New forecast (weeks 7-12):
      - Week 7: 510 units (was 720, now -29%)
      - Week 8: 425 units (was 610, now -30%)
      - Week 9-12: Gradual decline
    - New metrics:
      - Total season forecast: 7,170 units (down from 8,435)
      - Excess stock risk: 5% (down from 22%)
      - Markdown cost: $68,000 (acceptable)
    - User confident revised forecast aligns with new market reality

### Interfaces Involved
- **WeeklyChart.tsx**: Red variance indicators
- **PerformanceMetrics.tsx**: MAPE trend tracking
- **ClusterCards.tsx**: Cluster-level variance analysis
- **ReplenishmentQueue.tsx**: Excess stock warnings
- **MarkdownDecision.tsx**: Interactive discount slider
- **ParameterGathering.tsx**: Re-enter parameters for re-forecast
- **AgentWorkflow.tsx**: Re-run all 3 agents

### Expected Outcomes
- ✅ User detects high variance early (Week 6)
- ✅ User identifies root cause (market-wide demand shock)
- ✅ User adjusts markdown strategy to 40%
- ✅ User triggers re-forecast with -15% demand adjustment
- ✅ New forecast reduces excess stock risk from 22% to 5%

### Error Scenarios
- **Re-Forecast Fails**:
  - Error message: "Re-forecast failed. Please review parameters."
  - User can adjust parameters and retry

### Success Metrics
- Variance detection time: <10 minutes (vs 2 hours manual analysis)
- Excess stock reduction: 22% → 5% after re-forecast
- Revenue impact: Minimize markdown cost while clearing stock

---

## Flow 4: Markdown Decision

### User Goal
Determine optimal markdown timing and discount percentage to maximize revenue while clearing excess stock.

### User Persona
**Rachel - Pricing Strategist**: Needs data-driven markdown recommendations to balance revenue and sell-through.

### Entry Point
User accesses dashboard at markdown checkpoint (e.g., Week 6 of 12).

### Steps

1. **Navigate to Markdown Decision Section**
   - User scrolls to Section 6 or presses Alt+6
   - Section Header: "Markdown Decision"
   - Description: "Clearance strategy optimization"
   - Current status card shows:
     - Week: 6 of 12 (50% through season)
     - Current sell-through: 52%
     - Target: 60% by Week 6
     - Status: "Below Target" (yellow)

2. **Review Current Performance**
   - Summary metrics:
     - Units sold: 4,380 (52% of 8,435 total)
     - Units remaining: 4,055 (48% unsold)
     - Full-price revenue: $197,100 (52% of projected)
     - Projected excess stock: 18% (if no markdown)
   - Insight panel:
     - "Sell-through below 60% target. Consider markdown to accelerate sales."

3. **Explore Markdown Scenarios**
   - User sees 3 pre-defined scenarios in tabs:
     - **Conservative**: 20% discount
     - **Moderate**: 30% discount
     - **Aggressive**: 40% discount
   - Default view: Moderate (30%)

4. **View Scenario Impact (30% Discount)**
   - Impact preview shows:
     - **Discount**: 30%
     - **Expected Sell-Through**: Increase to 75% by Week 8
     - **Revenue Impact**:
       - Full-price revenue lost: -$36,495 (units sold at markdown)
       - Total revenue: $343,080 (down from $379,575)
       - Revenue loss: -9.6%
     - **Excess Stock**:
       - Before: 18% (1,518 units)
       - After: 8% (675 units)
       - Reduction: -56%
     - **Confidence**: High (based on historical markdown curves)
   - Chart shows:
     - Purple line: Projected sell-through curve with 30% markdown
     - Green area: Units expected to sell at markdown (weeks 7-12)
     - Red area: Remaining excess stock (8%)

5. **Compare Scenarios**
   - User clicks "Conservative (20%)" tab:
     - Sell-through: 65% by Week 8 (slower)
     - Revenue loss: -6.4% (less revenue lost)
     - Excess stock: 12% (more remaining)
     - Confidence: Medium
   - User clicks "Aggressive (40%)" tab:
     - Sell-through: 85% by Week 8 (faster)
     - Revenue loss: -14.2% (more revenue lost)
     - Excess stock: 4% (minimal remaining)
     - Confidence: Medium

6. **Customize Markdown Percentage**
   - User decides 30% is too aggressive, 20% too conservative
   - User drags slider to 25%
   - Impact preview updates in real-time:
     - Sell-through: 70% by Week 8
     - Revenue loss: -8.1%
     - Excess stock: 10%
     - Confidence: High

7. **Review Agent Reasoning**
   - User expands "Why 25%?" accordion
   - Reasoning panel shows:
     - "Based on historical Spring 2023 season, 25% discount cleared 70% of excess stock"
     - "Competitor analysis: Average market discount is 22-28%"
     - "Price elasticity model: 10% discount → 12% sales increase"
     - "Recommended timing: Week 6 (current week) to Week 8"

8. **Apply Markdown Decision**
   - User clicks "Apply Markdown Strategy" button
   - Confirmation dialog appears:
     - "Apply 25% markdown for weeks 6-8?"
     - Preview: Revenue loss -$30,600, Excess stock 10%
     - Buttons: "Cancel" | "Confirm"
   - User clicks "Confirm"
   - Toast notification: "Markdown strategy applied: 25% discount starting Week 6"

9. **View Updated Forecast**
   - Weekly chart (Section 4) updates:
     - Weeks 6-8 bars now show projected sales with 25% markdown
     - Purple line adjusts to show new sell-through curve
   - Forecast summary (Section 2) updates:
     - Projected revenue: $348,975 (down from $379,575)
     - Excess stock risk: 10% (down from 18%)
     - Markdown cost: $30,600
   - Performance metrics (Section 7) updates:
     - Expected MAPE: 15% (accounting for markdown impact)

10. **Monitor Markdown Performance**
    - User returns to dashboard at Week 7
    - Weekly chart shows Week 6 actual sales:
      - Forecast (with 25% markdown): 820 units
      - Actual: 805 units
      - Variance: -1.8% ✅ (on track)
    - Sell-through: 58% → 68% (10% increase from markdown)
    - User confident 25% discount was correct decision

### Interfaces Involved
- **MarkdownDecision.tsx**: Main markdown decision component
- **MarkdownDecisionCard.tsx**: Scenario cards (Conservative/Moderate/Aggressive)
- **ImpactPreview.tsx**: Real-time revenue and sell-through preview
- **ConfidenceIndicator.tsx**: Confidence level display
- **WeeklyChart.tsx**: Updates to show markdown impact
- **ForecastSummary.tsx**: Updated revenue and excess stock metrics

### Expected Outcomes
- ✅ User explores 3 scenarios (20%, 30%, 40%)
- ✅ User customizes to 25% discount
- ✅ User applies markdown with high confidence
- ✅ Sell-through increases from 52% to 68% by Week 7
- ✅ Excess stock reduced from 18% to 10%

### Error Scenarios
- **Markdown Application Fails**:
  - Error message: "Failed to apply markdown strategy. Please try again."
  - User can retry or contact support

### Success Metrics
- Decision time: <15 minutes (vs 2 hours manual analysis)
- Excess stock reduction: 18% → 10%
- Revenue optimization: Minimize revenue loss while hitting sell-through target

---

## Summary

These 5 user flows cover the complete lifecycle of retail season forecasting:

1. **Flow 0**: Quick parameter input (natural language)
2. **Flow 1**: Automated forecast generation (3 agents)
3. **Flow 2**: Weekly performance monitoring (variance tracking)
4. **Flow 3**: Adaptive re-forecasting (respond to market changes)
5. **Flow 4**: Data-driven markdown decisions (optimize revenue)

### Key Success Metrics Across All Flows

| Flow | Traditional Time | Dashboard Time | Time Savings |
|------|-----------------|----------------|--------------|
| Flow 0 | 15 minutes | <2 minutes | 87% |
| Flow 1 | 2-3 hours | ~24 seconds | 98% |
| Flow 2 | 30 minutes/week | <5 minutes | 83% |
| Flow 3 | 2 hours | <30 minutes | 75% |
| Flow 4 | 2 hours | <15 minutes | 88% |

**Overall Impact**: Reduce forecasting and planning time from 10+ hours per season to <1 hour, while improving forecast accuracy (MAPE <20%) and reducing excess stock (8-10% vs 15-20% baseline).

---

**Last Updated**: October 18, 2025
**Version**: 1.0.0
