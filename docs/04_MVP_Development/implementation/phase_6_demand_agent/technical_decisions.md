# Phase 6: Demand Agent - Technical Decisions

**Phase:** 6 of 8
**Date:** 2025-11-11
**Decision Maker:** Development Team + Architect
**Status:** Approved

---

## TD-6.1: Ensemble Approach (Prophet + ARIMA)

### Decision
Use **ensemble forecasting combining Prophet and ARIMA** instead of single model.

### Rationale
**Why Ensemble?**
- Prophet excels at capturing seasonality and holidays
- ARIMA excels at capturing trend and short-term patterns
- Ensemble reduces model-specific bias and improves robustness
- Industry best practice for retail forecasting

**Alternatives Considered:**
1. **Prophet only**: Simpler but less accurate on non-seasonal data
2. **ARIMA only**: Requires stationary data, struggles with seasonality
3. **LSTM/Neural Network**: Overkill for MVP, requires large dataset (1000+ weeks)

**Ensemble Weight Strategy:**
- Default: 60% Prophet, 40% ARIMA (based on retail forecasting literature)
- Dynamic weighting: Calculate MAPE on validation set, assign weights inversely proportional to error
- Formula: `weight_prophet = MAPE_arima / (MAPE_prophet + MAPE_arima)`

### Impact
- **Code Complexity:** Moderate (3 classes instead of 1)
- **Performance:** Minimal impact (<2 seconds additional)
- **Accuracy:** Expected MAPE improvement of 3-5%

### Validation
- Compare ensemble MAPE vs single model MAPE on test set
- Target: Ensemble MAPE < min(Prophet MAPE, ARIMA MAPE)

---

## TD-6.2: Prophet Hyperparameters

### Decision
Use the following Prophet configuration:

```python
model = Prophet(
    seasonality_mode='multiplicative',  # Retail sales scale with level
    yearly_seasonality=True,           # Capture annual patterns
    weekly_seasonality=True,           # Capture weekly patterns (weekend effect)
    daily_seasonality=False,           # Not relevant for weekly forecasts
    changepoint_prior_scale=0.05,      # Conservative (reduce overfitting)
    seasonality_prior_scale=10.0       # Strong seasonality (retail data)
)
```

### Rationale
**seasonality_mode='multiplicative':**
- Retail sales exhibit multiplicative seasonality (holiday sales are 3x baseline, not +constant)
- Aligns with domain knowledge

**changepoint_prior_scale=0.05:**
- Conservative setting to avoid overfitting on historical noise
- Retail demand has gradual trends, not sudden changepoints

**seasonality_prior_scale=10.0:**
- Retail data has strong weekly seasonality (weekend vs weekday)
- Higher value fits seasonality more aggressively

### Alternatives Considered
- Default Prophet settings: Less accurate on retail data (tested on sample dataset)
- Grid search hyperparameter tuning: Too slow for MVP, defer to post-MVP optimization

### Validation
- Test on 10 weeks held-out validation set
- Compare against default Prophet settings
- Target: 2-3% MAPE improvement

---

## TD-6.3: ARIMA Parameter Selection

### Decision
Use **Auto ARIMA from pmdarima library** for automatic (p, d, q) parameter selection.

```python
from pmdarima import auto_arima

model = auto_arima(
    y=historical_sales,
    start_p=0, max_p=5,      # AR terms
    start_q=0, max_q=5,      # MA terms
    d=None,                   # Auto-detect differencing
    seasonal=False,           # Weekly seasonality handled by Prophet
    stepwise=True,            # Faster than exhaustive search
    suppress_warnings=True,
    error_action='ignore',
    trace=False
)
```

### Rationale
**Why Auto ARIMA?**
- Manual (p, d, q) selection requires domain expertise and is time-consuming
- Auto ARIMA uses AIC/BIC for model selection
- Converges in <10 seconds on 52 weeks of data

