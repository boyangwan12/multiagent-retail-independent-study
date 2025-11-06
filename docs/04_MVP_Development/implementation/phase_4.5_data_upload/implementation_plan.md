# PHASE 4.5 IMPLEMENTATION PLAN

**Phase:** 4.5 - Data Upload Infrastructure
**Status:** Planning Complete
**Estimated Effort:** 12-17 hours (1.5-2 days)
**Priority:** P0 (Blocker for Phase 5)

---

## Overview

### Purpose

Phase 4.5 implements the missing data upload workflows required by the PRD:
- **PRD Story 1.1:** Upload Historical Sales Data (2-3 years for model training)
- **PRD Story 1.2:** Upload Store Attributes (store characteristics)
- **PRD Story 3.1:** Upload Weekly Actuals (in-season monitoring & variance calculation)

### Why This Phase Exists

**Problem:** Phase 4 implemented agent supplementary uploads (PHASE4-007) but NOT historical training data uploads. Phase 5 Context Assembly requires historical data to exist in the database.

**Solution:** Create Phase 4.5 as a bridge phase to:
1. Complete PRD requirements (Stories 1.1, 1.2, 3.1)
2. Ensure database ready for Phase 5
3. Enable variance monitoring and re-forecast triggering
4. Clean separation of concerns (upload infrastructure ≠ orchestration)

### Key Decisions

| Decision | Chosen Approach | Rationale |
|----------|----------------|-----------|
| **Data Storage** | Database (SQLite) | Single source of truth, production-ready, consistent with seed_db.py |
| **Upload Strategy** | Batch insert (1000 rows) | Performance optimization for large CSV files |
| **Validation** | Pre-insert validation | Fail fast, detailed error messages |
| **Duplicate Handling** | UNIQUE constraints | Database-level protection, prevent data corruption |
| **Variance Calculation** | Server-side | Consistent logic, centralized business rules |
| **Re-forecast Trigger** | Log warning (Phase 5 implementation) | Placeholder for orchestrator integration |

---

## Stories & Dependencies

### Story Overview

```
PHASE4.5-003 (Database Schema)
    ↓
PHASE4.5-001 (Historical Data Upload)
    ↓
PHASE4.5-002 (Weekly Actuals Upload)
```

### Story Details

| Story ID | Story Name | Effort | Priority | Can Parallelize? |
|----------|------------|--------|----------|------------------|
| **PHASE4.5-003** | Database Schema & Migration | 2-3 hours | P0 | No (must run first) |
| **PHASE4.5-001** | Historical Training Data Upload | 6-8 hours | P0 | No (depends on 003) |
| **PHASE4.5-002** | Weekly Actuals Upload | 4-6 hours | P0 | No (depends on 001) |

**Total Effort:** 12-17 hours

### Implementation Sequence

**Day 1 (6-8 hours):**
1. **Morning:** PHASE4.5-003 (Database Schema) - 2-3 hours
2. **Afternoon:** PHASE4.5-001 (Historical Data Upload) - 4-5 hours

**Day 2 (6-9 hours):**
3. **Morning:** PHASE4.5-001 completion + testing - 2-3 hours
4. **Afternoon:** PHASE4.5-002 (Weekly Actuals Upload) - 4-6 hours

---

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Section 0: Parameter Extraction                       │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  [Upload Historical Data] button                 │  │ │
│  │  │  ├─ Upload Historical Sales CSV                  │  │ │
│  │  │  └─ Upload Store Attributes CSV                  │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                          │ │
│  │  Section 4: Weekly Performance Chart                    │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Chart: Forecast vs Actual (Week 1-12)           │  │ │
│  │  │  [Upload Week N Actuals] button                  │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST (multipart/form-data)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  POST /api/v1/data/upload/historical-sales            │ │
│  │  POST /api/v1/data/upload/store-attributes            │ │
│  │  POST /api/v1/data/upload/weekly-actuals              │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  DataUploadService                                     │ │
│  │  ├─ validate_csv_format()                             │ │
│  │  ├─ validate_date_range()                             │ │
│  │  ├─ batch_insert() (1000 rows at a time)              │ │
│  │  └─ detect_categories()                               │ │
│  │                                                          │ │
│  │  WeeklyActualsService                                  │ │
│  │  ├─ validate_week_range()                             │ │
│  │  ├─ aggregate_daily_to_weekly()                       │ │
│  │  ├─ calculate_variance()                              │ │
│  │  └─ check_reforecast_needed()                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SQLAlchemy ORM Models                                 │ │
│  │  ├─ HistoricalSales (existing)                        │ │
│  │  ├─ Store (existing)                                  │ │
│  │  ├─ Category (existing)                               │ │
│  │  ├─ Workflow (existing)                               │ │
│  │  └─ WeeklyActuals (NEW)                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  SQLite Database                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  historical_sales (existing)                           │ │
│  │  stores (existing)                                     │ │
│  │  categories (existing)                                 │ │
│  │  workflows (existing)                                  │ │
│  │  weekly_actuals (NEW)                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Backend Components

