# Story: Integrate Prophet for Time Series Forecasting

**Epic:** Phase 6 - Demand Agent
**Story ID:** PHASE6-001
**Status:** Ready for Implementation
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
- [ ] Run `uv add prophet` in backend directory
- [ ] Verify installation: `uv pip list | grep prophet`
- [ ] Test import in Python: `from prophet import Prophet`
- [ ] Document any installation issues in technical_decisions.md

**Acceptance:**
- Prophet library successfully imported without errors
- Prophet version >= 1.1.5

---

### Task 2: Create ProphetWrapper Class Skeleton

**Goal:** Define class structure and method signatures

**Subtasks:**
- [ ] Create file: `backend/app/ml/prophet_wrapper.py`
- [ ] Define `ProphetWrapper` class
- [ ] Add `__init__(self, config: dict = None)` method
- [ ] Add `train(self, historical_data: pd.DataFrame) -> None` method stub
- [ ] Add `forecast(self, periods: int) -> dict` method stub
- [ ] Add `get_confidence(self, forecast_df: pd.DataFrame) -> float` method stub
- [ ] Add type hints to all methods
- [ ] Add docstrings (Google style) to all methods

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
- [ ] Validate input data (check for required columns, min 26 weeks)
- [ ] Preprocess data for Prophet (rename columns to 'ds' and 'y')
- [ ] Handle missing values (forward fill)
- [ ] Instantiate Prophet with configured hyperparameters:
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
- [ ] Call `model.fit(df)` to train
- [ ] Store trained model in `self.model`
- [ ] Log training completion with metrics (data size, duration)
- [ ] Raise `InsufficientDataError` if data < 26 weeks
- [ ] Raise `ModelTrainingError` if fit() fails

**Acceptance:**
- Model successfully trains on 52 weeks of test data
- Training completes in <5 seconds
- Errors raised for invalid input

---

### Task 4: Implement forecast() Method

**Goal:** Generate weekly forecasts using trained model

**Subtasks:**
- [ ] Check if model is trained (raise error if not)
- [ ] Create future DataFrame with `model.make_future_dataframe(periods=periods, freq='W')`
- [ ] Generate predictions: `forecast = model.predict(future)`
- [ ] Extract relevant columns: yhat (prediction), yhat_lower, yhat_upper
- [ ] Convert to dictionary format:
  ```python
  {
      "predictions": forecast['yhat'].tail(periods).tolist(),
      "lower_bound": forecast['yhat_lower'].tail(periods).tolist(),
      "upper_bound": forecast['yhat_upper'].tail(periods).tolist(),
      "dates": forecast['ds'].tail(periods).tolist()
  }
  ```
- [ ] Round predictions to integers (unit quantities)
- [ ] Log forecast generation completion

**Acceptance:**
- Forecast returns dict with predictions, bounds, and dates
- Forecast length matches `periods` parameter
- Predictions are positive integers

---

### Task 5: Implement get_confidence() Method

**Goal:** Calculate confidence score from prediction intervals

**Subtasks:**
- [ ] Extract yhat, yhat_lower, yhat_upper from forecast DataFrame
- [ ] Calculate interval width: `width = yhat_upper - yhat_lower`
- [ ] Calculate average interval width: `avg_width = width.mean()`
- [ ] Calculate average prediction: `avg_pred = yhat.mean()`
- [ ] Calculate confidence score: `confidence = 1.0 - (avg_width / avg_pred)`
- [ ] Clip confidence to [0.0, 1.0] range
- [ ] Return confidence score

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
- [ ] Create file: `backend/tests/unit/ml/test_prophet_wrapper.py`
- [ ] Write test fixture with sample historical data (52 weeks)
- [ ] **Test 1:** `test_prophet_train_with_valid_data()`
  - Train model with 52 weeks of data
  - Assert model is not None
  - Assert no errors raised
- [ ] **Test 2:** `test_prophet_forecast_returns_correct_shape()`
  - Train model, forecast 12 weeks
  - Assert predictions list has 12 items
  - Assert all predictions are positive integers
- [ ] **Test 3:** `test_prophet_confidence_score_in_range()`
  - Train model, forecast, calculate confidence
  - Assert 0.0 <= confidence <= 1.0
- [ ] **Test 4:** `test_prophet_raises_error_on_insufficient_data()`
  - Try to train with only 20 weeks of data
  - Assert InsufficientDataError is raised
- [ ] **Test 5:** `test_prophet_forecast_without_training_raises_error()`
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
- [ ] Load historical sales data (62 weeks total)
- [ ] Split into train (52 weeks) and validation (10 weeks)
- [ ] Train Prophet on 52 weeks
- [ ] Forecast next 10 weeks
- [ ] Calculate MAPE on validation set:
  ```python
  from sklearn.metrics import mean_absolute_percentage_error
  mape = mean_absolute_percentage_error(actual, predicted) * 100
  ```
- [ ] Document MAPE result in test output
- [ ] Assert MAPE < 20% (target for single model)

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
- [ ] ProphetWrapper class implemented with all methods
- [ ] Prophet configured with correct hyperparameters
- [ ] train() method trains model successfully
- [ ] forecast() method generates weekly predictions
- [ ] get_confidence() method calculates confidence score
- [ ] All type hints present
- [ ] All docstrings complete (Google style)

**Testing Complete:**
- [ ] 5 unit tests written and passing
- [ ] Validation test shows MAPE < 20%
- [ ] Test coverage >90% for ProphetWrapper
- [ ] No flaky tests

**Quality Checks:**
- [ ] Code follows project style guide
- [ ] No console.log or print statements (use logging)
- [ ] Error handling complete (InsufficientDataError, ModelTrainingError)
- [ ] Performance targets met (<5s training, <1s forecast)

**Documentation:**
- [ ] Docstrings complete for all public methods
- [ ] Any hyperparameter tuning decisions documented in technical_decisions.md
- [ ] MAPE results documented in test output

**Ready for Next Story:**
- [ ] ProphetWrapper can be imported and used
- [ ] Ready to integrate with ARIMA in Story 2
- [ ] Ready to be called by EnsembleForecaster in Story 3

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
