# Story: Initialize FastAPI Backend with UV Package Manager & Monorepo Structure

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-001
**Status:** Draft
**Estimate:** 2 hours
**Agent Model Used:** _TBD_
**Dependencies:** None

---

## Story

As a backend developer,
I want to initialize a FastAPI project with UV package manager and configure a monorepo structure with proper environment setup,
So that I have a production-ready Python backend foundation for implementing the multi-agent demand forecasting system.

**Business Value:** Establishes the technical foundation for the entire backend system. Without proper project setup, all subsequent backend development tasks cannot proceed. The UV package manager provides 10-100x faster dependency resolution compared to pip, critical for efficient development iteration.

**Epic Context:** This is Task 1 of 14 in Phase 3. It's the foundational step that enables all other backend development. The choices made here (FastAPI, UV, monorepo layout, Python 3.11+) align with modern best practices and the technical architecture specified in planning docs.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ UV package manager installed and configured
2. ✅ Python project initialized with `uv init`
3. ✅ `pyproject.toml` configured with all required dependencies
4. ✅ Monorepo structure created (`backend/` and `frontend/` folders)
5. ✅ `.gitignore` configured for Python and Node.js
6. ✅ `backend/.env.example` created with required Azure OpenAI variables
7. ✅ FastAPI minimal project runs successfully
8. ✅ Backend folder structure created per architecture spec

### Quality Requirements

9. ✅ All dependencies install without conflicts using UV
10. ✅ Python 3.11+ detected and used
11. ✅ No hardcoded secrets in source code
12. ✅ Environment variables load correctly from `.env`

---

## Tasks

### Task 1: Install UV Package Manager
- [ ] Check Python version: `python --version` (must be 3.11+)
- [ ] Install UV: `pip install uv`
- [ ] Verify UV installation: `uv --version`
- [ ] Confirm UV is in PATH and accessible

**Expected Output:** UV installed and ready to use

**Reference:** `implementation_plan.md` Task 1, lines 83-95

### Task 2: Initialize Python Project with UV
- [ ] Navigate to project root directory
- [ ] Run `uv init` to initialize Python project
- [ ] Verify `pyproject.toml` is created
- [ ] Configure project metadata in `pyproject.toml`

**Expected Output:** Basic `pyproject.toml` file created

### Task 3: Create Monorepo Folder Structure
- [ ] Create `backend/` directory (if not exists)
- [ ] Create `frontend/` directory (if not exists)
- [ ] Move backend-related files into `backend/`
- [ ] Verify structure matches architecture spec

