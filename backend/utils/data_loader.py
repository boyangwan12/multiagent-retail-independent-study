"""
Data Loader Utility
Loads and analyzes training data to provide context for agent elicitation
"""
import csv
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime


class TrainingDataLoader:
    """Loads and analyzes training data for agent context"""

    def __init__(self, data_dir: str = None):
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
        self._categories = None
        self._stores = None
        self._date_range = None
        self._store_attributes = None

    def get_categories(self) -> List[str]:
        """Get unique product categories from historical sales data"""
        if self._categories is None:
            categories = set()
            with open(self.historical_sales_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    categories.add(row['category'])
            self._categories = sorted(list(categories))
        return self._categories

    def get_stores(self) -> List[str]:
        """Get unique store IDs"""
        if self._stores is None:
            stores = set()
            with open(self.historical_sales_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stores.add(row['store_id'])
            self._stores = sorted(list(stores))
        return self._stores

    def get_date_range(self) -> Dict[str, str]:
        """Get the date range of historical data"""
        if self._date_range is None:
            dates = []
            with open(self.historical_sales_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dates.append(row['date'])

            dates.sort()
            self._date_range = {
                'start': dates[0],
                'end': dates[-1],
                'start_year': dates[0][:4],
                'end_year': dates[-1][:4]
            }
        return self._date_range

    def get_store_count(self) -> int:
        """Get total number of stores"""
        return len(self.get_stores())

    def get_store_attributes_summary(self) -> Dict:
        """Get summary statistics of store attributes"""
        if self._store_attributes is None:
            stores = []
            with open(self.store_attributes_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stores.append(row)

            # Calculate summaries
            mall_stores = sum(1 for s in stores if s['mall_location'] == 'True')

            self._store_attributes = {
                'total_stores': len(stores),
                'mall_stores': mall_stores,
                'standalone_stores': len(stores) - mall_stores,
                'store_ids': [s['store_id'] for s in stores]
            }
        return self._store_attributes

    def get_historical_sales(self, category: str) -> Dict[str, List]:
        """
        Get aggregated historical sales data for a specific category

        Args:
            category: Product category name (e.g., "Women's Dresses")

        Returns:
            Dictionary with 'date' and 'quantity_sold' lists aggregated across all stores
            Format: {'date': ['2022-01-01', ...], 'quantity_sold': [150, ...]}
        """
        from collections import defaultdict

        # Aggregate sales by date across all stores
        date_quantities = defaultdict(int)

        with open(self.historical_sales_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['category'] == category:
                    date = row['date']
                    quantity = int(row['quantity_sold'])
                    date_quantities[date] += quantity

        # Sort by date and convert to lists
        sorted_dates = sorted(date_quantities.keys())

        return {
            'date': sorted_dates,
            'quantity_sold': [date_quantities[date] for date in sorted_dates]
        }

    def get_context_summary(self) -> str:
        """Get a formatted summary of available data for agent context"""
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
_data_loader = None

def get_data_loader() -> TrainingDataLoader:
    """Get or create the global data loader instance"""
    global _data_loader
    if _data_loader is None:
        _data_loader = TrainingDataLoader()
    return _data_loader
