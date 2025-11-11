# Phase 6: Demand Agent - Implementation Checklist

**Phase:** 6 of 8
**Status:** Ready to Start
**Created:** 2025-11-11
**Estimated Duration:** 28 hours (3.5 days)

---

## Pre-Implementation Setup

### Environment Setup
- [ ] Python libraries installed
  - [ ] `uv add prophet` (time series forecasting)
  - [ ] `uv add pmdarima` (Auto ARIMA)
  - [ ] `uv add scikit-learn` (MAPE calculation)
  - [ ] Test imports: `python -c "from prophet import Prophet; from pmdarima import auto_arima; print('OK')"`

### Phase 5 Verification
- [x] Phase 5 (Orchestrator Foundation) complete
- [x] AgentHandoffManager operational
- [x] DemandAgentContext schema defined
- [x] ContextAssembler functional
- [x] WebSocket streaming working

### Data Verification
- [x] Historical sales data in database (52+ weeks)
- [x] Store data in database
- [x] Can load data via ContextAssembler

---

## Story 1: Prophet Integration (8 hours)

**File:** `stories/PHASE6-001-prophet-integration.md`
**Goal:** Integrate Facebook Prophet for seasonality forecasting

### Tasks
- [ ] Task 1: Install Prophet library (30 min)
  - [ ] Run `uv add prophet`
  - [ ] Verify installation
  - [ ] Document any issues

- [ ] Task 2: Create ProphetWrapper skeleton (1 hour)
  - [ ] Create `backend/app/ml/prophet_wrapper.py`
  - [ ] Define class structure
  - [ ] Add method stubs with docstrings

- [ ] Task 3: Implement train() method (2 hours)
  - [ ] Validate input data
  - [ ] Preprocess for Prophet (rename columns to 'ds', 'y')
  - [ ] Configure Prophet hyperparameters
  - [ ] Train model
  - [ ] Add error handling

- [ ] Task 4: Implement forecast() method (1.5 hours)
  - [ ] Generate predictions
  - [ ] Format output dictionary
  - [ ] Round to integers

- [ ] Task 5: Implement get_confidence() method (1 hour)
  - [ ] Calculate confidence from intervals
  - [ ] Return score in [0.0, 1.0]

- [ ] Task 6: Write unit tests (1.5 hours)
  - [ ] Test train with valid data
  - [ ] Test forecast shape
  - [ ] Test confidence score
  - [ ] Test insufficient data error
  - [ ] Test forecast without training error

- [ ] Task 7: Validation testing (30 min)
  - [ ] Split data (52 train, 10 validation)
  - [ ] Calculate MAPE
  - [ ] Assert MAPE < 20%

### Story 1 DoD
- [ ] ProphetWrapper class complete
- [ ] All 5 unit tests passing
- [ ] MAPE < 20% on validation set
- [ ] Code reviewed

---

## Story 2: ARIMA Integration (6 hours)

**File:** `stories/PHASE6-002-arima-integration.md`
**Goal:** Integrate ARIMA with Auto parameter selection

### Tasks
- [ ] Task 1: Install pmdarima (30 min)
  - [ ] Run `uv add pmdarima`
  - [ ] Verify installation

- [ ] Task 2: Create ARIMAWrapper skeleton (45 min)
  - [ ] Create `backend/app/ml/arima_wrapper.py`
  - [ ] Define class structure

- [ ] Task 3: Implement train() with Auto ARIMA (2 hours)
  - [ ] Configure auto_arima
  - [ ] Train model
  - [ ] Log selected (p, d, q)
  - [ ] Add fallback to ARIMA(1,1,1)

- [ ] Task 4: Implement forecast() method (1 hour)
  - [ ] Generate predictions with confidence intervals
  - [ ] Format output

- [ ] Task 5: Implement get_confidence() (30 min)
  - [ ] Calculate from intervals

- [ ] Task 6: Write unit tests (1 hour)
  - [ ] Test auto parameter selection
  - [ ] Test train
  - [ ] Test forecast
  - [ ] Test non-stationary data handling
  - [ ] Test insufficient data error

- [ ] Task 7: Validation testing (30 min)
  - [ ] Calculate MAPE
  - [ ] Assert MAPE < 20%

### Story 2 DoD
- [ ] ARIMAWrapper class complete
- [ ] All 5 unit tests passing
- [ ] MAPE < 20% on validation set
- [ ] Auto ARIMA working correctly

---

## Story 3: Ensemble Logic (8 hours)

**File:** `stories/PHASE6-003-ensemble-logic.md`
**Goal:** Combine Prophet and ARIMA with weighted averaging

### Tasks
- [ ] Task 1: Create EnsembleForecaster skeleton (1 hour)
  - [ ] Create `backend/app/ml/ensemble_forecaster.py`
  - [ ] Define class structure with Prophet + ARIMA

- [ ] Task 2: Implement train() method (1.5 hours)
  - [ ] Train both models
  - [ ] Add fallback handling
  - [ ] Update model_used field

- [ ] Task 3: Implement _weighted_average() (1 hour)
  - [ ] Calculate weighted average
  - [ ] Validate inputs

- [ ] Task 4: Implement _calculate_dynamic_weights() (1.5 hours)
  - [ ] Calculate validation MAPE for both models
  - [ ] Compute optimal weights

