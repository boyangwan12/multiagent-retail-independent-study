# Documentation Directory Guide
## Multi-Agent Retail Demand Forecasting System

**Project:** Independent Study - Multi-Agent System for Retail Demand Forecasting
**Timeline:** September 1 - December 10, 2025
**Status:** Planning Complete ✅ (v3.3 Parameter-Driven) | Implementation Starting 🚧

---

## 📁 Directory Structure

### 📘 01_Project_Foundation/
Core project definition and setup documents

- **`project_brief.md`** - Project overview with objectives, scope, timeline, and deliverables

---

### 🎤 02_Interviews/
User research: 5 interviews across 4 retail segments

#### Preparation Materials (`Prep/`)
- **`Interview_Guide_Retail_Operations.md`** - 45-minute semi-structured interview script
- **`Interview_Strategy.md`** - Strategy for mapping retail workflows to solution requirements

#### Interview Notes (`Notes/`)
- **`INT-001_Notes.md`** - Furniture Retail (Business Analyst, ~1000 employees, US/Canada operations)
- **`INT-002_Notes.md`** - Walmart (Planning Manager, 10,000 stores, millions of SKUs)
- **`INT-003_Notes.md`** - La Vie En Rose (Market Analyst, 400+ stores, fashion retail)
- **`INT-004_Notes.md`** - Canadian Tire (Data Scientist, 1,700 stores, multi-banner)
- **`INT-005_Notes.md`** - Groupe Dynamite/Walmart (BI Developer, CPG + fashion experience)

#### Interview Transcripts (`Transcripts/`)
- **`INT-004_Transcript.md`** - Full transcript from Canadian Tire interview
- **`INT-005_Transcript.md`** - Full transcript from Vaibhav Vishal interview

---

### 📊 03_Evidence_Pack/
**✅ COMPLETE** - Comprehensive validation of problem, user needs, and solution direction

#### Core Evidence Pack Components
1. **`01_Problem_Validation.md`** - Validates problem exists, is significant, and warrants solution
   - 33 pain points documented and categorized
   - Root cause analysis (cascading impacts)
   - Quantified time/cost impact (50% time waste, $500K losses)
   - Cross-industry validation (furniture, mass retail, fashion, multi-banner)

2. **`02_User_Research_Synthesis.md`** - User personas, workflows, and insights
   - 5 detailed user personas with goals, pain points, workflows
   - Current workflow documentation across 4 retail segments
   - 36 key quotes organized by theme
   - Collaboration opportunities (planning team access, expert review)

3. **`03_Requirements_Constraints.md`** - Requirements traceable to user needs
   - 12 Functional Requirements
   - 10 Data Requirements
   - 7 Technical Constraints
   - 4 Scope Boundaries
   - 7 User Success Criteria
   - Traceability matrix linking requirements to pain points

4. **`04_Approach_Validation.md`** - Validates solution direction (NOT technical architecture)
   - AI-based approach validated (vs. traditional ML)
   - Multi-source data integration confirmed as need
   - Continuous learning validated as requirement
   - Explainability critical for adoption

5. **`05_Success_Metrics.md`** - User-defined success criteria and measurement methodology
   - 7 measurable success criteria with baselines and targets
   - Business impact expectations
   - Validation checkpoints (INT-001 planning team, INT-005 expert review)
   - 3-tier success framework (critical/high-value/aspirational)

6. **`06_Research_Methodology.md`** - Research process documentation
   - Interview design and participant selection
   - Data collection methods
   - Analysis approach (thematic analysis, pain point categorization)
   - Limitations and ethical considerations
   - Validity and reliability assessment

#### Supporting Materials
- **`Evidence_Pack_Preparation_Plan.md`** - 3-phase plan for creating evidence pack (complete)
- **`_extraction/`** - Phase 1 raw extraction files:
  - **`Pain_Point_Inventory.md`** - 33 pain points with severity, impact, frequency
  - **`Quote_Library.md`** - 36 key quotes organized by 10 themes
  - **`Requirements_Extract.md`** - 41 requirements extracted from interviews

**Evidence Pack Statistics:**
- **Total Pages:** ~150 pages of comprehensive documentation
- **Pain Points:** 33 identified and analyzed
- **Interviews:** 5 conducted across 4 retail segments
- **Quotes:** 36 key quotes extracted and organized
- **Requirements:** 41 total (12 functional, 10 data, 7 technical, 4 scope, 7 success criteria)
- **Personas:** 5 detailed user personas created

