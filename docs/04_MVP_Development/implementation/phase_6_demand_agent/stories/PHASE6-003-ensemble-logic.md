# Story: Implement Ensemble Forecaster (Prophet + ARIMA)

**Epic:** Phase 6 - Demand Agent
**Story ID:** PHASE6-003
**Status:** Ready for Implementation
**Estimate:** 8 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE6-001, PHASE6-002 complete

**Planning References:**
- PRD v3.3: Section 5.3 (Ensemble Forecasting Strategy)
- Technical Architecture v3.3: Section 4.5 (ML Pipeline - Ensemble Logic)
- technical_decisions.md: TD-6.1 (Ensemble Approach), TD-6.6 (Fallback Strategy)

---

## Story

As a backend developer,
I want to combine Prophet and ARIMA forecasts using weighted averaging,
So that the system produces more accurate forecasts than either model alone (target MAPE < 15%).

**Business Value:** Ensemble forecasting is an industry best practice that reduces model-specific bias and improves robustness. By combining Prophet's seasonality strength with ARIMA's trend capture, we achieve 3-5% MAPE improvement over single models. This directly impacts inventory optimization and reduces stockouts/overstocks.

**Epic Context:** This is Story 3 of 4 in Phase 6. This story combines the work from Story 1 (Prophet) and Story 2 (ARIMA) into a production-ready forecasting system. Story 4 integrates this ensemble with the Phase 5 orchestrator to create the full Demand Agent.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ EnsembleForecaster class created in `backend/app/ml/ensemble_forecaster.py`
2. ✅ EnsembleForecaster combines ProphetWrapper and ARIMAWrapper
3. ✅ Default weights: 60% Prophet, 40% ARIMA
4. ✅ Dynamic weight calculation based on validation MAPE
5. ✅ Weighted average formula: `ensemble = w1*prophet + w2*arima`
6. ✅ Ensemble confidence: minimum of both model confidences
7. ✅ Fallback to Prophet-only if ARIMA fails
8. ✅ Fallback to ARIMA-only if Prophet fails
9. ✅ Raise ForecastingError if both models fail
10. ✅ Return model_used field ("prophet_arima_ensemble" | "prophet" | "arima")

### Quality Requirements

11. ✅ MAPE < 15% on 10-week validation set
12. ✅ Ensemble MAPE better than both individual models
13. ✅ Ensemble generation completes in <10 seconds total
14. ✅ All docstrings complete
15. ✅ 3 integration tests written and passing
16. ✅ Type hints on all methods
17. ✅ Logs which model(s) used for transparency

---

## Prerequisites

**Previous Stories Complete:**
- [x] PHASE6-001 (Prophet Integration) complete
- [x] PHASE6-002 (ARIMA Integration) complete
- [x] ProphetWrapper available and tested
- [x] ARIMAWrapper available and tested

**Validation Data:**
- [x] Historical sales data split: 52 weeks train + 10 weeks validation
- [x] Validation set used to calculate dynamic weights

---

## Tasks

### Task 1: Create EnsembleForecaster Class Skeleton

**Goal:** Define ensemble class structure

**Subtasks:**
- [ ] Create file: `backend/app/ml/ensemble_forecaster.py`
- [ ] Define `EnsembleForecaster` class
- [ ] Add `__init__(self, prophet_wrapper, arima_wrapper, weights=None)` method
- [ ] Add `train(self, historical_data: pd.DataFrame) -> None` method stub
- [ ] Add `forecast(self, periods: int) -> dict` method stub
- [ ] Add `_calculate_dynamic_weights(self, validation_data) -> tuple` method stub
- [ ] Add `_weighted_average(self, prophet_pred, arima_pred, weights) -> list` method stub
- [ ] Add type hints and docstrings

**Code Template:**
```python
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
import logging
from backend.app.ml.prophet_wrapper import ProphetWrapper
from backend.app.ml.arima_wrapper import ARIMAWrapper

logger = logging.getLogger(__name__)

class EnsembleForecaster:
    """Ensemble forecaster combining Prophet and ARIMA with weighted averaging.

    Attributes:
        prophet: ProphetWrapper instance
        arima: ARIMAWrapper instance
        weights: Tuple of (prophet_weight, arima_weight)
        model_used: String indicating which models were used
    """

    def __init__(
        self,
        prophet_wrapper: ProphetWrapper = None,
        arima_wrapper: ARIMAWrapper = None,
        weights: Optional[Tuple[float, float]] = None
    ):
        """Initialize EnsembleForecaster with model wrappers."""
        self.prophet = prophet_wrapper or ProphetWrapper()
        self.arima = arima_wrapper or ARIMAWrapper()
        self.weights = weights or (0.6, 0.4)  # Default: 60% Prophet, 40% ARIMA
        self.model_used = "prophet_arima_ensemble"

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train both Prophet and ARIMA models."""
        pass

    def forecast(self, periods: int) -> Dict:
        """Generate ensemble forecast."""
        pass

    def _calculate_dynamic_weights(
        self,
        validation_data: pd.DataFrame
    ) -> Tuple[float, float]:
        """Calculate optimal weights based on validation MAPE."""
        pass

    def _weighted_average(
        self,
        prophet_pred: list,
        arima_pred: list,
        weights: Tuple[float, float]
    ) -> list:
        """Compute weighted average of two forecasts."""
        pass
```

