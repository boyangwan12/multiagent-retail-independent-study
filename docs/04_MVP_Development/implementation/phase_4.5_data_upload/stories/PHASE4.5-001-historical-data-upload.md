# PHASE4.5-001: Historical Training Data Upload

**Story ID:** PHASE4.5-001
**Story Name:** Historical Training Data Upload (PRD Stories 1.1 & 1.2)
**Phase:** Phase 4.5 - Data Upload Infrastructure
**Dependencies:** Phase 4 complete
**Estimated Effort:** 6-8 hours
**Assigned To:** Developer (Full-Stack)
**Status:** Not Started

**Planning References:**
- PRD v3.3: Story 1.1 (Upload Historical Sales Data), Story 1.2 (Upload Store Attributes)
- Technical Architecture v3.3: Section 4.7 (Upload Endpoints & File Storage)
- Frontend Spec v3.3: Section 3.1 (Data Upload UI)

---

## User Story

**As a** retail planner using the Multi-Agent Forecasting System,
**I want** to upload historical sales data (2022-2024) and store attributes via the UI,
**So that** the system can train forecasting models without requiring manual database scripts.

---

## Context & Background

### What This Story Covers

This story implements UI-driven upload for **training data** required before forecasting:

1. **Historical Sales Data (PRD Story 1.1):**
   - 2-3 years of sales history
   - Format: date, category, store_id, quantity_sold, revenue
   - ~54,750 rows (50 stores × 365 days × 3 years)
   - Purpose: Train Prophet and ARIMA forecasting models

2. **Store Attributes (PRD Story 1.2):**
   - Store characteristics for clustering
   - Format: store_id, store_name, avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
   - 50 stores with 7 clustering features
   - Purpose: K-means clustering for allocation

### Why This Is Critical

**PRD Requirement:** Stories 1.1 and 1.2 are marked as **P0 (Blocker)** - system cannot forecast without this data.

**Current Gap:** Users must manually run `seed_db.py` script, which is:
- ❌ Not user-friendly for non-technical users
- ❌ Not mentioned in PRD user flow
- ❌ Blocks production deployment

**Solution:** UI-driven upload that:
- ✅ Allows drag-and-drop CSV upload
- ✅ Validates CSV format and content
- ✅ Inserts data directly into database
- ✅ Auto-detects available categories
- ✅ Provides clear error feedback

---

## Architecture

### Backend Endpoints

**1. POST /api/data/upload/historical-sales**

**Request:**
```http
POST /api/data/upload/historical-sales
Content-Type: multipart/form-data

Body:
  file: historical_sales_2022_2024.csv (File)
```

**Response (Success - 200 OK):**
```json
{
  "status": "success",
  "file_name": "historical_sales_2022_2024.csv",
  "rows_inserted": 54750,
  "categories_detected": ["Women's Dresses", "Men's Shirts", "Accessories"],
  "date_range": {
    "start": "2022-01-01",
    "end": "2024-12-31"
  },
  "validation_summary": {
    "stores_count": 50,
    "total_revenue": 12500000.00,
    "avg_daily_sales_per_store": 228.77
  },
  "uploaded_at": "2025-11-05T14:30:00Z"
}
```

**Response (Validation Error - 400 Bad Request):**
```json
{
  "status": "error",
  "error_type": "VALIDATION_ERROR",
  "message": "CSV validation failed: 3 errors found",
  "errors": [
    {
      "row": 125,
      "column": "quantity_sold",
      "error": "DATA_TYPE_MISMATCH",
      "expected": "integer",
      "actual": "N/A",
      "message": "Expected integer value, got 'N/A'"
    },
    {
      "row": 340,
      "column": "revenue",
      "error": "DATA_TYPE_MISMATCH",
      "expected": "float",
      "actual": "-100",
      "message": "Revenue cannot be negative"
    },
    {
      "error": "MISSING_COLUMN",
      "column": "store_id",
      "message": "Required column 'store_id' is missing"
    }
  ]
}
```

---

**2. POST /api/data/upload/store-attributes**

**Request:**
```http
POST /api/data/upload/store-attributes
Content-Type: multipart/form-data

Body:
  file: store_attributes.csv (File)
```

