# PHASE4-008: Integration Tests (Backend + Frontend)

**Story ID:** PHASE4-008
**Story Name:** Create Integration Tests for Frontend/Backend Communication
**Phase:** Phase 4 - Frontend/Backend Integration
**Dependencies:** PHASE4-001 through PHASE4-007
**Estimated Effort:** 8 hours
**Assigned To:** Developer (Testing Focus)
**Status:** Not Started

**Planning References:**
- PRD v3.3: Section 5 (Quality Assurance & Testing Strategy)
- Technical Architecture v3.3: Section 6 (Testing & Deployment)
- All previous story implementations (Stories 1-7)

---

## User Story

**As a** developer maintaining the Multi-Agent Forecasting System,
**I want** comprehensive integration tests for frontend/backend communication,
**So that** I can ensure all endpoints work correctly and catch regressions early.

---

## Context & Background

### What This Story Covers

This story creates integration tests for:

1. **Backend API Integration Tests (pytest):**
   - Parameter extraction endpoint
   - Workflow creation and status
   - WebSocket connection and message flow
   - Forecast, cluster, variance, allocation endpoints
   - Markdown analysis endpoint
   - CSV upload endpoints
   - Error handling and validation

2. **Frontend Integration Tests (Vitest + Testing Library):**
   - API service integration (real API calls with mock server)
   - Component integration with backend data
   - WebSocket connection and message handling
   - CSV upload with validation
   - Error boundary and error handling
   - End-to-end user workflows

### Why Integration Tests Are Critical

Integration tests validate that:
- Frontend and backend communicate correctly
- API contracts are honored (request/response formats)
- Error handling works across the stack
- WebSocket connections remain stable
- CSV uploads are validated properly
- Real-world user workflows complete successfully

### Testing Strategy

**Backend Tests (pytest):**
- Use FastAPI TestClient for HTTP requests
- Use pytest-asyncio for async WebSocket tests
- Mock database interactions (use SQLite in-memory)
- Validate response schemas with Pydantic
- Test error cases (404, 400, 422)

**Frontend Tests (Vitest + Testing Library):**
- Use MSW (Mock Service Worker) to mock API responses
- Test React components with real API integration
- Test WebSocket connection with mock WebSocket server
- Test file upload with FormData
- Test error states and user feedback

---

## Acceptance Criteria

### Backend Integration Tests

- [ ] **AC1:** Test suite created in `backend/tests/integration/`
- [ ] **AC2:** Parameter extraction endpoint tested:
  - Valid user input extracts SeasonParameters
  - Invalid input returns 422 with validation errors
  - Missing required fields handled gracefully
- [ ] **AC3:** Workflow endpoints tested:
  - POST /api/workflows creates workflow with unique ID
  - GET /api/workflows/{id} returns workflow status
  - GET /api/workflows/{id}/status updates as agents progress
- [ ] **AC4:** WebSocket connection tested:
  - Client connects to ws://localhost:8000/api/workflows/{id}/stream
  - 6 message types received (agent_started, agent_progress, etc.)
  - Connection closes gracefully on workflow completion
- [ ] **AC5:** Forecast endpoint tested:
  - GET /api/forecasts/{id} returns ForecastSummary
  - MAPE calculation is correct
  - Manufacturing order calculated correctly
- [ ] **AC6:** Cluster endpoint tested:
  - GET /api/stores/clusters returns 3 clusters (A, B, C)
  - Each cluster has correct store count
  - CSV export endpoint works
- [ ] **AC7:** Variance endpoint tested:
  - GET /api/variance/{id}/week/{week} returns weekly variance
  - Color coding thresholds applied correctly
- [ ] **AC8:** Allocation endpoint tested:
  - GET /api/allocations/{id} returns store-level allocations
  - Conditional display based on replenishment_strategy
- [ ] **AC9:** Markdown endpoint tested:
  - GET /api/markdowns/{id} returns markdown analysis
  - Returns 404 when markdown_checkpoint_week is null
  - Gap × Elasticity calculation is correct
- [ ] **AC10:** CSV upload endpoint tested:
  - Valid CSV uploads successfully
  - Invalid CSV returns validation errors with row/column details
  - File size limit enforced (max 10MB)

### Frontend Integration Tests

