# Story: Implement SQLAlchemy Models & Alembic Migrations for Hybrid Database Schema

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-002
**Status:** Draft
**Estimate:** 4 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-001 (Project Setup)

---

## Story

As a backend developer,
I want to create SQLAlchemy ORM models and Alembic migrations for a hybrid database schema (normalized tables + JSON columns),
So that I can persist forecasts, allocations, and actual sales data with proper referential integrity and efficient querying.

**Business Value:** Establishes the data persistence layer for the entire multi-agent system. The hybrid schema design balances normalization (for queryability) with flexibility (JSON columns for variable-length arrays), enabling efficient storage and retrieval of forecasting data without over-normalizing.

**Epic Context:** This is Task 2 of 14 in Phase 3. It builds directly on PHASE3-001 (project setup) and enables all subsequent tasks that require data persistence. The database schema supports the parameter-driven architecture with 10 tables covering categories, stores, forecasts, allocations, markdowns, and actual sales.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ SQLAlchemy and Alembic installed as dependencies
2. ✅ Database connection module created (`backend/app/database/db.py`)
3. ✅ All 10 SQLAlchemy models implemented:
   - `models/category.py` (categories table)
   - `models/store.py` (stores table)
   - `models/store_cluster.py` (store_clusters table)
   - `models/parameters.py` (season_parameters table) ⭐ NEW
   - `models/forecast.py` (forecasts table with JSON columns)
   - `models/allocation.py` (allocations table with JSON columns)
   - `models/markdown.py` (markdowns table)
   - `models/historical_sales.py` (historical_sales table)
   - `models/actual_sales.py` (actual_sales table)
   - `models/workflow_log.py` (workflow_logs table)
4. ✅ Alembic initialized (`alembic init migrations`)
5. ✅ Initial migration generated (`alembic revision --autogenerate`)
6. ✅ Migration successfully applied (`alembic upgrade head`)
7. ✅ All 10 tables created in SQLite database
8. ✅ Foreign key constraints enforced
9. ✅ Indexes created for performance-critical queries

### Quality Requirements

10. ✅ All models use type hints (Python 3.11+)
11. ✅ JSON columns properly serialized/deserialized
12. ✅ CHECK constraints validate data integrity
13. ✅ All enum fields use SQLAlchemy Enum types
14. ✅ Models follow consistent naming conventions

---

## Tasks

### Task 1: Install SQLAlchemy and Alembic
- [ ] Verify SQLAlchemy is in `pyproject.toml` dependencies: `sqlalchemy>=2.0.35`
- [ ] Verify Alembic is in dependencies: `alembic>=1.13.0`
- [ ] Run `uv pip install -e ".[dev]"` to ensure latest dependencies installed
- [ ] Verify installation: `python -c "import sqlalchemy, alembic; print(sqlalchemy.__version__, alembic.__version__)"`

**Expected Output:** SQLAlchemy 2.0.35+ and Alembic 1.13.0+ installed

**Reference:** PHASE3-001, pyproject.toml dependencies

### Task 2: Create Database Connection Module
- [ ] Create `backend/app/database/` directory
- [ ] Create `backend/app/database/__init__.py`
- [ ] Create `backend/app/database/db.py` with SQLAlchemy engine and session management
- [ ] Implement `get_db()` function for dependency injection
- [ ] Configure SQLite database URL from environment variable
- [ ] Add connection pooling configuration

**Database Connection Template:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fashion_forecast.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=True  # Set to False in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2440-2446

### Task 3: Create SQLAlchemy Model - categories
- [ ] Create `backend/app/models/` directory
- [ ] Create `backend/app/models/__init__.py`
- [ ] Create `backend/app/models/category.py`
- [ ] Implement `Category` model with all fields
- [ ] Add CHECK constraint for archetype enum
- [ ] Add `created_at` timestamp with default