**Response (Success - 200 OK):**
```json
{
  "status": "success",
  "file_name": "store_attributes.csv",
  "rows_inserted": 50,
  "features_validated": 7,
  "clustering_ready": true,
  "store_summary": {
    "total_stores": 50,
    "premium_tier": 15,
    "mainstream_tier": 20,
    "value_tier": 15,
    "avg_store_size_sqft": 8500,
    "avg_weekly_sales": 4250.00
  },
  "uploaded_at": "2025-11-05T14:31:00Z"
}
```

---

### Database Strategy

**Approach:** Insert directly into existing database tables (no CSV file storage)

**Tables Used:**
```sql
-- Table 1: historical_sales (already exists from Phase 1)
CREATE TABLE historical_sales (
    sale_id VARCHAR(100) PRIMARY KEY,
    week_start_date DATE NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    units_sold INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

-- Table 2: stores (already exists from Phase 1)
CREATE TABLE stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    cluster_id VARCHAR(50),
    store_size_sqft INTEGER NOT NULL,
    location_tier VARCHAR(20) NOT NULL,
    median_income INTEGER NOT NULL,
    store_format VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    avg_weekly_sales_12mo FLOAT NOT NULL,
    FOREIGN KEY (cluster_id) REFERENCES store_clusters(cluster_id)
);
```

**Data Flow:**
```
User uploads CSV
    ↓
Backend validates CSV (columns, data types, business rules)
    ↓
Backend clears existing data (TRUNCATE tables)
    ↓
Backend inserts new data (batch insert, 1000 rows at a time)
    ↓
Backend returns success with summary statistics
    ↓
Frontend displays: "✓ 54,750 rows | Categories detected: Women's Dresses, Men's Shirts, Accessories"
```

---

## Frontend UI Design

### Location: Section 0 (Before Parameter Extraction)

**User Flow:**
```
1. User lands on dashboard
2. Sees "📊 Data Upload" card at top (Section 0)
3. Two upload zones side-by-side:
   - Left: "Historical Sales Data (2022-2024)"
   - Right: "Store Attributes"
4. User drags CSV file or clicks "Browse Files"
5. File preview shows: "historical_sales_2022_2024.csv (5.2 MB)"
6. User clicks "Upload & Validate"
7. Loading spinner with progress: "Uploading... 75%"
8. Success: "✓ 54,750 rows uploaded | Categories: Women's Dresses, Men's Shirts, Accessories"
9. Category dropdown appears below (auto-populated)
10. User proceeds to Parameter Extraction (Section 0.5)
```

### Wireframe

```
┌────────────────────────────────────────────────────────────┐
│  📊 Data Upload (Required Before Forecasting)              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────┐  ┌──────────────────────────┐  │
│  │ Historical Sales     │  │ Store Attributes         │  │
│  │ (2022-2024)          │  │ (50 stores)              │  │
│  ├──────────────────────┤  ├──────────────────────────┤  │
│  │                      │  │                          │  │
│  │  📂 Drag & Drop      │  │  📂 Drag & Drop          │  │
│  │  or Browse Files     │  │  or Browse Files         │  │
│  │                      │  │                          │  │
│  │ [Browse Files]       │  │ [Browse Files]           │  │
│  │                      │  │                          │  │
│  │ Expected format:     │  │ Expected format:         │  │
│  │ date, category,      │  │ store_id, store_name,    │  │
│  │ store_id,            │  │ avg_weekly_sales_12mo,   │  │
│  │ quantity_sold,       │  │ store_size_sqft,         │  │
│  │ revenue              │  │ median_income, ...       │  │
│  └──────────────────────┘  └──────────────────────────┘  │
│                                                            │
│  Status: ⏳ Waiting for historical sales data upload      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**After Upload:**
```
┌────────────────────────────────────────────────────────────┐
│  📊 Data Upload (Required Before Forecasting)              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ✅ Historical Sales: 54,750 rows uploaded                 │
│     Categories detected: Women's Dresses, Men's Shirts,    │
│     Accessories                                            │
│     Date range: 2022-01-01 to 2024-12-31                   │
│                                                            │
│  ✅ Store Attributes: 50 stores uploaded                   │
│     Ready for clustering (7 features validated)            │
│                                                            │
│  📝 Select Category for Forecasting:                       │
│     ┌─────────────────────────────────────┐               │
│     │ Women's Dresses               ▼     │               │
│     └─────────────────────────────────────┘               │
│                                                            │
│  [Continue to Parameter Extraction →]                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

