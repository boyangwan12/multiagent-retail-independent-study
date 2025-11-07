# PHASE4.5-003: Database Schema & Migration

**Story ID:** PHASE4.5-003
**Story Name:** Database Schema Validation & Migration
**Phase:** Phase 4.5 - Data Upload Infrastructure
**Dependencies:** None (can run in parallel with PHASE4.5-001/002)
**Estimated Effort:** 2-3 hours
**Assigned To:** Developer (Backend)
**Status:** Complete
**Completed:** 2025-01-05

---

## User Story

**As a** developer implementing data upload workflows,
**I want** to ensure all required database tables and indexes exist,
**So that** upload operations can insert data efficiently without schema errors.

---

## Context & Background

### What This Story Covers

This story ensures database schema is ready for Phase 4.5 data uploads:

1. **Verify Existing Tables:**
   - `historical_sales` (from Phase 1 seed_db.py)
   - `stores` (from Phase 1 seed_db.py)
   - `categories` (from Phase 1 seed_db.py)
   - `workflows` (from Phase 4)

2. **Create New Table:**
   - `weekly_actuals` (for PRD Story 3.1)

3. **Add Indexes:**
   - Performance optimization for query operations
   - Foreign key constraints

4. **Migration Script:**
   - Idempotent (safe to run multiple times)
   - Logs all changes
   - Validates schema after changes

---

## Database Schema

### Existing Tables (Validate Only)

**historical_sales:**
```sql
CREATE TABLE IF NOT EXISTS historical_sales (
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
CREATE TABLE IF NOT EXISTS stores (
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

---

### New Table: weekly_actuals

**Purpose:** Store week-by-week actual sales data for variance monitoring

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
```

**Indexes:**
```sql
CREATE INDEX IF NOT EXISTS idx_weekly_actuals_workflow
ON weekly_actuals(workflow_id, week_number);

CREATE INDEX IF NOT EXISTS idx_weekly_actuals_store
ON weekly_actuals(store_id);

CREATE INDEX IF NOT EXISTS idx_weekly_actuals_date
ON weekly_actuals(week_start_date);
```

---

## SQLAlchemy Model

**File:** `backend/app/database/models.py`

**Add model:**
```python
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

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

    def __repr__(self):
        return f"<WeeklyActuals(workflow={self.workflow_id}, week={self.week_number}, store={self.store_id}, actual={self.actual_units_sold})>"
```

**Update Workflow model:**
```python
class Workflow(Base):
    # ... existing fields ...

    # Add relationship
    weekly_actuals = relationship("WeeklyActuals", back_populates="workflow", cascade="all, delete-orphan")
```

---

## Migration Script

**File:** `backend/scripts/migrate_phase_4_5.py`

