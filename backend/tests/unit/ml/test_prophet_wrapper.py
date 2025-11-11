"""Unit tests for ProphetWrapper

Tests cover:
- Training with valid data
- Forecasting with correct shape/values
- Confidence score calculation
- Error handling (insufficient data, untrained model)
- Edge cases
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.ml.prophet_wrapper import (
    ProphetWrapper,
    InsufficientDataError,
    ModelTrainingError
)


@pytest.fixture
def sample_historical_data_52_weeks():
    """Create sample historical data with 52 weeks of realistic sales patterns."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(52)]

    # Generate synthetic sales with seasonality and trend
    base_sales = 100
    trend = np.linspace(0, 20, 52)  # Upward trend
    seasonality = 20 * np.sin(np.linspace(0, 4 * np.pi, 52))  # Seasonal pattern
    noise = np.random.normal(0, 5, 52)  # Random noise

    quantity_sold = base_sales + trend + seasonality + noise
    quantity_sold = np.maximum(quantity_sold, 10)  # Ensure positive values

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity_sold
    })


@pytest.fixture
def sample_historical_data_20_weeks():
    """Create sample historical data with only 20 weeks (insufficient)."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(20)]
    quantity_sold = np.random.uniform(80, 120, 20)

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity_sold
    })


@pytest.fixture
def sample_historical_data_62_weeks():
    """Create 62 weeks of data for validation testing (52 train + 10 test)."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(62)]

    # Generate synthetic sales with clear pattern
    base_sales = 100
    trend = np.linspace(0, 30, 62)
    seasonality = 25 * np.sin(np.linspace(0, 5 * np.pi, 62))
    noise = np.random.normal(0, 5, 62)

    quantity_sold = base_sales + trend + seasonality + noise
    quantity_sold = np.maximum(quantity_sold, 10)

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity_sold
    })


class TestProphetWrapperTraining:
    """Test suite for ProphetWrapper training functionality."""

    def test_prophet_train_with_valid_data(self, sample_historical_data_52_weeks):
        """Test 1: Train model with 52 weeks of data."""
        wrapper = ProphetWrapper()

        # Should complete without errors
        wrapper.train(sample_historical_data_52_weeks)

        # Model should be initialized
        assert wrapper.model is not None
        assert hasattr(wrapper.model, 'predict')

    def test_prophet_train_with_minimal_data(self):
        """Test training with exactly 26 weeks (minimum requirement)."""
        # Create exactly 26 weeks of data
        start_date = datetime(2023, 1, 1)
        dates = [start_date + timedelta(weeks=i) for i in range(26)]
        data = pd.DataFrame({
            'date': dates,
            'quantity_sold': np.random.uniform(80, 120, 26)
        })

        wrapper = ProphetWrapper()
        wrapper.train(data)

        assert wrapper.model is not None

    def test_prophet_raises_error_on_insufficient_data(self, sample_historical_data_20_weeks):
        """Test 4: Try to train with only 20 weeks of data (should fail)."""
        wrapper = ProphetWrapper()

        with pytest.raises(InsufficientDataError) as exc_info:
            wrapper.train(sample_historical_data_20_weeks)

        assert "at least 26 weeks" in str(exc_info.value)

    def test_prophet_train_with_missing_columns(self):
        """Test error handling when required columns are missing."""
        # Data with wrong column names
        data = pd.DataFrame({
            'wrong_date': [datetime(2023, 1, 1)],
            'wrong_quantity': [100]
        })

        wrapper = ProphetWrapper()

        with pytest.raises(ValueError) as exc_info:
            wrapper.train(data)

        assert "must contain columns" in str(exc_info.value)

    def test_prophet_train_handles_missing_values(self):
        """Test that missing values are handled gracefully."""
        start_date = datetime(2023, 1, 1)
        dates = [start_date + timedelta(weeks=i) for i in range(30)]
        quantity_sold = np.random.uniform(80, 120, 30)
        quantity_sold[10] = np.nan  # Introduce missing value
        quantity_sold[15] = np.nan

        data = pd.DataFrame({
            'date': dates,
            'quantity_sold': quantity_sold
        })

        wrapper = ProphetWrapper()
        wrapper.train(data)  # Should not raise error

        assert wrapper.model is not None


