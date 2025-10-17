# Phase 3: Backend Architecture - Technical Decisions

**Phase:** 3 of 8
**Agent:** `*agent architect`
**Date:** 2025-10-17
**Status:** Not Started

---

## Key Decisions Summary

1. UV package manager over pip/poetry (10-100x faster)
2. OpenAI Agents SDK for multi-agent orchestration
3. FastAPI for REST + WebSocket server
4. SQLite with hybrid schema (normalized + JSON columns)
5. Alembic for database migrations
6. Azure OpenAI (gpt-4o-mini) for LLM reasoning
7. Pydantic for data validation and settings
8. Monorepo structure (backend + frontend in same repo)
9. Parameter extraction via LLM (natural language → structured JSON)
10. Mock ML models in Phase 3 (actual implementation in Phase 5-7)

---

## Decision Log

### Decision 1: UV vs pip/poetry for Package Management
**Date:** TBD
**Context:** Need fast, reliable Python dependency management

**Options Considered:**
1. **pip + venv**
   - Pros: Standard, widely used, familiar
   - Cons: Slow dependency resolution (minutes for large projects)

2. **Poetry**
   - Pros: Better dependency resolution, lock files
   - Cons: Still slow, complex configuration, heavy

3. **UV**
   - Pros: 10-100x faster than pip, built-in venv, compatible with pyproject.toml
   - Cons: Newer tool (less Stack Overflow), smaller ecosystem

**Decision:** UV

**Rationale:** Speed is critical for MVP iteration. UV resolves dependencies in seconds vs minutes. OpenAI recommends UV for Agents SDK projects. Compatible with standard pyproject.toml format.

**Implementation Notes:**
```bash
pip install uv
uv init
uv add fastapi uvicorn openai-agents-sdk
uv run python backend/app/main.py
```

---

### Decision 2: OpenAI Agents SDK vs Alternatives
**Date:** TBD
**Context:** Need multi-agent orchestration with handoffs and parameter passing

**Options Considered:**
1. **LangGraph**
   - Pros: Powerful graph-based workflows, LangChain ecosystem
   - Cons: Steep learning curve, complex for simple handoffs, overkill for MVP

2. **AutoGen**
   - Pros: Microsoft-backed, multi-agent conversations
   - Cons: Less mature, fewer production features, unclear longevity

3. **OpenAI Agents SDK**
   - Pros: Official OpenAI tool, built for Responses API, handoffs built-in, production-ready
   - Cons: Newer (v0.3.3), smaller community than LangChain

**Decision:** OpenAI Agents SDK

**Rationale:** Designed specifically for our use case (sequential agent handoffs with context). Uses Responses API (not deprecated Chat Completions). Simpler mental model than LangGraph. Official OpenAI support.

**Implementation Notes:**
```python
from openai_agents import Agent

orchestrator = Agent(
    name="Orchestrator",
    model="gpt-4o-mini",
    handoffs=["demand", "inventory", "pricing"],
    context={"parameters": season_parameters}
)
```

---

### Decision 3: Database Choice (SQLite vs PostgreSQL)
**Date:** TBD
**Context:** Need persistent storage for forecasts, allocations, parameters

**Options Considered:**
1. **PostgreSQL**
   - Pros: Production-ready, JSONB support, better performance
   - Cons: Requires Docker/server setup, overkill for MVP, deployment complexity

2. **SQLite**
   - Pros: Zero config, file-based, sufficient for MVP (<10k rows), easy to reset
   - Cons: No concurrent writes, not scalable for production

**Decision:** SQLite (with migration path to PostgreSQL)

**Rationale:** MVP runs locally, single user. SQLite eliminates Docker dependency. SQLAlchemy makes migration to PostgreSQL trivial (change connection string only).

**Implementation Notes:**
```python
DATABASE_URL = "sqlite:///./fashion_forecast.db"
engine = create_engine(DATABASE_URL)
```

**Migration Strategy:** Use SQLAlchemy ORM. When ready for production, change to `postgresql://...` - no code changes needed.

---

### Decision 4: Hybrid Database Schema (Normalized + JSON)
**Date:** TBD
**Context:** Need to store both structured entities and flexible arrays