- [ ] **AC11:** Test suite created in `frontend/src/tests/integration/`
- [ ] **AC12:** MSW (Mock Service Worker) configured for API mocking
- [ ] **AC13:** ParameterService integration tested:
  - extractParameters sends POST request correctly
  - Response parsed into SeasonParameters
  - Error handling for 422 responses
- [ ] **AC14:** WebSocket integration tested:
  - WebSocketService connects to backend
  - onMessage handler receives all 6 message types
  - Reconnection logic tested (simulated disconnect)
- [ ] **AC15:** ForecastService integration tested:
  - getForecastSummary fetches data correctly
  - Response matches ForecastSummary interface
- [ ] **AC16:** UploadService integration tested:
  - uploadFile sends FormData correctly
  - Validation errors displayed in UI
  - Progress indicator updates during upload
- [ ] **AC17:** Component integration tested:
  - ParameterGathering component submits form and receives workflow_id
  - AgentCards component connects to WebSocket and updates status
  - ForecastSummary component fetches and displays data
  - UploadZone component uploads file and shows success/error

### End-to-End Workflow Tests

- [ ] **AC18:** Full workflow tested (backend + frontend):
  - User enters natural language input
  - Parameters extracted successfully
  - Workflow ID returned
  - WebSocket connection established
  - All 8 sections display data
  - No console errors
- [ ] **AC19:** Error workflow tested:
  - Invalid parameter input shows validation errors
  - 404 responses handled gracefully
  - Network errors display user-friendly messages
- [ ] **AC20:** CSV upload workflow tested:
  - User uploads valid CSV
  - Backend validates and confirms upload
  - User uploads invalid CSV
  - Validation errors displayed with row/column details

---

## Tasks

### Task 1: Set Up Backend Test Environment

**Objective:** Configure pytest and testing dependencies for backend integration tests.

**Subtasks:**

1. **Install Testing Dependencies**
   - File: `backend/pyproject.toml`
   - Add to `[project.optional-dependencies]`:
     ```toml
     [project.optional-dependencies]
     test = [
       "pytest>=7.4.0",
       "pytest-asyncio>=0.21.0",
       "pytest-cov>=4.1.0",
       "httpx>=0.24.0",  # For TestClient
       "websockets>=11.0",  # For WebSocket testing
     ]
     ```
   - Install: `uv pip install -e ".[test]"`

2. **Create Test Configuration**
   - File: `backend/pytest.ini`
     ```ini
     [pytest]
     testpaths = tests
     python_files = test_*.py
     python_classes = Test*
     python_functions = test_*
     asyncio_mode = auto
     addopts = -v --cov=app --cov-report=html --cov-report=term
     ```

3. **Create Test Directory Structure**
   ```
   backend/tests/
   ├── __init__.py
   ├── conftest.py           # Shared fixtures
   ├── integration/
   │   ├── __init__.py
   │   ├── test_parameters.py
   │   ├── test_workflows.py
   │   ├── test_websocket.py
   │   ├── test_forecasts.py
   │   ├── test_clusters.py
   │   ├── test_variance.py
   │   ├── test_allocations.py
   │   ├── test_markdowns.py
   │   └── test_uploads.py
   └── unit/                 # (for future unit tests)
   ```

4. **Create Shared Fixtures**
   - File: `backend/tests/conftest.py`
     ```python
     import pytest
     from fastapi.testclient import TestClient
     from app.main import app
     from app.database import get_db, create_tables
     from sqlalchemy import create_engine
     from sqlalchemy.orm import sessionmaker

     @pytest.fixture
     def client():
         """FastAPI TestClient for HTTP requests"""
         return TestClient(app)

     @pytest.fixture
     def test_db():
         """In-memory SQLite database for testing"""
         engine = create_engine("sqlite:///:memory:")
         create_tables(engine)
         TestingSessionLocal = sessionmaker(bind=engine)
         db = TestingSessionLocal()
         try:
             yield db
         finally:
             db.close()

     @pytest.fixture
     def sample_user_input():
         """Sample user input for parameter extraction"""
         return {
             "user_input": "I need 8000 units over 12 weeks starting Jan 1, 2025. "
                          "Weekly replenishment. 15% DC holdback. "
                          "Markdown checkpoint at week 6 with 40% threshold."
         }

     @pytest.fixture
     def sample_parameters():
         """Sample extracted parameters"""
         return {
             "forecast_horizon_weeks": 12,
             "season_start_date": "2025-01-01",
             "season_end_date": "2025-03-26",
             "replenishment_strategy": "weekly",
             "dc_holdback_percentage": 0.15,
             "markdown_checkpoint_week": 6,
             "markdown_threshold": 0.40,
         }
     ```

