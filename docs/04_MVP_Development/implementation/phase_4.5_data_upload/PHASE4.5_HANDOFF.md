# PHASE 4.5 HANDOFF DOCUMENT

**Phase:** 4.5 - Data Upload Infrastructure
**Status:** Ready for Implementation
**Start Date:** TBD
**Target Completion:** 1.5-2 days (12-17 hours)
**Branch:** `phase4.5-data-upload`

---

## Executive Summary

Phase 4.5 bridges Phase 4 (Agent Workflow) and Phase 5 (Multi-Agent Orchestrator) by implementing the missing data upload workflows required by the PRD:

- **PRD Story 1.1:** Upload Historical Sales Data (2-3 years)
- **PRD Story 1.2:** Upload Store Attributes
- **PRD Story 3.1:** Upload Weekly Actuals (in-season monitoring)

**Why Phase 4.5 Exists:**
- Phase 4 implemented agent supplementary uploads (PHASE4-007) but NOT historical training data
- Phase 5 requires historical data for Context Assembly
- Creating dedicated phase ensures clean separation and complete PRD coverage

**Architecture Decision:**
- Store uploaded CSV data in **database tables** (not file system)
- Use existing seed_db.py data structure (historical_sales, stores, categories)
- Add new weekly_actuals table for variance monitoring
- Phase 5 queries database instead of reading CSV files

---

## What Was Completed in Phase 4

### Implemented Features
1. ✅ Parameter Extraction (PHASE4-001)
2. ✅ Workflow Orchestration (PHASE4-002, 003)
3. ✅ Polling-based Workflow Monitoring (PHASE4-004)
4. ✅ Forecast Display (PHASE4-005)
5. ✅ Weekly Performance Chart (PHASE4-005)
6. ✅ Replenishment Queue (PHASE4-005)
7. ✅ Markdown Decision Display (PHASE4-006)
8. ✅ Performance Metrics Display (PHASE4-006)
9. ✅ Agent Supplementary CSV Upload (PHASE4-007) - **Optional data only**

### What's Missing (Blockers for Phase 5)
- ❌ Historical Sales Upload (PRD Story 1.1) - **P0 Blocker**
- ❌ Store Attributes Upload (PRD Story 1.2) - **P0 Blocker**
- ❌ Weekly Actuals Upload (PRD Story 3.1) - **P0 Blocker**

---

## Phase 4.5 Scope

### Stories to Implement

| Story ID | Story Name | Effort | Priority | Dependencies |
|----------|------------|--------|----------|--------------|
| **PHASE4.5-001** | Historical Training Data Upload | 6-8 hours | P0 | PHASE4.5-003 |
| **PHASE4.5-002** | Weekly Actuals Upload | 4-6 hours | P0 | PHASE4.5-001 |
| **PHASE4.5-003** | Database Schema & Migration | 2-3 hours | P0 | None |

**Total Effort:** 12-17 hours (1.5-2 days)

### Implementation Order
1. **PHASE4.5-003** (Database Schema) - Run migration script first
2. **PHASE4.5-001** (Historical Data Upload) - Seed database with training data
3. **PHASE4.5-002** (Weekly Actuals Upload) - In-season monitoring

---

## Technical Architecture

### Backend Components

**New Services:**
```
backend/app/services/
├── data_upload_service.py       # Historical sales & store attributes upload
└── weekly_actuals_service.py    # Weekly actuals upload & variance calculation
```

**New API Endpoints:**
```
POST /api/v1/data/upload/historical-sales
POST /api/v1/data/upload/store-attributes
POST /api/v1/data/upload/weekly-actuals
```

**Database Schema:**
```
Tables (Existing):
- historical_sales (validated)
- stores (validated)
- categories (validated)
- workflows (validated)

Tables (New):
- weekly_actuals (created by migration)
```

**Migration Script:**
```
backend/scripts/migrate_phase_4_5.py
```

### Frontend Components

**New Components:**
```
frontend/src/components/
├── HistoricalDataUpload/
│   ├── HistoricalDataUpload.tsx         # Main upload container
│   ├── HistoricalSalesUpload.tsx        # Sales CSV upload
│   └── StoreAttributesUpload.tsx        # Store CSV upload
└── WeeklyPerformanceChart/
    └── WeeklyActualsUploadModal.tsx     # Weekly actuals upload modal
```

**Integration Points:**
- Section 0 (Parameter Extraction): Add "Upload Historical Data" button
- Section 4 (Weekly Performance Chart): Add "Upload Week N Actuals" button

---

## Database Schema

### Existing Tables (Validated)

**historical_sales:**
```sql
CREATE TABLE historical_sales (
    sale_id VARCHAR(100) PRIMARY KEY,
    week_start_date DATE NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    units_sold INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
```