**New Files:**
```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   └── data_upload.py (NEW)
│   ├── services/
│   │   ├── data_upload_service.py (NEW)
│   │   └── weekly_actuals_service.py (NEW)
│   └── database/
│       └── models.py (MODIFIED - add WeeklyActuals)
└── scripts/
    └── migrate_phase_4_5.py (NEW)
```

**Modified Files:**
```
backend/app/database/models.py (add WeeklyActuals model, update Workflow relationship)
backend/app/api/v1/api.py (register data_upload router)
```

#### Frontend Components

**New Files:**
```
frontend/src/
├── components/
│   ├── HistoricalDataUpload/
│   │   ├── HistoricalDataUpload.tsx (NEW)
│   │   ├── HistoricalSalesUpload.tsx (NEW)
│   │   └── StoreAttributesUpload.tsx (NEW)
│   └── WeeklyPerformanceChart/
│       └── WeeklyActualsUploadModal.tsx (NEW)
└── services/
    └── data-upload-service.ts (NEW)
```

**Modified Files:**
```
frontend/src/components/ParameterExtraction.tsx (integrate HistoricalDataUpload)
frontend/src/components/WeeklyPerformanceChart/WeeklyPerformanceChart.tsx (add upload button)
frontend/src/config/api.ts (add data upload endpoints)
```

---

## Data Flow

### Historical Sales Upload Flow

```
User uploads historical_sales.csv (163,944 rows)
    ↓
Frontend: File validation
  - Check file size (<50MB)
  - Check file extension (.csv)
  - Parse first row (headers)
    ↓
Frontend: POST /api/v1/data/upload/historical-sales
  - multipart/form-data
  - file: historical_sales.csv
    ↓
Backend: DataUploadService.upload_historical_sales()
  ├─ Validate CSV headers
  │  Expected: week_start_date, store_id, quantity_sold
  ├─ Validate date format (YYYY-MM-DD)
  ├─ Validate store_id exists in stores table
  ├─ Detect category from filename or data
  ├─ Batch insert (1000 rows at a time)
  │  ├─ Generate sale_id (UUID)
  │  ├─ Create HistoricalSales objects
  │  └─ session.bulk_save_objects()
  └─ Return summary
       ↓
Backend Response:
{
  "status": "success",
  "rows_inserted": 163944,
  "categories_detected": ["womens_dresses"],
  "date_range": {"start": "2023-01-01", "end": "2025-12-31"},
  "stores_count": 50
}
    ↓
Frontend: Display success toast
  "✓ Historical sales uploaded: 163,944 rows (2023-01-01 to 2025-12-31)"
```

### Weekly Actuals Upload Flow

```
User uploads week_3_actuals.csv (350 rows)
    ↓
Frontend: POST /api/v1/data/upload/weekly-actuals
  - workflow_id: wf_abc123
  - week_number: 3
  - file: week_3_actuals.csv
    ↓
Backend: WeeklyActualsService.upload_weekly_actuals()
  ├─ Validate workflow_id exists
  ├─ Validate week_number (1-52)
  ├─ Validate CSV headers
  │  Expected: date, store_id, quantity_sold
  ├─ Validate date range matches Week 3
  │  (2025-03-08 to 2025-03-14)
  ├─ Validate 7 consecutive days
  ├─ Validate all 50 stores present
  ├─ Aggregate daily sales to weekly totals
  │  (350 rows → 50 weekly totals)
  ├─ Fetch forecast for Week 3
  │  Query forecasts table
  ├─ Calculate variance
  │  variance_pct = (actual - forecast) / forecast
  ├─ Determine variance status
  │  0-10%: GREEN (Tracking well)
  │  10-20%: AMBER (Elevated variance)
  │  >20%: RED (High variance)
  ├─ Insert weekly_actuals rows (1 per store)
  │  - workflow_id, week_number
  │  - actual_units_sold, forecast_units_sold
  │  - variance_pct
  └─ Check if reforecast needed
      IF variance_pct > 0.20:
        ├─ Log warning
        ├─ Create reforecast workflow (Phase 5)
        └─ Set reforecast_triggered = true
       ↓
Backend Response:
{
  "status": "success",
  "workflow_id": "wf_abc123",
  "week_number": 3,
  "actuals_summary": {
    "total_units_sold": 3250,
    "stores_reported": 50
  },
  "variance_analysis": {
    "forecast_units": 3000,
    "actual_units": 3250,
    "variance_pct": 0.083,
    "variance_status": "NORMAL",
    "variance_color": "green"
  },
  "reforecast_triggered": false
}
    ↓
Frontend: Update chart
  - Add green bar for Week 3 (actual)
  - Update alert banner: "🟢 Week 3 variance: 8% - Tracking well"
  - Enable "Upload Week 4 Actuals" button
```

