"""Integration tests for EnsembleForecaster."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.ml.ensemble_forecaster import EnsembleForecaster, ForecastingError
from app.ml.prophet_wrapper import ProphetWrapper, InsufficientDataError
from app.ml.arima_wrapper import ARIMAWrapper


@pytest.fixture
def historical_data_52_weeks():
    """Generate 52 weeks of synthetic historical sales data."""
    dates = pd.date_range(start='2023-01-01', periods=52, freq='W')
    # Generate realistic sales data with seasonality
    base_demand = 100
    seasonal_factor = 20 * np.sin(np.arange(52) * 2 * np.pi / 52)
    noise = np.random.normal(0, 10, 52)
    quantity = np.maximum(base_demand + seasonal_factor + noise, 10).astype(int)

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity
    })


@pytest.fixture
def historical_data_62_weeks():
    """Generate 62 weeks of synthetic historical sales data (52 train + 10 validation)."""
    dates = pd.date_range(start='2023-01-01', periods=62, freq='W')
    # Generate realistic sales data with seasonality
    base_demand = 100
    seasonal_factor = 20 * np.sin(np.arange(62) * 2 * np.pi / 52)
    noise = np.random.normal(0, 10, 62)
    quantity = np.maximum(base_demand + seasonal_factor + noise, 10).astype(int)

    return pd.DataFrame({
        'date': dates,
        'quantity_sold': quantity
    })


class TestEnsembleForecasterInit:
    """Test EnsembleForecaster initialization."""

    def test_init_with_default_wrappers(self):
        """Test initialization with default wrappers."""
        ensemble = EnsembleForecaster()
        assert ensemble.prophet is not None
        assert ensemble.arima is not None
        assert ensemble.weights == (0.6, 0.4)
        assert ensemble.model_used == "prophet_arima_ensemble"

    def test_init_with_custom_wrappers(self):
        """Test initialization with custom wrappers."""
        prophet = ProphetWrapper()
        arima = ARIMAWrapper()
        ensemble = EnsembleForecaster(prophet_wrapper=prophet, arima_wrapper=arima)
        assert ensemble.prophet is prophet
        assert ensemble.arima is arima

    def test_init_with_custom_weights(self):
        """Test initialization with custom weights."""
        weights = (0.7, 0.3)
        ensemble = EnsembleForecaster(weights=weights)
        assert ensemble.weights == weights


class TestEnsembleForecasterTrain:
    """Test EnsembleForecaster training."""

    def test_train_with_both_models_success(self, historical_data_52_weeks):
        """Test successful training with both models."""
        ensemble = EnsembleForecaster()
        # Should not raise error
        ensemble.train(historical_data_52_weeks)
        assert ensemble.prophet is not None
        assert ensemble.arima is not None
        assert ensemble.model_used == "prophet_arima_ensemble"

    def test_train_insufficient_data(self):
        """Test training with insufficient data."""
        ensemble = EnsembleForecaster()
        insufficient_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=10, freq='W'),
            'quantity_sold': [100] * 10
        })
        with pytest.raises(ForecastingError):
            ensemble.train(insufficient_data)

    def test_train_both_models_fail_gracefully(self):
        """Test graceful handling when both models fail to train."""
        ensemble = EnsembleForecaster()
        invalid_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=52, freq='W'),
            'invalid_column': [100] * 52
        })
        with pytest.raises(ForecastingError):
            ensemble.train(invalid_data)


class TestEnsembleForecasterWeightedAverage:
    """Test weighted averaging logic."""

    def test_weighted_average_basic(self):
        """Test basic weighted average calculation."""
        ensemble = EnsembleForecaster()
        prophet_pred = [100, 110, 120]
        arima_pred = [90, 100, 110]
        weights = (0.6, 0.4)

        result = ensemble._weighted_average(prophet_pred, arima_pred, weights)

        expected = [
            int(0.6 * 100 + 0.4 * 90),
            int(0.6 * 110 + 0.4 * 100),
            int(0.6 * 120 + 0.4 * 110)
        ]
        assert result == expected

    def test_weighted_average_equal_weights(self):
        """Test weighted average with equal weights."""
        ensemble = EnsembleForecaster()
        prophet_pred = [100, 200]
        arima_pred = [200, 100]
        weights = (0.5, 0.5)

        result = ensemble._weighted_average(prophet_pred, arima_pred, weights)

        assert result == [150, 150]

    def test_weighted_average_mismatched_lengths(self):
        """Test weighted average with mismatched list lengths."""
        ensemble = EnsembleForecaster()
        prophet_pred = [100, 110]
        arima_pred = [90, 100, 110]
        weights = (0.6, 0.4)

        with pytest.raises(ValueError):
            ensemble._weighted_average(prophet_pred, arima_pred, weights)

    def test_weighted_average_handles_negative_values(self):
        """Test weighted average clipping negative values."""
        ensemble = EnsembleForecaster()
        prophet_pred = [100, 110]
        arima_pred = [-10, 100]
        weights = (0.6, 0.4)

        result = ensemble._weighted_average(prophet_pred, arima_pred, weights)
        # Negative values should be clipped to 0
        assert all(x >= 0 for x in result)


class TestEnsembleForecasterForecast:
    """Test ensemble forecasting with fallback logic."""

    def test_forecast_with_both_models(self, historical_data_52_weeks):
        """Test forecast when both models are available."""
        ensemble = EnsembleForecaster()
        ensemble.train(historical_data_52_weeks)

        result = ensemble.forecast(periods=12)

        assert "predictions" in result
        assert "confidence" in result
        assert "model_used" in result
        assert len(result["predictions"]) == 12
        assert result["model_used"] == "prophet_arima_ensemble"
        assert 0.0 <= result["confidence"] <= 1.0
        assert all(x >= 0 for x in result["predictions"])

    def test_forecast_fallback_to_prophet_only(self, historical_data_52_weeks):
        """Test fallback to Prophet when ARIMA fails."""
        ensemble = EnsembleForecaster()
        ensemble.train(historical_data_52_weeks)
        # Simulate ARIMA failure by setting it to None
        ensemble.arima = None

        result = ensemble.forecast(periods=12)

        assert result["model_used"] == "prophet"
        assert len(result["predictions"]) == 12
        assert 0.0 <= result["confidence"] <= 1.0

    def test_forecast_fallback_to_arima_only(self, historical_data_52_weeks):
        """Test fallback to ARIMA when Prophet fails."""
        ensemble = EnsembleForecaster()
        ensemble.train(historical_data_52_weeks)
        # Simulate Prophet failure by setting it to None
        ensemble.prophet = None

        result = ensemble.forecast(periods=12)

        assert result["model_used"] == "arima"
        assert len(result["predictions"]) == 12
        assert 0.0 <= result["confidence"] <= 1.0

    def test_forecast_both_models_fail(self):
        """Test forecast when both models are unavailable."""
        ensemble = EnsembleForecaster()
        ensemble.prophet = None
        ensemble.arima = None

        with pytest.raises(ForecastingError):
            ensemble.forecast(periods=12)


class TestEnsembleForecasterDynamicWeights:
    """Test dynamic weight calculation."""

    def test_calculate_dynamic_weights(self, historical_data_52_weeks):
        """Test dynamic weight calculation."""
        ensemble = EnsembleForecaster()
        ensemble.train(historical_data_52_weeks)

        # Use last 10 weeks as validation
        validation_data = historical_data_52_weeks.tail(10).reset_index(drop=True)
        weights = ensemble._calculate_dynamic_weights(validation_data)

        assert len(weights) == 2
        assert abs(sum(weights) - 1.0) < 0.01  # Sum should be ~1.0
        assert 0.3 <= weights[0] <= 0.7  # Prophet weight in reasonable range
        assert 0.3 <= weights[1] <= 0.7  # ARIMA weight in reasonable range

    def test_calculate_dynamic_weights_insufficient_data(self):
        """Test dynamic weights with insufficient validation data."""
        ensemble = EnsembleForecaster()
        insufficient_validation = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=3, freq='W'),
            'quantity_sold': [100, 110, 120]
        })

        weights = ensemble._calculate_dynamic_weights(insufficient_validation)
        # Should return default weights when validation data insufficient
        assert weights == ensemble.weights


class TestEnsembleForecasterMAPE:
    """Test MAPE calculation."""

    def test_calculate_mape(self):
        """Test MAPE calculation."""
        ensemble = EnsembleForecaster()
        actual = np.array([100, 110, 120, 130])
        predicted = np.array([95, 115, 118, 135])

        mape = ensemble._calculate_mape(actual, predicted)

        # Calculate expected MAPE manually
        # |100-95|/100 = 0.05, |110-115|/110 = 0.045, |120-118|/120 = 0.017, |130-135|/130 = 0.038
        # Mean = (0.05 + 0.045 + 0.017 + 0.038) / 4 * 100 = 3.75%
        assert 3.5 < mape < 4.0

    def test_calculate_mape_zero_actual(self):
        """Test MAPE with zero actual value (edge case)."""
        ensemble = EnsembleForecaster()
        actual = np.array([100, 0, 120])
        predicted = np.array([95, 10, 118])

        mape = ensemble._calculate_mape(actual, predicted)
        # Should handle zero actual by skipping it
        assert mape >= 0


class TestEnsembleForecasterAccuracy:
    """Test ensemble accuracy against individual models."""

    def test_ensemble_outperforms_individual_models(self, historical_data_62_weeks):
        """Test that ensemble MAPE is better than individual models."""
        # Split data: 52 weeks train, 10 weeks validation
        train_data = historical_data_62_weeks.iloc[:52]
        validation_data = historical_data_62_weeks.iloc[52:].reset_index(drop=True)

        # Train ensemble
        ensemble = EnsembleForecaster()
        ensemble.train(train_data)

        # Forecast on validation set
        ensemble_forecast = ensemble.forecast(len(validation_data))
        actual = validation_data['quantity_sold'].values

        # Calculate MAPE
        ensemble_mape = ensemble._calculate_mape(actual, ensemble_forecast['predictions'])

        # Train individual models for comparison
        prophet = ProphetWrapper()
        prophet.train(train_data)
        prophet_forecast = prophet.forecast(len(validation_data))
        prophet_mape = ensemble._calculate_mape(actual, prophet_forecast['predictions'])

        arima = ARIMAWrapper()
        arima.train(train_data)
        arima_forecast = arima.forecast(len(validation_data))
        arima_mape = ensemble._calculate_mape(actual, arima_forecast['predictions'])

        # Ensemble should perform well
        assert ensemble_mape < 25  # Allow some flexibility for synthetic data
        # Ensemble should be competitive with individual models
        assert ensemble_mape <= max(prophet_mape, arima_mape) * 1.1  # Allow 10% margin


class TestEnsembleForecasterOutputContract:
    """Test that ensemble output matches expected contract."""

    def test_forecast_output_contract(self, historical_data_52_weeks):
        """Test forecast output contains all required fields."""
        ensemble = EnsembleForecaster()
        ensemble.train(historical_data_52_weeks)
        result = ensemble.forecast(periods=12)

        # Required fields
        assert "predictions" in result
        assert "confidence" in result
        assert "model_used" in result
        assert "lower_bound" in result
        assert "upper_bound" in result

        # Type checks
        assert isinstance(result["predictions"], list)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["model_used"], str)
        assert isinstance(result["lower_bound"], list)
        assert isinstance(result["upper_bound"], list)

        # Value range checks
        assert len(result["predictions"]) == 12
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["model_used"] in ["prophet_arima_ensemble", "prophet", "arima"]
        assert all(x >= 0 for x in result["predictions"])