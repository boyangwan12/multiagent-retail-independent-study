# PHASE 4.5 TECHNICAL DECISIONS

**Phase:** 4.5 - Data Upload Infrastructure
**Date:** 2025-01-05
**Status:** Architecture Finalized

---

## Overview

This document captures all technical decisions made during Phase 4.5 planning, including architecture choices, trade-offs, and rationale.

---

## Decision Log

### Decision 1: Database Storage vs CSV Files

**Context:**
Phase 5 Context Assembly needs access to historical sales data and store attributes. Should uploaded CSV data be stored in the file system or inserted into database tables?

**Options Considered:**

**Option A: Store CSV Files**
- ✅ Simple implementation (save file to disk)
- ✅ Preserve original data format
- ✅ Fast upload (no parsing)
- ❌ Duplicate data source (database + files)
- ❌ Complex queries (need to parse CSV each time)
- ❌ No referential integrity
- ❌ Harder to validate data consistency

**Option B: Insert into Database** ⭐ **CHOSEN**
- ✅ Single source of truth
- ✅ Referential integrity (foreign keys)
- ✅ Efficient queries (SQL vs CSV parsing)
- ✅ Consistent with seed_db.py approach
- ✅ Production-ready architecture
- ❌ Slower upload (parsing + insert)
- ❌ More complex implementation

**Decision:** **Option B (Database Storage)**

**Rationale:**
1. **Consistency:** seed_db.py already populates database with 163,944 rows of historical_sales. Storing CSV files would create duplicate data sources.
2. **Production-Ready:** Databases are designed for concurrent access, ACID transactions, and referential integrity. CSV files are not.
3. **Query Performance:** Phase 5 Context Assembly will query data repeatedly. SQL queries are orders of magnitude faster than parsing CSV files.
4. **Data Validation:** Database constraints (FOREIGN KEY, UNIQUE, NOT NULL) prevent data corruption.
5. **Single Source of Truth:** All agents query the same database, ensuring consistency.

**Impact:**
- Phase 5 PHASE5-004 (Context Assembly) needs minor refactor (2-3 hours) to query database instead of reading CSV files.

---

### Decision 2: Batch Insert Strategy

**Context:**
Historical sales CSV contains 163,944 rows. Inserting one-by-one is slow. How should we optimize bulk inserts?

**Options Considered:**

**Option A: Insert One-by-One**
- ✅ Simple implementation
- ❌ Extremely slow (~30 minutes for 163K rows)
- ❌ High transaction overhead
- ❌ Poor user experience

**Option B: Single Bulk Insert (All Rows)**
- ✅ Fastest (single transaction)
- ❌ High memory usage (load all 163K rows into memory)
- ❌ Risk of timeout
- ❌ No progress updates

**Option C: Batch Insert (1000 rows at a time)** ⭐ **CHOSEN**
- ✅ Balanced memory usage
- ✅ Fast performance (~10-15 seconds for 163K rows)
- ✅ Can show progress (every 1000 rows)
- ✅ Resilient to timeouts
- ❌ Slightly more complex implementation

**Decision:** **Option C (Batch Insert - 1000 rows)**

**Rationale:**
1. **Performance:** Benchmarks show ~5,000-10,000 rows/second with batch insert
2. **Memory Efficiency:** 1000 rows at a time uses <1MB memory per batch
3. **User Experience:** Can update progress bar every batch
4. **Resilience:** If batch fails, can retry that batch without losing all data

**Implementation:**
```python
def batch_insert(self, rows: List[Dict], batch_size: int = 1000):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        objects = [HistoricalSales(**row) for row in batch]
        session.bulk_save_objects(objects)
        session.commit()
        logger.info(f"Inserted batch {i//batch_size + 1} ({len(batch)} rows)")
```

---

### Decision 3: CSV Validation Strategy

**Context:**
Uploaded CSVs may have wrong format, missing columns, invalid dates, etc. When should validation happen?

**Options Considered:**

**Option A: Validate During Insert**
- ✅ Simple implementation
- ❌ Fail after partial insert (e.g., fail at row 5000, rows 1-4999 already inserted)
- ❌ Poor user experience (need to manually clean up)
- ❌ Data corruption risk

