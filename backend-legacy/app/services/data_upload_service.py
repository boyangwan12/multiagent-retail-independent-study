"""
Data Upload Service for Historical Training Data.

Handles CSV uploads for historical sales and store attributes.
"""
from sqlalchemy.orm import Session
from app.database.models import HistoricalSales, Store, StoreCluster, Category
from app.utils.csv_validator import validate_historical_sales_csv, validate_store_attributes_csv
import pandas as pd
from typing import Dict, List
from datetime import date
import logging

logger = logging.getLogger("fashion_forecast")


class DataUploadService:
    """Service for handling historical data uploads."""

    def __init__(self, db: Session):
        self.db = db

    def upload_historical_sales(self, csv_file) -> Dict:
        """
        Upload and validate historical sales CSV.

        Args:
            csv_file: Uploaded CSV file (multipart/form-data)

        Returns:
            Dict with upload summary and validation results

        Raises:
            ValidationError: If CSV validation fails
        """
        logger.info("Starting historical sales upload")

        # Step 1: Validate CSV format
        df = validate_historical_sales_csv(csv_file)

        # Step 2: Auto-detect categories
        categories_detected = df['category'].unique().tolist()
        logger.info(f"Categories detected: {categories_detected}")

        # Step 3: Clear existing historical sales data
        deleted_count = self.db.query(HistoricalSales).delete()
        logger.info(f"Cleared {deleted_count} existing historical sales rows")
        self.db.commit()

        # Step 4: Insert categories (if new)
        self._insert_categories(categories_detected)

        # Step 5: Batch insert historical sales (1000 rows at a time)
        rows_inserted = self._batch_insert_sales(df)

        # Step 6: Calculate summary statistics
        summary = self._calculate_sales_summary(df)

        logger.info(f"Historical sales upload complete: {rows_inserted} rows inserted")

        return {
            "status": "success",
            "file_name": csv_file.filename,
            "rows_inserted": rows_inserted,
            "categories_detected": categories_detected,
            "date_range": {
                "start": df['date'].min().strftime('%Y-%m-%d'),
                "end": df['date'].max().strftime('%Y-%m-%d')
            },
            "validation_summary": summary,
            "uploaded_at": pd.Timestamp.now().isoformat()
        }

    def upload_store_attributes(self, csv_file) -> Dict:
        """
        Upload and validate store attributes CSV.

        Args:
            csv_file: Uploaded CSV file (multipart/form-data)

        Returns:
            Dict with upload summary and validation results

        Raises:
            ValidationError: If CSV validation fails
        """
        logger.info("Starting store attributes upload")

        # Step 1: Validate CSV format
        df = validate_store_attributes_csv(csv_file)

        # Step 2: Clear existing stores data
        deleted_count = self.db.query(Store).delete()
        logger.info(f"Cleared {deleted_count} existing stores")
        self.db.commit()

        # Step 3: Ensure store clusters exist
        self._ensure_store_clusters()

        # Step 4: Batch insert stores
        rows_inserted = self._batch_insert_stores(df)

        # Step 5: Calculate summary statistics
        summary = self._calculate_store_summary(df)

        logger.info(f"Store attributes upload complete: {rows_inserted} stores inserted")

        return {
            "status": "success",
            "file_name": csv_file.filename,
            "rows_inserted": rows_inserted,
            "features_validated": 7,
            "clustering_ready": True,
            "store_summary": summary,
            "uploaded_at": pd.Timestamp.now().isoformat()
        }

    def _insert_categories(self, category_names: List[str]):
        """Insert categories if they don't exist."""
        existing_categories = {c.category_id for c in self.db.query(Category).all()}

        for category_name in category_names:
            category_id = category_name.lower().replace(" ", "_").replace("'", "")

            if category_id not in existing_categories:
                category = Category(
                    category_id=category_id,
                    category_name=category_name,
                    season_start_date=date(2025, 1, 1),
                    season_end_date=date(2025, 3, 31),
                    season_length_weeks=12,
                    archetype="FASHION_RETAIL",
                    description=f"Auto-detected from historical sales: {category_name}"
                )
                self.db.add(category)
                logger.info(f"Created new category: {category_id}")

        self.db.commit()

    def _batch_insert_sales(self, df: pd.DataFrame) -> int:
        """Insert historical sales in batches of 1000."""
        batch_size = 1000
        rows_inserted = 0

        sales_records = []
        for _, row in df.iterrows():
            category_clean = row['category'].lower().replace(' ', '_').replace("'", '')
            date_str = row['date'].strftime('%Y%m%d')
            sale_id = f"{row['store_id']}_{category_clean}_{date_str}"

            sale = HistoricalSales(
                sale_id=sale_id,
                week_start_date=row["date"],
                category_id=category_clean,
                store_id=row["store_id"],
                units_sold=int(row["quantity_sold"])
            )
            sales_records.append(sale)

            if len(sales_records) >= batch_size:
                self.db.bulk_save_objects(sales_records)
                self.db.commit()
                rows_inserted += len(sales_records)
                logger.info(f"Inserted batch: {rows_inserted} rows total")
                sales_records = []

        # Insert remaining records
        if sales_records:
            self.db.bulk_save_objects(sales_records)
            self.db.commit()
            rows_inserted += len(sales_records)

        return rows_inserted

    def _ensure_store_clusters(self):
        """Ensure all store clusters exist."""
        clusters_needed = ["premium", "mainstream", "value"]
        existing_clusters = {c.cluster_id for c in self.db.query(StoreCluster).all()}

        for cluster_id in clusters_needed:
            if cluster_id not in existing_clusters:
                cluster_name = cluster_id.capitalize()
                fashion_tier = cluster_id.upper() if cluster_id == "value" else cluster_name.upper() if cluster_id == "premium" else "MAINSTREAM"

                cluster = StoreCluster(
                    cluster_id=cluster_id,
                    cluster_name=f"{cluster_name} Stores",
                    fashion_tier=fashion_tier,
                    description=f"{cluster_name} tier stores based on size and sales volume"
                )
                self.db.add(cluster)
                logger.info(f"Created store cluster: {cluster_id}")

        self.db.commit()

    def _batch_insert_stores(self, df: pd.DataFrame) -> int:
        """Insert stores in batch."""
        stores = []
        for _, row in df.iterrows():
            # Normalize values
            fashion_tier_raw = row.get("fashion_tier", "Mainstream")
            fashion_tier = fashion_tier_raw.lower() if isinstance(fashion_tier_raw, str) else "mainstream"
            cluster_id = fashion_tier

            # Handle optional store_name
            store_name = row.get("store_name", f"Store {row['store_id']}")

            # Normalize store_format and region to UPPERCASE with underscores
            store_format_raw = row.get("store_format", "Standalone")
            store_format = store_format_raw.upper().replace(" ", "_") if isinstance(store_format_raw, str) else "STANDALONE"

            region_raw = row.get("region", "Northeast")
            region = region_raw.upper().replace(" ", "_") if isinstance(region_raw, str) else "NORTHEAST"

            # Get location_tier
            location_tier = row.get("location_tier", "B")

            # Get avg_weekly_sales_12mo
            avg_weekly_sales = float(row.get("avg_weekly_sales_12mo", 10000.0))

            store = Store(
                store_id=row["store_id"],
                store_name=store_name,
                cluster_id=cluster_id,
                store_size_sqft=int(row["store_size_sqft"]),
                location_tier=location_tier,
                median_income=int(row["median_income"]),
                store_format=store_format,
                region=region,
                avg_weekly_sales_12mo=avg_weekly_sales
            )
            stores.append(store)

        self.db.bulk_save_objects(stores)
        self.db.commit()

        return len(stores)

    def _calculate_sales_summary(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics for sales data."""
        return {
            "stores_count": int(df['store_id'].nunique()),
            "total_revenue": float(df['revenue'].sum()) if 'revenue' in df.columns else None,
            "avg_daily_sales_per_store": float(df.groupby('store_id')['quantity_sold'].mean().mean())
        }

    def _calculate_store_summary(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics for store data."""
        # Count fashion tiers (normalize to lowercase for consistency)
        df_copy = df.copy()
        df_copy['fashion_tier_lower'] = df_copy['fashion_tier'].str.lower() if 'fashion_tier' in df_copy.columns else 'mainstream'

        premium_count = len(df_copy[df_copy['fashion_tier_lower'] == 'premium'])
        mainstream_count = len(df_copy[df_copy['fashion_tier_lower'] == 'mainstream'])
        value_count = len(df_copy[df_copy['fashion_tier_lower'] == 'value'])

        return {
            "total_stores": len(df),
            "premium_tier": premium_count,
            "mainstream_tier": mainstream_count,
            "value_tier": value_count,
            "avg_store_size_sqft": int(df['store_size_sqft'].mean()),
            "avg_weekly_sales": float(df['avg_weekly_sales_12mo'].mean()) if 'avg_weekly_sales_12mo' in df.columns else None
        }
