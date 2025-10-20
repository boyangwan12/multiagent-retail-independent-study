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

**Week 5 (October 17, 2025):**
- ✅ All v3.3 planning documents complete (7/7)
  - Planning Guide with documentation standards
  - Product Brief v3.3 (parameter-driven architecture)
  - Process Workflow v3.3 (5-phase with examples)
  - Technical Architecture v3.3 (implementation-ready)
  - PRD v3.3 (complete requirements)
  - Frontend Spec v3.3 (full UI/UX design)
  - Data Specification v3.2 (structures & validation)
- ✅ Strategic pivot from hardcoded to parameter-driven design
  - LLM gathers key parameters (allocation %, season length, markdown timing)
  - Adapts to diverse retail workflows (fast fashion, premium, etc.)
  - Emphasizes agentic coordination over deep-dive forecasting
- ✅ Documentation restructured (flattened, numeric prefixes)
- 📊 Next: Mock data generation
- 🎨 Next: Frontend mockup
- 🔧 Next: Backend architecture implementation

**Progress:** Planning phase 100% complete, ready for implementation

---

## Contact

**Students:** Boyang Wang, Jintao Li, Yina Liang Li, Jaeyoon Lee, and Henry Tang.
**Supervisor:** Fatih Nayebi
**Institution:** McGill University
**Program:** MMA

---

## License

Academic project - All rights reserved.
