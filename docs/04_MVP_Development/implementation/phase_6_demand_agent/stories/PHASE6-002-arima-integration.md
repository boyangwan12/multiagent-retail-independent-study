# Story: Integrate ARIMA for Trend Forecasting

**Epic:** Phase 6 - Demand Agent
**Story ID:** PHASE6-002
**Status:** Ready for Implementation
**Estimate:** 6 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE6-001 complete

**Planning References:**
- PRD v3.3: Section 5.2 (Demand Forecasting - ARIMA Model)
- Technical Architecture v3.3: Section 4.5 (ML Pipeline - ARIMA Integration)
- technical_decisions.md: TD-6.3 (ARIMA Parameter Selection)

---

## Story

As a backend developer,
I want to integrate ARIMA with Auto parameter selection for trend-based forecasting,
So that the system can capture non-seasonal patterns and complement Prophet's seasonality forecasts.

**Business Value:** ARIMA (AutoRegressive Integrated Moving Average) excels at capturing trend and autocorrelation patterns that Prophet may miss. Combined with Prophet in an ensemble (Story 3), this improves overall forecasting accuracy by 3-5% MAPE. ARIMA provides the "trend component" of the ensemble.

**Epic Context:** This is Story 2 of 4 in Phase 6. ARIMA handles trend patterns while Prophet (Story 1) handles seasonality. Story 3 combines both models. This story is critical for achieving target MAPE < 15%.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ ARIMAWrapper class created in `backend/app/ml/arima_wrapper.py`
2. ✅ pmdarima library installed for Auto ARIMA
3. ✅ ARIMAWrapper.train() uses auto_arima for parameter selection (p, d, q)
4. ✅ Auto ARIMA configured with stepwise=True for fast convergence
5. ✅ Auto ARIMA configured with seasonal=False (Prophet handles seasonality)
6. ✅ ARIMAWrapper.forecast() generates weekly predictions
7. ✅ Forecast output includes predictions and confidence intervals
8. ✅ Handles non-stationary data (auto differencing with d parameter)
9. ✅ Training completes in <8 seconds (includes auto parameter search)
10. ✅ Prediction completes in <1 second

### Quality Requirements

11. ✅ MAPE < 20% on 10-week validation set
12. ✅ Auto ARIMA selects reasonable parameters (p, q < 5)
13. ✅ Fallback to ARIMA(1,1,1) if auto_arima fails
14. ✅ Raises InsufficientDataError if data < 26 weeks
15. ✅ Raises ModelTrainingError if ARIMA training fails
16. ✅ All docstrings complete (Google style)
17. ✅ 5 unit tests written and passing
18. ✅ Type hints on all methods

---

## Prerequisites

**Story 1 Complete:**
- [x] PHASE6-001 (Prophet Integration) complete
- [x] ProphetWrapper class available for comparison

**Python Libraries:**
- [ ] pmdarima library installed (`uv add pmdarima`)
- [ ] statsmodels library installed (dependency of pmdarima)
- [ ] Test import: `python -c "from pmdarima import auto_arima; print('OK')"`

**Data Validation:**
- [x] Historical sales data available (52+ weeks)
- [x] Data preprocessed (weekly aggregation, outlier clipping)

---

## Tasks

### Task 1: Install pmdarima Library

**Goal:** Add pmdarima for Auto ARIMA functionality

**Subtasks:**
- [ ] Run `uv add pmdarima` in backend directory
- [ ] Verify installation: `uv pip list | grep pmdarima`
- [ ] Test import: `from pmdarima import auto_arima`
- [ ] Document any installation issues

**Acceptance:**
- pmdarima successfully imported
- Version >= 2.0.0

---

### Task 2: Create ARIMAWrapper Class Skeleton

**Goal:** Define class structure

**Subtasks:**
- [ ] Create file: `backend/app/ml/arima_wrapper.py`
- [ ] Define `ARIMAWrapper` class
- [ ] Add `__init__(self, config: dict = None)` method
- [ ] Add `train(self, historical_data: pd.DataFrame) -> None` method stub
- [ ] Add `forecast(self, periods: int) -> dict` method stub
- [ ] Add `get_confidence(self, forecast_result) -> float` method stub
- [ ] Add type hints and docstrings

**Code Template:**
```python
from pmdarima import auto_arima
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ARIMAWrapper:
    """Wrapper for ARIMA time series forecasting with Auto parameter selection.

    Attributes:
        model: Trained ARIMA model instance
        config: Configuration dict for hyperparameters
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize ARIMAWrapper."""
        self.model = None
        self.config = config or {}
        self.selected_order = None

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train ARIMA model using Auto ARIMA for parameter selection."""
        pass

    def forecast(self, periods: int) -> Dict:
        """Generate forecast for specified number of periods."""
        pass

    def get_confidence(self, forecast_result) -> float:
        """Calculate confidence score from prediction intervals."""
        pass
```

---

### Task 3: Implement train() Method with Auto ARIMA

**Goal:** Train ARIMA model with automatic parameter selection