### Backend API

- [ ] **AC1:** POST /api/data/upload/historical-sales endpoint accepts CSV file
- [ ] **AC2:** Backend validates required columns: date, category, store_id, quantity_sold, revenue
- [ ] **AC3:** Backend validates data types (date, string, integer, float)
- [ ] **AC4:** Backend validates business rules:
  - [ ] Date range at least 1 year
  - [ ] quantity_sold >= 0
  - [ ] revenue >= 0
  - [ ] store_id must exist in stores table (if stores uploaded first)
- [ ] **AC5:** Backend clears existing historical_sales data before insert
- [ ] **AC6:** Backend performs batch insert (1000 rows at a time)
- [ ] **AC7:** Backend auto-detects unique categories from CSV
- [ ] **AC8:** Backend returns validation errors with row numbers
- [ ] **AC9:** POST /api/data/upload/store-attributes endpoint accepts CSV file
- [ ] **AC10:** Backend validates 7 required features for clustering
- [ ] **AC11:** Backend validates enum values (location_tier, fashion_tier, store_format, region)
- [ ] **AC12:** Backend clears existing stores data before insert
- [ ] **AC13:** Backend returns summary statistics (row counts, averages)

### Frontend UI

- [ ] **AC14:** Upload UI appears in Section 0 (above parameter extraction)
- [ ] **AC15:** Two upload zones displayed side-by-side (responsive: stacks on mobile)
- [ ] **AC16:** Drag-and-drop functionality works for both zones
- [ ] **AC17:** "Browse Files" button opens file picker (accepts .csv only)
- [ ] **AC18:** File preview shows file name and size
- [ ] **AC19:** "Upload & Validate" button triggers upload
- [ ] **AC20:** Loading spinner displays during upload
- [ ] **AC21:** Progress indicator shows upload percentage (simulated or real)
- [ ] **AC22:** Success message displays:
  - ✓ Row count
  - ✓ Categories detected
  - ✓ Date range
- [ ] **AC23:** Error message displays validation errors in scrollable list
- [ ] **AC24:** "Download Error Report" button generates .txt file with all errors
- [ ] **AC25:** Category dropdown auto-populates after historical sales upload
- [ ] **AC26:** "Continue to Parameter Extraction" button appears after both uploads complete
- [ ] **AC27:** User cannot proceed to parameter extraction without uploads

### Data Validation

- [ ] **AC28:** System rejects CSV with missing required columns
- [ ] **AC29:** System rejects CSV with wrong data types (shows row number)
- [ ] **AC30:** System rejects CSV with negative values (quantity_sold, revenue)
- [ ] **AC31:** System rejects CSV with invalid dates
- [ ] **AC32:** System rejects CSV with duplicate store_id values
- [ ] **AC33:** System rejects file size > 50MB
- [ ] **AC34:** System provides specific error messages for each validation failure

### Accessibility

- [ ] **AC35:** Upload zones have aria-labels
- [ ] **AC36:** File input has accessible labels
- [ ] **AC37:** Success/error messages have role="status" or role="alert"
- [ ] **AC38:** Keyboard navigation works (Tab, Enter, Escape)
- [ ] **AC39:** Screen reader announces upload progress and results

---

## Tasks

### Task 1: Create Backend Data Upload Service (3 hours)

**File:** `backend/app/services/data_upload_service.py`

**Implementation:**

