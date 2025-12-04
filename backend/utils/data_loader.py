"""
Data Loader Utility

Loads and analyzes training data to provide context for agent tools.
Ported from backend-agent-as-tool with minimal changes.
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
import pandas as pd
import numpy as np


class TrainingDataLoader:
    """Loads and analyzes training data for agent context."""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the data loader.

        Args:
            data_dir: Path to training data directory. If None, uses default
                     location relative to project root: data/training/
        """
        if data_dir is None:
            # Default to data/training directory relative to project root
            backend_dir = Path(__file__).parent.parent
            project_root = backend_dir.parent
            self.data_dir = project_root / "data" / "training"
        else:
            self.data_dir = Path(data_dir)

        self.historical_sales_path = self.data_dir / "historical_sales_2022_2024.csv"
        self.store_attributes_path = self.data_dir / "store_attributes.csv"

        # Cache loaded data
        self._categories: Optional[List[str]] = None
        self._stores: Optional[List[str]] = None
        self._date_range: Optional[Dict[str, str]] = None
        self._store_attributes: Optional[Dict] = None

    def clear_cache(self):
        """Clear all cached data to force reload from files."""
        self._categories = None
        self._stores = None
        self._date_range = None
        self._store_attributes = None

    def update_data_paths(self, sales_path: Optional[str] = None, stores_path: Optional[str] = None):
        """Update data file paths and clear cache."""
        if sales_path:
            self.historical_sales_path = Path(sales_path)
        if stores_path:
            self.store_attributes_path = Path(stores_path)
        self.clear_cache()

    def get_categories(self) -> List[str]:
        """Get unique product categories from historical sales data."""
        if self._categories is None:
            categories = set()
            with open(self.historical_sales_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    categories.add(row["category"])
            self._categories = sorted(list(categories))
        return self._categories

    def get_stores(self) -> List[str]:
        """Get unique store IDs."""
        if self._stores is None:
            stores = set()
            with open(self.historical_sales_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stores.add(row["store_id"])
            self._stores = sorted(list(stores))
        return self._stores

    def get_date_range(self) -> Dict[str, str]:
        """Get the date range of historical data."""
        if self._date_range is None:
            dates = []
            with open(self.historical_sales_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dates.append(row["date"])

            dates.sort()
            self._date_range = {
                "start": dates[0],
                "end": dates[-1],
                "start_year": dates[0][:4],
                "end_year": dates[-1][:4],
            }
        return self._date_range

    def get_store_count(self) -> int:
        """Get total number of stores."""
        return len(self.get_stores())

    def get_store_attributes_df(self) -> pd.DataFrame:
        """
        Get store attributes as pandas DataFrame for clustering and allocation.

        Returns:
            DataFrame with store_id as index and required features:
            - avg_weekly_sales_12mo: 12-month average weekly sales
            - store_size_sqft: Store square footage
            - median_income: Median income of surrounding area
            - location_tier: Location tier (A/B/C)
            - fashion_tier: Fashion positioning (Premium/Mainstream/Value)
            - store_format: Store format (Mall/Standalone/ShoppingCenter/Outlet)
            - region: Geographic region (Northeast/Southeast/Midwest/West)
        """
        # Check if store_attributes.csv exists
        if not self.store_attributes_path.exists():
            # Generate mock store data for testing
            return self._generate_mock_store_data()

        # Load real store attributes
        df = pd.read_csv(self.store_attributes_path)

        # Set store_id as index
        if "store_id" in df.columns:
            df = df.set_index("store_id")

        return df

    def _generate_mock_store_data(self, n_stores: int = 50) -> pd.DataFrame:
        """
        Generate mock store attributes for testing when real data not available.

        Args:
            n_stores: Number of stores to generate (default: 50)

        Returns:
            DataFrame with mock store attributes
        """
        np.random.seed(42)

        # Generate store IDs
        store_ids = [f"store_{i:03d}" for i in range(1, n_stores + 1)]

        # Generate features with realistic distributions
        data = {
            "avg_weekly_sales_12mo": np.random.normal(600, 250, n_stores).clip(
                200, 1500
            ),
            "store_size_sqft": np.random.normal(35000, 15000, n_stores).clip(
                15000, 80000
            ),
            "median_income": np.random.normal(65000, 20000, n_stores).clip(
                35000, 120000
            ),
            "location_tier": np.random.choice(
                ["A", "B", "C"], n_stores, p=[0.2, 0.5, 0.3]
            ),
            "fashion_tier": np.random.choice(
                ["Premium", "Mainstream", "Value"], n_stores, p=[0.3, 0.5, 0.2]
            ),
            "store_format": np.random.choice(
                ["Mall", "Standalone", "ShoppingCenter", "Outlet"],
                n_stores,
                p=[0.4, 0.3, 0.2, 0.1],
            ),
            "region": np.random.choice(
                ["Northeast", "Southeast", "Midwest", "West"],
                n_stores,
                p=[0.25, 0.25, 0.25, 0.25],
            ),
        }

        df = pd.DataFrame(data, index=store_ids)
        df.index.name = "store_id"

        return df

    def get_store_attributes_summary(self) -> Dict:
        """Get summary statistics of store attributes."""
        if self._store_attributes is None:
            stores = []
            if self.store_attributes_path.exists():
                with open(self.store_attributes_path, "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        stores.append(row)

                # Calculate summaries
                mall_stores = sum(
                    1 for s in stores if s.get("mall_location") == "True"
                )

                self._store_attributes = {
                    "total_stores": len(stores),
                    "mall_stores": mall_stores,
                    "standalone_stores": len(stores) - mall_stores,
                    "store_ids": [s["store_id"] for s in stores],
                }
            else:
                # Use mock data count
                self._store_attributes = {
                    "total_stores": 50,
                    "mall_stores": 20,
                    "standalone_stores": 30,
                    "store_ids": [f"store_{i:03d}" for i in range(1, 51)],
                }
        return self._store_attributes

    def get_historical_sales(self, category: str) -> Dict[str, List]:
        """
        Get aggregated historical sales data for a specific category.

        Args:
            category: Product category name (e.g., "Women's Dresses")

        Returns:
            Dictionary with 'date' and 'quantity_sold' lists aggregated across all stores
            Format: {'date': ['2022-01-01', ...], 'quantity_sold': [150, ...]}
        """
        # Aggregate sales by date across all stores
        date_quantities = defaultdict(int)

        with open(self.historical_sales_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["category"] == category:
                    date = row["date"]
                    quantity = int(row["quantity_sold"])
                    date_quantities[date] += quantity

        # Sort by date and convert to lists
        sorted_dates = sorted(date_quantities.keys())

        return {
            "date": sorted_dates,
            "quantity_sold": [date_quantities[date] for date in sorted_dates],
        }

    def get_context_summary(self) -> str:
        """Get a formatted summary of available data for agent context."""
        categories = self.get_categories()
        date_range = self.get_date_range()
        store_attrs = self.get_store_attributes_summary()

        summary = f"""
## AVAILABLE TRAINING DATA

### Product Categories ({len(categories)} total):
{', '.join(categories)}

### Store Network:
- Total Stores: {store_attrs['total_stores']}
- Mall Locations: {store_attrs['mall_stores']}
- Standalone: {store_attrs['standalone_stores']}

### Historical Data Range:
- From: {date_range['start']}
- To: {date_range['end']}
- Coverage: {date_range['start_year']}-{date_range['end_year']} ({int(date_range['end_year']) - int(date_range['start_year']) + 1} years)

### Available for Forecasting:
All {len(categories)} categories across all {store_attrs['total_stores']} stores.
"""
        return summary.strip()


# Global instance for easy access
_data_loader: Optional[TrainingDataLoader] = None


def get_data_loader() -> TrainingDataLoader:
    """Get or create the global data loader instance."""
    global _data_loader
    if _data_loader is None:
        _data_loader = TrainingDataLoader()
    return _data_loader
