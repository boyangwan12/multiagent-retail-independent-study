# PHASE4.5-002: Weekly Actuals Upload

**Story ID:** PHASE4.5-002
**Story Name:** Weekly Actuals Upload (PRD Story 3.1)
**Phase:** Phase 4.5 - Data Upload Infrastructure
**Dependencies:** PHASE4.5-001 complete
**Estimated Effort:** 4-6 hours
**Assigned To:** Developer (Full-Stack)
**Status:** Not Started

**Planning References:**
- PRD v3.3: Story 3.1 (Upload Weekly Actuals)
- Technical Architecture v3.3: Section 4.8 (Variance Monitoring & Re-forecasting)
- Frontend Spec v3.3: Section 4 (Weekly Performance Chart)

---

## User Story

**As a** retail planner monitoring the active season,
**I want** to upload weekly actual sales data every Monday,
**So that** the system can calculate variance and trigger re-forecast if demand exceeds 20% threshold.

---

## Context & Background

### What This Story Covers

This story implements **in-season monitoring** via weekly actuals upload:

**Purpose:** Monitor forecast accuracy week-by-week during the active season

**User Flow:**
1. Season starts (Week 1)
2. After Week 1 ends (Sunday), dashboard shows: "⏳ Week 1 actuals pending upload"
3. Monday morning: User clicks "Upload Week 1 Actuals"
4. User uploads `week_1_actuals.csv` (~350 rows, 50 stores × 7 days)
5. System validates date range matches Week 1
6. System aggregates daily sales to weekly totals
7. System calculates variance (forecast vs actual)
8. System updates chart with actual bars (green/amber/red)
9. If variance >20%, system triggers re-forecast (logs warning for Phase 5)

**Key Metrics:**
- Variance 0-10%: 🟢 Green bar, "Tracking well"
- Variance 10-20%: 🟡 Amber bar, "Elevated variance"
- Variance >20%: 🔴 Red bar, "High variance - Re-forecast triggered"

---

## Architecture

### Backend Endpoint

**POST /api/data/upload/weekly-actuals**

**Request:**
```http
POST /api/data/upload/weekly-actuals
Content-Type: multipart/form-data

Body:
  workflow_id: wf_abc123 (form field)
  week_number: 3 (form field)
  file: week_3_actuals.csv (File)
```

**Expected CSV Format:**
```csv
date,store_id,quantity_sold
2025-03-08,S001,18
2025-03-09,S001,22
2025-03-10,S001,25
...
2025-03-14,S050,19
```

**Response (Success - 200 OK):**
```json
{
  "status": "success",
  "workflow_id": "wf_abc123",
  "week_number": 3,
  "week_date_range": {
    "start": "2025-03-08",
    "end": "2025-03-14"
  },
  "actuals_summary": {
    "total_units_sold": 3250,
    "stores_reported": 50,
    "daily_rows_inserted": 350
  },
  "variance_analysis": {
    "forecast_units": 3000,
    "actual_units": 3250,
    "variance_pct": 0.083,
    "variance_status": "NORMAL",
    "variance_color": "green"
  },
  "reforecast_triggered": false,
  "uploaded_at": "2025-03-15T09:00:00Z"
}
```

**Response (High Variance - Re-forecast Triggered):**
```json
{
  "status": "success",
  "workflow_id": "wf_abc123",
  "week_number": 5,
  "actuals_summary": {
    "total_units_sold": 4200,
    "stores_reported": 50
  },
  "variance_analysis": {
    "forecast_units": 3000,
    "actual_units": 4200,
    "variance_pct": 0.40,
    "variance_status": "HIGH",
    "variance_color": "red"
  },
  "reforecast_triggered": true,
  "reforecast_workflow_id": "wf_reforecast_xyz",
  "message": "Variance exceeds 20% threshold. Re-forecast initiated for weeks 6-12.",
  "uploaded_at": "2025-04-05T09:00:00Z"
}
```

---

### Database Schema

**Table: weekly_actuals**

```sql
CREATE TABLE weekly_actuals (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL,
    week_number INTEGER NOT NULL,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    actual_units_sold INTEGER NOT NULL,
    forecast_units_sold INTEGER,
    variance_pct FLOAT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (workflow_id, week_number, store_id),
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE INDEX idx_weekly_actuals_workflow ON weekly_actuals(workflow_id, week_number);
CREATE INDEX idx_weekly_actuals_store ON weekly_actuals(store_id);
```

---

### Data Flow

