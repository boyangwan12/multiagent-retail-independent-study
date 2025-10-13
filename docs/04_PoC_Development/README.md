# PoC Development Documentation

**Status**: Document Preparation Phase
**Last Updated**: 2025-10-12

---

## Current Documentation Structure

### 📁 Active Documents (Current Versions)

#### Product Brief & Operational Workflow
- **`product_brief/product_brief_v3.2.md`** ✅ - Current product brief (Archetype 1: Fashion Retail, 12 weeks, aligned with architecture)
  - Ensemble Prophet+ARIMA (parallel, averaged), K-means (7 features), Gap × Elasticity markdown
  - No confidence scoring (simplified MVP)
- **`product_brief/operational_workflow_v3.2.md`** ✅ - Streamlined operational guide with concrete examples (aligned with architecture)
  - 5-phase workflow with ensemble forecasting, K-means (7 features), simple replenishment, Gap × Elasticity
- **Key Features**: Category-level forecasting (NOT store-by-week), hierarchical allocation, 3-agent system

#### Planning & Next Steps
- **`next_steps_plan.md`** - Roadmap for moving from product brief to implementation
  - Lists 5 required documents
  - Recommended sequence: architect → designer → pm
  - Phase breakdown (Architecture & Design, Requirements & Planning, Implementation, Testing)

---

### 📁 Work-in-Progress Folders

#### `architecture/` 🏗️
- **`technical_architecture.md`** ✅ - Complete backend architecture (20 sections, ready for implementation)
  - Tech stack: Python + FastAPI + OpenAI Agents SDK + React + TypeScript
  - ML approach: Prophet+ARIMA ensemble, K-means clustering, markdown formula
  - Agent handoffs: Context-rich + dynamic enabling
  - Database: SQLite hybrid schema (normalized + JSON)
  - API: REST + WebSocket for real-time updates
  - Includes: Agent coordination workflow, handoff patterns, ML details
- **TODO**: Create `agent_specs.md` (talk to `*agent architect` + `*agent dev`)

#### `Design/` 🎨
- **EMPTY** - Ready for UI/UX documents
- **TODO**: Create `ux_design.md` (talk to `*agent designer`)
- Planned content: Merchandiser dashboard, forecast views, allocation tables, markdown manager

#### `Data/` 📊
- **EMPTY** - Ready for data requirements
- **TODO**: Create `data_requirements.md` (talk to `*agent data` or `*agent architect`)
- Planned content: Historical sales schemas, store attributes, sample datasets

#### `Research/` 🔍
- **`OpenAI_Agents_SDK_Retail_PoC_Research.md`** - OpenAI Agents SDK implementation research
- Contains: Core components, agent patterns, retail PoC recommendations

---

### 📁 Archive

**Old versions moved to `archive/`** (for reference only):
- `architecture_v1.1.md` - OLD (Archetype 2: Furniture, 26 weeks)
- `prd_v1.1.md` - OLD (Archetype 2: Furniture, 26 weeks)
- `product_brief_v1.1.md`, `product_brief_v2.1.md`, `product_brief_v3.1.md` - Superseded by v3.2
- `operational_workflow_v3.1.md` - Superseded by v3.2
- `2_key_parameter.md`, `2_operational_workflow.md` - Superseded by v3.x documents

**Important Note**: Archive documents focus on Archetype 2 (Stable Catalog Retail, Furniture, 26 weeks) which is NOT the current MVP focus. Current focus is Archetype 1 (Fashion Retail, Women's Dresses, 12 weeks).

---

## Key Concepts (Current Approach)

### Forecast Once, Allocate with Math
- **Category-level forecast**: "Women's Dresses will sell 8,000 units over 12 weeks" (1 forecast)
- **NOT store-by-week**: Avoids 600+ granular forecasts (50 stores × 12 weeks)
- **Hierarchical allocation**: Category → Cluster → Store using historical patterns + store attributes

### 3-Agent System
1. **Demand Agent**: Category forecasting, store clustering (K-means), allocation factors
2. **Inventory Agent**: Manufacturing orders, hierarchical allocation, weekly replenishment
3. **Pricing Agent**: Sell-through tracking, markdown decisions (Week 6 checkpoint), re-forecast triggers

### Archetype 1 Parameters (Fashion Retail - MVP)
- **Season**: 12 weeks
- **Category**: Women's Dresses
- **Stores**: 50 stores, 3 clusters (Fashion_Forward, Mainstream, Value_Conscious)
- **Allocation**: 55% initial, 45% holdback at DC
- **Markdown checkpoint**: Week 6 (target: 60% sell-through)
- **Re-forecast trigger**: >20% variance

---

## Next Steps (Document Prep Phase)

Follow the plan in **`next_steps_plan.md`**:

### Phase 1: Architecture & Design (Week 1-2)
1. ✅ **~~Talk to `*agent architect`~~** - COMPLETE! Technical architecture ready
2. **Talk to `*agent designer`** - Design merchandiser UI, wireframes, interaction patterns

### Phase 2: Requirements & Planning (Week 2-3)
3. **Talk to `*agent pm`** - Write PRD with user stories, MVP scope, acceptance criteria
4. **Talk to `*agent data`** - Define data schemas, create sample dataset

### Phase 3: Implementation (Week 4-8)
5. **Talk to `*agent dev`** - Implement agents using OpenAI Agents SDK
6. **Build Frontend** - React dashboard for merchandiser

### Phase 4: Testing & Validation (Week 9-10)
7. **Talk to `*agent qa`** - Test with sample data, validate MAPE <20%, hindcast validation

---

## Quick Reference

| What You Need | Who to Talk To | Output Path |
|---------------|----------------|-------------|
| Technical Architecture | `*agent architect` | `Architecture/technical_architecture.md` |
| UI/UX Design | `*agent designer` | `Design/ux_design.md` |
| PRD | `*agent pm` | Create new PRD (current prd_v1.1 is Archetype 2) |
| Data Requirements | `*agent data` or `*agent architect` | `Data/data_requirements.md` |
| Agent Implementation Specs | `*agent architect` + `*agent dev` | `Architecture/agent_specs.md` |

---

## Progress Status

**Completed:**
- ✅ Product Brief v3.2 (Archetype 1: Fashion Retail, aligned with architecture)
- ✅ Operational Workflow v3.2 (5-phase workflow, aligned with architecture)
- ✅ Technical Architecture v1.0 (20 sections, implementation-ready)

**Next Steps:**
- 🎨 **UI/UX Design** - Talk to `*agent designer` for wireframes and dashboard layouts
- 📋 **PRD** - Talk to `*agent pm` for user stories and acceptance criteria
- 📊 **Data Requirements** - Talk to `*agent data` for schemas and sample datasets
- 🤖 **Agent Specs** - Talk to `*agent dev` for detailed implementation specs

**Progress:** 3/7 documents complete (43%)

---

**Document Owner**: Independent Study Project
**Related Git Status**: `development_plan.md` deleted (replaced by `next_steps_plan.md`)