**stores:**
```sql
CREATE TABLE stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    cluster_id VARCHAR(50),
    store_size_sqft INTEGER NOT NULL,
    location_tier VARCHAR(20) NOT NULL,
    median_income INTEGER NOT NULL,
    store_format VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    avg_weekly_sales_12mo FLOAT NOT NULL,
    FOREIGN KEY (cluster_id) REFERENCES store_clusters(cluster_id)
);
```

### New Table: weekly_actuals

**Purpose:** Store week-by-week actual sales for variance monitoring

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

---

## Setup Instructions

### Prerequisites

1. **Phase 4 Complete:**
   - All Phase 4 stories implemented
   - Database initialized (backend/scripts/init_db.py run)
   - Backend running on http://localhost:8001
   - Frontend running on http://localhost:5173

2. **Dependencies Installed:**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

### Step 1: Create Phase 4.5 Branch

```bash
git checkout phase4-integration
git pull origin phase4-integration
git checkout -b phase4.5-data-upload
```

### Step 2: Run Database Migration

```bash
cd backend
python scripts/migrate_phase_4_5.py
```

**Expected Output:**
```
🔧 PHASE 4.5 DATABASE MIGRATION
Database: sqlite:///./fashion_forecast.db

==========================================================
VALIDATING EXISTING TABLES
==========================================================
✓ Table 'historical_sales' exists
✓ Table 'stores' exists
✓ Table 'categories' exists
✓ Table 'workflows' exists
✓ All required tables exist

==========================================================
CREATING WEEKLY_ACTUALS TABLE
==========================================================
✓ Created table 'weekly_actuals'
✓ Verified table 'weekly_actuals' exists

==========================================================
VALIDATING TABLE SCHEMA
==========================================================
✓ Column 'id' exists
✓ Column 'workflow_id' exists
✓ Column 'week_number' exists
...

==========================================================
TESTING INSERT & QUERY
==========================================================
✓ Test insert successful
✓ Test query successful: <WeeklyActuals(workflow=test_workflow, week=1, store=S001, actual=150)>
✓ Test data cleaned up

==========================================================
TABLE STATISTICS
==========================================================
historical_sales    : 163,944 rows
stores              : 50 rows
categories          : 7 rows
workflows           : 0 rows
weekly_actuals      : 0 rows

==========================================================
🎉 MIGRATION COMPLETE
==========================================================
✓ weekly_actuals table ready
✓ All indexes created
✓ Foreign keys validated
✓ Insert/query operations tested

Ready for Phase 4.5 data upload workflows!
```

### Step 3: Verify Database Schema

```bash
# Open SQLite database
sqlite3 backend/fashion_forecast.db

# Check tables
.tables

# Check weekly_actuals schema
.schema weekly_actuals

# Exit
.quit
```

### Step 4: Start Development Servers

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8001

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Step 5: Verify Backend Endpoints

```bash
# Health check
curl http://localhost:8001/api/v1/health

# Test upload endpoints (should return 422 - validation error expected)
curl -X POST http://localhost:8001/api/v1/data/upload/historical-sales
curl -X POST http://localhost:8001/api/v1/data/upload/store-attributes
curl -X POST http://localhost:8001/api/v1/data/upload/weekly-actuals
```

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review all Phase 4.5 story files
- [ ] Create phase4.5-data-upload branch
- [ ] Run database migration (migrate_phase_4_5.py)
- [ ] Verify all tables exist
- [ ] Backend and frontend servers running

### PHASE4.5-003: Database Schema (2-3 hours)
- [ ] Add WeeklyActuals model to models.py
- [ ] Update Workflow model with relationship
- [ ] Create migrate_phase_4_5.py script
- [ ] Test migration on clean database
- [ ] Test migration idempotency
- [ ] Update init_db.py to include WeeklyActuals

### PHASE4.5-001: Historical Data Upload (6-8 hours)
- [ ] Create DataUploadService
- [ ] Create POST /upload/historical-sales endpoint
- [ ] Create POST /upload/store-attributes endpoint
- [ ] Create HistoricalDataUpload component
- [ ] Integrate into Section 0 (Parameter Extraction)
- [ ] Test CSV validation
- [ ] Test batch insert (1000 rows)
- [ ] Test auto-detect categories
- [ ] Manual testing with sample CSVs

### PHASE4.5-002: Weekly Actuals Upload (4-6 hours)
- [ ] Create WeeklyActualsService
- [ ] Create POST /upload/weekly-actuals endpoint
- [ ] Implement variance calculation
- [ ] Create WeeklyActualsUploadModal component
- [ ] Integrate into Section 4 (Weekly Performance Chart)
- [ ] Test variance thresholds (green/amber/red)
- [ ] Test re-forecast trigger (variance >20%)
- [ ] Test chart update with actual bars

### Testing & QA
- [ ] Test all upload endpoints with Postman
- [ ] Test file validation (wrong format, missing columns)
- [ ] Test duplicate upload protection
- [ ] Test database constraints (foreign keys)
- [ ] Test frontend error handling
- [ ] Test accessibility (keyboard navigation, screen readers)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)