**Option B: Pre-Validate Before Insert** ⭐ **CHOSEN**
- ✅ Fail fast (before any database changes)
- ✅ Detailed error messages (all errors at once)
- ✅ No partial inserts
- ✅ Better user experience
- ❌ Slightly slower (parse CSV twice - validate, then insert)

**Decision:** **Option B (Pre-Validate Before Insert)**

**Rationale:**
1. **Data Integrity:** No partial inserts, no need for rollback
2. **User Experience:** Show all validation errors upfront (e.g., "Missing columns: week_start_date, quantity_sold. Invalid dates in rows: 15, 22, 38")
3. **Fail Fast:** Detect issues before wasting time on insert

**Validation Checks:**
1. **Format Validation:**
   - Required columns present
   - Column types correct (date, int, string)
2. **Business Logic Validation:**
   - Dates in valid range (e.g., 2020-2025)
   - store_id exists in stores table
   - category_id exists in categories table
   - No duplicate records
3. **Data Integrity Validation:**
   - No missing values in required columns
   - Week ranges are complete (all 7 days)

---

### Decision 4: Duplicate Upload Protection

**Context:**
User might accidentally upload the same CSV twice. How should we handle duplicates?

**Options Considered:**

**Option A: Allow Duplicates**
- ✅ Simple implementation
- ❌ Data corruption
- ❌ Inflated metrics
- ❌ Hard to clean up

**Option B: Check Before Insert**
- ✅ Prevents duplicates
- ❌ Slow (query database for every row)
- ❌ Complex logic

**Option C: Database UNIQUE Constraints** ⭐ **CHOSEN**
- ✅ Database-level protection
- ✅ Fast (index-based lookup)
- ✅ Automatic enforcement
- ✅ Clear error messages
- ❌ Fails entire batch if one duplicate found

**Decision:** **Option C (Database UNIQUE Constraints)**

**Rationale:**
1. **Performance:** Database indexes handle duplicate detection efficiently
2. **Reliability:** Enforced at database level, can't be bypassed
3. **Clarity:** Clear error messages ("UNIQUE constraint failed: historical_sales.sale_id")

**Implementation:**
```sql
-- historical_sales: Already has primary key (sale_id)
-- weekly_actuals: Add UNIQUE constraint
CONSTRAINT unique_workflow_week_store UNIQUE (workflow_id, week_number, store_id)
```

**Trade-off:** If user uploads same file twice, we return 400 error instead of silently ignoring duplicates. This is intentional - better to alert user than hide the issue.

---

### Decision 5: Variance Calculation (Client vs Server)

**Context:**
Weekly actuals upload requires variance calculation (forecast vs actual). Should this happen on client (React) or server (FastAPI)?

**Options Considered:**

**Option A: Client-Side Calculation**
- ✅ Reduces server load
- ❌ Inconsistent logic (if client logic changes, server must change too)
- ❌ Harder to test
- ❌ Security risk (client can manipulate calculations)