---

## Database Schema Changes

### New Table: weekly_actuals

**Purpose:** Store week-by-week actual sales for variance monitoring

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS weekly_actuals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    CONSTRAINT unique_workflow_week_store UNIQUE (workflow_id, week_number, store_id),
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_weekly_actuals_workflow ON weekly_actuals(workflow_id, week_number);
CREATE INDEX IF NOT EXISTS idx_weekly_actuals_store ON weekly_actuals(store_id);
CREATE INDEX IF NOT EXISTS idx_weekly_actuals_date ON weekly_actuals(week_start_date);
```

**Indexes Rationale:**
- `idx_weekly_actuals_workflow`: Fast lookup for chart queries (get all weeks for workflow)
- `idx_weekly_actuals_store`: Fast lookup for store-level variance reports
- `idx_weekly_actuals_date`: Fast lookup for date-range queries

**Constraints:**
- `unique_workflow_week_store`: Prevent duplicate actuals for same week/store
- `ON DELETE CASCADE`: If workflow deleted, delete associated actuals

### SQLAlchemy Model

```python
class WeeklyActuals(Base):
    """Weekly actual sales data for variance monitoring."""

    __tablename__ = "weekly_actuals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String(50), ForeignKey("workflows.workflow_id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(String(50), ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)
    actual_units_sold = Column(Integer, nullable=False)
    forecast_units_sold = Column(Integer, nullable=True)
    variance_pct = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workflow = relationship("Workflow", back_populates="weekly_actuals")
    store = relationship("Store")
    category = relationship("Category")

    # Constraints
    __table_args__ = (
        UniqueConstraint('workflow_id', 'week_number', 'store_id', name='unique_workflow_week_store'),
        Index('idx_weekly_actuals_workflow', 'workflow_id', 'week_number'),
        Index('idx_weekly_actuals_store', 'store_id'),
        Index('idx_weekly_actuals_date', 'week_start_date'),
    )
```

---

## API Design

### Endpoint: Upload Historical Sales

**POST /api/v1/data/upload/historical-sales**

**Request:**
```http
POST /api/v1/data/upload/historical-sales
Content-Type: multipart/form-data

Body:
  file: historical_sales.csv (File)
  category_id: womens_dresses (optional, auto-detect if omitted)
```

**Response (Success - 200 OK):**
```json
{
  "status": "success",
  "rows_inserted": 163944,
  "categories_detected": ["womens_dresses"],
  "date_range": {
    "start": "2023-01-01",
    "end": "2025-12-31"
  },
  "stores_count": 50,
  "processing_time_seconds": 12.5
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "status": "error",
  "error_code": "INVALID_CSV_FORMAT",
  "message": "Missing required columns",
  "details": {
    "expected_columns": ["week_start_date", "store_id", "quantity_sold"],
    "found_columns": ["date", "store_id", "quantity"],
    "missing_columns": ["week_start_date"]
  }
}
```

### Endpoint: Upload Weekly Actuals

**POST /api/v1/data/upload/weekly-actuals**

**Request:**
```http
POST /api/v1/data/upload/weekly-actuals
Content-Type: multipart/form-data

Body:
  workflow_id: wf_abc123 (form field)
  week_number: 3 (form field)
  file: week_3_actuals.csv (File)
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

---

## Testing Strategy

### Unit Tests