**Why seasonal=False?**
- Prophet already handles seasonality
- ARIMA focuses on trend and residual patterns
- Avoids redundant seasonal modeling

### Alternatives Considered
- Manual ARIMA(1,1,1): Fast but suboptimal for all datasets
- SARIMAX with seasonal terms: Redundant with Prophet, slower

### Validation
- Verify auto_arima completes in <10 seconds
- Check selected (p, d, q) parameters are reasonable (p, q < 5)
- Fallback to ARIMA(1,1,1) if auto_arima fails

---

## TD-6.4: Data Preprocessing

### Decision
Apply the following preprocessing pipeline:

```python
def preprocess_historical_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare historical sales data for Prophet and ARIMA"""
    # 1. Aggregate to weekly level (sum daily sales)
    weekly = df.groupby(pd.Grouper(key='date', freq='W')).sum()

    # 2. Handle missing weeks (forward fill)
    weekly = weekly.asfreq('W', method='ffill')

    # 3. Outlier detection (clip to 3 std deviations)
    mean = weekly['quantity_sold'].mean()
    std = weekly['quantity_sold'].std()
    weekly['quantity_sold'] = weekly['quantity_sold'].clip(
        lower=mean - 3*std,
        upper=mean + 3*std
    )

    # 4. Format for Prophet (requires 'ds' and 'y' columns)
    prophet_df = weekly.reset_index()
    prophet_df.columns = ['ds', 'y']

    return prophet_df
```

### Rationale
**Weekly Aggregation:**
- Forecasting at weekly level (not daily) per PRD requirements
- Reduces noise and improves model stability

**Missing Value Handling:**
- Forward fill assumes sales continue at last known level
- Better than dropping missing weeks (loses data)

**Outlier Clipping:**
- Prevents extreme values from skewing forecast
- 3 std dev threshold is industry standard

### Alternatives Considered
- No preprocessing: Results in noisy forecasts
- Interpolation for missing values: Assumes linear trend (less realistic)
- Remove outliers entirely: Loses information

### Validation
- Visualize preprocessed data (plot time series)
- Verify no NaN values remain
- Check data shape matches expected (52+ weeks)

---

## TD-6.5: Confidence Interval Calculation

### Decision
Use **Prophet's built-in uncertainty intervals** as primary confidence measure:

```python
# Prophet provides 'yhat_lower' and 'yhat_upper' (80% interval by default)
forecast = model.predict(future)

# Calculate confidence score (0.0-1.0)
confidence = 1.0 - (
    (forecast['yhat_upper'] - forecast['yhat_lower']).mean() /
    forecast['yhat'].mean()
)
```

### Rationale
**Why Prophet Intervals?**
- Prophet models uncertainty from trend, seasonality, and residuals
- More sophisticated than simple RMSE-based confidence
- Widely validated in industry

**Confidence Score Formula:**
- Narrow intervals → High confidence (close to 1.0)
- Wide intervals → Low confidence (close to 0.0)
- Normalized by forecast magnitude

### Alternatives Considered
- ARIMA confidence intervals: Less interpretable than Prophet
- Historical MAPE as confidence: Doesn't account for future uncertainty

### Validation
- Verify confidence scores are in range [0.0, 1.0]
- Check that low-variance forecasts have higher confidence
- Target: Confidence > 0.7 for typical retail data

---

## TD-6.6: Fallback Strategy

### Decision
Implement graceful fallback if one model fails:

```python
def generate_forecast(context):
    try:
        prophet_forecast = prophet_wrapper.forecast(context)
    except Exception as e:
        logger.warning(f"Prophet failed: {e}")
        prophet_forecast = None

    try:
        arima_forecast = arima_wrapper.forecast(context)
    except Exception as e:
        logger.warning(f"ARIMA failed: {e}")
        arima_forecast = None

    # Ensemble logic
    if prophet_forecast and arima_forecast:
        return weighted_average(prophet_forecast, arima_forecast)
    elif prophet_forecast:
        logger.info("Using Prophet only (ARIMA failed)")
        return prophet_forecast
    elif arima_forecast:
        logger.info("Using ARIMA only (Prophet failed)")
        return arima_forecast
    else:
        raise ForecastingError("Both models failed")
```

