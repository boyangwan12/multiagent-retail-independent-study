# Independent Study: Multi-Agent Demand Forecasting System

**Institution:** McGill University
**Program:** Master of Management in Analytics
**Timeline:** September 2025 - Dec 2025
**Focus:** LLM-powered multi-agent system for retail demand forecasting and inventory allocation

---

## Project Overview

Building a **parameter-driven 3-agent demand forecasting and inventory allocation system** for retail using OpenAI Agents SDK. The system uses **category-level hierarchical forecasting** to predict demand and optimize inventory decisions, addressing critical pain points: inaccurate forecasting, location-specific allocation failures, and late markdown decisions.

**Core Innovation:** "Forecast Once, Allocate with Math" - Category-level forecast (1 prediction) + hierarchical allocation (Category → Cluster → Store)

**Strategic Pivot (v3.3):** Parameter-driven architecture adapts to diverse retail workflows through LLM-gathered configuration (allocation %, season length, markdown timing, etc.)

**MVP Scope:** Generic retail planning solution emphasizing agentic coordination

---

## Repository Structure

```
independent_study/
├── docs/
│   ├── 01_Project_Foundation/
│   │   └── project_brief.md                    # Initial project proposal
│   │
│   ├── 02_Interviews/
│   │   ├── Notes/                              # 5 practitioner interviews
│   │   ├── Transcripts/                        # Interview transcripts
│   │   └── Prep/                               # Interview guides and strategy
│   │
│   ├── 03_Evidence_Pack/
│   │   ├── 01_Problem_Validation.md            # Evidence-based problem definition
│   │   ├── 02_User_Research_Synthesis.md       # Interview insights synthesis
│   │   ├── 03_Requirements_Constraints.md      # System requirements
│   │   ├── 04_Approach_Validation.md           # Solution validation
│   │   ├── 05_Success_Metrics.md               # Evaluation criteria
│   │   ├── 06_Research_Methodology.md          # Research approach
│   │   └── _extraction/
│   │       ├── Pain_Point_Inventory.md         # 28 pain points extracted
│   │       ├── Quote_Library.md                # Key practitioner quotes
│   │       └── Requirements_Extract.md         # Functional requirements
│   │
│   ├── 04_MVP_Development/
│   │   ├── planning/
│   │   │   ├── 0_PLANNING_GUIDE.md             # ✅ Navigation & standards
│   │   │   ├── 1_product_brief_v3.3.md         # ✅ Parameter-driven product spec
│   │   │   ├── 2_process_workflow_v3.3.md      # ✅ 5-phase workflow with examples
│   │   │   ├── 3_technical_architecture_v3.3.md # ✅ Complete architecture
│   │   │   ├── 4_prd_v3.3.md                   # ✅ Product requirements
│   │   │   ├── 5_front-end-spec_v3.3.md        # ✅ Frontend UI/UX specification
│   │   │   └── 6_data_specification_v3.2.md    # ✅ Data structures & validation
│   │   │
│   │   ├── archive/
│   │   │   ├── v1.1/                           # Architecture v1.1
│   │   │   ├── v2.1/                           # Product Brief v2.1
│   │   │   ├── v3.1/                           # Workflow v3.1
│   │   │   └── v3.2/                           # Original v3.2 documents
│   │   │
│   │   └── README.md                           # Planning documentation guide
│   │
│   └── 05_Progress_Reports/
│       └── Weekly_Supervisor_Meetings/         # Weekly progress updates
│           ├── Week_01_Updates.md
│           ├── Week_02_Updates.md
│           ├── Week_03_Updates.md
│           ├── Week_04_Updates.md
│           ├── Week_05_Updates.md              # v3.1 → v3.3 evolution
│           └── Week_05_Updates.html            # Visual presentation
│
└── src/                                        # (To be created in Phase 1)
    ├── agents/                                 # Demand, Inventory, Pricing, Orchestrator
    ├── forecasting/                            # Prophet, ARIMA, similar-item matching
    ├── data/                                   # Synthetic data generation
    ├── config/                                 # YAML configuration
    └── utils/                                  # Metrics, logging
```

---

## Key Documents