**Validation:**
- [ ] pytest installed and configured
- [ ] Test directory structure created
- [ ] conftest.py fixtures work correctly
- [ ] `pytest --collect-only` shows test discovery working

---

### Task 2: Create Backend Parameter Extraction Tests

**Objective:** Test POST /api/parameters/extract endpoint.

**File:** `backend/tests/integration/test_parameters.py`

**Implementation:**

```python
import pytest
from fastapi.testclient import TestClient

def test_parameter_extraction_success(client: TestClient, sample_user_input):
    """Test successful parameter extraction with valid input"""
    response = client.post("/api/parameters/extract", json=sample_user_input)

    assert response.status_code == 200

    data = response.json()
    assert "workflow_id" in data
    assert "parameters" in data

    params = data["parameters"]
    assert params["forecast_horizon_weeks"] == 12
    assert params["season_start_date"] == "2025-01-01"
    assert params["replenishment_strategy"] == "weekly"
    assert params["dc_holdback_percentage"] == 0.15
    assert params["markdown_checkpoint_week"] == 6
    assert params["markdown_threshold"] == 0.40


def test_parameter_extraction_missing_units(client: TestClient):
    """Test parameter extraction fails when units are missing"""
    user_input = {
        "user_input": "I need forecast over 12 weeks starting Jan 1, 2025."
        # Missing: total units
    }

    response = client.post("/api/parameters/extract", json=user_input)

    # Depending on backend implementation, could be 422 or 200 with partial extraction
    assert response.status_code in [200, 422]

    if response.status_code == 422:
        data = response.json()
        assert "detail" in data


def test_parameter_extraction_invalid_json(client: TestClient):
    """Test parameter extraction with malformed JSON"""
    response = client.post(
        "/api/parameters/extract",
        data="not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_parameter_extraction_empty_input(client: TestClient):
    """Test parameter extraction with empty user input"""
    user_input = {"user_input": ""}

    response = client.post("/api/parameters/extract", json=user_input)

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
```

**Validation:**
- [ ] All 4 test cases pass
- [ ] Response schemas validated
- [ ] Error cases return correct HTTP status codes

---

### Task 3: Create Backend WebSocket Tests

**Objective:** Test WebSocket connection and message flow.

**File:** `backend/tests/integration/test_websocket.py`

**Implementation:**

```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from websockets.sync.client import connect

def test_websocket_connection_success(client: TestClient, sample_user_input):
    """Test WebSocket connection and message flow"""
    # First, create a workflow
    response = client.post("/api/parameters/extract", json=sample_user_input)
    assert response.status_code == 200
    workflow_id = response.json()["workflow_id"]

    # Connect to WebSocket
    ws_url = f"ws://localhost:8000/api/workflows/{workflow_id}/stream"

    with connect(ws_url) as websocket:
        # Receive messages
        messages = []
        try:
            for _ in range(10):  # Receive up to 10 messages
                message = websocket.recv(timeout=5)
                messages.append(message)
        except TimeoutError:
            pass  # Normal - workflow completes

        # Validate message types
        message_types = [msg["type"] for msg in messages]
        assert "agent_started" in message_types
        assert "agent_completed" in message_types or "workflow_complete" in message_types


def test_websocket_connection_invalid_workflow(client: TestClient):
    """Test WebSocket connection with invalid workflow ID"""
    ws_url = "ws://localhost:8000/api/workflows/invalid_id_xyz/stream"

    try:
        with connect(ws_url) as websocket:
            # Should fail or close immediately
            message = websocket.recv(timeout=2)
            assert "error" in message or message is None
    except Exception as e:
        # Expected: connection refused or closed
        assert "404" in str(e) or "refused" in str(e)


@pytest.mark.asyncio
async def test_websocket_reconnection(client: TestClient, sample_user_input):
    """Test WebSocket reconnection after disconnect"""
    # Create workflow
    response = client.post("/api/parameters/extract", json=sample_user_input)
    workflow_id = response.json()["workflow_id"]

    ws_url = f"ws://localhost:8000/api/workflows/{workflow_id}/stream"

    # Connect, disconnect, reconnect
    with connect(ws_url) as websocket1:
        message1 = websocket1.recv(timeout=2)
        assert message1 is not None

    # Reconnect
    with connect(ws_url) as websocket2:
        message2 = websocket2.recv(timeout=2)
        assert message2 is not None
        # Should receive messages from where it left off
```

