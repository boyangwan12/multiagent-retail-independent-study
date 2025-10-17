# Planning Guide

**Status**: All Planning Complete (6/6 v3.3) → Ready for Implementation!
**Last Updated**: 2025-10-16
**Version**: v3.3 - Parameter-Driven Architecture
**Workflow**: BMad Method with specialized agents

---

## ✅ Completed Planning Documents (v3.3 - Parameter-Driven)

| Document | Status | BMad Agent | Output Path |
|----------|--------|------------|-------------|
| **Product Brief v3.3** | ✅ Complete | `*agent architect` | `1_product_brief_v3.3.md` |
| **Process Workflow v3.3** | ✅ Complete | `*agent architect` | `2_process_workflow_v3.3.md` |
| **Technical Architecture v3.3** | ✅ Complete | `*agent architect` | `3_technical_architecture_v3.3.md` |
| **PRD v3.3** | ✅ Complete | `*agent pm` | `4_prd_v3.3.md` |
| **Frontend UI/UX Spec v3.3** | ✅ Complete | `*agent ux-expert` | `5_front-end-spec_v3.3.md` |
| **Data Specification v3.2** | ✅ Complete | `*agent architect` | `6_data_specification_v3.2.md` |

**Key Achievements (v3.3 - Parameter-Driven):**
- ✅ **⭐ NEW: Natural language parameter extraction** - LLM extracts 5 key parameters from user input
- ✅ **⭐ NEW: Agent autonomous reasoning** - Agents adapt behavior based on parameters using LLM intelligence
- ✅ **⭐ NEW: Conditional phase execution** - Replenishment phase skipped when strategy = "none"
- ✅ **⭐ NEW: Phase 0 (Parameter Gathering)** - Complete UI/UX for parameter extraction and confirmation
- ✅ All documents aligned (no contradictions between v3.3 updates)
- ✅ Category auto-detection implemented
- ✅ Linear Dark Theme design system defined
- ✅ Complete API contracts + data models + NEW parameter extraction endpoint
- ✅ All wireframes and user flows complete (including Flow 0: Parameter Gathering)
- ✅ Comprehensive data spec with dictionary, validation, and realism strategies
- ✅ Formal PRD with 22 user stories (4 new for Phase 0), 50+ functional requirements, quantifiable success metrics

---

## 🚀 Implementation Roadmap (Ready to Start!)

### **⭐ Phase 0: Parameter Extraction Service** (Week 1) - NEW in v3.3
**BMad Agent**: `*agent dev`
**Task**: Implement natural language parameter extraction using Azure OpenAI

**Deliverables**:
- Parameter extraction API endpoint: `POST /api/parameters/extract`
- Pydantic model: `SeasonParameters` with 5 key parameters
- ReplenishmentStrategy enum (NONE, WEEKLY, BI_WEEKLY)
- LLM integration with Azure OpenAI gpt-4o-mini
- Parameter validation and confidence scoring
- Unit tests for parameter extraction logic

**Reference Documents**:
- `3_technical_architecture_v3.3.md` (Section: Parameter Extraction API)
- `4_prd_v3.3.md` (Section 4.0: Parameter Gathering user stories)

**How to Start**:
```
*agent dev
Task: Implement parameter extraction API endpoint with Azure OpenAI gpt-4o-mini
Output: POST /api/parameters/extract endpoint + SeasonParameters model + unit tests
```

**Priority**: **HIGHEST** (required before any agent logic)

---

### **Phase 1: Data Preparation** (Week 2)
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
- `6_data_specification_v3.2.md` (complete implementation guide)

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
- `3_technical_architecture_v3.3.md` (Section 9: ML Approach, Section 11: API Contracts)
- `6_data_specification_v3.2.md` (data models, validation criteria)

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
- `5_front-end-spec_v3.3.md` (complete UI/UX specification)
- `3_technical_architecture_v3.3.md` (API contracts, WebSocket events)

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
- `6_data_specification_v3.2.md` (Section 7: Testing Workflow, expected MAPE ranges)
- `2_process_workflow_v3.3.md` (expected behavior)

**How to Start**:
```
*agent qa
Task: Test 3 scenarios and validate MAPE accuracy
```

**Priority**: **HIGH**

---

## 🎯 BMad-Optimized Workflow Summary

### **What Makes This BMad-Optimized?**