```python
from sqlalchemy.orm import Session
from app.database.models import HistoricalSales, Store, Category
from app.utils.csv_validator import validate_historical_sales_csv, validate_store_attributes_csv
import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger("fashion_forecast")

class DataUploadService:
    """Service for handling historical data uploads."""

    def __init__(self, db: Session):
        self.db = db

    def upload_historical_sales(self, csv_file) -> Dict:
        """
        Upload and validate historical sales CSV.

        Args:
            csv_file: Uploaded CSV file (multipart/form-data)

        Returns:
            Dict with upload summary and validation results

        Raises:
            ValidationError: If CSV validation fails
        """
        logger.info("Starting historical sales upload")

        # Step 1: Validate CSV format
        df = validate_historical_sales_csv(csv_file)

        # Step 2: Auto-detect categories
        categories_detected = df['category'].unique().tolist()
        logger.info(f"Categories detected: {categories_detected}")

        # Step 3: Clear existing historical sales data
        deleted_count = self.db.query(HistoricalSales).delete()
        logger.info(f"Cleared {deleted_count} existing historical sales rows")

        # Step 4: Insert categories (if new)
        self._insert_categories(categories_detected)

        # Step 5: Batch insert historical sales (1000 rows at a time)
        rows_inserted = self._batch_insert_sales(df)

        # Step 6: Calculate summary statistics
        summary = self._calculate_sales_summary(df)

        logger.info(f"Historical sales upload complete: {rows_inserted} rows inserted")

        return {
            "status": "success",
            "file_name": csv_file.filename,
            "rows_inserted": rows_inserted,
            "categories_detected": categories_detected,
            "date_range": {
                "start": df['date'].min().strftime('%Y-%m-%d'),
                "end": df['date'].max().strftime('%Y-%m-%d')
            },
            "validation_summary": summary,
            "uploaded_at": pd.Timestamp.now().isoformat()
        }

    def upload_store_attributes(self, csv_file) -> Dict:
        """
        Upload and validate store attributes CSV.

        Args:
            csv_file: Uploaded CSV file (multipart/form-data)

        Returns:
            Dict with upload summary and validation results

        Raises:
            ValidationError: If CSV validation fails
        """
        logger.info("Starting store attributes upload")

        # Step 1: Validate CSV format
        df = validate_store_attributes_csv(csv_file)

        # Step 2: Clear existing stores data
        deleted_count = self.db.query(Store).delete()
        logger.info(f"Cleared {deleted_count} existing stores")

        # Step 3: Batch insert stores
        rows_inserted = self._batch_insert_stores(df)

        # Step 4: Calculate summary statistics
        summary = self._calculate_store_summary(df)

        logger.info(f"Store attributes upload complete: {rows_inserted} stores inserted")

        return {
            "status": "success",
            "file_name": csv_file.filename,
            "rows_inserted": rows_inserted,
            "features_validated": 7,
            "clustering_ready": True,
            "store_summary": summary,
            "uploaded_at": pd.Timestamp.now().isoformat()
        }

    def _insert_categories(self, category_names: List[str]):
        """Insert categories if they don't exist."""
        from datetime import date

        existing_categories = {c.category_id for c in self.db.query(Category).all()}

        for category_name in category_names:
            category_id = category_name.lower().replace(" ", "_").replace("'", "")

            if category_id not in existing_categories:
                category = Category(
                    category_id=category_id,
                    category_name=category_name,
                    season_start_date=date(2025, 1, 1),
                    season_end_date=date(2025, 3, 31),
                    season_length_weeks=12,
                    archetype="FASHION_RETAIL",
                    description=f"Auto-detected from historical sales: {category_name}"
                )
                self.db.add(category)

        self.db.commit()

    def _batch_insert_sales(self, df: pd.DataFrame) -> int:
        """Insert historical sales in batches of 1000."""
        batch_size = 1000
        rows_inserted = 0

        sales_records = []
        for _, row in df.iterrows():
            category_clean = row['category'].lower().replace(' ', '_').replace("'", '')
            date_str = row['date'].strftime('%Y%m%d')
            sale_id = f"{row['store_id']}_{category_clean}_{date_str}"

            sale = HistoricalSales(
                sale_id=sale_id,
                week_start_date=row["date"],
                category_id=category_clean,
                store_id=row["store_id"],
                units_sold=int(row["quantity_sold"])
            )
            sales_records.append(sale)

            if len(sales_records) >= batch_size:
                self.db.bulk_save_objects(sales_records)
                self.db.commit()
                rows_inserted += len(sales_records)
                logger.info(f"Inserted batch: {rows_inserted} rows total")
                sales_records = []

        # Insert remaining records
        if sales_records:
            self.db.bulk_save_objects(sales_records)
            self.db.commit()
            rows_inserted += len(sales_records)

        return rows_inserted

    def _batch_insert_stores(self, df: pd.DataFrame) -> int:
        """Insert stores in batch."""
        stores = []
        for _, row in df.iterrows():
            # Normalize values
            fashion_tier = row["fashion_tier"].lower()
            cluster_id = fashion_tier
            store_name = f"Store {row['store_id']}"
            store_format = row["store_format"].upper().replace(" ", "_")
            region = row["region"].upper().replace(" ", "_")

            store = Store(
                store_id=row["store_id"],
                store_name=store_name,
                cluster_id=cluster_id,
                store_size_sqft=int(row["store_size_sqft"]),
                location_tier=row["location_tier"],
                median_income=int(row["median_income"]),
                store_format=store_format,
                region=region,
                avg_weekly_sales_12mo=float(row["avg_weekly_sales_12mo"])
            )
            stores.append(store)

        self.db.bulk_save_objects(stores)
        self.db.commit()

        return len(stores)

    def _calculate_sales_summary(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics for sales data."""
        return {
            "stores_count": df['store_id'].nunique(),
            "total_revenue": float(df['revenue'].sum()) if 'revenue' in df.columns else None,
            "avg_daily_sales_per_store": float(df.groupby('store_id')['quantity_sold'].mean().mean())
        }

    def _calculate_store_summary(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics for store data."""
        return {
            "total_stores": len(df),
            "premium_tier": len(df[df['fashion_tier'] == 'PREMIUM']),
            "mainstream_tier": len(df[df['fashion_tier'] == 'MAINSTREAM']),
            "value_tier": len(df[df['fashion_tier'] == 'VALUE']),
            "avg_store_size_sqft": int(df['store_size_sqft'].mean()),
            "avg_weekly_sales": float(df['avg_weekly_sales_12mo'].mean())
        }
```