**Validation:**
- [ ] WebSocket connection succeeds for valid workflow_id
- [ ] Messages received have correct types
- [ ] Invalid workflow_id returns error
- [ ] Reconnection works correctly

---

### Task 4: Create Backend Forecast/Cluster/Variance Tests

**Objective:** Test GET endpoints for Sections 2-5.

**File:** `backend/tests/integration/test_forecasts.py`

**Implementation:**

```python
import pytest
from fastapi.testclient import TestClient

def test_forecast_summary_success(client: TestClient, sample_user_input):
    """Test GET /api/forecasts/{id} returns ForecastSummary"""
    # Create workflow
    response = client.post("/api/parameters/extract", json=sample_user_input)
    workflow_id = response.json()["workflow_id"]

    # Fetch forecast summary
    response = client.get(f"/api/forecasts/{workflow_id}")
    assert response.status_code == 200

    data = response.json()
    assert "total_demand" in data
    assert "safety_stock_percentage" in data
    assert "mape_percentage" in data
    assert "manufacturing_order" in data

    # Validate manufacturing order calculation
    total_demand = data["total_demand"]
    safety_stock = data["safety_stock_percentage"]
    dc_holdback = data["dc_holdback_percentage"]

    expected_manufacturing_order = int(
        total_demand * (1 + safety_stock) * (1 + dc_holdback)
    )
    assert data["manufacturing_order"] == expected_manufacturing_order


def test_forecast_summary_not_found(client: TestClient):
    """Test GET /api/forecasts/{id} with invalid workflow ID"""
    response = client.get("/api/forecasts/invalid_id_xyz")
    assert response.status_code == 404


def test_clusters_success(client: TestClient):
    """Test GET /api/stores/clusters returns cluster data"""
    response = client.get("/api/stores/clusters")
    assert response.status_code == 200

    data = response.json()
    assert "clusters" in data
    assert len(data["clusters"]) == 3

    cluster_ids = [c["cluster_id"] for c in data["clusters"]]
    assert "Cluster_A" in cluster_ids
    assert "Cluster_B" in cluster_ids
    assert "Cluster_C" in cluster_ids


def test_variance_by_week_success(client: TestClient, sample_user_input):
    """Test GET /api/variance/{id}/week/{week} returns weekly variance"""
    # Create workflow
    response = client.post("/api/parameters/extract", json=sample_user_input)
    workflow_id = response.json()["workflow_id"]

    # Fetch variance for week 3
    response = client.get(f"/api/variance/{workflow_id}/week/3")
    assert response.status_code == 200

    data = response.json()
    assert "week" in data
    assert data["week"] == 3
    assert "forecast_units" in data
    assert "actual_units" in data
    assert "variance_percentage" in data

    # Validate variance calculation
    forecast = data["forecast_units"]
    actual = data["actual_units"]
    expected_variance = ((actual - forecast) / forecast) * 100
    assert abs(data["variance_percentage"] - expected_variance) < 0.01
```

**File:** `backend/tests/integration/test_allocations.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_allocations_success(client: TestClient, sample_user_input):
    """Test GET /api/allocations/{id} returns allocation data"""
    # Create workflow
    response = client.post("/api/parameters/extract", json=sample_user_input)
    workflow_id = response.json()["workflow_id"]

    # Fetch allocations
    response = client.get(f"/api/allocations/{workflow_id}")
    assert response.status_code == 200

    data = response.json()
    assert "total_units_allocated" in data
    assert "replenishment_strategy" in data
    assert "store_allocations" in data

    # Validate replenishment strategy matches input
    assert data["replenishment_strategy"] == "weekly"


def test_allocations_no_replenishment(client: TestClient):
    """Test allocations with replenishment_strategy = 'none'"""
    user_input = {
        "user_input": "I need 8000 units over 12 weeks starting Jan 1, 2025. "
                     "No replenishment. 15% DC holdback."
    }

    response = client.post("/api/parameters/extract", json=user_input)
    workflow_id = response.json()["workflow_id"]

    response = client.get(f"/api/allocations/{workflow_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["replenishment_strategy"] == "none"
```

