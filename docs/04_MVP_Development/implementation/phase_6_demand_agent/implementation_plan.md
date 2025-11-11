# Phase 6: Demand Agent - Implementation Plan

**Phase:** 6 of 8
**Goal:** Replace mock Demand Agent with real Prophet + ARIMA ensemble forecasting
**Agent:** `*agent dev` (BMad Dev Agent)
**Duration Estimate:** 3.5 days (28 hours)
**Actual Duration:** TBD
**Status:** Ready to Start - All Stories Planned

---

## Requirements Source

- **Primary:** `planning/4_prd_v3.3.md` - PRD Section 5.1-5.3 (Demand Forecasting Requirements)
- **Primary:** `planning/3_technical_architecture_v3.3.md` - ML Pipeline Architecture
- **Reference:** `planning/2_product_brief_v3.3.md` - Business value of accurate forecasting
- **Reference:** `phase_5_orchestrator_foundation/PHASE5_OVERVIEW.md` - DemandAgentContext contracts

---

## Key Deliverables

1. **Prophet Integration**
   - Prophet model wrapper class
   - Hyperparameter configuration (seasonality, changepoint_prior_scale)
   - Training on historical sales data (52+ weeks)
   - Weekly forecast generation
   - Confidence interval calculation

2. **ARIMA Integration**
   - ARIMA model wrapper class
   - Auto ARIMA for parameter selection (p, d, q)
   - Training on historical sales data
   - Weekly forecast generation
   - Residual analysis

3. **Ensemble Logic**
   - Weighted average combining Prophet + ARIMA
   - Dynamic weight calculation based on historical accuracy
   - Ensemble confidence scoring
   - Model selection fallback logic

4. **Demand Agent Implementation**
   - DemandAgent class implementing agent interface
   - Integration with Phase 5 AgentHandoffManager
   - DemandAgentContext consumption
   - forecast_result output generation
   - Error handling and logging

5. **Testing & Validation**
   - Unit tests for Prophet wrapper (5 tests)
   - Unit tests for ARIMA wrapper (5 tests)
   - Integration tests for ensemble (3 tests)
   - End-to-end workflow test (demand agent in orchestrator)
   - Accuracy validation (MAPE < 15% on test set)

---

## Phase 6 Stories

### Story 1: Prophet Forecasting Integration ✅ STORY READY
**File:** `stories/PHASE6-001-prophet-integration.md`
**Estimate:** 8 hours
**Actual:** TBD
**Dependencies:** Phase 5 complete
**Status:** ⏳ Not Started

**Summary:**
- Create ProphetWrapper class for model training and forecasting
- Configure seasonality settings (weekly, yearly)
- Train on historical sales data from database
- Generate weekly forecasts with confidence intervals
- Return forecasts in standardized format
- Write unit tests for Prophet wrapper

**Key Tasks:**
- [ ] Create backend/app/ml/prophet_wrapper.py with ProphetWrapper class
- [ ] Implement train() method using historical data
- [ ] Implement forecast() method for weekly predictions
- [ ] Add confidence interval calculation
- [ ] Configure seasonality parameters (weekly=True, yearly=True)
- [ ] Write 5 unit tests (train, forecast, confidence, edge cases, invalid data)
- [ ] Verify MAPE < 20% on validation set

---

### Story 2: ARIMA Forecasting Integration ✅ STORY READY
**File:** `stories/PHASE6-002-arima-integration.md`
**Estimate:** 6 hours
**Actual:** TBD
**Dependencies:** Story 1
**Status:** ⏳ Not Started

**Summary:**
- Create ARIMAWrapper class for model training and forecasting
- Implement auto ARIMA for parameter selection
- Train on historical sales data
- Generate weekly forecasts
- Calculate residuals and confidence intervals
- Write unit tests for ARIMA wrapper

**Key Tasks:**
- [ ] Install pmdarima library (Auto ARIMA)
- [ ] Create backend/app/ml/arima_wrapper.py with ARIMAWrapper class
- [ ] Implement auto_arima parameter selection (p, d, q)
- [ ] Implement train() method
- [ ] Implement forecast() method
- [ ] Add residual analysis and confidence intervals
- [ ] Write 5 unit tests (train, forecast, auto_arima, edge cases, stationary check)
- [ ] Verify MAPE < 20% on validation set

