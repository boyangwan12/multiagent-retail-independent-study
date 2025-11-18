"""
Upload Service - Handles CSV file uploads and validation
"""

import csv
import io
import os
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.schemas.workflow_schemas import UploadResponse, ValidationError
import logging

logger = logging.getLogger("fashion_forecast")


# ============================================================================
# CSV Schema Definitions (Required Columns and Data Types)
# ============================================================================

CSV_SCHEMAS = {
    # Demand Agent Files
    "sales_data": {
        "required_columns": ["store_id", "week", "sales_units", "sales_revenue", "inventory_on_hand"],
        "data_types": {
            "store_id": "string",
            "week": "integer",
            "sales_units": "integer",
            "sales_revenue": "float",
            "inventory_on_hand": "integer"
        }
    },
    "store_profiles": {
        "required_columns": ["store_id", "store_name", "region", "size_sqft", "cluster_id"],
        "data_types": {
            "store_id": "string",
            "store_name": "string",
            "region": "string",
            "size_sqft": "integer",
            "cluster_id": "string"
        }
    },
    # Inventory Agent Files
    "dc_inventory": {
        "required_columns": ["sku", "dc_location", "available_units", "reserved_units"],
        "data_types": {
            "sku": "string",
            "dc_location": "string",
            "available_units": "integer",
            "reserved_units": "integer"
        }
    },
    "lead_times": {
        "required_columns": ["store_id", "dc_location", "lead_time_days"],
        "data_types": {
            "store_id": "string",
            "dc_location": "string",
            "lead_time_days": "integer"
        }
    },
    "safety_stock": {
        "required_columns": ["store_id", "safety_stock_units", "reorder_point"],
        "data_types": {
            "store_id": "string",
            "safety_stock_units": "integer",
            "reorder_point": "integer"
        }
    },
    # Pricing Agent Files
    "markdown_history": {
        "required_columns": ["week", "markdown_pct", "sell_through_pct", "demand_lift_pct"],
        "data_types": {
            "week": "integer",
            "markdown_pct": "float",
            "sell_through_pct": "float",
            "demand_lift_pct": "float"
        }
    },
    "elasticity": {
        "required_columns": ["category", "elasticity_coefficient"],
        "data_types": {
            "category": "string",
            "elasticity_coefficient": "float"
        }
    },
    "competitor_prices": {
        "required_columns": ["competitor", "price", "markdown_pct"],
        "data_types": {
            "competitor": "string",
            "price": "float",
            "markdown_pct": "float"
        }
    }
}


