# Fashion Forecast Backend

Multi-Agent Retail Forecasting System - FastAPI Backend

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (get one at https://platform.openai.com/api-keys)

### Installation

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   # Or if you have uv: uv sync
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Seed database with mock data:**
   ```bash
   python scripts/seed_db.py --data-dir ../data/mock/training
   ```

4. **Start development server:**
   ```bash
   ./scripts/dev.sh  # Linux/Mac
   # OR
   .\scripts\dev.bat  # Windows
   # OR manually:
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Verify installation:**
   - Health check: http://localhost:8000/api/v1/health
   - API docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📚 API Documentation

### Interactive Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Core Endpoints

**Health Check:**
```bash
GET /api/v1/health
```

**Parameter Extraction:**
```bash
POST /api/v1/parameters/extract
Content-Type: application/json

{
  "user_input": "12-week Spring 2025 season starting March 3rd with weekly replenishment",
  "category_id": "womens_blouses"
}
```

**Category Management:**
```bash
GET  /api/v1/categories           # List all categories
POST /api/v1/categories           # Create new category
GET  /api/v1/categories/{id}      # Get category details
PUT  /api/v1/categories/{id}      # Update category
DELETE /api/v1/categories/{id}    # Delete category
```

**Store Management:**
```bash
GET /api/v1/stores                # List all stores
GET /api/v1/stores/{id}           # Get store details
GET /api/v1/stores/clusters       # List store clusters
```

**Historical Sales:**
```bash
GET /api/v1/historical-sales                    # List sales data
GET /api/v1/historical-sales/{store_id}         # Sales by store
GET /api/v1/historical-sales/{store_id}/{category_id}  # Sales by store + category
```

## 🧪 Testing

### Run all tests:
```bash
python -m pytest
```

### Run specific test file:
```bash
python -m pytest tests/test_health.py -v
```

### Run tests with coverage:
```bash
python -m pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Test markers:
```bash
python -m pytest -m unit           # Unit tests only
python -m pytest -m integration    # Integration tests only
python -m pytest -m "not slow"     # Skip slow tests
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `OPENAI_API_KEY` - OpenAI API key (get from https://platform.openai.com/api-keys)
- `OPENAI_MODEL` - OpenAI model name (default: gpt-4o-mini, alternatives: gpt-4o, gpt-3.5-turbo)

**Optional:**
- `DATABASE_URL` - Database connection URL (default: sqlite:///./fashion_forecast.db)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Enable debug mode (default: true)
- `ENVIRONMENT` - Environment name (default: development)
- `LOG_LEVEL` - Logging level (default: INFO)
- `LOG_FILE` - Log file path (default: logs/fashion_forecast.log)
- `CORS_ORIGINS` - Allowed frontend origins (default: http://localhost:5173,http://localhost:3000)

### Database Management

**Create tables (if not using seed script):**
```python
from app.database.db import Base, engine
Base.metadata.create_all(engine)
```

**Seed with mock data:**
```bash
python scripts/seed_db.py --data-dir ../data/mock/training
```

**Backup database:**
```bash
python scripts/backup_db.py
# Creates timestamped backup in backups/ directory
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/        # API route handlers
│   │       │   ├── health.py     # Health check endpoint
│   │       │   ├── parameters.py # Parameter extraction
│   │       │   ├── categories.py # Category CRUD
│   │       │   ├── stores.py     # Store management
│   │       │   └── historical_sales.py  # Sales data
│   │       └── router.py         # Main API router
│   ├── core/
│   │   ├── config.py             # Pydantic settings
│   │   ├── logging.py            # Logging configuration
│   │   └── openai_client.py      # OpenAI client
│   ├── database/
│   │   └── db.py                 # SQLAlchemy setup
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── store.py              # Store, StoreCluster
│   │   ├── category.py           # Category
│   │   └── historical_sales.py   # HistoricalSales
│   ├── schemas/                  # Pydantic schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── store.py
│   │   ├── category.py
│   │   ├── historical_sales.py
│   │   └── parameter.py
│   ├── services/                 # Business logic
│   │   └── parameter_extractor.py  # LLM parameter extraction
│   ├── utils/                    # Utilities
│   │   └── csv_parser.py         # CSV validation and parsing
│   └── main.py                   # FastAPI application entry point
├── tests/                        # pytest test suite
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures
│   ├── test_health.py            # Health check tests
│   └── test_csv_parser.py        # CSV utility tests
├── scripts/                      # Development and utility scripts
│   ├── dev.sh                    # Start dev server (Linux/Mac)
│   ├── dev.bat                   # Start dev server (Windows)
│   ├── seed_db.py                # Database seeding script
│   └── backup_db.py              # Database backup utility
├── logs/                         # Application logs (gitignored)
├── backups/                      # Database backups (gitignored)
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── pytest.ini                    # pytest configuration
└── README.md                     # This file
```

## 🔍 Data Seeding

The backend includes comprehensive data seeding capabilities for development and testing.

### Store Attributes CSV Format

Required columns:
- `store_id` - Unique store identifier (integer)
- `size_sqft` - Store size in square feet
- `income_level` - Median household income
- `foot_traffic` - Daily foot traffic count
- `competitor_density` - Number of nearby competitors
- `online_penetration` - Online sales penetration (0.0-1.0)
- `population_density` - Population per square mile
- `mall_location` - Boolean (True/False)

The CSV parser automatically derives:
- `location_tier` - A/B/C based on median income
- `fashion_tier` - PREMIUM/MAINSTREAM/VALUE based on store size
- `store_format` - MALL/STANDALONE based on mall_location
- `region` - NORTHEAST/SOUTHEAST/MIDWEST/WEST based on store_id
- `avg_weekly_sales_12mo` - Computed from store features

### Historical Sales CSV Format

Required columns:
- `date` - Sale date (YYYY-MM-DD format)
- `category` - Product category name
- `store_id` - Store identifier
- `quantity_sold` - Units sold
- `revenue` - Total revenue (optional)

Validation rules:
- Minimum 2 years of historical data
- Date range: 2022-01-01 to 2024-12-31
- Automatically detects and creates categories

### Example: Seeding Database

```bash
# Seed with default mock data
python scripts/seed_db.py

# Seed with custom data directory
python scripts/seed_db.py --data-dir /path/to/csv/files

# Expected output:
# 🌱 STARTING DATABASE SEED
#   Data directory: /path/to/data
#   Database: sqlite:///./fashion_forecast.db
# ✓ Database tables created
# Creating initial store clusters...
# ✓ Created 3 initial clusters
# =================
# SEEDING STORES
# =================
# ✓ Inserted 50 stores
#   Premium: 15 stores
#   Mainstream: 20 stores
#   Value: 15 stores
# ==================================
# SEEDING CATEGORIES & HISTORICAL SALES
# ==================================
#   Detected 3 categories: Blouses, Sweaters, Dresses
# ✓ Inserted 3 categories
#   Inserting 164,400 sales rows...
#     Progress: 10,000 / 164,400 rows
#     ...
# ✓ Inserted 164,400 sales rows in 93.4s
# =================
# 🎉 SEED COMPLETE
# =================
#   Stores: 50
#   Categories: 3
#   Historical Sales: 164,400 rows
```

## 🐛 Debugging

### Enable debug logging:
```bash
LOG_LEVEL=DEBUG python -m uvicorn app.main:app --reload
```

### View logs:
```bash
tail -f logs/fashion_forecast.log
```

### Test OpenAI connection:
```python
from app.core.openai_client import openai_client
print(openai_client.test_connection())
```

### Check database contents:
```bash
# Install sqlite3 cli tool
sqlite3 fashion_forecast.db

sqlite> .tables
sqlite> SELECT COUNT(*) FROM stores;
sqlite> SELECT COUNT(*) FROM historical_sales;
sqlite> .exit
```

## 🚀 Testing All Endpoints

### Step 1: Start the Development Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# OR use the convenience script:
./scripts/dev.sh  # Linux/Mac
.\scripts\dev.bat  # Windows
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 2: Verify OpenAPI Documentation

**Open these URLs in your browser immediately:**

1. **Swagger UI (Interactive Testing):** http://localhost:8000/docs
   - Click on any endpoint to expand it
   - Click "Try it out" button
   - Fill in parameters
   - Click "Execute" to test

2. **ReDoc (Alternative Documentation):** http://localhost:8000/redoc
   - Read-only, more organized view
   - Good for understanding API structure

3. **OpenAPI JSON Schema:** http://localhost:8000/openapi.json
   - Raw API specification
   - Can be imported into Postman or other tools

### Step 3: Test Endpoints - Choose Your Method

#### Method A: Using Swagger UI (Easiest - No Extra Tools)

1. Go to http://localhost:8000/docs
2. Expand "Health" section
3. Click on `GET /health`
4. Click "Try it out"
5. Click "Execute"
6. See response: `{"status": "ok", ...}`

**Repeat for all endpoints!**

---

#### Method B: Using Postman (Desktop App)

**Installation:**
1. Download Postman: https://www.postman.com/downloads/
2. Install and open it

**Import API from OpenAPI spec:**
1. Click "File" → "Import"
2. Click "Link" tab
3. Paste: `http://localhost:8000/openapi.json`
4. Click "Import"
5. All endpoints now available in left sidebar

**Test any endpoint:**
1. Click endpoint in collection
2. Click "Send"
3. View response in right panel

---

#### Method C: Using cURL (Command Line)

```bash
# Test Health Check
curl http://localhost:8000/api/v1/health

# Test Parameter Extraction
curl -X POST http://localhost:8000/api/v1/parameters/extract \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "12-week Spring 2025 season starting March 3rd with weekly replenishment",
    "category_id": "womens_blouses"
  }'

# List Categories
curl http://localhost:8000/api/v1/categories

# List Stores
curl http://localhost:8000/api/v1/stores

# List Store Clusters
curl http://localhost:8000/api/v1/stores/clusters
```

---

### Complete Endpoint Testing Checklist

**Copy and save as `test_all_endpoints.sh` then run: `bash test_all_endpoints.sh`**

```bash
#!/bin/bash
set -e

BASE_URL="http://localhost:8000/api/v1"
PASSED=0
FAILED=0

test_endpoint() {
  local method=$1
  local endpoint=$2
  local name=$3
  local data=$4

  echo "Testing: $name"
  if [ "$method" = "GET" ]; then
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint")
  else
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
      -H "Content-Type: application/json" \
      -d "$data")
  fi

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)

  if [[ $http_code == 200 || $http_code == 201 ]]; then
    echo "  ✅ PASS ($http_code)"
    ((PASSED++))
  else
    echo "  ❌ FAIL ($http_code)"
    echo "  Response: $body"
    ((FAILED++))
  fi
  echo ""
}

echo "🧪 Testing All Fashion Forecast Backend Endpoints"
echo "=================================================="
echo ""

# Health Check
test_endpoint "GET" "/health" "Health Check" ""

# Parameters
test_endpoint "POST" "/parameters/extract" "Parameter Extraction" \
  '{"user_input": "12-week Spring season", "category_id": "test"}'

# Categories
test_endpoint "GET" "/categories" "List Categories" ""

# Stores
test_endpoint "GET" "/stores" "List Stores" ""

# Store Clusters
test_endpoint "GET" "/stores/clusters" "List Store Clusters" ""

# Forecasts
test_endpoint "GET" "/forecasts" "List Forecasts" ""

# Create Workflow
test_endpoint "POST" "/workflows/forecast" "Create Forecast Workflow" \
  '{
    "category_id": "blouses",
    "parameters": {
      "forecast_horizon_weeks": 12,
      "season_start_date": "2025-03-01",
      "replenishment_strategy": "weekly",
      "dc_holdback_percentage": 0.45,
      "markdown_checkpoint_week": 6
    }
  }'

# Allocations
test_endpoint "GET" "/allocations" "List Allocations" ""

# Markdowns
test_endpoint "GET" "/markdowns" "List Markdowns" ""

# Data endpoints
test_endpoint "GET" "/data/categories" "Data Categories" ""

echo "=================================================="
echo "Results: $PASSED passed, $FAILED failed"
echo "=================================================="

if [ $FAILED -eq 0 ]; then
  echo "✅ All endpoints working!"
  exit 0
else
  echo "❌ Some endpoints failed"
  exit 1
fi
```

---

## 🚀 Development Workflow

### 1. Make code changes

Edit files in `app/` directory.

### 2. Run tests

```bash
python -m pytest backend/tests/ -v
```

### 3. Check code style

```bash
ruff check app/
ruff format app/
```

### 4. Commit changes

```bash
git add .
git commit -m "Description of changes"
```

## 📊 Test Coverage

Current test coverage:

- Health endpoint: ✅ 100%
- CSV utilities: ✅ 100%
- API endpoints: 🔄 In progress (Phase 4-8)
- Agent services: 🔄 In progress (Phase 4-8)

Target coverage: ≥70% overall

## 🔐 Security Notes

**Development:**
- Use dummy OpenAI API key if testing without API access
- SQLite database is not suitable for production
- CORS is open to localhost origins

**Production TODO (future phases):**
- [ ] Use PostgreSQL instead of SQLite
- [ ] Add API key authentication
- [ ] Configure production CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Set up Sentry error tracking
- [ ] Use secrets management (e.g., Azure Key Vault)
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting

## 📝 API Response Examples

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2025-10-21T04:16:23.171278Z",
  "services": {
    "database": "ok",
    "api": "ok"
  }
}
```

### Parameter Extraction

```bash
curl -X POST http://localhost:8000/api/v1/parameters/extract \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "12-week Spring 2025 season starting March 3rd with weekly replenishment and 45% DC holdback",
    "category_id": "womens_blouses"
  }'