**Validation:**
- [ ] All forecast/cluster/variance/allocation tests pass
- [ ] Manufacturing order calculation validated
- [ ] Variance calculation validated
- [ ] 404 returns for invalid workflow IDs

---

### Task 5: Create Backend Markdown and Upload Tests

**Objective:** Test markdown analysis and CSV upload endpoints.

**File:** `backend/tests/integration/test_markdowns.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_markdown_analysis_success(client: TestClient):
    """Test GET /api/markdowns/{id} with markdown checkpoint set"""
    user_input = {
        "user_input": "I need 8000 units over 12 weeks starting Jan 1, 2025. "
                     "Weekly replenishment. 15% DC holdback. "
                     "Markdown checkpoint at week 6 with 40% threshold."
    }

    response = client.post("/api/parameters/extract", json=user_input)
    workflow_id = response.json()["workflow_id"]

    response = client.get(f"/api/markdowns/{workflow_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["markdown_checkpoint_week"] == 6
    assert data["markdown_threshold"] == 0.40
    assert "gap" in data
    assert "elasticity_coefficient" in data
    assert "recommended_markdown_percentage" in data

    # Validate Gap calculation
    gap = data["markdown_threshold"] - data["actual_sell_through"]
    assert abs(data["gap"] - gap) < 0.01


def test_markdown_not_applicable(client: TestClient):
    """Test markdown endpoint returns 404 when checkpoint week is null"""
    user_input = {
        "user_input": "I need 8000 units over 12 weeks starting Jan 1, 2025. "
                     "Weekly replenishment. 15% DC holdback."
        # No markdown checkpoint
    }

    response = client.post("/api/parameters/extract", json=user_input)
    workflow_id = response.json()["workflow_id"]

    response = client.get(f"/api/markdowns/{workflow_id}")
    assert response.status_code == 404
```

**File:** `backend/tests/integration/test_uploads.py`

```python
import pytest
from fastapi.testclient import TestClient
from io import BytesIO

def test_csv_upload_success(client: TestClient, sample_user_input):
    """Test CSV upload with valid file"""
    # Create workflow
    response = client.post("/api/parameters/extract", json=sample_user_input)
    workflow_id = response.json()["workflow_id"]

    # Create valid CSV
    csv_content = b"store_id,week,sales_units,sales_revenue,inventory_on_hand\n"
    csv_content += b"S001,1,150,3750,500\n"
    csv_content += b"S001,2,180,4500,470\n"

    files = {
        "file": ("sales_data.csv", BytesIO(csv_content), "text/csv")
    }
    data = {"file_type": "sales_data"}

    response = client.post(
        f"/api/workflows/{workflow_id}/demand/upload",
        files=files,
        data=data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["validation_status"] == "VALID"
    assert data["rows_uploaded"] == 2


def test_csv_upload_missing_column(client: TestClient, sample_user_input):
    """Test CSV upload with missing required column"""
    response = client.post("/api/parameters/extract", json=sample_user_input)
    workflow_id = response.json()["workflow_id"]

    # CSV missing "sales_units" column
    csv_content = b"store_id,week,sales_revenue,inventory_on_hand\n"
    csv_content += b"S001,1,3750,500\n"

    files = {
        "file": ("sales_data.csv", BytesIO(csv_content), "text/csv")
    }
    data = {"file_type": "sales_data"}

    response = client.post(
        f"/api/workflows/{workflow_id}/demand/upload",
        files=files,
        data=data
    )

    assert response.status_code == 400
    data = response.json()
    assert data["validation_status"] == "INVALID"
    assert len(data["errors"]) > 0
    assert data["errors"][0]["error_type"] == "MISSING_COLUMN"
```