**Option B: Server-Side Calculation** ⭐ **CHOSEN**
- ✅ Single source of truth for business logic
- ✅ Easier to test (unit tests)
- ✅ Secure (client can't manipulate)
- ✅ Consistent across all clients
- ❌ Slightly higher server load

**Decision:** **Option B (Server-Side Calculation)**

**Rationale:**
1. **Business Logic Belongs on Server:** Variance calculation is core business logic, not UI logic
2. **Consistency:** All clients (web, mobile, API consumers) get same calculation
3. **Security:** Client can't manipulate variance to bypass re-forecast triggers
4. **Testability:** Easy to write unit tests for variance calculation

**Implementation:**
```python
def calculate_variance(forecast: int, actual: int) -> Dict:
    variance_pct = (actual - forecast) / forecast

    if variance_pct <= 0.10:
        status = "NORMAL"
        color = "green"
    elif variance_pct <= 0.20:
        status = "ELEVATED"
        color = "amber"
    else:
        status = "HIGH"
        color = "red"

    return {
        "variance_pct": variance_pct,
        "variance_status": status,
        "variance_color": color
    }
```

---

### Decision 6: Re-forecast Trigger Implementation

**Context:**
PRD states: "If variance exceeds 20%, system should trigger re-forecast." Phase 4.5 has no orchestrator (that's Phase 5). How do we handle this?

**Options Considered:**

**Option A: Fully Implement Re-forecast**
- ✅ Complete feature
- ❌ Out of scope (orchestrator is Phase 5)
- ❌ Premature implementation

**Option B: Log Warning + Placeholder** ⭐ **CHOSEN**
- ✅ Acknowledges requirement
- ✅ Logs event for monitoring
- ✅ Returns flag to frontend
- ✅ Easy to integrate with Phase 5 orchestrator
- ❌ Not fully functional until Phase 5

**Option C: Skip Re-forecast**
- ✅ Simple
- ❌ Incomplete implementation
- ❌ PRD requirement ignored

**Decision:** **Option B (Log Warning + Placeholder)**

**Rationale:**
1. **Scope Boundary:** Phase 4.5 is data upload infrastructure. Orchestration belongs in Phase 5.
2. **Forward Compatibility:** Phase 5 orchestrator can listen for these log events or query weekly_actuals table for high variance.
3. **User Feedback:** Frontend shows "Re-forecast triggered" alert, so user knows system detected the issue.

**Implementation:**
```python
def check_reforecast_needed(variance_pct: float) -> bool:
    if variance_pct > 0.20:
        logger.warning(
            f"High variance detected ({variance_pct:.1%}). "
            f"Re-forecast workflow should be triggered (Phase 5 implementation)."
        )
        return True
    return False
```

**Phase 5 Integration:**
Phase 5 orchestrator will:
1. Query weekly_actuals for variance_pct > 0.20
2. Create new workflow with type="reforecast"
3. Route to Demand Agent for re-forecast
4. Update original workflow with reforecast_workflow_id

---

### Decision 7: Weekly Actuals Granularity

**Context:**
Weekly actuals CSV contains daily data (7 days × 50 stores = 350 rows per week). Should we store daily data or aggregate to weekly totals?

**Options Considered:**

**Option A: Store Daily Data**
- ✅ Preserve granularity
- ✅ Enables daily variance analysis (future feature)
- ❌ 12 weeks × 350 rows = 4,200 rows per workflow
- ❌ More complex queries
- ❌ Higher storage

**Option B: Aggregate to Weekly Totals** ⭐ **CHOSEN**
- ✅ Simpler schema (1 row per store per week)
- ✅ Faster queries
- ✅ Matches PRD requirement ("weekly performance chart")
- ✅ 12 weeks × 50 stores = 600 rows per workflow
- ❌ Lose daily granularity

**Decision:** **Option B (Aggregate to Weekly Totals)**

**Rationale:**
1. **PRD Requirement:** "Weekly Performance Chart" shows weekly variance, not daily
2. **Query Performance:** Querying 600 rows is 7× faster than 4,200 rows
3. **Storage Efficiency:** 7× less data
4. **Schema Simplicity:** weekly_actuals table is easier to understand

**Trade-off:** If future requirement needs daily granularity, we can:
1. Add daily_actuals table (separate concern)
2. Or keep raw CSV in blob storage (archive)

For MVP, weekly aggregation is sufficient.

---

### Decision 8: Category Detection Strategy

**Context:**
Historical sales upload needs category_id. Should user manually specify category or auto-detect from data/filename?

**Options Considered:**

**Option A: User Specifies Category**
- ✅ Explicit, no ambiguity
- ❌ Extra form field (poor UX)
- ❌ User might select wrong category

**Option B: Auto-Detect from Filename**
- ✅ No manual input
- ✅ Common pattern (historical_sales_womens_dresses.csv)
- ❌ Unreliable (user might name file differently)

**Option C: Auto-Detect from Data** ⭐ **CHOSEN**
- ✅ Most reliable
- ✅ Works regardless of filename
- ✅ Validates against categories table
- ❌ Requires parsing CSV

**Decision:** **Option C (Auto-Detect from Data)**

**Rationale:**
1. **Reliability:** Data content is source of truth, not filename
2. **User Experience:** No manual input required
3. **Validation:** Can validate category_id exists in database

**Implementation:**
```python
def detect_categories(csv_data: List[Dict]) -> List[str]:
    """Detect unique categories from CSV data."""
    categories = set()
    for row in csv_data:
        if 'category_id' in row:
            categories.add(row['category_id'])

    # Validate all categories exist in database
    valid_categories = session.query(Category.category_id).all()
    valid_category_ids = {cat[0] for cat in valid_categories}

    invalid = categories - valid_category_ids
    if invalid:
        raise ValueError(f"Invalid categories: {invalid}")

    return list(categories)
```

**Fallback:** If category_id column missing, user must specify category in form field.

---

### Decision 9: File Upload Size Limits

**Context:**
Historical sales CSV can be large (163K rows ≈ 10-15MB). What size limits should we enforce?

**Options Considered:**

**Option A: No Limit**
- ✅ Flexible
- ❌ Risk of DoS (user uploads 1GB file)
- ❌ Server memory issues

**Option B: Strict Limit (10MB)**
- ✅ Prevents abuse
- ❌ Might reject valid files

**Option C: Generous Limit (50MB)** ⭐ **CHOSEN**
- ✅ Accommodates largest expected files
- ✅ Prevents abuse
- ✅ Clear error message if exceeded
- ❌ Might allow very large files

**Decision:** **Option C (50MB Limit)**

**Rationale:**
1. **Expected Data:** 163K rows × ~100 bytes/row ≈ 16MB raw data, ~10-12MB compressed CSV
2. **Safety Margin:** 50MB allows 3-5× expected size (accounts for extra columns, formatting)
3. **DoS Protection:** Prevents malicious 1GB+ uploads

**Implementation:**
```python
# FastAPI endpoint
@router.post("/upload/historical-sales")
async def upload_historical_sales(
    file: UploadFile = File(..., max_length=50*1024*1024)  # 50MB
):
    ...
```

**Frontend Validation:**
```typescript
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

if (file.size > MAX_FILE_SIZE) {
  throw new Error("File size exceeds 50MB limit");
}
```

---

### Decision 10: Date Range Validation for Weekly Actuals

**Context:**
Weekly actuals upload specifies week_number (1-52). How do we map week_number to actual date range?

**Options Considered:**

**Option A: User Specifies Date Range**
- ✅ Explicit
- ❌ Extra form fields (poor UX)
- ❌ Risk of mismatch (week_number=3 but dates for week 4)

**Option B: Derive from Workflow Start Date** ⭐ **CHOSEN**
- ✅ Automatic, no manual input
- ✅ Consistent with workflow configuration
- ✅ Single source of truth (workflow.season_start_date)
- ❌ Requires workflow to store start date

**Decision:** **Option B (Derive from Workflow Start Date)**

**Rationale:**
1. **Consistency:** Workflow already has season_start_date (from parameter extraction)
2. **User Experience:** User only specifies week_number, system calculates date range
3. **Validation:** Can validate CSV dates match expected week range

**Implementation:**
```python
def get_week_date_range(workflow_id: str, week_number: int) -> Tuple[date, date]:
    """Calculate week date range from workflow start date."""
    workflow = session.query(Workflow).filter_by(workflow_id=workflow_id).first()
    season_start = workflow.season_start_date

    week_start = season_start + timedelta(weeks=week_number - 1)
    week_end = week_start + timedelta(days=6)

    return (week_start, week_end)

# Validation
expected_start, expected_end = get_week_date_range(workflow_id, week_number)
csv_dates = [row['date'] for row in csv_data]

if min(csv_dates) != expected_start or max(csv_dates) != expected_end:
    raise ValueError(
        f"Date range mismatch. Expected {expected_start} to {expected_end}, "
        f"found {min(csv_dates)} to {max(csv_dates)}"
    )
```

---

## Architecture Diagrams

### Data Upload Flow (Sequence Diagram)

```
User                Frontend              Backend API           DataUploadService      Database
 |                     |                       |                       |                  |
 |-- Upload CSV ------>|                       |                       |                  |
 |                     |                       |                       |                  |
 |                     |-- Validate file ----->|                       |                  |
 |                     |    (size, extension)  |                       |                  |
 |                     |                       |                       |                  |
 |                     |-- POST /upload ------>|                       |                  |
 |                     |    (multipart/form)   |                       |                  |
 |                     |                       |                       |                  |
 |                     |                       |-- validate_csv() ---->|                  |
 |                     |                       |                       |                  |
 |                     |                       |<----- errors ---------|                  |
 |                     |                       |   (if validation fails)                  |
 |                     |                       |                       |                  |
 |                     |                       |-- batch_insert() ---->|                  |
 |                     |                       |                       |-- INSERT (1000)-->|
 |                     |                       |                       |<----- OK --------|
 |                     |                       |                       |-- INSERT (1000)-->|
 |                     |                       |                       |<----- OK --------|
 |                     |                       |                       |      ...          |
 |                     |                       |                       |                  |
 |                     |                       |<----- summary --------|                  |
 |                     |                       |   (rows inserted,     |                  |
 |                     |                       |    categories, etc)   |                  |
 |                     |                       |                       |                  |
 |                     |<---- 200 OK ----------|                       |                  |
 |                     |   {status: success,   |                       |                  |
 |                     |    rows: 163944}      |                       |                  |
 |                     |                       |                       |                  |
 |<- Success toast ----|                       |                       |                  |
 | "163,944 rows       |                       |                       |                  |
 |  uploaded"          |                       |                       |                  |
```

### Database Schema (ERD)

```
┌─────────────────────┐
│    workflows        │
│─────────────────────│
│ workflow_id (PK)    │◄─────────────┐
│ workflow_type       │              │
│ status              │              │
│ season_start_date   │              │
│ ...                 │              │
└─────────────────────┘              │
                                     │ FK
┌─────────────────────┐              │
│  historical_sales   │              │
│─────────────────────│              │
│ sale_id (PK)        │              │
│ week_start_date     │              │
│ category_id (FK)────┼──────┐       │
│ store_id (FK)───────┼────┐ │       │
│ units_sold          │    │ │       │
└─────────────────────┘    │ │       │
                           │ │       │
                           │ │       │
┌─────────────────────┐    │ │   ┌───────────────────────┐
│     stores          │    │ │   │   weekly_actuals      │
│─────────────────────│    │ │   │───────────────────────│
│ store_id (PK)       │◄───┼─┼───│ id (PK)               │
│ store_name          │    │ │   │ workflow_id (FK)──────┼──►
│ cluster_id (FK)     │    │ │   │ week_number           │
│ store_size_sqft     │    │ │   │ week_start_date       │
│ location_tier       │    │ │   │ store_id (FK)─────────┼──┘
│ ...                 │    │ │   │ category_id (FK)──────┼──┐
└─────────────────────┘    │ │   │ actual_units_sold     │  │
                           │ │   │ forecast_units_sold   │  │
                           │ │   │ variance_pct          │  │
┌─────────────────────┐    │ │   │ uploaded_at           │  │
│    categories       │    │ │   │                       │  │
│─────────────────────│    │ │   │ UNIQUE (workflow_id,  │  │
│ category_id (PK)    │◄───┴─┴───│  week_number,         │  │
│ category_name       │          │  store_id)            │  │
│ ...                 │          └───────────────────────┘  │
└─────────────────────┘◄─────────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Web Framework** | FastAPI | 0.104+ | Async support, automatic OpenAPI docs, type safety |
| **Database** | SQLite | 3.x | Lightweight, zero-config, sufficient for MVP |
| **ORM** | SQLAlchemy | 2.0+ | Industry standard, type-safe, migration support |
| **CSV Parsing** | pandas | 2.0+ | Fast CSV parsing, data validation, built-in aggregation |
| **File Upload** | python-multipart | 0.0.6+ | FastAPI dependency for multipart/form-data |

### Frontend

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **UI Framework** | React | 18.x | Component reusability, large ecosystem |
| **UI Components** | shadcn/ui | Latest | Accessible, customizable, Tailwind-based |
| **File Upload** | react-dropzone | 14.x | Drag-and-drop, file validation, accessibility |
| **HTTP Client** | axios | 1.6+ | Interceptors, timeout support, request cancellation |
| **State Management** | React hooks | Built-in | Simple state needs, avoid over-engineering |

---

## Security Considerations

### File Upload Security

1. **File Type Validation:**
   - Only accept .csv files
   - Validate MIME type (text/csv)
   - Reject executable files (.exe, .sh, .bat)

2. **Size Limits:**
   - Frontend: 50MB max
   - Backend: 50MB max (double-check)

3. **Content Validation:**
   - Parse CSV with strict mode
   - Sanitize input (prevent SQL injection)
   - Validate all values against expected types

4. **Rate Limiting:**
   - Max 10 uploads per minute per user (prevent DoS)

### Data Privacy

1. **No PII in Logs:**
   - Log summary stats only (row counts, date ranges)
   - Never log actual sales data or store names

2. **Access Control:**
   - (Phase 6: Authentication) Only authenticated users can upload
   - (Phase 6: Authorization) Users can only upload to their own workflows

---

## Performance Benchmarks

### Target Metrics

| Operation | Target | Acceptable | Unacceptable |
|-----------|--------|------------|--------------|
| **Upload 163K rows** | <15s | <30s | >60s |
| **Batch insert (1000 rows)** | <200ms | <500ms | >1s |
| **CSV validation** | <2s | <5s | >10s |
| **Variance calculation (50 stores)** | <100ms | <500ms | >1s |
| **API response time** | <2s | <5s | >10s |

### Database Performance

**Indexes:**
- `historical_sales`: (week_start_date, category_id, store_id)
- `weekly_actuals`: (workflow_id, week_number), (store_id), (week_start_date)

**Expected Query Performance:**
- Get all historical sales for category: <100ms (indexed)
- Get weekly actuals for workflow: <50ms (indexed)
- Calculate variance for week: <100ms (indexed)

---

## Monitoring & Logging

### Log Levels

**INFO:**
- Upload started (workflow_id, filename, size)
- Batch insert progress (batch 1/164, 2/164, ...)
- Upload complete (rows inserted, processing time)

**WARNING:**
- High variance detected (variance_pct > 20%)
- Duplicate upload attempt

**ERROR:**
- Validation failed (missing columns, invalid dates)
- Database insert failed
- Unexpected errors

### Metrics to Track

1. **Upload Metrics:**
   - Total uploads per day
   - Average upload size (rows)
   - Average upload time (seconds)
   - Upload success rate (%)

2. **Performance Metrics:**
   - Database insert rate (rows/second)
   - API response time (p50, p95, p99)
   - Memory usage during upload

3. **Business Metrics:**
   - Workflows with historical data uploaded (%)
   - Average variance per week
   - Re-forecast trigger rate (%)

---

## Future Enhancements (Post-MVP)

1. **Async Background Processing:**
   - Use Celery for large CSV uploads
   - Show progress bar via WebSocket
   - Email notification on completion

2. **Data Validation Report:**
   - Downloadable PDF/CSV with validation errors
   - Summary stats (rows processed, errors found)
   - Suggested fixes

3. **CSV Preview:**
   - Show first 10 rows before upload
   - Confirm column mapping
   - Manual fixes for edge cases

4. **Bulk Operations:**
   - Delete all data for workflow
   - Overwrite existing data (with confirmation)
   - Export data to CSV

5. **Advanced Variance Analysis:**
   - Daily variance (not just weekly)
   - Store-level variance heatmap
   - Variance trend over time

---

## Lessons Learned (Post-Implementation)

_To be filled after Phase 4.5 implementation completes._

---

## References

- **PRD v3.3:** Stories 1.1, 1.2, 3.1
- **Technical Architecture v3.3:** Section 4.8 (Variance Monitoring)
- **Frontend Spec v3.3:** Section 4 (Weekly Performance Chart)
- **seed_db.py:** Database schema reference

---

**Last Updated:** 2025-01-05
**Status:** Architecture Finalized