**Category Model:**
```python
from sqlalchemy import Column, String, Date, Integer, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from backend.app.database.db import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String, primary_key=True)
    category_name = Column(String, nullable=False)
    season_start_date = Column(Date, nullable=False)
    season_end_date = Column(Date, nullable=False)
    season_length_weeks = Column(Integer, nullable=False)
    archetype = Column(
        String,
        nullable=False,
        default="FASHION_RETAIL"
    )
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "archetype IN ('FASHION_RETAIL', 'STABLE_CATALOG', 'CONTINUOUS')",
            name="check_archetype"
        ),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2212-2222

### Task 4: Create SQLAlchemy Model - store_clusters
- [ ] Create `backend/app/models/store_cluster.py`
- [ ] Implement `StoreCluster` model
- [ ] Add CHECK constraint for fashion_tier enum
- [ ] Establish relationship with stores (one-to-many)

**StoreCluster Model:**
```python
from sqlalchemy import Column, String, Text, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.db import Base

class StoreCluster(Base):
    __tablename__ = "store_clusters"

    cluster_id = Column(String, primary_key=True)
    cluster_name = Column(String, nullable=False)
    fashion_tier = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    stores = relationship("Store", back_populates="cluster")

    __table_args__ = (
        CheckConstraint(
            "fashion_tier IN ('PREMIUM', 'MAINSTREAM', 'VALUE')",
            name="check_fashion_tier"
        ),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2224-2233

### Task 5: Create SQLAlchemy Model - stores
- [ ] Create `backend/app/models/store.py`
- [ ] Implement `Store` model with all 7 features
- [ ] Add foreign key to store_clusters
- [ ] Add CHECK constraints for enums (location_tier, store_format, region)
- [ ] Add relationship to store_clusters

**Store Model:**
```python
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.db import Base

class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String, primary_key=True)
    store_name = Column(String, nullable=False)
    cluster_id = Column(String, ForeignKey("store_clusters.cluster_id"), nullable=False)
    store_size_sqft = Column(Integer, nullable=False)
    location_tier = Column(String, nullable=False)
    median_income = Column(Integer, nullable=False)
    store_format = Column(String, nullable=False)
    region = Column(String, nullable=False)
    avg_weekly_sales_12mo = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    cluster = relationship("StoreCluster", back_populates="stores")

    __table_args__ = (
        CheckConstraint("location_tier IN ('A', 'B', 'C')", name="check_location_tier"),
        CheckConstraint(
            "store_format IN ('MALL', 'STANDALONE', 'SHOPPING_CENTER', 'OUTLET')",
            name="check_store_format"
        ),
        CheckConstraint(
            "region IN ('NORTHEAST', 'SOUTHEAST', 'MIDWEST', 'WEST')",
            name="check_region"
        ),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2235-2249

### Task 6: Create SQLAlchemy Model - forecasts (with JSON columns)
- [ ] Create `backend/app/models/forecast.py`
- [ ] Implement `Forecast` model with JSON columns for variable-length arrays
- [ ] Add foreign key to categories
- [ ] Configure JSON serialization for `weekly_demand_curve` and `models_used`
- [ ] Add CHECK constraint for total_season_demand

**Forecast Model:**
```python
from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.db import Base

class Forecast(Base):
    __tablename__ = "forecasts"

    forecast_id = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    season = Column(String, nullable=False)
    forecast_horizon_weeks = Column(Integer, nullable=False)
    total_season_demand = Column(Integer, nullable=False)

    # JSON columns for variable-length arrays
    weekly_demand_curve = Column(JSON, nullable=False)  # [{"week_number": 1, "demand_units": 500}, ...]

    peak_week = Column(Integer, nullable=False)
    forecasting_method = Column(String, nullable=False, default="ensemble_prophet_arima")
    models_used = Column(JSON, nullable=False)  # ["prophet", "arima"]
    prophet_forecast = Column(Integer, nullable=True)
    arima_forecast = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    category = relationship("Category")

    __table_args__ = (
        CheckConstraint("total_season_demand >= 0", name="check_total_demand"),
    )
```

**Note:** SQLite JSON column type automatically serializes Python dict/list to JSON string

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2251-2267

### Task 7: Create SQLAlchemy Model - forecast_cluster_distribution
- [ ] Create `backend/app/models/forecast_cluster_distribution.py`
- [ ] Implement `ForecastClusterDistribution` model
- [ ] Add foreign keys to forecasts and store_clusters
- [ ] Add CHECK constraint for allocation_percentage (0-1 range)

**ForecastClusterDistribution Model:**
```python
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from backend.app.database.db import Base

class ForecastClusterDistribution(Base):
    __tablename__ = "forecast_cluster_distribution"

    distribution_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    cluster_id = Column(String, ForeignKey("store_clusters.cluster_id"), nullable=False)
    allocation_percentage = Column(Float, nullable=False)
    total_units = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "allocation_percentage >= 0 AND allocation_percentage <= 1",
            name="check_allocation_pct"
        ),
        CheckConstraint("total_units >= 0", name="check_total_units"),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2269-2279