✅ **Fewer Agent Switches** - Use `*agent dev` for parameters + data prep + backend + frontend (full-stack)
✅ **No Unnecessary Roles** - Removed Scrum Master, Product Owner (not needed for MVP)
✅ **Comprehensive Planning** - 6 complete v3.3 docs cover all requirements (Product Brief, Process Workflow, Technical Architecture, Frontend Spec, PRD, Data Spec)
✅ **Agent Specialization** - Only switch agents when truly needed (`*agent pm` → `*agent dev` → `*agent qa`)
✅ **Formal PRD Required** - PRD v3.3 with parameter-driven requirements and acceptance criteria
✅ **⭐ Parameter-Driven Architecture** - Single codebase adapts to multiple retail scenarios via 5 key parameters

### **Agents You'll Actually Use**

| BMad Agent | When to Use | Why |
|------------|-------------|-----|
| `*agent pm` | **Planning Phase: PRD Creation** | Formal requirements, user stories, acceptance criteria |
| `*agent dev` | **⭐ Phase 0-3: Implementation** | Full-stack development (parameters + data + backend + frontend) |
| `*agent qa` | **Phase 4: Testing** | Quality assurance, E2E testing, bug tracking |

### **Agents You WON'T Need**

❌ `*agent sm` (Scrum Master) - No sprint ceremonies for solo/small team MVP
❌ `*agent po` (Product Owner) - No ongoing backlog management needed
❌ `*agent data` - Use `*agent dev` for data generation scripts
❌ `*agent frontend` - Use `*agent dev` (handles full-stack)
❌ `*agent backend` - Use `*agent dev` (handles full-stack)

---

## 📊 Progress Tracking

### ✅ Planning & Documentation Phase (6/6 Complete - v3.3!)
- [x] Product Brief v3.3 ⭐ Parameter-Driven
- [x] Process Workflow v3.3 ⭐ Parameter-Driven
- [x] Technical Architecture v3.3 ⭐ Parameter-Driven
- [x] Frontend UI/UX Spec v3.3 ⭐ Parameter-Driven
- [x] Data Specification v3.2
- [x] **PRD v3.3** ⭐ Parameter-Driven ← JUST COMPLETED!

**Total Documentation**: 6,500+ lines across 6 comprehensive documents

### ⏳ Implementation Phase (5 Phases Remaining)
- [ ] **⭐ Phase 0: Parameter Extraction Service** (`*agent dev`) ← **START HERE!**
- [ ] Phase 1: Mock Data Generation (`*agent dev`)
- [ ] Phase 2: Backend Implementation (`*agent dev`)
- [ ] Phase 3: Frontend Implementation (`*agent dev`)
- [ ] Phase 4: Testing & Validation (`*agent qa`)

---

## 🚀 What to Do Right Now

### **⭐ Start Phase 0: Parameter Extraction Service** (Ready!)
```
*agent dev

Task: Implement parameter extraction API endpoint with Azure OpenAI gpt-4o-mini
Output: POST /api/parameters/extract endpoint + SeasonParameters model + unit tests
```

**Why start here?**
- ✅ All 6 planning documents complete (6,500+ lines, v3.3 parameter-driven!)
- ✅ **HIGHEST PRIORITY** - Required before any agent logic can be implemented
- ✅ Enables parameter-driven architecture (core innovation of v3.3)
- ✅ Technical Architecture v3.3 has complete implementation guide
- ✅ Takes 1-2 days to implement

**After Phase 0 completes:**
1. Continue with same `*agent dev` for Phase 1 (mock data generation)
2. Continue with same `*agent dev` for Phase 2 (backend 3-agent system)
3. Continue with same `*agent dev` for Phase 3 (frontend dashboard)
4. Switch to `*agent qa` for Phase 4 (testing & validation)

**Quick Start**: Copy the Phase 0 handoff message from the "Implementation Roadmap" section above!

---

## 📝 Recent Updates

### ⭐ v3.3 Updates (2025-10-16) - Parameter-Driven Architecture

**Major Architectural Shift**: From hardcoded "Archetype 1" to parameter-driven generic system

### ✅ Updated: Product Brief v3.3
- **Parameter-driven vision** replacing hardcoded Archetype 1
- Natural language parameter extraction as core innovation
- Agent autonomous reasoning capabilities
- 5 key parameters: forecast horizon, season dates, replenishment strategy, DC holdback, markdown timing

### ✅ Updated: Process Workflow v3.3
- **Added Phase 0**: Parameter Gathering (before existing 5 phases)
- LLM extracts structured parameters from free-form user input
- Agents receive parameters via Orchestrator context
- Conditional phase execution (replenishment phase skipped when strategy = "none")
- Agent reasoning examples throughout all phases

### ✅ Updated: Technical Architecture v3.3
- **New endpoint**: POST /api/parameters/extract
- SeasonParameters Pydantic model with ReplenishmentStrategy enum
- Azure OpenAI gpt-4o-mini integration for parameter extraction
- Updated agent implementations to consume parameters
- Context-rich handoffs between agents

### ✅ Updated: Frontend Spec v3.3
- **Added Flow 0**: Parameter Gathering UI/UX
- Free-form text input (500 char limit) with extraction
- Parameter confirmation modal with extraction reasoning
- Read-only parameter banner after confirmation
- Agent reasoning preview section
- "Edit Parameters" functionality throughout dashboard
- Updated Information Architecture to 8 sections (was 7)

### ✅ Updated: PRD v3.3
- **Added Phase 0 user stories**: 4 new stories for parameter gathering
- Updated Solution Overview: All agents now "Parameter-Aware"
- Updated existing user stories to show parameter-driven behavior
- Story 0.1: Describe Season Strategy in Natural Language
- Story 0.2: Review and Confirm Extracted Parameters
- Story 0.3: Handle Incomplete Parameter Extraction
- Story 0.4: View Agent Reasoning Based on Parameters
- Updated acceptance criteria across all phases to reflect parameters
- Now 22 total user stories (was 18)

### ✅ Data Specification v3.2 (Unchanged)
- Complete data dictionary for 3 CSV types
- 6 realism strategies to achieve MAPE 12-18%
- 3 scenario definitions with black swan events
- Validation suite with 6 check types

---

---

## 📦 Agent Handoff Messages (Copy & Paste)

### ~~**Planning Phase: All Documents v3.3**~~ ✅ COMPLETE!

All v3.3 planning documents have been updated with parameter-driven architecture:
- Product Brief v3.3, Process Workflow v3.3, Technical Architecture v3.3
- Frontend Spec v3.3, PRD v3.3 (22 user stories, 4 new for Phase 0)
- Data Specification v3.2 (unchanged)
- 6,500+ lines total documentation

**Locations**: `docs/04_MVP_Development/planning/`

---

### **⭐ Phase 0: Parameter Extraction Service** → Use `*agent dev`

```
*agent dev

Task: Implement natural language parameter extraction API with Azure OpenAI gpt-4o-mini

Reference Documents:
- docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md (Parameter Extraction API section)
- docs/04_MVP_Development/planning/4_prd_v3.3.md (Section 4.0: Parameter Gathering user stories)
- docs/04_MVP_Development/planning/2_process_workflow_v3.3.md (Phase 0 workflow)

Key Requirements:
1. POST /api/parameters/extract endpoint
2. SeasonParameters Pydantic model with 5 key parameters:
   - forecast_horizon_weeks (int)
   - season_start_date, season_end_date (datetime)
   - replenishment_strategy (ReplenishmentStrategy enum: NONE, WEEKLY, BI_WEEKLY)
   - dc_holdback_percentage (float, 0-100)
   - markdown_checkpoint_week (int), markdown_threshold (float, 0-1)
3. ReplenishmentStrategy enum implementation
4. Azure OpenAI gpt-4o-mini integration for LLM extraction
5. Parameter validation and confidence scoring
6. Unit tests with example scenarios (Zara-style, traditional retail)

Tech Stack:
- Python 3.11+
- FastAPI
- Azure OpenAI Python SDK
- Pydantic 2.0+

Output:
- backend/models/season_parameters.py (SeasonParameters model + enum)
- backend/api/routes/parameters.py (POST /extract endpoint)
- backend/services/parameter_extractor.py (LLM integration logic)
- tests/test_parameter_extraction.py (unit tests)

Priority: HIGHEST - Required before any agent logic implementation
```

---

### **Phase 1: Mock Data Generation** → Use `*agent dev`