**Options Considered:**
1. **Fully Normalized**
   - Pros: Relational integrity, easy queries
   - Cons: Complex joins for weekly_demand_curve (12+ rows per forecast)

2. **Fully JSON (NoSQL)**
   - Pros: Flexible, matches Pydantic models
   - Cons: No referential integrity, harder to query

3. **Hybrid (Normalized + JSON columns)**
   - Pros: Best of both worlds, SQLite supports JSON
   - Cons: Slightly more complex schema design

**Decision:** Hybrid approach

**Rationale:**
- Normalized: categories, stores, store_clusters, season_parameters (referential integrity)
- JSON columns: weekly_demand_curve, store_allocations, cluster_distribution (flexibility)

**Implementation Notes:**
```python
class Forecast(Base):
    forecast_id = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.category_id"))  # Normalized
    weekly_demand_curve = Column(JSON)  # [{week: 1, demand: 450}, ...]
```

---

### Decision 5: FastAPI vs Flask/Django
**Date:** TBD
**Context:** Need REST API + WebSocket server

**Options Considered:**
1. **Flask**
   - Pros: Mature, large ecosystem, simple
   - Cons: No async support, no WebSocket, manual OpenAPI docs

2. **Django + DRF**
   - Pros: Batteries-included, admin panel
   - Cons: Heavy, ORM lock-in, async support limited

3. **FastAPI**
   - Pros: Async native, WebSocket built-in, auto OpenAPI docs, Pydantic integration
   - Cons: Newer framework, smaller ecosystem

**Decision:** FastAPI

**Rationale:** Async critical for WebSocket agent updates. Auto-generated OpenAPI docs (/docs) save time. Pydantic integration eliminates manual validation. Modern Python (type hints, async/await).

**Implementation Notes:**
```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.post("/api/parameters/extract")
async def extract_parameters(request: ParameterExtractionRequest):
    ...

@app.websocket("/ws/{workflow_id}")
async def websocket_endpoint(websocket: WebSocket, workflow_id: str):
    ...
```

---

### Decision 6: Parameter Extraction Strategy
**Date:** TBD
**Context:** Need to extract 5 structured parameters from natural language

**Options Considered:**
1. **Structured Form (Dropdowns + Inputs)**
   - Pros: Predictable, easy validation
   - Cons: Poor UX, doesn't demonstrate LLM intelligence, rigid

2. **LLM Function Calling**
   - Pros: Structured output, OpenAI built-in
   - Cons: Requires gpt-4 (expensive), more complex

3. **LLM with Structured Prompt (JSON output)**
   - Pros: Works with gpt-4o-mini (cheaper), flexible, good UX
   - Cons: May need fallback for ambiguous input

**Decision:** LLM with structured prompt + validation

**Rationale:** Demonstrates parameter-driven innovation. gpt-4o-mini sufficient for extraction (90%+ accuracy). Frontend confirmation modal catches LLM errors.

**Implementation Notes:**
```python
prompt = f"""
Extract 5 parameters from user input. Return JSON only.

Parameters:
1. forecast_horizon_weeks (int, 1-52, default 12)
2. season_start_date (YYYY-MM-DD, default next Monday)
3. replenishment_strategy ("none"/"weekly"/"bi-weekly", default "weekly")
4. dc_holdback_percentage (float 0.0-1.0, default 0.45)
5. markdown_checkpoint_week (int or null, default null)

User Input: "{user_input}"
"""

response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[...])
parameters = SeasonParameters(**json.loads(response.content))
```

---

### Decision 7: WebSocket Message Format
**Date:** TBD
**Context:** Real-time agent status updates to frontend

**Options Considered:**
1. **Simple String Messages**
   - Pros: Easy to implement
   - Cons: No structure, hard to parse, error-prone

2. **JSON with type field**
   - Pros: Structured, extensible, type-safe
   - Cons: Slightly more verbose

**Decision:** JSON messages with type discriminator

**Rationale:** TypeScript frontend needs structure. Allows multiple message types (agent_status, error, approval_request).

**Implementation Notes:**
```json
{
  "type": "agent_status",
  "workflow_id": "wf_12345",
  "agent": "demand",
  "status": "thinking",
  "message": "Analyzing historical sales patterns...",
  "progress": 0.35,
  "timestamp": "2025-10-17T14:23:45Z"
}
```

