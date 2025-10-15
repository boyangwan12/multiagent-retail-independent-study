# PoC Development Documentation

**Status**: Planning Complete ✅ → Ready for Implementation
**Last Updated**: 2025-10-13

---

## Current Documentation Structure

### ✅ Completed Documents (All v3.2)

#### Product Brief & Process Workflow
- **`product_brief/product_brief_v3.2.md`** ✅ - Complete product specification (Archetype 1: Fashion Retail, 12 weeks)
  - Ensemble Prophet+ARIMA forecasting, K-means clustering (7 features), Gap × Elasticity markdown
  - Category auto-detection from CSV upload
  - Hierarchical allocation: Category → Cluster → Store
  - No confidence scoring (simplified MVP)

- **`process_workflow/process_workflow_v3.2.md`** ✅ - 5-phase operational guide with concrete examples
  - Pre-season → Season Start → In-Season → Mid-Season → Post-Season
  - Ensemble forecasting, K-means (7 features), simple replenishment, Gap × Elasticity
  - Variance-triggered re-forecast (>20% threshold)

#### Architecture & Design
- **`architecture/technical_architecture_v3.2.md`** ✅ - Complete backend architecture (ready for implementation)
  - Tech stack: Python + FastAPI + OpenAI Agents SDK + React + TypeScript + SQLite
  - ML: Prophet+ARIMA ensemble, K-means clustering, Gap × Elasticity markdown
  - API: REST + WebSocket for real-time agent progress
  - Context-rich handoffs + dynamic enabling

- **`design/front-end-spec_v3.2.md`** ✅ - Complete frontend UI/UX specification
  - Single-page dashboard (7 sections)
  - Linear Dark Theme (Shadcn/ui + Tailwind CSS)
  - WebSocket line-by-line agent progress updates
  - All wireframes, user flows, and component specs

#### Planning
- **`next_steps_plan.md`** ✅ - Implementation roadmap
  - Lists 4 remaining tasks (mock data, backend, frontend, testing)
  - "Who to talk to" for each phase
  - Recommended sequence: data → dev → frontend → qa

---

## Key Features (v3.2 System)

### Forecast Once, Allocate with Math
- **Category-level forecast**: "Women's Dresses will sell 8,000 units over 12 weeks" (1 forecast, not 600!)
- **Hierarchical allocation**: Category → Cluster → Store using K-means + historical patterns
- **Category auto-detection**: System detects "Women's Dresses", "Men's Shirts", "Accessories" from CSV

### 3-Agent System + Orchestrator
1. **Demand Agent**: Ensemble forecasting (Prophet+ARIMA), K-means clustering (7 features), allocation factors
2. **Inventory Agent**: Manufacturing orders, hierarchical allocation (55%/45%), weekly replenishment
3. **Pricing Agent**: Sell-through tracking, Gap × Elasticity markdown (Week 6 checkpoint)
4. **Orchestrator**: Variance monitoring (>20% trigger), re-forecast coordination

### Archetype 1 Parameters (Fashion Retail - MVP)
- **Season**: 12 weeks (Spring 2025)
- **Categories**: Auto-detected from CSV (e.g., Women's Dresses, Men's Shirts, Accessories)
- **Stores**: 50 stores, 3 clusters (Fashion_Forward, Mainstream, Value_Conscious)
- **Allocation**: 55% initial, 45% holdback at DC
- **Markdown**: Week 6 checkpoint, Gap × Elasticity formula (elasticity=2.0), uniform across stores
- **Re-forecast trigger**: Variance >20%

---

## What's Left to Build

| Task | Owner | Priority | Status | Output |
|------|-------|----------|--------|--------|
| **Mock Data Script** | `*agent data` | **HIGH** | ⏳ Not Started | `data/mock/generate_mock_data.py` + CSV files |
| **Backend (3 Agents + API)** | `*agent dev` | **HIGH** | ⏳ Not Started | `backend/` folder |
| **Frontend (Dashboard)** | `*agent frontend` | **HIGH** | ⏳ Not Started | `frontend/` folder |
| **Testing & Validation** | `*agent qa` | MEDIUM | ⏳ Not Started | Test results + bug reports |

---

## Next Steps

Follow the plan in **`next_steps_plan.md`**:

### Phase 1: Data Preparation (First!)
1. **Talk to `*agent data`** - Generate mock CSV files
   - `historical_sales_2022_2024.csv` (~54,750 rows, 3 categories mixed)
   - `store_attributes.csv` (50 stores, 7 features)

### Phase 2: Backend Foundation
2. **Talk to `*agent dev`** - Implement 3-agent system
   - Demand Agent (Prophet+ARIMA+K-means)
   - Inventory Agent (manufacturing+allocation+replenishment)
   - Pricing Agent (markdown+sell-through)
   - Orchestrator + REST API + WebSocket

### Phase 3: Frontend Development
3. **Talk to `*agent frontend`** - Build single-page dashboard
   - 7-section layout (agent cards, forecast, clusters, weekly chart, replenishment, markdown, metrics)
   - Linear Dark Theme (Shadcn/ui)
   - WebSocket integration

### Phase 4: Testing & Validation
4. **Talk to `*agent qa`** - Test accuracy and functionality
   - Test 3 scenarios (normal, high demand, low demand)
   - Validate MAPE <20%
   - Test variance triggers and re-forecasts

---

## Archive

**Old versions moved to `archive/`** (for reference only):
- `product_brief_v3.1.md`, `process_workflow_v3.1.md` - Superseded by v3.2
- `architecture_v1.1.md`, `prd_v1.1.md` - OLD (Archetype 2: Furniture, 26 weeks)
- `2_key_parameter.md`, `2_process_workflow.md` - Superseded

**Important**: Archive documents focus on Archetype 2 (Furniture, 26 weeks). Current MVP is Archetype 1 (Fashion, 12 weeks).

---

## Progress Status

**Completed (4/4 Planning Documents):**
- ✅ Product Brief v3.2
- ✅ Process Workflow v3.2
- ✅ Technical Architecture v3.2
- ✅ Frontend UI/UX Spec v3.2

**Key Achievements:**
- ✅ All v3.2 documents aligned (no contradictions)
- ✅ Category auto-detection implemented
- ✅ Linear Dark Theme design system defined
- ✅ Complete API contracts + data models

**Next: Implementation Phase (4 tasks remaining)**
- 📊 Mock Data Generation
- 🔧 Backend Implementation
- 🎨 Frontend Implementation
- 🧪 Testing & Validation

**Progress:** 100% planning complete, ready to start building!

---

## Quick Reference

**Talk to these agents:**
- `*agent data` - Generate mock CSV files (recommended first step)
- `*agent dev` - Build backend (3 agents + API)
- `*agent frontend` - Build React dashboard
- `*agent qa` - Test and validate

**Key Documents:**
- Product Brief v3.2 - System overview
- Technical Architecture v3.2 - Implementation details
- Frontend Spec v3.2 - Complete UI/UX design
- Process Workflow v3.2 - Agent behavior examples

---

**Document Owner**: Independent Study Project
**Ready to implement!** 🚀