### Task 8: Create SQLAlchemy Model - allocations (with JSON columns)
- [ ] Create `backend/app/models/allocation.py`
- [ ] Implement `Allocation` model with JSON column for store_allocations array
- [ ] Add foreign key to forecasts
- [ ] Add CHECK constraints for quantities

**Allocation Model:**
```python
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from backend.app.database.db import Base

class Allocation(Base):
    __tablename__ = "allocations"

    allocation_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    manufacturing_qty = Column(Integer, nullable=False)
    safety_stock_percentage = Column(Float, nullable=False, default=0.20)
    initial_allocation_total = Column(Integer, nullable=False)
    holdback_total = Column(Integer, nullable=False)

    # JSON column for variable-length store allocations
    store_allocations = Column(JSON, nullable=False)  # [{"store_id": "S01", "initial": 176, "holdback": 142}, ...]

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("manufacturing_qty >= 0", name="check_manufacturing_qty"),
        CheckConstraint("initial_allocation_total >= 0", name="check_initial_allocation"),
        CheckConstraint("holdback_total >= 0", name="check_holdback"),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2281-2293

### Task 9: Create SQLAlchemy Model - markdowns
- [ ] Create `backend/app/models/markdown.py`
- [ ] Implement `Markdown` model
- [ ] Add foreign key to forecasts
- [ ] Add CHECK constraints for percentages and week_number
- [ ] Add status enum constraint

**Markdown Model:**
```python
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from backend.app.database.db import Base

class Markdown(Base):
    __tablename__ = "markdowns"

    markdown_id = Column(String, primary_key=True)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    sell_through_pct = Column(Float, nullable=False)
    target_sell_through_pct = Column(Float, nullable=False, default=0.60)
    gap_pct = Column(Float, nullable=False)
    recommended_markdown_pct = Column(Float, nullable=False)
    elasticity_coefficient = Column(Float, nullable=False, default=2.0)
    expected_demand_lift_pct = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="pending")
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="check_week_number"),
        CheckConstraint("sell_through_pct >= 0 AND sell_through_pct <= 1", name="check_sell_through"),
        CheckConstraint(
            "recommended_markdown_pct >= 0 AND recommended_markdown_pct <= 0.40",
            name="check_markdown_pct"
        ),
        CheckConstraint("status IN ('pending', 'approved', 'applied')", name="check_status"),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2295-2311

### Task 10: Create SQLAlchemy Models - historical_sales & actual_sales
- [ ] Create `backend/app/models/historical_sales.py`
- [ ] Create `backend/app/models/actual_sales.py`
- [ ] Implement both models with foreign keys
- [ ] Add indexes for performance-critical queries
- [ ] Add CHECK constraints for units_sold

**HistoricalSales Model:**
```python
from sqlalchemy import Column, String, Date, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from backend.app.database.db import Base

class HistoricalSales(Base):
    __tablename__ = "historical_sales"

    sale_id = Column(String, primary_key=True)
    store_id = Column(String, ForeignKey("stores.store_id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    units_sold = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("units_sold >= 0", name="check_units_sold"),
        Index("idx_historical_sales_store_category", "store_id", "category_id"),
        Index("idx_historical_sales_date", "week_start_date"),
    )
```

