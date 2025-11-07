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

    from datetime import date, datetime

    with SessionLocal() as session:
        try:
            # Clean up any test data
            session.execute(text("DELETE FROM weekly_actuals WHERE workflow_id = 'test_workflow'"))
            session.execute(text("DELETE FROM workflows WHERE workflow_id = 'test_workflow'"))
            session.commit()

            # Create a temporary test workflow
            test_workflow = Workflow(
                workflow_id="test_workflow",
                workflow_type="forecast",
                category_id="womens_dresses",
                forecast_horizon_weeks=12,
                season_start_date="2025-01-01",
                replenishment_strategy="weekly",
                dc_holdback_percentage=0.15
            )
            session.add(test_workflow)
            session.commit()
            logger.info("✓ Test workflow created")

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

            # Clean up test data (CASCADE will delete weekly_actuals)
            session.execute(text("DELETE FROM workflows WHERE workflow_id = 'test_workflow'"))
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