- [ ] Task 5: Implement forecast() with fallback (2 hours)
  - [ ] Generate forecasts from both models
  - [ ] Implement fallback logic
  - [ ] Calculate ensemble confidence

- [ ] Task 6: Write integration tests (1.5 hours)
  - [ ] Test ensemble with both models
  - [ ] Test fallback to Prophet only
  - [ ] Test fallback to ARIMA only

- [ ] Task 7: Validation testing (30 min)
  - [ ] Calculate ensemble MAPE
  - [ ] Compare vs individual models
  - [ ] Assert MAPE < 15%

### Story 3 DoD
- [ ] EnsembleForecaster class complete
- [ ] All 3 integration tests passing
- [ ] Ensemble MAPE < 15%
- [ ] Ensemble outperforms individual models

---

## Story 4: Demand Agent Integration (6 hours)

**File:** `stories/PHASE6-004-integration-testing.md`
**Goal:** Integrate ensemble with Phase 5 orchestrator

### Tasks
- [ ] Task 1: Create DemandAgent skeleton (45 min)
  - [ ] Create `backend/app/agents/demand_agent.py`
  - [ ] Define class structure

- [ ] Task 2: Implement execute() method (1.5 hours)
  - [ ] Extract context parameters
  - [ ] Train and forecast using ensemble
  - [ ] Calculate total_demand and safety_stock
  - [ ] Format output

- [ ] Task 3: Add WebSocket progress messages (1 hour)
  - [ ] Send agent_status messages
  - [ ] Send progress updates
  - [ ] Send complete message

- [ ] Task 4: Register agent with orchestrator (30 min)
  - [ ] Update agent registry
  - [ ] Remove mock agent

- [ ] Task 5: Write end-to-end integration tests (1.5 hours)
  - [ ] Test demand agent with context
  - [ ] Test with orchestrator workflow
  - [ ] Test error handling

- [ ] Task 6: Performance optimization (45 min)
  - [ ] Profile code
  - [ ] Optimize bottlenecks
  - [ ] Verify <10 second target

- [ ] Task 7: Frontend verification (30 min)
  - [ ] Test in browser
  - [ ] Verify forecast data displays
  - [ ] Verify WebSocket updates

### Story 4 DoD
- [ ] DemandAgent class complete
- [ ] All integration tests passing
- [ ] Forecast generation <10 seconds
- [ ] End-to-end workflow <15 seconds
- [ ] Frontend displays real forecast data

---

## Phase 6 Completion Checklist

### Code Quality
- [ ] All type hints present
- [ ] All docstrings complete (Google style)
- [ ] No console.log or print statements (use logging)
- [ ] Error handling comprehensive
- [ ] Code follows project style guide

### Testing
- [ ] All unit tests passing (15 tests total)
- [ ] All integration tests passing (6 tests total)
- [ ] Test coverage >85% for ML wrappers
- [ ] Test coverage >90% for DemandAgent
- [ ] Performance tests passing

### Accuracy Validation
- [ ] Prophet MAPE documented
- [ ] ARIMA MAPE documented
- [ ] Ensemble MAPE < 15% ✅
- [ ] Ensemble outperforms individual models ✅

### Integration
- [ ] Agent registered with orchestrator
- [ ] WebSocket messages working
- [ ] Output matches DemandAgentOutput contract
- [ ] Phase 5 orchestrator unchanged (no breaking changes)
- [ ] Frontend displays forecast data

### Documentation
- [ ] All docstrings complete
- [ ] MAPE results documented
- [ ] Hyperparameter choices documented
- [ ] Performance optimization documented
- [ ] Ready for Phase 7 handoff

---

## Phase 6 Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Prophet MAPE | < 20% | TBD | ⏳ |
| ARIMA MAPE | < 20% | TBD | ⏳ |
| Ensemble MAPE | < 15% | TBD | ⏳ |
| Forecast Time | < 10s | TBD | ⏳ |
| Workflow Time | < 15s | TBD | ⏳ |
| Test Coverage | > 85% | TBD | ⏳ |
| Unit Tests | 15 passing | 0/15 | ⏳ |
| Integration Tests | 6 passing | 0/6 | ⏳ |

---

## Known Issues / Blockers

- None currently identified

---

## Phase 7 Handoff Readiness

- [ ] forecast_result output contract verified
- [ ] Output validated against DemandAgentOutput schema
- [ ] Sample forecast_result documented for Phase 7 reference
- [ ] No changes required to Phase 6 code for Phase 7

---

## Notes

**Estimated Timeline:**
- Story 1: 8 hours (Day 1)
- Story 2: 6 hours (Day 2 morning)
- Story 3: 8 hours (Day 2 afternoon + Day 3 morning)
- Story 4: 6 hours (Day 3 afternoon)
- **Total:** 28 hours (3.5 days)

**Dependencies:**
- Prophet and pmdarima libraries must install successfully
- Historical sales data must have 52+ weeks
- Phase 5 orchestrator must be fully functional

**Critical Path:**
- Story 1 → Story 2 → Story 3 → Story 4 (sequential)
- Cannot parallelize stories in Phase 6

---

**Last Updated:** 2025-11-11
**Version:** 1.0