---

### Task 2: Implement train() Method

**Goal:** Train both models with fallback handling

**Subtasks:**
- [ ] Try to train Prophet model
  ```python
  try:
      self.prophet.train(historical_data)
      logger.info("Prophet trained successfully")
  except Exception as e:
      logger.warning(f"Prophet training failed: {e}")
      self.prophet = None
  ```
- [ ] Try to train ARIMA model
  ```python
  try:
      self.arima.train(historical_data)
      logger.info("ARIMA trained successfully")
  except Exception as e:
      logger.warning(f"ARIMA training failed: {e}")
      self.arima = None
  ```
- [ ] Check if at least one model trained
- [ ] Raise ForecastingError if both failed
- [ ] Update self.model_used based on which models succeeded
- [ ] Log final model status

**Acceptance:**
- Both models train successfully (happy path)
- Fallback works if one model fails
- Error raised if both fail

---

### Task 3: Implement _weighted_average() Helper

**Goal:** Combine two forecasts using weights

**Subtasks:**
- [ ] Convert lists to numpy arrays
- [ ] Validate inputs (same length, non-negative)
- [ ] Calculate weighted average:
  ```python
  ensemble = w1 * np.array(prophet_pred) + w2 * np.array(arima_pred)
  ```
- [ ] Round to integers (unit quantities)
- [ ] Return as list

**Acceptance:**
- Weighted average calculated correctly
- Output length matches input length
- All values are positive integers

---

### Task 4: Implement _calculate_dynamic_weights() Method

**Goal:** Calculate optimal weights based on validation accuracy

**Subtasks:**
- [ ] Split validation_data: use first part for validation, last 10 weeks for testing
- [ ] Generate Prophet forecast on validation set
- [ ] Generate ARIMA forecast on validation set
- [ ] Calculate MAPE for Prophet: `mape_prophet = calculate_mape(actual, prophet_pred)`
- [ ] Calculate MAPE for ARIMA: `mape_arima = calculate_mape(actual, arima_pred)`
- [ ] Calculate inverse weights:
  ```python
  total_inv_mape = (1/mape_prophet) + (1/mape_arima)
  w_prophet = (1/mape_prophet) / total_inv_mape
  w_arima = (1/mape_arima) / total_inv_mape
  ```
- [ ] Return (w_prophet, w_arima)
- [ ] Log calculated weights

**Acceptance:**
- Weights sum to 1.0
- Lower MAPE model gets higher weight
- Weights are reasonable (both between 0.3 and 0.7)

---

### Task 5: Implement forecast() Method with Fallback Logic

**Goal:** Generate ensemble forecast with robustness

**Subtasks:**
- [ ] Try to generate Prophet forecast
  ```python
  prophet_forecast = None
  if self.prophet:
      try:
          prophet_forecast = self.prophet.forecast(periods)
      except Exception as e:
          logger.warning(f"Prophet forecast failed: {e}")
  ```
- [ ] Try to generate ARIMA forecast
  ```python
  arima_forecast = None
  if self.arima:
      try:
          arima_forecast = self.arima.forecast(periods)
      except Exception as e:
          logger.warning(f"ARIMA forecast failed: {e}")
  ```
- [ ] Implement fallback logic:
  ```python
  if prophet_forecast and arima_forecast:
      # Ensemble
      predictions = self._weighted_average(
          prophet_forecast['predictions'],
          arima_forecast['predictions'],
          self.weights
      )
      confidence = min(
          self.prophet.get_confidence(prophet_forecast),
          self.arima.get_confidence(arima_forecast)
      )
      self.model_used = "prophet_arima_ensemble"
  elif prophet_forecast:
      # Prophet only
      predictions = prophet_forecast['predictions']
      confidence = self.prophet.get_confidence(prophet_forecast)
      self.model_used = "prophet"
      logger.info("Using Prophet only (ARIMA unavailable)")
  elif arima_forecast:
      # ARIMA only
      predictions = arima_forecast['predictions']
      confidence = self.arima.get_confidence(arima_forecast)
      self.model_used = "arima"
      logger.info("Using ARIMA only (Prophet unavailable)")
  else:
      raise ForecastingError("Both Prophet and ARIMA failed")
  ```