**Validation:**
- [ ] Markdown tests pass (with and without checkpoint)
- [ ] CSV upload tests pass (valid and invalid)
- [ ] Validation errors include row/column details

---

### Task 6: Set Up Frontend Test Environment

**Objective:** Configure Vitest and MSW for frontend integration tests.

**Subtasks:**

1. **Install Testing Dependencies**
   - File: `frontend/package.json`
   - Add dependencies:
     ```json
     {
       "devDependencies": {
         "@testing-library/react": "^14.0.0",
         "@testing-library/jest-dom": "^6.1.0",
         "@testing-library/user-event": "^14.5.0",
         "vitest": "^1.0.0",
         "@vitest/ui": "^1.0.0",
         "msw": "^2.0.0",
         "happy-dom": "^12.0.0"
       }
     }
     ```
   - Install: `npm install`

2. **Create Vitest Configuration**
   - File: `frontend/vitest.config.ts`
     ```typescript
     import { defineConfig } from 'vitest/config';
     import react from '@vitejs/plugin-react';

     export default defineConfig({
       plugins: [react()],
       test: {
         globals: true,
         environment: 'happy-dom',
         setupFiles: './src/tests/setup.ts',
         coverage: {
           provider: 'v8',
           reporter: ['text', 'html'],
         },
       },
     });
     ```

3. **Create MSW Setup**
   - File: `frontend/src/tests/setup.ts`
     ```typescript
     import { beforeAll, afterEach, afterAll } from 'vitest';
     import { server } from './mocks/server';

     beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
     afterEach(() => server.resetHandlers());
     afterAll(() => server.close());
     ```

4. **Create MSW Handlers**
   - File: `frontend/src/tests/mocks/handlers.ts`
     ```typescript
     import { http, HttpResponse } from 'msw';

     export const handlers = [
       // Parameter extraction
       http.post('/api/parameters/extract', () => {
         return HttpResponse.json({
           workflow_id: 'test_wf_123',
           parameters: {
             forecast_horizon_weeks: 12,
             season_start_date: '2025-01-01',
             season_end_date: '2025-03-26',
             replenishment_strategy: 'weekly',
             dc_holdback_percentage: 0.15,
             markdown_checkpoint_week: 6,
             markdown_threshold: 0.40,
           },
         });
       }),

       // Forecast summary
       http.get('/api/forecasts/:id', () => {
         return HttpResponse.json({
           workflow_id: 'test_wf_123',
           total_demand: 8000,
           safety_stock_percentage: 0.20,
           dc_holdback_percentage: 0.15,
           manufacturing_order: 11040,
           mape_percentage: 12.5,
         });
       }),

       // Add more handlers for other endpoints...
     ];
     ```

   - File: `frontend/src/tests/mocks/server.ts`
     ```typescript
     import { setupServer } from 'msw/node';
     import { handlers } from './handlers';

     export const server = setupServer(...handlers);
     ```

5. **Create Test Directory Structure**
   ```
   frontend/src/tests/
   ├── setup.ts
   ├── mocks/
   │   ├── handlers.ts
   │   └── server.ts
   └── integration/
       ├── ParameterService.test.ts
       ├── ForecastService.test.ts
       ├── WebSocketService.test.ts
       ├── UploadService.test.ts
       └── components/
           ├── ParameterGathering.test.tsx
           ├── AgentCards.test.tsx
           ├── ForecastSummary.test.tsx
           └── UploadZone.test.tsx
   ```

**Validation:**
- [ ] Vitest installed and configured
- [ ] MSW setup complete with handlers
- [ ] Test directory structure created
- [ ] `npm run test` runs tests successfully

---

### Task 7: Create Frontend Service Integration Tests

**Objective:** Test API services with MSW mock server.

**File:** `frontend/src/tests/integration/ParameterService.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { ParameterService } from '../../services/parameterService';

describe('ParameterService Integration', () => {
  it('should extract parameters from user input', async () => {
    const userInput = 'I need 8000 units over 12 weeks starting Jan 1, 2025.';

    const response = await ParameterService.extractParameters(userInput);

    expect(response.workflow_id).toBe('test_wf_123');
    expect(response.parameters.forecast_horizon_weeks).toBe(12);
    expect(response.parameters.season_start_date).toBe('2025-01-01');
  });

  it('should handle extraction errors', async () => {
    // Override MSW handler for error case
    server.use(
      http.post('/api/parameters/extract', () => {
        return HttpResponse.json(
          { detail: 'Invalid input' },
          { status: 422 }
        );
      })
    );

    await expect(
      ParameterService.extractParameters('')
    ).rejects.toThrow('Invalid input');
  });
});
```