```

Response:
```json
{
  "forecast_horizon_weeks": 12,
  "season_start_date": "2025-03-03",
  "season_end_date": "2025-05-26",
  "replenishment_strategy": "weekly",
  "dc_holdback_percentage": 0.45,
  "markdown_checkpoint_week": 6,
  "markdown_threshold": 0.60,
  "extraction_confidence": "high"
}
```

### List Categories

```bash
curl http://localhost:8000/api/v1/categories
```

Response:
```json
[
  {
    "category_id": "blouses",
    "category_name": "Blouses",
    "season_start_date": "2025-01-01",
    "season_end_date": "2025-03-31",
    "season_length_weeks": 12,
    "archetype": "FASHION_RETAIL",
    "description": "Auto-detected category from historical sales: Blouses"
  },
  ...
]
```

## 🌐 WebSocket API

### Real-Time Agent Status Updates

The backend provides WebSocket support for real-time agent progress updates during workflow execution.

**WebSocket Endpoint:**
```
WS /api/v1/workflows/{workflow_id}/stream
```

**Example: Connect and Listen (JavaScript)**
```javascript
const workflowId = "wf_12345";
const ws = new WebSocket(`ws://localhost:8000/api/v1/workflows/${workflowId}/stream`);

ws.onopen = () => {
  console.log("WebSocket connected");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Agent update:", message.type, message);

  // message.type can be:
  // - "agent_started": Agent beginning work
  // - "agent_progress": Agent making progress (includes progress_pct)
  // - "agent_completed": Agent finished with results
  // - "human_input_required": Waiting for approval
  // - "workflow_complete": Entire workflow finished
  // - "error": Something went wrong
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("WebSocket closed");
};
```

**Example: Test WebSocket with cURL**
```bash
# Note: cURL has limited WebSocket support, use wscat instead:
# npm install -g wscat