- [ ] Return forecast dictionary:
  ```python
  return {
      "predictions": predictions,
      "confidence": confidence,
      "model_used": self.model_used
  }
  ```

**Acceptance:**
- Ensemble works when both models available
- Falls back to single model correctly
- Raises error when both unavailable
- Logs fallback decisions

---

### Task 6: Write Integration Tests

**Goal:** Verify ensemble behavior in all scenarios

**Subtasks:**
- [ ] Create file: `backend/tests/integration/test_ensemble_forecaster.py`
- [ ] **Test 1:** `test_ensemble_with_both_models()`
  - Train both models
  - Generate ensemble forecast
  - Assert model_used == "prophet_arima_ensemble"
  - Assert predictions length correct
  - Assert confidence in [0.0, 1.0]
- [ ] **Test 2:** `test_ensemble_fallback_to_prophet_only()`
  - Intentionally break ARIMA (pass None)
  - Generate forecast
  - Assert model_used == "prophet"
  - Assert forecast still generated
- [ ] **Test 3:** `test_ensemble_fallback_to_arima_only()`
  - Intentionally break Prophet (pass None)
  - Generate forecast
  - Assert model_used == "arima"
  - Assert forecast still generated

**Acceptance:**
- All 3 tests pass
- Coverage >90% for EnsembleForecaster

---

### Task 7: Validation Testing (MAPE < 15%)

**Goal:** Verify ensemble achieves target accuracy

**Subtasks:**
- [ ] Load 62 weeks of historical data
- [ ] Split: 52 weeks train, 10 weeks validation
- [ ] Train ensemble on 52 weeks
- [ ] Forecast next 10 weeks
- [ ] Calculate ensemble MAPE
- [ ] Calculate Prophet-only MAPE (for comparison)
- [ ] Calculate ARIMA-only MAPE (for comparison)
- [ ] Document all three MAPE values
- [ ] Assert ensemble MAPE < 15%
- [ ] Assert ensemble MAPE < min(Prophet MAPE, ARIMA MAPE)

**Acceptance:**
- Ensemble MAPE < 15%
- Ensemble outperforms individual models
- Results documented in test output

---

## Testing Strategy

### Integration Tests
- Test ensemble with both models
- Test fallback scenarios (Prophet-only, ARIMA-only)
- Test error handling (both models fail)

### Validation Tests
- Compare ensemble vs individual model accuracy
- Verify MAPE < 15% target
- Test on multiple datasets (high demand, low demand)

### Performance Tests
- End-to-end forecast generation < 10 seconds
- Includes training both models + ensemble logic

---

## Definition of Done

**Code Complete:**
- [ ] EnsembleForecaster class implemented
- [ ] Weighted averaging logic working
- [ ] Dynamic weight calculation implemented
- [ ] Fallback logic complete
- [ ] Type hints and docstrings complete

**Testing Complete:**
- [ ] 3 integration tests passing
- [ ] Ensemble MAPE < 15% on validation set
- [ ] Ensemble outperforms individual models
- [ ] Test coverage >90%

**Quality Checks:**
- [ ] Error handling complete
- [ ] Logging informative (which models used)
- [ ] Performance <10 seconds

**Documentation:**
- [ ] MAPE comparison documented
- [ ] Weight calculations documented
- [ ] Fallback behavior documented

**Ready for Next Story:**
- [ ] EnsembleForecaster ready for DemandAgent (Story 4)
- [ ] All model outputs match expected contract

---

## Notes

**Weight Tuning:**
Default 60/40 (Prophet/ARIMA) works well for most retail data. Dynamic weighting provides 1-2% additional MAPE improvement but adds complexity. For MVP, default weights are acceptable.

**Confidence Calculation:**
Using minimum confidence (most conservative) ensures we don't overstate forecast reliability. Alternative: weighted average of confidences.

**Ensemble Benefits:**
- Reduces overfitting (individual model biases cancel out)
- More robust to data anomalies
- Industry standard for production forecasting

**Expected MAPE Breakdown:**
- Prophet alone: ~18% MAPE
- ARIMA alone: ~17% MAPE
- Ensemble: ~13-14% MAPE (target < 15%)

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