### Product Specifications (Current - v3.3)
- **[Planning Guide](docs/04_MVP_Development/planning/0_PLANNING_GUIDE.md)**: Documentation navigation, standards, and workflow
- **[Product Brief v3.3](docs/04_MVP_Development/planning/1_product_brief_v3.3.md)**: Parameter-driven system design with LLM configuration gathering
- **[Process Workflow v3.3](docs/04_MVP_Development/planning/2_process_workflow_v3.3.md)**: 5-phase workflow with concrete examples
- **[Technical Architecture v3.3](docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md)**: Complete backend architecture - OpenAI Agents SDK, parameter-driven design
- **[PRD v3.3](docs/04_MVP_Development/planning/4_prd_v3.3.md)**: Product requirements document
- **[Frontend Spec v3.3](docs/04_MVP_Development/planning/5_front-end-spec_v3.3.md)**: Complete UI/UX specification
- **[Data Specification v3.2](docs/04_MVP_Development/planning/6_data_specification_v3.2.md)**: Data structures and validation rules

### Research & Validation
- **[Evidence Pack](docs/03_Evidence_Pack/)**: 6 components validating problem-solution fit with 5 practitioner interviews
- **[Pain Point Inventory](docs/03_Evidence_Pack/_extraction/Pain_Point_Inventory.md)**: 28 pain points extracted from user research

---

## System Architecture

### 3 Agents + Orchestrator

| Agent | Responsibility | Key Output |
|-------|---------------|-----------|
| **Demand Agent** | Category-level forecasting (Prophet+ARIMA ensemble), K-means clustering, allocation factors | Total season demand, cluster distribution, allocation factors |
| **Inventory Agent** | Manufacturing calculation (20% safety stock), 55/45 allocation, replenishment planning | Manufacturing order, store allocations, replenishment plans |
| **Pricing Agent** | Week 6 markdown checkpoint (Gap × Elasticity formula), variance monitoring | Markdown recommendations (5-40%), re-forecast triggers |
| **Orchestrator** | Sequential handoffs, context-rich object passing, dynamic re-forecast enabling | Workflow coordination, variance alerts (>20%) |

### Agentic Features (OpenAI Agents SDK)
- **Context-rich handoffs**: Pass forecast/allocation objects directly between agents (no database queries)
- **Dynamic handoff enabling**: Re-forecast handoff enabled dynamically when variance >20%
- **Human-in-the-loop**: Approval modals (Modify iterative + Accept, no Reject)
- **Real-time updates**: WebSocket streaming of agent progress
- **Guardrails**: Automatic output validation (fail-fast on errors)
- **Sessions**: Automatic conversation history management

### Technology Stack (Updated)
- **LLM**: Azure OpenAI Service (gpt-4o-mini via Responses API)
- **Agent Framework**: OpenAI Agents SDK (production-ready, v0.3.3+)
- **Package Manager**: UV (10-100x faster than pip)
- **Backend**: Python 3.11+ + FastAPI + SQLite
- **Frontend**: React 18 + TypeScript + Vite + Shadcn/ui + TanStack Query
- **ML/Forecasting**: Prophet, pmdarima (ARIMA), scikit-learn (K-means)
- **Budget**: <$5 LLM costs

---

## Development Timeline (10-Week Plan)

**Phase 1 (Weeks 1-2):** Backend foundation (UV + FastAPI + database + ML functions)
**Phase 2 (Weeks 3-4):** Agent implementation (Demand, Inventory, Pricing, Orchestrator)
**Phase 3 (Weeks 5-6):** API & integration (REST + WebSocket + handoffs)
**Phase 4 (Weeks 7-8):** Frontend (React dashboard + agent visualization + approval modals)
**Phase 5 (Weeks 9-10):** Testing & validation (Unit + Integration + E2E, MAPE <20%)

---

## Development Environment Setup

### Prerequisites

- **Backend Requirements:**
  - Python 3.11 or higher
  - UV package manager (`pip install uv`)
  - OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

- **Frontend Requirements:**
  - Node.js 18 or higher
  - npm 9 or higher

### Quick Start

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd multiagent-retail-independent-study
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create .env file from example
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your_actual_api_key_here

# Install dependencies using UV
uv sync

# Start the backend server
uvicorn app.main:app --reload

# Server will be available at: http://localhost:8000
# API docs available at: http://localhost:8000/docs
```

#### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Create .env file from example
cp .env.example .env

# Install dependencies
npm install

# Start the development server
npm run dev

# Frontend will be available at: http://localhost:5173
```

#### 4. Verify Setup

1. **Backend Health Check:**
   - Open http://localhost:8000/docs in your browser
   - You should see the FastAPI Swagger documentation
   - Try the `/api/v1/health` endpoint

2. **Frontend Connection:**
   - Open http://localhost:5173 in your browser
   - Open browser DevTools (F12) → Console
   - Verify no CORS errors

