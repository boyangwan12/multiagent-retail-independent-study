"""
Historical/Training Data Upload Endpoints.

Handles CSV uploads for historical sales and store attributes (PRD Stories 1.1 & 1.2).
These uploads happen BEFORE workflow creation and provide training data for forecasting models.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.data_upload_service import DataUploadService
from app.utils.csv_validator import ValidationError
import logging

logger = logging.getLogger("fashion_forecast")

router = APIRouter()


def get_upload_service(db: Session = Depends(get_db)) -> DataUploadService:
    """Dependency injection for DataUploadService."""
    return DataUploadService(db)


@router.post("/upload/historical-sales", status_code=status.HTTP_200_OK)
async def upload_historical_sales(
    file: UploadFile = File(...),
    service: DataUploadService = Depends(get_upload_service)
):
    """
    Upload historical sales data (2022-2024).

    **Required CSV Format:**
    - Columns: date, category, store_id, quantity_sold, revenue
    - Date format: YYYY-MM-DD
    - At least 2 years of data
    - 50 stores minimum

    **Returns:**
    - Row count
    - Categories detected
    - Date range
    - Validation summary

    **Example:**
    ```
    date,category,store_id,quantity_sold,revenue
    2022-01-01,Women's Dresses,S001,120,2400.00
    2022-01-01,Women's Dresses,S002,95,1900.00
    ...
    ```
    """
    try:
        logger.info(f"Received historical sales upload request: {file.filename}")

        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .csv files are accepted."
            )

        # Validate file size (max 50MB for historical data)
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum allowed size of 50MB"
            )

        # Reset file pointer for service to read
        await file.seek(0)

        # Process upload using service
        result = service.upload_historical_sales(file)

        logger.info(f"Historical sales uploaded successfully: {result['rows_inserted']} rows")
        return result

    except ValidationError as e:
        # CSV validation failed - return structured error
        logger.warning(f"Historical sales validation failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error_type": "VALIDATION_ERROR",
                "message": e.message,
                "errors": e.errors
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to upload historical sales: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.post("/upload/store-attributes", status_code=status.HTTP_200_OK)
async def upload_store_attributes(
    file: UploadFile = File(...),
    service: DataUploadService = Depends(get_upload_service)
):
    """
    Upload store attributes for clustering.

    **Required CSV Format:**
    - Columns: store_id, store_name, avg_weekly_sales_12mo, store_size_sqft,
               median_income, location_tier, fashion_tier, store_format, region
    - 50 stores minimum
    - 7 features for clustering

    **Returns:**
    - Row count
    - Feature validation status
    - Store summary statistics

    **Example:**
    ```
    store_id,store_name,avg_weekly_sales_12mo,store_size_sqft,median_income,location_tier,fashion_tier,store_format,region
    S001,Manhattan Flagship,50000,25000,125000,A,Premium,MALL,NORTHEAST
    S002,Brooklyn Heights,38000,18000,110000,A,Mainstream,SHOPPING_CENTER,NORTHEAST
    ...
    ```

    **Alternative Simplified Format (auto-derives required fields):**
    ```
    store_id,size_sqft,income_level,foot_traffic,competitor_density,online_penetration,population_density,mall_location
    S001,25000,125000,3500,0.35,0.25,12000,True
    ...
    ```
    """
    try:
        logger.info(f"Received store attributes upload request: {file.filename}")

        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .csv files are accepted."
            )

        # Validate file size (max 5MB for store attributes)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum allowed size of 5MB"
            )

        # Reset file pointer for service to read
        await file.seek(0)

        # Process upload using service
        result = service.upload_store_attributes(file)

        logger.info(f"Store attributes uploaded successfully: {result['rows_inserted']} stores")
        return result

    except ValidationError as e:
        # CSV validation failed - return structured error
        logger.warning(f"Store attributes validation failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error_type": "VALIDATION_ERROR",
                "message": e.message,
                "errors": e.errors
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to upload store attributes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )
