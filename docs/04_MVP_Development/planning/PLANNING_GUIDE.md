# Planning Guide

**Status**: All Planning Complete (6/6) → Ready for Implementation!
**Last Updated**: 2025-10-14
**Workflow**: BMad Method with specialized agents

---

## ✅ Completed Planning Documents (v3.2)

| Document | Status | BMad Agent | Output Path |
|----------|--------|------------|-------------|
| **Product Brief v3.2** | ✅ Complete | `*agent architect` | `product_brief/product_brief_v3.2.md` |
| **Process Workflow v3.2** | ✅ Complete | `*agent architect` | `process_workflow/process_workflow_v3.2.md` |
| **Technical Architecture v3.2** | ✅ Complete | `*agent architect` | `architecture/technical_architecture_v3.2.md` |
| **Frontend UI/UX Spec v3.2** | ✅ Complete | `*agent ux-expert` | `design/front-end-spec_v3.2.md` |
| **Data Specification v3.2** | ✅ Complete | `*agent architect` | `data/data_specification_v3.2.md` |
| **PRD v3.2** | ✅ Complete | `*agent pm` | `prd/prd_v3.2.md` |

**Key Achievements:**
- ✅ All documents aligned (no contradictions)
- ✅ Category auto-detection implemented
- ✅ Linear Dark Theme design system defined
- ✅ Complete API contracts + data models
- ✅ All wireframes and user flows complete
- ✅ Comprehensive data spec with dictionary, validation, and realism strategies
- ✅ Formal PRD with 18 user stories, 50+ functional requirements, quantifiable success metrics

---

## 🚀 Implementation Roadmap (Ready to Start!)

### **Phase 1: Data Preparation** (Week 5)
**BMad Agent**: `*agent dev`
**Task**: Create mock data generation script

**Deliverables**:
- Python script: `data/mock/generate_mock_data.py`
- 38 CSV files total:
  - `training/historical_sales_2022_2024.csv` (~54,750 rows)
  - `training/store_attributes.csv` (50 stores)
  - `scenarios/normal_season/actuals_week_01.csv` to `actuals_week_12.csv`
  - `scenarios/high_demand/actuals_week_01.csv` to `actuals_week_12.csv`
  - `scenarios/low_demand/actuals_week_01.csv` to `actuals_week_12.csv`
- README.md with usage guide and data dictionary
- Validation suite (6 types)
- Target MAPE: 12-18%

**Reference Documents**:
- `data/data_specification_v3.2.md` (complete implementation guide)

**How to Start**:
```
*agent dev
Task: Implement mock data generation script based on data_specification_v3.2.md
Output: generate_mock_data.py + 38 CSV files + README.md + validation suite
```

**Priority**: **HIGH** (blocks backend development)

---

### **Phase 2: Backend Implementation** (Week 5-8)
**BMad Agent**: `*agent dev` (same agent, continuous work)
**Task**: Implement 3-agent system using OpenAI Agents SDK

**Deliverables**:
- Project structure: `backend/` with `agents/`, `api/`, `ml/` folders
- **Demand Agent**: Prophet + ARIMA ensemble, K-means clustering (7 features), allocation logic
- **Inventory Agent**: Manufacturing calculation, hierarchical allocation, replenishment
- **Pricing Agent**: Gap × Elasticity markdown, sell-through tracking
- **Orchestrator**: Workflow coordination, variance monitoring (>20% threshold)
- REST API + WebSocket implementation

**Reference Documents**:
- `architecture/technical_architecture_v3.2.md` (Section 9: ML Approach, Section 11: API Contracts)
- `data/data_specification_v3.2.md` (data models, validation criteria)

**How to Start**:
```
*agent dev
Task: Implement backend 3-agent system with OpenAI Agents SDK
```

**Priority**: **HIGH**

---

### **Phase 3: Frontend Implementation** (Week 9-12)
**BMad Agent**: `*agent dev` (same agent, full-stack development)
**Task**: Build single-page dashboard with Linear Dark Theme

**Deliverables**:
- Project structure: `frontend/` with React + TypeScript + Vite
- 7-section single-page dashboard:
  1. Agent progress cards (3 cards with real-time status)
  2. Forecast results table
  3. Store cluster analysis
  4. Weekly forecast chart
  5. Replenishment schedule
  6. Markdown recommendations
  7. System metrics
- WebSocket integration (line-by-line agent progress)
- Linear Dark Theme (Shadcn/ui + Tailwind CSS)
- Report page: `/reports/spring-2025`

**Reference Documents**:
- `design/front-end-spec_v3.2.md` (complete UI/UX specification)
- `architecture/technical_architecture_v3.2.md` (API contracts, WebSocket events)

**How to Start**:
```
*agent dev
Task: Build React dashboard with 7-section layout and Linear Dark Theme
```

**Priority**: **HIGH**

---

### **Phase 4: Testing & Validation** (Week 13-14)
**BMad Agent**: `*agent qa`
**Task**: Validate system accuracy and functionality

**Deliverables**:
- Test 3 scenarios: normal season, high demand, low demand
- Validate forecast accuracy: MAPE 12-18% (per data spec)
- Test variance-triggered re-forecast (>20% threshold)
- Test Week 6 markdown logic (60% sell-through target)
- E2E testing: CSV upload → forecast → allocation → markdown → report
- Bug tracking and test reports

**Reference Documents**:
- `data/data_specification_v3.2.md` (Section 7: Testing Workflow, expected MAPE ranges)
- `process_workflow/process_workflow_v3.2.md` (expected behavior)

**How to Start**:
```
*agent qa
Task: Test 3 scenarios and validate MAPE accuracy
```

**Priority**: **HIGH**

---

## 🎯 BMad-Optimized Workflow Summary

### **What Makes This BMad-Optimized?**

✅ **Fewer Agent Switches** - Use `*agent dev` for data prep + backend + frontend (full-stack)
✅ **No Unnecessary Roles** - Removed Scrum Master, Product Owner (not needed for PoC)
✅ **Comprehensive Planning** - 5 complete v3.2 docs cover all requirements (Product Brief, Process Workflow, Technical Architecture, Frontend Spec, Data Spec)
✅ **Agent Specialization** - Only switch agents when truly needed (`*agent pm` → `*agent dev` → `*agent qa`)
✅ **Formal PRD Required** - PRD v3.2 needed for formal requirements and acceptance criteria

### **Agents You'll Actually Use**

| BMad Agent | When to Use | Why |
|------------|-------------|-----|
| `*agent pm` | **Phase 0: PRD Creation** | Formal requirements, user stories, acceptance criteria |
| `*agent dev` | **Phases 1-3: Implementation** | Full-stack development (data + backend + frontend) |
| `*agent qa` | **Phase 4: Testing** | Quality assurance, E2E testing, bug tracking |

### **Agents You WON'T Need**

❌ `*agent sm` (Scrum Master) - No sprint ceremonies for solo/small team PoC
❌ `*agent po` (Product Owner) - No ongoing backlog management needed
❌ `*agent data` - Use `*agent dev` for data generation scripts
❌ `*agent frontend` - Use `*agent dev` (handles full-stack)

---

## 📊 Progress Tracking

### ✅ Planning & Documentation Phase (6/6 Complete!)
- [x] Product Brief v3.2
- [x] Process Workflow v3.2
- [x] Technical Architecture v3.2
- [x] Frontend UI/UX Spec v3.2
- [x] Data Specification v3.2
- [x] **PRD v3.2** ← JUST COMPLETED!

**Total Documentation**: 6,000+ lines across 6 comprehensive documents

### ⏳ Implementation Phase (4 Phases Remaining)
- [ ] **Phase 1: Mock Data Generation** (`*agent dev`) ← **START HERE!**
- [ ] Phase 2: Backend Implementation (`*agent dev`)
- [ ] Phase 3: Frontend Implementation (`*agent dev`)
- [ ] Phase 4: Testing & Validation (`*agent qa`)

---

## 🚀 What to Do Right Now

### **Start Phase 1: Mock Data Generation** (Ready!)
```
*agent dev

Task: Implement mock data generation script based on data_specification_v3.2.md
Output: generate_mock_data.py + 38 CSV files + README.md + validation suite
```

**Why start here?**
- ✅ All 6 planning documents complete (6,000+ lines!)
- ✅ Data spec has complete implementation guide (Section 6: Implementation Guidance)
- ✅ Blocks backend development (need training data to train Prophet+ARIMA)
- ✅ Takes 1-2 days to implement

**After Phase 1 completes:**
1. Continue with same `*agent dev` for backend implementation
2. Continue with same `*agent dev` for frontend implementation
3. Switch to `*agent qa` for testing & validation

**Quick Start**: Copy the Phase 1 handoff message from the section below!

---

## 📝 Recent Updates (2025-10-14)

### ✅ Added: Data Specification v3.2
- **Complete data dictionary** for 3 CSV types (historical, store attributes, weekly actuals)
- **6 realism strategies** to achieve MAPE 12-18% (not suspiciously perfect)
- **3 scenario definitions** (Normal, High Demand, Low Demand) with black swan events
- **Validation suite** with 6 check types
- **Implementation guide** with code examples for key functions
- **Testing workflow** with expected variance ranges per week
- **README.md template** for data/mock/ folder

### ✅ Updated: Frontend Spec v3.2
- **Added Flow 2A**: Upload Weekly Actuals (critical workflow was missing)
- User must upload previous week's actuals CSV every Monday
- System calculates variance, triggers re-forecast if >20%

### ✅ Completed: PRD v3.2 (1,895 lines!)
- **PRD v3.2 COMPLETE** - Ready for implementation!
- 18 user stories across 5 workflow phases
- 50+ functional requirements (FR-1 through FR-10)
- 6 NFR categories with quantifiable targets
- 10 success metrics (MAPE 12-18%, business impact, performance)
- 12-week release plan with milestones
- References all 5 v3.2 planning docs

---

---

## 📦 Agent Handoff Messages (Copy & Paste)

### ~~**Phase 0: Create PRD v3.2**~~ ✅ COMPLETE!

PRD v3.2 has been created (1,895 lines) with:
- 18 user stories across 5 workflow phases
- 50+ functional requirements
- 6 NFR categories with quantifiable targets
- 10 success metrics
- 12-week release plan

**Location**: `docs/04_PoC_Development/prd/prd_v3.2.md`

---

### **Phase 1: Mock Data Generation** → Use `*agent dev`

```
*agent dev

Task: Implement mock data generation script for Fashion Retail PoC

Reference Documents:
- docs/04_PoC_Development/data/data_specification_v3.2.md (primary implementation guide)
- docs/04_PoC_Development/prd/prd_v3.2.md (acceptance criteria)
- docs/04_PoC_Development/architecture/technical_architecture_v3.2.md (Section 9: ML Approach, data models)

Key Requirements:
1. Generate 38 CSV files (1 historical + 1 store attributes + 36 weekly actuals)
2. Implement 6 realism strategies to achieve MAPE 12-18%
3. Create 3 scenarios: normal_season, high_demand, low_demand
4. Include black swan events in Week 5 for all scenarios
5. Pure Python (numpy + pandas only)
6. Fixed seed (42) + --regenerate flag
7. Validation suite (6 types)
8. README.md with data dictionary

Output:
- data/mock/generate_mock_data.py
- data/mock/training/historical_sales_2022_2024.csv (~54,750 rows)
- data/mock/training/store_attributes.csv (50 stores)
- data/mock/scenarios/normal_season/ (12 weekly CSVs)
- data/mock/scenarios/high_demand/ (12 weekly CSVs)
- data/mock/scenarios/low_demand/ (12 weekly CSVs)
- data/mock/README.md
```

---

### **Phase 2: Backend Implementation** → Use `*agent dev`