**ActualSales Model:**
```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from backend.app.database.db import Base

class ActualSales(Base):
    __tablename__ = "actual_sales"

    actual_id = Column(String, primary_key=True)
    store_id = Column(String, ForeignKey("stores.store_id"), nullable=False)
    forecast_id = Column(String, ForeignKey("forecasts.forecast_id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    units_sold = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("week_number >= 1 AND week_number <= 12", name="check_week_number"),
        CheckConstraint("units_sold >= 0", name="check_units_sold"),
        Index("idx_actual_sales_forecast_week", "forecast_id", "week_number"),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2313-2340

### Task 11: Create SQLAlchemy Model - workflow_logs
- [ ] Create `backend/app/models/workflow_log.py`
- [ ] Implement `WorkflowLog` model with JSON columns for input/output data
- [ ] Add CHECK constraint for status enum
- [ ] Add index on workflow_id for query performance

**WorkflowLog Model:**
```python
from sqlalchemy import Column, String, JSON, Float, Text, DateTime, CheckConstraint, Index
from sqlalchemy.sql import func
from backend.app.database.db import Base

class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    log_id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('started', 'completed', 'failed')", name="check_status"),
        Index("idx_workflow_logs_workflow", "workflow_id"),
    )
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2342-2358

### Task 12: Create Model Index File
- [ ] Update `backend/app/models/__init__.py` to export all models
- [ ] Import all models in a single place for Alembic discovery

**models/__init__.py:**
```python
from backend.app.models.category import Category
from backend.app.models.store_cluster import StoreCluster
from backend.app.models.store import Store
from backend.app.models.forecast import Forecast
from backend.app.models.forecast_cluster_distribution import ForecastClusterDistribution
from backend.app.models.allocation import Allocation
from backend.app.models.markdown import Markdown
from backend.app.models.historical_sales import HistoricalSales
from backend.app.models.actual_sales import ActualSales
from backend.app.models.workflow_log import WorkflowLog

__all__ = [
    "Category",
    "StoreCluster",
    "Store",
    "Forecast",
    "ForecastClusterDistribution",
    "Allocation",
    "Markdown",
    "HistoricalSales",
    "ActualSales",
    "WorkflowLog",
]
```

### Task 13: Initialize Alembic for Migrations
- [ ] Navigate to `backend/` directory
- [ ] Run `alembic init migrations` to initialize Alembic
- [ ] Update `alembic.ini` with SQLite database URL
- [ ] Update `migrations/env.py` to import models
- [ ] Configure `target_metadata` to use Base.metadata

**Update migrations/env.py:**
```python
from backend.app.database.db import Base
from backend.app.models import *  # Import all models

target_metadata = Base.metadata
```

**Reference:** Implementation plan Task 2, lines 148-150

### Task 14: Generate and Apply Initial Migration
- [ ] Run `alembic revision --autogenerate -m "Initial schema with 10 tables"`
- [ ] Review generated migration file in `migrations/versions/`
- [ ] Verify all 10 tables are included in migration
- [ ] Verify foreign keys are created
- [ ] Verify CHECK constraints are included
- [ ] Run `alembic upgrade head` to apply migration
- [ ] Verify SQLite database file created: `fashion_forecast.db`

**Expected Output:** Migration creates all 10 tables with foreign keys and constraints

### Task 15: Verify Database Schema
- [ ] Use SQLite CLI or DB Browser to inspect database
- [ ] Run: `sqlite3 fashion_forecast.db ".schema"` to see all tables
- [ ] Verify all 10 tables exist:
  - categories
  - store_clusters
  - stores
  - forecasts
  - forecast_cluster_distribution
  - allocations
  - markdowns
  - historical_sales
  - actual_sales
  - workflow_logs
- [ ] Verify foreign keys with: `PRAGMA foreign_keys;`
- [ ] Verify indexes with: `SELECT * FROM sqlite_master WHERE type='index';`

**Verification Commands:**
```bash
cd backend
sqlite3 fashion_forecast.db ".tables"  # List all tables
sqlite3 fashion_forecast.db ".schema categories"  # Show category table schema
sqlite3 fashion_forecast.db "PRAGMA foreign_key_list(stores);"  # Show foreign keys
```

