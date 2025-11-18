#!/usr/bin/env python
"""
Seed database with Phase 1 CSV files for development/testing.

Usage:
    python backend/scripts/seed_db.py [--data-dir PATH]

Requirements:
    - store_attributes.csv (50 stores, 7 features)
    - historical_sales_2022_2024.csv (~54,750 rows)
"""

import argparse
import logging
import sys
from pathlib import Path
import time
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.database.db import Base, engine, SessionLocal
from app.database.models import Store, Category, HistoricalSales, StoreCluster
from app.utils.csv_parser import (
    validate_store_attributes_csv,
    validate_historical_sales_csv,
    CSVValidationError,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("seed_db")


def create_initial_clusters(session: Session):
    """
    Create 3 default store clusters based on fashion tiers.
    These will be replaced by ML clustering in later phases.

    Args:
        session: Database session
    """
    logger.info("Creating initial store clusters...")

    # Clear existing clusters
    deleted_count = session.query(StoreCluster).delete()
    if deleted_count > 0:
        logger.info(f"  Cleared {deleted_count} existing clusters")

    clusters = [
        StoreCluster(
            cluster_id="premium",
            cluster_name="Premium Tier Cluster",
            fashion_tier="PREMIUM",
            description="High-end stores with larger sizes (>12K sqft) and premium demographics",
        ),
        StoreCluster(
            cluster_id="mainstream",
            cluster_name="Mainstream Tier Cluster",
            fashion_tier="MAINSTREAM",
            description="Mid-range stores with moderate sizes (8K-12K sqft) and mainstream positioning",
        ),
        StoreCluster(
            cluster_id="value",
            cluster_name="Value Tier Cluster",
            fashion_tier="VALUE",
            description="Compact stores with smaller sizes (<8K sqft) and value-oriented positioning",
        ),
    ]

    session.bulk_save_objects(clusters)
    session.commit()
    logger.info(f"✓ Created {len(clusters)} initial clusters")


def seed_stores(session: Session, csv_path: str) -> int:
    """
    Load stores from CSV and insert into database.

    Args:
        session: Database session
        csv_path: Path to store_attributes.csv

    Returns:
        Number of stores inserted
    """
    logger.info("=" * 60)
    logger.info("SEEDING STORES")
    logger.info("=" * 60)

    # Validate and load CSV
    df = validate_store_attributes_csv(csv_path)

    # Clear existing stores (for idempotency)
    deleted_count = session.query(Store).delete()
    if deleted_count > 0:
        logger.info(f"  Cleared {deleted_count} existing stores")

    # Insert stores
    stores = []
    for _, row in df.iterrows():
        # Map fashion_tier to cluster_id (temporary until ML clustering)
        fashion_tier = row["fashion_tier"].lower()
        cluster_id = fashion_tier  # "premium", "mainstream", or "value"

        # Generate store name from store_id
        store_name = f"Store {row['store_id']}"

        # Normalize store_format to uppercase with underscores
        store_format = row["store_format"].upper().replace(" ", "_")
        if store_format == "SHOPPINGCENTER":
            store_format = "SHOPPING_CENTER"

        # Normalize region to uppercase
        region = row["region"].upper().replace(" ", "_")

        store = Store(
            store_id=row["store_id"],
            store_name=store_name,
            cluster_id=cluster_id,
            store_size_sqft=int(row["store_size_sqft"]),
            location_tier=row["location_tier"],
            median_income=int(row["median_income"]),
            store_format=store_format,
            region=region,
            avg_weekly_sales_12mo=float(row["avg_weekly_sales_12mo"]),
        )
        stores.append(store)

    session.bulk_save_objects(stores)
    session.commit()

    logger.info(f"✓ Inserted {len(stores)} stores")

    # Log cluster distribution
    for cluster_id in ["premium", "mainstream", "value"]:
        count = session.query(Store).filter(Store.cluster_id == cluster_id).count()
        logger.info(f"  {cluster_id.capitalize()}: {count} stores")

    return len(stores)


def seed_categories_and_sales(session: Session, csv_path: str) -> tuple[int, int]:
    """
    Load historical sales from CSV, auto-detect categories, and insert into database.

    Args:
        session: Database session
        csv_path: Path to historical_sales_2022_2024.csv

    Returns:
        Tuple of (categories_created, sales_rows_inserted)
    """
    logger.info("=" * 60)
    logger.info("SEEDING CATEGORIES & HISTORICAL SALES")
    logger.info("=" * 60)

    # Validate and load CSV
    df = validate_historical_sales_csv(csv_path)

    # Auto-detect categories
    category_names = df["category"].unique().tolist()
    logger.info(f"  Detected {len(category_names)} categories: {', '.join(category_names)}")

    # Clear existing categories and sales (for idempotency)
    deleted_sales = session.query(HistoricalSales).delete()
    deleted_categories = session.query(Category).delete()
    if deleted_categories > 0 or deleted_sales > 0:
        logger.info(f"  Cleared {deleted_categories} categories, {deleted_sales} sales rows")

    # Insert categories
    from datetime import date
    categories = []
    for category_name in category_names:
        category = Category(
            category_id=category_name.lower().replace(" ", "_").replace("'", ""),
            category_name=category_name,
            season_start_date=date(2025, 1, 1),  # Default season start
            season_end_date=date(2025, 3, 31),   # Default 12-week season
            season_length_weeks=12,
            archetype="FASHION_RETAIL",
            description=f"Auto-detected category from historical sales: {category_name}",
        )
        categories.append(category)

    session.bulk_save_objects(categories)
    session.commit()
    logger.info(f"✓ Inserted {len(categories)} categories")

    # Insert historical sales (batch inserts for performance)
    logger.info(f"  Inserting {len(df):,} sales rows...")
    start_time = time.time()

    sales_records = []
    for idx, row in df.iterrows():
        # Generate unique sale_id
        category_clean = row['category'].lower().replace(' ', '_').replace("'", '')
        date_str = row['date'].strftime('%Y%m%d')
        sale_id = f"{row['store_id']}_{category_clean}_{date_str}"

        sale = HistoricalSales(
            sale_id=sale_id,
            week_start_date=row["date"],  # Use date as week_start_date
            category_id=category_clean,
            store_id=row["store_id"],
            units_sold=int(row["quantity_sold"]),  # Map quantity_sold to units_sold
        )
        sales_records.append(sale)

    # Batch insert in chunks of 1000 for performance
    batch_size = 1000
    for i in range(0, len(sales_records), batch_size):
        batch = sales_records[i : i + batch_size]
        session.bulk_save_objects(batch)
        session.commit()

        # Log progress every 10,000 rows
        if (i + batch_size) % 10000 == 0 or (i + batch_size) >= len(sales_records):
            logger.info(f"    Progress: {min(i + batch_size, len(sales_records)):,} / {len(sales_records):,} rows")

    duration = time.time() - start_time
    logger.info(f"✓ Inserted {len(sales_records):,} sales rows in {duration:.1f}s")

    return len(categories), len(sales_records)


def main():
    """Main seed script entry point"""
    parser = argparse.ArgumentParser(description="Seed database with Phase 1 CSV files")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/mock/training",
        help="Directory containing CSV files (default: data/mock/training)",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)

    # Check CSV files exist
    store_csv = data_dir / "store_attributes.csv"
    sales_csv = data_dir / "historical_sales_2022_2024.csv"

    if not store_csv.exists():
        logger.error(f"❌ Store attributes CSV not found: {store_csv}")
        sys.exit(1)

    if not sales_csv.exists():
        logger.error(f"❌ Historical sales CSV not found: {sales_csv}")
        sys.exit(1)

    logger.info("🌱 STARTING DATABASE SEED")
    logger.info(f"  Data directory: {data_dir.absolute()}")
    logger.info(f"  Database: {settings.DATABASE_URL}")

    try:
        # Create tables
        Base.metadata.create_all(engine)
        logger.info("✓ Database tables created")

        # Seed data
        with SessionLocal() as session:
            create_initial_clusters(session)
            stores_count = seed_stores(session, str(store_csv))
            categories_count, sales_count = seed_categories_and_sales(session, str(sales_csv))

        logger.info("=" * 60)
        logger.info("🎉 SEED COMPLETE")
        logger.info("=" * 60)
        logger.info(f"  Stores: {stores_count}")
        logger.info(f"  Categories: {categories_count}")
        logger.info(f"  Historical Sales: {sales_count:,} rows")
        logger.info("")
        logger.info("✓ Database is ready for development/testing")

    except CSVValidationError as e:
        logger.error(f"❌ CSV Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Seed failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
