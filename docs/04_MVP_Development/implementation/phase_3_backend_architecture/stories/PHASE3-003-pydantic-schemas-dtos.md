# Story: Implement Pydantic Schemas (DTOs) for Request/Response Validation

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-003
**Status:** Ready for Review
**Estimate:** 3 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-002 (Database Schema & Models)

---

## Story

As a backend developer,
I want to create Pydantic schema models (DTOs) for API request/response validation,
So that I can ensure type safety, automatic validation, and clear API contracts for all REST endpoints.

**Business Value:** Pydantic schemas provide automatic request/response validation, preventing invalid data from entering the system. They also auto-generate OpenAPI/Swagger documentation, reducing manual documentation work. Type-safe schemas catch bugs at development time rather than runtime.

**Epic Context:** This is Task 3 of 14 in Phase 3. It builds on PHASE3-002 (database models) and enables Task 4 (FastAPI application setup) and Task 5 (Parameter Extraction API). These schemas are the contract between frontend and backend, ensuring data consistency across the full stack.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `backend/app/schemas/` directory created
2. ✅ All Pydantic schema modules implemented:
   - `schemas/parameters.py` (SeasonParameters, ParameterExtractionRequest/Response)
   - `schemas/category.py` (Category, CategoryCreate)
   - `schemas/store.py` (Store, StoreCluster, StoreCreate)
   - `schemas/forecast.py` (Forecast, WeeklyDemand, ClusterDistribution)
   - `schemas/allocation.py` (AllocationPlan, StoreAllocation)
   - `schemas/markdown.py` (MarkdownDecision, MarkdownRequest)
   - `schemas/workflow.py` (WorkflowRequest, WorkflowResponse, AgentStatus)
3. ✅ All schemas have Field descriptions for OpenAPI docs
4. ✅ All schemas have validation rules (ge, le, min_length, etc.)
5. ✅ All schemas have example values in Config class
6. ✅ Enums defined for categorical fields (RetailArchetype, LocationTier, etc.)
7. ✅ Request/Response DTOs separated (Create vs Read models)

### Quality Requirements

8. ✅ All schemas use Python 3.11+ type hints
9. ✅ All numeric fields have appropriate constraints (ge=0, le=1, etc.)
10. ✅ All optional fields properly marked with Optional or None default
11. ✅ All schemas include json_schema_extra examples
12. ✅ No circular imports between schema modules

---

## Tasks

### Task 1: Create Schemas Directory Structure
- [ ] Create `backend/app/schemas/` directory
- [ ] Create `backend/app/schemas/__init__.py`
- [ ] Create placeholder files for all schema modules
- [ ] Verify import structure works

**Expected Structure:**
```
backend/app/schemas/
├── __init__.py
├── parameters.py
├── category.py
├── store.py
├── forecast.py
├── allocation.py
├── markdown.py
└── workflow.py
```

### Task 2: Create Enums Module
- [ ] Create `backend/app/schemas/enums.py`
- [ ] Define all enum types used across schemas:
  - `RetailArchetype` (FASHION_RETAIL, STABLE_CATALOG, CONTINUOUS)
  - `ReplenishmentStrategy` (NONE, WEEKLY, BI_WEEKLY)
  - `LocationTier` (A, B, C)
  - `FashionTier` (PREMIUM, MAINSTREAM, VALUE)
  - `StoreFormat` (MALL, STANDALONE, SHOPPING_CENTER, OUTLET)
  - `Region` (NORTHEAST, SOUTHEAST, MIDWEST, WEST)
  - `MarkdownStatus` (PENDING, APPROVED, APPLIED)
  - `WorkflowStatus` (STARTED, RUNNING, COMPLETED, FAILED)

**Enums Template:**
```python
from enum import Enum

class RetailArchetype(str, Enum):
    """Retail business model archetype"""
    FASHION_RETAIL = "FASHION_RETAIL"
    STABLE_CATALOG = "STABLE_CATALOG"
    CONTINUOUS = "CONTINUOUS"

class ReplenishmentStrategy(str, Enum):
    """Replenishment frequency strategy"""
    NONE = "none"              # One-shot allocation (Zara-style)
    WEEKLY = "weekly"          # Standard retail
    BI_WEEKLY = "bi-weekly"    # Conservative approach

class LocationTier(str, Enum):
    """Store location quality tier"""
    A = "A"  # Prime location
    B = "B"  # Standard location
    C = "C"  # Secondary location

# ... (continue for all enums)
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 386-418

### Task 3: Create Parameters Schemas ⭐ NEW in v3.3
- [ ] Create `schemas/parameters.py`
- [ ] Implement `SeasonParameters` model (5 key parameters)
- [ ] Implement `ParameterExtractionRequest` (natural language input)
- [ ] Implement `ParameterExtractionResponse` (extracted parameters + confidence)
- [ ] Add validation rules for all fields
- [ ] Add example in Config class

**SeasonParameters Schema:**
```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from backend.app.schemas.enums import ReplenishmentStrategy

class SeasonParameters(BaseModel):
    """The 5 key parameters extracted from natural language input"""

    # Parameter 1: Forecast Horizon
    forecast_horizon_weeks: int = Field(
        ...,
        description="How many weeks ahead to forecast (e.g., 12, 26)",
        ge=1,
        le=52,
        example=12
    )

    # Parameter 2: Season Length
    season_start_date: date = Field(
        ...,
        description="Season start date (e.g., 2025-03-01)",
        example="2025-03-01"
    )
    season_end_date: date = Field(
        ...,
        description="Season end date (calculated from horizon)",
        example="2025-05-23"
    )

    # Parameter 3: Replenishment Strategy
    replenishment_strategy: ReplenishmentStrategy = Field(
        ...,
        description="How often to replenish from DC to stores",
        example="none"
    )

    # Parameter 4: DC Holdback Strategy
    dc_holdback_percentage: float = Field(
        ...,
        description="% of inventory to hold at DC for replenishment (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.0
    )

    # Parameter 5: Markdown Timing
    markdown_checkpoint_week: Optional[int] = Field(
        None,
        description="Week to check sell-through and apply markdown (null = no markdowns)",
        ge=1,
        example=6
    )
    markdown_threshold: Optional[float] = Field(
        None,
        description="Sell-through % threshold for markdown (e.g., 0.60 = 60%)",
        ge=0.0,
        le=1.0,
        example=0.60
    )

    # Extraction metadata
    extraction_confidence: str = Field(
        default="medium",
        description="LLM confidence in extraction (high/medium/low)",
        example="high"
    )
    extraction_reasoning: str = Field(
        default="",
        description="LLM explanation of how parameters were extracted",
        example="User explicitly specified all 5 parameters"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "forecast_horizon_weeks": 12,
                "season_start_date": "2025-03-01",
                "season_end_date": "2025-05-23",
                "replenishment_strategy": "none",
                "dc_holdback_percentage": 0.0,
                "markdown_checkpoint_week": 6,
                "markdown_threshold": 0.60,
                "extraction_confidence": "high",
                "extraction_reasoning": "User explicitly specified all 5 parameters"
            }
        }


class ParameterExtractionRequest(BaseModel):
    """Request for natural language parameter extraction"""
    user_input: str = Field(
        ...,
        description="Natural language description of season strategy",
        min_length=10,
        max_length=1000,
        example="I'm planning a 12-week spring fashion season starting March 1st. Send all inventory to stores at launch with no DC holdback. I don't want ongoing replenishment - just one initial allocation. Check for markdown opportunities at week 6 if we're below 60% sell-through."
    )


class ParameterExtractionResponse(BaseModel):
    """Response from parameter extraction"""
    parameters: SeasonParameters = Field(..., description="Extracted parameters")
    success: bool = Field(..., description="Whether extraction succeeded")
    error_message: Optional[str] = Field(None, description="Error if extraction failed")
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 284-377

### Task 4: Create Category Schema
- [ ] Create `schemas/category.py`
- [ ] Implement `Category` model
- [ ] Implement `CategoryCreate` model (for POST requests)
- [ ] Add validation and examples

