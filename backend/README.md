# Fashion Forecast Backend

Parameter-Driven Multi-Agent Demand Forecasting & Inventory Allocation System

## Prerequisites

- Python 3.11+
- UV package manager

## Setup

### 1. Install Python 3.11+

**Windows:**
```bash
# Download Python 3.11+ from python.org
# Or use winget:
winget install Python.Python.3.11
```

**Mac:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2. Install UV Package Manager

```bash
pip install uv
```

or

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Install Dependencies

```bash
cd backend
uv pip install -e ".[dev]"
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

## Running the Server

### Development Mode (with auto-reload)

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Development Commands

- **Run server:** `uvicorn app.main:app --reload`
- **Run tests:** `pytest`
- **Run tests with coverage:** `pytest --cov=app tests/`
- **Type check:** `mypy app/`
- **Lint:** `ruff check .`
- **Format:** `ruff format .`

## API Documentation

Once the server is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── agents/              # OpenAI Agents SDK implementations
│   │   ├── __init__.py
│   │   ├── orchestrator.py  # Orchestrator agent
│   │   ├── demand.py        # Demand forecasting agent
│   │   ├── inventory.py     # Inventory allocation agent
│   │   └── pricing.py       # Pricing/markdown agent
│   ├── api/                 # REST API endpoints
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── parameters.py   # Parameter extraction
│   │       ├── workflows.py    # Workflow orchestration
│   │       ├── websockets.py   # WebSocket connections
│   │       ├── forecasts.py    # Forecast resources
│   │       ├── allocations.py  # Allocation resources
│   │       ├── markdowns.py    # Markdown resources
│   │       └── data.py         # Data management
│   ├── models/              # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── store.py
│   │   ├── forecast.py
│   │   ├── allocation.py
│   │   └── markdown.py
│   ├── schemas/             # Pydantic schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── parameters.py
│   │   ├── forecast.py
│   │   ├── allocation.py
│   │   └── workflow.py
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── parameter_extractor.py
│   │   └── workflow_service.py
│   ├── database/            # Database configuration
│   │   ├── __init__.py
│   │   └── base.py
│   ├── ml/                  # Machine learning models
│   │   ├── __init__.py
│   │   ├── prophet_model.py
│   │   ├── arima_model.py
│   │   └── clustering.py
│   ├── websocket/           # WebSocket connection manager
│   │   ├── __init__.py
│   │   └── manager.py
│   └── utils/               # Shared utilities
│       ├── __init__.py
│       └── csv_parser.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_parameters.py
│   ├── test_workflows.py
│   └── test_agents.py
├── pyproject.toml           # UV package configuration
├── .env.example             # Environment variable template
└── README.md                # This file
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource URL | `https://YOUR_RESOURCE.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | API authentication key | `your_api_key_here` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4o-mini` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-10-21` |
| `DATABASE_URL` | SQLite database path | `sqlite:///./fashion_forecast.db` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `true` |

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_parameters.py
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html tests/
```

## Database Migrations

### Initialize Alembic

```bash
alembic init migrations
```

### Create Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

## Troubleshooting

### UV Not Found

**Solution:** Restart terminal or add UV to PATH manually
- Windows: `C:\Users\<username>\AppData\Local\Programs\Python\Python311\Scripts`
- Mac/Linux: `~/.local/bin`

### Python Version Mismatch

**Solution:** Use `python3.11 -m pip install uv` to ensure correct Python version

### Prophet Installation Fails

**Solution:** Prophet requires compiler tools
- Windows: Install Visual Studio Build Tools
- Mac: `xcode-select --install`
- Linux: `sudo apt-get install python3-dev`

### Port 8000 Already in Use

**Solution:** Find and kill the process or use a different port
- Windows: `netstat -ano | findstr :8000`
- Mac/Linux: `lsof -i :8000`

## Technology Stack

- **FastAPI** - Modern Python web framework with automatic API documentation
- **UV** - Fast Python package manager (10-100x faster than pip)
- **OpenAI Agents SDK** - Multi-agent orchestration framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **Prophet** - Time-series forecasting by Meta
- **Scikit-learn** - Machine learning library

## Phase 3 Implementation

This backend is part of Phase 3 (Backend Architecture) of an 8-phase MVP development plan.

**Stories Completed:**
- PHASE3-001: Project Setup & UV Configuration ✅

**Next Stories:**
- PHASE3-002: Database Schema & Models
- PHASE3-003: Pydantic Schemas & DTOs
- PHASE3-004: FastAPI Application Setup
- ... (11 more stories)

For more details, see `docs/04_MVP_Development/implementation/phase_3_backend_architecture/`

## License

Academic Project - Independent Study

## Contributors

- Henry & Yina (Backend Development)