wscat -c ws://localhost:8000/api/v1/workflows/wf_test123/stream
```

---

## ⚙️ Approval Endpoints (Human-in-the-Loop)

These endpoints handle human approval decisions during the workflow.

### Manufacturing Approval

**Endpoint:**
```bash
POST /api/v1/approvals/manufacturing
```

**Request:**
```json
{
  "workflow_id": "wf_12345",
  "manufacturing_qty": 9600,
  "initial_allocation": 5280,
  "holdback": 4320,
  "decision": "accept"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/approvals/manufacturing \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf_12345",
    "manufacturing_qty": 9600,
    "initial_allocation": 5280,
    "holdback": 4320,
    "decision": "accept"
  }'
```

**Postman Instructions:**
1. Create new POST request
2. URL: `http://localhost:8000/api/v1/approvals/manufacturing`
3. Body → Raw → JSON
4. Paste request JSON above
5. Send

### Markdown Approval

**Endpoint:**
```bash
POST /api/v1/approvals/markdown
```

**Request:**
```json
{
  "workflow_id": "wf_12345",
  "week_number": 6,
  "sell_through_pct": 0.65,
  "recommended_markdown_pct": 0.25,
  "decision": "accept"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/approvals/markdown \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf_12345",
    "week_number": 6,
    "sell_through_pct": 0.65,
    "recommended_markdown_pct": 0.25,
    "decision": "accept"
  }'
```