```
*agent dev

Task: Implement mock data generation script for Fashion Retail MVP

Reference Documents:
- docs/04_MVP_Development/planning/6_data_specification_v3.2.md (primary implementation guide)
- docs/04_MVP_Development/planning/4_prd_v3.3.md (acceptance criteria)
- docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md (Section 9: ML Approach, data models)

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

Task: Implement parameter-driven 3-agent system using OpenAI Agents SDK v0.3.3+

⭐ IMPORTANT: Phase 0 (Parameter Extraction Service) MUST be complete before starting this phase!

Reference Documents:
- docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md (primary implementation guide)
- docs/04_MVP_Development/planning/4_prd_v3.3.md (acceptance criteria, user stories)
- docs/04_MVP_Development/planning/6_data_specification_v3.2.md (data models, CSV formats)
- docs/04_MVP_Development/planning/2_process_workflow_v3.3.md (agent behavior examples with parameters)

Key Requirements:
1. ⭐ Demand Agent (Parameter-Aware):
   - Receives SeasonParameters from Orchestrator context
   - Autonomous reasoning: Adjusts safety stock based on replenishment_strategy
   - Example: "No replenishment → increase safety stock 20% → 25%"
   - Prophet+ARIMA ensemble, K-means clustering (7 features), hierarchical allocation
2. ⭐ Inventory Agent (Parameter-Aware):
   - Autonomous reasoning: DC holdback based on dc_holdback_percentage parameter
   - Example: "0% holdback → allocate 100% to stores at Week 0, skip replenishment phase"
   - Manufacturing calculation, parameter-driven allocation (100% or 55/45 split)
   - Conditional replenishment (only if strategy ≠ NONE)
3. ⭐ Pricing Agent (Parameter-Aware):
   - Autonomous reasoning: Uses markdown_checkpoint_week and markdown_threshold from parameters
   - Example: "Week 6 @ 60% threshold → apply Gap × Elasticity markdown"
   - Gap × Elasticity formula (elasticity=2.0, 5% rounding, 40% cap)
4. ⭐ Orchestrator (Parameter Context Manager):
   - Passes SeasonParameters to all agents via context
   - Workflow coordination with conditional phase execution
   - Variance monitoring (>20% trigger), re-forecast logic
5. REST API (FastAPI) + WebSocket for real-time progress
6. SQLite database for session persistence
7. Use training data from data/mock/training/

Tech Stack:
- Python 3.11+
- FastAPI
- OpenAI Agents SDK v0.3.3+ (Responses API)
- Azure OpenAI gpt-4o-mini (agent reasoning)
- Prophet + statsmodels (ARIMA)
- scikit-learn (K-means)
- SQLite

Output:
- backend/agents/ (demand_agent.py, inventory_agent.py, pricing_agent.py, orchestrator.py)
- backend/api/ (routes, WebSocket handlers)
- backend/ml/ (forecasting, clustering, allocation logic)
- backend/database/ (SQLite schema)

Priority: HIGH - Depends on Phase 0 completion
```

---

### **Phase 3: Frontend Implementation** → Use `*agent dev`