**Validation:**
- [ ] Service validates CSV format
- [ ] Service clears existing data before insert
- [ ] Service performs batch inserts
- [ ] Service returns detailed summary
- [ ] Service handles validation errors gracefully

---

### Task 2: Create Backend API Endpoints (2 hours)

**File:** `backend/app/api/v1/endpoints/data_upload.py`

**Implementation:**

```python
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
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
    - At least 1 year of data
    - 50 stores minimum

    **Returns:**
    - Row count
    - Categories detected
    - Date range
    - Validation summary
    """
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .csv files are accepted."
        )

    # Validate file size (max 50MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    max_size = 50 * 1024 * 1024  # 50MB
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {max_size / (1024*1024)}MB"
        )

    try:
        result = service.upload_historical_sales(file.file)
        logger.info(f"Historical sales uploaded: {result['rows_inserted']} rows")
        return result

    except ValidationError as e:
        logger.error(f"Historical sales validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_type": "VALIDATION_ERROR",
                "message": str(e),
                "errors": e.errors if hasattr(e, 'errors') else []
            }
        )

    except Exception as e:
        logger.error(f"Historical sales upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
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
    """
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .csv files are accepted."
        )

    # Validate file size (max 5MB for store attributes)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size = 5 * 1024 * 1024  # 5MB
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {max_size / (1024*1024)}MB"
        )

    try:
        result = service.upload_store_attributes(file.file)
        logger.info(f"Store attributes uploaded: {result['rows_inserted']} stores")
        return result

    except ValidationError as e:
        logger.error(f"Store attributes validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_type": "VALIDATION_ERROR",
                "message": str(e),
                "errors": e.errors if hasattr(e, 'errors') else []
            }
        )

    except Exception as e:
        logger.error(f"Store attributes upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
```

**Add to main router:**

```python
# backend/app/api/v1/api.py

from app.api.v1.endpoints import data_upload

api_router.include_router(
    data_upload.router,
    prefix="/data",
    tags=["data-upload"]
)
```