---

### 💻 04_MVP_Development/
**✅ COMPLETE** - v3.3 parameter-driven planning documents finalized

#### Planning Documents (`planning/`)
- **`0_PLANNING_GUIDE.md`** - Documentation navigation, standards, and workflow
  - Document status table with all v3.3 planning docs
  - Documentation standards and versioning guidelines
  - Planning workflow with backward consistency checks

- **`1_product_brief_v3.3.md`** - Parameter-driven product specification
  - LLM-based parameter gathering (allocation %, season length, markdown timing)
  - Generic retail planning solution emphasizing agentic coordination
  - Adapts to diverse workflows (fast fashion, premium retail, etc.)
  - Category-level forecasting with hierarchical allocation

- **`2_process_workflow_v3.3.md`** - 5-phase operational workflow with examples
  - Pre-season → Season Start → In-Season → Mid-Season → Post-Season
  - Ensemble Prophet+ARIMA forecasting
  - K-means clustering (7 features)
  - Variance-triggered re-forecast (>20% threshold)

- **`3_technical_architecture_v3.3.md`** - Complete backend architecture
  - Tech stack: Python + FastAPI + OpenAI Agents SDK + React + TypeScript
  - Parameter-driven design with LLM configuration
  - Context-rich handoffs + dynamic enabling
  - REST + WebSocket for real-time updates

- **`4_prd_v3.3.md`** - Product requirements document
  - Functional requirements with parameter flexibility
  - User stories and acceptance criteria
  - System constraints and boundaries

- **`5_front-end-spec_v3.3.md`** - Complete frontend UI/UX specification
  - Single-page dashboard (7 sections)
  - Linear Dark Theme (Shadcn/ui + Tailwind CSS)
  - WebSocket line-by-line agent progress updates
  - Wireframes and component specifications

- **`6_data_specification_v3.2.md`** - Data structures and validation
  - CSV formats for historical sales and store attributes
  - Validation rules and constraints
  - Mock data generation specifications

#### Archive (`archive/`)
- **`v1.1/`** - Architecture v1.1, PRD v1.1, Product Brief v1.1
- **`v2.1/`** - Product Brief v2.1, Key Parameters, Operational Workflow
- **`v3.1/`** - Operational Workflow v3.1, Product Brief v3.1
- **`v3.2/`** - Original v3.2 documents (hardcoded parameters)

---

### 📈 05_Progress_Reports/
Project status tracking and supervisor updates

#### Weekly Supervisor Meetings (`Weekly_Supervisor_Meetings/`)
- **`Week_01_Updates.md`** - Initial project setup and planning
- **`Week_02_Updates.md`** - Interview completions (INT-001, INT-002, INT-003) and key findings
- **`Week_03_Updates.md`** - Evidence pack progress and remaining interviews
- **`Week_04_Updates.md`** - Product specs completion (v3.2 hardcoded approach)
- **`Week_05_Updates.md`** - Architecture evolution: v3.1 → v3.3
  - Granularity adjustment (category-level forecasting)
  - Strategic pivot to parameter-driven architecture
  - LLM-gathered configuration for diverse retail workflows
- **`Week_05_Updates.html`** - Visual presentation (black & white design)

---

## 📋 Quick Reference Guide

### What You Need → Where to Find It

