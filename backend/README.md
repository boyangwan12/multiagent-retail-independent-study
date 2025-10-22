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

## 🚀 Development Workflow

### 1. Make changes to code

Edit files in `app/` directory.

### 2. Run tests

```bash
python -m pytest
```

### 3. Check code style (if using ruff)

```bash
ruff check app/
ruff format app/
```

### 4. Test endpoints manually

Use Swagger UI at http://localhost:8000/docs to test API endpoints interactively.

### 5. Commit changes

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