---

### Story 3: Ensemble Logic (Prophet + ARIMA) ✅ STORY READY
**File:** `stories/PHASE6-003-ensemble-logic.md`
**Estimate:** 8 hours
**Actual:** TBD
**Dependencies:** Story 1, Story 2
**Status:** ⏳ Not Started

**Summary:**
- Create EnsembleForecaster class combining Prophet + ARIMA
- Implement weighted average logic (default: 60% Prophet, 40% ARIMA)
- Calculate ensemble confidence score
- Add fallback logic if one model fails
- Write integration tests for ensemble

**Key Tasks:**
- [ ] Create backend/app/ml/ensemble_forecaster.py
- [ ] Implement weighted_average() combining both models
- [ ] Calculate dynamic weights based on validation MAPE
- [ ] Add fallback to single model if other fails
- [ ] Calculate ensemble confidence (min of both models)
- [ ] Write 3 integration tests (both models, prophet only, arima only)
- [ ] Verify ensemble MAPE < 15% on validation set

---

### Story 4: Demand Agent Integration & Testing ✅ STORY READY
**File:** `stories/PHASE6-004-integration-testing.md`
**Estimate:** 6 hours
**Actual:** TBD
**Dependencies:** Story 1, Story 2, Story 3
**Status:** ⏳ Not Started

**Summary:**
- Create DemandAgent class implementing agent interface
- Integrate with Phase 5 orchestrator
- Consume DemandAgentContext from ContextAssembler
- Return forecast_result matching contract
- Write end-to-end workflow test
- Performance optimization (<10 seconds forecast generation)

**Key Tasks:**
- [ ] Create backend/app/agents/demand_agent.py with DemandAgent class
- [ ] Implement execute(context: DemandAgentContext) -> dict
- [ ] Integrate EnsembleForecaster
- [ ] Format output as forecast_result (total_demand, forecast_by_week, confidence)
- [ ] Register agent with AgentHandoffManager
- [ ] Write end-to-end workflow test (parameters → demand agent → forecast_result)
- [ ] Optimize performance (target: <10 seconds)
- [ ] Update mock orchestrator to use real demand agent
- [ ] Verify integration with Phase 5 WebSocket streaming

---

## Success Criteria

### Functional Requirements
- ✅ Prophet wrapper trained on 52+ weeks of historical data
- ✅ ARIMA wrapper trained on same historical data
- ✅ Ensemble combines both models with weighted average
- ✅ Demand agent returns forecast_result matching DemandAgentOutput contract
- ✅ Integration with Phase 5 orchestrator (no orchestrator code changes)
- ✅ WebSocket messages sent during forecasting (progress updates)

### Quality Requirements
- ✅ MAPE < 15% on validation set (ensemble)
- ✅ Forecast generation completes in <10 seconds
- ✅ Unit test coverage >85% for ML wrappers
- ✅ Integration test coverage >90% for demand agent
- ✅ All tests passing in pytest
- ✅ No breaking changes to Phase 5 orchestrator

### Business Requirements
- ✅ Forecasts are parameter-driven (horizon weeks, season dates)
- ✅ Forecasts adapt to different retail strategies (Zara vs traditional)
- ✅ Safety stock calculated based on forecast confidence
- ✅ Forecast output consumed successfully by Phase 7 (Inventory Agent)

---

## Dependencies

### Phase 5 (Orchestrator Foundation) - MUST BE COMPLETE
- [x] Phase 5 stories complete
- [x] AgentHandoffManager operational
- [x] ContextAssembler can build DemandAgentContext
- [x] WebSocket streaming functional
- [x] Mock demand agent replaced by real agent