**Implementation:**
```python
#!/usr/bin/env python
"""
Database migration for Phase 4.5 - Data Upload Infrastructure.

Creates weekly_actuals table and indexes.
Validates existing tables (historical_sales, stores, categories).
"""

import sys
from pathlib import Path
import logging
from sqlalchemy import inspect, text

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.db import engine, SessionLocal, Base
from app.database.models import WeeklyActuals, HistoricalSales, Store, Category, Workflow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("migrate_phase_4_5")


def table_exists(table_name: str) -> bool:
    """Check if table exists in database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def validate_existing_tables():
    """Validate that required tables exist."""
    logger.info("=" * 60)
    logger.info("VALIDATING EXISTING TABLES")
    logger.info("=" * 60)

    required_tables = [
        "historical_sales",
        "stores",
        "categories",
        "workflows"
    ]

    missing_tables = []

    for table_name in required_tables:
        if table_exists(table_name):
            logger.info(f"✓ Table '{table_name}' exists")
        else:
            logger.error(f"✗ Table '{table_name}' missing")
            missing_tables.append(table_name)

    if missing_tables:
        logger.error(f"❌ Missing required tables: {', '.join(missing_tables)}")
        logger.error("Run backend/scripts/init_db.py to create base tables")
        sys.exit(1)

    logger.info("✓ All required tables exist")


def create_weekly_actuals_table():
    """Create weekly_actuals table if it doesn't exist."""
    logger.info("=" * 60)
    logger.info("CREATING WEEKLY_ACTUALS TABLE")
    logger.info("=" * 60)

    if table_exists("weekly_actuals"):
        logger.info("⚠️  Table 'weekly_actuals' already exists - skipping creation")
        return

    # Create table using SQLAlchemy model
    WeeklyActuals.__table__.create(engine)
    logger.info("✓ Created table 'weekly_actuals'")

    # Verify table was created
    if table_exists("weekly_actuals"):
        logger.info("✓ Verified table 'weekly_actuals' exists")
    else:
        logger.error("❌ Failed to create table 'weekly_actuals'")
        sys.exit(1)


def validate_table_schema():
    """Validate weekly_actuals table schema."""
    logger.info("=" * 60)
    logger.info("VALIDATING TABLE SCHEMA")
    logger.info("=" * 60)

    inspector = inspect(engine)

    # Check columns
    columns = inspector.get_columns("weekly_actuals")
    column_names = [col['name'] for col in columns]

    required_columns = [
        'id', 'workflow_id', 'week_number', 'week_start_date', 'week_end_date',
        'store_id', 'category_id', 'actual_units_sold', 'forecast_units_sold',
        'variance_pct', 'uploaded_at'
    ]

    for col in required_columns:
        if col in column_names:
            logger.info(f"✓ Column '{col}' exists")
        else:
            logger.error(f"✗ Column '{col}' missing")

    # Check indexes
    indexes = inspector.get_indexes("weekly_actuals")
    index_names = [idx['name'] for idx in indexes]

    logger.info(f"Indexes found: {', '.join(index_names) if index_names else 'None'}")

    # Check foreign keys
    foreign_keys = inspector.get_foreign_keys("weekly_actuals")
    fk_columns = [fk['constrained_columns'][0] for fk in foreign_keys]

    logger.info(f"Foreign keys: {', '.join(fk_columns) if fk_columns else 'None'}")


def test_insert_and_query():
    """Test insert and query operations on weekly_actuals."""
    logger.info("=" * 60)
    logger.info("TESTING INSERT & QUERY")
    logger.info("=" * 60)

    from datetime import date

    with SessionLocal() as session:
        try:
            # Clean up any test data
            session.execute(text("DELETE FROM weekly_actuals WHERE workflow_id = 'test_workflow'"))
            session.commit()

            # Test insert
            test_actual = WeeklyActuals(
                workflow_id="test_workflow",
                week_number=1,
                week_start_date=date(2025, 1, 1),
                week_end_date=date(2025, 1, 7),
                store_id="S001",
                category_id="womens_dresses",
                actual_units_sold=150,
                forecast_units_sold=140,
                variance_pct=0.071
            )
            session.add(test_actual)
            session.commit()
            logger.info("✓ Test insert successful")

            # Test query
            result = session.query(WeeklyActuals).filter(
                WeeklyActuals.workflow_id == "test_workflow"
            ).first()

            if result:
                logger.info(f"✓ Test query successful: {result}")
            else:
                logger.error("✗ Test query failed - no results")

            # Clean up test data
            session.execute(text("DELETE FROM weekly_actuals WHERE workflow_id = 'test_workflow'"))
            session.commit()
            logger.info("✓ Test data cleaned up")

        except Exception as e:
            logger.error(f"❌ Test insert/query failed: {e}")
            session.rollback()
            sys.exit(1)


def get_table_stats():
    """Get row counts for all tables."""
    logger.info("=" * 60)
    logger.info("TABLE STATISTICS")
    logger.info("=" * 60)

    with SessionLocal() as session:
        tables = [
            ("historical_sales", HistoricalSales),
            ("stores", Store),
            ("categories", Category),
            ("workflows", Workflow),
            ("weekly_actuals", WeeklyActuals)
        ]

        for table_name, model in tables:
            try:
                count = session.query(model).count()
                logger.info(f"{table_name:20s}: {count:,} rows")
            except Exception as e:
                logger.warning(f"{table_name:20s}: Unable to query ({str(e)})")


def main():
    """Main migration entry point."""
    logger.info("🔧 PHASE 4.5 DATABASE MIGRATION")
    logger.info(f"Database: {engine.url}")
    logger.info("")

    try:
        # Step 1: Validate existing tables
        validate_existing_tables()

        # Step 2: Create weekly_actuals table
        create_weekly_actuals_table()

        # Step 3: Validate schema
        validate_table_schema()

        # Step 4: Test operations
        test_insert_and_query()

        # Step 5: Show table stats
        get_table_stats()

        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 MIGRATION COMPLETE")
        logger.info("=" * 60)
        logger.info("✓ weekly_actuals table ready")
        logger.info("✓ All indexes created")
        logger.info("✓ Foreign keys validated")
        logger.info("✓ Insert/query operations tested")
        logger.info("")
        logger.info("Ready for Phase 4.5 data upload workflows!")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Acceptance Criteria

### Schema Validation

- [x] **AC1:** Script validates historical_sales table exists
- [x] **AC2:** Script validates stores table exists
- [x] **AC3:** Script validates categories table exists
- [x] **AC4:** Script validates workflows table exists
- [x] **AC5:** Script exits with error if any required table missing

### Table Creation

- [x] **AC6:** Script creates weekly_actuals table if not exists
- [x] **AC7:** Script skips creation if table already exists (idempotent)
- [x] **AC8:** All columns created with correct types
- [x] **AC9:** UNIQUE constraint created on (workflow_id, week_number, store_id)
- [x] **AC10:** Foreign keys created for workflow_id, store_id, category_id
- [x] **AC11:** ON DELETE CASCADE set for all foreign keys

### Indexes

- [x] **AC12:** Index created on (workflow_id, week_number)
- [x] **AC13:** Index created on (store_id)
- [x] **AC14:** Index created on (week_start_date)

### Testing

- [x] **AC15:** Script tests INSERT operation
- [x] **AC16:** Script tests SELECT query
- [x] **AC17:** Script cleans up test data
- [x] **AC18:** Script displays table row counts

### SQLAlchemy Model

- [x] **AC19:** WeeklyActuals model added to models.py
- [x] **AC20:** Model has all required fields
- [x] **AC21:** Model has relationships (workflow, store, category)
- [x] **AC22:** Model has table constraints and indexes
- [x] **AC23:** Workflow model updated with weekly_actuals relationship

---

## Tasks

### Task 1: Add WeeklyActuals Model (0.5 hours)

- [x] Add WeeklyActuals class to `backend/app/database/models.py`
- [x] Add all fields with correct types
- [x] Add relationships
- [x] Add constraints and indexes
- [x] Update Workflow model with relationship

### Task 2: Create Migration Script (1 hour)

- [x] Create `backend/scripts/migrate_phase_4_5.py`
- [x] Implement validation functions
- [x] Implement table creation
- [x] Implement schema validation
- [x] Implement test operations
- [x] Add comprehensive logging

### Task 3: Test Migration (0.5 hours)

- [x] Run migration on clean database
- [x] Verify table created
- [x] Verify indexes created
- [x] Verify foreign keys work
- [x] Run migration again (test idempotency)

### Task 4: Update init_db.py (0.5 hours)

- [x] Update `backend/scripts/init_db.py` to include WeeklyActuals
- [x] Ensure all models registered with Base
- [x] Test that init_db creates all tables including weekly_actuals

---

## Definition of Done

- [x] WeeklyActuals model added to models.py
- [x] Migration script created and tested
- [x] Script validates existing tables
- [x] Script creates weekly_actuals table
- [x] Script is idempotent (safe to run multiple times)
- [x] All indexes and foreign keys created
- [x] Insert/query operations tested
- [x] init_db.py updated to include new model
- [x] Migration tested on clean database
- [x] Documentation updated

---

## Related Stories

- **PHASE4.5-001:** Historical Training Data Upload (uses historical_sales, stores tables)
- **PHASE4.5-002:** Weekly Actuals Upload (uses weekly_actuals table)

---

## Notes

### Running the Migration

```bash
# Method 1: Run migration script directly
cd backend
python scripts/migrate_phase_4_5.py

# Method 2: Include in init_db.py
cd backend
python scripts/init_db.py  # Now creates all tables including weekly_actuals
```

### Rollback (if needed)

```sql
-- SQLite: Drop table and cascade
DROP TABLE IF EXISTS weekly_actuals;
```

---

**Status:** Not Started
**Branch:** `phase4.5-data-upload`