### Documentation
- [ ] Update README.md with Phase 4.5
- [ ] Update API documentation
- [ ] Document CSV formats
- [ ] Update phase timeline

---

## Test Data

### Historical Sales CSV (Sample)

**File:** `test_data/historical_sales.csv`
**Expected Format:**
```csv
week_start_date,store_id,quantity_sold
2023-01-01,S001,120
2023-01-01,S002,95
2023-01-01,S003,150
...
```

**Expected Rows:** ~163,944 (50 stores × 7 categories × 156 weeks)

### Store Attributes CSV (Sample)

**File:** `test_data/store_attributes.csv`
**Expected Format:**
```csv
store_id,store_name,store_size_sqft,location_tier,median_income,store_format,region
S001,Manhattan Flagship,25000,Urban Premium,125000,Flagship,Northeast
S002,Brooklyn Heights,18000,Urban Premium,110000,Standard,Northeast
S003,Queens Center,15000,Suburban Standard,85000,Standard,Northeast
...
```

**Expected Rows:** 50 stores

### Weekly Actuals CSV (Sample)

**File:** `test_data/week_1_actuals.csv`
**Expected Format:**
```csv
date,store_id,quantity_sold
2025-03-01,S001,18
2025-03-02,S001,22
2025-03-03,S001,25
...
2025-03-07,S050,19
```

**Expected Rows:** ~350 (50 stores × 7 days)

---

## Known Issues & Limitations

### Current Limitations
1. **No Overwrite Protection:** Uploading same data twice will create duplicates (unless UNIQUE constraint violated)
2. **No Progress Bar:** Large CSV uploads (163K rows) show no progress indicator
3. **No Async Processing:** Upload blocks until complete (could timeout on large files)
4. **No Rollback on Partial Failure:** If row 5000 fails, rows 1-4999 already inserted

### Future Enhancements (Post-Phase 4.5)
- Background job processing with Celery
- Upload progress bar (polling-based updates)
- Data validation report (downloadable)
- CSV preview before upload
- Bulk delete/overwrite option

---

## Impact on Phase 5

### Required Changes to Phase 5

**PHASE5-004 (Context Assembly) - Minor Refactor (2-3 hours):**

**Before (CSV-based):**
```python
class ContextAssembler:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_historical_sales(self):
        return pd.read_csv(f"{self.data_dir}/historical_sales.csv")
```

**After (Database-based):**
```python
class ContextAssembler:
    def __init__(self, db_session: Session):
        self.db = db_session

    def load_historical_sales(self):
        query = self.db.query(HistoricalSales).all()
        return pd.DataFrame([row.__dict__ for row in query])
```

**No Impact On:**
- PHASE5-001 (Orchestrator Engine)
- PHASE5-002 (Agent Router)
- PHASE5-003 (Agent Handoff)
- PHASE5-005 (Approval Queue)
- PHASE5-006 (Dashboard Integration)

---

## Success Criteria

Phase 4.5 is complete when:

1. ✅ Database migration runs successfully
2. ✅ User can upload historical sales CSV (2-3 years)
3. ✅ User can upload store attributes CSV
4. ✅ User can upload weekly actuals CSV
5. ✅ System validates CSV format and date ranges
6. ✅ System inserts data into database tables
7. ✅ System calculates variance (forecast vs actual)
8. ✅ System displays variance with color coding (green/amber/red)
9. ✅ System triggers re-forecast alert when variance >20%
10. ✅ All acceptance criteria met for all 3 stories
11. ✅ Manual testing completed
12. ✅ Code merged to phase4-integration branch

---

## Handoff to Phase 5

After Phase 4.5 completion:

1. **Merge to Integration Branch:**
   ```bash
   git checkout phase4-integration
   git merge phase4.5-data-upload
   git push origin phase4-integration
   ```

2. **Update Phase 5 Stories:**
   - Modify PHASE5-004 to use database queries
   - Update PHASE5_OVERVIEW.md

3. **Create Phase 5 Branch:**
   ```bash
   git checkout -b phase5-orchestrator
   ```

4. **Verify Data Availability:**
   ```bash
   # Check data loaded
   python -c "
   from app.database.db import SessionLocal
   from app.database.models import HistoricalSales, Store
   db = SessionLocal()
   print(f'Historical Sales: {db.query(HistoricalSales).count()} rows')
   print(f'Stores: {db.query(Store).count()} rows')
   "
   ```

---

## Questions & Support

**Questions?** Check the story files:
- PHASE4.5-001-historical-data-upload.md
- PHASE4.5-002-weekly-actuals-upload.md
- PHASE4.5-003-database-schema.md

**Issues?** Review:
- technical_decisions.md (architecture rationale)
- implementation_plan.md (high-level overview)
- checklist.md (detailed task tracking)

---

**Last Updated:** 2025-01-05
**Phase Status:** Ready for Implementation
**Branch:** `phase4.5-data-upload`