```
User uploads week_3_actuals.csv
    ↓
Backend validates:
  - Date range matches Week 3 (2025-03-08 to 2025-03-14)
  - 7 days of data (Mon-Sun)
  - All 50 stores present
  - No missing dates per store
    ↓
Backend aggregates:
  - Sum quantity_sold per store (7 days → 1 weekly total)
    ↓
Backend fetches forecast for Week 3:
  - Query forecasts table for workflow_id, week_number=3
    ↓
Backend calculates variance:
  - variance_pct = (actual - forecast) / forecast
  - variance_status = "NORMAL" | "ELEVATED" | "HIGH"
  - variance_color = "green" | "amber" | "red"
    ↓
Backend inserts weekly_actuals row (1 per store)
    ↓
IF variance_pct > 0.20:
  - Log warning: "High variance detected - re-forecast required"
  - Create reforecast workflow (Phase 5 implementation)
    ↓
Backend returns variance_analysis to frontend
    ↓
Frontend updates chart:
  - Add actual bar for Week 3 (colored by variance_status)
  - Update alert banner
  - Show re-forecast notification if triggered
```

---

## Frontend UI Design

### Location: Section 4 (Weekly Performance Chart)

**Before Upload:**
```
┌──────────────────────────────────────────────────────────┐
│  Section 4: Weekly Performance Chart                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ⏳ Week 3 actuals pending upload                        │
│  [Upload Week 3 Actuals]                                 │
│                                                          │
│  Chart:                                                   │
│    Week 1: Forecast (blue line) + Actual (green bar)    │
│    Week 2: Forecast (blue line) + Actual (green bar)    │
│    Week 3: Forecast (blue line) only                     │
│    Week 4-12: Forecast (blue line) only                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Upload Modal:**
```
┌──────────────────────────────────────────────────────────┐
│  Upload Week 3 Actuals                            [X]    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Week: 3                                                 │
│  Date Range: March 8, 2025 - March 14, 2025             │
│                                                          │
│  Expected Format:                                        │
│  ┌────────────────────────────────────────────┐         │
│  │ date,store_id,quantity_sold                │         │
│  │ 2025-03-08,S001,18                         │         │
│  │ 2025-03-09,S001,22                         │         │
│  │ ...                                         │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  Expected Rows: ~350 (50 stores × 7 days)               │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │                                          │           │
│  │  📂 Drag & Drop CSV File                 │           │
│  │     or                                   │           │
│  │  [Browse Files]                          │           │
│  │                                          │           │
│  └──────────────────────────────────────────┘           │
│                                                          │
│  [Cancel]              [Upload & Calculate Variance]    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**After Upload (Normal Variance):**
```
┌──────────────────────────────────────────────────────────┐
│  Section 4: Weekly Performance Chart                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ✅ Week 3 actuals uploaded: 3,250 units                 │
│  🟢 Variance: 8% - Tracking well                         │
│                                                          │
│  Chart:                                                   │
│    Week 1: Forecast + Actual (green bar)                │
│    Week 2: Forecast + Actual (green bar)                │
│    Week 3: Forecast + Actual (green bar) ← NEW          │
│    Week 4-12: Forecast only                              │
│                                                          │
│  [Upload Week 4 Actuals]                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**After Upload (High Variance - Re-forecast Triggered):**
```
┌──────────────────────────────────────────────────────────┐
│  Section 4: Weekly Performance Chart                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ⚠️ HIGH VARIANCE DETECTED - RE-FORECAST TRIGGERED       │
│  ┌────────────────────────────────────────────────┐     │
│  │ 🔴 Week 5 Variance: 40%                        │     │
│  │                                                 │     │
│  │ Actual: 4,200 units                            │     │
│  │ Forecast: 3,000 units                          │     │
│  │ Difference: +1,200 units (+40%)                │     │
│  │                                                 │     │
│  │ System is re-forecasting weeks 6-12 based on   │     │
│  │ updated demand patterns...                      │     │
│  │                                                 │     │
│  │ Re-forecast workflow: wf_reforecast_xyz        │     │
│  │ [View Re-forecast Progress →]                  │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  Chart:                                                   │
│    Week 1-4: Forecast + Actual (green bars)             │
│    Week 5: Forecast + Actual (red bar) ← HIGH VARIANCE  │
│    Week 6-12: Updated forecast (dashed blue line)       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

### Backend API

- [ ] **AC1:** POST /api/data/upload/weekly-actuals endpoint accepts CSV file
- [ ] **AC2:** Endpoint validates workflow_id exists
- [ ] **AC3:** Endpoint validates week_number (1-52)
- [ ] **AC4:** Endpoint validates date range matches week_number
- [ ] **AC5:** Endpoint validates 7 consecutive days of data
- [ ] **AC6:** Endpoint validates all 50 stores present
- [ ] **AC7:** Endpoint validates no missing dates per store
- [ ] **AC8:** Backend aggregates daily sales to weekly totals per store
- [ ] **AC9:** Backend fetches forecast from database for comparison
- [ ] **AC10:** Backend calculates variance percentage
- [ ] **AC11:** Backend inserts weekly_actuals rows (1 per store)
- [ ] **AC12:** Backend returns variance_analysis with status and color
- [ ] **AC13:** Backend logs warning if variance >20%
- [ ] **AC14:** Backend returns reforecast_triggered flag
- [ ] **AC15:** Duplicate upload for same week returns 400 error

### Frontend UI

