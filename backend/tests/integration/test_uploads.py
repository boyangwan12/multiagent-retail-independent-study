"""
Integration tests for CSV upload endpoints
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO


def test_csv_upload_success(client: TestClient, mock_season_parameters):
    """Test CSV upload with valid file"""
    # Create workflow first
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Create valid CSV
    csv_content = b"store_id,week,sales_units,sales_revenue,inventory_on_hand\n"
    csv_content += b"S001,1,150,3750,500\n"
    csv_content += b"S001,2,180,4500,470\n"

    files = {
        "file": ("sales_data.csv", BytesIO(csv_content), "text/csv")
    }
    data = {"file_type": "sales_data"}

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/demand/upload",
        files=files,
        data=data
    )

    assert response.status_code == 200
    result = response.json()
    assert result["validation_status"] == "VALID"
    assert result["rows_uploaded"] == 2


def test_csv_upload_missing_column(client: TestClient, mock_season_parameters):
    """Test CSV upload with missing required column"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # CSV missing "sales_units" column
    csv_content = b"store_id,week,sales_revenue,inventory_on_hand\n"
    csv_content += b"S001,1,3750,500\n"

    files = {
        "file": ("sales_data.csv", BytesIO(csv_content), "text/csv")
    }
    data = {"file_type": "sales_data"}

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/demand/upload",
        files=files,
        data=data
    )

    assert response.status_code == 200  # Service returns 200 with validation errors
    result = response.json()
    assert result["validation_status"] == "INVALID"
    assert len(result["errors"]) > 0
    assert result["errors"][0]["error_type"] == "MISSING_COLUMN"


def test_csv_upload_wrong_data_type(client: TestClient, mock_season_parameters):
    """Test CSV upload with wrong data type"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # CSV with non-numeric value in sales_units
    csv_content = b"store_id,week,sales_units,sales_revenue,inventory_on_hand\n"
    csv_content += b"S001,1,N/A,3750,500\n"

    files = {
        "file": ("sales_data.csv", BytesIO(csv_content), "text/csv")
    }
    data = {"file_type": "sales_data"}

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/demand/upload",
        files=files,
        data=data
    )

    assert response.status_code == 200
    result = response.json()
    assert result["validation_status"] == "INVALID"
    assert len(result["errors"]) > 0
    assert result["errors"][0]["error_type"] == "DATA_TYPE_MISMATCH"


def test_csv_upload_invalid_extension(client: TestClient, mock_season_parameters):
    """Test CSV upload with wrong file extension"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Upload .xlsx file
    files = {
        "file": ("sales_data.xlsx", BytesIO(b"fake xlsx content"), "application/vnd.ms-excel")
    }
    data = {"file_type": "sales_data"}

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/demand/upload",
        files=files,
        data=data
    )

    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "csv" in result["detail"].lower()


def test_csv_upload_empty_file(client: TestClient, mock_season_parameters):
    """Test CSV upload with empty file"""
    # Create workflow
    request_data = {
        "category_id": "womens_dresses",
        "parameters": mock_season_parameters
    }
    create_response = client.post("/api/v1/workflows/forecast", json=request_data)
    workflow_id = create_response.json()["workflow_id"]

    # Empty CSV (only headers)
    csv_content = b"store_id,week,sales_units,sales_revenue,inventory_on_hand\n"

    files = {
        "file": ("sales_data.csv", BytesIO(csv_content), "text/csv")
    }
    data = {"file_type": "sales_data"}

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/demand/upload",
        files=files,
        data=data
    )

    assert response.status_code == 200
    result = response.json()
    assert result["validation_status"] == "INVALID"
    assert any(error["error_type"] == "EMPTY_FILE" for error in result["errors"])