3. **Check Backend Logs:**
   - Look for: `✅ All required environment variables are set`
   - If you see warnings about `OPENAI_API_KEY`, update your `.env` file

### Environment Variables

#### Backend (.env)
```env
# Required
OPENAI_API_KEY=sk-your_actual_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=sqlite:///./fashion_forecast.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development

# CORS (Frontend origins)
# IMPORTANT: Must be JSON array format for pydantic-settings
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

#### Frontend (.env)
```env
# API URLs
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Application
VITE_ENV=development
VITE_DEBUG=true
VITE_USE_MOCK_DATA=false
```

### Troubleshooting

#### CORS Errors
- **Symptom:** Browser console shows "Access to fetch blocked by CORS policy"
- **Fix:**
  1. Ensure `CORS_ORIGINS=http://localhost:5173` in `backend/.env`
  2. Restart the backend server
  3. Clear browser cache (Ctrl+Shift+R)

#### WebSocket Connection Failed
- **Symptom:** Console shows "WebSocket connection failed"
- **Fix:**
  1. Ensure backend is running at http://localhost:8000
  2. Check WebSocket URL uses `ws://` (not `wss://`)
  3. Verify firewall allows WebSocket connections

#### OpenAI API Key Issues
- **Symptom:** Backend logs show "OPENAI_API_KEY is not set or using placeholder"
- **Fix:**
  1. Get API key from https://platform.openai.com/api-keys
  2. Update `OPENAI_API_KEY` in `backend/.env`
  3. Restart backend server

#### Port Already in Use
- **Symptom:** "Address already in use" error
- **Fix:**
  - Backend: Change `PORT` in `backend/.env` or kill process on port 8000
  - Frontend: Vite will prompt you to use an alternative port

### Recommended Tools

- **API Testing:** Postman or Insomnia
- **WebSocket Testing:** wscat (`npm install -g wscat`)
- **VS Code Extensions:**
  - Python
  - ESLint
  - Prettier - Code formatter
  - Tailwind CSS IntelliSense

### Phase 4 Integration Guide

For detailed instructions on Phase 4 integration work, see:
- **Handoff Document:** `04_MVP_Development/implementation/phase_4_integration/PHASE4_HANDOFF.md`
- **Overview:** `04_MVP_Development/implementation/phase_4_integration/PHASE4_OVERVIEW.md`
- **Implementation Plan:** `04_MVP_Development/implementation/phase_4_integration/implementation_plan.md`

---

## Problem Addressed

Based on interviews with 5 retail practitioners, the system addresses:

1. **Inaccurate Demand Forecasting (PP-001)**: 20% forecast error on product launches
2. **Location-Specific Allocation Failures (PP-002, PP-015)**: 5 hrs/week firefighting + ongoing stockout/overstock costs
3. **Late Markdown Decisions (PP-016)**: **$500K lost margin annually**
4. **Inventory Optimization Challenges (PP-028)**: Balancing overstock vs understock across 50 stores

---

## Success Metrics (MVP - Archetype 1)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE (Category-level)** | <20% | Hindcast on mock data (Women's Dresses, 12 weeks) |
| **Bias** | ±5% | Over/under-forecasting check |
| **Workflow Runtime** | <60 seconds | Full 3-agent workflow (Demand → Inventory → Pricing) |
| **Re-forecast Trigger Accuracy** | 90%+ | Correctly identify variance >20% |
| **Human Approval Rate** | Track | % of manufacturing orders approved without modification |
| **LLM Cost** | <$5 | Total for full MVP testing |

---

## Current Status

**November 6, 2025 - Phase 4 Complete | Phase 4.5 In Progress:**

### Implementation Progress
| Phase | Status | Completion |
|-------|--------|------------|
| Phase 1: Data Generation | ✅ Complete | 100% |
| Phase 2: Frontend Foundation | ✅ Complete | 100% |
| Phase 3: Backend Architecture | ✅ Complete | 100% |
| Phase 3.5: Testing & Cleanup | ✅ Complete | 100% |
| **Phase 4: Frontend/Backend Integration** | **✅ Complete** | **100%** |
| **Phase 4.5: Data Upload Infrastructure** | **🔄 In Progress** | **33%** |
| Phase 5: Demand Agent | ⏳ Pending | 0% |
| Phase 6: Inventory Agent | ⏳ Pending | 0% |
| Phase 7: Orchestrator | ⏳ Pending | 0% |
| Phase 8: Pricing Agent | ⏳ Pending | 0% |