---

### Decision 8: Mock ML Models in Phase 3
**Date:** TBD
**Context:** Need to scaffold ML pipeline without blocking backend development

**Options Considered:**
1. **Implement Prophet/ARIMA now**
   - Pros: Complete integration, realistic testing
   - Cons: Blocks backend work, complex debugging, Phase 5 scope

2. **Return hardcoded values**
   - Pros: Simple, fast
   - Cons: Not realistic, hard to test variance triggers

3. **Return mock data with variation**
   - Pros: Realistic enough for testing, fast, unblocks backend
   - Cons: Not actual forecasts

**Decision:** Mock models with realistic variation

**Rationale:** Phase 3 focuses on backend architecture. Actual ML happens in Phase 5-7. Mock data sufficient to test API contracts, agent handoffs, and WebSocket.

**Implementation Notes:**
```python
def prophet_forecast_mock(historical_data):
    """Returns mock forecast with realistic seasonality"""
    base_demand = 650
    weekly_curve = [
        {"week": w, "demand": int(base_demand * seasonal_multiplier(w))}
        for w in range(1, 13)
    ]
    return {"total": sum(d["demand"] for d in weekly_curve), "weekly": weekly_curve}
```

---

### Decision 9: Monorepo vs Separate Repos
**Date:** TBD
**Context:** Manage backend + frontend codebases

**Options Considered:**
1. **Separate repos (backend/, frontend/)**
   - Pros: Clean separation, independent deployments
   - Cons: Slower iteration, complex atomic changes, overkill for solo MVP

2. **Monorepo**
   - Pros: Single source of truth, atomic commits, faster iteration
   - Cons: Larger repo, mixed languages

**Decision:** Monorepo

**Rationale:** Solo development MVP. Atomic commits critical for API contract changes (backend endpoint + frontend call). Easier to review full feature changes.

**Implementation Notes:**
```
project-root/
├── backend/
│   ├── app/
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
├── docs/
└── data/
```

---

### Decision 10: Alembic for Migrations
**Date:** TBD
**Context:** Need database schema versioning

**Options Considered:**
1. **Manual SQL scripts**
   - Pros: Simple, full control
   - Cons: Error-prone, no rollback, hard to sync with models

2. **SQLAlchemy create_all()**
   - Pros: Simple, auto-generates schema
   - Cons: No versioning, can't rollback, production risk

3. **Alembic**
   - Pros: Versioned migrations, rollback support, autogenerate from models
   - Cons: Learning curve, extra tooling

**Decision:** Alembic

**Rationale:** Production-grade approach. Autogenerate detects model changes. Rollback critical for development. SQLAlchemy integration seamless.

**Implementation Notes:**
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head  # Apply
alembic downgrade -1  # Rollback
```

---

## Key Metrics (TBD after implementation)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| API Endpoints | 12 | TBD | TBD |
| Database Tables | 8 | TBD | TBD |
| Agent Scaffolds | 4 | TBD | TBD |
| Test Coverage | >70% | TBD | TBD |
| Parameter Extraction Accuracy | >85% | TBD | TBD |
| API Response Time (p95) | <500ms | TBD | TBD |

---

## Future Enhancements

### Enhancement 1: Migrate to PostgreSQL
**Description:** Replace SQLite with PostgreSQL for production
**Benefit:** Concurrent writes, better performance, production-ready
**Effort:** Low (change connection string only)
**Priority:** Medium (needed for multi-user production)

### Enhancement 2: Redis for Caching
**Description:** Cache parameter extraction results, forecast responses
**Benefit:** Faster repeated queries, reduce OpenAI API calls
**Effort:** Medium (add Redis client, implement cache layer)
**Priority:** Low (acceptable for MVP)

### Enhancement 3: Celery for Background Tasks
**Description:** Run long ML tasks asynchronously with Celery
**Benefit:** Non-blocking API, better UX for slow forecasts
**Effort:** High (setup Celery + Redis broker)
**Priority:** Low (synchronous OK for MVP)

---

## Key Takeaways (to be filled after implementation)

### What Worked Well
- TBD

### Lessons Learned
- TBD

### For Next Phase (Phase 4: Orchestrator Agent)
- TBD

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Phase 3 Not Started