---

## 🤖 Agent Scaffolds & ML Pipeline

### Available Agents

The backend includes 4 agent scaffolds ready for Phase 4 implementation:

**Location:** `backend/app/agents/`

1. **Orchestrator Agent** (`orchestrator.py`)
   - Coordinates workflow execution
   - Delegates to specialized agents
   - Monitors variance and triggers re-forecasting
   - Status: Scaffold with placeholder logic

2. **Demand Agent** (`demand.py`)
   - Forecasts demand using Prophet/ARIMA
   - Clusters stores for allocation
   - Status: Scaffold with mock data

3. **Inventory Agent** (`inventory.py`)
   - Calculates manufacturing quantities
   - Plans DC allocation and store replenishment
   - Status: Scaffold with mock data

4. **Pricing Agent** (`pricing.py`)
   - Recommends markdown percentages
   - Applies elasticity coefficients
   - Status: Scaffold with mock data

### ML Pipeline Scaffolding

**Location:** `backend/app/ml/`

The ML module includes placeholder implementations:

```bash
backend/app/ml/
├── __init__.py
├── prophet_model.py      # Prophet forecasting (returns mock data)
├── arima_model.py        # ARIMA forecasting (returns mock data)
├── clustering.py         # K-means clustering (3 mock clusters)
├── ensemble.py           # Ensemble predictions
└── preprocessing.py      # Data preprocessing utilities
```