**File:** `frontend/src/tests/integration/ForecastService.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { ForecastService } from '../../services/forecastService';

describe('ForecastService Integration', () => {
  it('should fetch forecast summary', async () => {
    const workflowId = 'test_wf_123';

    const forecast = await ForecastService.getForecastSummary(workflowId);

    expect(forecast.total_demand).toBe(8000);
    expect(forecast.manufacturing_order).toBe(11040);
  });

  it('should handle 404 errors', async () => {
    server.use(
      http.get('/api/forecasts/:id', () => {
        return HttpResponse.json(
          { detail: 'Workflow not found' },
          { status: 404 }
        );
      })
    );

    await expect(
      ForecastService.getForecastSummary('invalid_id')
    ).rejects.toThrow('Workflow not found');
  });
});
```

**Validation:**
- [ ] ParameterService tests pass
- [ ] ForecastService tests pass
- [ ] Error handling tested for all services
- [ ] MSW intercepts all API calls correctly

---

### Task 8: Create Frontend Component Integration Tests

**Objective:** Test React components with real API integration (mocked with MSW).

**File:** `frontend/src/tests/integration/components/ParameterGathering.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ParameterGathering } from '../../../components/ParameterGathering';

describe('ParameterGathering Component Integration', () => {
  it('should submit user input and extract parameters', async () => {
    const mockOnParametersExtracted = vi.fn();

    render(
      <ParameterGathering onParametersExtracted={mockOnParametersExtracted} />
    );

    const textarea = screen.getByPlaceholderText(/describe your season/i);
    const submitButton = screen.getByRole('button', { name: /extract/i });

    await userEvent.type(textarea, 'I need 8000 units over 12 weeks.');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnParametersExtracted).toHaveBeenCalledWith(
        expect.objectContaining({
          forecast_horizon_weeks: 12,
        }),
        'test_wf_123'
      );
    });
  });

  it('should display error message on extraction failure', async () => {
    server.use(
      http.post('/api/parameters/extract', () => {
        return HttpResponse.json(
          { detail: 'Invalid input' },
          { status: 422 }
        );
      })
    );

    render(<ParameterGathering onParametersExtracted={vi.fn()} />);

    const textarea = screen.getByPlaceholderText(/describe your season/i);
    const submitButton = screen.getByRole('button', { name: /extract/i });

    await userEvent.type(textarea, 'Invalid input');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid input/i)).toBeInTheDocument();
    });
  });
});
```

**File:** `frontend/src/tests/integration/components/UploadZone.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UploadZone } from '../../../components/UploadZone';

describe('UploadZone Component Integration', () => {
  it('should upload CSV file successfully', async () => {
    const mockOnSuccess = vi.fn();

    render(
      <UploadZone
        workflowId="test_wf_123"
        agentType="demand"
        fileType="sales_data"
        fileTypeLabel="Sales Data"
        onUploadSuccess={mockOnSuccess}
        onUploadError={vi.fn()}
      />
    );

    const file = new File(['store_id,week,sales_units\nS001,1,150'], 'sales_data.csv', {
      type: 'text/csv',
    });

    const input = screen.getByLabelText(/browse files/i);
    await userEvent.upload(input, file);

    const uploadButton = screen.getByRole('button', { name: /upload/i });
    await userEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('sales_data.csv', 1);
    });
  });
});
```

**Validation:**
- [ ] ParameterGathering component tests pass
- [ ] UploadZone component tests pass
- [ ] User interactions (type, click, upload) work correctly
- [ ] Error states display correctly

---

### Task 9: Run All Tests and Generate Coverage Reports

**Objective:** Execute full test suite and generate coverage reports.

**Subtasks:**

