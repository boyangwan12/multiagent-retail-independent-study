# Phase 5: Demand Agent - Checklist

**Phase:** 5 of 8
**Agent:** `*agent dev`
**Status:** Not Started
**Progress:** 0/13 tasks complete

---

## Task Checklist

### Task 1: Demand Agent Foundation & LLM Instructions
- [ ] Update `backend/app/agents/demand.py` (remove mock implementation)
- [ ] Define Demand Agent using OpenAI Agents SDK
- [ ] Write LLM instructions for parameter interpretation
- [ ] Add parameter context to agent initialization
- [ ] Implement handoff registration (to Inventory Agent)
- [ ] Create `DemandAgentContext` data class
- [ ] Test basic agent creation and parameter reception
**Status:** Not Started

### Task 2: Ensemble Forecasting - Prophet Implementation
- [ ] Install Prophet: `uv add prophet`
- [ ] Create `backend/app/ml/prophet_forecast.py`
- [ ] Implement Prophet forecasting function
- [ ] Handle Prophet-specific parameters (changepoint_prior_scale, seasonality_mode)
- [ ] Implement error handling for Prophet failures
- [ ] Add logging for Prophet model parameters
- [ ] Unit tests for Prophet forecast function
**Status:** Not Started

### Task 3: Ensemble Forecasting - ARIMA Implementation
- [ ] Install pmdarima: `uv add pmdarima`
- [ ] Create `backend/app/ml/arima_forecast.py`
- [ ] Implement auto-ARIMA forecasting function
- [ ] Handle ARIMA-specific settings (seasonal ARIMA, stepwise)
- [ ] Implement error handling for ARIMA failures
- [ ] Add logging for ARIMA model parameters
- [ ] Unit tests for ARIMA forecast function
**Status:** Not Started

### Task 4: Ensemble Averaging & Parallel Execution
- [ ] Create `backend/app/ml/ensemble_forecast.py`
- [ ] Implement parallel execution of Prophet + ARIMA (asyncio.gather)
- [ ] Implement ensemble averaging logic
- [ ] Add model agreement metric (% difference)
- [ ] Implement fallback logic (Prophet fails → ARIMA only, etc.)
- [ ] Unit tests for ensemble logic
**Status:** Not Started

### Task 5: K-means Store Clustering
- [ ] Install scikit-learn: `uv add scikit-learn`
- [ ] Create `backend/app/ml/clustering.py`
- [ ] Implement K-means clustering with 7 features
- [ ] Apply StandardScaler normalization
- [ ] Run K-means++ (K=3)
- [ ] Calculate cluster characteristics
- [ ] Calculate clustering quality metrics (silhouette score >0.4)
- [ ] Save cluster assignments to database
- [ ] Unit tests for clustering logic
**Status:** Not Started

### Task 6: Cluster Distribution & Store Allocation Factors
- [ ] Create `backend/app/ml/allocation.py`
- [ ] Implement cluster distribution calculation
- [ ] Implement store allocation factor calculation (70% historical + 30% attributes)
- [ ] Validate allocation factors sum to 100% per cluster
- [ ] Unit tests for allocation logic
**Status:** Not Started

### Task 7: Parameter-Aware Safety Stock Adjustment
- [ ] Create `backend/app/agents/demand_reasoning.py`
- [ ] Implement safety stock adjustment logic (20%-25%)
- [ ] Add LLM reasoning for safety stock decision
- [ ] Return safety stock multiplier with forecast
- [ ] Unit tests for safety stock logic
**Status:** Not Started

### Task 8: Structured Forecast Output & Handoff Object
- [ ] Create `backend/app/schemas/forecast.py`
- [ ] Define `ForecastResult` Pydantic model
- [ ] Define `ClusterDistribution` Pydantic model
- [ ] Define `StoreAllocation` Pydantic model
- [ ] Implement forecast object builder
- [ ] Test JSON serialization for handoff
- [ ] Integration test with Orchestrator handoff
**Status:** Not Started

