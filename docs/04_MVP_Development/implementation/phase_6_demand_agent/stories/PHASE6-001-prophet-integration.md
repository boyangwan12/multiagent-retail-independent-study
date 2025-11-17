# Story: Integrate Prophet for Time Series Forecasting

**Epic:** Phase 6 - Demand Agent
**Story ID:** PHASE6-001
**Status:** Ready for Review
**Estimate:** 8 hours
**Agent:** `*agent dev`
**Dependencies:** Phase 5 Orchestrator Foundation complete

**Planning References:**
- PRD v3.3: Section 5.1 (Demand Forecasting - Prophet Model)
- Technical Architecture v3.3: Section 4.5 (ML Pipeline - Prophet Integration)
- Product Brief v3.3: Section 2.2 (Forecasting Accuracy Requirements)
- technical_decisions.md: TD-6.2 (Prophet Hyperparameters)

---

## Story

As a backend developer,
I want to integrate Facebook Prophet for time series forecasting on historical sales data,
So that the system can generate accurate weekly demand forecasts with confidence intervals.

**Business Value:** Prophet is a proven time series forecasting library used by Meta/Facebook for production forecasting. It excels at capturing seasonality patterns (weekly, yearly) which are critical for retail demand prediction. This story delivers 60% of the ensemble forecasting capability and establishes the foundation for accurate demand prediction (target MAPE < 15%).

**Epic Context:** This is Story 1 of 4 in Phase 6 (Demand Agent). Prophet handles the seasonality component of the ensemble, while Story 2 (ARIMA) handles trend patterns. Story 3 combines both models into an ensemble. This story enables the core AI forecasting that differentiates this system from rule-based inventory systems.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ ProphetWrapper class created in `backend/app/ml/prophet_wrapper.py`
2. ✅ ProphetWrapper.train() method accepts historical sales DataFrame (52+ weeks)
3. ✅ Prophet configured with multiplicative seasonality
4. ✅ Prophet configured with weekly_seasonality=True, yearly_seasonality=True
5. ✅ Prophet configured with changepoint_prior_scale=0.05 (conservative)
6. ✅ Prophet configured with seasonality_prior_scale=10.0 (strong seasonality)
7. ✅ ProphetWrapper.forecast() method generates weekly predictions
8. ✅ Forecast output includes: predicted values, upper bound, lower bound
9. ✅ Forecast length matches forecast_horizon_weeks parameter
10. ✅ Confidence score calculated from prediction intervals

### Quality Requirements

11. ✅ MAPE < 20% on 10-week validation set
12. ✅ Training completes in <5 seconds (52 weeks historical data)
13. ✅ Prediction completes in <1 second
14. ✅ Handles missing data gracefully (forward fill or raise InsufficientDataError)
15. ✅ Raises ModelTrainingError if Prophet training fails
16. ✅ All docstrings complete (Google style)
17. ✅ 5 unit tests written and passing
18. ✅ Type hints on all methods

---

## Prerequisites

Before implementing this story, ensure the following are ready:

**Phase 5 Complete:**
- [x] Phase 5 orchestrator foundation complete
- [x] DemandAgentContext schema defined
- [x] ContextAssembler can load historical sales data
- [x] Historical sales data available in database (52+ weeks)

**Python Libraries:**
- [ ] prophet library installed (`uv add prophet`)
- [ ] scikit-learn installed for MAPE calculation (`uv add scikit-learn`)
- [ ] numpy installed for array operations (`uv add numpy`)
- [ ] Test prophet import: `python -c "from prophet import Prophet; print('OK')"`

**Data Validation:**
- [ ] Historical sales data has at least 52 weeks (1 year minimum)
- [ ] Data format: DataFrame with columns ['date', 'quantity_sold']
- [ ] No extreme outliers (checked with data profiling)

**Why This Matters:**
Prophet requires at least 2 seasonal cycles (24 weeks minimum) to fit seasonality. With 52 weeks, we have 1 year of weekly data which enables both weekly and yearly seasonality detection.

---

## Tasks

### Task 1: Install Prophet Library

**Goal:** Add prophet to project dependencies

**Subtasks:**
- [x] Run `uv add prophet` in backend directory
- [x] Verify installation: `uv pip list | grep prophet`
- [x] Test import in Python: `from prophet import Prophet`
- [x] Document any installation issues in technical_decisions.md

**Acceptance:**
- Prophet library successfully imported without errors
- Prophet version >= 1.1.5

---

### Task 2: Create ProphetWrapper Class Skeleton

**Goal:** Define class structure and method signatures

**Subtasks:**
- [x] Create file: `backend/app/ml/prophet_wrapper.py`
- [x] Define `ProphetWrapper` class
- [x] Add `__init__(self, config: dict = None)` method
- [x] Add `train(self, historical_data: pd.DataFrame) -> None` method stub
- [x] Add `forecast(self, periods: int) -> dict` method stub
- [x] Add `get_confidence(self, forecast_df: pd.DataFrame) -> float` method stub
- [x] Add type hints to all methods
- [x] Add docstrings (Google style) to all methods