class TestProphetWrapperForecasting:
    """Test suite for ProphetWrapper forecasting functionality."""

    def test_prophet_forecast_returns_correct_shape(self, sample_historical_data_52_weeks):
        """Test 2: Train model and forecast 12 weeks."""
        wrapper = ProphetWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        forecast = wrapper.forecast(periods=12)

        # Check structure
        assert 'predictions' in forecast
        assert 'lower_bound' in forecast
        assert 'upper_bound' in forecast
        assert 'dates' in forecast

        # Check lengths
        assert len(forecast['predictions']) == 12
        assert len(forecast['lower_bound']) == 12
        assert len(forecast['upper_bound']) == 12
        assert len(forecast['dates']) == 12

        # Check all predictions are positive integers
        assert all(isinstance(p, int) for p in forecast['predictions'])
        assert all(p > 0 for p in forecast['predictions'])

    def test_prophet_forecast_without_training_raises_error(self):
        """Test 5: Try to call forecast() without training."""
        wrapper = ProphetWrapper()

        with pytest.raises(RuntimeError) as exc_info:
            wrapper.forecast(periods=12)

        assert "not been trained" in str(exc_info.value)

    def test_prophet_forecast_bounds_make_sense(self, sample_historical_data_52_weeks):
        """Test that confidence bounds are reasonable."""
        wrapper = ProphetWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        forecast = wrapper.forecast(periods=12)

        # Upper bound should be >= prediction >= lower bound
        for i in range(12):
            assert forecast['lower_bound'][i] <= forecast['predictions'][i]
            assert forecast['predictions'][i] <= forecast['upper_bound'][i]

    def test_prophet_forecast_dates_are_sequential(self, sample_historical_data_52_weeks):
        """Test that forecast dates are properly sequential."""
        wrapper = ProphetWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        forecast = wrapper.forecast(periods=12)

        # Convert dates back to datetime for comparison
        dates = [datetime.fromisoformat(d) for d in forecast['dates']]

        # Check dates are sequential (approximately 7 days apart)
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i-1]).days
            assert 5 <= delta <= 9  # Allow some flexibility around 7 days


class TestProphetWrapperConfidence:
    """Test suite for confidence score calculation."""

    def test_prophet_confidence_score_in_range(self, sample_historical_data_52_weeks):
        """Test 3: Train model, forecast, and calculate confidence."""
        wrapper = ProphetWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        # Generate forecast
        future = wrapper.model.make_future_dataframe(periods=12, freq='W')
        forecast_df = wrapper.model.predict(future)

        # Calculate confidence
        confidence = wrapper.get_confidence(forecast_df)

        # Confidence should be between 0.0 and 1.0
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)

    def test_prophet_confidence_narrow_intervals_higher(self):
        """Test that narrow prediction intervals result in higher confidence."""
        # Create mock forecast DataFrame with narrow intervals
        forecast_narrow = pd.DataFrame({
            'yhat': [100, 105, 110],
            'yhat_lower': [95, 100, 105],
            'yhat_upper': [105, 110, 115]
        })

        # Create mock forecast DataFrame with wide intervals
        forecast_wide = pd.DataFrame({
            'yhat': [100, 105, 110],
            'yhat_lower': [70, 75, 80],
            'yhat_upper': [130, 135, 140]
        })

        wrapper = ProphetWrapper()

        confidence_narrow = wrapper.get_confidence(forecast_narrow)
        confidence_wide = wrapper.get_confidence(forecast_wide)

        # Narrow intervals should have higher confidence
        assert confidence_narrow > confidence_wide

    def test_prophet_confidence_handles_zero_prediction(self):
        """Test confidence calculation when predictions are zero."""
        forecast_df = pd.DataFrame({
            'yhat': [0, 0, 0],
            'yhat_lower': [0, 0, 0],
            'yhat_upper': [0, 0, 0]
        })

        wrapper = ProphetWrapper()
        confidence = wrapper.get_confidence(forecast_df)

        assert confidence == 0.0  # Should return 0.0 for zero predictions


class TestProphetWrapperConfiguration:
    """Test suite for configuration and initialization."""

    def test_prophet_default_config(self):
        """Test that default configuration is applied."""
        wrapper = ProphetWrapper()

        assert wrapper.config['seasonality_mode'] == 'multiplicative'
        assert wrapper.config['yearly_seasonality'] is True
        assert wrapper.config['weekly_seasonality'] is True
        assert wrapper.config['daily_seasonality'] is False
        assert wrapper.config['changepoint_prior_scale'] == 0.05
        assert wrapper.config['seasonality_prior_scale'] == 10.0

    def test_prophet_custom_config(self):
        """Test that custom configuration is respected."""
        custom_config = {
            'seasonality_mode': 'additive',
            'yearly_seasonality': False,
            'weekly_seasonality': True,
            'daily_seasonality': False,
            'changepoint_prior_scale': 0.1,
            'seasonality_prior_scale': 5.0
        }

        wrapper = ProphetWrapper(config=custom_config)

        assert wrapper.config['seasonality_mode'] == 'additive'
        assert wrapper.config['yearly_seasonality'] is False
        assert wrapper.config['changepoint_prior_scale'] == 0.1


class TestProphetWrapperPerformance:
    """Test suite for performance requirements."""

    def test_prophet_training_time(self, sample_historical_data_52_weeks):
        """Test that training completes in <5 seconds."""
        import time

        wrapper = ProphetWrapper()

        start_time = time.time()
        wrapper.train(sample_historical_data_52_weeks)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 5.0, f"Training took {elapsed_time:.2f}s (should be <5s)"

    def test_prophet_forecasting_time(self, sample_historical_data_52_weeks):
        """Test that forecasting completes in <1 second."""
        import time

        wrapper = ProphetWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        start_time = time.time()
        wrapper.forecast(periods=12)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 1.0, f"Forecasting took {elapsed_time:.2f}s (should be <1s)"