### Task 9: Demand Agent Main Logic Integration
- [ ] Implement `demand_agent_main()` function
- [ ] Orchestrate all 10 components (parameter → forecast → handoff)
- [ ] Add comprehensive error handling
- [ ] Add logging for all major steps
- [ ] Add WebSocket status updates
- [ ] Validate execution time <10 seconds
**Status:** Not Started

### Task 10: Re-Forecast Logic (Variance-Triggered)
- [ ] Implement re-forecast logic for variance triggers
- [ ] Receive variance context from Orchestrator
- [ ] Adjust historical data with actuals
- [ ] Re-run ensemble forecast for remaining weeks
- [ ] Return updated forecast object
- [ ] Unit tests for re-forecast logic
**Status:** Not Started

### Task 11: Integration Testing with Orchestrator
- [ ] Create integration test suite
- [ ] Test 1: Zara parameters (no replenishment, 25% safety stock)
- [ ] Test 2: Standard retail parameters (weekly replenishment, 20% safety stock)
- [ ] Test 3: Luxury parameters (no markdowns)
- [ ] Test 4: Variance-triggered re-forecast (>20% at Week 5)
- [ ] Test 5: Prophet failure fallback (ARIMA-only)
- [ ] Test 6: End-to-end workflow (Orchestrator → Demand → Inventory handoff)
**Status:** Not Started

### Task 12: Performance Optimization
- [ ] Profile forecast execution time (Prophet, ARIMA, clustering)
- [ ] Optimize slow components (caching, Pandas optimization)
- [ ] Target: <10 seconds total execution
- [ ] Add performance metrics to logs
**Status:** Not Started

### Task 13: Documentation & Code Quality
- [ ] Document Demand Agent logic (docstrings)
- [ ] Add inline code comments for complex sections
- [ ] Create `backend/app/agents/README_DEMAND.md`
- [ ] Add type hints to all functions
- [ ] Run mypy type checking
- [ ] Run Ruff linting and formatting
- [ ] Update main README with Demand Agent details
**Status:** Not Started

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (40% complete)
- [ ] Demand Agent foundation created
- [ ] Ensemble forecasting (Prophet + ARIMA) working
- [ ] K-means clustering functional
- [ ] Clustering quality metrics acceptable (silhouette >0.4)
- [ ] Parameter context received correctly
**Status:** Not Started

### Checkpoint 2: Pre-Completion (80% complete)
- [ ] All ML components integrated
- [ ] Structured forecast object returned
- [ ] Safety stock adjustment working
- [ ] Store allocation factors calculated
- [ ] Re-forecast logic functional
- [ ] WebSocket status updates working
**Status:** Not Started

### Checkpoint 3: Final
- [ ] Integration tests passing (6/6)
- [ ] End-to-end workflow test passing (Orchestrator → Demand → Inventory handoff)
- [ ] Forecast MAPE <20% on Phase 1 CSV data
- [ ] Performance target met (<10 seconds)
- [ ] Documentation complete
- [ ] Ready for handoff to Phase 6 (Inventory Agent)
**Status:** Not Started

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Forecast MAPE | <20% | TBD | TBD |
| Clustering silhouette score | >0.4 | TBD | TBD |
| Prophet + ARIMA agreement | Within 10% | TBD | TBD |
| Parameter interpretation accuracy | >90% | TBD | TBD |
| Forecast execution time | <10s | TBD | TBD |
| Context-rich handoff success | 100% | TBD | TBD |

---

## Notes

- Update this checklist in real-time as tasks complete
- Mark subtasks with [x] when done
- This implements actual ML models (Prophet, ARIMA, K-means)
- Replaces mocked Demand Agent from Phase 4
- Phase 1 CSV data required for historical forecasting (52+ weeks)

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Progress:** 0/13 tasks (0%)
