# Product Requirements Document (PRD) v3.3
# Parameter-Driven Multi-Agent Demand Forecasting & Inventory Allocation System

**Version:** 3.3
**Date:** 2025-10-16
**Status:** Ready for Development
**Product Owner:** Independent Study Project
**Target Approach:** Parameter-Driven MVP (Zara-Style Fast Fashion Test Scenario)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [Target Users](#3-target-users)
4. [User Stories](#4-user-stories)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Acceptance Criteria](#7-acceptance-criteria)
8. [Success Metrics](#8-success-metrics)
9. [System Features](#9-system-features)
10. [Data Requirements](#10-data-requirements)
11. [Technical Constraints](#11-technical-constraints)
12. [Assumptions & Dependencies](#12-assumptions--dependencies)
13. [Out of Scope](#13-out-of-scope)
14. [Release Plan](#14-release-plan)
15. [Appendix](#15-appendix)

---

## 1. Executive Summary

### 1.1 Product Overview

The Demand Forecasting & Inventory Allocation System is a **parameter-driven 3-agent AI system** designed to help retailers optimize category-level demand forecasting, inventory allocation, and markdown timing for seasonal products. The system uses natural language parameter extraction combined with agent autonomous reasoning to adapt to different retail strategies without code changes.

**Core Innovation (v3.3 - Parameter-Driven):**
- **⭐ NEW: User describes strategy** in natural language (free-form text box)
- **⭐ NEW: LLM extracts 5 key parameters** (forecast horizon, season length, replenishment strategy, DC holdback, markdown timing)
- **⭐ NEW: Agents autonomously reason** about how parameters affect their behavior using LLM intelligence
- **Forecast once** at category level (e.g., "Women's Dresses: 8,000 units over 12 weeks")
- **Allocate with math** using K-means clustering (3 clusters) and historical patterns
- **Adapt dynamically** via variance monitoring (>20% triggers automated re-forecast)
- **Same code adapts to any retail scenario** (Zara, luxury, furniture) without code modifications

### 1.2 Business Problem

Fashion retailers face critical challenges that result in significant financial losses:

1. **Inaccurate Demand Forecasting (PP-001, PP-019):**
   - Traditional ML models achieve only 20%+ forecast error on new product launches
   - Result: Poor manufacturing decisions → $500K+ lost margin annually

2. **Location-Specific Allocation Failures (PP-002, PP-015):**
   - Store-level demand patterns not captured → inventory misallocation
   - Impact: Stockouts in high-demand stores, overstock in low-demand stores
   - Cost: 5 hrs/week manual firefighting + ongoing carrying costs

3. **Late Markdown Decisions (PP-016):**
   - 3-day data lag prevents timely price reductions
   - Impact: **$500K lost margin annually** from missed markdown timing

4. **Long Manufacturing Lead Times (PP-001):**
   - Must commit to quantities 3-6 months before season launch
   - No sales history for new products → high forecast error → expensive overproduction or stockouts

### 1.3 Solution Overview

A parameter-driven hierarchical 3-agent system that:

**Agent 1: Demand Agent (Parameter-Aware)**
- Receives 5 extracted parameters from natural language input
- **Autonomous reasoning:** Adjusts safety stock (20% → 25%) when no replenishment configured
- Ensemble forecasting (Prophet + ARIMA in parallel, averaged)
- K-means store clustering (K=3, 7 features, StandardScaler normalization)
- Store allocation factors (70% historical + 30% attributes)

**Agent 2: Inventory Agent (Parameter-Aware)**
- **Autonomous reasoning:** Allocates 100% to stores when DC holdback = 0%, skips replenishment phase entirely
- Manufacturing order calculation (forecast + parameter-driven safety stock)
- Hierarchical allocation (parameter-driven: 100% or 55/45 split)
- Conditional weekly replenishment (only if strategy ≠ "none")

**Agent 3: Pricing Agent (Parameter-Aware)**
- **Autonomous reasoning:** Uses parameter-specified markdown week and threshold
- Markdown checkpoint at configurable week (default: Week 6, 60% threshold)
- Gap × Elasticity formula (elasticity=2.0, tunable, 5% rounding, 40% cap)
- Uniform markdown across all stores

**Orchestrator:**
- **NEW: Parameter extraction** via LLM (Azure OpenAI gpt-4o-mini)
- **NEW: Context-rich handoffs** (passes parameters to all agents)
- Workflow coordination (sequential agent handoffs)
- **Conditional phase execution** (skips phases based on parameters)
- Variance monitoring (>20% triggers re-forecast)
- Human-in-the-loop (Modify/Accept approval modals)

### 1.4 Expected Business Impact

| Benefit | Target | Timeline |
|---------|--------|----------|
| **Reduce Overstock** | 15-25% reduction | 6-12 months |
| **Reduce Stockouts** | 20-30% reduction | 6-12 months |
| **Optimize Manufacturing Orders** | 15% reduction in markdown costs | 12 months |
| **Improve Replenishment** | 10-15% inventory turnover improvement | 6-12 months |
| **Data-Driven Markdowns** | Maximize revenue, minimize leftover inventory | Immediate |

---

## 2. Product Vision

### 2.1 Long-Term Vision

Build a category-level demand forecasting platform that adapts to different retail business models through configurable parameters, providing accurate forecasts and optimal allocation strategies across seasonal fashion, stable catalog, and continuous replenishment retail.

### 2.2 MVP Vision (Parameter-Driven Architecture)

Prove the parameter-driven architecture using a Zara-style test scenario (12-week season, 0% holdback, no replenishment, Week 6 markdown), demonstrating:
- **Parameter extraction** from natural language works reliably
- **Agent autonomous reasoning** adapts behavior based on extracted parameters
- MAPE 12-18% forecast accuracy (realistic target)
- **Conditional phase execution** (replenishment phase skipped when strategy = "none")
- Variance >20% in Week 5 (testing adaptive re-forecasting)
- Markdown triggered in Week 6 (testing pricing agent)
- Workflow runtime <60 seconds (testing system performance)
- **Same code handles different retail strategies** without code changes

### 2.3 Success Definition

The MVP is successful if:
1. ✅ MAPE 12-18% on Spring 2025 hindcast (validates forecasting accuracy)
2. ✅ System correctly triggers re-forecast when variance >20% (validates adaptive behavior)
3. ✅ Human approval rate >80% (validates agent reasoning quality)
4. ✅ Workflow completes in <60 seconds (validates performance target)
5. ✅ User completes 12-week season workflow without critical errors (validates usability)

---

## 3. Target Users

### 3.1 Primary User: Merchandise Planner (Fashion Retail)

**Profile:**
- **Role:** Forecasts demand and sets inventory targets for seasonal categories
- **Responsibilities:**
  - Manufacturing order approvals (6 months before season)
  - Weekly replenishment reviews
  - Markdown decision approvals
- **Pain Points:**
  - Inaccurate forecasts lead to expensive mistakes
  - Manual allocation is time-consuming and error-prone
  - Late markdowns erode margins
- **Goals:**
  - Fast decision-making (approve decisions in <2 minutes)
  - Transparent workflow (understand agent reasoning)
  - Reduce overstock and stockouts

**Technical Proficiency:** Medium (comfortable with CSV uploads, dashboards, approval workflows)

### 3.2 Secondary Users

**Allocation Analyst:**
- Reviews store-level distributions
- Validates cluster allocations match business understanding
- Monitors replenishment queue

**Merchandising Manager:**
- Final approval authority for high-value decisions
- Reviews post-season performance reports
- Tunes parameters for next season

### 3.3 User Needs

| User Type | Primary Needs | MVP Support |
|-----------|--------------|-------------|
| **Merchandise Planner** | Fast approvals, forecast transparency, variance alerts | ✅ Full support |
| **Allocation Analyst** | Drill-down from cluster → store, CSV exports | ✅ Full support |
| **Merchandising Manager** | Post-season reports, parameter tuning visibility | ✅ Read-only display (no tuning in UI) |

---

## 4. User Stories

### 4.0 Parameter Gathering ⭐ NEW in v3.3 (Phase 0)

#### Story 0.1: Describe Season Strategy in Natural Language
**As a** Merchandise Planner
**I want to** describe my season planning strategy in natural language
**So that** the system can extract key parameters and configure agents without code changes

**Acceptance Criteria:**
- [ ] "Configure Strategy" section appears at top of dashboard (before data upload)
- [ ] Free-form text area allows multi-line input (up to 500 characters)
- [ ] Placeholder text provides example: "I'm planning a 12-week spring fashion season starting March 1st. Send all inventory to stores at launch with no DC holdback. I don't want ongoing replenishment - just one initial allocation. Check for markdown opportunities at week 6 if we're below 60% sell-through."
- [ ] "Extract Parameters" button triggers LLM parameter extraction
- [ ] Loading indicator during extraction (~2-5 seconds)
- [ ] Inline help tooltip explains the 5 key parameters system will extract

**Priority:** P0 (Blocker)

---

#### Story 0.2: Review and Confirm Extracted Parameters
**As a** Merchandise Planner
**I want to** review LLM-extracted parameters before starting workflow
**So that** I can validate and adjust parameters if extraction is incorrect

**Acceptance Criteria:**
- [ ] Modal displays extracted parameters in structured format:
  - **Forecast Horizon:** 12 weeks
  - **Season Dates:** March 1, 2025 - May 23, 2025
  - **Replenishment Strategy:** None (one-shot allocation)
  - **DC Holdback:** 0% (100% initial to stores)
  - **Markdown Timing:** Week 6, 60% threshold
- [ ] Each parameter is editable (inline edit or separate inputs)
- [ ] "Extraction Reasoning" expandable section shows LLM explanation
- [ ] "Re-Extract" button allows user to revise natural language input and retry
- [ ] "Confirm & Continue" button saves parameters and proceeds to data upload
- [ ] Parameters displayed as read-only summary in dashboard header after confirmation

**Priority:** P0 (Blocker)

---

#### Story 0.3: Handle Incomplete Parameter Extraction
**As a** Merchandise Planner
**I want to** be notified if system cannot extract all required parameters
**So that** I can provide additional information to complete extraction

**Acceptance Criteria:**
- [ ] Error modal displays if extraction incomplete:
  - "⚠️ Could not extract all parameters"
  - "Missing: Season start date, Markdown threshold"
  - "Please specify when the season begins and your markdown strategy."
- [ ] User can edit natural language input and retry extraction
- [ ] System provides specific guidance for missing parameters
- [ ] User can manually input missing parameters via form fields
- [ ] System re-validates before allowing workflow to proceed

**Priority:** P0 (Blocker)

---

#### Story 0.4: View Agent Reasoning Based on Parameters
**As a** Merchandise Planner
**I want to** see how agents will adapt their behavior based on my parameters
**So that** I can understand system decisions before running workflow

**Acceptance Criteria:**
- [ ] After parameter confirmation, "Agent Reasoning Preview" section displays:
  - **Demand Agent:** "No replenishment configured → increasing safety stock from 20% to 25%"
  - **Inventory Agent:** "0% DC holdback → allocating 100% at Week 0, skipping replenishment phase"
  - **Pricing Agent:** "Week 6 checkpoint at 60% threshold → monitoring for Gap × Elasticity markdown"
- [ ] Each reasoning statement is italicized to indicate LLM-generated insight
- [ ] User can proceed to data upload after reviewing reasoning
- [ ] Reasoning preview updates if user modifies parameters

**Priority:** P1 (High)

---

### 4.1 Pre-Season Forecasting (Week -24)

#### Story 1.1: Upload Historical Sales Data
**As a** Merchandise Planner
**I want to** upload historical sales data (2022-2024)
**So that** the system can train forecasting models on past category performance

**Acceptance Criteria:**
- [ ] System accepts CSV with columns: date, category, store_id, quantity_sold, revenue
- [ ] System validates: 2+ years of data, 50 stores present, no missing values
- [ ] System auto-detects available categories (e.g., Women's Dresses, Men's Shirts, Accessories)
- [ ] System shows preview: "✓ 54,750 rows | Categories detected: Women's Dresses, Men's Shirts, Accessories"
- [ ] Inline error messages for invalid format: "❌ Missing required columns: date, category, store_id, quantity_sold"

**Priority:** P0 (Blocker)

---

#### Story 1.2: Upload Store Attributes
**As a** Merchandise Planner
**I want to** upload store attributes (size, demographics, sales performance)
**So that** the system can cluster stores and calculate allocation factors

**Acceptance Criteria:**
- [ ] System accepts CSV with 7 required features: avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
- [ ] System validates: 50 stores, all features present, valid enum values
- [ ] System shows preview: "✓ 50 stores | 7 features validated"
- [ ] System performs K-means clustering (K=3) and displays cluster summary
- [ ] Inline error for missing stores: "❌ Missing data for stores: S15, S22, S38"

**Priority:** P0 (Blocker)

---

#### Story 1.3: Select Category for Forecasting
**As a** Merchandise Planner
**I want to** select a category for forecasting
**So that** the system can train models on the right historical data

**Acceptance Criteria:**
- [ ] Dropdown auto-populates with detected categories from uploaded CSV
- [ ] System displays confirmed parameters in read-only summary at top of page:
  - Forecast Horizon: 12 weeks
  - Season Dates: March 1, 2025 - May 23, 2025
  - Replenishment Strategy: None
  - DC Holdback: 0%
  - Markdown Timing: Week 6, 60% threshold
- [ ] "Edit Parameters" button allows user to return to Phase 0 parameter extraction
- [ ] User cannot proceed without category selection

**Priority:** P0 (Blocker)

---

#### Story 1.4: Generate Initial Forecast
**As a** Merchandise Planner
**I want to** trigger the 3-agent workflow to generate a category-level forecast
**So that** I can review total season demand and manufacturing order recommendations

**Acceptance Criteria:**
- [ ] "Run Forecast" button triggers Orchestrator
- [ ] Agent cards expand and show real-time progress via WebSocket:
  - ✓ Prophet forecast: 8,200 units (15s)
  - ⏳ ARIMA forecast: Running... (10s)
  - ✓ ARIMA forecast: 7,800 units (10s)
  - ✓ Ensemble averaging: 8,000 units (2s)
  - ✓ K-means clustering: 3 clusters (15s)
  - ✓ Store allocation factors calculated (8s)
  - ✓ Manufacturing order: 9,600 units (2s)
- [ ] Workflow completes in <60 seconds
- [ ] Agent cards auto-collapse 5 seconds after completion
- [ ] Error handling: "Retry" button if agent fails, "View Logs" for details

**Priority:** P0 (Blocker)

---

#### Story 1.5: Approve Manufacturing Order with Agent Reasoning
**As a** Merchandise Planner
**I want to** review agent reasoning and approve manufacturing order
**So that** I can commit to production quantities with transparent AI decision-making

**Acceptance Criteria:**
- [ ] Modal displays:
  - Total Season Forecast: 8,000 units
  - Prophet Forecast: 8,200 units
  - ARIMA Forecast: 7,800 units
  - Ensemble Method: Average
  - **Agent Reasoning:** *"Replenishment strategy is 'none' → increasing safety stock from 20% to 25% to account for no ongoing replenishment buffer"*
  - Safety Stock: 25% (2,000 units) - adjusted from default 20%
  - **Manufacturing Order: 10,000 units**
- [ ] Safety stock slider (10-30%) updates manufacturing order in real-time
- [ ] Agent reasoning updates dynamically when user adjusts slider
- [ ] "Modify" button: Agent recalculates with new safety stock % → Modal updates
- [ ] "Accept" button: Saves to database, closes modal, populates dashboard
- [ ] No "Reject" button (iterative Modify only)

**Priority:** P0 (Blocker)

---

### 4.2 Season Start Allocation (Week 0)

#### Story 2.1: View Forecast Summary with Parameter Context
**As a** Merchandise Planner
**I want to** see category-level forecast details with parameter context
**So that** I can understand total demand and how parameters influenced the forecast

**Acceptance Criteria:**
- [ ] Section 2 shows:
  - Category: Women's Dresses - Spring 2025 (12 weeks)
  - Total Season Forecast: 8,000 units
  - Prophet: 8,200 | ARIMA: 7,800 | Method: Ensemble
  - Manufacturing Order: 10,000 units (25% safety - adjusted for no replenishment) ✓
  - **Parameter Context:** "No replenishment strategy → 100% allocation at Week 0"
  - Mini bar chart: Weekly demand curve (Recharts 400×60px)
- [ ] "Edit Parameters" button returns to Phase 0 parameter extraction
- [ ] Section expanded by default (Collapsible defaultOpen={true})

**Priority:** P0 (Blocker)

---

#### Story 2.2: Review Cluster Allocations (Parameter-Driven)
**As a** Allocation Analyst
**I want to** drill down from category → cluster → store allocations
**So that** I can validate hierarchical distribution matches business understanding and parameters

**Acceptance Criteria:**
- [ ] Section 3 shows 3 cluster cards (stacked vertically):
  - **Fashion_Forward:** 4,000 units | 20 stores | 40% of total
  - **Mainstream:** 3,500 units | 18 stores | 35% of total
  - **Value_Conscious:** 2,500 units | 12 stores | 25% of total
- [ ] Each cluster card displays:
  - **Parameter Banner:** "0% DC Holdback → 100% allocated to stores at Week 0"
  - Cluster characteristics (avg income, avg size, location tier, fashion tier, avg weekly sales)
  - Store allocation table (TanStack Table with columns):
    - **Zara Parameters (0% Holdback):** Store ID, Season Total, Initial (100%), DC Reserve (0%), Attributes [View]
    - Example: S01 | 200 | 200 | 0 | [View]
    - **Standard Parameters (45% Holdback):** Store ID, Season Total, Initial (55%), Holdback (45%), Attributes [View]
  - "Export CSV" button (downloads cluster-specific allocations)
- [ ] Multiple clusters can be expanded simultaneously (Accordion type="multiple")
- [ ] Click row → Opens modal with store attributes details

**Priority:** P1 (High)

---

### 4.3 Weekly Monitoring (Weeks 1-12)

#### Story 3.1: Upload Weekly Actuals
**As a** Merchandise Planner
**I want to** upload actual sales data every Monday
**So that** the system can calculate variance and trigger re-forecast if needed

**Acceptance Criteria:**
- [ ] Dashboard shows notice: "⚠️ Week 3 actuals pending upload" when not yet uploaded
- [ ] "Upload Week 3 Actuals" button opens modal:
  - Week: 3 (2025-03-08 to 2025-03-14)
  - Expected format: date, store_id, quantity_sold
  - Date range: 7 days (Mon-Sun)
  - Rows: ~350 (50 stores × 7 days)
- [ ] User selects CSV file → "Upload & Calculate Variance" button
- [ ] System processes (5 seconds):
  - Validates date range matches Week 3
  - Validates all 50 stores present
  - Aggregates daily sales to weekly totals
  - Calculates category-level variance
- [ ] Toast notification: "✓ Week 3 actuals uploaded. Variance: 8%"
- [ ] Section 4 chart updates: Actual bar appears for Week 3 (green if variance <10%)
- [ ] Alert banner updates: "🟢 Variance 8% - Tracking well"

**Error Handling:**
- [ ] Wrong date range → "❌ Date range mismatch. Expected 2025-03-08 to 2025-03-14"
- [ ] Missing stores → "❌ Missing data for stores: S15, S22, S38"
- [ ] Duplicate upload → "⚠️ Week 3 actuals already uploaded. Overwrite existing data?"

**Priority:** P0 (Blocker)

---

#### Story 3.2: Monitor Weekly Variance (Normal)
**As a** Merchandise Planner
**I want to** see weekly forecast vs actual performance
**So that** I can identify trends and monitor accuracy

**Acceptance Criteria:**
- [ ] Section 4 shows:
  - **Recharts ComposedChart:**
    - Blue line: Forecast
    - Green bars: Actuals (when variance <10%)
    - Amber bars: Actuals (when variance 10-20%)
    - Red bars: Actuals (when variance >20%)
  - **Week-by-Week Table:**
    - Columns: Week | Forecast | Actual | Variance | Status
    - Example: 1 | 650 | 640 | -2% | 🟢
    - Hover row → Highlights corresponding bar in chart
- [ ] Alert banner shows:
  - 🟢 Variance <10%: "Tracking well"
  - 🟡 Variance 10-20%: "Elevated variance 15%"
  - 🔴 Variance >20%: "High variance 25% - Re-forecast triggered"

**Priority:** P0 (Blocker)

---

#### Story 3.3: Drill Down to Store-Level Variance
**As a** Allocation Analyst
**I want to** expand weekly rows to see store-level variance breakdown
**So that** I can identify problem stores

**Acceptance Criteria:**
- [ ] Click Week 3 row in table → Row expands inline
- [ ] Expanded content shows store-level breakdown table:
  - Columns: Store | Forecast | Actual | Variance
  - Example: S01 | 12 | 15 | +25% 🔴
  - Example: S02 | 11 | 11 | 0% 🟢
  - Color-coded variance badges (🟢 <10%, 🟡 10-20%, 🔴 >20%)
- [ ] "Collapse" button to close expanded row
- [ ] User can expand multiple weeks simultaneously

**Priority:** P1 (High)

---

#### Story 3.4: Automatic Re-Forecast on High Variance
**As a** Merchandise Planner
**I want to** the system to automatically re-forecast when variance exceeds 20%
**So that** I can adapt to unexpected demand changes without manual intervention

**Acceptance Criteria:**
- [ ] System detects variance >20% after actuals upload
- [ ] Alert banner updates: "🔴 High variance 25% - Re-forecast triggered"
- [ ] Loading overlay blocks entire page
- [ ] Auto-scrolls to top
- [ ] Demand Agent card expands with progress:
  - ⏳ Re-forecasting weeks 4-12...
  - ✓ Prophet: 10,800 units
  - ✓ ARIMA: 10,200 units
  - ✓ Ensemble: 10,500 units (new forecast)
- [ ] Workflow completes in <60 seconds
- [ ] Loading overlay disappears
- [ ] Section 2 updates: New forecast 10,500 (was 8,000)
- [ ] Section 5 updates: Replenishment plan adjusted
- [ ] No approval modal (re-forecast auto-applies per technical decisions)

**Priority:** P0 (Blocker)

---

#### Story 3.5: Conditional Weekly Replenishment (Parameter-Driven)
**As a** Merchandise Planner
**I want to** review and approve weekly store replenishments when configured
**So that** stores receive adequate inventory based on updated forecasts

**Acceptance Criteria - Replenishment Enabled (Standard Parameters: 45% holdback, weekly replenishment):**
- [ ] Section 5 shows: "Week 3 Replenishment Queue (12 stores)"
- [ ] Table displays:
  - Columns: Store ID | Current Inventory | Forecast Next Week | Replenish Needed | DC Available
  - Example: S01 | 6 | 10 | 4 | ✓
  - Example: S15 | 2 | 12 | 10 | ⚠️ 5 (insufficient DC inventory)
- [ ] DC Inventory Status: "4,200 units available (45% holdback reserve)"
- [ ] "Approve Replenishments" button
- [ ] After approval:
  - Rows update: "✓ Shipped" status (green checkmark)
  - Toast for partial shipments: "⚠️ Partial shipment approved. Manual restock needed for S15."

**Acceptance Criteria - Replenishment Disabled (Zara Parameters: 0% holdback, no replenishment):**
- [ ] Section 5 shows: "⚠️ Replenishment Disabled - 100% Allocated at Week 0"
- [ ] **Agent Reasoning Displayed:** *"Replenishment strategy is 'none' and DC holdback is 0%. All inventory was shipped to stores at Week 0. Phase skipped."*
- [ ] No replenishment table displayed
- [ ] User proceeds directly to Week 6 markdown checkpoint

**Priority:** P0 (Blocker)

---

### 4.4 Mid-Season Markdown (Week 6)

#### Story 4.1: View Markdown Checkpoint Countdown
**As a** Merchandise Planner
**I want to** see countdown to Week 6 markdown checkpoint
**So that** I'm prepared for mid-season pricing decisions

**Acceptance Criteria:**
- [ ] Section 6 shows (Weeks 1-5):
  - "📅 Markdown Checkpoint - Week 6 (in 3 weeks)"
  - "Countdown: 3 weeks until checkpoint"
  - "Target Sell-Through: 60% by Week 6"
- [ ] Countdown decrements weekly as actuals are uploaded

**Priority:** P2 (Nice to Have)

---

#### Story 4.2: Review Markdown Recommendation
**As a** Merchandise Planner
**I want to** see Gap × Elasticity markdown calculation and recommendation
**So that** I can make informed pricing decisions

**Acceptance Criteria:**
- [ ] Section 6 activates at Week 6:
  - "⚠️ Week 6 Markdown Checkpoint - Action Required"
  - **Sell-Through Analysis:**
    - Total Manufactured: 9,600 units
    - Total Sold (W1-W6): 5,280 units
    - Sell-Through: 55% (Target: 60%)
    - Gap: 5 percentage points
  - **Markdown Recommendation:**
    - Formula: Gap × Elasticity = 0.05 × 2.0 = 10%
    - Application: Uniform across all stores
    - Expected Sales Lift: +18%
- [ ] Real-time elasticity slider:
  - Default: 2.0
  - Range: 1.0 to 3.0
  - Preview updates: Move to 2.5 → "12.5% markdown"
- [ ] "Apply Markdown & Re-forecast" button

**Priority:** P0 (Blocker)

---

#### Story 4.3: Apply Markdown and Trigger Re-Forecast
**As a** Merchandise Planner
**I want to** apply recommended markdown and automatically re-forecast remaining weeks
**So that** I can accelerate sell-through and avoid excess inventory

**Acceptance Criteria:**
- [ ] Click "Apply Markdown & Re-forecast" button
- [ ] Loading overlay blocks page
- [ ] Auto-scrolls to top
- [ ] Agent cards show progress:
  - Pricing Agent: ✓ Applying 10% markdown (5s)
  - Demand Agent: 🔄 Re-forecasting weeks 7-12... (55s)
- [ ] Section 2 updates: New forecast for weeks 7-12
- [ ] Section 6 updates: Historical record:
  - "✓ 10% Markdown Applied (Week 6)"
  - "Historical Record:"
  - "Applied: Week 6 | Depth: 10% | Elasticity: 2.0"
  - "Expected Lift: +18% | Re-forecast: Completed ✓"
- [ ] Markdown applies uniformly to all stores (no cluster differentiation)

**Priority:** P0 (Blocker)

---

### 4.5 Post-Season Analysis

#### Story 5.1: View Performance Metrics Dashboard
**As a** Merchandise Planner
**I want to** see real-time season performance metrics
**So that** I can track forecast accuracy and business impact

**Acceptance Criteria:**
- [ ] Section 7 shows 3 metric cards (grid 3 columns):
  - **Forecast Accuracy:**
    - MAPE: 12% (Target: <20%) ✓
    - Bias: +2% (Target: ±5%) ✓
    - Re-forecast Trigger: 92% accuracy (Target: 90%+) ✓
  - **Business Impact:**
    - Stockouts: 3 events
    - Overstock: 1,800 units
    - Markdown Costs: $24K
    - Inventory Turnover: +8%
  - **System Performance:**
    - Runtime: 58s (Target: <60s) ✓
    - Approval Rate: 85% Accept
    - Uptime: 99%+
- [ ] Metrics update weekly as new actuals are uploaded
- [ ] Read-only display (no interactive elements)

**Priority:** P1 (High)

---

#### Story 5.2: Access Detailed Performance Report
**As a** Merchandising Manager
**I want to** view a comprehensive post-season performance report
**So that** I can analyze forecast accuracy, business impact, and parameter recommendations

**Acceptance Criteria:**
- [ ] "View Detailed Report →" button in Section 7
- [ ] Navigates to `/reports/spring-2025` (new page)
- [ ] Report sections:
  - **Executive Summary:** High-level metrics
  - **Forecast Accuracy Deep Dive:** MAPE by week chart, MAPE by cluster table, bias analysis
  - **Variance & Re-forecast Events Timeline:** Week-by-week timeline of re-forecast triggers
  - **Business Impact:** Stockout analysis, overstock analysis, markdown impact
  - **System Performance:** Agent runtimes, approval rates
  - **Parameter Recommendations:** Display-only suggestions (e.g., "Consider reducing safety stock from 20% to 18%")
- [ ] "← Back to Dashboard" button returns to main dashboard
- [ ] Read-only, no PDF export or parameter tuning actions

**Priority:** P2 (Nice to Have)

---

## 5. Functional Requirements

### 5.1 Data Upload & Validation

**FR-1.1:** System shall accept CSV uploads for historical sales data (2022-2024) with required columns: date, category, store_id, quantity_sold, revenue.

**FR-1.2:** System shall validate uploaded CSV files:
- Minimum 2 years of data
- All 50 stores present
- No missing values in required columns
- Valid date formats (YYYY-MM-DD)
- Numeric values for quantity_sold and revenue

**FR-1.3:** System shall auto-detect available categories from historical sales CSV and populate dropdown (e.g., Women's Dresses, Men's Shirts, Accessories).

**FR-1.4:** System shall accept CSV uploads for store attributes with 7 required features: avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region.

**FR-1.5:** System shall validate store attributes CSV:
- Exactly 50 stores
- All 7 features present
- Valid enum values for categorical fields (location_tier, fashion_tier, store_format, region)

**FR-1.6:** System shall display inline error messages for invalid uploads with expected format guidance.

---

### 5.2 Forecasting & Clustering

**FR-2.1:** System shall generate category-level forecast using ensemble method (Prophet + ARIMA run in parallel, results averaged).

**FR-2.2:** System shall perform K-means clustering (K=3) on 50 stores using 7 features with StandardScaler normalization:
- avg_weekly_sales_12mo (most important)
- store_size_sqft
- median_income
- location_tier (A=3, B=2, C=1)
- fashion_tier (Premium=3, Mainstream=2, Value=1)
- store_format (Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1)
- region (Northeast=1, Southeast=2, Midwest=3, West=4)

**FR-2.3:** System shall label clusters as Fashion_Forward, Mainstream, Value_Conscious based on cluster characteristics.

**FR-2.4:** System shall calculate cluster allocation percentages based on historical sales performance.

**FR-2.5:** System shall calculate store allocation factors within each cluster using hybrid method (70% historical performance + 30% attribute-based capacity score).

**FR-2.6:** System shall complete full 3-agent workflow (Demand → Inventory → Pricing) in <60 seconds.

---

### 5.3 Inventory Management

**FR-3.1:** System shall calculate manufacturing order quantity using formula: `manufacturing_qty = total_demand × (1 + safety_stock_pct)` where safety_stock_pct = 20%.

**FR-3.2:** System shall allocate manufactured inventory hierarchically:
- 55% initial allocation to stores (Week 0)
- 45% holdback at DC for replenishment

**FR-3.3:** System shall distribute initial allocation across stores using calculated allocation factors, ensuring minimum 2-week forecast per store.

**FR-3.4:** System shall calculate weekly replenishment using simple formula:
```python
remaining_allocation = season_total - total_shipped_so_far
weeks_remaining = 12 - current_week
next_week_forecast = remaining_allocation / weeks_remaining
replenishment_qty = max(0, next_week_forecast - current_inventory)
```

**FR-3.5:** System shall flag stores with insufficient DC inventory for partial shipments.

---

### 5.4 Variance Monitoring & Re-Forecasting

**FR-4.1:** System shall calculate weekly variance after actuals upload:
```python
variance = abs(actual_demand - forecast_demand) / forecast_demand × 100%
```

**FR-4.2:** System shall display variance alerts:
- 🟢 Variance <10%: "Tracking well"
- 🟡 Variance 10-20%: "Elevated variance X%"
- 🔴 Variance >20%: "High variance X% - Re-forecast triggered"

**FR-4.3:** System shall automatically trigger re-forecast workflow when variance >20%:
- Enable re-forecast handoff dynamically
- Demand Agent re-runs ensemble forecast for remaining weeks
- Inventory Agent recalculates replenishment plan
- No human approval required (auto-applies)

**FR-4.4:** System shall block user interactions with loading overlay during re-forecast and auto-scroll to top.

---

### 5.5 Markdown Management

**FR-5.1:** System shall evaluate Week 6 sell-through checkpoint:
```python
sell_through_rate = total_sold / total_manufactured
gap = target_sell_through - sell_through_rate  # Target: 0.60
```

**FR-5.2:** System shall calculate markdown depth using Gap × Elasticity formula:
```python
elasticity_coefficient = 2.0  # Tunable parameter
markdown_raw = gap × elasticity_coefficient
markdown_rounded = round(markdown_raw × 20) / 20  # Round to nearest 5%
markdown_depth = min(markdown_rounded, 0.40)  # Cap at 40%
```

**FR-5.3:** System shall provide real-time markdown preview when user adjusts elasticity slider (range: 1.0 to 3.0).

**FR-5.4:** System shall apply markdown uniformly across all stores (no cluster-specific differentiation).

**FR-5.5:** System shall trigger re-forecast after markdown application to update forecast for weeks 7-12 with new price.

**FR-5.6:** System shall display historical markdown record after application: Week applied, depth %, elasticity used, expected sales lift.

---

### 5.6 Human-in-the-Loop Approvals

**FR-6.1:** System shall require human approval for manufacturing orders via modal with:
- Total Season Forecast
- Prophet Forecast
- ARIMA Forecast
- Ensemble Method
- Safety Stock % (adjustable slider 10-30%)
- Manufacturing Order (auto-updates with slider)
- Actions: [Modify] [Accept]

**FR-6.2:** "Modify" button shall trigger agent recalculation with new safety stock % and update modal.

**FR-6.3:** "Accept" button shall save decision to database, close modal, and populate dashboard.

**FR-6.4:** System shall NOT provide "Reject" button (iterative Modify only).

**FR-6.5:** System shall display approval rate in Section 7 metrics (% Modify vs Accept).

---

### 5.7 Real-Time Updates

**FR-7.1:** System shall stream agent progress via WebSocket with line-by-line message updates (not batched).

**FR-7.2:** Agent cards shall expand when workflow starts and display progress:
- ✓ Completed steps (green checkmark, duration)
- ⏳ Running steps (spinner, "Running...")
- ⏸ Waiting steps (muted, "Waiting...")

**FR-7.3:** Agent cards shall display progress bar (0-100%) based on workflow completion.

**FR-7.4:** Agent cards shall auto-collapse 5 seconds after workflow completion.

**FR-7.5:** System shall display toast notifications for:
- Successful actuals upload
- Re-forecast triggered
- Markdown applied
- Partial replenishment approvals

---

### 5.8 Data Visualization

**FR-8.1:** System shall display weekly performance chart (Recharts ComposedChart):
- Blue line: Forecast
- Green bars: Actuals (variance <10%)
- Amber bars: Actuals (variance 10-20%)
- Red bars: Actuals (variance >20%)

**FR-8.2:** Chart hover shall display tooltip and highlight corresponding table row.

**FR-8.3:** System shall display mini bar chart (400×60px) in Section 2 showing weekly demand curve.

**FR-8.4:** System shall allow table row expansion to show store-level variance breakdown inline.

**FR-8.5:** System shall color-code variance badges:
- 🟢 <10%: Green
- 🟡 10-20%: Amber
- 🔴 >20%: Red

---

### 5.9 Data Export

**FR-9.1:** System shall provide "Export CSV" button for each cluster card to download cluster-specific allocations.

**FR-9.2:** System shall provide "Export Shipment List" button in Section 5 to download weekly replenishment queue.

**FR-9.3:** System shall provide "Export Metrics CSV" button in Section 7 to download performance metrics.

**FR-9.4:** Exported CSVs shall include headers and maintain data types (dates, numbers, strings).

---

### 5.10 Error Handling

**FR-10.1:** System shall display inline error messages for:
- Invalid CSV format
- Missing required columns
- Wrong date ranges
- Missing stores
- Duplicate actuals uploads

**FR-10.2:** System shall provide "Retry" button in agent cards if workflow fails.

**FR-10.3:** System shall provide "View Logs" button to expand detailed error messages.

**FR-10.4:** System shall display network disconnect toast: "⚠️ Connection lost. Retrying..." with auto-retry (3 attempts).

**FR-10.5:** If browser refreshes during agent run, system shall display: "Previous forecast in progress was interrupted. Please re-run forecast."

---

### 5.11 Orchestrator Infrastructure ⭐ NEW in v3.3

**FR-11.1:** System shall extract 5 season parameters from natural language input using Azure OpenAI gpt-4o-mini:
- `forecast_horizon_weeks` (INTEGER): Number of weeks to forecast, range 4-52
- `season_start_date` (DATE): Season start date in YYYY-MM-DD format
- `season_end_date` (DATE): Season end date (calculated from start + horizon)
- `replenishment_strategy` (STRING): Enum ("none" | "weekly" | "bi-weekly")
- `dc_holdback_percentage` (FLOAT): Percentage kept at DC, range 0.0-1.0

**FR-11.2:** System shall validate extracted parameters against business rules:
- Horizon: 4-52 weeks (outside range → 422 Unprocessable Entity)
- Dates: Valid YYYY-MM-DD format, end_date = start_date + (horizon × 7 days)
- Replenishment: Must be one of allowed enum values
- Holdback: 0.0-1.0 range (outside range → 422 Unprocessable Entity)

**FR-11.3:** System shall return 400 Bad Request for incomplete parameter extraction with:
- Error message: "Could not extract all parameters"
- List of missing parameters (e.g., ["season_start_date", "dc_holdback_percentage"])
- Suggestions for user to provide additional information

**FR-11.4:** System shall provide POST /api/orchestrator/extract-parameters endpoint:
- Input: `strategy_description` (STRING, 10-500 characters)
- Output: `SeasonParameters` object with all 5 parameters + extraction_reasoning + confidence_score
- Response time: <5 seconds (includes LLM API call)

**FR-11.5:** System shall coordinate sequential agent execution through AgentHandoffManager with:
- Agent registration by name and handler function (callable validation)
- `call_agent(name, context, timeout)` method for single agent execution
- `handoff_chain(agents[], context)` method for sequential execution where result from Agent N becomes context for Agent N+1
- Timeout enforcement (default: 30 seconds per agent, configurable)
- Execution logging capturing: agent_name, start_time, duration_seconds, status (success/timeout/failed)

**FR-11.6:** System shall assemble context packages for each agent containing:
- **Demand Agent Context:**
  - `parameters` (SeasonParameters): Extracted season parameters
  - `historical_data` (DataFrame): Historical sales with columns [date, category_id, units_sold]
  - `stores_data` (DataFrame): Store attributes with 7 features
  - `category_id` (STRING): Category identifier
- **Inventory Agent Context:**
  - `parameters` (SeasonParameters): Forwarded from Demand Agent
  - `forecast_result` (DICT): Demand Agent's forecast output
  - `stores_data` (DataFrame): Forwarded from Demand Agent
- **Pricing Agent Context:**
  - `parameters` (SeasonParameters): Forwarded from previous agents
  - `forecast_result` (DICT): Demand Agent's output
  - `inventory_plan` (DICT): Inventory Agent's output
  - `actuals_data` (DataFrame): Optional actual sales to date

**FR-11.7:** System shall load historical data from Phase 1 CSV files:
- File path: Configurable via DATA_DIR environment variable
- Required columns: date, store_id, category_id, units_sold
- Validation: Minimum 52 weeks (1 year) of data required for Prophet forecasting
- Caching: Data cached after first load to avoid repeated file reads

**FR-11.8:** System shall complete context assembly in <2 seconds:
- Historical data loading: <1 second (with caching)
- Store data loading: <500ms (with caching)
- Context object validation: <500ms

---

## 6. Non-Functional Requirements

### 6.1 Performance

**NFR-1.1:** System shall complete full 3-agent workflow (Demand → Inventory → Pricing) in <60 seconds.
- **Target:** <60 seconds
- **Measurement:** Backend timing from workflow start to completion
- **Acceptance:** 90% of workflows complete within target

**NFR-1.2:** System shall achieve MAPE 12-18% on Spring 2025 hindcast testing.
- **Target:** 12-18% category-level MAPE
- **Measurement:** `mean(abs(actual - forecast) / actual) × 100%`
- **Acceptance:** MAPE within target range validates forecasting accuracy

**NFR-1.3:** System shall trigger re-forecast with 90%+ accuracy when variance >20%.
- **Target:** 90% correct identification
- **Measurement:** `(true_positives + true_negatives) / total_weeks`
- **Acceptance:** System correctly triggers/skips re-forecast based on threshold

**NFR-1.4:** Frontend Time to Interactive shall be <3 seconds.
- **Target:** <3 seconds
- **Measurement:** Lighthouse performance audit
- **Acceptance:** TTI <3s on simulated 4G network

**NFR-1.5:** WebSocket message latency shall be <100ms.
- **Target:** <100ms
- **Measurement:** Time from backend send to frontend display
- **Acceptance:** 95% of messages delivered within target

**NFR-1.6:** Chart render time shall be <500ms.
- **Target:** <500ms
- **Measurement:** Time from data update to visual render
- **Acceptance:** Recharts render within target for 12-week dataset

---

### 6.2 Usability

**NFR-2.1:** User shall be able to review 3-agent workflow results and approve manufacturing order within 2 minutes.
- **Target:** <2 minutes
- **Measurement:** Time from workflow completion to approval modal submission
- **Acceptance:** User study with 5 users averages <2 min

**NFR-2.2:** Dashboard shall be fully functional on desktop browsers (1280px+ screen width).
- **Target:** Desktop-first design
- **Browsers:** Chrome, Firefox, Edge, Safari (latest 2 versions)
- **Acceptance:** All features work without horizontal scroll or layout breaks

**NFR-2.3:** System shall provide inline validation errors with clear guidance (e.g., "Expected format: date, store_id, quantity_sold").
- **Target:** Zero ambiguous error messages
- **Acceptance:** User can correct errors without external documentation

**NFR-2.4:** Agent progress updates shall appear line-by-line in real-time (not batched).
- **Target:** New line every 2-5 seconds during 60s workflow
- **Acceptance:** User sees 10-15 progress updates per workflow

**NFR-2.5:** System shall support keyboard navigation for all interactive elements.
- **Target:** WCAG 2.1 Level AA compliance
- **Acceptance:** All buttons, inputs, modals accessible via Tab key

---

### 6.3 Reliability

**NFR-3.1:** System uptime shall be 99%+ during development/testing phase.
- **Target:** 99% uptime
- **Measurement:** Backend availability monitoring
- **Acceptance:** <7.2 hours downtime per month

**NFR-3.2:** System shall handle network disconnects gracefully with auto-retry (3 attempts).
- **Target:** 3 auto-retries with exponential backoff
- **Acceptance:** Toast notification shows retry progress, success/failure status

**NFR-3.3:** Database writes shall use transactions to prevent partial updates.
- **Target:** ACID compliance for forecast/allocation/actuals writes
- **Acceptance:** Zero data corruption cases during testing

**NFR-3.4:** System shall log all agent interactions to `workflow_logs` table for debugging.
- **Target:** 100% workflow coverage
- **Acceptance:** Each workflow step logged with timestamp, status, duration

---

### 6.4 Security

**NFR-4.1:** Azure OpenAI API keys shall be stored in environment variables (not hardcoded).
- **Target:** No secrets in source code
- **Acceptance:** `.env` file excluded from git, keys loaded via `python-dotenv`

**NFR-4.2:** CSV uploads shall be validated for malicious content (e.g., formula injection).
- **Target:** Zero CSV injection vulnerabilities
- **Acceptance:** Pydantic validation rejects non-numeric values in numeric columns

**NFR-4.3:** System shall enforce HTTPS in production (local dev allows HTTP).
- **Target:** TLS 1.2+ in production
- **Acceptance:** Browser shows secure connection icon

**NFR-4.4:** Frontend shall implement basic CSRF protection (CORS configuration).
- **Target:** FastAPI CORS middleware configured for frontend origin only
- **Acceptance:** Cross-origin requests blocked except from allowed origin

---

### 6.5 Maintainability

**NFR-5.1:** Code shall follow Python style guide (PEP 8) enforced by Ruff.
- **Target:** Zero Ruff errors/warnings
- **Acceptance:** `uv run ruff check .` passes

**NFR-5.2:** Code shall pass mypy type checking with strict mode.
- **Target:** Zero mypy errors
- **Acceptance:** `uv run mypy .` passes

**NFR-5.3:** Frontend code shall follow ESLint + Prettier configuration.
- **Target:** Zero ESLint errors
- **Acceptance:** `npm run lint` passes

**NFR-5.4:** All agent tools shall have Pydantic schemas for input/output validation.
- **Target:** 100% tool coverage
- **Acceptance:** Each tool function decorated with `@tool` and schema defined

**NFR-5.5:** Database schema shall use hybrid approach (normalized entities + JSON arrays).
- **Target:** Balance of flexibility and normalization
- **Acceptance:** SQLite schema defined with foreign keys, JSON columns for arrays

---

### 6.6 Testability

**NFR-6.1:** Backend shall have unit test coverage for all agent tools.
- **Target:** 80%+ coverage for tool functions
- **Acceptance:** `pytest --cov` reports >80% coverage

**NFR-6.2:** Frontend shall have component test coverage for critical user flows.
- **Target:** 70%+ coverage for approval modals, data upload
- **Acceptance:** Vitest coverage report >70%

**NFR-6.3:** System shall have end-to-end tests for 3 scenarios (normal, high demand, low demand).
- **Target:** 3 E2E test suites
- **Acceptance:** Playwright tests pass for all scenarios

**NFR-6.4:** Mock data shall produce realistic MAPE 12-18% on hindcast testing.
- **Target:** MAPE 12-18%
- **Acceptance:** Generated mock data validated against target range

---

## 7. Acceptance Criteria

### 7.1 Pre-Season Workflow (Week -24)

**AC-1:** User uploads historical sales CSV (2022-2024)
- [ ] System validates and displays preview
- [ ] System auto-detects 3 categories
- [ ] Inline errors shown for invalid format

**AC-2:** User uploads store attributes CSV
- [ ] System validates 50 stores with 7 features
- [ ] System displays preview
- [ ] Inline errors shown for missing features

**AC-3:** User selects category and sets season dates
- [ ] Dropdown populated with detected categories
- [ ] Date picker accepts custom range
- [ ] System auto-calculates 12-week horizon

**AC-4:** User triggers forecast workflow
- [ ] Agent cards expand with real-time progress
- [ ] Workflow completes in <60 seconds
- [ ] Prophet (8,200) + ARIMA (7,800) → Ensemble (8,000)
- [ ] K-means clustering produces 3 clusters
- [ ] Manufacturing order calculated (9,600 = 8,000 × 1.20)

**AC-5:** User reviews and approves manufacturing order
- [ ] Modal displays forecast details
- [ ] Safety stock slider (10-30%) updates order in real-time
- [ ] "Modify" button triggers agent recalculation
- [ ] "Accept" button saves and closes modal
- [ ] Dashboard populates with forecast data

---

### 7.2 Season Start Workflow (Week 0)

**AC-6:** User views forecast summary
- [ ] Section 2 displays: Category, total demand, Prophet/ARIMA/Ensemble, manufacturing order, weekly curve chart
- [ ] "Edit Parameters" button present (display-only in MVP)

**AC-7:** User drills down cluster allocations
- [ ] Section 3 displays 3 cluster cards (Fashion_Forward, Mainstream, Value_Conscious)
- [ ] Each cluster shows: allocation %, total units, store count, characteristics
- [ ] Store allocation table shows: Store ID, Season Total, Initial (55%), Holdback (45%)
- [ ] Multiple clusters can be expanded simultaneously
- [ ] "Export CSV" button downloads cluster-specific data

---

### 7.3 Weekly Monitoring Workflow (Weeks 1-12)

**AC-8:** User uploads weekly actuals
- [ ] "Upload Week X Actuals" button opens modal
- [ ] Modal shows expected format and date range
- [ ] User selects CSV file
- [ ] System validates and processes in <5 seconds
- [ ] Toast notification: "✓ Week X actuals uploaded. Variance: Y%"
- [ ] Chart updates with actual bar
- [ ] Alert banner updates with variance status

**AC-9:** User monitors weekly variance (normal: <10%)
- [ ] Section 4 chart displays forecast line + actual bars
- [ ] Table shows week-by-week variance
- [ ] Alert banner: 🟢 "Tracking well"
- [ ] Green bars in chart

**AC-10:** User monitors elevated variance (10-20%)
- [ ] Alert banner: 🟡 "Elevated variance 15%"
- [ ] Amber bars in chart
- [ ] No auto re-forecast (below 20% threshold)

**AC-11:** System triggers automatic re-forecast (>20%)
- [ ] Alert banner: 🔴 "High variance 25% - Re-forecast triggered"
- [ ] Loading overlay blocks page
- [ ] Auto-scrolls to top
- [ ] Demand Agent card shows re-forecast progress
- [ ] Workflow completes in <60 seconds
- [ ] Section 2 updates with new forecast
- [ ] Section 5 replenishment plan adjusts
- [ ] No human approval required

**AC-12:** User drills down to store-level variance
- [ ] Click Week X row → Expands inline
- [ ] Store breakdown table displays
- [ ] Color-coded variance badges (🟢🟡🔴)
- [ ] "Collapse" button closes expansion

**AC-13:** User approves weekly replenishment
- [ ] Section 5 displays replenishment queue
- [ ] Table shows: Store ID, Current Inventory, Forecast Next Week, Replenish Needed, DC Available
- [ ] Warning icons for insufficient DC inventory
- [ ] "Approve Replenishments" button
- [ ] After approval: "✓ Shipped" status
- [ ] Toast for partial shipments

---

### 7.4 Mid-Season Markdown Workflow (Week 6)

**AC-14:** User views markdown countdown (Weeks 1-5)
- [ ] Section 6 displays countdown
- [ ] Target sell-through: 60% by Week 6

**AC-15:** User reviews markdown recommendation (Week 6)
- [ ] Section 6 activates with sell-through analysis
- [ ] Displays: Total Manufactured, Total Sold, Sell-Through %, Gap
- [ ] Markdown formula: Gap × Elasticity = X%
- [ ] Real-time elasticity slider (1.0-3.0)
- [ ] Preview updates with slider adjustment

**AC-16:** User applies markdown and re-forecast
- [ ] "Apply Markdown & Re-forecast" button
- [ ] Loading overlay blocks page
- [ ] Pricing Agent: ✓ Applying X% markdown
- [ ] Demand Agent: 🔄 Re-forecasting weeks 7-12
- [ ] Section 2 updates with new forecast
- [ ] Section 6 displays historical record
- [ ] Markdown uniform across all stores

---

### 7.5 Post-Season Analysis Workflow

**AC-17:** User views performance metrics dashboard
- [ ] Section 7 displays 3 metric cards:
  - Forecast Accuracy (MAPE, Bias, Re-forecast Trigger Accuracy)
  - Business Impact (Stockouts, Overstock, Markdown Costs, Inventory Turnover)
  - System Performance (Runtime, Approval Rate, Uptime)
- [ ] Metrics update weekly
- [ ] Read-only display

**AC-18:** User accesses detailed performance report
- [ ] "View Detailed Report →" button in Section 7
- [ ] Navigates to `/reports/spring-2025`
- [ ] Report sections: Executive Summary, Forecast Accuracy, Variance Timeline, Business Impact, System Performance, Parameter Recommendations
- [ ] "← Back to Dashboard" button returns to dashboard
- [ ] Read-only, no PDF export or parameter tuning

---

## 8. Success Metrics

### 8.1 Forecast Accuracy (Primary)

**Metric 1: Mean Absolute Percentage Error (MAPE)**
- **Definition:** `mean(abs(actual - forecast) / actual) × 100%`
- **Target:** 12-18% (category-level)
- **Measurement:** Weekly comparison of forecast vs actuals
- **Success Criteria:** MAPE within target range validates realistic forecasting accuracy

**Metric 2: Forecast Bias**
- **Definition:** `mean((forecast - actual) / actual) × 100%`
- **Target:** ±5% (check for consistent over/under-forecasting)
- **Measurement:** Average weekly bias across season
- **Success Criteria:** Bias within ±5% indicates balanced forecast (not systematically high/low)

**Metric 3: Re-Forecast Trigger Accuracy**
- **Definition:** `(true_positives + true_negatives) / total_weeks × 100%`
- **Target:** 90%+ (correctly identify variance >20%)
- **Measurement:** Confusion matrix of variance threshold triggers
- **Success Criteria:** System correctly triggers re-forecast when needed, avoids false alarms

---

### 8.2 Business Impact (Secondary)

**Metric 4: Stockout Reduction**
- **6-Month Target:** 15% reduction vs baseline
- **12-Month Target:** 25% reduction vs baseline
- **Measurement:** Count of stockout events (inventory = 0 when demand exists)
- **Success Criteria:** Fewer stockouts indicate better allocation and replenishment

**Metric 5: Overstock Reduction**
- **6-Month Target:** 10% reduction vs baseline
- **12-Month Target:** 20% reduction vs baseline
- **Measurement:** End-of-season leftover inventory value
- **Success Criteria:** Lower overstock indicates more accurate demand forecasting

**Metric 6: Markdown Cost Reduction**
- **6-Month Target:** 10% reduction vs baseline
- **12-Month Target:** 15% reduction vs baseline
- **Measurement:** Total revenue lost to markdowns
- **Success Criteria:** Lower markdown costs indicate better sell-through management

**Metric 7: Inventory Turnover Improvement**
- **6-Month Target:** 8% improvement vs baseline
- **12-Month Target:** 15% improvement vs baseline
- **Measurement:** `COGS / Average Inventory`
- **Success Criteria:** Higher turnover indicates more efficient inventory management

---

### 8.3 System Performance (Operational)

**Metric 8: Workflow Runtime**
- **Target:** <60 seconds for full 3-agent workflow
- **Measurement:** Time from "Run Forecast" to completion
- **Success Criteria:** 90% of workflows complete within target

**Metric 9: Human Approval Rate**
- **Target:** Track % Modify vs Accept (no fixed target)
- **Measurement:** `(Accept clicks) / (Modify clicks + Accept clicks) × 100%`
- **Success Criteria:** >80% Accept rate indicates high agent reasoning quality

**Metric 10: System Uptime**
- **Target:** 99%+ availability
- **Measurement:** Backend uptime monitoring
- **Success Criteria:** <7.2 hours downtime per month

---

### 8.4 Quantifiable Targets Summary

| Metric | 6-Month Target | 12-Month Target | MVP Validation |
|--------|----------------|-----------------|----------------|
| **MAPE** | 12-18% | 12-18% | ✅ Hindcast test |
| **Bias** | ±5% | ±5% | ✅ Hindcast test |
| **Re-forecast Trigger Accuracy** | 90%+ | 90%+ | ✅ Scenario tests |
| **Stockout Reduction** | 15% | 25% | ❌ Post-MVP |
| **Overstock Reduction** | 10% | 20% | ❌ Post-MVP |
| **Markdown Cost Reduction** | 10% | 15% | ❌ Post-MVP |
| **Inventory Turnover Improvement** | 8% | 15% | ❌ Post-MVP |
| **Workflow Runtime** | <60s | <60s | ✅ Performance test |
| **Human Approval Rate** | Track | 80%+ | ✅ User study |
| **Uptime** | 99%+ | 99%+ | ✅ Monitoring |

**MVP Success Criteria:**
1. ✅ MAPE 12-18% on Spring 2025 hindcast
2. ✅ Variance >20% triggers re-forecast in Week 5 (all scenarios)
3. ✅ Markdown triggered in Week 6 (low demand scenario)
4. ✅ Workflow runtime <60 seconds
5. ✅ User completes 12-week season without critical errors

---

## 9. System Features

### 9.1 Feature Priority Matrix

| Feature | Priority | Complexity | MVP | Post-MVP |
|---------|----------|-----------|-----|----------|
| **CSV Upload & Validation** | P0 | Medium | ✅ | - |
| **Category Auto-Detection** | P0 | Low | ✅ | - |
| **Ensemble Forecasting (Prophet + ARIMA)** | P0 | High | ✅ | - |
| **K-means Clustering (7 features)** | P0 | Medium | ✅ | - |
| **Store Allocation Factors** | P0 | Medium | ✅ | - |
| **Manufacturing Order Approval** | P0 | Medium | ✅ | - |
| **Hierarchical Allocation (55/45 split)** | P0 | Low | ✅ | - |
| **Weekly Actuals Upload** | P0 | Medium | ✅ | - |
| **Variance Monitoring** | P0 | Medium | ✅ | - |
| **Automatic Re-Forecast (>20%)** | P0 | High | ✅ | - |
| **Simple Replenishment Formula** | P0 | Low | ✅ | - |
| **Week 6 Markdown Checkpoint** | P0 | Medium | ✅ | - |
| **Gap × Elasticity Markdown Formula** | P0 | Medium | ✅ | - |
| **Uniform Markdown** | P0 | Low | ✅ | - |
| **Real-Time Agent Progress (WebSocket)** | P0 | High | ✅ | - |
| **Weekly Performance Chart** | P1 | Medium | ✅ | - |
| **Store-Level Variance Drill-Down** | P1 | Medium | ✅ | - |
| **Cluster Allocation Cards** | P1 | Medium | ✅ | - |
| **CSV Export (cluster, replenishment, metrics)** | P1 | Low | ✅ | - |
| **Performance Metrics Dashboard** | P1 | Low | ✅ | - |
| **Detailed Performance Report** | P2 | Medium | ✅ | - |
| **Parameter Tuning UI** | P2 | High | ❌ | ✅ |
| **Multi-Category Support** | P2 | High | ❌ | ✅ |
| **Cluster-Specific Markdowns** | P2 | Medium | ❌ | ✅ |
| **Store-to-Store Transfers** | P3 | High | ❌ | ✅ |
| **Multi-Season Overlap** | P3 | High | ❌ | ✅ |

---

### 9.2 Feature Descriptions

#### 9.2.1 CSV Upload & Validation
**Description:** Users upload 2 CSV files (historical sales 2022-2024, store attributes) to provide training data for forecasting and clustering.

**Business Value:** Enables category-level forecasting without manual data entry, supports CSV as industry-standard format.

**User Interaction:**
1. Click "Upload Historical Sales CSV"
2. Select file from computer
3. System validates and displays preview
4. Repeat for "Upload Store Attributes CSV"

**Technical Implementation:**
- FastAPI endpoint: `POST /api/data/upload/historical`
- Pydantic validation: Required columns, date formats, numeric ranges
- Frontend: React Hook Form + file input

---

#### 9.2.2 Ensemble Forecasting (Prophet + ARIMA)
**Description:** Demand Agent runs Prophet and ARIMA models in parallel, averages results to generate category-level forecast.

**Business Value:** More robust than single-model approach, reduces forecast bias, industry-standard time-series methods.

**User Interaction:**
- Transparent to user (happens during "Run Forecast")
- Agent card shows: "✓ Prophet: 8,200 units | ✓ ARIMA: 7,800 units | ✓ Ensemble: 8,000 units"

**Technical Implementation:**
- Prophet: Meta's forecasting library
- ARIMA: pmdarima (auto-arima)
- Ensemble: Simple average (no confidence weighting)

---

#### 9.2.3 K-means Clustering (7 Features)
**Description:** Demand Agent clusters 50 stores into 3 groups (Fashion_Forward, Mainstream, Value_Conscious) using K-means++ with StandardScaler.

**Business Value:** Data-driven store segmentation, enables hierarchical allocation, improves allocation accuracy vs manual grouping.

**User Interaction:**
- Section 3 displays cluster cards with characteristics
- User validates clusters match business understanding

**Technical Implementation:**
- scikit-learn KMeans (K=3, K-means++ initialization)
- Features: avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
- StandardScaler normalization (mean=0, std=1)

---

#### 9.2.4 Automatic Re-Forecast (>20%)
**Description:** Orchestrator monitors weekly variance and triggers re-forecast workflow when threshold exceeded.

**Business Value:** Adaptive forecasting, captures demand changes mid-season, reduces reliance on perfect initial forecast.

**User Interaction:**
1. User uploads weekly actuals
2. System calculates variance
3. If >20%: Loading overlay blocks page, auto-scrolls to top, agent cards show re-forecast progress
4. No human approval required (auto-applies)

**Technical Implementation:**
- Orchestrator dynamic handoff enabling: `handoff(demand_agent, name="reforecast", enabled=False)`
- When variance >20%: Enable handoff, pass context (actuals, variance reason)
- Demand Agent re-runs ensemble forecast for remaining weeks

---

#### 9.2.5 Gap × Elasticity Markdown Formula
**Description:** Pricing Agent calculates markdown depth using formula: `markdown = (target - actual_sell_through) × elasticity`

**Business Value:** Data-driven markdown recommendations, tunable elasticity parameter, avoids fixed markdown tables.

**User Interaction:**
1. Week 6: Section 6 displays sell-through analysis
2. User adjusts elasticity slider (default: 2.0)
3. Preview updates in real-time
4. Click "Apply Markdown & Re-forecast"

**Technical Implementation:**
```python
gap = target_sell_through - actual_sell_through  # 0.60 - 0.55 = 0.05
markdown_raw = gap × elasticity  # 0.05 × 2.0 = 0.10
markdown_rounded = round(markdown_raw × 20) / 20  # 0.10 → 10%
markdown_depth = min(markdown_rounded, 0.40)  # Cap at 40%
```

---

#### 9.2.6 Real-Time Agent Progress (WebSocket)
**Description:** Backend streams agent progress messages to frontend via WebSocket, displayed line-by-line in agent cards.

**Business Value:** Workflow transparency, user understands what system is doing, reduces perceived wait time.

**User Interaction:**
- Agent cards expand when workflow starts
- Messages appear line-by-line (not batched)
- Example: "✓ Prophet forecast: 8,200 units (15s)"
- Progress bar updates (0-100%)
- Cards auto-collapse 5 seconds after completion

**Technical Implementation:**
- FastAPI WebSocket endpoint: `ws://localhost:8000/ws/agents`
- Message format: `{"agent": "demand", "status": "running", "progress": 80, "step": "Running ARIMA...", "duration": "10s"}`
- Frontend: useWebSocket hook with react-use-websocket

---

#### 9.2.7 Weekly Performance Chart
**Description:** Recharts ComposedChart displays forecast line + actual bars with color-coded variance.

**Business Value:** Visual variance monitoring, quick identification of problem weeks, supports drill-down to store level.

**User Interaction:**
- Hover chart → Tooltip + highlight table row
- Click table row → Expand inline with store breakdown
- Color-coded bars: Green (<10%), Amber (10-20%), Red (>20%)

**Technical Implementation:**
- Recharts ComposedChart (Line + Bar)
- Data: 12 weeks × (forecast, actual, variance)
- Conditional styling based on variance threshold

---

## 10. Data Requirements

### 10.1 Input Data (Provided by User)

#### 10.1.1 Historical Sales Data (Training)
**File:** `historical_sales_2022_2024.csv`

**Columns:**
- `date` (DATE): Sales date, format YYYY-MM-DD, range 2022-01-01 to 2024-12-31
- `category` (STRING): Product category (e.g., Women's Dresses, Men's Shirts, Accessories)
- `store_id` (STRING): Store identifier (S001 to S050)
- `quantity_sold` (INTEGER): Units sold, range 0 to 200
- `revenue` (FLOAT): Total revenue (price × quantity), variable pricing

**Requirements:**
- 2-3 years of data (minimum 2 years)
- 50 stores present in all dates
- No missing values
- Category-level data (not individual SKUs)

**Row Count:** ~54,750 rows (3 years × 365 days × 50 stores)

---

#### 10.1.2 Store Attributes (Clustering Features)
**File:** `store_attributes.csv`

**Columns:**
- `store_id` (STRING): Store identifier (S001 to S050)
- `store_size_sqft` (INTEGER): Store size in square feet, range 3,000 to 15,000
- `median_income` (INTEGER): Area median household income, range $35K to $150K
- `location_tier` (STRING): A/B/C tier (A=Prime, B=Standard, C=Secondary)
- `fashion_tier` (STRING): Premium/Mainstream/Value positioning
- `store_format` (STRING): Mall/Standalone/ShoppingCenter/Outlet
- `region` (STRING): Northeast/Southeast/Midwest/West
- `avg_weekly_sales_12mo` (FLOAT): Historical sales performance (MOST IMPORTANT feature)

**Requirements:**
- Exactly 50 stores
- All 7 features present
- Valid enum values for categorical fields
- Numeric values within expected ranges

**Row Count:** 50 rows (one per store)

---

#### 10.1.3 Weekly Actuals (Testing)
**File:** `actuals_week_XX.csv` (12 files, one per week)

**Columns:**
- `date` (DATE): Sales date, format YYYY-MM-DD, 7 consecutive days (Mon-Sun)
- `store_id` (STRING): Store identifier (S001 to S050)
- `quantity_sold` (INTEGER): Units sold, messier than historical (±20-25% noise)

**Requirements:**
- 7 consecutive days (Mon-Sun)
- All 50 stores present
- Week 1 starts 2025-02-17 (Monday)
- Week 12 ends 2025-05-11 (Sunday)

**Row Count:** ~350 rows per file (50 stores × 7 days)

---

### 10.2 Output Data (Generated by System)

#### 10.2.1 Forecast Object
**Generated by:** Demand Agent

**Fields:**
- `forecast_id` (STRING): Unique identifier
- `category_id` (STRING): FK to categories
- `season` (STRING): Season identifier (e.g., "Spring 2025")
- `total_season_demand` (INTEGER): Total units for season (e.g., 8,000)
- `weekly_demand_curve` (ARRAY): Week-by-week demand (e.g., [650, 720, 680, ...])
- `peak_week` (INTEGER): Week with highest demand
- `cluster_distribution` (ARRAY): Cluster allocations (e.g., [{cluster_id, percentage, total_units}, ...])
- `forecasting_method` (STRING): "ensemble_prophet_arima"
- `models_used` (ARRAY): ["prophet", "arima"]
- `prophet_forecast` (INTEGER): Prophet result (e.g., 8,200)
- `arima_forecast` (INTEGER): ARIMA result (e.g., 7,800)
- `created_at` (DATETIME): Timestamp

---

#### 10.2.2 Allocation Plan
**Generated by:** Inventory Agent

**Fields:**
- `allocation_id` (STRING): Unique identifier
- `forecast_id` (STRING): FK to forecasts
- `manufacturing_qty` (INTEGER): Total to manufacture (e.g., 9,600 = 8,000 × 1.20)
- `safety_stock_percentage` (FLOAT): Fixed 20%
- `initial_allocation_total` (INTEGER): Total 55% to stores (e.g., 5,280)
- `holdback_total` (INTEGER): Total 45% at DC (e.g., 4,320)
- `store_allocations` (ARRAY): Store-level detail (e.g., [{store_id, initial, holdback, total}, ...])
- `created_at` (DATETIME): Timestamp

---

#### 10.2.3 Markdown Recommendation
**Generated by:** Pricing Agent

**Fields:**
- `markdown_id` (STRING): Unique identifier
- `forecast_id` (STRING): FK to forecasts
- `week_applied` (INTEGER): Week number (e.g., 6)
- `sell_through_rate` (FLOAT): Actual sell-through % (e.g., 0.55)
- `target_sell_through` (FLOAT): Target % (e.g., 0.60)
- `gap` (FLOAT): Difference (e.g., 0.05)
- `elasticity_coefficient` (FLOAT): Tunable parameter (e.g., 2.0)
- `markdown_depth` (FLOAT): Calculated % (e.g., 0.10 = 10%)
- `expected_sales_lift` (FLOAT): Estimated impact (e.g., 0.18 = +18%)
- `created_at` (DATETIME): Timestamp

---

### 10.3 Data Validation Rules

**Validation Type 1: Completeness**
- [ ] Historical CSV has 54,750 rows (3 years × 365 days × 50 stores)
- [ ] Store attributes CSV has 50 rows
- [ ] Each weekly actuals CSV has ~350 rows (50 stores × 7 days)
- [ ] No missing values in required columns

**Validation Type 2: Data Quality**
- [ ] `quantity_sold` ≥ 0 (no negative sales)
- [ ] `revenue` = `quantity_sold` × `price` (within ±1% tolerance)
- [ ] `date` is valid and sequential
- [ ] `store_id` matches S001 to S050 format

**Validation Type 3: Format**
- [ ] CSV delimiter: comma (`,`)
- [ ] Date format: `YYYY-MM-DD`
- [ ] Encoding: UTF-8
- [ ] No extra whitespace in columns

**Validation Type 4: Statistical**
- [ ] Women's Dresses: Mean weekly sales 50-150 units/store, StdDev 20-60
- [ ] Men's Shirts: Mean weekly sales 30-100 units/store, StdDev 15-40
- [ ] Accessories: Mean weekly sales 40-120 units/store, StdDev 25-70
- [ ] K-means silhouette score >0.4 (validates distinct clusters)

**Validation Type 5: Pattern**
- [ ] Historical data shows clear seasonality (FFT or autocorrelation test)
- [ ] Women's Dresses peak in Spring/Summer (Mar-Aug avg > Nov-Feb avg)
- [ ] Accessories peak in Nov-Dec (Q4 avg > Q1-Q3 avg)
- [ ] Weekly actuals (2025) have higher variance than historical (2022-2024)

**Validation Type 6: Weekly Actuals**
- [ ] Each actuals file covers exactly 7 consecutive days (Mon-Sun)
- [ ] Week 1 starts 2025-02-17, Week 12 ends 2025-05-11
- [ ] All 50 stores present in every file

---

## 11. Technical Constraints

### 11.1 Technology Stack Constraints

**Backend:**
- Python 3.11+ (required for OpenAI Agents SDK)
- UV package manager (10-100x faster than pip, recommended by OpenAI)
- FastAPI 0.115+ (WebSocket support)
- OpenAI Agents SDK 0.3.3+ (production-ready agentic framework)
- Azure OpenAI Service (gpt-4o-mini via Responses API, not deprecated Chat Completions)
- SQLite 3.45+ (local file-based database, no PostgreSQL for MVP)

**Frontend:**
- TypeScript 5.6+ (type-safe JavaScript)
- React 18.3+ (UI library)
- Vite 5.4+ (fast dev server + bundler)
- Shadcn/ui (accessible component library)
- TanStack Query 5.59+ (server state management)

**Development:**
- Monorepo structure (single repository for backend + frontend)
- UV for Python package management
- npm for frontend package management
- Git for version control

---

### 11.2 Performance Constraints

**Workflow Runtime:**
- Full 3-agent workflow (Demand → Inventory → Pricing) must complete in <60 seconds
- Individual agent runtimes:
  - Demand Agent: <40 seconds (Prophet 15s + ARIMA 10s + Clustering 15s)
  - Inventory Agent: <10 seconds
  - Pricing Agent: <5 seconds
  - Orchestrator overhead: <5 seconds

**Frontend Performance:**
- Time to Interactive: <3 seconds
- WebSocket message latency: <100ms
- Chart render time: <500ms
- First Contentful Paint: <1.5 seconds

**Database Performance:**
- SQLite queries: <100ms for typical reads
- Transaction writes: <200ms

---

### 11.3 Data Constraints

**Input Data:**
- Maximum CSV file size: 50 MB (prevents browser memory issues)
- Historical sales: Minimum 2 years, maximum 5 years
- Store count: Fixed 50 stores (MVP limitation)
- Categories: Maximum 10 detected categories (dropdown performance)

**Output Data:**
- Forecast horizon: Fixed 12 weeks (Archetype 1)
- Cluster count: Fixed 3 clusters (K-means K=3)
- Store allocations: 50 stores × 12 weeks = 600 data points

**Storage:**
- SQLite database: <500 MB expected size for MVP
- No cloud storage (local development only)

---

### 11.4 Integration Constraints

**Azure OpenAI API:**
- Rate limit: 60 requests/minute (gpt-4o-mini tier)
- Token limit: 128K context window
- Latency: <2 seconds per API call (regional dependent)
- Cost: ~$0.50 per 3-agent workflow (estimate)

**WebSocket:**
- Maximum 1 concurrent WebSocket connection per user
- Message size: <10 KB per message
- Heartbeat: 30-second keepalive pings

---

### 11.5 Browser Compatibility

**Supported Browsers:**
- Chrome 120+ (latest 2 versions)
- Firefox 120+ (latest 2 versions)
- Edge 120+ (latest 2 versions)
- Safari 17+ (latest 2 versions)

**Screen Resolutions:**
- Desktop: 1280px+ (primary target)
- Tablet: 768px-1279px (limited support, vertical stacking)
- Mobile: <768px (read-only monitoring, no complex interactions)

---

### 11.6 Security Constraints

**Authentication:**
- MVP: No authentication (local development only)
- Post-MVP: SSO integration required for production

**Data Privacy:**
- CSV uploads stored locally (no cloud transmission)
- Azure OpenAI: No data retention per contract (zero-day policy)
- Database: SQLite file encrypted at rest (OS-level encryption)

**API Security:**
- Azure OpenAI API keys: Environment variables only (no hardcoding)
- CORS: Configured for frontend origin only
- HTTPS: Required in production (TLS 1.2+)

---

## 12. Assumptions & Dependencies

### 12.1 Assumptions

**Business Assumptions:**
1. User has 2+ years of historical sales data at category level (not SKU level)
2. User understands retail terminology (forecast, allocation, markdown, sell-through)
3. Category definitions remain consistent over time (no mid-season reclassification)
4. Store attributes are accurate and up-to-date
5. Weekly actuals are uploaded every Monday (user discipline)

**Technical Assumptions:**
1. Historical data is "clean enough" for Prophet/ARIMA training (±10-15% noise)
2. K-means clustering (K=3) produces meaningful store segments
3. Safety stock 20% is appropriate for fashion retail volatility
4. Markdown elasticity coefficient 2.0 is reasonable starting point
5. SQLite performance is adequate for 50 stores × 12 weeks (600 data points)

**User Assumptions:**
1. User has access to desktop browser (1280px+ screen)
2. User can upload CSV files (comfortable with file formats)
3. User can review and approve decisions within 2 minutes
4. User understands agent reasoning from displayed messages

---

### 12.2 Dependencies

**External Services:**
1. **Azure OpenAI Service**
   - Dependency: API availability and rate limits
   - Risk: Service downtime or rate limit exceeded
   - Mitigation: Implement retry logic (3 attempts), display error messages

2. **Prophet Library (Meta)**
   - Dependency: Prophet forecasting accuracy on fashion retail data
   - Risk: Prophet struggles with high seasonality or sparse data
   - Mitigation: Ensemble with ARIMA, validation on hindcast testing

3. **ARIMA (pmdarima)**
   - Dependency: ARIMA model convergence on noisy data
   - Risk: Model fitting fails on highly volatile data
   - Mitigation: Auto-ARIMA parameter tuning, fallback to Prophet-only if ARIMA fails

**Data Dependencies:**
1. **Historical Sales Data**
   - Dependency: User provides 2+ years of category-level sales
   - Risk: Insufficient data or poor quality
   - Mitigation: Validation checks, inline error messages, minimum 2-year requirement

2. **Store Attributes**
   - Dependency: User provides accurate store attributes (7 features)
   - Risk: Outdated or incorrect attributes
   - Mitigation: Validation checks, user can re-upload updated attributes

3. **Weekly Actuals**
   - Dependency: User uploads actuals every Monday
   - Risk: User forgets or uploads late
   - Mitigation: Dashboard notice "⚠️ Week X actuals pending upload"

**Infrastructure Dependencies:**
1. **Local Development Environment**
   - Dependency: User has Python 3.11+, Node.js 18+, Git
   - Risk: Version incompatibility
   - Mitigation: Clear setup instructions in README, version checks in scripts

2. **UV Package Manager**
   - Dependency: UV installation and compatibility with Python 3.11+
   - Risk: UV installation issues on Windows
   - Mitigation: Fallback to pip if UV fails, troubleshooting guide

---

### 12.3 Risks & Mitigation Strategies

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Azure OpenAI API downtime** | Low | High | Retry logic (3 attempts), fallback to cached forecast |
| **Prophet/ARIMA fails to converge** | Medium | High | Ensemble approach reduces risk, fallback to single model |
| **K-means clustering poor quality** | Medium | Medium | Validate silhouette score >0.4, manual cluster review |
| **User uploads invalid CSV** | High | Low | Inline validation, clear error messages, format guidance |
| **Workflow exceeds 60s target** | Medium | Medium | Optimize Prophet/ARIMA hyperparameters, async processing |
| **SQLite performance degradation** | Low | Medium | Index key columns, transaction batching |
| **Browser refresh during workflow** | Medium | Low | Display "Previous run interrupted" message, re-run workflow |
| **WebSocket disconnect** | Medium | Low | Auto-retry (3 attempts), toast notification |

---

## 13. Out of Scope

### 13.1 Explicitly Out of Scope for MVP

**Multi-Archetype Support:**
- ❌ Archetype 2 (Stable Catalog Retail)
- ❌ Archetype 3 (Continuous Replenishment Retail)
- ❌ Classifier Agent (auto-route to archetype)
- **Reason:** MVP focuses on proving concept with single archetype (Fashion Retail)

**SKU-Level Forecasting:**
- ❌ Individual SKU demand forecasting
- ❌ SKU attributes (color, size, style)
- ❌ New SKU forecasting (no sales history)
- **Reason:** Category-level forecasting is MVP scope, SKU-level adds 100x complexity

**Store-Level Granular Forecasting:**
- ❌ Store × Week direct forecasting (600 predictions)
- ❌ Store-specific seasonality adjustments
- **Reason:** Hierarchical allocation (cluster → store) is more scalable

**Multi-Season Overlap:**
- ❌ Concurrent forecasting for multiple seasons (e.g., Spring + Summer)
- ❌ Leftover inventory carryover to next season
- **Reason:** MVP focuses on single 12-week season

**Store-to-Store Transfers:**
- ❌ Lateral replenishment between stores
- ❌ Emergency stock transfers
- **Reason:** DC-to-store replenishment only for MVP simplicity

**Confidence Scoring:**
- ❌ Forecast confidence intervals (removed in v3.2)
- ❌ Confidence-based approval thresholds
- **Reason:** User decision - "too complicated, I want to just skip this"

**Cluster-Specific Markdowns:**
- ❌ Different markdown % per cluster (e.g., 10% Fashion_Forward, 15% Mainstream)
- **Reason:** Uniform markdown simplifies MVP, cluster-specific adds complexity

**Advanced Features:**
- ❌ Parameter tuning UI (display-only in MVP)
- ❌ PDF export of performance reports
- ❌ Email notifications for variance alerts
- ❌ Mobile app (desktop-first)
- ❌ Multi-user authentication (single-user local dev)
- ❌ Real-time POS data integration (CSV uploads only)
- ❌ External data sources (weather, fashion trends, social media) - optional in MVP

---

### 13.2 Post-MVP Roadmap

**Phase 2 (6-12 months):**
- Multi-archetype support (Archetype 2 + 3)
- Classifier Agent (auto-route based on business characteristics)
- Parameter tuning UI (adjust safety stock, holdback %, elasticity)
- Cluster-specific markdowns
- PDF export of performance reports

**Phase 3 (12-18 months):**
- SKU-level forecasting (hierarchical: category → SKU)
- New SKU forecasting (transfer learning from similar SKUs)
- Store-to-store transfers
- Multi-season overlap management
- Real-time POS data integration (replace CSV uploads)

**Phase 4 (18-24 months):**
- Production deployment (cloud infrastructure)
- Multi-user authentication (SSO)
- Mobile app (responsive design)
- External data sources integration (weather, fashion trends)
- AI-powered parameter recommendations (auto-tune based on performance)

---

## 14. Release Plan

### 14.1 MVP Timeline (12 Weeks)

| Week | Milestone | Deliverables |
|------|-----------|-------------|
| **1-2** | Environment Setup & Data Pipeline | - UV + Vite project setup<br>- Mock data generation script<br>- CSV upload endpoints<br>- Validation suite (6 types) |
| **3-4** | Demand Agent - Forecasting | - Prophet + ARIMA ensemble implementation<br>- Historical sales data loading<br>- Category-level forecast output<br>- Unit tests (80%+ coverage) |
| **5-6** | Demand Agent - Clustering & Allocation | - K-means clustering (7 features)<br>- StandardScaler normalization<br>- Store allocation factors (70% hist + 30% attr)<br>- Cluster distribution calculation |
| **7-8** | Inventory Agent - Manufacturing & Allocation | - Manufacturing order calculation (20% safety stock)<br>- Hierarchical allocation (55/45 split)<br>- Initial store allocation (2-week minimum)<br>- Human-in-the-loop approval modal |
| **9** | Inventory Agent - Replenishment | - Simple replenishment formula<br>- Weekly replenishment queue<br>- DC inventory tracking<br>- Partial shipment handling |
| **10** | Pricing Agent - Markdown Logic | - Week 6 checkpoint implementation<br>- Gap × Elasticity formula<br>- Real-time elasticity slider<br>- Uniform markdown application |
| **11** | Orchestrator - Workflow Coordination | - Sequential agent handoffs<br>- Variance monitoring (>20% threshold)<br>- Dynamic re-forecast handoff enabling<br>- WebSocket real-time updates |
| **12** | Validation & Testing | - Hindcast testing (Spring 2024)<br>- 3 scenario tests (normal, high demand, low demand)<br>- MAPE 12-18% validation<br>- E2E tests (Playwright) |

---

### 14.2 Release Criteria

**Code Quality:**
- [ ] Backend: Zero Ruff errors/warnings
- [ ] Backend: Zero mypy type errors
- [ ] Frontend: Zero ESLint errors
- [ ] Frontend: Prettier formatted

**Testing:**
- [ ] Backend unit tests: 80%+ coverage
- [ ] Frontend component tests: 70%+ coverage
- [ ] E2E tests: 3 scenarios pass (normal, high demand, low demand)
- [ ] Hindcast testing: MAPE 12-18% on Spring 2024

**Performance:**
- [ ] Workflow runtime: <60 seconds (90% of runs)
- [ ] Frontend TTI: <3 seconds
- [ ] WebSocket latency: <100ms

**Documentation:**
- [ ] README with setup instructions
- [ ] API documentation (FastAPI auto-generated)
- [ ] Data specification (CSV formats)
- [ ] Architecture diagram

**Deployment:**
- [ ] Local development environment working
- [ ] Mock data generated and validated
- [ ] .env.example provided for Azure OpenAI keys

---

### 14.3 Launch Checklist

**Pre-Launch:**
- [ ] All MVP features implemented and tested
- [ ] Mock data generated (3 scenarios)
- [ ] User study with 5 participants (target: 80%+ approval rate)
- [ ] Performance benchmarking (workflow runtime <60s)
- [ ] Security review (no hardcoded secrets, HTTPS in production)

**Launch:**
- [ ] Deploy to local development environment
- [ ] Provide user training materials (CSV format guides)
- [ ] Monitor system performance (uptime, runtime, errors)

**Post-Launch:**
- [ ] Collect user feedback (approval rates, pain points)
- [ ] Analyze MAPE on real Spring 2025 season (if available)
- [ ] Identify parameter tuning opportunities (safety stock, elasticity)
- [ ] Plan Phase 2 features (multi-archetype, parameter tuning UI)

---

## 15. Appendix

### 15.1 Glossary

**Category-Level Forecasting:** Predicting aggregate demand for a product category (e.g., "Women's Dresses") rather than individual SKUs.

**Hierarchical Allocation:** Top-down allocation approach (category → cluster → store).

**Store Clustering:** Grouping stores using K-means (K=3) based on 7 features with StandardScaler normalization.

**Holdback Percentage:** % of inventory kept at DC instead of allocated to stores (45% for Archetype 1).

**MAPE:** Mean Absolute Percentage Error - forecast accuracy metric.

**Markdown:** Price reduction to accelerate sales (calculated via Gap × Elasticity formula).

**Replenishment:** Periodic shipment from DC to stores to restock inventory (simple formula: forecast - inventory).

**Safety Stock:** Extra inventory buffer to avoid stockouts (20% above forecast for Archetype 1).

**Sell-Through Rate:** % of manufactured inventory sold by a given week.

**Variance Threshold:** % deviation that triggers re-forecasting (20% for Archetype 1).

**Gap × Elasticity:** Markdown formula where `Markdown = (target - actual) × elasticity_coefficient`.

**Ensemble Forecasting:** Prophet + ARIMA run in parallel, results averaged.

**K-means++:** K-means initialization algorithm that improves cluster quality.

**StandardScaler:** Normalization technique (mean=0, std=1) for feature scaling before clustering.

**Responses API:** OpenAI's production-ready API for agentic workflows (successor to Chat Completions).

**Context-Rich Handoffs:** Passing forecast/allocation objects directly between agents (no database queries).

**Dynamic Handoff Enabling:** Re-forecast handoff enabled only when variance >20%.

**Human-in-the-Loop:** Critical decisions require approval (Modify/Accept modals).

**WebSocket:** Real-time bidirectional communication protocol for agent progress streaming.

---

### 15.2 Reference Documents

**Product Brief v3.2:**
- `docs/04_MVP_Development/planning/1_product_brief_v3.3.md`
- System overview, business value, agent responsibilities, MVP scope

**Process Workflow v3.2:**
- `docs/04_MVP_Development/planning/2_process_workflow_v3.3.md`
- 5-phase workflow, concrete examples, scenario walkthroughs

**Technical Architecture v3.2:**
- `docs/04_MVP_Development/planning/architecture/technical_architecture_v3.2.md`
- Tech stack, data models, API contracts, ML approach

**Frontend Specification v3.2:**
- `docs/04_MVP_Development/planning/design/front-end-spec_v3.2.md`
- UI/UX design, wireframes, component library, Linear Dark Theme

**Data Specification v3.2:**
- `docs/04_MVP_Development/planning/data/data_specification_v3.2.md`
- Mock data generation, CSV formats, validation rules, scenario definitions

---

### 15.3 Contact Information

**Product Owner:** Independent Study Project
**Last Updated:** 2025-10-14
**Version:** 3.2
**Status:** Ready for Development ✅

---

**End of Product Requirements Document v3.2**