**Validation:**
- [ ] Endpoints accept multipart/form-data
- [ ] File extension validated (.csv only)
- [ ] File size validated (50MB max for sales, 5MB for stores)
- [ ] Validation errors return 400 with detailed error list
- [ ] Server errors return 500 with error message
- [ ] Success returns 200 with upload summary

---

### Task 3: Create Frontend Upload Component (3-4 hours)

**File:** `frontend/src/components/DataUpload/HistoricalDataUpload.tsx`

**Implementation:**

```typescript
import React, { useState } from 'react';
import { UploadZone } from './UploadZone';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { CheckCircle2, AlertCircle, ChevronRight } from 'lucide-react';
import { DataUploadService } from '@/services/data-upload-service';

interface UploadStatus {
  historical_sales: {
    uploaded: boolean;
    rows?: number;
    categories?: string[];
    date_range?: { start: string; end: string };
  };
  store_attributes: {
    uploaded: boolean;
    rows?: number;
    features_validated?: boolean;
  };
}

export function HistoricalDataUpload({ onComplete }: { onComplete: (categories: string[]) => void }) {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    historical_sales: { uploaded: false },
    store_attributes: { uploaded: false }
  });

  const [error, setError] = useState<string | null>(null);

  const handleHistoricalSalesUpload = async (file: File) => {
    try {
      setError(null);
      const result = await DataUploadService.uploadHistoricalSales(file);

      setUploadStatus(prev => ({
        ...prev,
        historical_sales: {
          uploaded: true,
          rows: result.rows_inserted,
          categories: result.categories_detected,
          date_range: result.date_range
        }
      }));

      // Auto-advance to parameter extraction if both uploads complete
      if (uploadStatus.store_attributes.uploaded && result.categories_detected) {
        onComplete(result.categories_detected);
      }
    } catch (err: any) {
      setError(err.message || 'Historical sales upload failed');
      console.error('Upload error:', err);
    }
  };

  const handleStoreAttributesUpload = async (file: File) => {
    try {
      setError(null);
      const result = await DataUploadService.uploadStoreAttributes(file);

      setUploadStatus(prev => ({
        ...prev,
        store_attributes: {
          uploaded: true,
          rows: result.rows_inserted,
          features_validated: result.clustering_ready
        }
      }));

      // Auto-advance if both uploads complete
      if (uploadStatus.historical_sales.uploaded && uploadStatus.historical_sales.categories) {
        onComplete(uploadStatus.historical_sales.categories);
      }
    } catch (err: any) {
      setError(err.message || 'Store attributes upload failed');
      console.error('Upload error:', err);
    }
  };

  const bothUploadsComplete =
    uploadStatus.historical_sales.uploaded &&
    uploadStatus.store_attributes.uploaded;

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          📊 Data Upload
        </h2>
        <p className="text-sm text-gray-600">
          Upload historical sales data and store attributes to train forecasting models.
          Both uploads are required before proceeding.
        </p>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Two-column upload grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Historical Sales Upload */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">
            Historical Sales Data (2022-2024)
          </h3>
          <UploadZone
            onFileSelect={handleHistoricalSalesUpload}
            fileTypeLabel="Historical Sales CSV"
            acceptedFormat=".csv"
            expectedColumns={['date', 'category', 'store_id', 'quantity_sold', 'revenue']}
            maxSizeMB={50}
          />

          {uploadStatus.historical_sales.uploaded && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-green-900">
                    ✓ {uploadStatus.historical_sales.rows?.toLocaleString()} rows uploaded
                  </p>
                  <p className="text-xs text-green-700 mt-1">
                    Categories: {uploadStatus.historical_sales.categories?.join(', ')}
                  </p>
                  <p className="text-xs text-green-700">
                    Date range: {uploadStatus.historical_sales.date_range?.start} to {uploadStatus.historical_sales.date_range?.end}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Store Attributes Upload */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">
            Store Attributes
          </h3>
          <UploadZone
            onFileSelect={handleStoreAttributesUpload}
            fileTypeLabel="Store Attributes CSV"
            acceptedFormat=".csv"
            expectedColumns={['store_id', 'store_name', 'avg_weekly_sales_12mo', 'store_size_sqft', 'median_income', 'location_tier', 'fashion_tier', 'store_format', 'region']}
            maxSizeMB={5}
          />

          {uploadStatus.store_attributes.uploaded && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-green-900">
                    ✓ {uploadStatus.store_attributes.rows} stores uploaded
                  </p>
                  <p className="text-xs text-green-700 mt-1">
                    7 features validated - Ready for clustering
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Continue button (appears when both uploads complete) */}
      {bothUploadsComplete && (
        <div className="flex justify-center pt-4 border-t">
          <Button
            size="lg"
            onClick={() => onComplete(uploadStatus.historical_sales.categories || [])}
            className="gap-2"
          >
            Continue to Parameter Extraction
            <ChevronRight className="w-5 h-5" />
          </Button>
        </div>
      )}

      {/* Status indicator */}
      {!bothUploadsComplete && (
        <div className="text-center pt-4 border-t">
          <p className="text-sm text-gray-600">
            {uploadStatus.historical_sales.uploaded
              ? '⏳ Waiting for store attributes upload...'
              : uploadStatus.store_attributes.uploaded
              ? '⏳ Waiting for historical sales upload...'
              : '⏳ Waiting for both uploads to complete...'}
          </p>
        </div>
      )}
    </Card>
  );
}
```

