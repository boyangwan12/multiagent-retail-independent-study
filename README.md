# Independent Study: Multi-Agent Demand Forecasting System

**Institution:** Concordia University
**Program:** Master of Engineering in Quality Systems Engineering
**Timeline:** September 2025 - January 2026
**Focus:** LLM-powered multi-agent system for retail demand forecasting and inventory allocation

---

## Project Overview

Building a **3-agent demand forecasting and inventory allocation system** for retail using OpenAI Agents SDK. The system uses **category-level hierarchical forecasting** to predict demand and optimize inventory decisions, addressing critical pain points: inaccurate forecasting, location-specific allocation failures, and late markdown decisions.

**Core Innovation:** "Forecast Once, Allocate with Math" - Category-level forecast (1 prediction) + hierarchical allocation (Category → Cluster → Store)

**MVP Scope:** Archetype 1 - Fashion Retail (Women's Dresses, 12-week season, 50 stores, 3 clusters)

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
│   ├── 04_PoC_Development/
│   │   ├── product_brief/
│   │   │   ├── product_brief_v3.1.md           # ✅ Current product spec (Archetype 1)
│   │   │   └── 3_operational_workflow.md       # ✅ Streamlined workflow with examples
│   │   │
│   │   ├── architecture/
│   │   │   └── technical_architecture.md       # ✅ Complete architecture (20 sections, includes handoff patterns)
│   │   │
│   │   ├── Design/                             # 🎨 TODO: UI/UX design
│   │   ├── Data/                               # 📊 TODO: Data requirements
│   │   ├── prd/                                # 📋 TODO: New PRD for Archetype 1
│   │   │
│   │   ├── Research/
│   │   │   └── OpenAI_Agents_SDK_Retail_PoC_Research.md
│   │   │
│   │   ├── archive/                            # Old Archetype 2 documents
│   │   └── next_steps_plan.md                  # Roadmap to implementation
│   │
│   └── 05_Progress_Reports/
│       └── Weekly_Supervisor_Meetings/         # Weekly progress updates
│           ├── Week_01_Updates.md
│           ├── Week_02_Updates.md
│           ├── Week_03_Updates.md
│           └── Week_04_Updates.md
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

### Product Specifications (Current - Archetype 1)
- **[Product Brief v3.1](docs/04_PoC_Development/product_brief/product_brief_v3.1.md)**: Category-level forecasting approach, Archetype 1 (Fashion Retail, 12 weeks)
- **[Operational Workflow v3](docs/04_PoC_Development/product_brief/3_operational_workflow.md)**: Streamlined workflow with concrete examples
- **[Technical Architecture](docs/04_PoC_Development/architecture/technical_architecture.md)**: Complete backend architecture (20 sections) - OpenAI Agents SDK, Prophet+ARIMA, React+TypeScript, includes agent coordination workflow
- **[Next Steps Plan](docs/04_PoC_Development/next_steps_plan.md)**: Document roadmap to implementation

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

**Week 4 (October 12, 2025):**
- ✅ Evidence Pack completed (6 components)
- ✅ Product Brief v3.1 finalized (Archetype 1: Fashion Retail)
- ✅ Operational Workflow v3 (streamlined with examples)
- ✅ Technical Architecture complete (20 sections, implementation-ready)
  - OpenAI Agents SDK + UV + FastAPI + React
  - Prophet+ARIMA ensemble, K-means clustering
  - Context-rich handoffs, dynamic re-forecast enabling
  - WebSocket real-time updates, human-in-the-loop
- 🎨 Next: UI/UX Design (talk to `*agent designer`)
- 📋 Next: PRD for Archetype 1 (talk to `*agent pm`)
- 📊 Next: Data Requirements (talk to `*agent data`)

**Progress:** 3/7 documents complete (43%)

---

## Contact

**Student:** [Your Name]
**Supervisor:** [Supervisor Name]
**Institution:** Concordia University
**Program:** MEng Quality Systems Engineering

---

## License

Academic project - All rights reserved.
