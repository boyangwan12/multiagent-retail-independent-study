"""
CSV Validator for File Uploads.

Adapts existing csv_parser validators to work with FastAPI UploadFile objects.
"""
import pandas as pd
import io
import logging
from typing import Dict, List
from fastapi import UploadFile

logger = logging.getLogger("fashion_forecast")


class ValidationError(Exception):
    """Raised when CSV validation fails with detailed error information."""

    def __init__(self, message: str, errors: List[Dict] = None):
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)


def validate_historical_sales_csv(file: UploadFile) -> pd.DataFrame:
    """
    Validate and load historical sales CSV from uploaded file.

    Required columns:
    - date (DATE): YYYY-MM-DD, range 2022-01-01 to 2024-12-31
    - category (STRING): Product category
    - store_id (STRING): S001 to S050
    - quantity_sold (INTEGER): Units sold, >= 0
    - revenue (FLOAT): Total revenue, >= 0

    Args:
        file: Uploaded CSV file (FastAPI UploadFile)

    Returns:
        Validated DataFrame

    Raises:
        ValidationError: If validation fails
    """
    logger.info(f"Validating historical sales CSV: {file.filename}")

    # Read uploaded file into memory
    try:
        contents = file.file.read()
        df = pd.read_csv(io.BytesIO(contents), parse_dates=["date"])
    except Exception as e:
        raise ValidationError(
            "Failed to read CSV file",
            errors=[{
                "error": "FILE_READ_ERROR",
                "message": f"Could not parse CSV: {str(e)}"
            }]
        )
    finally:
        file.file.seek(0)  # Reset file pointer for potential re-reading

    # Validate required columns
    required_columns = ["date", "category", "store_id", "quantity_sold", "revenue"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValidationError(
            f"Missing required columns: {', '.join(missing_columns)}",
            errors=[{
                "error": "MISSING_COLUMN",
                "column": col,
                "message": f"Required column '{col}' is missing"
            } for col in missing_columns]
        )

    # Check for missing values
    validation_errors = []
    for col in required_columns:
        null_rows = df[df[col].isnull()].index.tolist()
        if null_rows:
            for row_idx in null_rows[:5]:  # Limit to first 5 errors per column
                validation_errors.append({
                    "row": int(row_idx) + 2,  # +2 for header and 0-indexing
                    "column": col,
                    "error": "MISSING_VALUE",
                    "message": f"Missing value in column '{col}'"
                })

    if validation_errors:
        raise ValidationError(
            f"Found {len(validation_errors)} missing values",
            errors=validation_errors
        )

    # Validate data types and ranges
    validation_errors = []

    # quantity_sold: integer, >= 0
    try:
        df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors='coerce')
        invalid_qty = df[df["quantity_sold"].isnull() | (df["quantity_sold"] < 0)]

        for idx, row in invalid_qty.head(10).iterrows():
            validation_errors.append({
                "row": int(idx) + 2,
                "column": "quantity_sold",
                "error": "DATA_TYPE_MISMATCH",
                "expected": "integer >= 0",
                "actual": str(row["quantity_sold"]),
                "message": "quantity_sold must be a non-negative integer"
            })

        df["quantity_sold"] = df["quantity_sold"].fillna(0).astype(int)

    except Exception as e:
        validation_errors.append({
            "column": "quantity_sold",
            "error": "DATA_TYPE_ERROR",
            "message": f"Failed to parse quantity_sold: {str(e)}"
        })

    # revenue: float, >= 0
    try:
        df["revenue"] = pd.to_numeric(df["revenue"], errors='coerce')
        invalid_revenue = df[df["revenue"].isnull() | (df["revenue"] < 0)]

        for idx, row in invalid_revenue.head(10).iterrows():
            validation_errors.append({
                "row": int(idx) + 2,
                "column": "revenue",
                "error": "DATA_TYPE_MISMATCH",
                "expected": "float >= 0",
                "actual": str(row["revenue"]),
                "message": "revenue must be a non-negative number"
            })

        df["revenue"] = df["revenue"].fillna(0.0)

    except Exception as e:
        validation_errors.append({
            "column": "revenue",
            "error": "DATA_TYPE_ERROR",
            "message": f"Failed to parse revenue: {str(e)}"
        })

    if validation_errors:
        raise ValidationError(
            f"CSV validation failed: {len(validation_errors)} errors found",
            errors=validation_errors
        )

    # Validate date range (2022-01-01 to 2024-12-31)
    from datetime import datetime
    min_date = pd.Timestamp(datetime(2022, 1, 1))
    max_date = pd.Timestamp(datetime(2024, 12, 31))

    out_of_range = df[(df["date"] < min_date) | (df["date"] > max_date)]
    if not out_of_range.empty:
        for idx, row in out_of_range.head(10).iterrows():
            validation_errors.append({
                "row": int(idx) + 2,
                "column": "date",
                "error": "DATE_OUT_OF_RANGE",
                "actual": str(row["date"].date()) if pd.notnull(row["date"]) else "invalid",
                "message": f"Date must be between {min_date.date()} and {max_date.date()}"
            })

    if validation_errors:
        raise ValidationError(
            f"Found {len(validation_errors)} date range errors",
            errors=validation_errors
        )

    # Check minimum 2 years of data
    date_range_years = (df["date"].max() - df["date"].min()).days / 365.25
    if date_range_years < 2.0:
        raise ValidationError(
            f"Minimum 2 years of data required, found {date_range_years:.1f} years",
            errors=[{
                "error": "INSUFFICIENT_DATA",
                "message": "Historical sales data must span at least 2 years"
            }]
        )

    # Check all 50 stores are present
    unique_stores = df["store_id"].nunique()
    if unique_stores != 50:
        raise ValidationError(
            f"Expected 50 stores in historical data, found {unique_stores}",
            errors=[{
                "error": "INVALID_STORE_COUNT",
                "expected": 50,
                "actual": unique_stores,
                "message": "Historical sales must include all 50 stores"
            }]
        )

    # Detect categories
    categories = df["category"].unique().tolist()

    logger.info(
        f"✓ Historical sales CSV validated: {len(df):,} rows, "
        f"{len(categories)} categories, {unique_stores} stores"
    )
    logger.info(f"  Categories detected: {', '.join(categories)}")

    return df