### Python Libraries - MUST BE INSTALLED
- [ ] prophet (Meta's time series forecasting library)
- [ ] pmdarima (Auto ARIMA for parameter selection)
- [ ] scikit-learn (for MAPE calculation and train/test split)
- [ ] numpy (for array operations)
- [ ] pandas (already installed)

### Data Requirements - MUST BE AVAILABLE
- [x] Historical sales data in database (52+ weeks)
- [x] Store data in database (for context)
- [x] Phase 4.5 data upload complete

---

## Risk Mitigation

### Risk 1: Prophet/ARIMA Library Installation Issues
**Probability:** Medium
**Impact:** High (blocks all development)
**Mitigation:**
- Test library installation in virtual environment BEFORE starting stories
- Document any dependency conflicts
- Use uv for dependency management (consistent with project)

### Risk 2: Poor Forecast Accuracy (MAPE > 15%)
**Probability:** Medium
**Impact:** High (core business value compromised)
**Mitigation:**
- Tune hyperparameters during Story 1 and 2
- Implement ensemble in Story 3 to improve accuracy
- Add validation set testing in all stories
- Document accuracy metrics in each test

### Risk 3: Performance Issues (>10 seconds forecast)
**Probability:** Low
**Impact:** Medium (user experience degraded)
**Mitigation:**
- Profile code during Story 4
- Cache trained models if possible
- Optimize data loading (already done in Phase 5 context assembly)
- Consider async processing if needed

### Risk 4: Integration Issues with Phase 5
**Probability:** Low
**Impact:** Medium (delays Phase 6 completion)
**Mitigation:**
- Follow DemandAgentContext contract strictly
- Test with Phase 5 orchestrator after each story
- No changes to Phase 5 code (only replace mock agent)

---

## Testing Strategy

### Unit Tests (Prophet/ARIMA Wrappers)
```python
# tests/unit/ml/test_prophet_wrapper.py
def test_prophet_train_with_historical_data()
def test_prophet_forecast_returns_weekly_predictions()
def test_prophet_confidence_intervals()
def test_prophet_handles_missing_data()
def test_prophet_raises_error_on_insufficient_data()

# tests/unit/ml/test_arima_wrapper.py
def test_arima_auto_parameter_selection()
def test_arima_train_with_historical_data()
def test_arima_forecast_returns_weekly_predictions()
def test_arima_handles_non_stationary_data()
def test_arima_confidence_intervals()
```

### Integration Tests (Ensemble + Demand Agent)
```python
# tests/integration/test_ensemble_forecaster.py
def test_ensemble_combines_prophet_and_arima()
def test_ensemble_fallback_to_prophet_only()
def test_ensemble_fallback_to_arima_only()

# tests/integration/test_demand_agent.py
def test_demand_agent_with_real_historical_data()
def test_demand_agent_output_matches_contract()
def test_demand_agent_integrates_with_orchestrator()
def test_demand_agent_sends_websocket_progress()
```

### Performance Tests
```python
# tests/performance/test_forecast_performance.py
def test_forecast_generation_under_10_seconds()
def test_context_assembly_cached_performance()
```

---

## Technical Decisions

See `technical_decisions.md` for detailed technical choices including:
- Why Prophet + ARIMA ensemble over single model
- Hyperparameter tuning approach
- Weight calculation for ensemble
- Error handling strategy
- Model versioning (future consideration)

---

## Definition of Done

**Story-Level DoD:**
- [ ] All acceptance criteria met
- [ ] All tasks completed
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Code reviewed (self-review minimum)
- [ ] Documentation updated (docstrings)
- [ ] No console.log or debug statements
- [ ] Performance targets met

**Phase-Level DoD:**
- [ ] All 4 stories complete
- [ ] MAPE < 15% on validation set
- [ ] Forecast generation < 10 seconds
- [ ] Integration with Phase 5 orchestrator verified
- [ ] End-to-end workflow test passing
- [ ] Ready to hand off forecast_result to Phase 7 (Inventory Agent)

---

## Next Phase

**Phase 7: Inventory Agent**
- Consumes forecast_result from Phase 6
- Implements K-means clustering for store segmentation
- Generates inventory allocation by store
- Enables Section 5 (Replenishment Queue) in frontend

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