**Backend Tests:**
```
tests/services/
├── test_data_upload_service.py
│   ├── test_validate_csv_format()
│   ├── test_validate_date_range()
│   ├── test_batch_insert()
│   ├── test_detect_categories()
│   └── test_duplicate_protection()
├── test_weekly_actuals_service.py
│   ├── test_validate_week_range()
│   ├── test_aggregate_daily_to_weekly()
│   ├── test_calculate_variance()
│   └── test_check_reforecast_needed()
```

**Frontend Tests:**
```
frontend/src/components/
├── HistoricalDataUpload/__tests__/
│   ├── HistoricalDataUpload.test.tsx
│   └── HistoricalSalesUpload.test.tsx
└── WeeklyPerformanceChart/__tests__/
    └── WeeklyActualsUploadModal.test.tsx
```

### Integration Tests

**End-to-End Scenarios:**
1. Upload 163K rows historical sales CSV
2. Upload store attributes CSV
3. Upload week 1 actuals (normal variance)
4. Upload week 2 actuals (elevated variance)
5. Upload week 3 actuals (high variance - triggers re-forecast)
6. Attempt duplicate upload (should fail)
7. Upload with missing columns (should fail)
8. Upload with wrong date range (should fail)

### Manual Testing

**Test Cases:**
- [ ] Upload historical sales CSV (163,944 rows)
- [ ] Verify data inserted into database
- [ ] Upload store attributes CSV (50 rows)
- [ ] Upload weekly actuals with variance <10% (green)
- [ ] Upload weekly actuals with variance 10-20% (amber)
- [ ] Upload weekly actuals with variance >20% (red, re-forecast triggered)
- [ ] Verify chart updates with colored bars
- [ ] Verify alert banner shows correct variance status
- [ ] Test file validation (wrong format, missing columns)
- [ ] Test duplicate upload protection
- [ ] Test accessibility (keyboard navigation, screen readers)

---

## Risk Assessment

### High Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Large CSV upload timeout** | Medium | High | Batch insert (1000 rows), increase timeout to 60s |
| **Database constraint violations** | Medium | Medium | Pre-validation, detailed error messages |
| **Memory issues (163K rows)** | Low | High | Stream processing, batch insert |
| **Duplicate data corruption** | Low | High | UNIQUE constraints, pre-check duplicates |

### Medium Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Browser memory limits** | Low | Medium | Chunk file processing, show progress |
| **Date format inconsistencies** | Medium | Low | Strict validation, show expected format |
| **Missing stores in CSV** | Medium | Low | Validate against stores table, detailed error |

---

## Success Metrics

### Functional Metrics
- ✅ User can upload 163,944 rows in <30 seconds
- ✅ Variance calculation accuracy: 100%
- ✅ Error messages are clear and actionable
- ✅ Re-forecast trigger accuracy: 100% (variance >20%)

### Technical Metrics
- ✅ API response time: <2 seconds (1000 row batch)
- ✅ Database insert performance: >5,000 rows/second
- ✅ Frontend bundle size increase: <50KB

### Quality Metrics
- ✅ All acceptance criteria met
- ✅ Code coverage: >80%
- ✅ Zero console errors
- ✅ Accessibility score: 95+ (Lighthouse)

---

## Timeline

### Day 1 (6-8 hours)

**Morning (2-3 hours):**
- [ ] PHASE4.5-003: Database Schema
  - [ ] Add WeeklyActuals model
  - [ ] Create migration script
  - [ ] Test migration

**Afternoon (4-5 hours):**
- [ ] PHASE4.5-001: Historical Data Upload (Backend)
  - [ ] Create DataUploadService
  - [ ] Create API endpoints
  - [ ] Test with Postman

### Day 2 (6-9 hours)

**Morning (2-3 hours):**
- [ ] PHASE4.5-001: Historical Data Upload (Frontend)
  - [ ] Create HistoricalDataUpload components
  - [ ] Integrate into Section 0
  - [ ] Manual testing

**Afternoon (4-6 hours):**
- [ ] PHASE4.5-002: Weekly Actuals Upload
  - [ ] Create WeeklyActualsService
  - [ ] Create WeeklyActualsUploadModal
  - [ ] Integrate into Section 4
  - [ ] Manual testing

---

## Next Steps

After Phase 4.5 completion:

1. **Merge to Integration Branch**
2. **Update Phase 5 Stories** (PHASE5-004 database refactor)
3. **Create Phase 5 Branch**
4. **Begin Phase 5 Implementation**

---

**Last Updated:** 2025-01-05
**Status:** Planning Complete
