"""ARIMA Wrapper for Time Series Forecasting

This module provides a wrapper around statsmodels ARIMA for trend-based demand forecasting.
ARIMA captures non-seasonal patterns and autocorrelation, complementing Prophet's seasonality.
"""

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging
import warnings

logger = logging.getLogger("fashion_forecast")


class InsufficientDataError(Exception):
    """Raised when insufficient historical data is provided for training."""
    pass


class ModelTrainingError(Exception):
    """Raised when ARIMA model training fails."""
    pass


class ARIMAWrapper:
    """Wrapper for ARIMA time series forecasting with Auto parameter selection.

    This class provides ARIMA forecasting with automatic parameter selection
    using AIC (Akaike Information Criterion) for optimal model fit.

    Attributes:
        model: Trained ARIMA model instance
        config: Configuration dict for hyperparameters
        selected_order: Tuple (p, d, q) of selected ARIMA parameters
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize ARIMAWrapper with optional configuration.

        Args:
            config: Optional configuration dictionary with parameters:
                   - start_p: Minimum AR order (default: 0)
                   - max_p: Maximum AR order (default: 5)
                   - start_q: Minimum MA order (default: 0)
                   - max_q: Maximum MA order (default: 5)
                   - stepwise: Use stepwise search (default: True)
        """
        self.model: Optional[ARIMA] = None
        self.config = config or {
            'start_p': 0,
            'max_p': 5,
            'start_q': 0,
            'max_q': 5,
            'stepwise': True
        }
        self.selected_order: Optional[Tuple[int, int, int]] = None
        logger.info("ARIMAWrapper initialized with config: %s", self.config)

    def _determine_d(self, y: np.ndarray) -> int:
        """Determine differencing order using ADF test.

        Args:
            y: Time series values

        Returns:
            Differencing order (0, 1, or 2)
        """
        # Test stationarity with ADF test
        try:
            result = adfuller(y, autolag='AIC')
            p_value = result[1]

            # If p-value < 0.05, series is stationary (d=0)
            if p_value < 0.05:
                return 0

            # Try first difference
            y_diff = np.diff(y)
            result = adfuller(y_diff, autolag='AIC')
            p_value = result[1]

            if p_value < 0.05:
                return 1

            # If still not stationary, use d=2
            return 2
        except Exception as e:
            logger.warning(f"ADF test failed: {e}. Defaulting to d=1")
            return 1

    def _select_parameters_stepwise(self, y: np.ndarray, d: int) -> Tuple[int, int, int]:
        """Select ARIMA parameters using stepwise search.

        Args:
            y: Time series values
            d: Differencing order

        Returns:
            Tuple (p, d, q) with best parameters
        """
        best_aic = np.inf
        best_order = (1, d, 1)  # Default fallback

        # Stepwise search: start with simple models
        search_space = [
            (0, d, 0), (1, d, 0), (0, d, 1), (1, d, 1),
            (2, d, 1), (1, d, 2), (2, d, 2)
        ]

        for p, d_param, q in search_space:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    model = ARIMA(y, order=(p, d_param, q))
                    fitted = model.fit()

                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d_param, q)
            except Exception:
                continue

        logger.info(f"Stepwise search: Best order {best_order} with AIC={best_aic:.2f}")
        return best_order

    def _select_parameters_grid(self, y: np.ndarray, d: int) -> Tuple[int, int, int]:
        """Select ARIMA parameters using grid search.

        Args:
            y: Time series values
            d: Differencing order

        Returns:
            Tuple (p, d, q) with best parameters
        """
        best_aic = np.inf
        best_order = (1, d, 1)  # Default fallback

        max_p = self.config['max_p']
        max_q = self.config['max_q']

        for p in range(self.config['start_p'], max_p + 1):
            for q in range(self.config['start_q'], max_q + 1):
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore")
                        model = ARIMA(y, order=(p, d, q))
                        fitted = model.fit()

                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                except Exception:
                    continue

        logger.info(f"Grid search: Best order {best_order} with AIC={best_aic:.2f}")
        return best_order

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train ARIMA model using Auto parameter selection.

        Args:
            historical_data: DataFrame with columns ['date', 'quantity_sold'].
                           Must contain at least 26 weeks (6 months) of data.

        Raises:
            InsufficientDataError: If data contains fewer than 26 weeks
            ModelTrainingError: If ARIMA model training fails
            ValueError: If required columns are missing

        Example:
            >>> wrapper = ARIMAWrapper()
            >>> df = pd.DataFrame({
            ...     'date': pd.date_range('2024-01-01', periods=52, freq='W'),
            ...     'quantity_sold': [100, 120, 115, ...]
            ... })
            >>> wrapper.train(df)
        """
        logger.info("Starting ARIMA model training...")

        # Validate required columns
        required_columns = ['date', 'quantity_sold']
        if not all(col in historical_data.columns for col in required_columns):
            raise ValueError(
                f"Historical data must contain columns: {required_columns}. "
                f"Found: {list(historical_data.columns)}"
            )

        # Validate minimum data requirement (26 weeks = 6 months)
        if len(historical_data) < 26:
            raise InsufficientDataError(
                f"ARIMA requires at least 26 weeks of data. "
                f"Provided: {len(historical_data)} weeks"
            )

        # Extract time series values
        y = historical_data['quantity_sold'].values

        # Handle missing values
        if np.isnan(y).any():
            logger.warning("Missing values detected. Forward filling...")
            y = pd.Series(y).ffill().values

        try:
            # Determine differencing order
            d = self._determine_d(y)
            logger.info(f"Auto-detected differencing order: d={d}")

            # Select p and q parameters
            if self.config['stepwise']:
                p, d, q = self._select_parameters_stepwise(y, d)
            else:
                p, d, q = self._select_parameters_grid(y, d)

            # Store selected order
            self.selected_order = (p, d, q)

            # Train final model with selected parameters
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                model = ARIMA(y, order=self.selected_order)
                self.model = model.fit()

            logger.info(
                f"ARIMA model training completed. "
                f"Selected order: {self.selected_order}, "
                f"AIC: {self.model.aic:.2f}, "
                f"Data points: {len(y)}"
            )

        except InsufficientDataError:
            raise
        except Exception as e:
            # Fallback to ARIMA(1,1,1)
            logger.warning(f"Auto ARIMA failed: {e}. Falling back to ARIMA(1,1,1)")
            try:
                self.selected_order = (1, 1, 1)
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    model = ARIMA(y, order=self.selected_order)
                    self.model = model.fit()
                logger.info("Fallback ARIMA(1,1,1) training completed")
            except Exception as fallback_error:
                raise ModelTrainingError(
                    f"ARIMA training failed: {e}. Fallback also failed: {fallback_error}"
                )

    def forecast(self, periods: int) -> Dict:
        """Generate forecast for specified number of periods.

        Args:
            periods: Number of future periods (weeks) to forecast

        Returns:
            Dictionary containing:
                - predictions: List of forecasted values (integers)
                - lower_bound: List of lower confidence bounds
                - upper_bound: List of upper confidence bounds

        Raises:
            RuntimeError: If model has not been trained yet

        Example:
            >>> wrapper = ARIMAWrapper()
            >>> wrapper.train(historical_data)
            >>> forecast = wrapper.forecast(12)
            >>> print(forecast['predictions'])
            [150, 155, 148, ...]
        """
        if self.model is None:
            raise RuntimeError(
                "Model has not been trained yet. Call train() before forecast()."
            )

        logger.info(f"Generating forecast for {periods} periods...")

        try:
            # Generate forecast with confidence intervals
            forecast_result = self.model.forecast(steps=periods)

            # Get prediction interval using get_forecast
            forecast_obj = self.model.get_forecast(steps=periods)
            pred_int = forecast_obj.conf_int()

            # Extract predictions and bounds
            # forecast_result is already a numpy array
            if isinstance(forecast_result, np.ndarray):
                predictions = forecast_result
            else:
                predictions = forecast_result.values

            # conf_int() returns DataFrame or numpy array depending on statsmodels version
            if isinstance(pred_int, pd.DataFrame):
                lower_bound = pred_int.iloc[:, 0].values
                upper_bound = pred_int.iloc[:, 1].values
            else:
                # It's a numpy array
                lower_bound = pred_int[:, 0]
                upper_bound = pred_int[:, 1]

            # Round to integers and ensure positive
            predictions = np.maximum(np.round(predictions), 0).astype(int)
            lower_bound = np.maximum(np.round(lower_bound), 0).astype(int)
            upper_bound = np.maximum(np.round(upper_bound), 0).astype(int)

            result = {
                "predictions": predictions.tolist(),
                "lower_bound": lower_bound.tolist(),
                "upper_bound": upper_bound.tolist()
            }

            logger.info(
                f"Forecast generated: {len(result['predictions'])} periods, "
                f"Average prediction: {np.mean(predictions):.1f} units"
            )

            return result

        except Exception as e:
            raise ModelTrainingError(f"Forecast generation failed: {e}")

    def get_confidence(self, forecast_result: Dict) -> float:
        """Calculate confidence score from prediction intervals.

        Confidence is calculated as 1 - (average_interval_width / average_prediction).
        Narrow intervals indicate higher confidence in predictions.

        Args:
            forecast_result: Dictionary from forecast() containing predictions,
                           lower_bound, and upper_bound

        Returns:
            Confidence score between 0.0 (low confidence) and 1.0 (high confidence)

        Example:
            >>> forecast = wrapper.forecast(12)
            >>> confidence = wrapper.get_confidence(forecast)
            >>> print(f"Confidence: {confidence:.2f}")
            Confidence: 0.75
        """
        predictions = np.array(forecast_result['predictions'])
        lower_bound = np.array(forecast_result['lower_bound'])
        upper_bound = np.array(forecast_result['upper_bound'])

        # Calculate interval width
        interval_width = upper_bound - lower_bound

        # Calculate averages
        avg_width = interval_width.mean()
        avg_prediction = predictions.mean()

        # Avoid division by zero
        if avg_prediction == 0:
            logger.warning("Average prediction is zero. Returning 0.0 confidence.")
            return 0.0

        # Calculate confidence score
        confidence = 1.0 - (avg_width / avg_prediction)

        # Clip to [0.0, 1.0] range
        confidence = max(0.0, min(1.0, confidence))

        logger.info(f"Confidence score calculated: {confidence:.3f}")

        return confidence
