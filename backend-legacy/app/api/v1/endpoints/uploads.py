from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.db import get_db
from app.schemas.workflow_schemas import UploadResponse, MultipleUploadResponse, ValidationError
from app.services.upload_service import UploadService
import logging

logger = logging.getLogger("fashion_forecast")

router = APIRouter()


def get_upload_service(db: Session = Depends(get_db)) -> UploadService:
    """Dependency injection for UploadService."""
    return UploadService(db)


@router.post("/{workflow_id}/demand/upload", response_model=UploadResponse)
async def upload_demand_data(
    workflow_id: str,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    service: UploadService = Depends(get_upload_service)
):
    """
    Upload CSV file for Demand Agent.

    **Supported file types:**
    - sales_data: Historical sales data
    - store_profiles: Store profiles

    **Example Request:**
    - Method: POST
    - Content-Type: multipart/form-data
    - Body:
      - file: sales_data.csv
      - file_type: "sales_data"

    **Example Response:**
    ```json
    {
      "workflow_id": "wf_abc123",
      "file_type": "sales_data",
      "file_name": "sales_data.csv",
      "file_size_bytes": 2048,
      "rows_uploaded": 50,
      "columns": ["store_id", "week", "sales_units", "sales_revenue", "inventory_on_hand"],
      "validation_status": "VALID",
      "uploaded_at": "2025-01-15T10:30:00Z",
      "message": "File uploaded successfully"
    }
    ```
    """
    try:
        logger.info(f"Uploading demand agent file: {file.filename} for workflow {workflow_id}")

        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .csv files are accepted."
            )

        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum allowed size of 10MB"
            )

        # Reset file pointer
        await file.seek(0)

        # Process upload
        response = await service.process_upload(
            workflow_id=workflow_id,
            agent_type="demand",
            file=file,
            file_type=file_type,
            file_content=file_content
        )

        logger.info(f"Demand file uploaded: {response.file_name} ({response.rows_uploaded} rows)")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload demand file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.post("/{workflow_id}/inventory/upload", response_model=UploadResponse)
async def upload_inventory_data(
    workflow_id: str,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    service: UploadService = Depends(get_upload_service)
):
    """
    Upload CSV file for Inventory Agent.

    **Supported file types:**
    - dc_inventory: DC inventory levels
    - lead_times: Lead times by store
    - safety_stock: Safety stock policies
    """
    try:
        logger.info(f"Uploading inventory agent file: {file.filename} for workflow {workflow_id}")

        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .csv files are accepted."
            )

        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum allowed size of 10MB"
            )

        # Reset file pointer
        await file.seek(0)

        # Process upload
        response = await service.process_upload(
            workflow_id=workflow_id,
            agent_type="inventory",
            file=file,
            file_type=file_type,
            file_content=file_content
        )

        logger.info(f"Inventory file uploaded: {response.file_name} ({response.rows_uploaded} rows)")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload inventory file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.post("/{workflow_id}/pricing/upload", response_model=UploadResponse)
async def upload_pricing_data(
    workflow_id: str,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    service: UploadService = Depends(get_upload_service)
):
    """
    Upload CSV file for Pricing Agent.

    **Supported file types:**
    - markdown_history: Historical markdown data
    - elasticity: Price elasticity coefficients
    - competitor_prices: Competitive pricing data
    """
    try:
        logger.info(f"Uploading pricing agent file: {file.filename} for workflow {workflow_id}")

        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .csv files are accepted."
            )

        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum allowed size of 10MB"
            )

        # Reset file pointer
        await file.seek(0)

        # Process upload
        response = await service.process_upload(
            workflow_id=workflow_id,
            agent_type="pricing",
            file=file,
            file_type=file_type,
            file_content=file_content
        )

        logger.info(f"Pricing file uploaded: {response.file_name} ({response.rows_uploaded} rows)")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload pricing file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )
