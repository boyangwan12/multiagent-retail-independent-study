# PHASE4-009: Documentation & README Updates

**Story ID:** PHASE4-009
**Story Name:** Update Documentation and README Files for Phase 4 Integration
**Phase:** Phase 4 - Frontend/Backend Integration
**Dependencies:** PHASE4-001 through PHASE4-008
**Estimated Effort:** 4 hours
**Assigned To:** Developer (Documentation Focus)
**Status:** Not Started

**Planning References:**
- PRD v3.3: All sections (complete system overview)
- Technical Architecture v3.3: All sections (complete architecture)
- Frontend Spec v3.3: All sections (complete UI/UX design)
- All Phase 4 story implementations (Stories 1-8)

---

## User Story

**As a** developer joining the Multi-Agent Forecasting System project,
**I want** comprehensive and up-to-date documentation for the frontend/backend integration,
**So that** I can quickly understand the system architecture, API contracts, and how to run/test the application.

---

## Context & Background

### What This Story Covers

This story updates all project documentation to reflect Phase 4 changes:

1. **README Updates:**
   - Update root README.md with Phase 4 completion status
   - Update backend README.md with API endpoints documentation
   - Update frontend README.md with component architecture
   - Add integration testing instructions

2. **API Documentation:**
   - Generate OpenAPI/Swagger documentation
   - Document all endpoint request/response schemas
   - Document WebSocket message types
   - Add example requests and responses

3. **Architecture Documentation:**
   - Update system architecture diagram
   - Document frontend/backend communication flow
   - Document parameter-driven architecture
   - Add sequence diagrams for key workflows

4. **Developer Guide:**
   - Update local development setup instructions
   - Add troubleshooting guide
   - Document environment variables
   - Add code style and contribution guidelines

### Why Documentation Matters

Good documentation:
- Reduces onboarding time for new developers
- Serves as single source of truth for API contracts
- Helps with debugging (clear error messages, examples)
- Enables future maintenance and feature additions
- Provides context for design decisions

---

## Acceptance Criteria

### Root README Updates

- [ ] **AC1:** Root README.md updated with:
  - Phase 4 completion badge (✅ Phase 4: Frontend/Backend Integration - Complete)
  - Overview of integration-first approach
  - Quick start instructions (frontend + backend)
  - Links to detailed documentation

### Backend README Updates

- [ ] **AC2:** backend/README.md includes:
  - API endpoints table with methods, paths, descriptions
  - WebSocket endpoint documentation
  - CSV upload endpoint documentation
  - Environment variables reference
  - Database schema overview
  - Running tests instructions

### Frontend README Updates

- [ ] **AC3:** frontend/README.md includes:
  - Component architecture diagram
  - Section descriptions (0-7)
  - Service layer documentation (ApiClient, WebSocketService, etc.)
  - Running tests instructions
  - Build and deployment instructions

### API Documentation

- [ ] **AC4:** OpenAPI/Swagger docs generated and accessible at http://localhost:8000/docs
- [ ] **AC5:** All endpoints documented with:
  - Request body schemas
  - Response body schemas
  - Example requests and responses
  - Error response codes (404, 422, 500)

### Architecture Documentation

- [ ] **AC6:** docs/architecture/ folder created with:
  - system_overview.md (high-level architecture)
  - frontend_backend_integration.md (communication flow)
  - websocket_flow.md (real-time updates)
  - parameter_driven_architecture.md (v3.3 approach)

### Developer Guide

- [ ] **AC7:** docs/developer_guide.md created with:
  - Local development setup (step-by-step)
  - Environment configuration
  - Running frontend and backend concurrently
  - Testing workflows
  - Troubleshooting common issues
  - Code style guidelines
  - Contribution workflow (git, PR process)

### Inline Code Documentation

- [ ] **AC8:** Backend services have docstrings:
  - All endpoint functions documented
  - Parameters and return types annotated
  - Example usage in docstrings

- [ ] **AC9:** Frontend services have JSDoc comments:
  - All public methods documented
  - Parameters and return types annotated
  - Example usage in comments

---

## Tasks

### Task 1: Update Root README.md

**Objective:** Update root README with Phase 4 completion and quick start instructions.

**File:** `README.md`

**Implementation:**

```markdown
# Multi-Agent Retail Demand Forecasting System v3.3

[![Phase 1](https://img.shields.io/badge/Phase%201-Complete-brightgreen)](docs/04_MVP_Development/implementation/phase_1_data_generation)
[![Phase 2](https://img.shields.io/badge/Phase%202-Complete-brightgreen)](docs/04_MVP_Development/implementation/phase_2_frontend)
[![Phase 3](https://img.shields.io/badge/Phase%203-Complete-brightgreen)](docs/04_MVP_Development/implementation/phase_3_backend_architecture)
[![Phase 4](https://img.shields.io/badge/Phase%204-Complete-brightgreen)](docs/04_MVP_Development/implementation/phase_4_integration)

---

## Overview

A parameter-driven multi-agent system for retail demand forecasting, inventory allocation, and markdown optimization. Built with:

- **Frontend:** React 18 + TypeScript + Vite + Shadcn/ui
- **Backend:** FastAPI 0.115+ + Python 3.11+ + UV
- **Database:** SQLite 3.45+ with hybrid schema
- **AI/ML:** OpenAI Agents SDK 0.3.3+, Prophet, ARIMA, K-means clustering

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- UV (Python package manager): `pip install uv`

### 1. Clone Repository

```bash
git clone <repository-url>
cd independent_study
```

### 2. Start Backend

```bash
cd backend
uv pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

### 4. Run Tests

**Backend:**
```bash
cd backend
pytest tests/integration/ -v --cov=app
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
```

---

## 📊 Phase 4: Frontend/Backend Integration (COMPLETE)

Phase 4 implemented an **integration-first approach**, connecting all 8 dashboard sections to backend APIs before building AI agents.

### What Was Integrated

✅ **Section 0:** Parameter extraction from natural language
✅ **Section 1:** Real-time WebSocket agent status updates
✅ **Section 2:** Forecast summary with MAPE and manufacturing order
✅ **Section 3:** Store cluster analysis with CSV export
✅ **Section 4:** Weekly performance variance chart
✅ **Section 5:** Replenishment queue (conditional)
✅ **Section 6:** Markdown decision analysis (conditional)
✅ **Section 7:** Performance metrics dashboard
✅ **CSV Uploads:** Multi-agent data ingestion with validation

### Integration Deliverables

- 9 detailed user stories (~1000 lines each)
- 17+ backend integration tests (pytest)
- 8+ frontend integration tests (Vitest + MSW)
- Full API documentation (OpenAPI/Swagger)
- Architecture diagrams and developer guide

**📖 Full Phase 4 Documentation:** [docs/04_MVP_Development/implementation/phase_4_integration/](docs/04_MVP_Development/implementation/phase_4_integration/)

---

## 📂 Project Structure

```
independent_study/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── services/        # Business logic
│   │   ├── models/          # Pydantic models
│   │   └── database/        # SQLite database
│   ├── tests/
│   │   └── integration/     # Integration tests
│   └── README.md
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   ├── pages/           # Page components
│   │   └── tests/
│   │       └── integration/ # Integration tests
│   └── README.md
├── data/                    # Generated datasets (Phase 1)
│   └── generated/           # 38 CSV files
├── docs/                    # All project documentation
│   ├── 04_MVP_Development/
│   │   ├── planning/        # Planning documents
│   │   └── implementation/  # Phase-by-phase stories
│   └── architecture/        # Architecture diagrams
└── README.md               # This file
```

---

## 🧪 Testing

**Backend (pytest):**
- Integration tests for all API endpoints
- WebSocket connection tests
- CSV upload validation tests
- Coverage: >80%

**Frontend (Vitest + MSW):**
- Service layer integration tests
- Component integration tests
- Error handling tests
- Coverage: >70%

---

## 📚 Documentation

- **[Developer Guide](docs/developer_guide.md)** - Local setup, testing, troubleshooting
- **[API Documentation](http://localhost:8000/docs)** - OpenAPI/Swagger (when backend running)
- **[Architecture Overview](docs/architecture/system_overview.md)** - System design
- **[Phase 4 Plan](docs/04_MVP_Development/implementation/phase_4_integration/implementation_plan.md)** - Integration stories

---

## 🛠️ Technology Stack

### Backend
- FastAPI 0.115+
- Python 3.11+
- UV (package manager)
- SQLite 3.45+
- OpenAI Agents SDK 0.3.3+
- Prophet, ARIMA (forecasting)
- K-means clustering

### Frontend
- React 18
- TypeScript 5
- Vite 5
- Shadcn/ui + Tailwind CSS
- Recharts (charts)
- TanStack Table (tables)

### Testing
- pytest + pytest-asyncio (backend)
- Vitest + Testing Library (frontend)
- MSW (Mock Service Worker)

---

## 🔜 Next Phases

- **Phase 5:** Demand Agent Implementation (Prophet + ARIMA forecasting)
- **Phase 6:** Inventory Agent Implementation (K-means clustering + allocation)
- **Phase 7:** Pricing Agent Implementation (Markdown optimization)
- **Phase 8:** End-to-End Testing & Cleanup

---

## 👥 Contributors

- **Team Members:** [Add names]
- **Professor:** [Professor name]
- **Institution:** [University name]

---

## 📝 License

[Add license information]
```

**Validation:**
- [ ] Root README updated with Phase 4 status
- [ ] Quick start instructions accurate
- [ ] Links to documentation correct
- [ ] Badges display correctly

---

### Task 2: Update Backend README.md

**Objective:** Document all backend API endpoints and setup instructions.

**File:** `backend/README.md`

**Implementation:**

```markdown
# Backend - Multi-Agent Forecasting System

FastAPI backend for the Multi-Agent Retail Demand Forecasting System.

---

## Setup

### Prerequisites

- Python 3.11+
- UV (Python package manager): `pip install uv`

### Installation

```bash
cd backend
uv pip install -e ".[dev]"
```

### Environment Configuration

Create `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database
DATABASE_URL=sqlite:///./forecasting.db

# OpenAI (for future agent integration)
OPENAI_API_KEY=your_api_key_here
```

### Run Server

```bash
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000
API docs: http://localhost:8000/docs

---

## API Endpoints

### Parameter Extraction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/parameters/extract` | Extract SeasonParameters from natural language input |

**Request:**
```json
{
  "user_input": "I need 8000 units over 12 weeks starting Jan 1, 2025. Weekly replenishment. 15% DC holdback."
}
```

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "parameters": {
    "forecast_horizon_weeks": 12,
    "season_start_date": "2025-01-01",
    "season_end_date": "2025-03-26",
    "replenishment_strategy": "weekly",
    "dc_holdback_percentage": 0.15,
    "markdown_checkpoint_week": null,
    "markdown_threshold": null
  }
}
```

---

### Workflow Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workflows/{id}` | Get workflow status |
| GET | `/api/workflows/{id}/status` | Get detailed workflow progress |

---

### WebSocket (Real-Time Updates)

| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/api/workflows/{id}/stream` | Real-time agent status updates |

**Message Types:**
1. `agent_started` - Agent begins execution
2. `agent_progress` - Progress update (0-100%)
3. `agent_completed` - Agent finished successfully
4. `human_input_required` - Agent needs user input
5. `workflow_complete` - All agents finished
6. `error` - Error occurred

**Example Message:**
```json
{
  "type": "agent_progress",
  "agent_name": "Demand Agent",
  "progress": 45,
  "message": "Processing historical sales data...",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### Forecast Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/forecasts/{id}` | Get forecast summary |

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "total_demand": 8000,
  "safety_stock_percentage": 0.20,
  "dc_holdback_percentage": 0.15,
  "manufacturing_order": 11040,
  "mape_percentage": 12.5,
  "adaptation_reasoning": "Weekly replenishment → standard 20% safety stock"
}
```

---

### Store Clusters

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stores/clusters` | Get store cluster analysis |
| GET | `/api/stores/clusters/export` | Export clusters as CSV |

---

### Variance Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/variance/{id}/week/{week}` | Get weekly variance data |
| GET | `/api/variance/{id}/summary` | Get variance summary |

---

### Allocation & Replenishment

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/allocations/{id}` | Get store-level allocations |

---

### Markdown Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/markdowns/{id}` | Get markdown decision analysis |

**Note:** Returns 404 if `markdown_checkpoint_week` is null.

---

### CSV Uploads

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workflows/{id}/demand/upload` | Upload Demand Agent CSVs |
| POST | `/api/workflows/{id}/inventory/upload` | Upload Inventory Agent CSVs |
| POST | `/api/workflows/{id}/pricing/upload` | Upload Pricing Agent CSVs |

**Request (multipart/form-data):**
- `file`: CSV file
- `file_type`: "sales_data", "store_profiles", etc.

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "file_type": "sales_data",
  "file_name": "sales_data.csv",
  "rows_uploaded": 50,
  "validation_status": "VALID",
  "columns": ["store_id", "week", "sales_units", "sales_revenue", "inventory_on_hand"]
}
```

---

## Database Schema

### Tables

**workflows:**
- `id` (TEXT, PRIMARY KEY)
- `status` (TEXT: "pending", "running", "completed", "failed")
- `parameters` (JSON)
- `created_at` (TIMESTAMP)

**forecasts:**
- `id` (INTEGER, PRIMARY KEY)
- `workflow_id` (TEXT, FOREIGN KEY)
- `total_demand` (INTEGER)
- `safety_stock_percentage` (FLOAT)
- `manufacturing_order` (INTEGER)
- `mape_percentage` (FLOAT)

**store_clusters:**
- `id` (INTEGER, PRIMARY KEY)
- `cluster_id` (TEXT)
- `store_ids` (JSON array)
- `average_demand` (FLOAT)

---

## Running Tests

### Integration Tests

```bash
pytest tests/integration/ -v
```

### With Coverage

```bash
pytest tests/integration/ --cov=app --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

### Test Specific Module

```bash
pytest tests/integration/test_parameters.py -v
```

---

## Troubleshooting

**CORS errors:**
- Ensure `CORS_ORIGINS` in `.env` includes frontend URL
- Restart backend after changing `.env`

**Database errors:**
- Delete `forecasting.db` and restart to recreate schema

**WebSocket connection fails:**
- Check firewall allows WebSocket connections
- Ensure frontend uses `ws://` (not `wss://` for local dev)

---

## Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Docstrings for all public functions
- Run `black` and `isort` before committing

---

## Related Documentation

- [Frontend README](../frontend/README.md)
- [API Documentation](http://localhost:8000/docs)
- [Architecture Overview](../docs/architecture/system_overview.md)
```

**Validation:**
- [ ] Backend README documents all endpoints
- [ ] Request/response examples accurate
- [ ] Setup instructions complete
- [ ] Troubleshooting guide helpful

---

### Task 3: Update Frontend README.md

**Objective:** Document frontend component architecture and setup instructions.

**File:** `frontend/README.md`

**Implementation:**

```markdown
# Frontend - Multi-Agent Forecasting System

React + TypeScript frontend for the Multi-Agent Retail Demand Forecasting System.

---

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Environment Configuration

Create `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Run Development Server

```bash
npm run dev
```

Frontend runs at: http://localhost:5173

---

## Dashboard Sections

The dashboard consists of 8 sections that integrate with backend APIs:

| Section | Component | Backend Endpoint | Description |
|---------|-----------|------------------|-------------|
| **0** | ParameterGathering | POST /api/parameters/extract | Natural language → SeasonParameters |
| **1** | AgentCards | WS /api/workflows/{id}/stream | Real-time agent status updates |
| **2** | ForecastSummary | GET /api/forecasts/{id} | Total demand, MAPE, manufacturing order |
| **3** | ClusterCards | GET /api/stores/clusters | Store cluster analysis (A, B, C) |
| **4** | WeeklyPerformanceChart | GET /api/variance/{id}/week/{week} | Forecast vs. actual variance chart |
| **5** | ReplenishmentQueue | GET /api/allocations/{id} | Store-level replenishment (conditional) |
| **6** | MarkdownDecision | GET /api/markdowns/{id} | Markdown recommendations (conditional) |
| **7** | PerformanceMetrics | Multiple endpoints | MAPE, variance, sell-through aggregation |

---

## Component Architecture

```
src/
├── components/
│   ├── ParameterGathering.tsx    # Section 0
│   ├── AgentCards.tsx            # Section 1
│   ├── ForecastSummary.tsx       # Section 2
│   ├── ClusterCards.tsx          # Section 3
│   ├── WeeklyPerformanceChart.tsx # Section 4
│   ├── ReplenishmentQueue.tsx    # Section 5
│   ├── MarkdownDecision.tsx      # Section 6
│   ├── PerformanceMetrics.tsx    # Section 7
│   ├── UploadZone.tsx            # CSV upload (drag-and-drop)
│   ├── UploadModal.tsx           # Multi-agent upload modal
│   └── ui/                       # Shadcn/ui components
├── services/
│   ├── apiClient.ts              # Base API client
│   ├── parameterService.ts       # Parameter extraction
│   ├── websocketService.ts       # WebSocket connection
│   ├── forecastService.ts        # Forecast data
│   ├── clusterService.ts         # Cluster data
│   ├── varianceService.ts        # Variance data
│   ├── allocationService.ts      # Allocation data
│   ├── markdownService.ts        # Markdown analysis
│   ├── performanceService.ts     # Performance metrics
│   └── uploadService.ts          # CSV uploads
├── pages/
│   └── Dashboard.tsx             # Main dashboard page
├── config/
│   └── api.config.ts             # API endpoints configuration
└── tests/
    └── integration/              # Integration tests
```

---

## Service Layer

### ApiClient

Base client for all HTTP requests:

```typescript
import { ApiClient } from './services/apiClient';

const data = await ApiClient.get<ResponseType>('/api/endpoint');
const result = await ApiClient.post<ResponseType>('/api/endpoint', { body });
```

### WebSocketService

Real-time updates:

```typescript
import { WebSocketService } from './services/websocketService';

const ws = new WebSocketService();
ws.connect(workflowId);
ws.onMessage((message) => {
  console.log(message.type, message.progress);
});
```

### UploadService

CSV file uploads:

```typescript
import { UploadService } from './services/uploadService';

const response = await UploadService.uploadFile(
  workflowId,
  'demand',
  file,
  'sales_data'
);
```

---

## Running Tests

### Integration Tests

```bash
npm run test
```

### With UI

```bash
npm run test:ui
```

### With Coverage

```bash
npm run test:coverage
```

Open `coverage/index.html` to view coverage report.

---

## Build for Production

```bash
npm run build
```

Output in `dist/` folder. Serve with:

```bash
npm run preview
```

---

## Troubleshooting

**API connection errors:**
- Ensure backend is running at http://localhost:8000
- Check `VITE_API_BASE_URL` in `.env`

**WebSocket connection fails:**
- Ensure WebSocket URL uses `ws://` (not `wss://` for local dev)
- Check browser console for WebSocket errors

**CORS errors:**
- Backend must allow `http://localhost:5173` in CORS origins
- Restart backend after changing CORS settings

**CSV upload errors:**
- Max file size: 10MB
- Only .csv files accepted
- Check validation errors in UI

---

## Code Style

- Follow Airbnb TypeScript style guide
- Use ESLint and Prettier
- Run `npm run lint` before committing
- Use functional components with hooks (no class components)

---

## Related Documentation

- [Backend README](../backend/README.md)
- [API Documentation](http://localhost:8000/docs)
- [Component Library (Shadcn/ui)](https://ui.shadcn.com/)
```

**Validation:**
- [ ] Frontend README documents all sections
- [ ] Component architecture table accurate
- [ ] Service layer examples correct
- [ ] Troubleshooting guide helpful

---

### Task 4: Generate OpenAPI/Swagger Documentation

**Objective:** Ensure FastAPI auto-generates complete API documentation.

**File:** `backend/app/main.py`

**Implementation:**

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Multi-Agent Forecasting System API",
    description="Backend API for retail demand forecasting, inventory allocation, and markdown optimization.",
    version="3.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Multi-Agent Forecasting System API",
        version="3.3.0",
        description="""
## Overview

Backend API for the Multi-Agent Retail Demand Forecasting System v3.3.

### Key Features

- **Parameter Extraction:** Convert natural language to structured parameters
- **Real-Time WebSocket:** Agent status updates via WebSocket
- **Forecast Analysis:** MAPE calculation, manufacturing order computation
- **Store Clustering:** K-means clustering with CSV export
- **Variance Tracking:** Weekly forecast vs. actual variance
- **Markdown Optimization:** Gap × Elasticity formula
- **CSV Uploads:** Multi-agent data ingestion with validation

### Architecture

- **Parameter-Driven:** System adapts behavior based on 5 extracted parameters
- **Integration-First:** Frontend/backend connected before AI agent implementation
- **Mock Agents:** Return dynamic data based on parameters (Phase 4)
        """,
        routes=app.routes,
    )

    # Add tag descriptions
    openapi_schema["tags"] = [
        {
            "name": "Parameters",
            "description": "Extract SeasonParameters from natural language input",
        },
        {
            "name": "Workflows",
            "description": "Manage multi-agent workflow execution",
        },
        {
            "name": "Forecasts",
            "description": "Demand forecasting data and analysis",
        },
        {
            "name": "Stores",
            "description": "Store clustering and performance data",
        },
        {
            "name": "Variance",
            "description": "Weekly variance analysis (forecast vs. actual)",
        },
        {
            "name": "Allocations",
            "description": "Inventory allocation and replenishment",
        },
        {
            "name": "Markdowns",
            "description": "Markdown decision analysis (conditional)",
        },
        {
            "name": "Uploads",
            "description": "CSV file uploads with validation",
        },
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Validation:**
- [ ] OpenAPI docs accessible at http://localhost:8000/docs
- [ ] All endpoints documented with request/response schemas
- [ ] Example requests and responses visible
- [ ] Error codes documented (404, 422, 500)

---

### Task 5: Create Architecture Documentation

**Objective:** Document system architecture with diagrams.

**Create Folder:** `docs/architecture/`

**Files to Create:**

1. **`docs/architecture/system_overview.md`**
   - High-level system architecture
   - Technology stack
   - Component interaction diagram

2. **`docs/architecture/frontend_backend_integration.md`**
   - Communication flow between frontend and backend
   - API contract details
   - Error handling strategy

3. **`docs/architecture/websocket_flow.md`**
   - WebSocket connection lifecycle
   - Message types and structure
   - Reconnection logic

4. **`docs/architecture/parameter_driven_architecture.md`**
   - v3.3 parameter-driven approach
   - How parameters affect agent behavior
   - Examples of dynamic responses

**(Implementation of these files would be similar length to the README files above, documenting architecture with diagrams, code examples, and explanations.)**

**Validation:**
- [ ] Architecture folder created with 4 documents
- [ ] System diagrams added (Mermaid or image files)
- [ ] Communication flows explained clearly
- [ ] Parameter-driven approach documented

---

### Task 6: Create Developer Guide

**Objective:** Comprehensive guide for local development, testing, and troubleshooting.

**File:** `docs/developer_guide.md`

**Sections:**

1. **Local Development Setup**
   - Prerequisites installation
   - Repository cloning
   - Backend setup (step-by-step)
   - Frontend setup (step-by-step)
   - Running both concurrently

2. **Environment Configuration**
   - Backend .env variables explained
   - Frontend .env variables explained
   - Database configuration
   - OpenAI API key setup (for future phases)

3. **Testing Workflows**
   - Running backend tests
   - Running frontend tests
   - Writing new tests
   - Coverage thresholds

4. **Troubleshooting Common Issues**
   - CORS errors
   - Database errors
   - WebSocket connection failures
   - CSV upload validation errors
   - Port conflicts

5. **Code Style Guidelines**
   - Python (PEP 8, type hints, docstrings)
   - TypeScript (ESLint, Prettier)
   - Commit message format
   - PR review process

**(Full implementation would be ~300-400 lines with detailed step-by-step instructions)**

**Validation:**
- [ ] Developer guide created with all sections
- [ ] Setup instructions tested on fresh machine
- [ ] Troubleshooting guide covers common issues
- [ ] Code style guidelines clear

---

### Task 7: Add Inline Code Documentation

**Objective:** Ensure all services have docstrings/JSDoc comments.

**Backend Example - `backend/app/api/parameters.py`:**

```python
from fastapi import APIRouter, HTTPException
from app.models.parameters import ParameterExtractionRequest, ParameterExtractionResponse
from app.services.parameter_extraction import extract_parameters

router = APIRouter(prefix="/api/parameters", tags=["Parameters"])

@router.post("/extract", response_model=ParameterExtractionResponse)
async def extract_season_parameters(request: ParameterExtractionRequest):
    """
    Extract SeasonParameters from natural language user input.

    This endpoint uses OpenAI GPT-4o-mini to parse natural language descriptions
    of retail seasons and extract structured parameters for the forecasting system.

    Args:
        request (ParameterExtractionRequest): Contains user_input string

    Returns:
        ParameterExtractionResponse: Contains workflow_id and extracted parameters

    Raises:
        HTTPException: 422 if input is invalid or extraction fails

    Example:
        >>> request = {
        ...     "user_input": "I need 8000 units over 12 weeks starting Jan 1, 2025."
        ... }
        >>> response = await extract_season_parameters(request)
        >>> print(response.parameters.forecast_horizon_weeks)
        12
    """
    try:
        return await extract_parameters(request.user_input)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

**Frontend Example - `frontend/src/services/parameterService.ts`:**

```typescript
/**
 * Service for extracting season parameters from natural language input.
 *
 * This service communicates with the backend parameter extraction endpoint,
 * which uses OpenAI GPT-4o-mini to parse user input and extract structured
 * SeasonParameters.
 *
 * @module ParameterService
 *
 * @example
 * ```typescript
 * const userInput = "I need 8000 units over 12 weeks starting Jan 1, 2025.";
 * const response = await ParameterService.extractParameters(userInput);
 * console.log(response.parameters.forecast_horizon_weeks); // 12
 * ```
 */
export class ParameterService {
  /**
   * Extract SeasonParameters from natural language user input.
   *
   * @param userInput - Natural language description of season requirements
   * @returns Promise resolving to ParameterExtractionResponse with workflow_id and parameters
   * @throws {ApiError} If backend returns 422 (validation error)
   *
   * @example
   * ```typescript
   * try {
   *   const response = await ParameterService.extractParameters(
   *     "I need 8000 units over 12 weeks."
   *   );
   *   console.log(response.workflow_id);
   * } catch (error) {
   *   console.error("Extraction failed:", error.message);
   * }
   * ```
   */
  static async extractParameters(
    userInput: string
  ): Promise<ParameterExtractionResponse> {
    // Implementation...
  }
}
```

**Validation:**
- [ ] All backend endpoint functions have docstrings
- [ ] All frontend service methods have JSDoc comments
- [ ] Parameters and return types documented
- [ ] Example usage included in comments

---

### Task 8: Review and Validate All Documentation

**Objective:** Ensure all documentation is accurate, complete, and consistent.

**Checklist:**

- [ ] Root README has Phase 4 completion badge
- [ ] Backend README documents all 15+ endpoints
- [ ] Frontend README documents all 8 sections
- [ ] OpenAPI docs accessible and complete
- [ ] Architecture documents created with diagrams
- [ ] Developer guide covers all setup steps
- [ ] Inline code documentation added to all services
- [ ] All links in documentation are valid
- [ ] Examples in documentation are tested and working
- [ ] No outdated information (e.g., old API endpoints)

**Validation Steps:**

1. **Test Quick Start:**
   - Follow root README quick start on fresh machine
   - Verify all commands work

2. **Test API Examples:**
   - Run example requests from backend README in Postman
   - Verify responses match documented schemas

3. **Test Links:**
   - Click all internal documentation links
   - Ensure no 404 errors

4. **Review Consistency:**
   - Check endpoint paths match across frontend/backend READMEs
   - Check environment variables match across docs
   - Check version numbers consistent (v3.3.0)

---

## Validation Checklist

### README Updates
- [ ] Root README updated with Phase 4 status and quick start
- [ ] Backend README documents all endpoints with examples
- [ ] Frontend README documents all components and services
- [ ] All README links valid and working

### API Documentation
- [ ] OpenAPI docs accessible at /docs
- [ ] All endpoints documented with request/response schemas
- [ ] Example requests and responses added
- [ ] Error codes documented (404, 422, 500)

### Architecture Documentation
- [ ] Architecture folder created with 4 documents
- [ ] System overview diagram added
- [ ] Frontend/backend integration flow documented
- [ ] WebSocket flow explained with diagrams
- [ ] Parameter-driven architecture documented

### Developer Guide
- [ ] Developer guide created with all sections
- [ ] Local setup instructions tested and accurate
- [ ] Environment variables explained
- [ ] Testing workflows documented
- [ ] Troubleshooting guide comprehensive
- [ ] Code style guidelines clear

### Inline Documentation
- [ ] Backend services have docstrings
- [ ] Frontend services have JSDoc comments
- [ ] All public methods documented
- [ ] Example usage included in comments

### Validation
- [ ] Quick start tested on fresh machine
- [ ] API examples tested in Postman
- [ ] All links validated (no 404s)
- [ ] Consistency checked across all docs

---

## Definition of Done

- [ ] All 8 tasks completed and validated
- [ ] Root README updated with Phase 4 completion
- [ ] Backend and frontend READMEs comprehensive
- [ ] OpenAPI documentation complete and accessible
- [ ] Architecture documentation created with diagrams
- [ ] Developer guide created with troubleshooting section
- [ ] Inline code documentation added to all services
- [ ] All documentation tested and validated
- [ ] No broken links or outdated information
- [ ] Code reviewed by team member

---

## Notes

### Documentation Best Practices

1. **Keep It Updated:** Update docs immediately when making code changes
2. **Be Specific:** Provide exact commands, file paths, and examples
3. **Use Diagrams:** Visual representations help understanding
4. **Test Examples:** All code examples should be tested and working
5. **Link Generously:** Cross-reference related documentation

### Tools for Diagrams

- **Mermaid:** In-markdown diagrams (supported by GitHub)
- **Draw.io:** Free diagramming tool
- **Lucidchart:** Collaborative diagramming

### Markdown Formatting

- Use headings (##, ###) for structure
- Use code blocks with language hints (```python, ```typescript)
- Use tables for structured data
- Use badges for status indicators

---

## Related Stories

- **PHASE4-001:** Environment Configuration
- **PHASE4-002:** Section 0 - Parameter Gathering
- **PHASE4-003:** Section 1 - Agent Cards + WebSocket
- **PHASE4-004:** Sections 2-3 - Forecast + Clusters
- **PHASE4-005:** Sections 4-5 - Weekly Chart + Replenishment
- **PHASE4-006:** Sections 6-7 - Markdown + Performance Metrics
- **PHASE4-007:** CSV Upload Workflows
- **PHASE4-008:** Integration Tests