---

## Dev Notes

### Hybrid Schema Design Philosophy

**Why Hybrid (Normalized + JSON)?**

**Normalized Tables (Master Data):**
- **categories, stores, store_clusters**: Highly queryable, referenced by foreign keys
- **Benefits**: Referential integrity, efficient joins, clear relationships
- **Use case**: "Show me all stores in the Fashion_Forward cluster"

**JSON Columns (Variable-Length Arrays):**
- **weekly_demand_curve, store_allocations, models_used**: Flexible, no fixed schema
- **Benefits**: No separate tables for arrays, simpler queries, less joins
- **Use case**: "Get all 12 weeks of demand in a single query"

**Alternative Considered (Fully Normalized):**
- Create `weekly_demand` table (12 rows per forecast × 50 stores = 600 rows)
- **Rejected**: Too many joins, over-normalized for MVP, added complexity

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2201-2207

### SQLAlchemy 2.0 Modern Syntax

**Key Features Used:**
- **Declarative Base**: `Base = declarative_base()`
- **Type Hints**: Python 3.11+ style (`str | None` instead of `Optional[str]`)
- **func.now()**: SQLAlchemy 2.0 server-side default timestamp
- **JSON Column Type**: Native JSON support (SQLite 3.38+)
- **relationship()**: ORM relationships without back_populates circular imports

**Migration from SQLAlchemy 1.x:**
- Use `String` instead of `VARCHAR` (more portable)
- Use `JSON` instead of `Text` + manual serialization
- Use `DateTime` with `server_default=func.now()` instead of `default=datetime.now`

### JSON Column Serialization

**Automatic Serialization (SQLite + SQLAlchemy):**
```python
# Python dict → JSON string (automatic)
weekly_demand_curve = [{"week_number": 1, "demand_units": 500}, ...]
forecast.weekly_demand_curve = weekly_demand_curve  # Automatically serialized

# JSON string → Python dict (automatic)
loaded_forecast = session.query(Forecast).first()
demand_curve = loaded_forecast.weekly_demand_curve  # Automatically deserialized
print(demand_curve[0]["demand_units"])  # 500
```

**No Manual Serialization Needed:**
- SQLAlchemy handles `json.dumps()` and `json.loads()` automatically
- Query JSON fields with SQLite JSON functions: `json_extract(weekly_demand_curve, '$.week_number')`

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2259, 2290

### Foreign Key Relationships

**One-to-Many Relationships:**
- `store_clusters` (1) → `stores` (many)
- `categories` (1) → `forecasts` (many)
- `forecasts` (1) → `allocations` (many)

**Foreign Key Enforcement (SQLite):**
```python
# Enable foreign keys in SQLite connection
engine = create_engine(
    "sqlite:///./fashion_forecast.db",
    connect_args={"check_same_thread": False},
    echo=True
)

# Foreign keys are enforced by CHECK constraint at table level
# Example: Cannot insert store with non-existent cluster_id
```

**Cascade Deletes (Not Used in MVP):**
- MVP does not implement cascade deletes
- Manual deletion required if parent record removed
- Post-MVP: Consider `ondelete="CASCADE"` for cleanup

### CHECK Constraints

**Data Integrity Rules:**
| Table | Constraint | Purpose |
|-------|------------|---------|
| categories | `archetype IN (...)` | Validate retail archetype |
| stores | `location_tier IN ('A', 'B', 'C')` | Validate location tier |
| stores | `store_format IN (...)` | Validate store format |
| stores | `region IN (...)` | Validate region |
| forecasts | `total_season_demand >= 0` | No negative demand |
| allocations | `manufacturing_qty >= 0` | No negative quantities |
| markdowns | `week_number >= 1 AND <= 12` | Valid week range |
| markdowns | `recommended_markdown_pct <= 0.40` | Cap markdown at 40% |

**SQLite CHECK Constraint Behavior:**
- Enforced at INSERT and UPDATE time
- Violation raises `IntegrityError`
- Named constraints help with debugging