**File:** `frontend/src/services/data-upload-service.ts`

```typescript
import { API_CONFIG } from '@/config/api';

export interface HistoricalSalesUploadResponse {
  status: string;
  file_name: string;
  rows_inserted: number;
  categories_detected: string[];
  date_range: {
    start: string;
    end: string;
  };
  validation_summary: {
    stores_count: number;
    total_revenue: number;
    avg_daily_sales_per_store: number;
  };
  uploaded_at: string;
}

export interface StoreAttributesUploadResponse {
  status: string;
  file_name: string;
  rows_inserted: number;
  features_validated: number;
  clustering_ready: boolean;
  store_summary: {
    total_stores: number;
    premium_tier: number;
    mainstream_tier: number;
    value_tier: number;
    avg_store_size_sqft: number;
    avg_weekly_sales: number;
  };
  uploaded_at: string;
}

export class DataUploadService {
  static async uploadHistoricalSales(file: File): Promise<HistoricalSalesUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${API_CONFIG.BASE_URL}/api/v1/data/upload/historical-sales`,
      {
        method: 'POST',
        body: formData
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || 'Upload failed');
    }

    return await response.json();
  }

  static async uploadStoreAttributes(file: File): Promise<StoreAttributesUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${API_CONFIG.BASE_URL}/api/v1/data/upload/store-attributes`,
      {
        method: 'POST',
        body: formData
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || 'Upload failed');
    }

    return await response.json();
  }
}
```

**Validation:**
- [ ] Component displays two upload zones side-by-side
- [ ] Drag-and-drop works for both zones
- [ ] File picker opens on "Browse Files" click
- [ ] Upload progress indicator displays
- [ ] Success state shows row counts and summary
- [ ] Error state shows validation errors
- [ ] "Continue" button appears after both uploads
- [ ] Category list passed to parent component

---

## Definition of Done

- [ ] Backend endpoints created and tested (Postman)
- [ ] DataUploadService handles validation and batch inserts
- [ ] Frontend upload component integrated into Section 0
- [ ] User can upload both CSVs via drag-and-drop or file picker
- [ ] Validation errors displayed with specific row/column details
- [ ] Success messages show upload summary
- [ ] Category dropdown auto-populates after historical sales upload
- [ ] User cannot proceed without both uploads complete
- [ ] Accessibility requirements met (aria-labels, keyboard navigation)
- [ ] Manual testing completed with valid and invalid CSVs
- [ ] No console errors or warnings
- [ ] Code reviewed

---

## Related Stories

- **PRD Story 1.1:** Upload Historical Sales Data
- **PRD Story 1.2:** Upload Store Attributes
- **PHASE4.5-002:** Weekly Actuals Upload (next)
- **PHASE5-004:** Context Assembly (will use database instead of CSV files)

---

**Status:** Not Started
**Branch:** Create new branch `phase4.5-data-upload` from `phase4-integration`
