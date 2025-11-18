"""
Tests for CSV parsing and validation utilities.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from app.utils.csv_parser import (
    validate_store_attributes_csv,
    validate_historical_sales_csv,
    CSVValidationError,
)


@pytest.mark.unit
def test_validate_store_attributes_wrong_count():
    """
    Test CSV validation enforces exactly 50 stores.
    """
    # Create temporary CSV file with only 2 stores (should require 50)
    csv_content = """store_id,size_sqft,income_level,foot_traffic,competitor_density,online_penetration,population_density,mall_location
1,15000,125000,8500,3,0.25,5000,True
2,9000,85000,6000,5,0.35,3500,False
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        with pytest.raises(CSVValidationError) as exc_info:
            validate_store_attributes_csv(temp_path)

        # Should fail because it expects exactly 50 stores
        assert "Expected exactly 50 stores" in str(exc_info.value)

    finally:
        os.unlink(temp_path)


@pytest.mark.unit
def test_validate_store_attributes_missing_columns():
    """
    Test CSV validation fails with missing required columns.
    """
    csv_content = """store_id,size_sqft
1,15000
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        with pytest.raises(CSVValidationError) as exc_info:
            validate_store_attributes_csv(temp_path)

        assert "Missing required columns" in str(exc_info.value)
    finally:
        os.unlink(temp_path)


@pytest.mark.unit
def test_validate_store_attributes_file_not_found():
    """
    Test CSV validation fails when file doesn't exist.
    """
    with pytest.raises(CSVValidationError) as exc_info:
        validate_store_attributes_csv("nonexistent_file.csv")

    assert "File not found" in str(exc_info.value) or "does not exist" in str(exc_info.value)


@pytest.mark.unit
def test_validate_historical_sales_insufficient_data():
    """
    Test CSV validation enforces minimum 2 years of data.
    """
    # Create data with only a few days (less than 2 years)
    csv_content = """date,category,store_id,quantity_sold,revenue
2024-01-01,Blouses,1,120,2400
2024-01-08,Blouses,1,115,2300
2024-01-01,Sweaters,2,95,3800
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        with pytest.raises(CSVValidationError) as exc_info:
            validate_historical_sales_csv(temp_path)

        # Should fail because it requires minimum 2 years of data
        assert "Minimum 2 years of data required" in str(exc_info.value)

    finally:
        os.unlink(temp_path)


@pytest.mark.unit
def test_validate_historical_sales_missing_columns():
    """
    Test historical sales CSV validation fails with missing columns.
    """
    csv_content = """date,category,store_id
2024-01-01,Blouses,1
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        with pytest.raises(CSVValidationError) as exc_info:
            validate_historical_sales_csv(temp_path)

        assert "Missing required columns" in str(exc_info.value)
    finally:
        os.unlink(temp_path)


@pytest.mark.unit
def test_validate_historical_sales_invalid_date_format():
    """
    Test historical sales CSV validation fails with invalid date format.
    """
    csv_content = """date,category,store_id,quantity_sold,revenue
invalid-date,Blouses,1,120,2400
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        with pytest.raises((CSVValidationError, ValueError, TypeError)) as exc_info:
            validate_historical_sales_csv(temp_path)

        # Should fail during date parsing or validation
        # Accept multiple exception types as the failure can occur at different stages
    finally:
        os.unlink(temp_path)