**Subtasks:**
- [ ] Validate input data (min 26 weeks)
- [ ] Extract time series values: `y = historical_data['quantity_sold'].values`
- [ ] Configure auto_arima parameters:
  ```python
  model = auto_arima(
      y=y,
      start_p=0, max_p=5,
      start_q=0, max_q=5,
      d=None,  # Auto-detect differencing
      seasonal=False,
      stepwise=True,
      suppress_warnings=True,
      error_action='ignore',
      trace=False
  )
  ```
- [ ] Store trained model and selected (p, d, q) parameters
- [ ] Log selected parameters: `logger.info(f"Selected ARIMA order: {model.order}")`
- [ ] Implement fallback to ARIMA(1,1,1) if auto_arima fails
- [ ] Raise errors for invalid input

**Acceptance:**
- Model trains successfully on 52 weeks data
- Training completes in <8 seconds
- Selected (p, d, q) parameters logged

---

### Task 4: Implement forecast() Method

**Goal:** Generate weekly forecasts

**Subtasks:**
- [ ] Check if model is trained
- [ ] Generate forecast: `forecast, conf_int = model.predict(n_periods=periods, return_conf_int=True)`
- [ ] Round predictions to integers
- [ ] Return dictionary:
  ```python
  {
      "predictions": forecast.tolist(),
      "lower_bound": conf_int[:, 0].tolist(),
      "upper_bound": conf_int[:, 1].tolist()
  }
  ```
- [ ] Log forecast generation

**Acceptance:**
- Forecast returns predictions with confidence intervals
- Predictions are positive integers
- Forecast length matches `periods` parameter

---

### Task 5: Implement get_confidence() Method

**Goal:** Calculate confidence from ARIMA intervals

**Subtasks:**
- [ ] Extract predictions, lower_bound, upper_bound
- [ ] Calculate interval widths
- [ ] Calculate confidence score (same formula as Prophet)
- [ ] Return confidence between 0.0 and 1.0

**Acceptance:**
- Confidence score in range [0.0, 1.0]
- Narrow intervals → Higher confidence

---

### Task 6: Write Unit Tests

**Goal:** Verify ARIMAWrapper functionality

**Subtasks:**
- [ ] Create file: `backend/tests/unit/ml/test_arima_wrapper.py`
- [ ] **Test 1:** `test_arima_auto_parameter_selection()`
  - Train model, check selected (p, d, q) are reasonable
- [ ] **Test 2:** `test_arima_train_with_valid_data()`
  - Train successfully with 52 weeks
- [ ] **Test 3:** `test_arima_forecast_returns_correct_shape()`
  - Forecast 12 weeks, assert 12 predictions
- [ ] **Test 4:** `test_arima_handles_non_stationary_data()`
  - Test with trending data, verify differencing applied
- [ ] **Test 5:** `test_arima_raises_error_on_insufficient_data()`
  - Test with <26 weeks, assert error raised

**Acceptance:**
- All 5 tests pass
- Test coverage >90%

---

### Task 7: Validation Testing

**Goal:** Verify forecasting accuracy

**Subtasks:**
- [ ] Split data into train (52 weeks) and validation (10 weeks)
- [ ] Train ARIMA on 52 weeks
- [ ] Forecast next 10 weeks
- [ ] Calculate MAPE on validation set
- [ ] Document MAPE result
- [ ] Assert MAPE < 20%

**Acceptance:**
- MAPE < 20% on validation set
- Performance comparable to Prophet

---

## Testing Strategy

- **Unit Tests:** ARIMAWrapper class methods
- **Integration Tests:** Deferred to Story 4 (with DemandAgent)
- **Performance Tests:** Training <8s, forecasting <1s

---

## Definition of Done

**Code Complete:**
- [ ] ARIMAWrapper class implemented
- [ ] Auto ARIMA parameter selection working
- [ ] Fallback to ARIMA(1,1,1) implemented
- [ ] Type hints and docstrings complete

**Testing Complete:**
- [ ] 5 unit tests passing
- [ ] Validation MAPE < 20%
- [ ] Test coverage >90%

**Quality Checks:**
- [ ] Error handling complete
- [ ] Performance targets met
- [ ] No print statements (use logging)

**Documentation:**
- [ ] Selected (p, d, q) parameters documented
- [ ] MAPE results documented

**Ready for Next Story:**
- [ ] ARIMAWrapper ready for ensemble (Story 3)
- [ ] Can be compared against Prophet accuracy

---

## Notes

**Auto ARIMA Performance:**
- Stepwise search is faster than exhaustive
- Typical runtime: 5-8 seconds on 52 weeks
- Selected parameters usually: p=1-3, d=1, q=1-2

**Stationarity:**
- ARIMA requires stationary data (constant mean/variance)
- Auto ARIMA automatically applies differencing (d parameter)
- Check ADF test if stationarity concerns arise

**Confidence Intervals:**
- ARIMA confidence intervals based on residual variance
- Typically wider than Prophet intervals
- Indicates higher uncertainty in trend forecasts

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
