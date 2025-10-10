# Documentation Directory Guide
## Multi-Agent Retail Demand Forecasting System

**Project:** Independent Study - Multi-Agent System for Retail Demand Forecasting
**Timeline:** September 1 - December 10, 2025
**Status:** Evidence Pack Complete ✅ | Product Specs Complete ✅ | Development Starting 🚧

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

### 💻 04_PoC_Development/
**✅ COMPLETE** - Product specifications, PRD, and development plan finalized

#### Product Brief (`product_brief/`)
- **`product_brief_v2.1.md`** - Main product specification (Archetype 2: Stable Catalog Retail)
  - 3-agent system (Demand, Inventory, Pricing + Orchestrator)
  - Core prediction: `demand_by_store_by_week` matrix (50 stores × 26 weeks)
  - Evidence-based problem validation (PP-001, PP-002, PP-015, PP-016, PP-028)
  - MVP scope: 50 SKUs, 50 stores, 26-week furniture retail season

- **`2_key_parameter.md`** - Parameter-driven system design
  - 3 retail archetypes (Fashion, Stable Catalog, Continuous Replenishment)
  - MVP validates on Archetype 2
  - Configurable parameters: season length, replenishment cadence, markdown timing, DC holdback

- **`2_operational_workflow.md`** - 5-phase seasonal workflow
  - Phase 1: Pre-season planning (Week -12)
  - Phase 2: Initial allocation (Week 0)
  - Phase 3: In-season operations (bi-weekly, Weeks 2-10)
  - Phase 4: Mid-season pricing (Week 12 markdown checkpoint)
  - Phase 5: Season end analytics (Week 26)

- **`2_simplified_three_agent_mvp.md`** - Streamlined MVP specification
  - Adaptive forecasting methods (similar-item matching, time-series)
  - Inventory optimization approach
  - Pricing logic and markdown triggers

#### PRD (`prd/`)
- **`prd_demand_forecasting_system.md`** - Comprehensive Product Requirements Document (600+ lines)
  - Functional requirements for all 4 agents with plain language explanations
  - ML/forecasting methods (OpenAI embeddings, Prophet, ARIMA, rule-based pricing)
  - Agentic features (autonomous decision-making, LLM reasoning, semantic understanding, multi-agent collaboration)
  - Non-functional requirements (zero-cost MVP, <$5 LLM budget)
  - User stories, data requirements, 12-week timeline
  - Technology stack (LangChain, OpenAI SDK, Prophet, statsmodels)

- **`agent_coordination_workflow.md`** - Multi-agent orchestration specification
  - 7 Mermaid flowcharts (season workflow, phase coordination, decision trees, sequence diagrams)
  - Phase-by-phase coordination (5 phases)
  - Event-based triggers (variance >15%, confidence <70%)
  - Message passing protocol and state management
  - Performance metrics (~$0.05 LLM cost per season)

- **`development_plan.md`** - 9-week implementation plan (Oct 10 - Dec 10, 2025)
  - Phase 1-2: Environment setup & data generation (Weeks 1-2)
  - Phase 3-4: Similar-item matching with embeddings (Weeks 3-4)
  - Phase 4-5: Forecasting methods (Prophet, ARIMA, hybrid) (Weeks 4-5)
  - Phase 5-6: Inventory agent (Weeks 5-6)
  - Phase 6-7: Pricing agent & orchestrator (Weeks 6-7)
  - Phase 8: Integration & validation (Week 8, MAPE <20%)
  - Phase 9: Documentation & final report (Week 9)

#### Architecture (`Architecture/`)
- **`architecture_v1.1.md`** - System architecture design

#### Research (`Research/`)
- **`OpenAI_Agents_SDK_Retail_PoC_Research.md`** - OpenAI SDK evaluation for retail demand forecasting

---

### 📈 05_Progress_Reports/
Project status tracking and supervisor updates

#### Weekly Supervisor Meetings (`Weekly_Supervisor_Meetings/`)
- **`Week_01_Updates.md`** - Initial project setup and planning
- **`Week_02_Updates.md`** - Interview completions (INT-001, INT-002, INT-003) and key findings
- **`Week_03_Updates.md`** - Evidence pack progress and remaining interviews
- **`Week_04_Updates.md`** - Product specs completion (7 major deliverables)
  - Product Brief v2.1
  - Operational Workflow Document
  - Key Parameters Document
  - Simplified Three-Agent MVP Specification
  - Comprehensive PRD (600+ lines)
  - Agent Coordination Workflow (7 flowcharts)

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
| **Product Brief** | `04_PoC_Development/product_brief/product_brief_v2.1.md` | Main product specification |
| **PRD** | `04_PoC_Development/prd/prd_demand_forecasting_system.md` | Comprehensive requirements (600+ lines) |
| **Agent Coordination** | `04_PoC_Development/prd/agent_coordination_workflow.md` | Multi-agent orchestration + flowcharts |
| **Development Plan** | `04_PoC_Development/prd/development_plan.md` | 9-week implementation plan |
| **Operational Workflow** | `04_PoC_Development/product_brief/2_operational_workflow.md` | 5-phase seasonal workflow |
| **System Architecture** | `04_PoC_Development/Architecture/architecture_v1.1.md` | Technical architecture |

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

### ✅ Phase 4: Product Specifications (COMPLETE)
**Duration:** Weeks 6-8
**Deliverables:**
- Product Brief v2.1 (Archetype 2: Stable Catalog Retail)
- Operational Workflow (5-phase seasonal workflow)
- Key Parameters (3 retail archetypes, parameter-driven design)
- Comprehensive PRD (600+ lines with ML methods, agentic features)
- Agent Coordination Workflow (7 Mermaid flowcharts)
- 9-week Development Plan (Oct 10 - Dec 10)

### 🚧 Phase 5: PoC Development (STARTING - Week 8)
**Duration:** Weeks 8-16 (October 10 - December 10, 2025)
**Current Status:** Starting Phase 1 (Environment Setup & Data Generation)
**Planned:**
- Week 1-2: Environment setup, synthetic data generation (50 SKUs, 50 stores, 2 years)
- Week 3-4: Similar-item matching with OpenAI embeddings
- Week 4-5: Forecasting methods (Prophet, ARIMA, hybrid)
- Week 5-6: Inventory agent (manufacturing, allocation, replenishment)
- Week 6-7: Pricing agent + orchestrator (5-phase workflow)
- Week 8: Integration & validation (MAPE <20%, cost <$5)
- Week 9: Documentation & final report

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

**Week 4 (October 10, 2025):**
- ✅ Evidence Pack completed (6 components, 150+ pages)
- ✅ Product specifications completed (7 major deliverables)
- ✅ 9-week Development Plan finalized
- 🚧 Starting Phase 1: Environment Setup & Data Generation

**Next Milestone:** Week 2 - Data & Environment Ready (synthetic data for 50 SKUs, 50 stores, 2 years)

---

**Project Status:** Product Specs Complete ✅ | Development Starting 🚧
**Last Updated:** October 10, 2025
**Document Version:** 3.0