**Expected Directory Structure:**
```
project-root/
├── backend/           # Python FastAPI backend
├── frontend/          # React frontend (Phase 2 already exists)
├── data/              # Mock CSV data (Phase 1 already exists)
├── docs/              # Documentation (already exists)
├── .gitignore
└── README.md
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2408-2544 (Source Tree Structure)

### Task 4: Configure pyproject.toml with Dependencies
- [ ] Add project metadata (name, version, python version)
- [ ] Add core dependencies:
  - `fastapi>=0.115.0`
  - `uvicorn[standard]>=0.30.0`
  - `openai-agents-sdk>=0.3.3`
  - `openai>=1.54.0`
  - `sqlalchemy>=2.0.35`
  - `alembic>=1.13.0`
  - `pydantic>=2.10.0`
  - `pydantic-settings>=2.6.0`
  - `pandas>=2.2.0`
  - `numpy>=1.26.0`
  - `prophet>=1.1.6`
  - `pmdarima>=2.0.4`
  - `scikit-learn>=1.5.0`
  - `python-multipart>=0.0.12`
  - `websockets>=13.1`
- [ ] Add dev dependencies:
  - `pytest>=8.3.0`
  - `pytest-asyncio>=0.24.0`
  - `mypy>=1.13.0`
  - `ruff>=0.7.0`
- [ ] Set `requires-python = ">=3.11"`

**Complete pyproject.toml Template:**
```toml
[project]
name = "fashion-forecast-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "openai-agents-sdk>=0.3.3",
    "openai>=1.54.0",
    "sqlalchemy>=2.0.35",
    "alembic>=1.13.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "pandas>=2.2.0",
    "numpy>=1.26.0",
    "prophet>=1.1.6",
    "pmdarima>=2.0.4",
    "scikit-learn>=1.5.0",
    "python-multipart>=0.0.12",
    "websockets>=13.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "mypy>=1.13.0",
    "ruff>=0.7.0",
]
```

**Reference:** `implementation_plan.md` lines 97-128

### Task 5: Configure .gitignore
- [ ] Create/update `.gitignore` in project root
- [ ] Add Python-specific ignores:
  - `__pycache__/`
  - `*.py[cod]`
  - `*$py.class`
  - `.Python`
  - `venv/`
  - `env/`
  - `.env`
  - `.venv`
  - `*.egg-info/`
  - `dist/`
  - `build/`
- [ ] Add Node.js-specific ignores:
  - `node_modules/`
  - `dist/`
  - `.next/`
  - `build/`
- [ ] Add database ignores:
  - `*.db`
  - `*.sqlite`
  - `*.sqlite3`
- [ ] Add IDE ignores:
  - `.vscode/`
  - `.idea/`
  - `*.swp`
  - `*.swo`
  - `.DS_Store`

**Expected Output:** Comprehensive `.gitignore` file preventing secrets from being committed

### Task 6: Create Backend Folder Structure
- [ ] Create `backend/app/` directory
- [ ] Create `backend/app/agents/` directory
- [ ] Create `backend/app/api/` directory
- [ ] Create `backend/app/api/routes/` directory
- [ ] Create `backend/app/models/` directory
- [ ] Create `backend/app/database/` directory
- [ ] Create `backend/app/ml/` directory
- [ ] Create `backend/app/utils/` directory
- [ ] Create `backend/tests/` directory
- [ ] Create placeholder `__init__.py` files in each Python package directory

**Expected Backend Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── agents/
│   │   └── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── database/
│   │   └── __init__.py
│   ├── ml/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── .env.example
└── README.md
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2414-2476 (Backend folder structure)

### Task 7: Create .env.example Template
- [ ] Create `backend/.env.example` file
- [ ] Add Azure OpenAI configuration variables:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_DEPLOYMENT`
  - `AZURE_OPENAI_API_VERSION`
- [ ] Add database configuration:
  - `DATABASE_URL`
- [ ] Add server configuration:
  - `HOST`
  - `PORT`
  - `DEBUG`
- [ ] Add comments explaining each variable

**.env.example Template:**
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-10-21

# Database Configuration
DATABASE_URL=sqlite:///./fashion_forecast.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

**Security Note:** Never commit the actual `.env` file - ensure it's in `.gitignore`

**Reference:** `implementation_plan.md` lines 192-207

### Task 8: Install Dependencies with UV
- [ ] Navigate to `backend/` directory
- [ ] Run `uv pip install -e .` to install project dependencies
- [ ] Run `uv pip install -e ".[dev]"` to install dev dependencies
- [ ] Verify all packages installed successfully
- [ ] Check for any dependency conflicts

**Expected Output:** All dependencies installed without errors

**Note:** UV should be significantly faster than pip (10-100x speed improvement)

### Task 9: Create Minimal FastAPI App for Testing
- [ ] Create `backend/app/main.py`
- [ ] Implement minimal FastAPI application:
  - Create FastAPI instance
  - Add root endpoint (`GET /`)
  - Add health check endpoint (`GET /api/health`)
- [ ] Add CORS middleware configuration (placeholder)
- [ ] Test server startup

**Minimal main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Fashion Forecast Backend",
    version="0.1.0",
    description="Parameter-Driven Multi-Agent Demand Forecasting & Inventory Allocation System"
)

# CORS configuration (to be refined in later tasks)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Fashion Forecast API", "version": "0.1.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}
```

**Reference:** `implementation_plan.md` Task 4, lines 176-191

### Task 10: Test Backend Server Startup
- [ ] Navigate to `backend/` directory
- [ ] Run `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [ ] Verify server starts without errors
- [ ] Open browser to `http://localhost:8000`
- [ ] Verify root endpoint returns JSON response
- [ ] Test health check endpoint: `http://localhost:8000/api/health`
- [ ] Verify automatic API docs: `http://localhost:8000/docs`
- [ ] Stop server (Ctrl+C)

**Expected Output:**
- Server starts on port 8000
- Root endpoint returns: `{"message": "Fashion Forecast API", "version": "0.1.0"}`
- Health check returns: `{"status": "healthy", "service": "backend"}`
- FastAPI automatic docs accessible at `/docs`

