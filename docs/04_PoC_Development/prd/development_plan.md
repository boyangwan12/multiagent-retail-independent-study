# Development Plan
**Multi-Agent Demand Forecasting System - MVP**

**Timeline:** October 10 - December 10, 2025 (9 weeks)
**Archetype:** Archetype 2 - Stable Catalog Retail
**Budget:** <$5 (LLM API costs)

---

## Overview

Build a 3-agent demand forecasting and inventory allocation system using LangChain + OpenAI (gpt-4o-mini). Validate on synthetic furniture retail data (50 SKUs, 50 stores, 26-week season).

---

## Phase 1: Environment Setup & Data Generation (Week 1-2)
**Dates:** October 10-23, 2025

### Deliverables
- Python environment with dependencies (LangChain, OpenAI SDK, pandas, Prophet, statsmodels)
- Synthetic historical sales data (2 years, 50 SKUs, 50 stores)
- Product catalog (50 furniture SKUs with attributes)
- Store master data (50 stores with size, region, demographics)
- Configuration system (YAML for Archetype 2 parameters)

### Key Tasks
- Set up local development environment
- Generate realistic synthetic data using statistical distributions
- Create data validation pipeline
- Build YAML config loader for archetype parameters

### Success Criteria
- Historical data completeness ≥80%
- Data passes validation checks
- Config system loads Archetype 2 parameters correctly

---

## Phase 2: Demand Agent - Similar-Item Matching (Week 3-4)
**Dates:** October 24 - November 6, 2025

### Deliverables
- Similar-item matching using OpenAI embeddings (text-embedding-3-small)
- Embedding cache system (avoid repeated API calls)
- Top-5 similar SKU retrieval with similarity scores
- Confidence scoring based on match quality

### Key Tasks
- Implement SKU attribute → text description converter
- Build embedding generation pipeline
- Create cosine similarity search
- Validate matches on 10 test SKUs

### Success Criteria
- Similarity score >0.75 for relevant matches
- Embedding cost <$0.05 for 50 SKUs
- Manual validation: 8/10 similar items make business sense

---

## Phase 3: Demand Agent - Forecasting Methods (Week 4-5)
**Dates:** November 7-20, 2025

### Deliverables
- Prophet forecasting for new SKUs (<12 weeks data)
- ARIMA/SARIMA for existing SKUs (12+ weeks data)
- Hybrid approach (similar-item + time-series)
- Store-level disaggregation logic
- LLM-based method selection (gpt-4o-mini)

### Key Tasks
- Implement Prophet forecasting wrapper
- Implement ARIMA forecasting wrapper
- Build adaptive logic: method selection based on data availability
- Create store-level split using historical penetration rates
- Test on 10 SKUs with varying data availability

### Success Criteria
- Generates 50 stores × 26 weeks forecast matrix
- Method selection makes logical decisions
- Forecast runtime <4 hours for 50 SKUs

---

## Phase 4: Inventory Agent (Week 5-6)
**Dates:** November 21 - December 4, 2025

### Deliverables
- Manufacturing order calculation (demand + 15% safety stock)
- Initial allocation (first 2 weeks demand per store)
- Bi-weekly replenishment planning (periodic review policy)
- DC holdback optimization (60-70% constraint)

### Key Tasks
- Implement manufacturing order formula
- Build proportional allocation logic
- Create replenishment calculator (target inventory - current inventory)
- Validate DC holdback meets 60-70% threshold

### Success Criteria
- Manufacturing order = total demand + 15%
- Initial allocation leaves 60-70% at DC
- Replenishment plan covers all 26 weeks

---

## Phase 5: Pricing Agent & Orchestrator (Week 6-7)
**Dates:** December 5-11, 2025 (partial overlap with Phase 4)

### Deliverables
- Sell-through monitoring (Week 12 checkpoint)
- Markdown trigger (threshold: 50%)
- Markdown depth calculation (10%, 20%, 30% tiered rules)
- Post-markdown demand adjustment (elasticity-based)
- Orchestrator with 5-phase workflow coordination
- Variance detection (>15% threshold)
- Performance monitoring (MAPE, bias)

### Key Tasks
- Implement sell-through calculator
- Build markdown recommendation logic
- Create orchestrator state machine (5 phases)
- Implement variance-triggered re-forecast
- Add LLM reasoning for edge cases

### Success Criteria
- Pricing Agent correctly triggers markdown when sell-through <50%
- Orchestrator executes all 5 phases sequentially
- Variance detection triggers re-forecast correctly

---

## Phase 6: Integration & Validation (Week 8)
**Dates:** December 12-18, 2025 (if time permits)

### Deliverables
- End-to-end workflow execution (Week -12 to Week 26)
- Hindcast validation on synthetic data
- MAPE calculation vs baseline methods
- Confidence calibration check
- User documentation (README, setup guide)

