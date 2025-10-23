import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("fashion_forecast")

class CSVValidationError(Exception):
    """Raised when CSV validation fails"""
    pass

def validate_store_attributes_csv(file_path: str) -> pd.DataFrame:
    """
    Validate and load store attributes CSV.

    Actual columns (from existing CSV):
    - store_id, size_sqft, income_level, foot_traffic, competitor_density,
      online_penetration, population_density, mall_location

    This function adapts the existing CSV format to the database schema by:
    - Renaming size_sqft -> store_size_sqft
    - Renaming income_level -> median_income
    - Deriving location_tier from income_level (A: >$100K, B: $70K-$100K, C: <$70K)
    - Deriving fashion_tier from size_sqft (Premium: >12K, Mainstream: 8K-12K, Value: <8K)
    - Deriving store_format from mall_location (Mall if True, else Standalone)
    - Deriving region from store_id ranges (hardcoded distribution)
    - Computing avg_weekly_sales_12mo from historical sales (will be computed later)

    Args:
        file_path: Path to store_attributes.csv

    Returns:
        Validated and transformed DataFrame

    Raises:
        CSVValidationError: If validation fails
    """
    logger.info(f"Validating store attributes CSV: {file_path}")

    # Check file exists
    if not Path(file_path).exists():
        raise CSVValidationError(f"File not found: {file_path}")

    # Load CSV
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise CSVValidationError(f"Failed to read CSV: {e}")

    # Check required columns (actual CSV format)
    required_columns = [
        "store_id",
        "size_sqft",
        "income_level",
        "foot_traffic",
        "competitor_density",
        "online_penetration",
        "population_density",
        "mall_location",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise CSVValidationError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Check row count (exactly 50 stores)
    if len(df) != 50:
        raise CSVValidationError(
            f"Expected exactly 50 stores, found {len(df)}"
        )

    # Check for missing values
    if df[required_columns].isnull().any().any():
        null_cols = df[required_columns].columns[df[required_columns].isnull().any()].tolist()
        raise CSVValidationError(
            f"Missing values in columns: {', '.join(null_cols)}"
        )

    # Validate data types
    try:
        df["size_sqft"] = df["size_sqft"].astype(int)
        df["income_level"] = df["income_level"].astype(int)
        df["foot_traffic"] = df["foot_traffic"].astype(int)
        df["competitor_density"] = df["competitor_density"].astype(float)
        df["online_penetration"] = df["online_penetration"].astype(float)
        df["population_density"] = df["population_density"].astype(int)
        df["mall_location"] = df["mall_location"].astype(bool)

    except (ValueError, TypeError) as e:
        raise CSVValidationError(f"Data type validation failed: {e}")

    # Derive required fields for database schema
    # Rename columns
    df = df.rename(columns={
        "size_sqft": "store_size_sqft",
        "income_level": "median_income"
    })

    # Derive location_tier from median_income
    df["location_tier"] = df["median_income"].apply(
        lambda x: "A" if x > 100000 else ("B" if x > 70000 else "C")
    )

    # Derive fashion_tier from store_size_sqft
    df["fashion_tier"] = df["store_size_sqft"].apply(
        lambda x: "Premium" if x > 12000 else ("Mainstream" if x > 8000 else "Value")
    )

    # Derive store_format from mall_location
    df["store_format"] = df["mall_location"].apply(
        lambda x: "Mall" if x else "Standalone"
    )

    # Derive region from store_id (distribute evenly across 4 regions)
    def get_region(store_id):
        store_num = int(store_id[1:])  # Extract number from "S001"
        if store_num <= 13:
            return "Northeast"
        elif store_num <= 26:
            return "Southeast"
        elif store_num <= 39:
            return "Midwest"
        else:
            return "West"

    df["region"] = df["store_id"].apply(get_region)

    # Compute avg_weekly_sales_12mo based on store features
    # Formula: size_sqft * income_multiplier * foot_traffic_multiplier
    # This is an estimate that will be refined by actual historical sales data
    df["avg_weekly_sales_12mo"] = (
        df["store_size_sqft"] *
        (df["median_income"] / 100000) *  # Income multiplier (normalized to $100K)
        (df["foot_traffic"] / 2000) *     # Foot traffic multiplier (normalized to 2000)
        50.0  # Base multiplier to get reasonable weekly sales figures
    )

    logger.info(f"✓ Store attributes CSV validated and transformed: 50 stores, 7 features")
    return df


def validate_historical_sales_csv(file_path: str) -> pd.DataFrame:
    """
    Validate and load historical sales CSV.

    Required columns:
    - date (DATE): YYYY-MM-DD, range 2022-01-01 to 2024-12-31
    - category (STRING): Product category
    - store_id (STRING): S001 to S050
    - quantity_sold (INTEGER): Units sold, >= 0
    - revenue (FLOAT): Total revenue, >= 0

    Args:
        file_path: Path to historical_sales_2022_2024.csv

    Returns:
        Validated DataFrame

    Raises:
        CSVValidationError: If validation fails
    """
    logger.info(f"Validating historical sales CSV: {file_path}")

    # Check file exists
    if not Path(file_path).exists():
        raise CSVValidationError(f"File not found: {file_path}")

    # Load CSV
    try:
        df = pd.read_csv(file_path, parse_dates=["date"])
    except Exception as e:
        raise CSVValidationError(f"Failed to read CSV: {e}")

    # Check required columns
    required_columns = ["date", "category", "store_id", "quantity_sold", "revenue"]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise CSVValidationError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Check for missing values
    if df[required_columns].isnull().any().any():
        null_cols = df[required_columns].columns[df[required_columns].isnull().any()].tolist()
        raise CSVValidationError(
            f"Missing values in columns: {', '.join(null_cols)}"
        )

    # Validate data types and ranges
    try:
        # quantity_sold: integer, >= 0
        df["quantity_sold"] = df["quantity_sold"].astype(int)
        if not (df["quantity_sold"] >= 0).all():
            raise CSVValidationError("quantity_sold must be >= 0 (no negative sales)")

        # revenue: float, >= 0
        df["revenue"] = df["revenue"].astype(float)
        if not (df["revenue"] >= 0).all():
            raise CSVValidationError("revenue must be >= 0")

    except (ValueError, TypeError) as e:
        raise CSVValidationError(f"Data type validation failed: {e}")

    # Validate date range (2022-01-01 to 2024-12-31)
    min_date = pd.Timestamp(datetime(2022, 1, 1))
    max_date = pd.Timestamp(datetime(2024, 12, 31))

    if not (df["date"] >= min_date).all() or not (df["date"] <= max_date).all():
        raise CSVValidationError(
            f"Dates must be between {min_date.date()} and {max_date.date()}"
        )

    # Check minimum 2 years of data
    date_range_years = (df["date"].max() - df["date"].min()).days / 365.25
    if date_range_years < 2.0:
        raise CSVValidationError(
            f"Minimum 2 years of data required, found {date_range_years:.1f} years"
        )

    # Check all 50 stores are present
    unique_stores = df["store_id"].nunique()
    if unique_stores != 50:
        raise CSVValidationError(
            f"Expected 50 stores in historical data, found {unique_stores}"
        )

    # Detect categories
    categories = df["category"].unique().tolist()

    logger.info(
        f"✓ Historical sales CSV validated: {len(df):,} rows, "
        f"{len(categories)} categories, {unique_stores} stores"
    )
    logger.info(f"  Categories detected: {', '.join(categories)}")

    return df