| What You Need | File Path | Description |
|---------------|-----------|-------------|
| **Project Overview** | `01_Project_Foundation/project_brief.md` | Objectives, scope, timeline |
| **Interview Questions** | `02_Interviews/Prep/Interview_Guide_Retail_Operations.md` | Complete interview script |
| **All Interview Data** | `02_Interviews/Notes/` | 5 interview notes + 2 transcripts |
| **Problem Validation** | `03_Evidence_Pack/01_Problem_Validation.md` | 33 pain points, severity analysis |
| **User Personas** | `03_Evidence_Pack/02_User_Research_Synthesis.md` | 5 detailed personas + workflows |
| **Requirements** | `03_Evidence_Pack/03_Requirements_Constraints.md` | 41 requirements with traceability |
| **Success Metrics** | `03_Evidence_Pack/05_Success_Metrics.md` | Measurable criteria + baselines |
| **Pain Points List** | `03_Evidence_Pack/_extraction/Pain_Point_Inventory.md` | 33 pain points with details |
| **Planning Guide** | `04_MVP_Development/planning/0_PLANNING_GUIDE.md` | Documentation navigation & standards |
| **Product Brief v3.3** | `04_MVP_Development/planning/1_product_brief_v3.3.md` | Parameter-driven product spec |
| **Process Workflow v3.3** | `04_MVP_Development/planning/2_process_workflow_v3.3.md` | 5-phase workflow with examples |
| **Technical Architecture v3.3** | `04_MVP_Development/planning/3_technical_architecture_v3.3.md` | Complete backend architecture |
| **PRD v3.3** | `04_MVP_Development/planning/4_prd_v3.3.md` | Product requirements |
| **Frontend Spec v3.3** | `04_MVP_Development/planning/5_front-end-spec_v3.3.md` | Complete UI/UX specification |
| **Data Specification v3.2** | `04_MVP_Development/planning/6_data_specification_v3.2.md` | Data structures & validation |

---

## 🎯 Project Workflow

### ✅ Phase 1: Discovery (COMPLETE)
**Duration:** Weeks 1-2
**Deliverables:**
- Project brief and interview guides created
- Interview strategy defined

### ✅ Phase 2: User Research (COMPLETE)
**Duration:** Weeks 2-4
**Deliverables:**
- 5 interviews conducted across 4 retail segments
- Interview notes and 2 full transcripts documented
- Key findings: 33 pain points, 50% time waste on data prep, $500K losses

### ✅ Phase 3: Evidence Pack Creation (COMPLETE)
**Duration:** Weeks 4-6
**Deliverables:**
- 6 core Evidence Pack components created
- 3 extraction files (pain points, quotes, requirements)
- Problem validated, requirements defined, direction confirmed

### ✅ Phase 4: Product Specifications (COMPLETE - Week 8)
**Duration:** Weeks 6-8
**Deliverables:**
- v3.3 parameter-driven planning documents (7 documents)
- Strategic pivot from hardcoded to flexible architecture
- LLM-based parameter gathering system
- Flattened documentation structure with numeric prefixes
- Complete frontend UI/UX specification
- Data structures and validation rules

### 🚧 Phase 5: MVP Development (STARTING - Week 9)
**Duration:** Weeks 9-16 (October 17 - December 10, 2025)
**Current Status:** Planning complete, starting implementation
**Next Steps:**
- Mock data generation (data spec ready)
- Frontend mockup development
- Backend architecture implementation (3 agents + orchestrator)
- Integration & validation (MAPE <20%, cost <$5)

### ⏳ Phase 6: Validation & Delivery (UPCOMING)
**Duration:** Weeks 16-17
**Planned:**
- Test with synthetic retail data
- Measure accuracy (MAPE <20% target)
- Demo to supervisor
- Final technical report

---

## 📊 System Architecture Overview

### 3 Agents + Orchestrator

```
┌─────────────────────────────────────────┐
│           ORCHESTRATOR                  │
│  • 5-phase workflow coordination        │
│  • Variance detection (>15%)            │
│  • Performance monitoring               │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┬───────────────┐
    │                   │               │
    ▼                   ▼               ▼
┌─────────┐      ┌──────────┐   ┌──────────┐
│ DEMAND  │─────▶│INVENTORY │   │  PRICING │
│  AGENT  │      │  AGENT   │   │  AGENT   │
└─────────┘      └──────────┘   └────┬─────┘
                                      │
                                      │ triggers
                                      ▼
                                 ┌─────────┐
                                 │ DEMAND  │
                                 │(rerun)  │
                                 └─────────┘
```

### Agent Responsibilities

| Agent | Primary Responsibility | Key Output |
|-------|----------------------|-----------|
| **Demand Agent** | Predict store-week demand using similar-item matching + time-series | `demand_by_store_by_week` matrix |
| **Inventory Agent** | Calculate manufacturing orders, allocate inventory, plan replenishment | Manufacturing order, allocation plans |
| **Pricing Agent** | Monitor sell-through, recommend markdowns | Markdown triggers, depth recommendations |
| **Orchestrator** | Coordinate agents through 5-phase seasonal workflow | Agent execution sequence, performance metrics |