```
*agent dev

Task: Build parameter-driven single-page React dashboard with Linear Dark Theme

⭐ IMPORTANT: Phase 0 (Parameter Extraction Service) MUST be complete before starting this phase!

Reference Documents:
- docs/04_MVP_Development/planning/5_front-end-spec_v3.3.md (primary implementation guide)
- docs/04_MVP_Development/planning/3_technical_architecture_v3.3.md (Section 11: API contracts, WebSocket events)
- docs/04_MVP_Development/planning/4_prd_v3.3.md (user stories, acceptance criteria)

Key Requirements:
1. ⭐ 8-section single-page dashboard (NEW: Section 0 for parameter gathering):
   - ⭐ Section 0: Parameter Gathering (Phase 0 UI) - NEW!
     * Free-form text input (500 char limit) with placeholder example
     * "Extract Parameters" button → POST /api/parameters/extract
     * Parameter confirmation modal (5 parameters + extraction reasoning)
     * Read-only parameter banner after confirmation
     * Agent reasoning preview section
     * "Edit Parameters" button to return to this section
   - Section 1: Agent progress cards (3 cards, real-time WebSocket updates)
   - Section 2: Forecast results table with parameter context
   - Section 3: Store cluster analysis (3 clusters, allocation factors)
   - Section 4: Weekly forecast chart (forecast vs actuals, variance overlay)
   - Section 5: Replenishment schedule (conditional display based on replenishment_strategy)
   - Section 6: Markdown recommendations (parameter-driven checkpoint week/threshold)
   - Section 7: System metrics (MAPE, variance, sell-through)
2. Linear Dark Theme (Shadcn/ui + Tailwind CSS)
3. WebSocket integration for line-by-line agent progress
4. CSV upload workflows (historical data + weekly actuals)
5. Report page: /reports/spring-2025
6. ⭐ Parameter extraction integration with loading states and error handling

Tech Stack:
- React 18.3+
- TypeScript 5.6+
- Vite
- Shadcn/ui (Dialog, Textarea, Button, Badge components)
- Tailwind CSS
- Recharts (for charts)

Output:
- frontend/src/components/ (Dashboard, AgentCard, ForecastTable, ParameterGathering, etc.)
- frontend/src/pages/ (Dashboard.tsx, Report.tsx)
- frontend/src/hooks/ (useWebSocket, useForecast, useParameterExtraction)
- frontend/src/styles/ (Linear Dark Theme)
- frontend/src/types/ (SeasonParameters interface matching backend model)

Priority: HIGH - Depends on Phase 0 completion
```

---

### **Phase 4: Testing & Validation** → Use `*agent qa`

```
*agent qa

Task: Test parameter-driven system with 3 scenarios and validate accuracy

Reference Documents:
- docs/04_MVP_Development/planning/6_data_specification_v3.2.md (Section 7: Testing Workflow, expected MAPE ranges)
- docs/04_MVP_Development/planning/4_prd_v3.3.md (acceptance criteria, parameter-driven user stories)
- docs/04_MVP_Development/planning/2_process_workflow_v3.3.md (expected system behavior with parameters)

⭐ Parameter-Driven Test Scenarios:
1. ⭐ Zara-Style Fast Fashion (NEW primary test scenario):
   - Parameters: 12 weeks, 0% holdback, no replenishment, Week 6 @ 60% markdown
   - Expected: 100% allocation at Week 0, replenishment phase skipped
   - Agent reasoning: Demand +5% safety stock, Inventory skips Phase 3
   - MAPE 12-15%, Week 5 variance ~25%
2. Traditional Retail (Normal Season):
   - Parameters: 12 weeks, 45% holdback, weekly replenishment, Week 6 @ 60%
   - Expected: 55/45 split, weekly replenishment, standard safety stock
   - MAPE 12-15%, Week 5 variance ~25%
3. High Demand Scenario:
   - MAPE 15-18%, Week 5 variance ~32% (competitor bankruptcy)
4. Low Demand Scenario:
   - MAPE 15-18%, Week 5 variance ~28% (supply chain disruption)

Key Test Cases:
1. ⭐ E2E Workflow with Parameter Extraction:
   - Phase 0: Natural language input → parameter extraction → confirmation
   - Phase 1-5: CSV upload → forecast → allocation → markdown → report
2. ⭐ Agent Reasoning Validation:
   - Verify Demand Agent adjusts safety stock based on replenishment_strategy
   - Verify Inventory Agent skips replenishment when strategy = NONE
   - Verify Pricing Agent uses parameter-specified checkpoint week/threshold
3. ⭐ Conditional Phase Execution:
   - Test replenishment phase skip when strategy = NONE
   - Test full workflow when strategy = WEEKLY
4. Variance-triggered re-forecast (>20% threshold in Week 5)
5. WebSocket real-time updates
6. Store cluster allocation accuracy
7. Data validation (6 types from data spec)

Validation Criteria:
- MAPE between 12-18% (not <10% = too perfect, not >20% = unusable)
- Week 5 variance >20% in all scenarios (black swan detection)
- Re-forecast improves accuracy in Weeks 6-12
- All CSV formats match data specification
- ⭐ Agent reasoning appears in UI and matches parameter context
- ⭐ Parameter extraction accuracy >95% for structured scenarios

Output:
- Test reports (pass/fail for each scenario)
- Bug tracking (if any issues found)
- Performance metrics (API response times, forecast accuracy)
- ⭐ Parameter extraction accuracy report
```

---

**Ready to start implementation?** Copy the Phase 0 message above and run:
```
*agent dev
```