def validate_store_attributes_csv(file: UploadFile) -> pd.DataFrame:
    """
    Validate and load store attributes CSV from uploaded file.

    Expected columns (will be auto-derived):
    - store_id, size_sqft, income_level, foot_traffic, competitor_density,
      online_penetration, population_density, mall_location

    OR user-friendly format:
    - store_id, store_name, avg_weekly_sales_12mo, store_size_sqft, median_income,
      location_tier, fashion_tier, store_format, region

    This function adapts the existing CSV format to the database schema.

    Args:
        file: Uploaded CSV file (FastAPI UploadFile)

    Returns:
        Validated and transformed DataFrame

    Raises:
        ValidationError: If validation fails
    """
    logger.info(f"Validating store attributes CSV: {file.filename}")

    # Read uploaded file into memory
    try:
        contents = file.file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise ValidationError(
            "Failed to read CSV file",
            errors=[{
                "error": "FILE_READ_ERROR",
                "message": f"Could not parse CSV: {str(e)}"
            }]
        )
    finally:
        file.file.seek(0)  # Reset file pointer

    # Check which format the CSV is in
    has_simple_format = all(col in df.columns for col in [
        "store_id", "size_sqft", "income_level"
    ])

    has_full_format = all(col in df.columns for col in [
        "store_id", "store_size_sqft", "median_income", "location_tier",
        "fashion_tier", "store_format", "region"
    ])

    if has_full_format:
        # User provided full format - validate it directly
        required_columns = [
            "store_id", "store_name", "avg_weekly_sales_12mo", "store_size_sqft",
            "median_income", "location_tier", "fashion_tier", "store_format", "region"
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValidationError(
                f"Missing required columns: {', '.join(missing_columns)}",
                errors=[{
                    "error": "MISSING_COLUMN",
                    "column": col,
                    "message": f"Required column '{col}' is missing"
                } for col in missing_columns]
            )

    elif has_simple_format:
        # Legacy format - derive required fields
        from app.utils.csv_parser import validate_store_attributes_csv as legacy_validator

        # Save to temp file and use legacy validator
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            df = legacy_validator(tmp_path)
        except Exception as e:
            raise ValidationError(
                f"Validation failed: {str(e)}",
                errors=[{"error": "VALIDATION_ERROR", "message": str(e)}]
            )
        finally:
            import os
            os.unlink(tmp_path)

    else:
        raise ValidationError(
            "Unrecognized CSV format",
            errors=[{
                "error": "INVALID_FORMAT",
                "message": "CSV must contain either simplified format (size_sqft, income_level) or full format (store_size_sqft, median_income, location_tier, etc.)"
            }]
        )

    # Check row count (exactly 50 stores)
    if len(df) != 50:
        raise ValidationError(
            f"Expected exactly 50 stores, found {len(df)}",
            errors=[{
                "error": "INVALID_STORE_COUNT",
                "expected": 50,
                "actual": len(df),
                "message": "Store attributes must include exactly 50 stores"
            }]
        )

    # Validate enum values
    validation_errors = []

    valid_location_tiers = ["A", "B", "C"]
    invalid_location = df[~df["location_tier"].isin(valid_location_tiers)]
    for idx, row in invalid_location.head(10).iterrows():
        validation_errors.append({
            "row": int(idx) + 2,
            "column": "location_tier",
            "error": "INVALID_ENUM_VALUE",
            "actual": str(row["location_tier"]),
            "expected": ", ".join(valid_location_tiers),
            "message": f"location_tier must be one of: {', '.join(valid_location_tiers)}"
        })

    valid_fashion_tiers = ["Premium", "Mainstream", "Value"]
    invalid_fashion = df[~df["fashion_tier"].isin(valid_fashion_tiers)]
    for idx, row in invalid_fashion.head(10).iterrows():
        validation_errors.append({
            "row": int(idx) + 2,
            "column": "fashion_tier",
            "error": "INVALID_ENUM_VALUE",
            "actual": str(row["fashion_tier"]),
            "expected": ", ".join(valid_fashion_tiers),
            "message": f"fashion_tier must be one of: {', '.join(valid_fashion_tiers)}"
        })

    if validation_errors:
        raise ValidationError(
            f"CSV validation failed: {len(validation_errors)} errors found",
            errors=validation_errors
        )

    logger.info(f"✓ Store attributes CSV validated and transformed: 50 stores, 7+ features")
    return df