### Rationale
- System remains operational even if one model fails
- Prophet more robust (recommended primary)
- Logs failures for debugging

### Validation
- Test with intentionally broken Prophet (verify ARIMA fallback)
- Test with intentionally broken ARIMA (verify Prophet fallback)
- Test with both broken (verify error raised)

---

## TD-6.7: Output Contract (DemandAgentOutput)

### Decision
Strictly follow the contract defined in Phase 5:

```python
# backend/app/agents/contracts.py (created in Phase 5)
class DemandAgentOutput(BaseModel):
    total_demand: int
    forecast_by_week: List[int]
    safety_stock_pct: float
    confidence: float
    model_used: str  # "prophet_arima_ensemble" | "prophet" | "arima"
```

### Rationale
- Phase 7 (Inventory Agent) depends on this contract
- Changing contract breaks downstream agents
- Pydantic validation ensures compliance

### Validation
- Assert output matches DemandAgentOutput schema in tests
- Verify Phase 7 can consume output without changes

---

## TD-6.8: Performance Optimization

### Decision
Target forecast generation in <10 seconds:

**Optimization Strategies:**
1. **Cache trained models** (in-memory for same parameters)
2. **Use Phase 5 cached historical data** (already loaded by ContextAssembler)
3. **Parallelize Prophet and ARIMA** (asyncio if needed)
4. **Limit historical data to 52 weeks** (more data doesn't improve weekly forecasts significantly)

### Rationale
- 10-second threshold balances accuracy and UX
- Caching avoids redundant training
- Most time spent in model training (not prediction)

### Validation
- Profile code with cProfile
- Measure end-to-end time (context → forecast_result)
- Target breakdown: Training 6s + Prediction 2s + Overhead 2s = 10s

---

## TD-6.9: Error Handling

### Decision
Raise custom exceptions with helpful messages:

```python
# backend/app/agents/errors.py
class ForecastingError(Exception):
    """Base exception for forecasting errors"""
    pass

class InsufficientDataError(ForecastingError):
    """Raised when historical data < 26 weeks"""
    pass

class ModelTrainingError(ForecastingError):
    """Raised when model training fails"""
    pass
```

### Rationale
- Specific exceptions allow targeted error handling
- Helpful messages aid debugging
- Consistent with Phase 5 error handling pattern

### Validation
- Test error paths (insufficient data, training failure)
- Verify error messages are clear and actionable

---

## TD-6.10: Logging Strategy

### Decision
Log key metrics during forecasting:

```python
logger.info(f"Starting demand forecast for {horizon_weeks} weeks")
logger.info(f"Historical data: {len(historical_data)} weeks")
logger.info(f"Prophet MAPE: {prophet_mape:.2f}%")
logger.info(f"ARIMA MAPE: {arima_mape:.2f}%")
logger.info(f"Ensemble MAPE: {ensemble_mape:.2f}%")
logger.info(f"Forecast total demand: {total_demand} units")
logger.info(f"Confidence: {confidence:.2f}")
logger.info(f"Forecast generation took {elapsed:.2f}s")
```

### Rationale
- Enables performance monitoring
- Tracks accuracy over time
- Aids debugging in production

### Validation
- Verify logs appear in console during testing
- Check log format is parseable (JSON logs in production)

---

## Summary

These technical decisions prioritize:
1. **Accuracy:** Ensemble approach + hyperparameter tuning
2. **Robustness:** Fallback strategies + error handling
3. **Performance:** Caching + optimization (<10s target)
4. **Maintainability:** Clear contracts + logging + testing

All decisions align with Phase 5 orchestrator contracts and enable seamless integration with Phase 7 (Inventory Agent).

---

**Approved By:** Development Team
**Date:** 2025-11-11
**Version:** 1.0