**Current Status:** All models return realistic mock data for testing. Actual ML implementation happens in Phase 5-7.

**Example: Forecast with Prophet (Mock)**
```python
from app.ml.prophet_model import ProphetModel

model = ProphetModel()
forecast = model.forecast(
    historical_data=weekly_sales,
    periods=12,
    confidence_interval=0.95
)
# Returns: {"trend": [...], "seasonal": [...], "forecast": [...]}
```

---

## ✅ Phase 3 Verification Checklist

Use these commands to verify Phase 3 is fully implemented:

### 1. Server Health
```bash
# Start server
cd backend
python -m uvicorn app.main:app --reload

# In another terminal, test health
curl http://localhost:8000/api/v1/health
# Expected: {"status": "ok", ...}
```

### 2. Database Verification
```bash
# Check tables exist (requires sqlite3 CLI)
sqlite3 fashion_forecast.db ".tables"

# Verify 50 stores seeded
sqlite3 fashion_forecast.db "SELECT COUNT(*) FROM stores;"
# Expected: 50

# Verify historical sales data
sqlite3 fashion_forecast.db "SELECT COUNT(*) FROM historical_sales;"
# Expected: ~164,400 rows
```

### 3. OpenAPI Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 4. Parameter Extraction
```bash
curl -X POST http://localhost:8000/api/v1/parameters/extract \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "12-week Spring 2025 season starting March 3rd with weekly replenishment",
    "category_id": "womens_blouses"
  }'
# Expected: Extracted parameters with confidence score
```

### 5. Workflow Creation
```bash
curl -X POST http://localhost:8000/api/v1/workflows/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "blouses",
    "parameters": {
      "forecast_horizon_weeks": 12,
      "season_start_date": "2025-03-01",
      "replenishment_strategy": "weekly",
      "dc_holdback_percentage": 0.45,
      "markdown_checkpoint_week": 6
    }
  }'
# Expected: workflow_id and WebSocket URL
```

### 6. Run All Tests
```bash
cd backend
pytest tests/ -v
# Expected: 35 tests passed
```

### 7. Review ML Scaffolding
```bash
ls -la backend/app/ml/
# Should see: prophet_model.py, arima_model.py, clustering.py, ensemble.py
```

---

## 🆘 Support & Contributing

**Issues:** Report bugs or request features via GitHub Issues

**Documentation:** See `/docs` directory for detailed design documents

**Contributing:**
1. Create a feature branch
2. Make changes
3. Write tests (all tests must pass)
4. Submit pull request


---

**Backend Status:** ✅ Phase 3 Complete (All 14 Stories - Days 1-4)

**Configuration:** OpenAI API (standard, not Azure)

**Next Phase:** Phase 4 - Orchestrator Agent Implementation
