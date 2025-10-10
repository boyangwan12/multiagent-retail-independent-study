# Independent Study: Multi-Agent Demand Forecasting System

**Institution:** Concordia University
**Program:** Master of Engineering in Quality Systems Engineering
**Timeline:** September 2025 - January 2026
**Focus:** LLM-powered multi-agent system for retail demand forecasting and inventory allocation

---

## Project Overview

Building a **3-agent demand forecasting and inventory allocation system** for retail using LangChain and OpenAI APIs. The system predicts store-week granular demand and optimizes inventory decisions to address critical pain points: inaccurate forecasting, location-specific allocation failures, and late markdown decisions.

**Core Prediction:** `demand_by_store_by_week` matrix (50 stores × 26 weeks = 1,300 predictions per SKU)

**MVP Scope:** Archetype 2 - Stable Catalog Retail (furniture, 26-week season, 50 SKUs, 50 stores)

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
│   │   │   ├── product_brief_v2.1.md           # Main product specification
│   │   │   ├── 2_key_parameter.md              # Parameter-driven design (3 archetypes)
│   │   │   └── 2_operational_workflow.md       # 5-phase seasonal workflow
│   │   │
│   │   ├── prd/
│   │   │   ├── prd_demand_forecasting_system.md        # Comprehensive PRD (600+ lines)
│   │   │   ├── agent_coordination_workflow.md          # Multi-agent orchestration + flowcharts
│   │   │   └── development_plan.md                     # 9-week implementation plan
│   │   │
│   │   ├── Architecture/
│   │   │   └── architecture_v1.1.md            # System architecture design
│   │   │
│   │   └── Research/
│   │       └── OpenAI_Agents_SDK_Retail_PoC_Research.md
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

### Product Specifications
- **[Product Brief v2.1](docs/04_PoC_Development/product_brief/product_brief_v2.1.md)**: Problem definition, solution overview, evidence-based validation
- **[PRD - Demand Forecasting System](docs/04_PoC_Development/prd/prd_demand_forecasting_system.md)**: Comprehensive requirements with ML methods, agentic features, user stories
- **[Agent Coordination Workflow](docs/04_PoC_Development/prd/agent_coordination_workflow.md)**: Multi-agent orchestration with 7 Mermaid flowcharts
- **[Development Plan](docs/04_PoC_Development/prd/development_plan.md)**: 9-week implementation timeline (Oct 10 - Dec 10, 2025)

### Research & Validation
- **[Evidence Pack](docs/03_Evidence_Pack/)**: 6 components validating problem-solution fit with 5 practitioner interviews
- **[Pain Point Inventory](docs/03_Evidence_Pack/_extraction/Pain_Point_Inventory.md)**: 28 pain points extracted from user research

---

## System Architecture

### 3 Agents + Orchestrator

| Agent | Responsibility | Key Output |
|-------|---------------|-----------|
| **Demand Agent** | Predict store-week demand using similar-item matching + time-series | `demand_by_store_by_week` matrix |
| **Inventory Agent** | Calculate manufacturing orders, allocate inventory, plan replenishment | Manufacturing order, allocation plans |
| **Pricing Agent** | Monitor sell-through, recommend markdowns | Markdown triggers, depth recommendations |
| **Orchestrator** | Coordinate agents through 5-phase seasonal workflow | Agent execution sequence, performance metrics |

### Agentic Features
- **Autonomous decision-making**: LLM chooses forecasting methods (Prophet, ARIMA, hybrid)
- **Reasoning & explanation**: Natural language explanations for all decisions
- **Semantic understanding**: OpenAI embeddings for similar-item matching
- **Adaptive behavior**: Method selection based on data availability and confidence
- **Multi-agent collaboration**: Cascading decisions (Pricing → Demand → Inventory)

### Technology Stack
- **LLM API**: OpenAI SDK (gpt-4o-mini, text-embedding-3-small)
- **Agent Framework**: LangChain
- **Forecasting**: Prophet, statsmodels (ARIMA/SARIMA)
- **Data Processing**: pandas, NumPy
- **Storage**: SQLite, CSV/Parquet (local)
- **Budget**: <$5 LLM costs (~$0.05 per season)

---

## Development Timeline

**Phase 1 (Weeks 1-2):** Environment setup, synthetic data generation
**Phase 2 (Weeks 3-4):** Similar-item matching with embeddings
**Phase 3 (Weeks 4-5):** Forecasting methods (Prophet, ARIMA, hybrid)
**Phase 4 (Weeks 5-6):** Inventory agent (manufacturing, allocation, replenishment)
**Phase 5 (Weeks 6-7):** Pricing agent + orchestrator
**Phase 6 (Week 8):** Integration & validation (MAPE <20%)
**Phase 7 (Week 9):** Documentation & final report

---

## Problem Addressed

Based on interviews with 5 retail practitioners, the system addresses:

1. **Inaccurate Demand Forecasting (PP-001)**: 20% forecast error on product launches
2. **Location-Specific Allocation Failures (PP-002, PP-015)**: 5 hrs/week firefighting + ongoing stockout/overstock costs
3. **Late Markdown Decisions (PP-016)**: **$500K lost margin annually**
4. **Inventory Optimization Challenges (PP-028)**: Balancing overstock vs understock across 50 stores

---

## Success Metrics (MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE (Store-Week)** | <20% | Hindcast on synthetic data |
| **Bias** | ±5% | Over/under-forecasting check |
| **Confidence Calibration** | 80%+ | Predicted confidence vs actual error |
| **Runtime (Initial Forecast)** | <4 hours | 50 SKUs, local machine |
| **Runtime (Bi-weekly Update)** | <30 min | Single update cycle |
| **LLM Cost** | <$5 | Total for full season (26 weeks) |

---

## Current Status

**Week 4 (October 10, 2025):**
- ✅ Evidence Pack completed (6 components)
- ✅ Product Brief v2.1 finalized
- ✅ Comprehensive PRD with ML methods and agentic features
- ✅ Agent Coordination Workflow with 7 flowcharts
- ✅ 9-week Development Plan
- 🚧 Starting Phase 1: Environment Setup & Data Generation

---

## Contact

**Student:** [Your Name]
**Supervisor:** [Supervisor Name]
**Institution:** Concordia University
**Program:** MEng Quality Systems Engineering

---

## License

Academic project - All rights reserved.