**Category Schema:**
```python
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from backend.app.schemas.enums import RetailArchetype

class CategoryBase(BaseModel):
    """Base category fields"""
    category_name: str = Field(..., description="Display name (e.g., 'Women's Dresses')", example="Women's Dresses")
    season_start_date: date = Field(..., description="Season start", example="2025-03-01")
    season_end_date: date = Field(..., description="Season end", example="2025-05-23")
    season_length_weeks: int = Field(..., description="Duration in weeks", ge=1, le=52, example=12)
    archetype: RetailArchetype = Field(..., description="Retail archetype", example="FASHION_RETAIL")
    description: Optional[str] = Field(None, description="Optional description", example="Spring 2025 women's dresses collection")


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    category_id: str = Field(..., description="Unique category identifier", example="cat_womens_dresses_spring_2025")


class Category(CategoryBase):
    """Schema for reading a category (includes timestamps)"""
    category_id: str = Field(..., description="Unique category identifier")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True  # Enables ORM mode for SQLAlchemy models
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 380-399

### Task 5: Create Store Schemas
- [ ] Create `schemas/store.py`
- [ ] Implement `StoreCluster` model
- [ ] Implement `Store` model
- [ ] Implement `StoreCreate` model
- [ ] Add validation and examples

**Store Schemas:**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from backend.app.schemas.enums import LocationTier, FashionTier, StoreFormat, Region

class StoreClusterBase(BaseModel):
    """Base store cluster fields"""
    cluster_name: str = Field(..., description="Display name", example="Fashion Forward")
    fashion_tier: FashionTier = Field(..., description="Fashion positioning", example="PREMIUM")
    description: Optional[str] = Field(None, description="Cluster characteristics", example="High-income, fashion-forward customers")


class StoreCluster(StoreClusterBase):
    """Schema for reading a store cluster"""
    cluster_id: str = Field(..., description="Unique cluster ID", example="fashion_forward")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class StoreBase(BaseModel):
    """Base store fields"""
    store_name: str = Field(..., description="Store name", example="Manhattan Fifth Avenue")
    store_size_sqft: int = Field(..., description="Store size in sq ft", ge=1000, le=50000, example=8000)
    location_tier: LocationTier = Field(..., description="A/B/C tier", example="A")
    median_income: int = Field(..., description="Area median income ($)", ge=20000, le=200000, example=95000)
    store_format: StoreFormat = Field(..., description="Store format type", example="MALL")
    region: Region = Field(..., description="Geographic region", example="NORTHEAST")
    avg_weekly_sales_12mo: float = Field(..., description="Historical sales performance", ge=0, example=2500.0)


class StoreCreate(StoreBase):
    """Schema for creating a store"""
    store_id: str = Field(..., description="Unique store identifier", example="S01")
    cluster_id: str = Field(..., description="FK to store_clusters", example="fashion_forward")


class Store(StoreBase):
    """Schema for reading a store"""
    store_id: str = Field(..., description="Unique store identifier")
    cluster_id: str = Field(..., description="FK to store_clusters")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 401-445

### Task 6: Create Forecast Schemas
- [ ] Create `schemas/forecast.py`
- [ ] Implement `WeeklyDemand` model
- [ ] Implement `ClusterDistribution` model
- [ ] Implement `Forecast` model
- [ ] Add validation and examples

**Forecast Schemas:**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class WeeklyDemand(BaseModel):
    """Weekly demand data point"""
    week_number: int = Field(..., ge=1, le=52, description="Week 1-52", example=1)
    demand_units: int = Field(..., ge=0, description="Forecasted units", example=650)


class ClusterDistribution(BaseModel):
    """Cluster allocation breakdown"""
    cluster_id: str = Field(..., description="Cluster identifier", example="fashion_forward")
    cluster_name: str = Field(..., description="Cluster display name", example="Fashion Forward")
    allocation_percentage: float = Field(..., ge=0, le=1, description="% of total demand", example=0.40)
    total_units: int = Field(..., ge=0, description="Total units for cluster", example=3200)


class ForecastBase(BaseModel):
    """Base forecast fields"""
    season: str = Field(..., description="Season identifier", example="Spring 2025")
    forecast_horizon_weeks: int = Field(..., description="Number of weeks", ge=1, le=52, example=12)
    total_season_demand: int = Field(..., ge=0, description="Total units for season", example=8000)
    weekly_demand_curve: List[WeeklyDemand] = Field(..., description="Week-by-week demand")
    peak_week: int = Field(..., ge=1, description="Week with highest demand", example=3)
    cluster_distribution: List[ClusterDistribution] = Field(..., description="Cluster allocations")
    forecasting_method: str = Field(default="ensemble_prophet_arima", description="Method used")
    models_used: List[str] = Field(default=["prophet", "arima"], description="Models in ensemble")
    prophet_forecast: Optional[int] = Field(None, description="Prophet result", example=8200)
    arima_forecast: Optional[int] = Field(None, description="ARIMA result", example=7800)


class Forecast(ForecastBase):
    """Schema for reading a forecast"""
    forecast_id: str = Field(..., description="Unique forecast ID", example="f_spring_2025_womens_dresses")
    category_id: str = Field(..., description="FK to categories", example="cat_womens_dresses")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 448-473

### Task 7: Create Allocation Schemas
- [ ] Create `schemas/allocation.py`
- [ ] Implement `StoreAllocation` model
- [ ] Implement `AllocationPlan` model
- [ ] Add validation and examples

**Allocation Schemas:**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class StoreAllocation(BaseModel):
    """Store-level allocation detail"""
    store_id: str = Field(..., description="Store identifier", example="S01")
    store_name: str = Field(..., description="Store name", example="Manhattan Fifth Avenue")
    cluster_id: str = Field(..., description="Cluster identifier", example="fashion_forward")
    initial_allocation: int = Field(..., ge=0, description="55% initial allocation", example=176)
    holdback_allocation: int = Field(..., ge=0, description="45% DC holdback", example=142)
    total_season_allocation: int = Field(..., ge=0, description="Total for season", example=318)


class AllocationPlanBase(BaseModel):
    """Base allocation plan fields"""
    manufacturing_qty: int = Field(..., ge=0, description="Total to manufacture (with safety stock)", example=9600)
    safety_stock_percentage: float = Field(default=0.20, description="Safety stock %", ge=0, le=1, example=0.20)
    initial_allocation_total: int = Field(..., description="Total 55% to stores", example=5280)
    holdback_total: int = Field(..., description="Total 45% at DC", example=4320)
    store_allocations: List[StoreAllocation] = Field(..., description="Store-level detail")


class AllocationPlan(AllocationPlanBase):
    """Schema for reading an allocation plan"""
    allocation_id: str = Field(..., description="Unique allocation ID", example="alloc_spring_2025")
    forecast_id: str = Field(..., description="FK to forecasts", example="f_spring_2025")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 475-494

### Task 8: Create Markdown Schemas
- [ ] Create `schemas/markdown.py`
- [ ] Implement `MarkdownRequest` model (for user adjustments)
- [ ] Implement `MarkdownDecision` model
- [ ] Add validation and examples

**Markdown Schemas:**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from backend.app.schemas.enums import MarkdownStatus

class MarkdownRequest(BaseModel):
    """Request to apply markdown"""
    forecast_id: str = Field(..., description="Forecast to apply markdown to", example="f_spring_2025")
    week_number: int = Field(..., ge=1, le=12, description="Week to apply markdown", example=6)
    elasticity_coefficient: float = Field(default=2.0, description="Elasticity tuning parameter", ge=1.0, le=3.0, example=2.0)


class MarkdownDecisionBase(BaseModel):
    """Base markdown decision fields"""
    week_number: int = Field(..., ge=1, le=12, description="Week number", example=6)
    sell_through_pct: float = Field(..., ge=0, le=1, description="Actual sell-through %", example=0.55)
    target_sell_through_pct: float = Field(default=0.60, description="Target sell-through %", example=0.60)
    gap_pct: float = Field(..., description="Gap between target and actual", example=0.05)
    recommended_markdown_pct: float = Field(..., ge=0, le=0.40, description="Recommended markdown %", example=0.10)
    elasticity_coefficient: float = Field(default=2.0, description="Elasticity coefficient used", example=2.0)
    expected_demand_lift_pct: Optional[float] = Field(None, description="Expected sales lift %", example=0.18)
    reasoning: Optional[str] = Field(None, description="Agent reasoning for recommendation")


class MarkdownDecision(MarkdownDecisionBase):
    """Schema for reading a markdown decision"""
    markdown_id: str = Field(..., description="Unique markdown ID", example="md_spring_2025_w6")
    forecast_id: str = Field(..., description="FK to forecasts", example="f_spring_2025")
    status: MarkdownStatus = Field(..., description="Markdown status", example="pending")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
```

### Task 9: Create Workflow Schemas
- [ ] Create `schemas/workflow.py`
- [ ] Implement `WorkflowRequest` model
- [ ] Implement `AgentStatus` model
- [ ] Implement `WorkflowResponse` model
- [ ] Add validation and examples

**Workflow Schemas:**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.app.schemas.enums import WorkflowStatus
from backend.app.schemas.parameters import SeasonParameters

class WorkflowRequest(BaseModel):
    """Request to start a forecast workflow"""
    category_id: str = Field(..., description="Category to forecast", example="cat_womens_dresses")
    parameters: SeasonParameters = Field(..., description="Season parameters")


class AgentStatus(BaseModel):
    """Real-time agent status update"""
    agent_name: str = Field(..., description="Agent name", example="Demand Agent")
    status: str = Field(..., description="Status", example="running")
    message: str = Field(..., description="Progress message", example="Running Prophet forecasting model...")
    progress_pct: int = Field(..., ge=0, le=100, description="Progress percentage", example=33)
    timestamp: datetime = Field(..., description="Status timestamp")


class WorkflowResponse(BaseModel):
    """Response from workflow creation"""
    workflow_id: str = Field(..., description="Unique workflow ID", example="wf_2025_10_19_123456")
    status: WorkflowStatus = Field(..., description="Workflow status", example="started")
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates", example="ws://localhost:8000/api/workflows/wf_2025_10_19_123456/stream")
    created_at: datetime = Field(..., description="Creation timestamp")


class WorkflowResult(BaseModel):
    """Final workflow results"""
    workflow_id: str = Field(..., description="Workflow ID")
    status: WorkflowStatus = Field(..., description="Final status")
    forecast_id: str = Field(..., description="Generated forecast ID")
    allocation_id: str = Field(..., description="Generated allocation ID")
    duration_seconds: float = Field(..., description="Total execution time")
    error_message: Optional[str] = Field(None, description="Error if failed")
```

### Task 10: Create Schema Index File
- [ ] Update `backend/app/schemas/__init__.py` to export all schemas
- [ ] Organize exports by module

**schemas/__init__.py:**
```python
# Enums
from backend.app.schemas.enums import (
    RetailArchetype,
    ReplenishmentStrategy,
    LocationTier,
    FashionTier,
    StoreFormat,
    Region,
    MarkdownStatus,
    WorkflowStatus,
)

# Parameters
from backend.app.schemas.parameters import (
    SeasonParameters,
    ParameterExtractionRequest,
    ParameterExtractionResponse,
)

# Category
from backend.app.schemas.category import (
    Category,
    CategoryCreate,
)

# Store
from backend.app.schemas.store import (
    Store,
    StoreCreate,
    StoreCluster,
)

# Forecast
from backend.app.schemas.forecast import (
    Forecast,
    WeeklyDemand,
    ClusterDistribution,
)

# Allocation
from backend.app.schemas.allocation import (
    AllocationPlan,
    StoreAllocation,
)

# Markdown
from backend.app.schemas.markdown import (
    MarkdownDecision,
    MarkdownRequest,
)

# Workflow
from backend.app.schemas.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    AgentStatus,
    WorkflowResult,
)

__all__ = [
    # Enums
    "RetailArchetype",
    "ReplenishmentStrategy",
    "LocationTier",
    "FashionTier",
    "StoreFormat",
    "Region",
    "MarkdownStatus",
    "WorkflowStatus",
    # Parameters
    "SeasonParameters",
    "ParameterExtractionRequest",
    "ParameterExtractionResponse",
    # Category
    "Category",
    "CategoryCreate",
    # Store
    "Store",
    "StoreCreate",
    "StoreCluster",
    # Forecast
    "Forecast",
    "WeeklyDemand",
    "ClusterDistribution",
    # Allocation
    "AllocationPlan",
    "StoreAllocation",
    # Markdown
    "MarkdownDecision",
    "MarkdownRequest",
    # Workflow
    "WorkflowRequest",
    "WorkflowResponse",
    "AgentStatus",
    "WorkflowResult",
]
```

### Task 11: Verify Schema Imports and Examples
- [ ] Test all schema imports: `python -c "from backend.app.schemas import *"`
- [ ] Verify no circular imports
- [ ] Test schema serialization: Create instance, call `.model_dump()`
- [ ] Test schema validation: Pass invalid data, verify ValidationError raised
- [ ] Verify Config.json_schema_extra examples appear in OpenAPI docs

**Verification Script:**
```python
# test_schemas.py
from backend.app.schemas import SeasonParameters, Category, Store, Forecast