### Indexes for Performance

**Performance-Critical Queries:**
1. **historical_sales**:
   - `idx_historical_sales_store_category`: Fast lookup by store + category
   - `idx_historical_sales_date`: Fast time-series queries
2. **actual_sales**:
   - `idx_actual_sales_forecast_week`: Fast variance calculation
3. **workflow_logs**:
   - `idx_workflow_logs_workflow`: Fast workflow tracking

**Index Creation (Automatic via Alembic):**
```python
Index("idx_name", "column1", "column2")  # Composite index
```

**When to Add Indexes (Post-MVP):**
- If queries on `forecasts.category_id` are slow
- If queries on `allocations.forecast_id` are slow
- Monitor query performance with SQLite `EXPLAIN QUERY PLAN`

### Alembic Migration Workflow

**Development Workflow:**
1. Modify SQLAlchemy models
2. Run `alembic revision --autogenerate -m "Description"`
3. Review generated migration in `migrations/versions/`
4. Edit migration if needed (Alembic doesn't catch everything)
5. Run `alembic upgrade head` to apply
6. Run `alembic downgrade -1` to rollback if needed

**Important Alembic Notes:**
- **Autogenerate limitations**: May miss CHECK constraints, need manual review
- **Downgrade migrations**: Write explicit downgrade logic
- **Production migrations**: Test on copy of production DB first
- **Schema changes**: Alembic detects table/column changes, not data migrations

### Common Issues & Solutions

**Issue 1: JSON column shows as string in queries**
- Solution: SQLite 3.38+ required for JSON support
- Check version: `python -c "import sqlite3; print(sqlite3.sqlite_version)"`
- Upgrade SQLite if needed

**Issue 2: Foreign key constraint violation**
- Solution: Ensure parent record exists before inserting child
- Example: Create `store_clusters` before `stores`

**Issue 3: Alembic autogenerate misses constraints**
- Solution: Manually add CHECK constraints to migration file
- Review migration before applying

**Issue 4: Migration fails with "table already exists"**
- Solution: Drop database and rerun: `rm fashion_forecast.db && alembic upgrade head`
- Or: Run `alembic downgrade base` first

**Issue 5: Relationship errors in queries**
- Solution: Ensure both sides of relationship are defined
- Use `back_populates` for bidirectional relationships

### Critical References

- **Database Schema:** `planning/3_technical_architecture_v3.3.md` lines 2199-2404
- **Data Models (Pydantic):** `planning/3_technical_architecture_v3.3.md` lines 280-550
- **Implementation Plan:** Task 2, lines 130-155
- **SQLAlchemy 2.0 Docs:** https://docs.sqlalchemy.org/en/20/
- **Alembic Tutorial:** https://alembic.sqlalchemy.org/en/latest/tutorial.html
- **SQLite JSON Functions:** https://www.sqlite.org/json1.html

---

## Testing

### Manual Testing Checklist

- [ ] All SQLAlchemy models import without errors
- [ ] Database connection established successfully
- [ ] Alembic initialized without errors
- [ ] Initial migration generated successfully
- [ ] Migration includes all 10 tables
- [ ] Foreign keys present in migration
- [ ] CHECK constraints present in migration
- [ ] Migration applies without errors (`alembic upgrade head`)
- [ ] SQLite database file created (`fashion_forecast.db`)
- [ ] All 10 tables exist in database
- [ ] Foreign keys enforced (test with invalid insert)
- [ ] CHECK constraints enforced (test with invalid data)
- [ ] Indexes created successfully

### Verification Commands

```bash
# Navigate to backend directory
cd backend

# Verify SQLAlchemy/Alembic installed
python -c "import sqlalchemy, alembic; print(sqlalchemy.__version__, alembic.__version__)"

# Initialize Alembic
alembic init migrations

# Generate migration
alembic revision --autogenerate -m "Initial schema with 10 tables"

# Apply migration
alembic upgrade head

# Verify tables created
sqlite3 fashion_forecast.db ".tables"

# Show schema for a table
sqlite3 fashion_forecast.db ".schema stores"

# Show foreign keys
sqlite3 fashion_forecast.db "PRAGMA foreign_key_list(stores);"

# Show indexes
sqlite3 fashion_forecast.db "SELECT name FROM sqlite_master WHERE type='index';"

# Test foreign key constraint (should fail)
sqlite3 fashion_forecast.db "INSERT INTO stores VALUES ('S99', 'Test Store', 'invalid_cluster', 5000, 'A', 50000, 'MALL', 'WEST', 1000.0, datetime('now'));"
```

### Unit Tests (Optional for this story, will be added in Task 13)

```python
# tests/test_models/test_category.py
def test_category_creation():
    category = Category(
        category_id="cat_001",
        category_name="Women's Dresses",
        season_start_date="2025-03-01",
        season_end_date="2025-05-23",
        season_length_weeks=12,
        archetype="FASHION_RETAIL"
    )
    assert category.category_name == "Women's Dresses"

# tests/test_models/test_json_serialization.py
def test_forecast_json_columns():
    weekly_curve = [{"week_number": 1, "demand_units": 500}]
    forecast = Forecast(
        forecast_id="f_001",
        category_id="cat_001",
        season="Spring 2025",
        forecast_horizon_weeks=12,
        total_season_demand=8000,
        weekly_demand_curve=weekly_curve,
        peak_week=3,
        forecasting_method="ensemble",
        models_used=["prophet", "arima"]
    )
    # JSON serialization happens automatically
    assert forecast.weekly_demand_curve[0]["demand_units"] == 500
```

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial story creation | Product Owner |
| 2025-10-19 | 1.1 | Fixed task numbering (Task 12→14), moved Change Log to top-level section, added QA Results section for template compliance | Product Owner |

---

## Dev Agent Record

### Agent Model Used

_TBD_

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

### File List

_Dev Agent will populate this section during implementation_

**Files to Create:**
- `backend/app/database/__init__.py`
- `backend/app/database/db.py`
- `backend/app/models/__init__.py`
- `backend/app/models/category.py`
- `backend/app/models/store_cluster.py`
- `backend/app/models/store.py`
- `backend/app/models/forecast.py`
- `backend/app/models/forecast_cluster_distribution.py`
- `backend/app/models/allocation.py`
- `backend/app/models/markdown.py`
- `backend/app/models/historical_sales.py`
- `backend/app/models/actual_sales.py`
- `backend/app/models/workflow_log.py`
- `backend/alembic.ini`
- `backend/migrations/env.py`
- `backend/migrations/versions/XXXXX_initial_schema.py` (generated)

**Files to Modify:**
- None (all new files)

**Files to Verify:**
- `backend/fashion_forecast.db` (created by migration)

---

## Definition of Done

- [ ] SQLAlchemy and Alembic installed and verified
- [ ] Database connection module created (`db.py`)
- [ ] All 10 SQLAlchemy models implemented
- [ ] All models use proper type hints
- [ ] JSON columns configured for serialization
- [ ] CHECK constraints added for data integrity
- [ ] Foreign key relationships defined
- [ ] Indexes created for performance-critical queries
- [ ] Alembic initialized successfully
- [ ] Initial migration generated with all 10 tables
- [ ] Migration includes foreign keys and constraints
- [ ] Migration applied successfully (`alembic upgrade head`)
- [ ] SQLite database file created
- [ ] All 10 tables exist in database
- [ ] Foreign key enforcement verified
- [ ] CHECK constraints verified
- [ ] All verification commands pass

---

## QA Results

_This section will be populated by QA Agent after story implementation and testing_

**QA Status:** Pending
**QA Agent:** TBD
**QA Date:** TBD

### Test Execution Results
- TBD

### Issues Found
- TBD

### Sign-Off
- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No critical issues found
- [ ] Story approved for deployment

---

**Created:** 2025-10-19
**Last Updated:** 2025-10-19 (Template compliance fixes: task numbering, Change Log, QA Results)
**Story Points:** 4
**Priority:** P0 (Blocker for all data-dependent tasks)
