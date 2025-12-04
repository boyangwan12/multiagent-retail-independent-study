# Phase 3 Backend - Progress Tracker

**Team:** Henry & Yina
**Branch:** `phase3-backend-henry-yina`
**Timeline:** 4 days (48 hours)

---

## How to Use BMAD Agent

### First Time Setup (5 mins)

```bash
# 1. Open Claude Code in project directory
claude code

# 2. Activate BMad Orchestrator
/BMad:agents:bmad-orchestrator

# 3. Switch to Developer Agent
*agent dev

# 4. Start first story
Implement Phase 3: Start with story PHASE3-001
```

### After Each Story Completes

```bash
# Option 1: Continue to next story automatically
Continue with next story

# Option 2: Jump to specific story
Start PHASE3-XXX
```

### If Agent Gets Stuck

```bash
# Exit and restart
*exit
/BMad:agents:bmad-orchestrator
*agent dev
Continue with PHASE3-XXX
```

### What the Agent Does

1. **Reads** the story file from `docs/.../stories/PHASE3-XXX.md`
2. **Implements** code using templates in the story
3. **Tests** the code (runs commands from story)
4. **Updates** the story's "Dev Agent Record" section
5. **Tells you** when it's done

### Your Job

- Tell agent which story to do next
- Review the code it writes
- Test the API endpoints (Postman/browser)
- Commit to git after each story
- Update this checklist (change ⬜ to ✅)

---

## Progress: 14/14 Stories Complete

| Story | Title | Assigned | Status | Hours |
|-------|-------|----------|--------|-------|
| PHASE3-001 | Project Setup | Both | ✅ Complete | 2h |
| PHASE3-002 | Database Models | Both | ✅ Complete | 4h |
| PHASE3-003 | Pydantic Schemas | Both | ✅ Complete | 3h |
| PHASE3-004 | FastAPI App | Henry | ✅ Complete | 3h |
| PHASE3-005 | Parameter Extraction | Henry | ✅ Complete | 4h |
| PHASE3-006 | Data Seeding | Yina | ✅ Complete | 2h |
| PHASE3-007 | Workflow Orchestration | Henry | ✅ Complete | 5h |
| PHASE3-008 | WebSocket Server | Yina | ✅ Complete | 4h |
| PHASE3-009 | OpenAI Agents SDK | Henry | ✅ Complete | 6h |
| PHASE3-010 | Approval Endpoints | Yina | ✅ Complete | 3h |
| PHASE3-011 | ML Pipeline | Yina | ✅ Complete | 3h |
| PHASE3-012 | Configuration | Yina | ✅ Complete | 2h |
| PHASE3-013 | Testing & Docs | Yina | ✅ Complete | 3h |
| PHASE3-014 | Data Management | Both | ✅ Complete | 4h |

**Use:** ⬜ Not Started | 🟨 In Progress | ✅ Complete

---

## Day 1 - Foundation (Together)

### Before Starting
- [ ] Create branch: `git checkout -b phase3-backend-henry-yina`
- [ ] Open Claude Code and activate dev agent (see instructions above)

### Stories to Implement
- [ ] Tell agent: `Implement Phase 3: Start with story PHASE3-001`
- [ ] PHASE3-001: Project setup with UV (agent implements)
- [ ] Review code, test server: `uvicorn backend.app.main:app --reload`
- [ ] Tell agent: `Continue with next story`
- [ ] PHASE3-002: Database models (agent implements 10 tables)
- [ ] Test database: `sqlite3 fashion_forecast.db ".tables"`
- [ ] Tell agent: `Continue with next story`
- [ ] PHASE3-003: Pydantic schemas (agent implements)
- [ ] Review schemas in `backend/app/schemas/`

### End of Day
- [ ] Git commit: "Day 1: Foundation (Stories 1-3)"
- [ ] Update progress table above (⬜ → ✅)

---

## Day 2 - Core APIs (Split Work)

**Henry (open separate Claude Code):**
- [ ] Tell agent: `Start PHASE3-004`
- [ ] PHASE3-004: FastAPI app with middleware (agent implements)
- [ ] Test server: `uvicorn backend.app.main:app --reload`
- [ ] Test health endpoint: `curl http://localhost:8000/api/v1/health`
- [ ] Tell agent: `Continue with next story`
- [ ] PHASE3-005: Parameter extraction API (agent implements)
- [ ] **Ask for Azure OpenAI credentials (.env file)**
- [ ] Test extraction: `POST /api/v1/parameters/extract` in Postman