# Test SeasonParameters
params = SeasonParameters(
    forecast_horizon_weeks=12,
    season_start_date="2025-03-01",
    season_end_date="2025-05-23",
    replenishment_strategy="none",
    dc_holdback_percentage=0.0,
    markdown_checkpoint_week=6,
    markdown_threshold=0.60,
    extraction_confidence="high"
)
print(params.model_dump())

# Test validation failure
try:
    invalid_params = SeasonParameters(
        forecast_horizon_weeks=100,  # Invalid: exceeds le=52
        season_start_date="2025-03-01",
        season_end_date="2025-05-23",
        replenishment_strategy="none",
        dc_holdback_percentage=0.0
    )
except Exception as e:
    print(f"Validation error caught: {e}")

print("All schema tests passed!")
```

---

## Dev Notes

### Pydantic vs SQLAlchemy Models

**Why Two Sets of Models?**

**SQLAlchemy Models (PHASE3-002):**
- **Purpose**: Database ORM, persistence layer
- **Location**: `backend/app/models/`
- **Usage**: Query database, relationships, transactions
- **Example**: `from backend.app.models import Category`

**Pydantic Schemas (This Story):**
- **Purpose**: API request/response validation, DTOs (Data Transfer Objects)
- **Location**: `backend/app/schemas/`
- **Usage**: Validate incoming requests, serialize responses
- **Example**: `from backend.app.schemas import CategoryCreate`

**Key Differences:**
| Feature | SQLAlchemy Model | Pydantic Schema |
|---------|------------------|-----------------|
| **Persistence** | Yes (writes to DB) | No (validation only) |
| **Relationships** | Yes (ForeignKey, relationship()) | No (flat structure) |
| **Validation** | Minimal (CHECK constraints) | Extensive (Field validators) |
| **API Docs** | No | Yes (auto-generates OpenAPI) |
| **Timestamps** | Yes (created_at, updated_at) | Optional (for responses) |

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 280-550

### Create vs Read Schemas Pattern

**Pattern: Separate schemas for POST (create) and GET (read)**

**Why?**
- **Create (POST)**: User provides data, no timestamps, may include sensitive fields
- **Read (GET)**: Includes timestamps, calculated fields, excludes sensitive data

**Example:**
```python
# CategoryBase: Shared fields
class CategoryBase(BaseModel):
    category_name: str
    season_start_date: date
    # ... common fields

# CategoryCreate: For POST requests (user input)
class CategoryCreate(CategoryBase):
    category_id: str  # User provides ID

# Category: For GET responses (includes timestamps)
class Category(CategoryBase):
    category_id: str
    created_at: datetime  # Auto-populated

    class Config:
        from_attributes = True  # Enables loading from SQLAlchemy models
```

**Benefits:**
- Type safety: Different endpoints have different schemas
- Clear API contracts: Frontend knows exact request/response shape
- Auto-validation: Pydantic rejects invalid requests

### Pydantic Field Validators

**Common Validation Rules:**
| Rule | Purpose | Example |
|------|---------|---------|
| `ge=0` | Greater than or equal | `units: int = Field(..., ge=0)` |
| `le=1` | Less than or equal | `percentage: float = Field(..., le=1)` |
| `min_length=1` | String min length | `name: str = Field(..., min_length=1)` |
| `max_length=100` | String max length | `name: str = Field(..., max_length=100)` |
| `regex="^[A-Z]"` | Regex pattern | `store_id: str = Field(..., regex="^S")` |

**Example with Multiple Validators:**
```python
forecast_horizon_weeks: int = Field(
    ...,
    description="How many weeks ahead to forecast",
    ge=1,       # Must be at least 1
    le=52,      # Must be at most 52
    example=12  # Example value for docs
)
```

### OpenAPI Documentation Auto-Generation

**Pydantic automatically generates OpenAPI/Swagger docs:**

**Example: SeasonParameters in Swagger UI:**
```json
{
  "forecast_horizon_weeks": 12,
  "season_start_date": "2025-03-01",
  "season_end_date": "2025-05-23",
  "replenishment_strategy": "none",
  "dc_holdback_percentage": 0.0,
  "markdown_checkpoint_week": 6,
  "markdown_threshold": 0.60,
  "extraction_confidence": "high",
  "extraction_reasoning": "User explicitly specified all 5 parameters"
}
```

**Field descriptions appear in Swagger UI:**
- Hover over field → Shows Field(description="...")
- Example values → Shows Config.json_schema_extra
- Validation rules → Shows ge, le, min_length constraints

**Access Swagger UI:** `http://localhost:8000/docs` (after FastAPI app running)