```
*agent dev

Task: Implement 3-agent demand forecasting system using OpenAI Agents SDK

Reference Documents:
- docs/04_PoC_Development/architecture/technical_architecture_v3.2.md (primary implementation guide)
- docs/04_PoC_Development/prd/prd_v3.2.md (acceptance criteria)
- docs/04_PoC_Development/data/data_specification_v3.2.md (data models, CSV formats)
- docs/04_PoC_Development/process_workflow/process_workflow_v3.2.md (agent behavior examples)

Key Requirements:
1. Demand Agent: Prophet+ARIMA ensemble, K-means clustering (7 features), hierarchical allocation
2. Inventory Agent: Manufacturing calculation, 55%/45% allocation, weekly replenishment
3. Pricing Agent: Gap × Elasticity markdown, sell-through tracking, Week 6 checkpoint
4. Orchestrator: Workflow coordination, variance monitoring (>20% trigger), re-forecast logic
5. REST API (FastAPI) + WebSocket for real-time progress
6. SQLite database for session persistence
7. Use training data from data/mock/training/

Tech Stack:
- Python 3.11+
- FastAPI
- OpenAI Agents SDK
- Prophet + statsmodels (ARIMA)
- scikit-learn (K-means)
- SQLite

Output:
- backend/agents/ (demand_agent.py, inventory_agent.py, pricing_agent.py, orchestrator.py)
- backend/api/ (routes, WebSocket handlers)
- backend/ml/ (forecasting, clustering, allocation logic)
- backend/database/ (SQLite schema)
```

---

### **Phase 3: Frontend Implementation** → Use `*agent dev`

```
*agent dev

Task: Build single-page React dashboard with Linear Dark Theme

Reference Documents:
- docs/04_PoC_Development/design/front-end-spec_v3.2.md (primary implementation guide)
- docs/04_PoC_Development/architecture/technical_architecture_v3.2.md (Section 11: API contracts, WebSocket events)
- docs/04_PoC_Development/prd/prd_v3.2.md (user stories, acceptance criteria)

Key Requirements:
1. 7-section single-page dashboard:
   - Section 1: Agent progress cards (3 cards, real-time WebSocket updates)
   - Section 2: Forecast results table (category-level, 12 weeks)
   - Section 3: Store cluster analysis (3 clusters, allocation factors)
   - Section 4: Weekly forecast chart (forecast vs actuals, variance overlay)
   - Section 5: Replenishment schedule (weekly manufacturing + DC releases)
   - Section 6: Markdown recommendations (Week 6 checkpoint, Gap × Elasticity)
   - Section 7: System metrics (MAPE, variance, sell-through)
2. Linear Dark Theme (Shadcn/ui + Tailwind CSS)
3. WebSocket integration for line-by-line agent progress
4. CSV upload workflows (historical data + weekly actuals)
5. Report page: /reports/spring-2025

Tech Stack:
- React 18+
- TypeScript
- Vite
- Shadcn/ui
- Tailwind CSS
- Recharts (for charts)

Output:
- frontend/src/components/ (Dashboard, AgentCard, ForecastTable, etc.)
- frontend/src/pages/ (Dashboard.tsx, Report.tsx)
- frontend/src/hooks/ (useWebSocket, useForecast)
- frontend/src/styles/ (Linear Dark Theme)
```

---

### **Phase 4: Testing & Validation** → Use `*agent qa`

```
*agent qa

Task: Test 3 scenarios and validate system accuracy

Reference Documents:
- docs/04_PoC_Development/data/data_specification_v3.2.md (Section 7: Testing Workflow, expected MAPE ranges)
- docs/04_PoC_Development/prd/prd_v3.2.md (acceptance criteria)
- docs/04_PoC_Development/process_workflow/process_workflow_v3.2.md (expected system behavior)

Test Scenarios:
1. Normal Season: MAPE 12-15%, Week 5 variance ~25% (viral TikTok trend)
2. High Demand: MAPE 15-18%, Week 5 variance ~32% (competitor bankruptcy)
3. Low Demand: MAPE 15-18%, Week 5 variance ~28% (supply chain disruption)

Key Test Cases:
1. E2E Workflow: CSV upload → forecast → allocation → markdown → report
2. Variance-triggered re-forecast (>20% threshold in Week 5)
3. Week 6 markdown logic (if sell-through <60%)
4. WebSocket real-time updates
5. Store cluster allocation accuracy
6. Data validation (6 types from data spec)

Validation Criteria:
- MAPE between 12-18% (not <10% = too perfect, not >20% = unusable)
- Week 5 variance >20% in all scenarios (black swan detection)
- Re-forecast improves accuracy in Weeks 6-12
- All CSV formats match data specification

Output:
- Test reports (pass/fail for each scenario)
- Bug tracking (if any issues found)
- Performance metrics (API response times, forecast accuracy)
```

---

**Ready to start implementation?** Copy the Phase 1 message above and run:
```
*agent dev
```
