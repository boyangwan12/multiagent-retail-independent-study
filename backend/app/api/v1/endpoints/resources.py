"""Resource & Data Management Endpoints"""

from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from io import StringIO
import logging

from app.database.db import get_db
from app.models.category import Category
from app.models.store import Store
from app.models.allocation import Allocation
from app.models.markdown import Markdown
from app.services.variance_check import check_variance_and_trigger_reforecast

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Resources"])


# Allocation Endpoints
@router.get("/allocations/{forecast_id}", response_model=dict)
async def get_allocation_plan(forecast_id: str, db: Session = Depends(get_db)):
    """Get allocation plan for a forecast."""
    allocation = db.query(Allocation).filter(Allocation.forecast_id == forecast_id).first()

    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    return {
        "allocation_id": allocation.allocation_id or forecast_id,
        "forecast_id": allocation.forecast_id,
        "manufacturing_qty": allocation.manufacturing_qty or 0,
        "safety_stock_percentage": allocation.safety_stock_percentage or 0.20,
        "initial_allocation_total": allocation.initial_allocation_total or 0,
        "holdback_total": allocation.holdback_total or 0,
        "store_allocations": allocation.store_allocations or [],
        "created_at": allocation.created_at.isoformat() if allocation.created_at else None
    }


# Markdown Endpoints
@router.get("/markdowns/{forecast_id}", response_model=dict)
async def get_markdown_recommendation(forecast_id: str, db: Session = Depends(get_db)):
    """Get markdown recommendation for a forecast."""
    markdown = db.query(Markdown).filter(Markdown.forecast_id == forecast_id).first()

    if not markdown:
        raise HTTPException(status_code=404, detail="Markdown decision not found")

    return {
        "markdown_id": markdown.markdown_id or forecast_id,
        "forecast_id": markdown.forecast_id,
        "week_number": markdown.week_number or 6,
        "sell_through_pct": markdown.sell_through_pct or 0.55,
        "target_sell_through_pct": 0.60,
        "gap_pct": (0.60 - (markdown.sell_through_pct or 0.55)),
        "recommended_markdown_pct": markdown.recommended_markdown_pct or 0.10,
        "elasticity_coefficient": 2.0,
        "expected_demand_lift_pct": (markdown.recommended_markdown_pct or 0.10) * 1.5,
        "status": markdown.status or "pending",
        "reasoning": markdown.reasoning or "Gap × Elasticity formula applied",
        "created_at": markdown.created_at.isoformat() if markdown.created_at else None
    }


# Data Endpoints
@router.get("/categories", response_model=List[dict])
async def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    categories = db.query(Category).all()

    return [
        {
            "category_id": c.category_id,
            "category_name": c.category_name,
            "row_count": c.row_count or 0
        }
        for c in categories
    ]


@router.get("/stores", response_model=List[dict])
async def list_stores(db: Session = Depends(get_db)):
    """List all stores with attributes."""
    stores = db.query(Store).all()

    return [
        {
            "store_id": s.store_id,
            "store_name": s.store_name,
            "cluster_id": s.cluster_id or "mainstream",
            "store_size_sqft": s.store_size_sqft or 5000,
            "location_tier": s.location_tier or "A",
            "fashion_tier": s.fashion_tier or "mainstream",
            "store_format": s.store_format or "full_line",
            "region": s.region or "Northeast",
            "median_income": s.median_income or 75000,
            "avg_weekly_sales_12mo": s.avg_weekly_sales_12mo or 10000
        }
        for s in stores
    ]


@router.get("/stores/clusters", response_model=List[dict])
async def list_clusters(db: Session = Depends(get_db)):
    """List store clusters with assignments."""
    stores = db.query(Store).all()

    clusters = {}
    for store in stores:
        cluster_id = store.cluster_id or "mainstream"
        if cluster_id not in clusters:
            clusters[cluster_id] = {
                "cluster_id": cluster_id,
                "cluster_name": cluster_id.replace("_", " ").title(),
                "fashion_tier": store.fashion_tier or "mainstream",
                "store_count": 0,
                "stores": []
            }
        clusters[cluster_id]["store_count"] += 1
        clusters[cluster_id]["stores"].append(store.store_id)

    return list(clusters.values())


# CSV Upload Endpoints
@router.post("/data/upload-historical-sales", response_model=dict)
async def upload_historical_sales(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload historical sales CSV."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=422, detail="File must be CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        required_columns = ['date', 'category', 'store_id', 'quantity_sold', 'revenue']
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            raise HTTPException(status_code=422, detail=f"Missing columns: {missing}")

        df['date'] = pd.to_datetime(df['date'])
        categories = df['category'].unique().tolist()

        for category_name in categories:
            existing = db.query(Category).filter(Category.category_name == category_name).first()
            if not existing:
                category = Category(
                    category_id=category_name.lower().replace(' ', '_'),
                    category_name=category_name,
                    row_count=len(df[df['category'] == category_name])
                )
                db.add(category)

        db.commit()

        date_range = f"{df['date'].min().date()} to {df['date'].max().date()}"

        return {
            "rows_imported": len(df),
            "date_range": date_range,
            "categories_detected": categories
        }

    except Exception as e:
        logger.error(f"Error uploading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/upload-weekly-sales", response_model=dict)
async def upload_weekly_sales(
    file: UploadFile = File(...),
    forecast_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload weekly actual sales and check variance."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=422, detail="File must be CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))

        required_columns = ['store_id', 'week_number', 'units_sold']
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            raise HTTPException(status_code=422, detail=f"Missing columns: {missing}")

        max_week = int(df['week_number'].max())

        variance_result = check_variance_and_trigger_reforecast(
            db=db,
            forecast_id=forecast_id,
            week_number=max_week
        )

        return {
            "rows_imported": len(df),
            "week_number": max_week,
            "variance_check": variance_result
        }

    except Exception as e:
        logger.error(f"Error uploading: {e}")
        raise HTTPException(status_code=500, detail=str(e))