### Key Tasks
- Run full season simulation
- Calculate MAPE, bias, confidence calibration
- Compare to naive baseline (historical average)
- Document setup and usage instructions
- Create demo notebook

### Success Criteria
- MAPE <20% (target from PRD)
- Bias ±5%
- System completes full season without errors
- LLM cost <$5 total

---

## Phase 7: Documentation & Final Report (Week 9)
**Dates:** December 19-31, 2025 (extends past deadline if needed)

### Deliverables
- Technical documentation
- Performance analysis report
- Code documentation
- Final presentation deck

### Key Tasks
- Document code with docstrings
- Write performance analysis (MAPE, cost, runtime)
- Create presentation summarizing results
- Prepare demo for supervisor meeting

### Success Criteria
- All code documented
- Performance report shows MAPE <20%
- Demo runs successfully

---

## Milestones

| Week | Milestone | Key Output |
|------|-----------|-----------|
| **Week 2** | Data & Environment Ready | Synthetic data (2 years, 50 SKUs, 50 stores) |
| **Week 4** | Similar-Item Matching Works | Top-5 matches with >0.75 similarity |
| **Week 5** | Demand Agent Complete | 50 stores × 26 weeks forecast matrix |
| **Week 6** | Inventory Agent Complete | Manufacturing order + replenishment plan |
| **Week 7** | Full System Integration | Orchestrator runs 5-phase workflow |
| **Week 8** | Validation Complete | MAPE <20%, cost <$5 |
| **Week 9** | Final Deliverables | Documentation + presentation |

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **LLM costs exceed $5** | Medium | Low | Cache embeddings, minimize API calls, use gpt-4o-mini |
| **Forecasting accuracy <20% MAPE** | Medium | High | Focus on similar-item matching quality, use ensemble methods |
| **Runtime >4 hours** | Low | Medium | Parallelize SKU forecasting, optimize embeddings |
| **Data generation unrealistic** | Medium | Medium | Validate with industry benchmarks, adjust distributions |
| **Integration complexity** | Medium | Medium | Build incrementally, test each agent independently first |

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.9+ | Development |
| **LLM API** | OpenAI SDK (gpt-4o-mini, text-embedding-3-small) | Agent reasoning, embeddings |
| **Agent Framework** | LangChain | Multi-agent orchestration |
| **Forecasting** | Prophet, statsmodels (ARIMA) | Time-series forecasting |
| **Data Processing** | pandas, NumPy | Data manipulation |
| **Storage** | SQLite, CSV/Parquet | Local data storage |
| **Testing** | pytest | Unit tests |
| **Version Control** | Git/GitHub | Code versioning |

---

## Development Approach

**Incremental Development:**
1. Build each agent independently
2. Test agent in isolation before integration
3. Integrate agents one at a time into Orchestrator
4. Validate end-to-end workflow

**Testing Strategy:**
- Unit tests for core functions (forecasting, allocation)
- Integration tests for agent communication
- End-to-end test on synthetic season data

**Code Organization:**
```
src/
├── agents/
│   ├── demand_agent.py
│   ├── inventory_agent.py
│   ├── pricing_agent.py
│   └── orchestrator.py
├── forecasting/
│   ├── prophet_wrapper.py
│   ├── arima_wrapper.py
│   └── similar_item.py
├── data/
│   ├── synthetic_generator.py
│   └── loader.py
├── config/
│   └── archetype2_config.yaml
└── utils/
    ├── metrics.py
    └── logger.py
```

---

## Weekly Checkpoints

**Every Friday:**
- Review progress against phase deliverables
- Update Week_XX_Updates.md with completed tasks
- Identify blockers and adjust timeline if needed
- Estimate remaining effort

**Deliverable Tracking:**
- Use GitHub issues/projects for task management
- Commit code daily
- Document decisions in meeting notes

---

## Success Metrics (Final)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAPE** | <20% | Hindcast on synthetic data |
| **Bias** | ±5% | Over/under-forecasting check |
| **Confidence Calibration** | 80%+ | Predicted confidence vs actual error |
| **Runtime (Initial Forecast)** | <4 hours | 50 SKUs, local machine |
| **Runtime (Bi-weekly Update)** | <30 min | Single update cycle |
| **LLM Cost** | <$5 | Total for full season |
| **Code Coverage** | >70% | pytest coverage report |

---

**Next Step:** Begin Phase 1 (Environment Setup & Data Generation) on October 10, 2025.

**Reference Documents:**
- [PRD](prd_demand_forecasting_system.md)
- [Agent Coordination Workflow](agent_coordination_workflow.md)
- [Product Brief](../product_brief/2_demand_forecasting_product_brief.md)