### from_attributes = True (ORM Mode)

**Purpose: Load Pydantic models from SQLAlchemy models**

**Without from_attributes:**
```python
# Manual conversion required
db_category = session.query(CategoryModel).first()
category_schema = Category(
    category_id=db_category.category_id,
    category_name=db_category.category_name,
    # ... manually map all fields
)
```

**With from_attributes = True:**
```python
# Automatic conversion
db_category = session.query(CategoryModel).first()
category_schema = Category.from_orm(db_category)  # Pydantic v1
# OR
category_schema = Category.model_validate(db_category)  # Pydantic v2
```

**FastAPI Integration:**
```python
@app.get("/categories/{id}", response_model=Category)
def get_category(id: str, db: Session = Depends(get_db)):
    db_category = db.query(CategoryModel).filter(CategoryModel.category_id == id).first()
    # FastAPI automatically converts SQLAlchemy model to Pydantic schema
    return db_category  # No manual conversion needed!
```

### Enum vs Literal Types

**Why use Enum instead of Literal?**

**Enum (Recommended):**
```python
class LocationTier(str, Enum):
    A = "A"
    B = "B"
    C = "C"

location_tier: LocationTier = Field(...)
```

**Benefits:**
- Auto-complete in IDEs
- Reusable across multiple schemas
- Swagger UI shows dropdown with options
- Type-safe comparisons: `if location_tier == LocationTier.A`

**Literal (Alternative):**
```python
from typing import Literal
location_tier: Literal["A", "B", "C"] = Field(...)
```

**Drawbacks:**
- No auto-complete
- Not reusable
- Error-prone: typos not caught

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 403-418 (Store enums)

### Common Issues & Solutions

**Issue 1: Circular import between schemas**
- Solution: Use string literals for forward references
- Example: `forecast_id: str` instead of `forecast_id: "Forecast"`

**Issue 2: Field default vs Field(...)**
- `Field(...)` = Required field (no default)
- `Field(default=0)` = Optional field with default
- `Field(None)` = Optional field, defaults to None

**Issue 3: Pydantic v1 vs v2 syntax**
- Pydantic v2 (current): `Config.from_attributes = True`, `model_dump()`, `model_validate()`
- Pydantic v1 (old): `Config.orm_mode = True`, `dict()`, `from_orm()`
- Solution: Use Pydantic v2 syntax (specified in pyproject.toml `pydantic>=2.10.0`)

**Issue 4: Validation not working**
- Solution: Ensure `Field(...)` has validators: `ge`, `le`, `min_length`
- Test with invalid data to verify ValidationError raised

**Issue 5: OpenAPI example not showing in Swagger**
- Solution: Add `Config.json_schema_extra` with full example object
- Restart FastAPI server to reload schemas

### Critical References

- **Pydantic Models (Architecture):** `planning/3_technical_architecture_v3.3.md` lines 280-494
- **Implementation Plan:** Task 3, lines 156-175
- **Pydantic v2 Docs:** https://docs.pydantic.dev/latest/
- **FastAPI Request Body:** https://fastapi.tiangolo.com/tutorial/body/
- **OpenAPI Schema:** https://fastapi.tiangolo.com/tutorial/schema-extra-example/

---

## Testing

### Manual Testing Checklist

- [ ] All schema modules import without errors
- [ ] No circular imports detected
- [ ] Valid data passes validation
- [ ] Invalid data raises ValidationError
- [ ] Enum types work correctly
- [ ] Optional fields accept None
- [ ] Field descriptions present
- [ ] Examples present in Config
- [ ] from_attributes = True works with SQLAlchemy models
- [ ] Schemas export from __init__.py