### Agentic Features
- **Autonomous decision-making**: LLM chooses forecasting methods (Prophet, ARIMA, hybrid)
- **Reasoning & explanation**: Natural language explanations for all decisions
- **Semantic understanding**: OpenAI embeddings for similar-item matching (charcoal sofa ≈ grey sectional)
- **Adaptive behavior**: Method selection based on data availability and confidence
- **Multi-agent collaboration**: Cascading decisions (Pricing → Demand → Inventory)
- **Memory & state**: Orchestrator maintains full season history
- **Human-in-the-loop**: Escalates when confidence <70%

### Technology Stack
- **LLM API**: OpenAI SDK (gpt-4o-mini, text-embedding-3-small)
- **Agent Framework**: LangChain
- **Forecasting**: Prophet, statsmodels (ARIMA/SARIMA)
- **Data Processing**: pandas, NumPy
- **Storage**: SQLite, CSV/Parquet (local)
- **Budget**: <$5 LLM costs (~$0.05 per season)

---

## 🔑 Key Project Insights

### Problem Severity
- **5 severity-5 pain points** (critical impact)
- **11 severity-4 pain points** (high impact)
- **82% of pain points** occur daily/weekly/seasonally

### Quantified Impact
- **50%+ of analyst time** on data preparation (INT-004, INT-005)
- **$500K annual margin loss** from late markdowns (INT-003)
- **60-70% forecast accuracy** across companies (needs improvement)
- **6-18 hrs/week firefighting** reactive issues (INT-002)

### Cross-Industry Validation
- **Furniture:** 1-year planning cycles, cross-border complexity
- **Mass Retail:** Massive scale (10,000 stores, millions SKUs)
- **Fashion:** Trend volatility, seasonal dependency
- **Multi-Banner:** Weather sensitivity, dealer complexity

### MVP Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE (Store-Week)** | <20% | Hindcast on synthetic data |
| **Bias** | ±5% | Over/under-forecasting check |
| **Confidence Calibration** | 80%+ | Predicted confidence vs actual error |
| **Runtime (Initial Forecast)** | <4 hours | 50 SKUs, local machine |
| **Runtime (Bi-weekly Update)** | <30 min | Single update cycle |
| **LLM Cost** | <$5 | Total for full season (26 weeks) |

---

## 📌 Current Status

**October 29, 2025 - Phase 4 PO Validation Complete:**

### Implementation Progress
| Phase | Status | Completion |
|-------|--------|------------|
| Phase 1: Data Generation | ✅ Complete | 100% |
| Phase 2: Frontend Foundation | ✅ Complete | 100% |
| Phase 3: Backend Architecture | ✅ Complete | 100% |
| Phase 3.5: Testing & Cleanup | ✅ Complete | 100% |
| **Phase 4: Integration** | **🚀 Ready for Dev** | **PO Validated** |
| Phase 5: Demand Agent | ⏳ Pending | 0% |
| Phase 6: Inventory Agent | ⏳ Pending | 0% |
| Phase 7: Orchestrator | ⏳ Pending | 0% |
| Phase 8: Pricing Agent | ⏳ Pending | 0% |

### Recent Achievements (Oct 29, 2025)
- ✅ Evidence Pack completed (6 components, 150+ pages)
- ✅ v3.3 Planning documents completed (7 documents, parameter-driven)
- ✅ Phases 1-3.5 implementation complete
- ✅ **Phase 4 PO Validation Complete**:
  - All 9 stories validated against v3.3 planning docs
  - Upgraded to React Context API (eliminates prop drilling)
  - WCAG 2.1 Level AA accessibility compliance
  - Comprehensive error handling (401, 404, 422, 429, 500)
  - Updated time estimate: 55 hours
  - Branch: `phase4-integration` ready for developer

**Next Milestone:**
- Phase 4 Implementation (55 hours, 9 stories)
- See: `04_MVP_Development/implementation/phase_4_integration/PHASE4_HANDOFF.md`

---

**Project Status:** Planning Complete ✅ (v3.3) | Phases 1-3.5 Complete ✅ | Phase 4 Ready 🚀
**Last Updated:** October 29, 2025
**Document Version:** 5.0