### Recent Milestones
- ✅ All v3.3 planning documents complete (7/7)
- ✅ Strategic pivot to parameter-driven architecture
- ✅ Phases 1-3.5 implementation complete
- ✅ **Phase 4 Complete (Nov 4, 2025)**:
  - All 9 stories implemented (PHASE4-001 through PHASE4-009)
  - 8 dashboard sections integrated with backend APIs
  - 36 integration tests created (88% pass rate: 23/28 backend, 13/13 frontend)
  - CSV upload workflows with validation (agent supplementary data)
  - Polling-based workflow monitoring (WebSocket replaced)
  - Real LLM parameter extraction (OpenAI gpt-4o-mini)
  - Comprehensive documentation complete
  - Git branch: `phase4-integration`
- 🔄 **Phase 4.5 In Progress (Nov 6, 2025)**:
  - ✅ Weekly actuals upload with variance monitoring (PHASE4.5-002)
  - ⏳ Historical training data upload (PHASE4.5-001) - pending
  - ⏳ Database schema migration (PHASE4.5-003) - pending
  - Purpose: Bridge Phase 4 and Phase 5 with required training data infrastructure

**Next:** Complete Phase 4.5, then Phase 5 Implementation - Demand Agent (Prophet + ARIMA)

**Progress:** Planning 100% complete | Phases 1-4 complete | Phase 4.5 in progress

---

## 📊 Phase 4 Integration Summary

Phase 4 implemented an **integration-first approach**, connecting all 8 dashboard sections to backend APIs:

### What Was Integrated

✅ **Section 0:** Parameter extraction from natural language
✅ **Section 1:** Real-time WebSocket agent status updates
✅ **Section 2:** Forecast summary with MAPE and manufacturing order
✅ **Section 3:** Store cluster analysis with CSV export
✅ **Section 4:** Weekly performance variance chart
✅ **Section 5:** Replenishment queue (conditional on strategy)
✅ **Section 6:** Markdown decision analysis (conditional on checkpoint)
✅ **Section 7:** Performance metrics dashboard
✅ **CSV Uploads:** Multi-agent data ingestion with validation

### Integration Testing

**Backend (pytest):**
- 28 integration tests created
- 23 passed (82%), 3 failed (mocking issues), 2 skipped (WebSocket)
- 63% code coverage
- Test command: `pytest tests/integration/ -v --cov=app`

**Frontend (Vitest + MSW):**
- 13 integration tests created
- 13 passed (100%)
- MSW (Mock Service Worker) for API mocking
- Test command: `npm run test:coverage`

### Documentation Created

- ✅ Root README updated with Phase 4 status
- ✅ Backend README with all API endpoints
- ✅ Frontend README with component architecture
- ✅ Integration test documentation
- ✅ PHASE4-008-EXECUTION-SUMMARY.md with test results
- ✅ PHASE4-007-IMPLEMENTATION-SUMMARY.md for CSV uploads

### API Endpoints Integrated

| Endpoint | Method | Purpose | Phase |
|----------|--------|---------|-------|
| `/api/v1/parameters/extract` | POST | Extract parameters from natural language | 4 |
| `/api/v1/workflows/forecast` | POST | Create forecast workflow | 4 |
| `/api/v1/workflows/{id}` | GET | Get workflow status (polling) | 4 |
| `/api/v1/forecasts/{id}` | GET | Get forecast summary | 4 |
| `/api/v1/stores/clusters` | GET | Get store clusters | 4 |
| `/api/v1/variance/{id}/week/{week}` | GET | Get weekly variance | 4 |
| `/api/v1/allocations/{id}` | GET | Get store allocations | 4 |
| `/api/v1/markdowns/{id}` | GET | Get markdown analysis | 4 |
| `/api/v1/workflows/{id}/demand/upload` | POST | Upload Demand Agent supplementary CSVs | 4 |
| `/api/v1/workflows/{id}/inventory/upload` | POST | Upload Inventory Agent supplementary CSVs | 4 |
| `/api/v1/workflows/{id}/pricing/upload` | POST | Upload Pricing Agent supplementary CSVs | 4 |
| `/api/v1/data/upload-weekly-sales` | POST | Upload weekly actuals for variance monitoring | 4.5 |

**Full API Documentation:** http://localhost:8000/docs (when backend running)

---

## Contact

**Students:** Boyang Wang, Jintao Li, Yina Liang Li, Jaeyoon Lee, and Henry Tang.
**Supervisor:** Fatih Nayebi
**Institution:** McGill University
**Program:** MMA

---

## License

Academic project - All rights reserved.