### Task 11: Create Backend README
- [ ] Create `backend/README.md`
- [ ] Add sections:
  - Project overview
  - Prerequisites
  - Setup instructions
  - Running the server
  - Development commands
  - Environment variables
- [ ] Include UV-specific commands

**README.md Template:**
```markdown
# Fashion Forecast Backend

Parameter-Driven Multi-Agent Demand Forecasting & Inventory Allocation System

## Prerequisites

- Python 3.11+
- UV package manager

## Setup

1. Install UV:
   ```bash
   pip install uv
   ```

2. Install dependencies:
   ```bash
   cd backend
   uv pip install -e ".[dev]"
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

## Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Development Commands

- **Run server:** `uvicorn app.main:app --reload`
- **Run tests:** `pytest`
- **Type check:** `mypy app/`
- **Lint:** `ruff check .`
- **Format:** `ruff format .`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
```

### Task 12: Final Verification
- [ ] Verify monorepo structure matches architecture spec
- [ ] Verify all dependencies installed successfully
- [ ] Verify `.env.example` exists and is complete
- [ ] Verify `.gitignore` prevents `.env` from being committed
- [ ] Verify FastAPI server starts without errors
- [ ] Verify all folder structures created correctly
- [ ] Verify `pyproject.toml` has correct dependencies
- [ ] Test: Create a dummy `.env` file (don't commit) and verify it's ignored by git

---

## Dev Notes

### Technology Stack Rationale

**UV Package Manager:**
- 10-100x faster than pip for dependency resolution
- Built-in virtual environment management
- Compatible with pyproject.toml (PEP 621)
- Recommended by OpenAI for agent development
- Rust-based implementation for performance

**FastAPI:**
- Modern Python web framework
- Automatic API documentation (Swagger UI)
- Built-in WebSocket support (critical for real-time agent updates)
- Pydantic integration for data validation
- Async support for concurrent operations

**Python 3.11+:**
- Required for OpenAI Agents SDK compatibility
- Performance improvements over 3.10
- Better error messages
- Type hinting improvements

**Monorepo Structure:**
- Single repository for backend + frontend
- Easier atomic commits across full-stack changes
- Simplified development for solo project
- Academic MVP focus (no need for microservices complexity)

### Project Structure Philosophy

**Backend Organization:**
```
backend/
├── app/              # Application code
│   ├── agents/       # OpenAI Agents SDK implementations
│   ├── api/          # FastAPI routes
│   ├── models/       # Pydantic models
│   ├── database/     # SQLite + Alembic migrations
│   ├── ml/           # ML models (Prophet, ARIMA, K-means)
│   └── utils/        # Shared utilities
├── tests/            # Test suite
└── pyproject.toml    # UV configuration
```

**Key Principles:**
- **agents/**: Agent implementations (demand, inventory, pricing, orchestrator)
- **api/**: REST API endpoints + WebSocket handlers
- **models/**: Pydantic schemas for request/response validation
- **database/**: SQLAlchemy models + migrations
- **ml/**: Forecasting and clustering algorithms
- **utils/**: Logging, validators, helpers

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 2408-2544

### Environment Variables

**Critical Variables:**
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

**Security Best Practices:**
- Never commit `.env` to git (ensured by `.gitignore`)
- Use `.env.example` as template without real secrets
- Rotate API keys regularly
- Use environment-specific `.env` files for different deployments

### Dependencies Breakdown

**Core Backend:**
- `fastapi`: Web framework + WebSocket
- `uvicorn[standard]`: ASGI server with HTTP/2 + WebSocket support
- `pydantic`: Data validation
- `pydantic-settings`: Environment variable management

**Agent Framework:**
- `openai-agents-sdk`: Multi-agent orchestration
- `openai`: Azure OpenAI API client

**Database:**
- `sqlalchemy`: ORM for SQLite
- `alembic`: Database migrations

**ML & Data:**
- `prophet`: Meta's time-series forecasting
- `pmdarima`: Auto-ARIMA models
- `scikit-learn`: K-means clustering
- `pandas + numpy`: Data manipulation

**Utilities:**
- `python-multipart`: File upload support (CSV uploads)
- `websockets`: Real-time agent updates

**Dev Tools:**
- `pytest + pytest-asyncio`: Testing
- `mypy`: Static type checking
- `ruff`: Fast linter + formatter

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 230-278

### Common Issues & Solutions

**Issue 1: UV not found after installation**
- Solution: Restart terminal or add UV to PATH manually
- Windows: `C:\Users\<username>\AppData\Local\Programs\Python\Python311\Scripts`
- Mac/Linux: `~/.local/bin`

**Issue 2: Python version mismatch**
- Solution: Use `python3.11 -m pip install uv` to ensure correct Python version
- Verify: `python --version` should show 3.11+

**Issue 3: Prophet installation fails**
- Solution: Prophet requires compiler tools
  - Windows: Install Visual Studio Build Tools
  - Mac: `xcode-select --install`
  - Linux: `sudo apt-get install python3-dev`

**Issue 4: FastAPI server won't start**
- Solution: Check if port 8000 is already in use
  - Windows: `netstat -ano | findstr :8000`
  - Mac/Linux: `lsof -i :8000`
  - Kill process or use different port

**Issue 5: CORS errors from frontend**
- Solution: Verify `allow_origins` in main.py includes Vite dev server URL (`http://localhost:5173`)

