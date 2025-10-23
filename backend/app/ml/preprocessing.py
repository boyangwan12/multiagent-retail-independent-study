"""Data Preprocessing Utilities"""

import pandas as pd
from typing import Tuple


def clean_historical_sales(data: pd.DataFrame) -> pd.DataFrame:
    """Clean historical sales data (handle missing values, duplicates)."""
    if data is None or len(data) == 0:
        return pd.DataFrame(columns=['date', 'units_sold'])

    # Remove duplicates
    data = data.drop_duplicates(subset=['date'], keep='first')

    # Fill missing dates with forward fill
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
        data = data.set_index('date').asfreq('D').reset_index()

    # Fill missing units with 0
    if 'units_sold' in data.columns:
        data['units_sold'] = data['units_sold'].fillna(0)

    return data


def validate_sales_data(data: pd.DataFrame) -> bool:
    """Validate historical sales data."""
    required_columns = ['date', 'units_sold']

    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Missing required columns. Expected: {required_columns}")

    if len(data) < 52:
        raise ValueError("Insufficient historical data. Need at least 52 weeks.")

    if data['units_sold'].isna().any():
        raise ValueError("Missing values in 'units_sold' column.")

    return True


def detect_outliers(data: pd.DataFrame, column: str = 'units_sold', std_dev: float = 3.0) -> pd.DataFrame:
    """Detect outliers using Z-score method."""
    mean = data[column].mean()
    std = data[column].std()

    data['is_outlier'] = (data[column] - mean).abs() > (std_dev * std)
    return data