**Acceptance:**
- Class structure matches interface design
- All methods have docstrings
- Type hints present on all parameters and returns

**Code Template:**
```python
from prophet import Prophet
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ProphetWrapper:
    """Wrapper for Facebook Prophet time series forecasting.

    Attributes:
        model: Trained Prophet model instance
        config: Configuration dict for hyperparameters
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize ProphetWrapper with optional configuration."""
        pass

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train Prophet model on historical sales data."""
        pass

    def forecast(self, periods: int) -> Dict:
        """Generate forecast for specified number of periods."""
        pass

    def get_confidence(self, forecast_df: pd.DataFrame) -> float:
        """Calculate confidence score from prediction intervals."""
        pass
```

---

### Task 3: Implement train() Method

**Goal:** Train Prophet model on historical sales data

**Subtasks:**
- [x] Validate input data (check for required columns, min 26 weeks)
- [x] Preprocess data for Prophet (rename columns to 'ds' and 'y')
- [x] Handle missing values (forward fill)
- [x] Instantiate Prophet with configured hyperparameters:
  ```python
  model = Prophet(
      seasonality_mode='multiplicative',
      yearly_seasonality=True,
      weekly_seasonality=True,
      daily_seasonality=False,
      changepoint_prior_scale=0.05,
      seasonality_prior_scale=10.0
  )
  ```
- [x] Call `model.fit(df)` to train
- [x] Store trained model in `self.model`
- [x] Log training completion with metrics (data size, duration)
- [x] Raise `InsufficientDataError` if data < 26 weeks
- [x] Raise `ModelTrainingError` if fit() fails

**Acceptance:**
- Model successfully trains on 52 weeks of test data
- Training completes in <5 seconds
- Errors raised for invalid input

---

### Task 4: Implement forecast() Method

**Goal:** Generate weekly forecasts using trained model

**Subtasks:**
- [x] Check if model is trained (raise error if not)
- [x] Create future DataFrame with `model.make_future_dataframe(periods=periods, freq='W')`
- [x] Generate predictions: `forecast = model.predict(future)`
- [x] Extract relevant columns: yhat (prediction), yhat_lower, yhat_upper
- [x] Convert to dictionary format:
  ```python
  {
      "predictions": forecast['yhat'].tail(periods).tolist(),
      "lower_bound": forecast['yhat_lower'].tail(periods).tolist(),
      "upper_bound": forecast['yhat_upper'].tail(periods).tolist(),
      "dates": forecast['ds'].tail(periods).tolist()
  }
  ```
- [x] Round predictions to integers (unit quantities)
- [x] Log forecast generation completion

**Acceptance:**
- Forecast returns dict with predictions, bounds, and dates
- Forecast length matches `periods` parameter
- Predictions are positive integers

---

### Task 5: Implement get_confidence() Method

**Goal:** Calculate confidence score from prediction intervals

**Subtasks:**
- [x] Extract yhat, yhat_lower, yhat_upper from forecast DataFrame
- [x] Calculate interval width: `width = yhat_upper - yhat_lower`
- [x] Calculate average interval width: `avg_width = width.mean()`
- [x] Calculate average prediction: `avg_pred = yhat.mean()`
- [x] Calculate confidence score: `confidence = 1.0 - (avg_width / avg_pred)`
- [x] Clip confidence to [0.0, 1.0] range
- [x] Return confidence score

**Acceptance:**
- Confidence score is float between 0.0 and 1.0
- Narrow intervals → Higher confidence
- Wide intervals → Lower confidence

**Formula:**
```python
confidence = 1.0 - (
    (forecast['yhat_upper'] - forecast['yhat_lower']).mean() /
    forecast['yhat'].mean()
)
confidence = max(0.0, min(1.0, confidence))
```

---

### Task 6: Write Unit Tests

**Goal:** Ensure ProphetWrapper works correctly

**Subtasks:**
- [x] Create file: `backend/tests/unit/ml/test_prophet_wrapper.py`
- [x] Write test fixture with sample historical data (52 weeks)
- [x] **Test 1:** `test_prophet_train_with_valid_data()`
  - Train model with 52 weeks of data
  - Assert model is not None
  - Assert no errors raised
- [x] **Test 2:** `test_prophet_forecast_returns_correct_shape()`
  - Train model, forecast 12 weeks
  - Assert predictions list has 12 items
  - Assert all predictions are positive integers
- [x] **Test 3:** `test_prophet_confidence_score_in_range()`
  - Train model, forecast, calculate confidence
  - Assert 0.0 <= confidence <= 1.0
- [x] **Test 4:** `test_prophet_raises_error_on_insufficient_data()`
  - Try to train with only 20 weeks of data
  - Assert InsufficientDataError is raised
- [x] **Test 5:** `test_prophet_forecast_without_training_raises_error()`
  - Create wrapper without training
  - Try to call forecast()
  - Assert error is raised

**Acceptance:**
- All 5 tests pass
- Test coverage >90% for ProphetWrapper class
- Tests run in <30 seconds

---

### Task 7: Validation Testing

**Goal:** Verify forecasting accuracy on validation set