- [ ] **AC16:** "Upload Week N Actuals" button appears in Section 4
- [ ] **AC17:** Button shows pending week number (e.g., "Upload Week 3 Actuals")
- [ ] **AC18:** Modal opens with week number and date range
- [ ] **AC19:** Modal shows expected CSV format example
- [ ] **AC20:** Drag-and-drop functionality works
- [ ] **AC21:** "Browse Files" button opens file picker
- [ ] **AC22:** "Upload & Calculate Variance" triggers upload
- [ ] **AC23:** Loading spinner displays during upload
- [ ] **AC24:** Success toast shows: "✓ Week 3 actuals uploaded. Variance: 8%"
- [ ] **AC25:** Chart updates with actual bar (colored by variance)
- [ ] **AC26:** Alert banner updates with variance status
- [ ] **AC27:** If variance >20%, re-forecast alert displays
- [ ] **AC28:** "Upload Week N+1 Actuals" button appears after successful upload

### Variance Calculation

- [ ] **AC29:** Variance 0-10%: Green bar, "🟢 Tracking well"
- [ ] **AC30:** Variance 10-20%: Amber bar, "🟡 Elevated variance 15%"
- [ ] **AC31:** Variance >20%: Red bar, "🔴 High variance 25% - Re-forecast triggered"
- [ ] **AC32:** Variance displayed as percentage (e.g., "8%", "+15%", "-12%")

### Error Handling

- [ ] **AC33:** Wrong date range: "❌ Date range mismatch. Expected 2025-03-08 to 2025-03-14"
- [ ] **AC34:** Missing stores: "❌ Missing data for stores: S15, S22, S38"
- [ ] **AC35:** Duplicate upload: "⚠️ Week 3 actuals already uploaded. Overwrite existing data?"
- [ ] **AC36:** Invalid date format: "❌ Invalid date format in row 12. Expected YYYY-MM-DD"

---

## Tasks

### Task 1: Create WeeklyActualsService (2 hours)

**File:** `backend/app/services/weekly_actuals_service.py`

**Key Methods:**
```python
class WeeklyActualsService:
    def upload_weekly_actuals(
        self,
        workflow_id: str,
        week_number: int,
        csv_file
    ) -> Dict:
        # 1. Validate workflow exists
        # 2. Validate CSV format and date range
        # 3. Aggregate daily sales to weekly totals
        # 4. Fetch forecast for comparison
        # 5. Calculate variance
        # 6. Insert weekly_actuals rows
        # 7. Check if reforecast needed (variance >20%)
        # 8. Return variance_analysis
        pass

    def calculate_variance(
        self,
        forecast_units: int,
        actual_units: int
    ) -> Dict:
        # Returns: variance_pct, variance_status, variance_color
        pass

    def check_reforecast_needed(
        self,
        variance_pct: float
    ) -> bool:
        # Returns: True if variance >20%
        pass
```

---

### Task 2: Create Backend API Endpoint (1.5 hours)

**File:** `backend/app/api/v1/endpoints/data_upload.py` (enhance)

**Add endpoint:**
```python
@router.post("/upload/weekly-actuals", status_code=status.HTTP_200_OK)
async def upload_weekly_actuals(
    workflow_id: str = Form(...),
    week_number: int = Form(...),
    file: UploadFile = File(...),
    service: WeeklyActualsService = Depends(get_weekly_actuals_service)
):
    # Validate and upload weekly actuals
    pass
```

---

### Task 3: Create Frontend Upload Modal (2-3 hours)

**File:** `frontend/src/components/WeeklyPerformanceChart/WeeklyActualsUploadModal.tsx`

**Component:**
```typescript
export function WeeklyActualsUploadModal({
  workflowId,
  weekNumber,
  weekDateRange,
  isOpen,
  onClose,
  onUploadSuccess
}: Props) {
  // Handle file upload
  // Show loading state
  // Display variance result
  // Show re-forecast alert if triggered
}
```

---

### Task 4: Integrate into WeeklyPerformanceChart (1 hour)

**File:** `frontend/src/components/WeeklyPerformanceChart/WeeklyPerformanceChart.tsx`

**Add:**
- "Upload Week N Actuals" button
- Modal trigger logic
- Chart update after upload
- Alert banner with variance status

---

## Definition of Done

- [ ] Backend endpoint created and tested
- [ ] WeeklyActualsService validates and inserts data
- [ ] Variance calculation works correctly
- [ ] Frontend modal opens with correct week info
- [ ] User can upload CSV via drag-and-drop or file picker
- [ ] Chart updates with colored actual bars
- [ ] Alert banner shows variance status
- [ ] Re-forecast alert displays if variance >20%
- [ ] Validation errors displayed clearly
- [ ] Accessibility requirements met
- [ ] Manual testing completed
- [ ] Code reviewed

---

## Related Stories

- **PRD Story 3.1:** Upload Weekly Actuals
- **PHASE4.5-001:** Historical Training Data Upload (prerequisite)
- **PHASE5-002:** Agent Handoff Framework (will use variance to trigger re-forecast)

---

**Status:** Not Started
**Branch:** `phase4.5-data-upload`