### Critical References

- **Planning Spec:** `planning/3_technical_architecture_v3.3.md` lines 230-278 (Tech Stack)
- **Source Tree:** `planning/3_technical_architecture_v3.3.md` lines 2408-2544 (Folder Structure)
- **Implementation Plan:** `implementation/phase_3_backend_architecture/implementation_plan.md` Task 1, lines 83-128
- **UV Docs:** https://github.com/astral-sh/uv
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **OpenAI Agents SDK:** https://github.com/openai/openai-agents

---

## Testing

### Manual Testing Checklist

- [ ] UV installed successfully (`uv --version`)
- [ ] Python 3.11+ detected (`python --version`)
- [ ] Dependencies install without conflicts (`uv pip install -e ".[dev]"`)
- [ ] Monorepo folder structure matches architecture spec
- [ ] Backend folder structure created correctly
- [ ] `.env.example` exists with all required variables
- [ ] `.gitignore` prevents `.env` from being tracked
- [ ] FastAPI server starts successfully
- [ ] Root endpoint returns correct JSON
- [ ] Health check endpoint returns healthy status
- [ ] Swagger UI accessible at `/docs`
- [ ] Backend README is clear and accurate

### Verification Commands

```bash
# Verify UV installation
uv --version

# Verify Python version
python --version

# Install dependencies
cd backend
uv pip install -e ".[dev]"

# Run server
uvicorn app.main:app --reload

# Test endpoints (in separate terminal)
curl http://localhost:8000/
curl http://localhost:8000/api/health

# Check git ignore
git status  # .env should NOT appear if it exists
```

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

### File List

_Dev Agent will populate this section during implementation_

**Files to Create:**
- `backend/pyproject.toml`
- `backend/.env.example`
- `backend/README.md`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/agents/__init__.py`
- `backend/app/api/__init__.py`
- `backend/app/api/routes/__init__.py`
- `backend/app/models/__init__.py`
- `backend/app/database/__init__.py`
- `backend/app/ml/__init__.py`
- `backend/app/utils/__init__.py`
- `backend/tests/__init__.py`
- `.gitignore` (project root)

**Files to Modify:**
- None (this is the initial setup)

---

## Definition of Done

- [ ] UV package manager installed and verified
- [ ] Python project initialized with UV
- [ ] `pyproject.toml` configured with all dependencies
- [ ] Monorepo structure created (backend/ and frontend/)
- [ ] `.gitignore` configured for Python + Node.js
- [ ] `backend/.env.example` created with required variables
- [ ] Backend folder structure matches architecture spec
- [ ] All dependencies installed successfully with UV
- [ ] Minimal FastAPI app created
- [ ] FastAPI server starts without errors
- [ ] Root endpoint (`/`) returns correct JSON
- [ ] Health check endpoint (`/api/health`) works
- [ ] Swagger UI accessible at `/docs`
- [ ] Backend README created with setup instructions
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
**Last Updated:** 2025-10-19 (Template compliance fixes added)
**Story Points:** 2
**Priority:** P0 (Blocker for all other Phase 3 tasks)