class UploadService:
    """Service for handling CSV file uploads and validation."""

    def __init__(self, db: Session):
        self.db = db
        self.upload_directory = "data/uploads"
        self._ensure_upload_directory()

    def _ensure_upload_directory(self):
        """Create upload directory if it doesn't exist."""
        os.makedirs(self.upload_directory, exist_ok=True)

    async def process_upload(
        self,
        workflow_id: str,
        agent_type: str,
        file: UploadFile,
        file_type: str,
        file_content: bytes
    ) -> UploadResponse:
        """
        Process CSV file upload with validation.

        Args:
            workflow_id: Workflow identifier
            agent_type: Agent type (demand, inventory, pricing)
            file: Uploaded file
            file_type: Type of file (e.g., sales_data, store_profiles)
            file_content: File content as bytes

        Returns:
            UploadResponse with validation results
        """
        logger.info(f"Processing upload for workflow {workflow_id}, file_type: {file_type}")

        # Decode file content
        try:
            text_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            return UploadResponse(
                workflow_id=workflow_id,
                file_type=file_type,
                file_name=file.filename,
                file_size_bytes=len(file_content),
                rows_uploaded=0,
                columns=[],
                validation_status="INVALID",
                errors=[ValidationError(
                    error_type="OTHER",
                    message="File encoding is invalid. Please ensure the file is UTF-8 encoded."
                )],
                uploaded_at=datetime.utcnow().isoformat() + "Z",
                message="Upload failed: Invalid file encoding"
            )

        # Parse CSV
        try:
            csv_reader = csv.DictReader(io.StringIO(text_content))
            rows = list(csv_reader)
            columns = csv_reader.fieldnames or []
        except Exception as e:
            return UploadResponse(
                workflow_id=workflow_id,
                file_type=file_type,
                file_name=file.filename,
                file_size_bytes=len(file_content),
                rows_uploaded=0,
                columns=[],
                validation_status="INVALID",
                errors=[ValidationError(
                    error_type="OTHER",
                    message=f"Failed to parse CSV file: {str(e)}"
                )],
                uploaded_at=datetime.utcnow().isoformat() + "Z",
                message="Upload failed: Invalid CSV format"
            )

        # Check if file is empty
        if len(rows) == 0:
            return UploadResponse(
                workflow_id=workflow_id,
                file_type=file_type,
                file_name=file.filename,
                file_size_bytes=len(file_content),
                rows_uploaded=0,
                columns=columns,
                validation_status="INVALID",
                errors=[ValidationError(
                    error_type="EMPTY_FILE",
                    message="CSV file is empty or contains only headers"
                )],
                uploaded_at=datetime.utcnow().isoformat() + "Z",
                message="Upload failed: Empty file"
            )

        # Validate CSV schema
        errors = self._validate_csv(file_type, columns, rows)

        if errors:
            return UploadResponse(
                workflow_id=workflow_id,
                file_type=file_type,
                file_name=file.filename,
                file_size_bytes=len(file_content),
                rows_uploaded=len(rows),
                columns=columns,
                validation_status="INVALID",
                errors=errors,
                uploaded_at=datetime.utcnow().isoformat() + "Z",
                message=f"Validation failed: {len(errors)} errors found"
            )

        # Save file to disk
        file_path = self._save_file(workflow_id, agent_type, file_type, file.filename, file_content)
        logger.info(f"File saved to: {file_path}")

        # Return success response
        return UploadResponse(
            workflow_id=workflow_id,
            file_type=file_type,
            file_name=file.filename,
            file_size_bytes=len(file_content),
            rows_uploaded=len(rows),
            columns=columns,
            validation_status="VALID",
            uploaded_at=datetime.utcnow().isoformat() + "Z",
            message="File uploaded successfully"
        )

    def _validate_csv(
        self,
        file_type: str,
        columns: list[str],
        rows: list[dict]
    ) -> list[ValidationError]:
        """
        Validate CSV against schema.

        Args:
            file_type: Type of file (e.g., sales_data)
            columns: Column names from CSV
            rows: Parsed CSV rows

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check if schema exists for this file type
        if file_type not in CSV_SCHEMAS:
            errors.append(ValidationError(
                error_type="OTHER",
                message=f"Unknown file type: {file_type}"
            ))
            return errors

        schema = CSV_SCHEMAS[file_type]

        # Check for missing required columns
        missing_columns = set(schema["required_columns"]) - set(columns)
        for col in missing_columns:
            errors.append(ValidationError(
                error_type="MISSING_COLUMN",
                column=col,
                message=f"Required column '{col}' is missing from CSV file"
            ))

        # If columns are missing, skip row validation
        if missing_columns:
            return errors

        # Validate data types for each row (limit to first 100 rows for performance)
        for row_idx, row in enumerate(rows[:100], start=1):
            for col_name, expected_type in schema["data_types"].items():
                if col_name not in row:
                    continue

                value = row[col_name].strip()

                # Skip empty values
                if not value:
                    continue

                # Validate based on expected type
                if expected_type == "integer":
                    try:
                        int(value)
                    except ValueError:
                        errors.append(ValidationError(
                            error_type="DATA_TYPE_MISMATCH",
                            row=row_idx,
                            column=col_name,
                            expected_type="integer",
                            actual_value=value,
                            message=f"Row {row_idx}, column '{col_name}': expected integer, got '{value}'"
                        ))
                elif expected_type == "float":
                    try:
                        float(value)
                    except ValueError:
                        errors.append(ValidationError(
                            error_type="DATA_TYPE_MISMATCH",
                            row=row_idx,
                            column=col_name,
                            expected_type="float",
                            actual_value=value,
                            message=f"Row {row_idx}, column '{col_name}': expected float, got '{value}'"
                        ))
                elif expected_type == "string":
                    # Strings are always valid
                    pass

        return errors

    def _save_file(
        self,
        workflow_id: str,
        agent_type: str,
        file_type: str,
        filename: str,
        content: bytes
    ) -> str:
        """
        Save uploaded file to disk.

        Args:
            workflow_id: Workflow identifier
            agent_type: Agent type (demand, inventory, pricing)
            file_type: Type of file
            filename: Original filename
            content: File content

        Returns:
            Path to saved file
        """
        # Create workflow-specific directory
        workflow_dir = os.path.join(self.upload_directory, workflow_id, agent_type)
        os.makedirs(workflow_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{file_type}_{timestamp}.csv"
        file_path = os.path.join(workflow_dir, safe_filename)

        # Write file
        with open(file_path, 'wb') as f:
            f.write(content)

        return file_path