**Subtasks:**
- [x] Load historical sales data (62 weeks total)
- [x] Split into train (52 weeks) and validation (10 weeks)
- [x] Train Prophet on 52 weeks
- [x] Forecast next 10 weeks
- [x] Calculate MAPE on validation set:
  ```python
  from sklearn.metrics import mean_absolute_percentage_error
  mape = mean_absolute_percentage_error(actual, predicted) * 100
  ```
- [x] Document MAPE result in test output
- [x] Assert MAPE < 20% (target for single model)

**Acceptance:**
- MAPE < 20% on validation set
- Validation test passes consistently

---

## Testing Strategy

### Unit Tests (ProphetWrapper Class)
- Test model training with valid data
- Test forecasting with trained model
- Test confidence calculation
- Test error handling (insufficient data, untrained model)
- Test edge cases (exact 26 weeks data, large forecast horizon)

### Integration Tests (Deferred to Story 4)
- Integration with DemandAgent
- Integration with Phase 5 orchestrator
- End-to-end workflow test

### Performance Tests
- Training time: <5 seconds (52 weeks data)
- Forecasting time: <1 second (12 periods)
- Memory usage: <500MB

---

## Definition of Done

**Code Complete:**
- [x] ProphetWrapper class implemented with all methods
- [x] Prophet configured with correct hyperparameters
- [x] train() method trains model successfully
- [x] forecast() method generates weekly predictions
- [x] get_confidence() method calculates confidence score
- [x] All type hints present
- [x] All docstrings complete (Google style)

**Testing Complete:**
- [x] 5 unit tests written and passing (16 unit tests total)
- [x] Validation test shows MAPE < 20% (achieved 12.71%)
- [x] Test coverage >90% for ProphetWrapper
- [x] No flaky tests

**Quality Checks:**
- [x] Code follows project style guide
- [x] No console.log or print statements (use logging)
- [x] Error handling complete (InsufficientDataError, ModelTrainingError)
- [x] Performance targets met (<5s training, <1s forecast)

**Documentation:**
- [x] Docstrings complete for all public methods
- [x] Any hyperparameter tuning decisions documented in technical_decisions.md
- [x] MAPE results documented in test output

**Ready for Next Story:**
- [x] ProphetWrapper can be imported and used
- [x] Ready to integrate with ARIMA in Story 2
- [x] Ready to be called by EnsembleForecaster in Story 3

---

## Dev Agent Record

### Agent Model Used
- Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Implementation Summary
Successfully implemented ProphetWrapper class for time series forecasting with Facebook Prophet. All acceptance criteria met and exceeded expectations.

### Completion Notes
- ✅ ProphetWrapper class created in `backend/app/ml/prophet_wrapper.py`
- ✅ All methods implemented with full type hints and docstrings
- ✅ Prophet configured with multiplicative seasonality (weekly + yearly)
- ✅ Error handling: InsufficientDataError, ModelTrainingError
- ✅ 16 unit tests written (exceeded requirement of 5)
- ✅ 3 validation tests created in separate file
- ✅ **MAPE achieved: 12.71%** (target: <20%) ✨
- ✅ Training time: <2 seconds (target: <5s)
- ✅ Forecasting time: <1 second (target: <1s)
- ✅ All 19 tests passing

### File List
**Created:**
- `backend/app/ml/prophet_wrapper.py` (new implementation)
- `backend/tests/unit/ml/test_prophet_wrapper.py` (16 unit tests)
- `backend/tests/unit/ml/test_prophet_validation.py` (3 validation tests)
- `backend/tests/unit/__init__.py`
- `backend/tests/unit/ml/__init__.py`

**Modified:**
- `backend/pyproject.toml` (added prophet>=1.1.5 dependency)

### Debug Log References
No blocking issues encountered. Implementation was straightforward following the story specification.

### Change Log
- 2025-11-11: Initial implementation complete
- 2025-11-11: Fixed pandas fillna deprecation warning (replaced `.fillna(method='ffill')` with `.ffill()`)
- 2025-11-11: All tests passing, validation MAPE: 12.71%

---

## Notes

**Prophet Installation Issues:**
If Prophet installation fails on Windows, try:
```bash
uv add prophet --no-binary prophet
# OR
conda install -c conda-forge prophet  # If using conda
```

**Data Preprocessing:**
Prophet expects DataFrame with columns 'ds' (date) and 'y' (value). The train() method must rename columns:
```python
df_prophet = historical_data.rename(columns={'date': 'ds', 'quantity_sold': 'y'})
```

**Seasonality Configuration:**
- `weekly_seasonality=True`: Captures weekend vs weekday patterns
- `yearly_seasonality=True`: Captures seasonal trends (spring/summer/fall/winter)
- `multiplicative`: Sales scale with level (holidays are 3x baseline, not +constant)

**Confidence Interpretation:**
- Confidence > 0.8: High confidence, narrow prediction intervals
- Confidence 0.6-0.8: Moderate confidence, reasonable intervals
- Confidence < 0.6: Low confidence, wide intervals (more uncertain forecast)

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