### Verification Commands

```bash
# Navigate to backend directory
cd backend

# Test schema imports
python -c "from backend.app.schemas import *; print('All schemas imported successfully')"

# Test SeasonParameters validation
python -c "
from backend.app.schemas import SeasonParameters
params = SeasonParameters(
    forecast_horizon_weeks=12,
    season_start_date='2025-03-01',
    season_end_date='2025-05-23',
    replenishment_strategy='none',
    dc_holdback_percentage=0.0,
    markdown_checkpoint_week=6,
    markdown_threshold=0.60
)
print('SeasonParameters validation passed')
print(params.model_dump())
"

# Test validation failure (should raise error)
python -c "
from backend.app.schemas import SeasonParameters
try:
    invalid = SeasonParameters(
        forecast_horizon_weeks=100,  # Invalid: exceeds le=52
        season_start_date='2025-03-01',
        season_end_date='2025-05-23',
        replenishment_strategy='none',
        dc_holdback_percentage=0.0
    )
except Exception as e:
    print(f'Validation error correctly caught: {type(e).__name__}')
"

# Test enum validation
python -c "
from backend.app.schemas.enums import LocationTier
print('Enum values:', [e.value for e in LocationTier])
"
```

### Unit Tests (Optional for this story)

```python
# tests/test_schemas/test_parameters.py
import pytest
from pydantic import ValidationError
from backend.app.schemas import SeasonParameters

def test_valid_parameters():
    params = SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date="2025-03-01",
        season_end_date="2025-05-23",
        replenishment_strategy="none",
        dc_holdback_percentage=0.0,
        markdown_checkpoint_week=6,
        markdown_threshold=0.60
    )
    assert params.forecast_horizon_weeks == 12
    assert params.dc_holdback_percentage == 0.0

def test_invalid_horizon_weeks():
    with pytest.raises(ValidationError):
        SeasonParameters(
            forecast_horizon_weeks=100,  # Exceeds le=52
            season_start_date="2025-03-01",
            season_end_date="2025-05-23",
            replenishment_strategy="none",
            dc_holdback_percentage=0.0
        )

def test_invalid_holdback_percentage():
    with pytest.raises(ValidationError):
        SeasonParameters(
            forecast_horizon_weeks=12,
            season_start_date="2025-03-01",
            season_end_date="2025-05-23",
            replenishment_strategy="none",
            dc_holdback_percentage=1.5  # Exceeds le=1.0
        )
```

---

## File List

_Dev Agent will populate this section during implementation_

**Files to Create:**
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/enums.py`
- `backend/app/schemas/parameters.py`
- `backend/app/schemas/category.py`
- `backend/app/schemas/store.py`
- `backend/app/schemas/forecast.py`
- `backend/app/schemas/allocation.py`
- `backend/app/schemas/markdown.py`
- `backend/app/schemas/workflow.py`

**Files to Modify:**
- None (all new files)

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial story creation | Product Owner |
| 2025-10-19 | 1.1 | Added Change Log and QA Results sections for template compliance | Product Owner |

---

## Dev Agent Record

### Agent Model Used

_TBD_

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

---

## Definition of Done

- [ ] `backend/app/schemas/` directory created
- [ ] All 8 schema modules implemented (enums, parameters, category, store, forecast, allocation, markdown, workflow)
- [ ] All schemas have Field descriptions
- [ ] All schemas have validation rules (ge, le, etc.)
- [ ] All schemas have example values in Config
- [ ] Enums defined for all categorical fields
- [ ] Request/Response DTOs separated (Create vs Read)
- [ ] All schemas use Python 3.11+ type hints
- [ ] All numeric fields have appropriate constraints
- [ ] All optional fields properly marked
- [ ] All schemas include json_schema_extra examples
- [ ] No circular imports between modules
- [ ] All schemas import successfully
- [ ] Validation works (invalid data raises ValidationError)
- [ ] Enum types work correctly
- [ ] All verification commands pass

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
**Last Updated:** 2025-10-19 (Implementation completed)
**Story Points:** 3
**Priority:** P0 (Blocker for FastAPI endpoints)