1. **Run Backend Tests**
   ```bash
   cd backend
   pytest tests/integration/ -v --cov=app --cov-report=html
   ```

   - Expected output:
     ```
     tests/integration/test_parameters.py::test_parameter_extraction_success PASSED
     tests/integration/test_forecasts.py::test_forecast_summary_success PASSED
     tests/integration/test_uploads.py::test_csv_upload_success PASSED
     ... (all tests passing)

     Coverage: 85% (target: >80%)
     ```

2. **Run Frontend Tests**
   ```bash
   cd frontend
   npm run test -- --coverage
   ```

   - Expected output:
     ```
     ✓ tests/integration/ParameterService.test.ts (2 passed)
     ✓ tests/integration/ForecastService.test.ts (2 passed)
     ✓ tests/integration/components/ParameterGathering.test.tsx (2 passed)
     ... (all tests passing)

     Coverage: 75% (target: >70%)
     ```

3. **Generate Coverage Reports**
   - Backend: Open `backend/htmlcov/index.html` in browser
   - Frontend: Open `frontend/coverage/index.html` in browser
   - Review uncovered lines and add tests if needed

4. **Add Test Scripts to package.json / pyproject.toml**
   - Frontend `package.json`:
     ```json
     {
       "scripts": {
         "test": "vitest",
         "test:ui": "vitest --ui",
         "test:coverage": "vitest --coverage"
       }
     }
     ```

   - Backend (pytest already configured in pytest.ini)

**Validation:**
- [ ] All backend tests pass (>80% coverage)
- [ ] All frontend tests pass (>70% coverage)
- [ ] Coverage reports generated successfully
- [ ] No failing tests or warnings

---

## Validation Checklist

### Backend Tests
- [ ] pytest configured with pytest.ini and conftest.py
- [ ] Parameter extraction tests pass (4 test cases)
- [ ] WebSocket tests pass (3 test cases)
- [ ] Forecast/cluster/variance tests pass (4 test cases)
- [ ] Allocation tests pass (2 test cases)
- [ ] Markdown tests pass (2 test cases)
- [ ] CSV upload tests pass (2 test cases)
- [ ] Backend coverage >80%

### Frontend Tests
- [ ] Vitest configured with vitest.config.ts
- [ ] MSW setup complete with handlers
- [ ] ParameterService tests pass (2 test cases)
- [ ] ForecastService tests pass (2 test cases)
- [ ] Component integration tests pass (4 test cases)
- [ ] Error handling tested for all services
- [ ] Frontend coverage >70%

### Coverage & Reporting
- [ ] Backend coverage report generated (htmlcov/index.html)
- [ ] Frontend coverage report generated (coverage/index.html)
- [ ] All critical paths covered (parameter extraction, WebSocket, uploads)
- [ ] Test scripts added to package.json

---

## Definition of Done

- [ ] All 9 tasks completed and validated
- [ ] Backend test suite created with 17+ integration tests
- [ ] Frontend test suite created with 8+ integration tests
- [ ] All tests pass successfully (no failures)
- [ ] Backend coverage >80%
- [ ] Frontend coverage >70%
- [ ] Coverage reports generated and reviewed
- [ ] Test scripts added to package.json and pyproject.toml
- [ ] Code reviewed by team member
- [ ] Documentation updated with testing instructions

---

## Notes

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/integration/ -v
pytest tests/integration/test_parameters.py -v  # Run specific test file
pytest --cov=app --cov-report=html  # With coverage
```

**Frontend:**
```bash
cd frontend
npm run test  # Run all tests
npm run test:ui  # Run tests with UI
npm run test:coverage  # Run tests with coverage
```

### CI/CD Integration

Add to `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          cd backend
          uv pip install -e ".[test]"
      - name: Run tests
        run: |
          cd backend
          pytest tests/integration/ --cov=app

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
```

---

## Related Stories

- **PHASE4-001:** Environment Configuration
- **PHASE4-002:** Section 0 - Parameter Gathering
- **PHASE4-003:** Section 1 - Agent Cards + WebSocket
- **PHASE4-004:** Sections 2-3 - Forecast + Clusters
- **PHASE4-005:** Sections 4-5 - Weekly Chart + Replenishment
- **PHASE4-006:** Sections 6-7 - Markdown + Performance Metrics
- **PHASE4-007:** CSV Upload Workflows
- **PHASE4-009:** Documentation & README Updates (next)
