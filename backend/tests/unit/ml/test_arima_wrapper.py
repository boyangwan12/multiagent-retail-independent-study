"""Unit tests for ARIMAWrapper

Tests cover:
- Auto parameter selection (p, d, q)
- Training with valid data
- Forecasting with correct shape/values
- Non-stationary data handling
- Error handling (insufficient data, untrained model)
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.ml.arima_wrapper import (
    ARIMAWrapper,
    InsufficientDataError,
    ModelTrainingError
)


@pytest.fixture
def sample_historical_data_52_weeks():
    """Create sample historical data with 52 weeks and trend."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(52)]

    # Generate synthetic sales with clear trend (ARIMA excels at trends)
    base_sales = 100
    trend = np.linspace(0, 30, 52)  # Upward trend
    noise = np.random.normal(0, 8, 52)  # Random noise

    quantity_sold = base_sales + trend + noise
    quantity_sold = np.maximum(quantity_sold, 10)  # Ensure positive

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
def sample_non_stationary_data():
    """Create non-stationary data with strong trend (requires differencing)."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(52)]

    # Strong upward trend (non-stationary)
    quantity_sold = 50 + np.linspace(0, 100, 52) + np.random.normal(0, 5, 52)
    quantity_sold = np.maximum(quantity_sold, 10)

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity_sold
    })


@pytest.fixture
def sample_historical_data_62_weeks():
    """Create 62 weeks of data for validation testing."""
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(weeks=i) for i in range(62)]

    # Generate data with trend
    base_sales = 100
    trend = np.linspace(0, 35, 62)
    noise = np.random.normal(0, 8, 62)

    quantity_sold = base_sales + trend + noise
    quantity_sold = np.maximum(quantity_sold, 10)

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity_sold
    })


class TestARIMAWrapperParameterSelection:
    """Test suite for ARIMA auto parameter selection."""

    def test_arima_auto_parameter_selection(self, sample_historical_data_52_weeks):
        """Test 1: Train model and verify selected (p, d, q) are reasonable."""
        wrapper = ARIMAWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        # Check that parameters were selected
        assert wrapper.selected_order is not None
        p, d, q = wrapper.selected_order

        # Parameters should be reasonable (within typical bounds)
        assert 0 <= p <= 5, f"p={p} should be between 0 and 5"
        assert 0 <= d <= 2, f"d={d} should be between 0 and 2"
        assert 0 <= q <= 5, f"q={q} should be between 0 and 5"

        print(f"\nSelected ARIMA order: ({p}, {d}, {q})")

    def test_arima_differencing_detection(self, sample_non_stationary_data):
        """Test that ARIMA detects need for differencing (d > 0)."""
        wrapper = ARIMAWrapper()
        wrapper.train(sample_non_stationary_data)

        p, d, q = wrapper.selected_order

        # Non-stationary data should require differencing
        assert d >= 1, f"Non-stationary data should have d >= 1, got d={d}"

        print(f"\nNon-stationary data: Selected d={d} (differencing applied)")


class TestARIMAWrapperTraining:
    """Test suite for ARIMA training functionality."""

    def test_arima_train_with_valid_data(self, sample_historical_data_52_weeks):
        """Test 2: Train successfully with 52 weeks of data."""
        wrapper = ARIMAWrapper()

        # Should complete without errors
        wrapper.train(sample_historical_data_52_weeks)

        # Model should be initialized
        assert wrapper.model is not None
        assert hasattr(wrapper.model, 'forecast')

        # Selected order should be stored
        assert wrapper.selected_order is not None

    def test_arima_train_with_minimal_data(self):
        """Test training with exactly 26 weeks (minimum requirement)."""
        start_date = datetime(2023, 1, 1)
        dates = [start_date + timedelta(weeks=i) for i in range(26)]
        data = pd.DataFrame({
            'date': dates,
            'quantity_sold': 100 + np.linspace(0, 20, 26) + np.random.normal(0, 5, 26)
        })

        wrapper = ARIMAWrapper()
        wrapper.train(data)

        assert wrapper.model is not None

    def test_arima_raises_error_on_insufficient_data(self, sample_historical_data_20_weeks):
        """Test 5: Try to train with only 20 weeks of data (should fail)."""
        wrapper = ARIMAWrapper()

        with pytest.raises(InsufficientDataError) as exc_info:
            wrapper.train(sample_historical_data_20_weeks)

        assert "at least 26 weeks" in str(exc_info.value)

    def test_arima_train_with_missing_columns(self):
        """Test error handling when required columns are missing."""
        data = pd.DataFrame({
            'wrong_date': [datetime(2023, 1, 1)],
            'wrong_quantity': [100]
        })

        wrapper = ARIMAWrapper()

        with pytest.raises(ValueError) as exc_info:
            wrapper.train(data)

        assert "must contain columns" in str(exc_info.value)

    def test_arima_handles_missing_values(self):
        """Test that missing values are handled gracefully."""
        start_date = datetime(2023, 1, 1)
        dates = [start_date + timedelta(weeks=i) for i in range(30)]
        quantity_sold = np.random.uniform(80, 120, 30)
        quantity_sold[10] = np.nan  # Introduce missing value

        data = pd.DataFrame({
            'date': dates,
            'quantity_sold': quantity_sold
        })

        wrapper = ARIMAWrapper()
        wrapper.train(data)  # Should not raise error

        assert wrapper.model is not None

    def test_arima_fallback_on_failure(self):
        """Test fallback to ARIMA(1,1,1) when auto selection fails."""
        # Create pathological data that might cause auto-selection issues
        start_date = datetime(2023, 1, 1)
        dates = [start_date + timedelta(weeks=i) for i in range(30)]
        # Constant data (might cause issues)
        quantity_sold = np.full(30, 100.0) + np.random.normal(0, 0.1, 30)

        data = pd.DataFrame({
            'date': dates,
            'quantity_sold': quantity_sold
        })

        wrapper = ARIMAWrapper()
        wrapper.train(data)

        # Should still have a model (fallback)
        assert wrapper.model is not None
        assert wrapper.selected_order is not None


class TestARIMAWrapperForecasting:
    """Test suite for ARIMA forecasting functionality."""

    def test_arima_forecast_returns_correct_shape(self, sample_historical_data_52_weeks):
        """Test 3: Train model and forecast 12 weeks."""
        wrapper = ARIMAWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        forecast = wrapper.forecast(periods=12)

        # Check structure
        assert 'predictions' in forecast
        assert 'lower_bound' in forecast
        assert 'upper_bound' in forecast

        # Check lengths
        assert len(forecast['predictions']) == 12
        assert len(forecast['lower_bound']) == 12
        assert len(forecast['upper_bound']) == 12

        # Check all predictions are non-negative integers
        assert all(isinstance(p, int) for p in forecast['predictions'])
        assert all(p >= 0 for p in forecast['predictions'])

    def test_arima_forecast_without_training_raises_error(self):
        """Test that forecast() raises error without training."""
        wrapper = ARIMAWrapper()

        with pytest.raises(RuntimeError) as exc_info:
            wrapper.forecast(periods=12)

        assert "not been trained" in str(exc_info.value)

    def test_arima_forecast_bounds_make_sense(self, sample_historical_data_52_weeks):
        """Test that confidence bounds are reasonable."""
        wrapper = ARIMAWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        forecast = wrapper.forecast(periods=12)

        # Upper bound should be >= prediction >= lower bound
        for i in range(12):
            assert forecast['lower_bound'][i] <= forecast['predictions'][i]
            assert forecast['predictions'][i] <= forecast['upper_bound'][i]

    def test_arima_handles_non_stationary_data(self, sample_non_stationary_data):
        """Test 4: Verify ARIMA handles non-stationary data with differencing."""
        wrapper = ARIMAWrapper()

        # Should train successfully despite non-stationarity
        wrapper.train(sample_non_stationary_data)

        # Should be able to forecast
        forecast = wrapper.forecast(periods=10)

        # Forecast should have reasonable values
        assert len(forecast['predictions']) == 10
        assert all(p >= 0 for p in forecast['predictions'])

        # Differencing should have been applied (d > 0)
        p, d, q = wrapper.selected_order
        assert d >= 1, "Non-stationary data should trigger differencing"


class TestARIMAWrapperConfidence:
    """Test suite for confidence score calculation."""

    def test_arima_confidence_score_in_range(self, sample_historical_data_52_weeks):
        """Test that confidence score is between 0.0 and 1.0."""
        wrapper = ARIMAWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        forecast = wrapper.forecast(periods=12)
        confidence = wrapper.get_confidence(forecast)

        # Confidence should be between 0.0 and 1.0
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)

    def test_arima_confidence_narrow_intervals_higher(self):
        """Test that narrow prediction intervals result in higher confidence."""
        # Mock narrow interval forecast
        forecast_narrow = {
            'predictions': [100, 105, 110],
            'lower_bound': [95, 100, 105],
            'upper_bound': [105, 110, 115]
        }

        # Mock wide interval forecast
        forecast_wide = {
            'predictions': [100, 105, 110],
            'lower_bound': [70, 75, 80],
            'upper_bound': [130, 135, 140]
        }

        wrapper = ARIMAWrapper()

        confidence_narrow = wrapper.get_confidence(forecast_narrow)
        confidence_wide = wrapper.get_confidence(forecast_wide)

        # Narrow intervals should have higher confidence
        assert confidence_narrow > confidence_wide

    def test_arima_confidence_handles_zero_prediction(self):
        """Test confidence calculation when predictions are zero."""
        forecast = {
            'predictions': [0, 0, 0],
            'lower_bound': [0, 0, 0],
            'upper_bound': [0, 0, 0]
        }

        wrapper = ARIMAWrapper()
        confidence = wrapper.get_confidence(forecast)

        assert confidence == 0.0


class TestARIMAWrapperConfiguration:
    """Test suite for configuration and initialization."""

    def test_arima_default_config(self):
        """Test that default configuration is applied."""
        wrapper = ARIMAWrapper()

        assert wrapper.config['start_p'] == 0
        assert wrapper.config['max_p'] == 5
        assert wrapper.config['start_q'] == 0
        assert wrapper.config['max_q'] == 5
        assert wrapper.config['stepwise'] is True

    def test_arima_custom_config(self):
        """Test that custom configuration is respected."""
        custom_config = {
            'start_p': 1,
            'max_p': 3,
            'start_q': 1,
            'max_q': 3,
            'stepwise': False
        }

        wrapper = ARIMAWrapper(config=custom_config)

        assert wrapper.config['start_p'] == 1
        assert wrapper.config['max_p'] == 3
        assert wrapper.config['stepwise'] is False


class TestARIMAWrapperPerformance:
    """Test suite for performance requirements."""

    def test_arima_training_time(self, sample_historical_data_52_weeks):
        """Test that training completes in <8 seconds."""
        import time

        wrapper = ARIMAWrapper()

        start_time = time.time()
        wrapper.train(sample_historical_data_52_weeks)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 8.0, f"Training took {elapsed_time:.2f}s (should be <8s)"

    def test_arima_forecasting_time(self, sample_historical_data_52_weeks):
        """Test that forecasting completes in <1 second."""
        import time

        wrapper = ARIMAWrapper()
        wrapper.train(sample_historical_data_52_weeks)

        start_time = time.time()
        wrapper.forecast(periods=12)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 1.0, f"Forecasting took {elapsed_time:.2f}s (should be <1s)"
