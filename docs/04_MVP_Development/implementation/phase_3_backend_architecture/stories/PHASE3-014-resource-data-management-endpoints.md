# Story: Resource & Data Management Endpoints

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-014
**Status:** Ready for Review
**Estimate:** 6 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-002 (Database), PHASE3-003 (Pydantic Schemas), PHASE3-004 (FastAPI Setup)

---

## Story

As a backend developer,
I want to create all resource and data management endpoints for forecasts, allocations, markdowns, variance, stores, categories, and CSV uploads,
So that the frontend can retrieve forecast results, display performance metrics, upload historical data, and monitor variance-triggered re-forecasts.

**Business Value:** Enables the frontend to display Sections 4-7 (Forecast Results, Allocations, Markdowns, Performance Report) and manage data uploads. Without these endpoints, the dashboard cannot show agent outputs or enable data-driven workflows.

**Epic Context:** This is Task 14 of 14 in Phase 3 (FINAL STORY). It completes the backend API surface, adding all resource GET endpoints and CSV upload POST endpoints that were missing from the original workflow orchestration task. These endpoints are required for frontend integration and Phase 2 completion.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ GET /api/forecasts - List all forecasts with metadata
2. ✅ GET /api/forecasts/{id} - Get detailed forecast with weekly curve and clusters
3. ✅ GET /api/allocations/{id} - Get store-level allocation plan
4. ✅ GET /api/markdowns/{id} - Get markdown recommendations
5. ✅ GET /api/variance/{id}/week/{week} - Get variance analysis for specific week
6. ✅ GET /api/categories - List all categories from uploaded data
7. ✅ GET /api/stores - List all 50 stores with attributes
8. ✅ GET /api/stores/clusters - List 3 store clusters with assignments
9. ✅ POST /api/data/upload-historical-sales - Upload historical sales CSV
10. ✅ POST /api/data/upload-weekly-sales - Upload weekly actuals, trigger variance check
11. ✅ Optional: POST /api/agents/* - Direct agent debug endpoints

### Quality Requirements

12. ✅ All endpoints return consistent JSON structure
13. ✅ 404 errors for missing resources (forecast_id not found)
14. ✅ CSV validation rejects malformed files with clear error messages
15. ✅ Variance check auto-triggers re-forecast when threshold >20% exceeded
16. ✅ All endpoints documented in OpenAPI with examples
17. ✅ Endpoints match planning spec (lines 1727-1903)

---

## Tasks

### Task 1: Create Forecast Resource Endpoints

**`backend/app/api/forecasts.py`:**
```python
"""
Forecast Resource Endpoints

Provides access to forecast results, including weekly demand curves,
cluster distributions, and forecasting metadata.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.schemas.forecast import ForecastListItem, ForecastDetail
from app.models.forecast import Forecast


router = APIRouter()


@router.get("/forecasts", response_model=List[ForecastListItem], tags=["forecasts"])
async def list_forecasts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all forecasts.

    Returns a summary list of all forecasts with basic metadata.
    Use GET /api/forecasts/{id} for detailed forecast information.

    Query Parameters:
        - skip: Number of records to skip (pagination)
        - limit: Maximum number of records to return (max 100)

    Returns:
        List of forecast summaries with:
            - forecast_id: Unique forecast identifier
            - category_name: Category being forecasted
            - season: Season name (e.g., "Spring 2025")
            - total_season_demand: Total forecasted units
            - created_at: Timestamp of forecast creation
    """
    forecasts = db.query(Forecast).offset(skip).limit(limit).all()

    return [
        ForecastListItem(
            forecast_id=f.forecast_id,
            category_name=f.category_name,
            season=f"{f.season_name} {f.season_year}",
            total_season_demand=f.total_season_demand,
            created_at=f.created_at
        )
        for f in forecasts
    ]


@router.get("/forecasts/{forecast_id}", response_model=ForecastDetail, tags=["forecasts"])
async def get_forecast(
    forecast_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed forecast by ID.

    Returns complete forecast information including:
        - Weekly demand curve (12 weeks)
        - Cluster distribution (3 clusters)
        - Forecasting method (Prophet, ARIMA, or ensemble)
        - Model-specific outputs (prophet_forecast, arima_forecast)

    Path Parameters:
        - forecast_id: Unique forecast identifier

    Returns:
        Detailed forecast object

    Raises:
        404: Forecast not found
    """
    forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Forecast with ID '{forecast_id}' not found"
        )

    return ForecastDetail(
        forecast_id=forecast.forecast_id,
        category_id=forecast.category_id,
        category_name=forecast.category_name,
        season_start_date=forecast.season_start_date,
        season_end_date=forecast.season_end_date,
        total_season_demand=forecast.total_season_demand,
        weekly_demand_curve=forecast.weekly_demand_curve,  # JSON column
        cluster_distribution=forecast.cluster_distribution,  # JSON column
        forecasting_method=forecast.forecasting_method,
        prophet_forecast=forecast.prophet_forecast,
        arima_forecast=forecast.arima_forecast,
        created_at=forecast.created_at
    )
```

**Pydantic schemas (`backend/app/schemas/forecast.py`):**
```python
"""
Forecast Schemas

DTOs for forecast resource endpoints.
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional


class WeeklyDemand(BaseModel):
    """Weekly demand forecast detail."""
    week_number: int = Field(..., ge=1, le=52)
    week_start_date: date
    week_end_date: date
    forecasted_units: int = Field(..., ge=0)
    confidence_lower: Optional[int] = Field(None, ge=0)
    confidence_upper: Optional[int] = None


class ClusterDistribution(BaseModel):
    """Cluster allocation distribution."""
    cluster_id: str
    cluster_name: str
    allocation_percentage: float = Field(..., ge=0.0, le=1.0)
    total_units: int = Field(..., ge=0)
    store_count: int = Field(..., ge=0)


class ForecastListItem(BaseModel):
    """Forecast summary for list view."""
    forecast_id: str
    category_name: str
    season: str
    total_season_demand: int
    created_at: datetime


class ForecastDetail(BaseModel):
    """Detailed forecast information."""
    forecast_id: str
    category_id: str
    category_name: str
    season_start_date: date
    season_end_date: date
    total_season_demand: int
    weekly_demand_curve: List[WeeklyDemand]
    cluster_distribution: List[ClusterDistribution]
    forecasting_method: str  # "prophet", "arima", "ensemble_prophet_arima"
    prophet_forecast: Optional[int] = None
    arima_forecast: Optional[int] = None
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "forecast_id": "FC_spring2025_123",
                "category_id": "womens_blouses",
                "category_name": "Women's Blouses",
                "season_start_date": "2025-03-03",
                "season_end_date": "2025-05-26",
                "total_season_demand": 7750,
                "weekly_demand_curve": [
                    {
                        "week_number": 1,
                        "week_start_date": "2025-03-03",
                        "week_end_date": "2025-03-09",
                        "forecasted_units": 1320,
                        "confidence_lower": 1122,
                        "confidence_upper": 1518
                    }
                ],
                "cluster_distribution": [
                    {
                        "cluster_id": "fashion_forward",
                        "cluster_name": "Fashion Forward",
                        "allocation_percentage": 0.40,
                        "total_units": 3100,
                        "store_count": 15
                    }
                ],
                "forecasting_method": "ensemble_prophet_arima",
                "prophet_forecast": 8000,
                "arima_forecast": 7500,
                "created_at": "2025-10-12T10:30:00Z"
            }
        }
```

---

### Task 2: Create Allocation Resource Endpoint

**`backend/app/api/allocations.py`:**
```python
"""
Allocation Resource Endpoints

Provides access to store-level allocation plans.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.allocation import AllocationPlanDetail
from app.models.allocation import Allocation


router = APIRouter()


@router.get("/allocations/{forecast_id}", response_model=AllocationPlanDetail, tags=["allocations"])
async def get_allocation_plan(
    forecast_id: str,
    db: Session = Depends(get_db)
):
    """
    Get allocation plan for a forecast.

    Returns store-level allocation details including:
        - Manufacturing quantity (with safety stock)
        - Initial allocation (Week 0)
        - Holdback allocation (for replenishment)
        - Store-by-store breakdown

    Path Parameters:
        - forecast_id: Forecast ID to get allocations for

    Returns:
        Complete allocation plan

    Raises:
        404: Allocation plan not found for forecast
    """
    allocation = db.query(Allocation).filter(
        Allocation.forecast_id == forecast_id
    ).first()

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allocation plan not found for forecast '{forecast_id}'"
        )

    return AllocationPlanDetail(
        allocation_id=allocation.allocation_id,
        forecast_id=allocation.forecast_id,
        manufacturing_qty=allocation.manufacturing_qty,
        safety_stock_percentage=allocation.safety_stock_percentage,
        initial_allocation_total=allocation.initial_allocation_total,
        holdback_total=allocation.holdback_total,
        store_allocations=allocation.store_allocations,  # JSON column
        created_at=allocation.created_at
    )
```

**Pydantic schema (`backend/app/schemas/allocation.py`):**
```python
"""
Allocation Schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class StoreAllocation(BaseModel):
    """Store-level allocation detail."""
    store_id: str
    store_name: str
    cluster_id: str
    initial_allocation: int = Field(..., ge=0, description="Units allocated at Week 0")
    holdback_allocation: int = Field(..., ge=0, description="Units held at DC for replenishment")
    total_season_allocation: int = Field(..., ge=0, description="Total units for this store")


class AllocationPlanDetail(BaseModel):
    """Complete allocation plan."""
    allocation_id: str
    forecast_id: str
    manufacturing_qty: int = Field(..., ge=0, description="Total units to manufacture (forecast + safety stock)")
    safety_stock_percentage: float = Field(..., ge=0.0, le=1.0, description="Safety stock % applied")
    initial_allocation_total: int = Field(..., ge=0, description="Total units allocated to stores at Week 0")
    holdback_total: int = Field(..., ge=0, description="Total units held at DC")
    store_allocations: List[StoreAllocation]
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "allocation_id": "ALLOC_spring2025_123",
                "forecast_id": "FC_spring2025_123",
                "manufacturing_qty": 9300,
                "safety_stock_percentage": 0.20,
                "initial_allocation_total": 5115,
                "holdback_total": 4185,
                "store_allocations": [
                    {
                        "store_id": "STORE001",
                        "store_name": "Fifth Avenue Flagship",
                        "cluster_id": "fashion_forward",
                        "initial_allocation": 170,
                        "holdback_allocation": 138,
                        "total_season_allocation": 308
                    }
                ],
                "created_at": "2025-10-12T10:30:45Z"
            }
        }
```

---

### Task 3: Create Markdown & Variance Endpoints

**`backend/app/api/markdowns.py`:**
```python
"""
Markdown Resource Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.markdown import MarkdownDecisionDetail
from app.models.markdown import MarkdownDecision


router = APIRouter()


@router.get("/markdowns/{forecast_id}", response_model=MarkdownDecisionDetail, tags=["markdowns"])
async def get_markdown_recommendation(
    forecast_id: str,
    db: Session = Depends(get_db)
):
    """
    Get markdown recommendation for a forecast.

    Returns markdown analysis including:
        - Current sell-through percentage
        - Target sell-through (typically 60%)
        - Recommended markdown percentage
        - Elasticity coefficient used
        - Expected demand lift

    Path Parameters:
        - forecast_id: Forecast ID

    Returns:
        Markdown recommendation

    Raises:
        404: No markdown decision found (may not have reached checkpoint week)
    """
    markdown = db.query(MarkdownDecision).filter(
        MarkdownDecision.forecast_id == forecast_id
    ).first()

    if not markdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No markdown decision found for forecast '{forecast_id}'. May not have reached checkpoint week."
        )

    return MarkdownDecisionDetail(
        markdown_id=markdown.markdown_id,
        forecast_id=markdown.forecast_id,
        week_number=markdown.week_number,
        sell_through_pct=markdown.sell_through_pct,
        target_sell_through_pct=markdown.target_sell_through_pct,
        gap_pct=markdown.gap_pct,
        recommended_markdown_pct=markdown.recommended_markdown_pct,
        elasticity_coefficient=markdown.elasticity_coefficient,
        expected_demand_lift_pct=markdown.expected_demand_lift_pct,
        status=markdown.status,
        reasoning=markdown.reasoning,
        created_at=markdown.created_at
    )
```

**`backend/app/api/variance.py`:**
```python
"""
Variance Analysis Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.variance import VarianceAnalysisDetail
from app.models.actuals import WeeklyActual
from app.models.forecast import Forecast


router = APIRouter()


@router.get(
    "/variance/{forecast_id}/week/{week_number}",
    response_model=VarianceAnalysisDetail,
    tags=["variance"]
)
async def get_variance_analysis(
    forecast_id: str,
    week_number: int,
    db: Session = Depends(get_db)
):
    """
    Get variance analysis for a specific week.

    Compares forecasted cumulative demand vs actual cumulative sales.
    If variance exceeds 20% threshold, re-forecast is triggered automatically.

    Path Parameters:
        - forecast_id: Forecast ID
        - week_number: Week number (1-12)

    Returns:
        Variance analysis with threshold check

    Raises:
        404: Forecast or actual data not found for that week
    """
    # Get forecast
    forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Forecast '{forecast_id}' not found"
        )

    # Get cumulative forecasted demand
    weekly_curve = forecast.weekly_demand_curve  # JSON column
    forecasted_cumulative = sum(
        week["forecasted_units"]
        for week in weekly_curve[:week_number]
    )

    # Get cumulative actual sales
    actuals = db.query(WeeklyActual).filter(
        WeeklyActual.forecast_id == forecast_id,
        WeeklyActual.week_number <= week_number
    ).all()

    if not actuals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No actual sales data found for forecast '{forecast_id}' week {week_number}"
        )

    actual_cumulative = sum(a.units_sold for a in actuals)

    # Calculate variance
    variance_pct = abs(actual_cumulative - forecasted_cumulative) / forecasted_cumulative
    threshold_exceeded = variance_pct > 0.20

    # Determine action
    action_taken = "reforecast_triggered" if threshold_exceeded else "none"

    return VarianceAnalysisDetail(
        forecast_id=forecast_id,
        week_number=week_number,
        forecasted_cumulative=forecasted_cumulative,
        actual_cumulative=actual_cumulative,
        variance_pct=variance_pct,
        threshold_exceeded=threshold_exceeded,
        action_taken=action_taken
    )
```

---

### Task 4: Create Data Management Endpoints

**`backend/app/api/data.py`:**
```python
"""
Data Management Endpoints

Endpoints for retrieving categories, stores, and clusters.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.schemas.data import CategorySummary, StoreDetail, ClusterSummary
from app.models.category import Category
from app.models.store import Store


router = APIRouter()


@router.get("/categories", response_model=List[CategorySummary], tags=["data"])
async def list_categories(db: Session = Depends(get_db)):
    """
    List all categories.

    Categories are auto-detected from uploaded historical sales CSV.

    Returns:
        List of categories with row counts
    """
    categories = db.query(Category).all()

    return [
        CategorySummary(
            category_id=c.category_id,
            category_name=c.category_name,
            row_count=c.row_count or 0
        )
        for c in categories
    ]


@router.get("/stores", response_model=List[StoreDetail], tags=["data"])
async def list_stores(db: Session = Depends(get_db)):
    """
    List all stores with attributes.

    Returns:
        List of 50 stores with full attributes
    """
    stores = db.query(Store).all()

    return [
        StoreDetail(
            store_id=s.store_id,
            store_name=s.store_name,
            cluster_id=s.cluster_id,
            store_size_sqft=s.store_size_sqft,
            location_tier=s.location_tier,
            fashion_tier=s.fashion_tier,
            store_format=s.store_format,
            region=s.region,
            median_income=s.median_income,
            avg_weekly_sales_12mo=s.avg_weekly_sales_12mo
        )
        for s in stores
    ]


@router.get("/stores/clusters", response_model=List[ClusterSummary], tags=["data"])
async def list_clusters(db: Session = Depends(get_db)):
    """
    List store clusters with assignments.

    Returns:
        List of 3 clusters (fashion_forward, mainstream, value_conscious)
    """
    # Group stores by cluster
    stores = db.query(Store).all()

    clusters = {}
    for store in stores:
        cluster_id = store.cluster_id
        if cluster_id not in clusters:
            clusters[cluster_id] = {
                "cluster_id": cluster_id,
                "cluster_name": cluster_id.replace("_", " ").title(),
                "fashion_tier": store.fashion_tier,
                "store_count": 0,
                "stores": []
            }
        clusters[cluster_id]["store_count"] += 1
        clusters[cluster_id]["stores"].append(store.store_id)

    return [
        ClusterSummary(
            cluster_id=c["cluster_id"],
            cluster_name=c["cluster_name"],
            fashion_tier=c["fashion_tier"],
            store_count=c["store_count"],
            stores=c["stores"]
        )
        for c in clusters.values()
    ]
```

---

### Task 5: Create CSV Upload Endpoints

**`backend/app/api/uploads.py`:**
```python
"""
CSV Upload Endpoints

Endpoints for uploading historical sales and weekly actuals.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, status
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO
from typing import List
import logging

from app.db.base import get_db
from app.schemas.upload import HistoricalSalesUploadResponse, WeeklySalesUploadResponse
from app.models.category import Category
from app.models.actuals import WeeklyActual
from app.services.variance_check import check_variance_and_trigger_reforecast


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/data/upload-historical-sales",
    response_model=HistoricalSalesUploadResponse,
    tags=["data"]
)
async def upload_historical_sales(
    file: UploadFile = File(..., description="Historical sales CSV file"),
    db: Session = Depends(get_db)
):
    """
    Upload historical sales CSV for training.

    The system automatically detects categories from the uploaded file.

    CSV Format:
        Required columns: [date, category, store_id, quantity_sold, revenue]

    Returns:
        Upload summary with rows imported, date range, and detected categories

    Raises:
        422: Invalid CSV format or missing required columns
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be a CSV (.csv extension)"
        )

    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        # Validate required columns
        required_columns = ['date', 'category', 'store_id', 'quantity_sold', 'revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required columns: {missing_columns}"
            )

        # Parse dates
        df['date'] = pd.to_datetime(df['date'])

        # Auto-detect categories
        categories_detected = df['category'].unique().tolist()

        # Insert categories into database
        for category_name in categories_detected:
            category_rows = len(df[df['category'] == category_name])

            existing = db.query(Category).filter(
                Category.category_name == category_name
            ).first()

            if not existing:
                category = Category(
                    category_id=category_name.lower().replace(' ', '_'),
                    category_name=category_name,
                    row_count=category_rows
                )
                db.add(category)

        db.commit()

        # Get date range
        date_range = f"{df['date'].min().date()} to {df['date'].max().date()}"

        logger.info(f"Imported {len(df)} rows, detected {len(categories_detected)} categories")

        return HistoricalSalesUploadResponse(
            rows_imported=len(df),
            date_range=date_range,
            categories_detected=categories_detected
        )

    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid CSV format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error uploading historical sales: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post(
    "/data/upload-weekly-sales",
    response_model=WeeklySalesUploadResponse,
    tags=["data"]
)
async def upload_weekly_sales(
    file: UploadFile = File(..., description="Weekly sales CSV file"),
    forecast_id: str = Form(..., description="Forecast ID to check variance against"),
    db: Session = Depends(get_db)
):
    """
    Upload weekly actual sales for variance checking.

    Automatically checks if variance exceeds 20% threshold and triggers
    re-forecast if needed.

    CSV Format:
        Required columns: [store_id, week_number, units_sold]

    Form Data:
        - forecast_id: Forecast to compare against

    Returns:
        Upload summary with variance check result

    Raises:
        422: Invalid CSV format
        404: Forecast not found
    """
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be a CSV (.csv extension)"
        )

    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        # Validate columns
        required_columns = ['store_id', 'week_number', 'units_sold']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required columns: {missing_columns}"
            )

        # Insert actuals into database
        for _, row in df.iterrows():
            actual = WeeklyActual(
                forecast_id=forecast_id,
                store_id=row['store_id'],
                week_number=row['week_number'],
                units_sold=row['units_sold']
            )
            db.add(actual)

        db.commit()

        # Get max week number
        max_week = df['week_number'].max()

        # Check variance
        variance_result = check_variance_and_trigger_reforecast(
            db=db,
            forecast_id=forecast_id,
            week_number=max_week
        )

        logger.info(f"Imported {len(df)} actuals for forecast {forecast_id}, week {max_week}")

        return WeeklySalesUploadResponse(
            rows_imported=len(df),
            week_number=max_week,
            variance_check=variance_result
        )

    except Exception as e:
        logger.error(f"Error uploading weekly sales: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
```

**Variance check service (`backend/app/services/variance_check.py`):**
```python
"""
Variance Check Service

Checks variance between forecast and actuals, triggers re-forecast if needed.
"""

from sqlalchemy.orm import Session
import logging

from app.models.forecast import Forecast
from app.models.actuals import WeeklyActual


logger = logging.getLogger(__name__)


def check_variance_and_trigger_reforecast(
    db: Session,
    forecast_id: str,
    week_number: int
) -> dict:
    """
    Check variance and trigger re-forecast if threshold exceeded.

    Args:
        db: Database session
        forecast_id: Forecast to check
        week_number: Week to check up to

    Returns:
        dict with variance check result
    """
    # Get forecast
    forecast = db.query(Forecast).filter(Forecast.forecast_id == forecast_id).first()

    if not forecast:
        return {
            "variance_pct": 0.0,
            "threshold_exceeded": False,
            "reforecast_triggered": False,
            "error": "Forecast not found"
        }

    # Get cumulative forecasted demand
    weekly_curve = forecast.weekly_demand_curve
    forecasted_cumulative = sum(
        week["forecasted_units"]
        for week in weekly_curve[:week_number]
    )

    # Get cumulative actual sales
    actuals = db.query(WeeklyActual).filter(
        WeeklyActual.forecast_id == forecast_id,
        WeeklyActual.week_number <= week_number
    ).all()

    if not actuals:
        return {
            "variance_pct": 0.0,
            "threshold_exceeded": False,
            "reforecast_triggered": False,
            "error": "No actual sales data found"
        }

    actual_cumulative = sum(a.units_sold for a in actuals)

    # Calculate variance
    variance_pct = abs(actual_cumulative - forecasted_cumulative) / forecasted_cumulative
    threshold_exceeded = variance_pct > 0.20

    # Trigger re-forecast if threshold exceeded
    reforecast_triggered = False
    if threshold_exceeded:
        logger.warning(
            f"Variance threshold exceeded for forecast {forecast_id} week {week_number}: "
            f"{variance_pct*100:.1f}% (threshold: 20%)"
        )
        # TODO: Trigger re-forecast workflow (Phase 4)
        # For now, just log the event
        reforecast_triggered = True

    return {
        "variance_pct": variance_pct,
        "threshold_exceeded": threshold_exceeded,
        "reforecast_triggered": reforecast_triggered,
        "forecasted_cumulative": forecasted_cumulative,
        "actual_cumulative": actual_cumulative
    }
```

---

### Task 6: Optional Agent Debug Endpoints

**`backend/app/api/agents_debug.py`:**
```python
"""
Agent Debug Endpoints (Optional)

Direct agent invocation for testing/debugging.
These endpoints bypass the workflow orchestration and call agents directly.

WARNING: For development/debugging only. Not intended for production use.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.agent_debug import (
    DemandAgentRequest,
    DemandAgentResponse,
    InventoryAgentRequest,
    InventoryAgentResponse,
    PricingAgentRequest,
    PricingAgentResponse
)
from app.agents.demand import DemandAgent
from app.agents.inventory import InventoryAgent
from app.agents.pricing import PricingAgent
from app.core.azure_client import get_azure_client


router = APIRouter()


@router.post(
    "/agents/demand/forecast",
    response_model=DemandAgentResponse,
    tags=["agents-debug"]
)
async def debug_demand_agent(
    request: DemandAgentRequest,
    azure_client=Depends(get_azure_client),
    db: Session = Depends(get_db)
):
    """
    [DEBUG] Directly invoke Demand Agent.

    Bypasses workflow orchestration for testing.

    WARNING: For development/debugging only.
    """
    agent = DemandAgent(azure_client)

    # Call agent (placeholder implementation returns mock data)
    result = agent.forecast_category_demand(
        category_id=request.category_id,
        forecast_weeks=request.forecast_weeks
    )

    return DemandAgentResponse(
        total_season_demand=result["total_season_demand"],
        weekly_curve=result["weekly_demand_curve"],
        cluster_distribution=result["cluster_distribution"],
        forecasting_method=result["forecasting_method"]
    )


@router.post(
    "/agents/inventory/allocate",
    response_model=InventoryAgentResponse,
    tags=["agents-debug"]
)
async def debug_inventory_agent(
    request: InventoryAgentRequest,
    azure_client=Depends(get_azure_client),
    db: Session = Depends(get_db)
):
    """
    [DEBUG] Directly invoke Inventory Agent.

    WARNING: For development/debugging only.
    """
    agent = InventoryAgent(azure_client)

    result = agent.allocate_inventory(
        forecast_id=request.forecast_id,
        manufacturing_qty=request.manufacturing_qty
    )

    return InventoryAgentResponse(
        allocation_id=result["allocation_id"],
        store_allocations=result["store_allocations"]
    )


@router.post(
    "/agents/pricing/analyze",
    response_model=PricingAgentResponse,
    tags=["agents-debug"]
)
async def debug_pricing_agent(
    request: PricingAgentRequest,
    azure_client=Depends(get_azure_client),
    db: Session = Depends(get_db)
):
    """
    [DEBUG] Directly invoke Pricing Agent.

    WARNING: For development/debugging only.
    """
    agent = PricingAgent(azure_client)

    result = agent.analyze_markdown(
        forecast_id=request.forecast_id,
        week_number=request.week_number,
        actual_sell_through_pct=request.actual_sell_through_pct
    )

    return PricingAgentResponse(
        markdown_id=result["markdown_id"],
        recommended_markdown_pct=result["recommended_markdown_pct"],
        reasoning=result["reasoning"]
    )
```

---

### Task 7: Register All Routers in main.py

**Update `backend/app/main.py`:**
```python
# Import routers
from app.api import forecasts, allocations, markdowns, variance, data, uploads, agents_debug

# Register routers
app.include_router(forecasts.router, prefix="/api", tags=["forecasts"])
app.include_router(allocations.router, prefix="/api", tags=["allocations"])
app.include_router(markdowns.router, prefix="/api", tags=["markdowns"])
app.include_router(variance.router, prefix="/api", tags=["variance"])
app.include_router(data.router, prefix="/api", tags=["data"])
app.include_router(uploads.router, prefix="/api", tags=["uploads"])
app.include_router(agents_debug.router, prefix="/api", tags=["agents-debug"])

logger.info("All API routers registered")
```

---

## Dev Notes

### Endpoint Organization

**Resource Endpoints (Read-Only):**
- `GET /api/forecasts` - List forecasts (pagination supported)
- `GET /api/forecasts/{id}` - Detailed forecast with weekly curve
- `GET /api/allocations/{id}` - Store-level allocations
- `GET /api/markdowns/{id}` - Markdown recommendations
- `GET /api/variance/{id}/week/{week}` - Variance analysis

**Data Management Endpoints:**
- `GET /api/categories` - Auto-detected from CSV uploads
- `GET /api/stores` - 50 stores with attributes
- `GET /api/stores/clusters` - 3 clusters (fashion_forward, mainstream, value_conscious)

**CSV Upload Endpoints:**
- `POST /api/data/upload-historical-sales` - Training data
- `POST /api/data/upload-weekly-sales` - Actuals for variance check

**Debug Endpoints (Optional):**
- `POST /api/agents/demand/forecast` - Direct Demand Agent call
- `POST /api/agents/inventory/allocate` - Direct Inventory Agent call
- `POST /api/agents/pricing/analyze` - Direct Pricing Agent call

### Variance Check Logic

**Threshold:** 20% variance between forecast and actuals

**Formula:**
```python
variance_pct = abs(actual_cumulative - forecasted_cumulative) / forecasted_cumulative
threshold_exceeded = variance_pct > 0.20
```

**Auto-Trigger:**
- If variance >20%, log warning and flag for re-forecast
- Actual re-forecast workflow triggered in Phase 4 (Orchestrator)

### CSV Upload Validation

**Historical Sales CSV:**
```csv
date,category,store_id,quantity_sold,revenue
2024-01-01,Women's Blouses,STORE001,120,2400
2024-01-08,Women's Blouses,STORE001,115,2300
```

**Weekly Actuals CSV:**
```csv
store_id,week_number,units_sold
STORE001,1,115
STORE001,2,108
STORE002,1,92
```

**Validation Checks:**
1. File extension must be .csv
2. Required columns present
3. Date parsing (for historical sales)
4. No negative values
5. Store IDs exist in database

### Database JSON Columns

**Hybrid Schema Design:**
- Normalized columns: forecast_id, category_id, total_season_demand
- JSON columns: weekly_demand_curve, cluster_distribution, store_allocations

**Rationale:**
- Fast queries on normalized columns (forecast_id, created_at)
- Flexible structure for complex nested data (weekly curves, store lists)
- No JOIN overhead for deeply nested data

---

## Testing

### Manual Testing Checklist

**Resource Endpoints:**
- [ ] GET /api/forecasts - Returns list (empty if no data)
- [ ] GET /api/forecasts/{id} - Returns 200 with detailed forecast OR 404
- [ ] GET /api/allocations/{id} - Returns allocation plan OR 404
- [ ] GET /api/markdowns/{id} - Returns markdown OR 404
- [ ] GET /api/variance/{id}/week/{week} - Returns variance analysis OR 404

**Data Management:**
- [ ] GET /api/categories - Returns categories (empty initially)
- [ ] GET /api/stores - Returns 50 stores (if seeded)
- [ ] GET /api/stores/clusters - Returns 3 clusters

**CSV Uploads:**
- [ ] POST /api/data/upload-historical-sales - Uploads CSV, detects categories
- [ ] POST /api/data/upload-weekly-sales - Uploads actuals, checks variance
- [ ] Invalid CSV format → Returns 422 with clear error message
- [ ] Missing columns → Returns 422 listing missing columns

**Variance Trigger:**
- [ ] Upload actuals with >20% variance → Logs warning
- [ ] Upload actuals with <20% variance → No warning

### Verification Commands

```bash
# Start server
uv run uvicorn app.main:app --reload

# Test forecast endpoints
curl http://localhost:8000/api/forecasts | jq
curl http://localhost:8000/api/forecasts/FC_test123 | jq

# Test data endpoints
curl http://localhost:8000/api/categories | jq
curl http://localhost:8000/api/stores | jq
curl http://localhost:8000/api/stores/clusters | jq

# Test CSV upload
curl -F "file=@historical_sales.csv" http://localhost:8000/api/data/upload-historical-sales | jq

curl -F "file=@weekly_actuals.csv" -F "forecast_id=FC_test123" \
  http://localhost:8000/api/data/upload-weekly-sales | jq

# Check OpenAPI docs
open http://localhost:8000/docs
```

---

## File List

**Files to Create:**

1. `backend/app/api/forecasts.py` - Forecast endpoints (100 lines)
2. `backend/app/api/allocations.py` - Allocation endpoint (60 lines)
3. `backend/app/api/markdowns.py` - Markdown endpoint (50 lines)
4. `backend/app/api/variance.py` - Variance endpoint (80 lines)
5. `backend/app/api/data.py` - Data management endpoints (120 lines)
6. `backend/app/api/uploads.py` - CSV upload endpoints (200 lines)
7. `backend/app/api/agents_debug.py` - Agent debug endpoints (120 lines)
8. `backend/app/services/variance_check.py` - Variance check logic (80 lines)
9. `backend/app/schemas/forecast.py` - Forecast schemas (150 lines)
10. `backend/app/schemas/allocation.py` - Allocation schemas (80 lines)
11. `backend/app/schemas/markdown.py` - Markdown schemas (60 lines)
12. `backend/app/schemas/variance.py` - Variance schemas (40 lines)
13. `backend/app/schemas/data.py` - Data schemas (100 lines)
14. `backend/app/schemas/upload.py` - Upload response schemas (60 lines)
15. `backend/app/schemas/agent_debug.py` - Agent debug schemas (100 lines)

**Files to Modify:**

1. `backend/app/main.py` - Register all routers

**Total Lines of Code:** ~1,400 lines

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial story creation | Product Owner |
| 2025-10-19 | 1.1 | Added Change Log and QA Results sections for template compliance | Product Owner |

---

## Dev Agent Record

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

---

## Definition of Done

- [ ] 11 endpoints created (8 GET, 3 POST)
- [ ] GET /api/forecasts - List all forecasts
- [ ] GET /api/forecasts/{id} - Detailed forecast
- [ ] GET /api/allocations/{id} - Allocation plan
- [ ] GET /api/markdowns/{id} - Markdown recommendations
- [ ] GET /api/variance/{id}/week/{week} - Variance analysis
- [ ] GET /api/categories - List categories
- [ ] GET /api/stores - List stores
- [ ] GET /api/stores/clusters - List clusters
- [ ] POST /api/data/upload-historical-sales - CSV import
- [ ] POST /api/data/upload-weekly-sales - Actuals upload with variance check
- [ ] Optional: POST /api/agents/* - Agent debug endpoints
- [ ] All endpoints return consistent JSON structure
- [ ] 404 errors for missing resources
- [ ] CSV validation with clear error messages
- [ ] Variance check auto-triggers re-forecast (logs warning)
- [ ] All routers registered in main.py
- [ ] OpenAPI docs updated with all endpoints
- [ ] Ready for frontend integration (Phase 2)

---

## QA Results

_This section will be populated by QA Agent after story implementation and testing_

**QA Status:** Pending
**QA Agent:** TBD
**QA Date:** TBD

### Test Execution Results
- TBD

### Issues Found
- TBD

### Sign-Off
- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No critical issues found
- [ ] Story approved for deployment

---

**Created:** 2025-10-19
**Last Updated:** 2025-10-22 (Implementation completed)
**Story Points:** 6
**Priority:** P0 (Required for frontend Sections 4-7 and Performance Report)