**Yina (open separate Claude Code):**
- [ ] Tell agent: `Start PHASE3-006`
- [ ] PHASE3-006: Data seeding utilities (agent implements)
- [ ] Test seed script: `python backend/scripts/seed_db.py`
- [ ] Verify 50 stores: `sqlite3 fashion_forecast.db "SELECT COUNT(*) FROM stores;"`
- [ ] Tell agent: `Start PHASE3-012`
- [ ] PHASE3-012: Configuration & .env (agent implements)
- [ ] Tell agent: `Continue with next story`
- [ ] PHASE3-013: Testing framework (agent implements)
- [ ] Run tests: `pytest backend/tests/ -v`

### End of Day
- [ ] Pull each other's changes: `git pull origin phase3-backend-henry-yina`
- [ ] Resolve any conflicts
- [ ] Git commit: "Day 2: Core APIs (Stories 4-6, 12-13)"
- [ ] Update progress table above (⬜ → ✅)

---

## Day 3 - Advanced Features (Split Work)

**Henry:**
- [ ] Tell agent: `Start PHASE3-007`
- [ ] PHASE3-007: Workflow orchestration (agent implements)
- [ ] Test workflow: `POST /api/v1/workflows/forecast` in Postman
- [ ] Tell agent: `Continue with next story`
- [ ] PHASE3-009: OpenAI Agents SDK (agent implements) ⚠️ Longest task (6h)
- [ ] Test agent coordination

**Yina:**
- [ ] Tell agent: `Start PHASE3-008`
- [ ] PHASE3-008: WebSocket server (agent implements)
- [ ] Test WebSocket: Browser console or Postman
- [ ] Tell agent: `Continue with next story`
- [ ] PHASE3-010: Approval endpoints (agent implements)
- [ ] Test approve: `POST /api/v1/approvals/{id}/approve`
- [ ] Tell agent: `Continue with next story`
- [ ] PHASE3-011: ML pipeline (agent implements)
- [ ] Review ML scaffolding in `backend/app/ml/`

### End of Day
- [ ] Pull each other's changes: `git pull origin phase3-backend-henry-yina`
- [ ] Resolve any conflicts
- [ ] Git commit: "Day 3: Advanced features (Stories 7-11)"
- [ ] Update progress table above (⬜ → ✅)

---

## Day 4 - Final Story + Testing

### Morning (Together)
- [ ] Tell agent: `Start PHASE3-014`
- [ ] PHASE3-014: Data management endpoints (agent implements)
- [ ] Test CSV upload: `POST /api/v1/data/upload-stores` in Postman
- [ ] Test data export: `GET /api/v1/data/export/stores`
- [ ] Review all code together

### Afternoon (Together)
- [ ] Run all tests: `pytest backend/tests/ -v`
- [ ] Fix any failing tests (ask agent for help)
- [ ] Update README (agent can help)
- [ ] Test all endpoints in Postman
- [ ] Verify OpenAPI docs: http://localhost:8000/docs

### End of Day
- [ ] Git commit: "Day 4: Complete (Story 14)"
- [ ] Update progress table above (⬜ → ✅)

---

## Final Checks (Before Merge to Main)

- [ ] Server starts: `uvicorn backend.app.main:app --reload`
- [ ] OpenAPI docs work: http://localhost:8000/docs
- [ ] Health check works: `curl http://localhost:8000/api/v1/health`
- [ ] Database has 10 tables: `sqlite3 fashion_forecast.db ".tables"`
- [ ] All tests pass: `pytest backend/tests/ -v`
- [ ] No hardcoded secrets (check .env)

---

## Merge to Main

```bash
git checkout main
git pull origin main
git merge --no-ff phase3-backend-henry-yina
git push origin main
```

---

## Presentation Checklist

- [ ] Create 12-15 slides
- [ ] Prepare demo (live or video)
- [ ] Test demo before presentation
- [ ] Take screenshots for slides

---

**Last Updated:** 2025-10-24
