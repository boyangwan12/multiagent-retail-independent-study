# Frontend UI/UX Specification - Parameter-Driven Demand Forecasting & Inventory Allocation System

**Version:** 3.3
**Date:** 2025-10-16
**Status:** Ready for Implementation
**Design System:** Linear Dark Theme
**Core Innovation:** Natural language parameter extraction + Agent autonomous reasoning

---

## Table of Contents

1. [Introduction](#introduction)
2. [UX Goals & Principles](#ux-goals--principles)
3. [Information Architecture](#information-architecture)
4. [User Flows](#user-flows)
5. [Wireframes & Key Screens](#wireframes--key-screens)
6. [Component Library](#component-library)
7. [Design System (Linear Dark Theme)](#design-system-linear-dark-theme)
8. [Accessibility](#accessibility)
9. [Responsiveness](#responsiveness)
10. [Animation & Micro-interactions](#animation--micro-interactions)
11. [Performance Considerations](#performance-considerations)
12. [Data Generation Requirements](#data-generation-requirements)
13. [Next Steps & Handoff](#next-steps--handoff)

---

## 1. Introduction

### Purpose

This document defines the complete user experience and visual design for the **Parameter-Driven Demand Forecasting & Inventory Allocation System** (v3.3 MVP). The system uses natural language parameter extraction combined with a 3-agent architecture (Demand, Inventory, Pricing) coordinated by an Orchestrator to forecast category-level demand and optimize store allocations. The system adapts to different retail strategies (e.g., Zara-style fast fashion, standard retail) without code changes by having agents autonomously reason about extracted parameters.

### Target User Persona

**Primary User: Merchandise Planner (Fashion Retail)**
- Forecasts demand and sets inventory targets for seasonal categories
- Makes manufacturing order approvals (6 months ahead)
- Reviews weekly replenishments and markdown decisions
- Needs: Fast decision-making (2 min approval), workflow transparency, hierarchical drill-down

**Secondary Users:**
- Allocation Analyst (reviews store distributions)
- Merchandising Manager (final approval authority)

### Scope (MVP)

- **⭐ NEW: Natural language strategy input** - Users describe planning strategy in free-form text, LLM extracts 5 key parameters
- **⭐ NEW: Agent reasoning display** - Show how agents adapt behavior based on parameters
- **Single category:** Auto-detected from CSV upload (e.g., Women's Dresses, Men's Shirts, Accessories)
- **50 stores** across 3 clusters (Fashion_Forward, Mainstream, Value_Conscious)
- **Configurable season length:** Default 12 weeks (e.g., Spring 2025: March 1 - May 23)
- **6 operational phases:** Phase 0 (Parameter Gathering) → Pre-season → Season Start → In-Season → Mid-Season → Post-Season
- **Primary test scenario:** Zara-style fast fashion (0% holdback, no replenishment, 100% initial allocation)

---

## 2. UX Goals & Principles

### Usability Goals

1. **Fast Decision Making**: Review 3-agent workflow results and approve decisions within 2 minutes
2. **Workflow Transparency**: Real-time WebSocket updates show which agent is running and what it's doing
3. **Error Prevention**: Human-in-the-loop approvals for critical decisions (Modify iterative + Accept, no Reject)
4. **Hierarchical Navigation**: Category → Cluster → Store drill-down matches forecasting hierarchy
5. **Performance Awareness**: System completes 3-agent workflow in <60 seconds (success metric)

### Design Principles

1. **Single-Page Dashboard** - All information on one scrollable page (no multi-page navigation)
2. **Card-Based Workflow** - 3 agent cards show real-time progress with detailed WebSocket updates
3. **Expandable Hierarchy** - Category summary → Cluster cards → Store tables (click to expand)
4. **Transparent Agent Behavior** - Show technical details (Prophet 8,200 + ARIMA 7,800 = 8,000 avg)
5. **Modal Approvals** - Human-in-the-loop decisions appear as modals over dashboard

### Key Interactions

- **Agent Progress**: WebSocket messages load line-by-line in agent cards (not all at once)
- **Variance-Driven**: Color-coded alerts (🟢 <10%, 🟡 10-20%, 🔴 >20% triggers auto re-forecast)
- **Expandable Rows**: Click weekly table rows to see store-level variance breakdown
- **Direct Actions**: "Apply Markdown" button → No confirmation modal, auto-scrolls to agents
- **Session Persistence**: Browser refresh during agent run → Progress lost, must re-run (trade-off for MVP simplicity)

---

## 3. Information Architecture

### Single-Page Dashboard Structure

The dashboard is a **vertically scrollable single page** with 8 sections (NEW: Phase 0 at top):

```
┌─────────────────────────────────────────────────────┐
│ ⭐ SECTION 0: Parameter Gathering (Phase 0)        │ ← NEW in v3.3
│ • FREE-FORM TEXT INPUT (500 char limit)            │
│ • "Extract Parameters" button                      │
│ • Parameter confirmation modal                     │
│ • Confirmed parameters display (read-only banner)  │
│ • Agent reasoning preview                          │
│ • "Edit Parameters" returns to this section        │
├─────────────────────────────────────────────────────┤
│ SECTION 1: Fixed Header (Sticky)                   │ ← Always visible
│ • Phase indicator (Week X of 12)                   │
│ • Variance alert banner (🟢🟡🔴)                    │
│ • 3 Agent cards (Last run + Next run)              │
│ • Expands with live progress when running          │
│ • Auto-collapses 5s after completion               │
├─────────────────────────────────────────────────────┤
│ SECTION 2: Forecast Summary (Expanded by default)  │ ← Scroll to see
│ • Category forecast (8,000 units)                  │
│ • Prophet/ARIMA/Ensemble details                   │
│ • Parameter context displayed                      │
│ • Mini bar chart for weekly curve                  │
│ • "Edit Parameters" button                         │
├─────────────────────────────────────────────────────┤
│ SECTION 3: Cluster Cards (Stacked vertically)      │
│ • Fashion_Forward / Mainstream / Value_Conscious   │
│ • Detailed cluster stats                           │
│ • Expandable store tables (all columns visible)    │
│ • Export CSV per cluster                           │
├─────────────────────────────────────────────────────┤
│ SECTION 4: Weekly Performance Chart                │
│ • Recharts: Forecast line + Actual bars            │
│ • Hover: Tooltip + highlight table row             │
│ • Variance >20%: Red background                    │
│ • Click table row: Inline store-level breakdown    │
├─────────────────────────────────────────────────────┤
│ SECTION 5: Replenishment Queue (Always expanded)   │
│ • Current week's shipments                         │
│ • Warning icons for insufficient DC inventory      │
│ • Read-only, agents decide quantities              │
│ • Checkmarks after approval                        │
├─────────────────────────────────────────────────────┤
│ SECTION 6: Markdown Decision (Week 6)              │
│ • Countdown before Week 6                          │
│ • Gap × Elasticity calculator                      │
│ • Real-time slider preview                         │
│ • Direct action (auto-scrolls to agents)           │
│ • Historical record after applied                  │
├─────────────────────────────────────────────────────┤
│ SECTION 7: Performance Metrics (Bottom)            │
│ • 3 metric cards (Forecast/Business/System)        │
│ • Real-time weekly updates                         │
│ • Read-only display                                │
│ • "View Detailed Report" → /reports/spring-2025    │
└─────────────────────────────────────────────────────┘
```

### Secondary Page: Performance Report

**URL:** `/reports/spring-2025`

**Purpose:** Post-season analysis (read-only, no user interactions)

**Sections:**
- Executive Summary
- Forecast Accuracy Deep Dive (MAPE by week/cluster, bias analysis)
- Variance & Re-forecast Events Timeline
- Business Impact (stockouts, overstock, markdown analysis)
- System Performance (runtimes, approval rates)
- Parameter Recommendations (display only, no editing)

**Navigation:** `← Back to Dashboard` button only

---

## 4. User Flows

### Flow 0: Parameter Gathering (Phase 0) ⭐ NEW in v3.3

**User Goal:** Describe season planning strategy and configure system parameters

**Steps:**

1. User lands on dashboard
2. **Section 0 displays** at top (before any other sections):
   ```
   ┌─────────────────────────────────────────────┐
   │ ⭐ Configure Your Season Strategy           │
   ├─────────────────────────────────────────────┤
   │ Describe your planning approach:            │
   │ ┌─────────────────────────────────────────┐ │
   │ │ I'm planning a 12-week spring fashion  │ │ Textarea
   │ │ season starting March 1st. Send all    │ │ 500 char limit
   │ │ inventory to stores at launch with no  │ │
   │ │ DC holdback. I don't want ongoing      │ │
   │ │ replenishment - just one initial       │ │
   │ │ allocation. Check for markdown         │ │
   │ │ opportunities at week 6 if we're below │ │
   │ │ 60% sell-through.                      │ │
   │ └─────────────────────────────────────────┘ │
   │ 245 / 500 characters                        │
   │                                             │
   │ [Extract Parameters]  ⓘ Help               │
   └─────────────────────────────────────────────┘
   ```

3. User clicks **[Extract Parameters]** button
4. **Loading indicator** (2-5 seconds): "Extracting parameters from your description..."
5. **Parameter Confirmation Modal appears:**
   ```
   ┌─────────────────────────────────────────────┐
   │ Review Extracted Parameters             [X] │
   ├─────────────────────────────────────────────┤
   │ ✓ Successfully extracted 5 key parameters: │
   │                                             │
   │ 1. Forecast Horizon: 12 weeks              │
   │ 2. Season Dates: March 1, 2025 - May 23   │
   │ 3. Replenishment: None (one-shot)         │
   │ 4. DC Holdback: 0% (100% to stores)       │
   │ 5. Markdown: Week 6, 60% threshold        │
   │                                             │
   │ ▼ Extraction Reasoning                     │
   │ User explicitly stated: 12-week season     │
   │ starting March 1st, no DC holdback (0%),   │
   │ no ongoing replenishment, Week 6 markdown  │
   │ checkpoint at 60% threshold.               │
   │                                             │
   │ [Re-Extract] [Confirm & Continue]          │
   └─────────────────────────────────────────────┘
   ```

6. **Option A:** User clicks **[Confirm & Continue]**
   - Parameters saved
   - Modal closes
   - **Section 0 collapses** to read-only banner:
     ```
     ┌─────────────────────────────────────────┐
     │ ✓ Parameters Confirmed:                 │
     │ 12 weeks | Mar 1 - May 23 | No replen  │
     │ | 0% holdback | Week 6 markdown (60%)   │
     │ [Edit Parameters]                       │
     └─────────────────────────────────────────┘
     ```
   - **Agent Reasoning Preview section displays:**
     ```
     ┌─────────────────────────────────────────┐
     │ How Agents Will Adapt:                  │
     │ • Demand: "No replenishment → +5%      │
     │   safety stock buffer"                  │
     │ • Inventory: "0% holdback → 100% Week  │
     │   0, skip replenishment phase"          │
     │ • Pricing: "Week 6 @ 60% → Gap ×       │
     │   Elasticity markdown"                  │
     └─────────────────────────────────────────┘
     ```
   - User proceeds to Flow 1 (data upload)

7. **Option B:** User clicks **[Re-Extract]**
   - Returns to textarea
   - User modifies input
   - Clicks Extract again

**Error Handling:**
- Incomplete extraction → Modal shows: "⚠️ Could not extract: Season start date, Markdown threshold. Please specify."
  - User can manually input missing fields
- Network error → Toast: "❌ Extraction failed. Retry or contact support."

**Key UX Notes:**
- Phase 0 MUST complete before any other workflow steps
- Parameters persist throughout session
- "Edit Parameters" button returns user to Phase 0 at any time

---

### Flow 1: Pre-Season Forecast & Manufacturing Approval (Week -24)

**User Goal:** Generate forecast and approve manufacturing order

**Steps:**

1. User lands on dashboard
2. Click "Upload Historical Sales CSV"
   - System validates & parses (must contain: date, category, store_id, quantity_sold)
   - Shows preview: "✓ 10,243 rows | Categories detected: Women's Dresses, Men's Shirts, Accessories"
3. Click "Upload Store Attributes CSV"
   - System validates: 50 stores, 7 features (avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region)
4. Category dropdown auto-populates (detected from CSV)
5. User selects "Women's Dresses"
6. Season date picker: Start 2025-03-01, End 2025-05-23
7. Forecast horizon auto-calculates: 12 weeks
8. Click "Run Forecast" button
9. **Agent Progress (60 seconds):**
   - Section 1: Agent cards expand
   - WebSocket messages load **line-by-line**:
     - ✓ Loading historical data (2s)
     - ✓ Prophet forecast: 8,200 units (15s)
     - ⏳ ARIMA forecast: Running... (10s)
     - ✓ ARIMA forecast: 7,800 units (10s)
     - ✓ Ensemble averaging: 8,000 units (2s)
     - ⏳ K-means clustering (K=3)...
     - ✓ Clustering complete: 3 clusters (15s)
     - ✓ Calculating store allocation factors... (8s)
     - ✓ Manufacturing order: 9,600 units (2s)
10. **Manufacturing Approval Modal appears:**
    - Shows: Total forecast 8,000 | Prophet 8,200 | ARIMA 7,800 | Safety stock 20% | Manufacturing order 9,600
    - Adjustable: Safety stock slider (10-30%)
    - Actions: [Modify] [Accept]
11. User clicks "Accept"
12. Dashboard populates with forecast data
13. Sections 2-7 now show data

**Error Handling:**
- CSV invalid → Inline error with expected format
- Agent fails → Show "Retry" button in agent card
- Browser refresh during run → Progress lost, show "Previous run interrupted. Start new forecast."

---

### Flow 2: Weekly Monitoring & Variance Response (Weeks 1-12)

**User Goal:** Monitor forecast vs. actuals, respond to variance alerts

**Prerequisites:** Each week, user must upload actual sales data before variance analysis can occur.

---

#### **Flow 2A: Upload Weekly Actuals** (Required Every Monday)

**User Goal:** Input actual sales data from completed week

**Steps:**

1. User logs in on Monday of Week 4
2. Dashboard shows Section 4 with notice: "⚠️ Week 3 actuals pending upload"
3. User clicks **[Upload Week 3 Actuals]** button
4. **Upload Modal appears:**
   ```
   ┌─────────────────────────────────────────────┐
   │ Upload Week 3 Actuals                  [X] │
   ├─────────────────────────────────────────────┤
   │ Week: 3 (2025-03-08 to 2025-03-14)         │
   │                                             │
   │ Expected format:                            │
   │ • Columns: date, store_id, quantity_sold   │
   │ • Date range: 7 days (Mon-Sun)             │
   │ • Rows: ~350 (50 stores × 7 days)          │
   │                                             │
   │ [Choose CSV File]  actuals_week_3.csv      │
   │                                             │
   │ [Cancel]  [Upload & Calculate Variance]    │
   └─────────────────────────────────────────────┘
   ```
5. User selects `actuals_week_3.csv` from computer
6. Clicks **[Upload & Calculate Variance]**
7. **System processing (5 seconds):**
   - Validates date range matches Week 3
   - Validates all 50 stores present
   - Aggregates daily sales to weekly totals per store
   - Calculates category-level variance
   - Updates database
8. **Upload success:**
   - Toast: "✓ Week 3 actuals uploaded. Variance: 8%"
   - Section 4 chart updates: Actual bar appears for Week 3 (green)
   - Alert banner updates: "🟢 Variance 8% - Tracking well"
   - Dashboard ready for next workflow step

**Error Handling:**
- Wrong date range → "❌ Date range mismatch. Expected 2025-03-08 to 2025-03-14"
- Missing stores → "❌ Missing data for stores: S15, S22, S38"
- Duplicate upload → "⚠️ Week 3 actuals already uploaded. Overwrite existing data?"
- Invalid format → "❌ Missing required columns: date, store_id, quantity_sold"

---

#### **Flow 2B: Variance Analysis Scenarios** (After Actuals Uploaded)

**Scenario A: Normal Week (🟢 Variance <10%)**
1. User opens dashboard Week 3 (after uploading actuals via Flow 2A)
2. Views Section 4: Weekly chart (now shows actual bar for Week 3)
3. Alert banner: "🟢 Variance 8% - Tracking well"
4. Scrolls to Section 5: Replenishment Queue
5. Reviews 12 stores needing replenishment
6. Clicks "Approve Replenishments"
7. Rows show ✓ Shipped status
8. Waits for next week (must upload Week 4 actuals next Monday)

**Scenario B: Elevated Variance (🟡 10-20%)**
1. Alert banner: "🟡 Variance elevated 15%"
2. User clicks Week 3 row in table
3. Row expands inline → Shows store-level breakdown:
   - S01: +25% 🔴 (problem store)
   - S02: 0% 🟢
   - S07: -11% 🟡
4. User notes S01 variance, monitors closely
5. No action needed yet (below 20% threshold)

**Scenario C: High Variance - Auto Re-forecast (🔴 >20%)**
1. Alert banner: "🔴 High variance 25% - Re-forecast triggered"
2. **Loading overlay blocks entire page**
3. Auto-scrolls to top
4. Demand Agent card expands with progress:
   - ⏳ Re-forecasting weeks 4-12...
   - ✓ Prophet: 10,800 units
   - ✓ ARIMA: 10,200 units
   - ✓ Ensemble: 10,500 units (new forecast)
5. 60 seconds progress
6. Loading overlay disappears
7. Section 2 updates: New forecast 10,500 (was 8,000)
8. Section 5 updates: Replenishment plan adjusted
9. User reviews updated allocations
10. Proceeds with replenishment approval

**Key Behavior:**
- Variance >20% triggers **automatic** re-forecast (no user action needed)
- Re-forecast applies automatically (no approval modal per earlier decisions)
- User can't cancel re-forecast once triggered

---

### Flow 3: Week 6 Markdown Decision

**User Goal:** Review sell-through and approve markdown

**Timeline:**

**Weeks 1-5:** Section 6 shows countdown
```
📅 Markdown Checkpoint - Week 6 (in 3 weeks)
Countdown: 3 weeks until checkpoint
Target Sell-Through: 60% by Week 6
```

**Week 6:** Section 6 activates
```
⚠️ Week 6 Markdown Checkpoint - Action Required

Sell-Through Analysis:
  Total Manufactured: 9,600 units
  Total Sold (W1-W6): 5,280 units
  Sell-Through: 55% (Target: 60%)
  Gap: 5 percentage points

Markdown Recommendation:
  Formula: Gap × Elasticity = 0.05 × 2.0 = 10%
  Application: Uniform across all stores
  Expected Sales Lift: +18%

Elasticity Coefficient: [●─────] 2.0 ← Real-time slider

[Apply Markdown & Re-forecast]
```

**Steps:**

1. User reviews sell-through (55% vs 60% target)
2. Sees recommendation: 10% markdown
3. **Option A:** Accepts recommendation
   - Clicks "Apply Markdown & Re-forecast"
   - Loading overlay blocks page
   - Auto-scrolls to top
   - Pricing Agent card: ✓ Applying 10% markdown
   - Demand Agent card: 🔄 Re-forecasting weeks 7-12...
   - 60 seconds progress
   - Section 2 updates with new forecast
   - Section 6 updates: "✓ 10% Markdown Applied (Week 6)"
4. **Option B:** Adjusts elasticity first
   - Moves slider 2.0 → 2.5
   - Preview updates in real-time: "12.5% markdown"
   - Then clicks "Apply Markdown & Re-forecast"

**Weeks 7-12:** Section 6 shows historical record
```
✓ 10% Markdown Applied (Week 6)

Historical Record:
Applied: Week 6 | Depth: 10% | Elasticity: 2.0
Expected Lift: +18% | Re-forecast: Completed ✓
```

---

### Flow 4: Error Recovery

**CSV Upload Errors:**
- Invalid format → Inline error: "❌ Missing required columns: date, category, store_id, quantity_sold"
- User fixes CSV → Re-uploads

**Agent Run Failures:**
- Agent card shows: "❌ Forecast failed: Insufficient historical data"
- "Retry" button appears → User clicks → Re-runs agents
- "View Logs" button → Expands detailed error log

**Network Disconnect:**
- Toast: "⚠️ Connection lost. Retrying..."
- Auto-retry 3 times
- Success → Toast: "✓ Reconnected"
- Fail → Modal: "Cannot connect. Check internet and refresh page."

**DC Inventory Insufficient:**
- Replenishment table: S15 needs 10 units, DC has 5
- Shows: ⚠️ 5 (warning icon with available quantity)
- User clicks "Approve" anyway
- Toast: "⚠️ Partial shipment approved. Manual restock needed for S15."

**Browser Refresh During Agent Run:**
- Page loads
- Shows message: "Previous forecast in progress was interrupted. Please re-run forecast."
- "Start New Forecast" button appears

---

### Flow 5: Post-Season Performance Review

**Entry Point:** User clicks "View Detailed Report →" from Section 7

**Steps:**

1. Browser navigates to `/reports/spring-2025`
2. New page loads (full-page report)
3. User scrolls through sections:
   - Executive Summary
   - MAPE by Week chart
   - MAPE by Cluster table
   - Variance timeline
   - Stockout/Overstock analysis
   - Markdown impact
   - System performance metrics
   - Parameter recommendations (display only)
4. User reviews report (read-only, no interactions)
5. Clicks "← Back to Dashboard"
6. Returns to main dashboard

**Note:** No PDF export, no parameter tuning actions on this page (display only per requirements).

---

## 5. Wireframes & Key Screens

### Section 1: Fixed Header & Agent Cards (Sticky)

```
┌─────────────────────────────────────────────────────┐
│ 🎯 Demand Forecasting System - Spring 2025         │ bg-[#0D0D0D]
│ Phase: Week 3 of 12 (In-Season Monitoring)         │ text-white
│ Alert: 🟢 Variance 8% - Tracking well              │ text-[#00D084]
├─────────────────────────────────────────────────────┤
│ ┌───────────────┐ ┌───────────────┐ ┌───────────┐ │
│ │ Demand Agent  │ │Inventory Agent│ │Pricing Agt│ │ bg-[#1A1A1A]
│ │               │ │               │ │           │ │ border-[#2A2A2A]
│ │Last: Week 3   │ │Last: Week 3   │ │Next: Week 6│ text-[#6B7280]
│ │Forecast: 8,000│ │Replenish: 12  │ │Markdown:  │ │ font-mono
│ │Status: ✓      │ │stores ✓       │ │Pending    │ │ text-white
│ │               │ │               │ │           │ │
│ │Next: Week 4   │ │Next: Week 4   │ │           │ │
│ │Check variance │ │Plan shipments │ │           │ │
│ └───────────────┘ └───────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────┘

When running (WebSocket line-by-line updates):
┌───────────────────────────────────────────────────┐
│ Demand Agent: Running Re-forecast... 🔄           │ text-[#5B8DEF]
│ ████████░░ 80%                                    │ bg-[#5B8DEF]
│                                                   │
│ ✓ Loading historical data (2s)                   │ text-[#00D084]
│ ✓ Prophet forecast: 8,200 units (15s)            │ text-[#00D084]
│ ⏳ ARIMA forecast: Running... (10s)               │ text-[#9CA3AF]
│ ⏸ Ensemble averaging: Waiting...                  │ text-[#6B7280]
│ ⏸ K-means clustering: Waiting...                  │ text-[#6B7280]
└───────────────────────────────────────────────────┘
```

**Sticky Behavior:**
- Header stays at top when scrolling (`sticky top-0 z-50`)
- Agent cards always visible (no minimize)

---

### Section 2: Forecast Summary

```
┌─────────────────────────────────────────────────────┐
│ [▼] Category Forecast Details                      │ text-[#9CA3AF]
├─────────────────────────────────────────────────────┤
│ Women's Dresses - Spring 2025 (12 weeks)           │ text-white
│                                                     │
│ Total Season Forecast: 8,000 units                 │ font-mono text-2xl
│ Prophet: 8,200 | ARIMA: 7,800 | Method: Ensemble  │ text-[#6B7280]
│ Manufacturing Order: 9,600 units (20% safety) ✓    │ text-[#00D084]
│                                                     │
│ Weekly Demand Curve:                               │
│ ▂▅▃▂▂▁▁▁▁▁▁▁ (mini bar chart)                      │ Recharts 400x60px
│                                                     │
│ [Edit Parameters]                                   │ Button outline
└─────────────────────────────────────────────────────┘
```

**Expanded by default:** `defaultOpen={true}` on Collapsible

---

### Section 3: Cluster Cards (Stacked)

```
┌─────────────────────────────────────────────────────┐
│ Store Allocations by Cluster                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─────────────────────────────────────────────────┐│
│ │ [▼] Fashion_Forward Cluster                     ││ Accordion
│ │                                                 ││ bg-[#1A1A1A]
│ │ 3,840 units | 20 stores | 40% of total         ││ text-white
│ │                                                 ││
│ │ Cluster Characteristics:                        ││
│ │ • Avg Income: $95,000 | Avg Size: 18,000 sqft  ││ text-[#9CA3AF]
│ │ • Location: Urban/High-end malls (Tier A)      ││
│ │ • Fashion Tier: Premium | Avg Weekly: 285u     ││
│ │                                                 ││
│ │ Store Allocation Table:                         ││ TanStack Table
│ │ ┌──────┬────────┬─────────┬──────────┬────────┐││
│ │ │Store │ Season │ Initial │ Holdback │ Attrs  │││ text-[#6B7280]
│ │ │  ID  │  Total │ (55%)   │  (45%)   │        │││ header
│ │ ├──────┼────────┼─────────┼──────────┼────────┤││
│ │ │ S01  │  211   │   116   │    95    │ [View] │││ text-white
│ │ │ S02  │  192   │   106   │    86    │ [View] │││ font-mono
│ │ │ S07  │  138   │    76   │    62    │ [View] │││
│ │ │ ...  │  ...   │   ...   │   ...    │  ...   │││
│ │ └──────┴────────┴─────────┴──────────┴────────┘││
│ │                                                 ││
│ │ [Export CSV] [Collapse]                         ││
│ └─────────────────────────────────────────────────┘│
│                                                     │
│ ┌─────────────────────────────────────────────────┐│
│ │ [▶] Mainstream Cluster                          ││ Collapsed
│ │ 2,800 units | 18 stores | 35% of total         ││
│ │ [Click to expand]                               ││
│ └─────────────────────────────────────────────────┘│
│                                                     │
│ ┌─────────────────────────────────────────────────┐│
│ │ [▶] Value_Conscious Cluster                     ││ Collapsed
│ │ 2,400 units | 12 stores | 25% of total         ││
│ │ [Click to expand]                               ││
│ └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

**Behavior:**
- Vertically stacked (not side-by-side)
- Multiple can be expanded simultaneously
- Expanded card pushes others down

---

### Section 4: Weekly Performance Chart

```
┌─────────────────────────────────────────────────────┐
│ Weekly Performance: Forecast vs Actual              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Chart (Recharts ComposedChart):                    │
│ ┌─────────────────────────────────────────────┐   │
│ │  800│   ─── Forecast (blue line)           │   │ Line: stroke-[#5E6AD2]
│ │  700│  ╱ ╲╱╲                                │   │ Bars: fill-[#00D084]
│ │  600│ ╱      ╲                              │   │
│ │  400│║ ║ ║ ║  ╲  Actual (green bars)       │   │
│ │     │1 2 3 4 5 6 7 8 9 10 11 12            │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ Week-by-Week Table (click row to expand):          │
│ ┌──────┬─────────┬────────┬──────────┬────────┐  │
│ │ Week │Forecast │ Actual │ Variance │ Status │  │
│ ├──────┼─────────┼────────┼──────────┼────────┤  │
│ │  1   │  650    │  640   │  -2%     │  🟢    │  │ hover:bg-[#1F1F1F]
│ │  2   │  720    │  735   │  +2%     │  🟢    │  │
│ │▼ 3   │  680    │  730   │  +7%     │  🟢    │  │ Expanded
│ ├──────┴─────────┴────────┴──────────┴────────┤  │
│ │ 📊 Week 3 Store-Level Breakdown:             │  │
│ │ ┌──────┬─────────┬────────┬──────────┐      │  │
│ │ │Store │Forecast │ Actual │ Variance │      │  │
│ │ ├──────┼─────────┼────────┼──────────┤      │  │
│ │ │ S01  │   12    │   15   │  +25% 🔴 │      │  │ text-[#F97066]
│ │ │ S02  │   11    │   11   │   0%  🟢 │      │  │ text-[#00D084]
│ │ │ ...  │   ...   │  ...   │   ...    │      │  │
│ │ └──────┴─────────┴────────┴──────────┘      │  │
│ │ [Collapse]                                    │  │
│ └───────────────────────────────────────────────┘  │
│ │  4   │  620    │   -    │    -     │  ⏳    │  │ Future week
│ │ ...  │  ...    │  ...   │  ...     │  ...   │  │
│ └──────┴─────────┴────────┴──────────┴────────┘  │
└─────────────────────────────────────────────────────┘
```

**Interactions:**
- Hover chart → Tooltip appears + highlights table row
- Click table row → Expands inline with store breakdown
- Variance >20% → Red background on that week's bar

---

### Section 5: Replenishment Queue

```
┌─────────────────────────────────────────────────────┐
│ [▼] Week 3 Replenishment Queue (12 stores)         │ Always expanded
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌──────┬────────┬──────────┬─────────┬─────────┐  │
│ │Store │Current │Forecast  │Replenish│   DC    │  │
│ │  ID  │Invent. │Next Week │ Needed  │Available│  │
│ ├──────┼────────┼──────────┼─────────┼─────────┤  │
│ │ S01  │   6    │   10     │   4     │   ✓     │  │
│ │ S02  │   8    │   9      │   1     │   ✓     │  │
│ │ S15  │   2    │   12     │  10     │   ⚠️ 5  │  │ Warning: insufficient
│ │ ...  │  ...   │   ...    │   ...   │   ...   │  │
│ └──────┴────────┴──────────┴─────────┴─────────┘  │
│                                                     │
│ DC Inventory Status: 4,200 units available         │
│                                                     │
│ [Approve Replenishments] [Export Shipment List]    │
│                                                     │
│ After approval:                                     │
│ │ S01  │   6    │   10     │   4     │ ✓ Shipped││ text-[#00D084]
└─────────────────────────────────────────────────────┘
```

---

### Section 6: Markdown Decision

```
Before Week 6:
┌─────────────────────────────────────────────────────┐
│ 📅 Markdown Checkpoint - Week 6 (in 3 weeks)       │ text-[#9CA3AF]
├─────────────────────────────────────────────────────┤
│ Countdown: 3 weeks until checkpoint                │
│ Target Sell-Through: 60% by Week 6                 │
└─────────────────────────────────────────────────────┘

At Week 6:
┌─────────────────────────────────────────────────────┐
│ ⚠️ Week 6 Markdown Checkpoint - Action Required    │ bg-[#F97066]/10
├─────────────────────────────────────────────────────┤
│ Sell-Through: 55% (Target: 60%) | Gap: 5pp         │
│                                                     │
│ Markdown Recommendation:                           │
│ Formula: Gap × Elasticity = 0.05 × 2.0 = 10%      │ font-mono
│ Application: Uniform across all stores             │
│                                                     │
│ Elasticity: [●─────] 2.0 ← Real-time preview       │ Shadcn Slider
│ (Move to 2.5 → Preview: 12.5% markdown)           │
│                                                     │
│ [Apply Markdown & Re-forecast]                     │ Button destructive
└─────────────────────────────────────────────────────┘

After applied:
┌─────────────────────────────────────────────────────┐
│ ✓ 10% Markdown Applied (Week 6)                    │ text-[#00D084]
├─────────────────────────────────────────────────────┤
│ Historical Record:                                  │
│ Applied: Week 6 | Depth: 10% | Elasticity: 2.0    │
│ Expected Lift: +18% | Re-forecast: Completed ✓    │
└─────────────────────────────────────────────────────┘
```

---

### Section 7: Performance Metrics

```
┌─────────────────────────────────────────────────────┐
│ Season Performance Metrics                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│ │ Forecast    │ │  Business   │ │   System    │  │ Grid 3 cols
│ │ Accuracy    │ │   Impact    │ │ Performance │  │
│ │             │ │             │ │             │  │
│ │ MAPE: 12%   │ │Stockouts: 3 │ │Runtime: 58s │  │ font-mono
│ │ Target:<20%✓│ │Overstock:   │ │Target:<60s✓ │  │ text-white
│ │             │ │  1,800 units│ │             │  │
│ │ Bias: +2%   │ │Markdown:    │ │Approval:    │  │
│ │ Target:±5%✓ │ │  $24K costs │ │  85% Accept │  │
│ │             │ │             │ │             │  │
│ │ Re-forecast │ │Inventory    │ │Uptime: 99%+ │  │
│ │ Trigger:92%✓│ │Turnover:+8% │ │             │  │
│ └─────────────┘ └─────────────┘ └─────────────┘  │
│                                                     │
│ [View Detailed Report →] [Export Metrics CSV]      │
│ (Navigates to /reports/spring-2025)               │
└─────────────────────────────────────────────────────┘
```

---

### Modal: Manufacturing Approval

```
┌─────────────────────────────────────────────────┐
│ Manufacturing Order Approval Required       [X] │ Dialog
├─────────────────────────────────────────────────┤
│                                                 │
│ Forecast Summary:                               │
│ • Total Season Forecast: 8,000 units           │ font-mono
│ • Prophet Forecast: 8,200 units                │
│ • ARIMA Forecast: 7,800 units                  │
│ • Ensemble Method: Average                     │
│                                                 │
│ Manufacturing Calculation:                      │
│ • Base Demand: 8,000 units                     │
│ • Safety Stock: 20% (1,600 units)              │
│ • Manufacturing Order: 9,600 units             │ text-2xl
│                                                 │
│ Adjust Parameters:                             │
│ Safety Stock %: [●─────] 20%                   │ Slider 10-30%
│ (Move to 22% → New order: 9,760 units)        │ Real-time update
│                                                 │
│ [Modify] [Accept]                               │
│ (Modify → Agent recalculates → Modal updates)  │
└─────────────────────────────────────────────────┘
```

---

## 6. Component Library

### Shadcn/ui Components Used

| Component | Usage | Props/Variants |
|-----------|-------|----------------|
| `<Card>` | Agent cards, cluster cards, metric cards | `className="bg-[#1A1A1A] border-[#2A2A2A]"` |
| `<Button>` | Primary actions, secondary actions | `variant="default"` (primary), `"outline"` (secondary), `"ghost"` |
| `<Badge>` | Status indicators, variance badges | `variant="default"`, `"outline"`, `"destructive"` |
| `<Alert>` | Variance alerts, warnings | `variant="default"` (🟢), `"warning"` (🟡), `"destructive"` (🔴) |
| `<Dialog>` | Manufacturing approval modal | `className="max-w-2xl"` |
| `<Table>` | Store allocations, weekly data | TanStack Table integration |
| `<Accordion>` | Cluster cards | `type="multiple"` (allows multiple expanded) |
| `<Collapsible>` | Forecast summary | `defaultOpen={true}` |
| `<Slider>` | Safety stock, elasticity | `min`, `max`, `step`, real-time `onValueChange` |
| `<Progress>` | Agent progress bars | `value={80}` |
| `<ScrollArea>` | Agent log messages | `maxHeight="200px"` |
| `<Toast>` | Success/error notifications | `variant="default"`, `"destructive"` |

### Additional Libraries

- **TanStack Table v8:** Complex tables with sorting, filtering, row expansion
- **Recharts:** Charts (ComposedChart with Line + Bar)
- **Lucide Icons:** `CheckCircle2`, `AlertCircle`, `Clock`, `AlertTriangle`, `ArrowUpDown`, `ExternalLink`, `Download`, `ChevronDown`

### Custom Components Needed

```typescript
// components/agent-status-card.tsx
<AgentStatusCard
  agentName="Demand Agent"
  agentColor="#5B8DEF" // Blue for Demand
  status="running" | "completed" | "idle"
  lastRun={{ week: 3, result: "8,000 units" }}
  nextRun={{ week: 4, action: "Check variance" }}
  progress={{ percent: 80, currentStep: "Running ARIMA..." }}
  logs={[
    { status: "completed", text: "Prophet: 8,200 units", duration: "15s" },
    { status: "running", text: "ARIMA: Running...", duration: "10s" }
  ]}
/>

// components/cluster-card.tsx
<ClusterCard
  clusterId="fashion_forward"
  clusterName="Fashion Forward"
  allocation={{ units: 3840, stores: 20, percentage: 0.40 }}
  characteristics={{
    avgIncome: 95000,
    avgSize: 18000,
    locationTier: "A",
    fashionTier: "Premium",
    avgWeeklySales: 285
  }}
  stores={[...]} // Store allocation data
  onExport={() => exportClusterCSV("fashion_forward")}
/>

// components/weekly-performance-chart.tsx
<WeeklyPerformanceChart
  weeks={12}
  forecastData={[650, 720, 680, ...]}
  actualData={[640, 735, 730, null, ...]} // null for future weeks
  onWeekHover={(week) => highlightTableRow(week)}
  varianceThreshold={0.20}
/>

// components/expandable-weekly-table.tsx
<ExpandableWeeklyTable
  weeks={[...]}
  onRowClick={(week) => expandStoreBreakdown(week)}
  expandedContent={(week) => <StoreBreakdownTable week={week} />}
/>

// components/metric-card.tsx
<MetricCard
  title="Forecast Accuracy"
  metrics={[
    { label: "MAPE", value: "12%", target: "<20%", status: "success" },
    { label: "Bias", value: "+2%", target: "±5%", status: "success" },
  ]}
/>
```

---

## 7. Design System (Linear Dark Theme)

### Color Palette

**Base Colors:**
```css
--background: #0D0D0D;       /* Near black page background */
--surface: #1A1A1A;          /* Dark gray cards */
--border: #2A2A2A;           /* Subtle borders */
--hover: #1F1F1F;            /* Hover states */
--text-primary: #FFFFFF;     /* White text */
--text-secondary: #9CA3AF;   /* Light gray */
--text-muted: #6B7280;       /* Muted gray */
```

**Accent Colors:**
```css
--primary: #5E6AD2;          /* Linear purple-blue (buttons, links) */
--success: #00D084;          /* Green (🟢 variance <10%) */
--warning: #F5A623;          /* Amber (🟡 variance 10-20%) */
--error: #F97066;            /* Soft red (🔴 variance >20%) */
--info: #5B8DEF;             /* Soft blue */
```

**Agent Colors:**
```css
--agent-demand: #5B8DEF;     /* Soft blue */
--agent-inventory: #00D084;  /* Green */
--agent-pricing: #F59E0B;    /* Amber */
```

**Chart Colors:**
```css
--chart-forecast: #5E6AD2;   /* Purple-blue line */
--chart-actual: #00D084;     /* Green bars (on track) */
--chart-variance: #F97066;   /* Red bars (high variance) */
```

### Typography

**Font Stack:**
```css
font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
font-mono: "SF Mono", "Monaco", "Cascadia Code", "Roboto Mono", monospace;
```

**Type Scale:**
```css
/* Headings */
.text-h1 { font-size: 24px; font-weight: 600; color: #FFFFFF; }
.text-h2 { font-size: 18px; font-weight: 500; color: #FFFFFF; }
.text-h3 { font-size: 16px; font-weight: 500; color: #FFFFFF; }

/* Body */
.text-body { font-size: 14px; font-weight: 400; color: #9CA3AF; }
.text-small { font-size: 12px; font-weight: 400; color: #6B7280; }

/* Data (numbers, monospace) */
.text-data { font-family: var(--font-mono); font-size: 14px; color: #FFFFFF; }
```

### Spacing & Layout

**Container:**
```css
.container {
  max-width: 1280px;
  padding: 32px;
  margin: 0 auto;
}
```

**Sections:**
```css
.section-gap { gap: 24px; } /* Between sections */
.card-padding { padding: 16px; } /* Within cards */
```

**Grid:**
```css
.grid-3-cols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
```

### Component Styles

**Cards:**
```css
.card {
  background: #1A1A1A;
  border: 1px solid #2A2A2A;
  border-radius: 8px;
  padding: 16px;
  box-shadow: none; /* Flat design, no shadows */
}
.card:hover {
  border-color: #3A3A3A;
}
```

**Buttons:**
```css
/* Primary */
.btn-primary {
  background: #5E6AD2;
  color: #FFFFFF;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
}
.btn-primary:hover {
  background: #4E5AC2;
}

/* Secondary */
.btn-secondary {
  background: #2A2A2A;
  color: #FFFFFF;
  border: 1px solid #3A3A3A;
  border-radius: 6px;
  padding: 8px 16px;
}
.btn-secondary:hover {
  background: #3A3A3A;
}

/* Ghost */
.btn-ghost {
  background: transparent;
  color: #9CA3AF;
  border: none;
}
.btn-ghost:hover {
  background: #2A2A2A;
  color: #FFFFFF;
}
```

**Tables:**
```css
.table {
  width: 100%;
  background: transparent;
}
.table-header {
  font-size: 12px;
  text-transform: uppercase;
  color: #6B7280;
  font-weight: 500;
}
.table-row {
  border-bottom: 1px solid #2A2A2A;
  transition: background 0.2s;
}
.table-row:hover {
  background: #1F1F1F;
}
.table-cell {
  font-size: 14px;
  color: #FFFFFF;
  padding: 12px 8px;
}
.table-cell-mono {
  font-family: var(--font-mono);
}
```

**Badges (Variance):**
```css
/* Success 🟢 */
.badge-success {
  background: rgba(0, 208, 132, 0.1);
  color: #00D084;
  border: 1px solid rgba(0, 208, 132, 0.2);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
}

/* Warning 🟡 */
.badge-warning {
  background: rgba(245, 166, 35, 0.1);
  color: #F5A623;
  border: 1px solid rgba(245, 166, 35, 0.2);
}

/* Error 🔴 */
.badge-error {
  background: rgba(249, 112, 102, 0.1);
  color: #F97066;
  border: 1px solid rgba(249, 112, 102, 0.2);
}
```

### Tailwind Config

```typescript
// tailwind.config.ts
export default {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0D0D0D",
        foreground: "#FFFFFF",
        card: {
          DEFAULT: "#1A1A1A",
          foreground: "#FFFFFF",
        },
        border: "#2A2A2A",
        hover: "#1F1F1F",
        primary: {
          DEFAULT: "#5E6AD2",
          foreground: "#FFFFFF",
        },
        success: "#00D084",
        warning: "#F5A623",
        error: "#F97066",
        muted: {
          DEFAULT: "#1F1F1F",
          foreground: "#9CA3AF",
        },
        "text-muted": "#6B7280",
        "agent-demand": "#5B8DEF",
        "agent-inventory": "#00D084",
        "agent-pricing": "#F59E0B",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["SF Mono", "Monaco", "Cascadia Code", "monospace"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## 8. Accessibility

### WCAG 2.1 Level AA Compliance

**Color Contrast:**
- White text on #0D0D0D background: 21:1 ratio ✓
- Gray text (#9CA3AF) on #0D0D0D: 8.3:1 ratio ✓
- All buttons meet minimum 4.5:1 contrast

**Keyboard Navigation:**
- All interactive elements focusable (Tab order)
- Focus visible: `focus:ring-2 focus:ring-[#5E6AD2]`
- Escape closes modals
- Arrow keys navigate tables

**Screen Reader Support:**
- Semantic HTML (`<header>`, `<main>`, `<section>`)
- ARIA labels for icon-only buttons
- `aria-live="polite"` for agent status updates
- Table headers properly associated with cells

**Focus Management:**
- Modal open → Focus trapped inside modal
- Modal close → Focus returns to trigger button
- Auto-scroll to top → Focus moves to agent card

---

## 9. Responsiveness

### Desktop-First Approach

**Primary Target:** Desktop/Laptop (1280px - 1920px)

**Breakpoints:**
- Desktop: 1280px+ (primary)
- Tablet: 768px - 1279px (limited support)
- Mobile: < 768px (monitoring only, no complex interactions)

### Responsive Behavior

**1280px+ (Desktop):**
- All sections visible, full functionality
- 3-column metric grid
- Side-by-side agent cards (3 columns)

**768px - 1279px (Tablet):**
- Stack sections vertically
- 2-column metric grid
- Agent cards stack 2+1
- Tables horizontal scroll if needed

**< 768px (Mobile):**
- **Limited Support:** Display message: "For full functionality, please use desktop browser."
- Show only: Current phase, latest variance alert, key metrics
- No CSV upload, no agent runs, no approvals (desktop required)

### Responsive Utilities

```css
/* Desktop only */
@media (max-width: 767px) {
  .desktop-only { display: none; }
}

/* Mobile message */
@media (max-width: 767px) {
  .mobile-warning {
    display: block;
    background: #F97066;
    color: #FFFFFF;
    padding: 16px;
    text-align: center;
  }
}
```

---

## 10. Animation & Micro-interactions

### Agent Card Expansion

```css
/* Smooth height transition */
.agent-card {
  transition: height 0.3s ease-in-out;
}

/* Progress bar fill animation */
.progress-bar {
  transition: width 0.5s ease-out;
}
```

### WebSocket Message Appearance

```css
/* Fade in + slide down for each new log line */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.agent-log-line {
  animation: slideDown 0.3s ease-out;
}
```

### Table Row Hover

```css
.table-row {
  transition: background 0.2s ease;
}
.table-row:hover {
  background: #1F1F1F;
}
```

### Button Hover

```css
.btn {
  transition: all 0.2s ease;
}
.btn:hover {
  transform: translateY(-1px);
}
.btn:active {
  transform: translateY(0);
}
```

### Loading Overlay

```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.loading-overlay {
  animation: fadeIn 0.2s ease-in;
  background: rgba(13, 13, 13, 0.8);
  backdrop-filter: blur(4px);
}
```

### Auto-Scroll Behavior

```typescript
// Smooth scroll to top when re-forecast triggers
window.scrollTo({
  top: 0,
  behavior: 'smooth'
});
```

---

## 11. Performance Considerations

### Target Metrics

- **Time to Interactive:** <3 seconds
- **First Contentful Paint:** <1.5 seconds
- **Agent Workflow Runtime:** <60 seconds (backend)
- **WebSocket Message Latency:** <100ms
- **Chart Render Time:** <500ms

### Optimization Strategies

**Code Splitting:**
```typescript
// Lazy load report page
const ReportPage = lazy(() => import('./pages/ReportPage'));
```

**Memoization:**
```typescript
// Prevent unnecessary re-renders
const AgentCard = memo(({ agentName, status, logs }) => {
  // Component implementation
});

// Memoize expensive calculations
const clusterDistribution = useMemo(() => {
  return calculateClusterAllocation(forecast, stores);
}, [forecast, stores]);
```

**Virtualization:**
```typescript
// Use react-window for large tables (>100 rows)
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={400}
  itemCount={storeAllocations.length}
  itemSize={48}
>
  {StoreRow}
</FixedSizeList>
```

**WebSocket Connection Management:**
```typescript
// Single WebSocket connection, reuse across components
const { lastMessage, sendMessage } = useWebSocket('ws://localhost:8000/ws/agents', {
  shouldReconnect: () => true,
  reconnectInterval: 3000,
  reconnectAttempts: 10,
});
```

**Chart Performance:**
```typescript
// Debounce chart updates
const debouncedChartData = useMemo(() =>
  debounce(updateChartData, 100),
  []
);
```

---

## 12. Data Generation Requirements

### CSV Structure for Mock Data

**File 1: Historical Sales CSV**

**Filename:** `historical_sales_2022_2024.csv`

**Columns:** `date, category, store_id, quantity_sold, revenue`

**Requirements:**
- **Date range:** 2022-01-01 to 2024-12-31 (3 years)
- **Categories:** Women's Dresses, Men's Shirts, Accessories (user selects one)
- **Store IDs:** S01 to S50
- **Frequency:** Daily records
- **Total rows:** ~54,750 rows (50 stores × 365 days × 3 years)

**Example rows:**
```csv
date,category,store_id,quantity_sold,revenue
2022-01-01,Women's Dresses,S01,15,450.00
2022-01-01,Women's Dresses,S02,12,360.00
2022-01-01,Men's Shirts,S01,8,240.00
2022-01-02,Women's Dresses,S01,18,540.00
...
```

**Data Characteristics:**
- Seasonality: Higher sales Spring/Summer for dresses
- Variance: 10-30% week-to-week fluctuation
- Store patterns: S01-S20 (high sales), S21-S38 (medium), S39-S50 (low)

---

**File 2: Store Attributes CSV**

**Filename:** `store_attributes.csv`

**Columns:** `store_id, store_name, store_size_sqft, location_tier, median_income, store_format, region, avg_weekly_sales_12mo, fashion_tier`

**Requirements:**
- **50 stores** (S01 to S50)
- **7 features** for K-means clustering

**Example rows:**
```csv
store_id,store_name,store_size_sqft,location_tier,median_income,store_format,region,avg_weekly_sales_12mo,fashion_tier
S01,Downtown NYC,20000,A,95000,MALL,NORTHEAST,285,PREMIUM
S02,LA Mall,18000,A,88000,MALL,WEST,260,PREMIUM
S03,Chicago Suburb,15000,B,65000,SHOPPING_CENTER,MIDWEST,180,MAINSTREAM
S25,Rural Ohio,10000,C,45000,OUTLET,MIDWEST,95,VALUE
...
```

**Cluster Distribution (Expected after K-means):**
- **Fashion_Forward:** S01-S20 (20 stores, high income/size/sales)
- **Mainstream:** S21-S38 (18 stores, medium)
- **Value_Conscious:** S39-S50 (12 stores, low)

---

### Test Scenarios Data

**Scenario 1: Normal Season (Low Variance)**
- Actual sales: 95-105% of forecast weekly
- No re-forecast triggers
- Week 6 sell-through: 62% (above 60% target → no markdown)

**Scenario 2: High Demand (Re-forecast Triggered)**
- Actual sales Week 1: 850 units (forecast: 650) → 31% variance
- Triggers re-forecast
- Updated forecast: 10,500 units (from 8,000)

**Scenario 3: Low Demand (Markdown Applied)**
- Actual sales: 85-90% of forecast
- Week 6 sell-through: 52% (below 60% target)
- Gap: 8% → Markdown: 16% (rounded to 15%)

---

## 13. Next Steps & Handoff

### For Frontend Developer

**Setup:**
1. Initialize React + TypeScript + Vite project
2. Install dependencies:
   ```bash
   npm install @tanstack/react-table @tanstack/react-query
   npm install recharts lucide-react
   npm install react-hook-form zod
   ```
3. Install Shadcn/ui components:
   ```bash
   npx shadcn-ui@latest init
   npx shadcn-ui@latest add card button badge alert dialog table accordion collapsible slider progress scroll-area toast
   ```
4. Configure Tailwind with Linear Dark Theme colors (see Section 7)

**Implementation Order:**
1. **Week 1:** Section 1 (Header + Agent cards with WebSocket stub)
2. **Week 2:** Section 2-3 (Forecast summary + Cluster cards)
3. **Week 3:** Section 4 (Weekly chart + expandable table)
4. **Week 4:** Section 5-6 (Replenishment + Markdown)
5. **Week 5:** Section 7 + Report page
6. **Week 6:** WebSocket integration, error handling, polish

**Key Files to Reference:**
- This spec (all sections)
- Technical Architecture v3.2 (backend API contracts)
- Operational Workflow v3.2 (agent behavior)

---

### For Backend Developer

**WebSocket Requirements:**
- Endpoint: `ws://localhost:8000/ws/agents`
- Message format (line-by-line updates):
  ```json
  {
    "agent": "demand",
    "status": "running" | "completed" | "error",
    "progress": 80,
    "step": "Running ARIMA model...",
    "duration": "10s",
    "result": "7,800 units" // if completed
  }
  ```
- Send messages sequentially (not batched)
- Client expects ~10-15 messages per 60-second workflow

**API Endpoints Needed:**
- `POST /api/forecast/run` (trigger agents)
- `GET /api/forecast/{forecast_id}` (get results)
- `POST /api/replenishment/approve` (approve weekly shipments)
- `POST /api/markdown/apply` (apply markdown + re-forecast)
- `GET /api/reports/{season_id}` (performance report data)

---

### For UX Designer

**Design Deliverables Needed:**
1. High-fidelity mockups of all 7 sections (Figma/Sketch)
2. Agent card states: idle, running, completed, error
3. Modal designs: manufacturing approval, parameter editing
4. Loading overlay design
5. Toast notification designs
6. Report page layout

**Design Tool:** Figma recommended
**Handoff:** Export to Figma Dev Mode for developers

---

### For Data Generator

**Task:** Create mock CSVs matching Section 12 specifications

**Deliverables:**
1. `historical_sales_2022_2024.csv` (~54,750 rows)
2. `store_attributes.csv` (50 rows)
3. Ensure data supports 3 test scenarios (normal, high demand, low demand)

**Tools:** Python script, Faker library, or manual spreadsheet

---

## Document Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-13 | Initial specification (Linear Dark Theme) | Sally (UX Expert) |

---

**Status:** ✅ Complete - Ready for Implementation

**Questions?** Contact the UX team or refer to Technical Architecture v3.2 for backend integration details.
