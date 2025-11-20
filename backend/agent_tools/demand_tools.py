"""
Demand Forecasting Tools for OpenAI Agents SDK

STRUCTURE:
  Section 1-5: Internal implementation (classes, helpers)
  Section 6: AGENT TOOL - run_demand_forecast() ← This is what the agent calls

The agent tool (Section 6) uses everything from Sections 1-5 internally.
"""

# ============================================================================
# SECTION 1: Imports & Exceptions (INTERNAL)
# ============================================================================

from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
import logging
import warnings
import sys
import io
from agents import RunContextWrapper, function_tool
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger("fashion_forecast")


# ============================================================================
# Pydantic Models for Strict Type Schemas (required by @function_tool)
# ============================================================================

class HistoricalData(BaseModel):
    """Historical sales data for forecasting"""
    model_config = ConfigDict(extra='forbid')

    date: List[str] = Field(description="List of date strings in YYYY-MM-DD format")
    quantity_sold: List[int] = Field(description="List of quantities sold corresponding to each date")


class ForecastResult(BaseModel):
    """Forecast output from demand forecasting tool"""
    model_config = ConfigDict(extra='forbid')

    total_demand: int = Field(description="Sum of all weekly forecasts")
    forecast_by_week: List[int] = Field(description="List of weekly demand predictions")
    safety_stock_pct: float = Field(description="Safety stock percentage (0.10 to 0.50)")
    confidence: float = Field(description="Forecast confidence score (0.0 to 1.0)")
    model_used: str = Field(description="Which model(s) were used: 'prophet_arima_ensemble', 'prophet', or 'arima'")
    lower_bound: List[int] = Field(default_factory=list, description="Lower confidence interval bounds")
    upper_bound: List[int] = Field(default_factory=list, description="Upper confidence interval bounds")
    error: Optional[str] = Field(default=None, description="Error message if forecasting failed")


# Custom Exceptions
class InsufficientDataError(Exception):
    """Raised when insufficient historical data is provided for training."""
    pass


class ModelTrainingError(Exception):
    """Raised when model training fails."""
    pass


class ForecastingError(Exception):
    """Raised when both Prophet and ARIMA forecasting fails."""
    pass


# ============================================================================
# SECTION 2: ProphetWrapper - Seasonality forecasting (INTERNAL)
# ============================================================================

class ProphetWrapper:
    """Wrapper for Facebook Prophet time series forecasting.

    This class provides a simplified interface to Prophet for demand forecasting
    with pre-configured hyperparameters optimized for retail sales data.

    Attributes:
        model: Trained Prophet model instance
        config: Configuration dict for hyperparameters
        forecast_df: DataFrame from Prophet's predict() (for confidence calculation)
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize ProphetWrapper with optional configuration.

        Args:
            config: Optional configuration dictionary. If not provided, uses default
                   hyperparameters optimized for retail demand forecasting.
        """
        self.model: Optional[Prophet] = None
        self.forecast_df: Optional[pd.DataFrame] = None
        self.config = config or {
            'seasonality_mode': 'multiplicative',
            'yearly_seasonality': True,
            'weekly_seasonality': True,
            'daily_seasonality': False,
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0
        }
        logger.info("ProphetWrapper initialized with config: %s", self.config)

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train Prophet model on historical sales data.

        Args:
            historical_data: DataFrame with columns ['date', 'quantity_sold'].
                           Must contain at least 26 weeks (6 months) of data.

        Raises:
            InsufficientDataError: If data contains fewer than 26 weeks
            ModelTrainingError: If Prophet model training fails
            ValueError: If required columns are missing

        Example:
            >>> wrapper = ProphetWrapper()
            >>> df = pd.DataFrame({
            ...     'date': pd.date_range('2024-01-01', periods=52, freq='W'),
            ...     'quantity_sold': [100, 120, 115, ...]
            ... })
            >>> wrapper.train(df)
        """
        logger.info("Starting Prophet model training...")

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
                f"Prophet requires at least 26 weeks of data. "
                f"Provided: {len(historical_data)} weeks"
            )

        # Preprocess data for Prophet (rename columns to 'ds' and 'y')
        df_prophet = historical_data.copy()
        df_prophet = df_prophet.rename(columns={'date': 'ds', 'quantity_sold': 'y'})

        # Handle missing values (forward fill)
        if df_prophet['y'].isna().any():
            logger.warning("Missing values detected in sales data. Forward filling...")
            df_prophet['y'] = df_prophet['y'].ffill()

        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df_prophet['ds']):
            df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

        # Initialize Prophet with configured hyperparameters
        try:
            self.model = Prophet(
                seasonality_mode=self.config['seasonality_mode'],
                yearly_seasonality=self.config['yearly_seasonality'],
                weekly_seasonality=self.config['weekly_seasonality'],
                daily_seasonality=self.config['daily_seasonality'],
                changepoint_prior_scale=self.config['changepoint_prior_scale'],
                seasonality_prior_scale=self.config['seasonality_prior_scale']
            )

            # Suppress Prophet's informational messages
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            # Train the model
            self.model.fit(df_prophet)

            # Restore stdout
            sys.stdout = old_stdout

            logger.info(
                "Prophet model training completed. "
                f"Data points: {len(df_prophet)}, "
                f"Date range: {df_prophet['ds'].min()} to {df_prophet['ds'].max()}"
            )

        except Exception as e:
            raise ModelTrainingError(f"Prophet training failed: {str(e)}")

    def forecast(self, periods: int) -> Dict:
        """Generate forecast for specified number of periods.

        Args:
            periods: Number of future periods (weeks) to forecast

        Returns:
            Dictionary containing:
                - predictions: List of forecasted values
                - lower_bound: List of lower confidence bounds
                - upper_bound: List of upper confidence bounds
                - dates: List of forecast dates

        Raises:
            RuntimeError: If model has not been trained yet

        Example:
            >>> wrapper = ProphetWrapper()
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

        # Create future DataFrame
        future = self.model.make_future_dataframe(periods=periods, freq='W')

        # Generate predictions
        forecast_df = self.model.predict(future)

        # Extract only the future predictions (not historical)
        forecast_future = forecast_df.tail(periods)

        # Store the forecast DataFrame for confidence calculation
        self.forecast_df = forecast_future

        # Convert to dictionary format
        result = {
            "predictions": [int(round(val)) for val in forecast_future['yhat'].tolist()],
            "lower_bound": [int(round(val)) for val in forecast_future['yhat_lower'].tolist()],
            "upper_bound": [int(round(val)) for val in forecast_future['yhat_upper'].tolist()],
            "dates": forecast_future['ds'].dt.strftime('%Y-%m-%d').tolist()
        }

        logger.info(
            f"Forecast generated: {len(result['predictions'])} periods, "
            f"Average prediction: {sum(result['predictions']) / len(result['predictions']):.1f} units"
        )

        return result

    def get_confidence(self, forecast_df: pd.DataFrame) -> float:
        """Calculate confidence score from prediction intervals.

        Confidence is calculated as 1 - (average_interval_width / average_prediction).
        Narrow intervals indicate higher confidence in predictions.

        Args:
            forecast_df: DataFrame from Prophet's predict() containing yhat,
                        yhat_lower, and yhat_upper columns

        Returns:
            Confidence score between 0.0 (low confidence) and 1.0 (high confidence)

        Example:
            >>> forecast_df = model.predict(future)
            >>> confidence = wrapper.get_confidence(forecast_df)
            >>> print(f"Confidence: {confidence:.2f}")
            Confidence: 0.75
        """
        # Calculate interval width
        interval_width = forecast_df['yhat_upper'] - forecast_df['yhat_lower']

        # Calculate averages
        avg_width = interval_width.mean()
        avg_prediction = forecast_df['yhat'].mean()

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


# ============================================================================
# SECTION 3: ARIMAWrapper - Trend forecasting (INTERNAL)
# ============================================================================

class ARIMAWrapper:
    """Wrapper for ARIMA time series forecasting with Auto parameter selection.

    This class provides ARIMA forecasting with automatic parameter selection
    using AIC (Akaike Information Criterion) for optimal model fit.

    Attributes:
        model: Trained ARIMA model instance
        config: Configuration dict for hyperparameters
        selected_order: Tuple (p, d, q) of selected ARIMA parameters
        forecast_result: Forecast result dict (for confidence calculation)
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
        self.forecast_result: Optional[Dict] = None
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

            # Store the forecast result for confidence calculation
            self.forecast_result = result

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


# ============================================================================
# SECTION 4: EnsembleForecaster - Combines Prophet + ARIMA (INTERNAL)
# ============================================================================

class EnsembleForecaster:
    """Ensemble forecaster combining Prophet and ARIMA with weighted averaging.

    This class combines Prophet's seasonality strength with ARIMA's trend capture
    to produce more accurate forecasts. It supports dynamic weight calculation based
    on validation accuracy and fallback logic if one model fails.

    Attributes:
        prophet: ProphetWrapper instance
        arima: ARIMAWrapper instance
        weights: Tuple of (prophet_weight, arima_weight)
        model_used: String indicating which models were used ("prophet_arima_ensemble", "prophet", or "arima")
    """

    def __init__(
        self,
        prophet_wrapper: Optional[ProphetWrapper] = None,
        arima_wrapper: Optional[ARIMAWrapper] = None,
        weights: Optional[Tuple[float, float]] = None
    ):
        """Initialize EnsembleForecaster with model wrappers.

        Args:
            prophet_wrapper: ProphetWrapper instance (creates new if None)
            arima_wrapper: ARIMAWrapper instance (creates new if None)
            weights: Tuple of (prophet_weight, arima_weight). Default (0.6, 0.4)
        """
        self.prophet = prophet_wrapper or ProphetWrapper()
        self.arima = arima_wrapper or ARIMAWrapper()
        self.weights = weights or (0.6, 0.4)  # Default: 60% Prophet, 40% ARIMA
        self.model_used = "prophet_arima_ensemble"
        logger.info(
            "EnsembleForecaster initialized with weights: "
            f"Prophet={self.weights[0]:.2f}, ARIMA={self.weights[1]:.2f}"
        )

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train both Prophet and ARIMA models with fallback handling.

        Args:
            historical_data: DataFrame with columns ['date', 'quantity_sold']

        Raises:
            ForecastingError: If both Prophet and ARIMA training fails
        """
        logger.info("Starting ensemble model training...")

        prophet_success = False
        arima_success = False

        # Train Prophet
        try:
            self.prophet.train(historical_data)
            logger.info("Prophet trained successfully")
            prophet_success = True
        except Exception as e:
            logger.warning(f"Prophet training failed: {e}")
            self.prophet = None

        # Train ARIMA
        try:
            self.arima.train(historical_data)
            logger.info("ARIMA trained successfully")
            arima_success = True
        except Exception as e:
            logger.warning(f"ARIMA training failed: {e}")
            self.arima = None

        # Check if at least one model trained
        if not prophet_success and not arima_success:
            raise ForecastingError("Both Prophet and ARIMA training failed")

        # Update model_used based on which models succeeded
        if prophet_success and arima_success:
            self.model_used = "prophet_arima_ensemble"
            logger.info("Both models trained successfully - using ensemble")
        elif prophet_success:
            self.model_used = "prophet"
            logger.info("Only Prophet trained - will use Prophet fallback")
        else:
            self.model_used = "arima"
            logger.info("Only ARIMA trained - will use ARIMA fallback")

    def _weighted_average(
        self,
        prophet_pred: list,
        arima_pred: list,
        weights: Tuple[float, float]
    ) -> list:
        """Compute weighted average of two forecasts.

        Args:
            prophet_pred: Prophet predictions (list of integers)
            arima_pred: ARIMA predictions (list of integers)
            weights: Tuple of (prophet_weight, arima_weight)

        Returns:
            List of weighted average predictions (rounded to integers)

        Raises:
            ValueError: If inputs have different lengths or are invalid
        """
        if len(prophet_pred) != len(arima_pred):
            raise ValueError(
                f"Prediction lists must have same length. "
                f"Prophet: {len(prophet_pred)}, ARIMA: {len(arima_pred)}"
            )

        # Convert to numpy arrays
        prophet_arr = np.array(prophet_pred, dtype=float)
        arima_arr = np.array(arima_pred, dtype=float)

        # Validate non-negative
        if np.any(prophet_arr < 0) or np.any(arima_arr < 0):
            logger.warning("Negative predictions detected. Clipping to zero.")
            prophet_arr = np.maximum(prophet_arr, 0)
            arima_arr = np.maximum(arima_arr, 0)

        # Calculate weighted average
        w1, w2 = weights
        ensemble = w1 * prophet_arr + w2 * arima_arr

        # Round to integers
        ensemble = np.round(ensemble).astype(int)

        return ensemble.tolist()

    def forecast(self, periods: int) -> Dict:
        """Generate ensemble forecast with robustness and fallback logic.

        Args:
            periods: Number of periods (weeks) to forecast

        Returns:
            Dictionary containing:
                - predictions: List of forecasted values
                - confidence: Confidence score (0.0-1.0)
                - model_used: Which model(s) were used
                - lower_bound: Lower confidence bounds (if available)
                - upper_bound: Upper confidence bounds (if available)

        Raises:
            ForecastingError: If both models unavailable or all fail
        """
        logger.info(f"Generating {periods}-period ensemble forecast...")

        prophet_forecast = None
        arima_forecast = None

        # Try to generate Prophet forecast
        if self.prophet:
            try:
                prophet_forecast = self.prophet.forecast(periods)
                logger.info("Prophet forecast generated successfully")
            except Exception as e:
                logger.warning(f"Prophet forecast failed: {e}")

        # Try to generate ARIMA forecast
        if self.arima:
            try:
                arima_forecast = self.arima.forecast(periods)
                logger.info("ARIMA forecast generated successfully")
            except Exception as e:
                logger.warning(f"ARIMA forecast failed: {e}")

        # Implement fallback logic
        if prophet_forecast and arima_forecast:
            # Ensemble: use both models
            predictions = self._weighted_average(
                prophet_forecast['predictions'],
                arima_forecast['predictions'],
                self.weights
            )
            confidence = min(
                self.prophet.get_confidence(self.prophet.forecast_df),
                self.arima.get_confidence(self.arima.forecast_result)
            )
            self.model_used = "prophet_arima_ensemble"
            logger.info("Using ensemble (both models available)")

            # Return ensemble result with bounds
            lower_bound = self._weighted_average(
                prophet_forecast['lower_bound'],
                arima_forecast['lower_bound'],
                self.weights
            )
            upper_bound = self._weighted_average(
                prophet_forecast['upper_bound'],
                arima_forecast['upper_bound'],
                self.weights
            )

            return {
                "predictions": predictions,
                "confidence": confidence,
                "model_used": self.model_used,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            }

        elif prophet_forecast:
            # Prophet only fallback
            predictions = prophet_forecast['predictions']
            confidence = self.prophet.get_confidence(self.prophet.forecast_df)
            self.model_used = "prophet"
            logger.info("Using Prophet only (ARIMA unavailable)")

            return {
                "predictions": predictions,
                "confidence": confidence,
                "model_used": self.model_used,
                "lower_bound": prophet_forecast['lower_bound'],
                "upper_bound": prophet_forecast['upper_bound']
            }

        elif arima_forecast:
            # ARIMA only fallback
            predictions = arima_forecast['predictions']
            confidence = self.arima.get_confidence(self.arima.forecast_result)
            self.model_used = "arima"
            logger.info("Using ARIMA only (Prophet unavailable)")

            return {
                "predictions": predictions,
                "confidence": confidence,
                "model_used": self.model_used,
                "lower_bound": arima_forecast['lower_bound'],
                "upper_bound": arima_forecast['upper_bound']
            }

        else:
            # Both failed
            raise ForecastingError(
                "Both Prophet and ARIMA forecasts failed. Cannot generate ensemble forecast."
            )


# ============================================================================
# SECTION 5: Data validation & cleaning helpers (INTERNAL)
# ============================================================================

def validate_historical_data(data: pd.DataFrame, min_weeks: int = 26) -> bool:
    """Validate historical sales data.

    Args:
        data: DataFrame with sales data
        min_weeks: Minimum number of weeks required (default: 26)

    Returns:
        True if validation passes

    Raises:
        ValueError: If validation fails
    """
    required_columns = ['date', 'quantity_sold']

    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Missing required columns. Expected: {required_columns}")

    if len(data) < min_weeks:
        raise ValueError(f"Insufficient historical data. Need at least {min_weeks} weeks, got {len(data)}.")

    if data['quantity_sold'].isna().any():
        raise ValueError("Missing values in 'quantity_sold' column.")

    return True


def clean_historical_sales(data: pd.DataFrame) -> pd.DataFrame:
    """Clean historical sales data (handle missing values, duplicates).

    Args:
        data: Raw sales DataFrame

    Returns:
        Cleaned DataFrame
    """
    if data is None or len(data) == 0:
        return pd.DataFrame(columns=['date', 'quantity_sold'])

    # Remove duplicates
    data = data.drop_duplicates(subset=['date'], keep='first')

    # Ensure date is datetime
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')

    # Fill missing quantity with 0
    if 'quantity_sold' in data.columns:
        data['quantity_sold'] = data['quantity_sold'].fillna(0)

    return data


# ============================================================================
# SECTION 6: AGENT TOOL ← The function the Demand Agent calls
# ============================================================================
# Everything above (Sections 1-5) is internal implementation.
# THIS is the actual tool registered with the agent.

@function_tool
def run_demand_forecast(
    ctx: RunContextWrapper,
    category: str,
    forecast_horizon_weeks: int
) -> ForecastResult:
    """
    Generate demand forecasts using ensemble of Prophet and ARIMA models.

    Automatically fetches historical sales data from the context and generates
    weekly demand predictions with confidence scores and safety stock recommendations.

    Args:
        category: Product category name (e.g., "Women's Dresses", "Men's Shirts")
        forecast_horizon_weeks: Number of weeks to forecast ahead (typically 1-52, recommended 12)

    Returns:
        ForecastResult containing weekly predictions, confidence scores, and safety stock recommendations

    Example:
        The agent calls: run_demand_forecast("Women's Dresses", 12)
        The tool automatically fetches historical data and returns forecasts.
    """
    logger.info(f"Starting demand forecast for category: {category}, horizon: {forecast_horizon_weeks} weeks")

    try:
        # Access data_loader from context
        data_loader = ctx.context.data_loader

        if data_loader is None:
            return ForecastResult(
                total_demand=0,
                forecast_by_week=[],
                safety_stock_pct=0.50,
                confidence=0.0,
                model_used="none",
                error="No data_loader in context. Context must contain a data_loader instance."
            )

        # Fetch historical sales data for this category
        logger.info(f"Fetching historical sales data for category: {category}")
        historical_data = data_loader.get_historical_sales(category)

        if not historical_data or len(historical_data.get('date', [])) == 0:
            return ForecastResult(
                total_demand=0,
                forecast_by_week=[],
                safety_stock_pct=0.50,
                confidence=0.0,
                model_used="none",
                error=f"No historical sales data found for category: {category}"
            )

        # Convert dictionary to DataFrame
        df = pd.DataFrame(historical_data)

        # Validate data
        validate_historical_data(df, min_weeks=26)

        # Clean data
        df = clean_historical_sales(df)

        # Initialize ensemble forecaster
        ensemble = EnsembleForecaster()

        # Train models
        ensemble.train(df)

        # Generate forecast
        forecast_result = ensemble.forecast(forecast_horizon_weeks)

        # Calculate total demand
        total_demand = sum(forecast_result['predictions'])

        # Calculate safety stock percentage
        confidence = forecast_result['confidence']
        safety_stock_pct = 1.0 - confidence
        safety_stock_pct = max(0.10, min(0.50, safety_stock_pct))  # Clamp to [10%, 50%]

        # Build result using Pydantic model
        result = ForecastResult(
            total_demand=total_demand,
            forecast_by_week=forecast_result['predictions'],
            safety_stock_pct=round(safety_stock_pct, 2),
            confidence=round(confidence, 2),
            model_used=forecast_result['model_used'],
            lower_bound=forecast_result.get('lower_bound', []),
            upper_bound=forecast_result.get('upper_bound', [])
        )

        logger.info(
            f"Forecast complete: total_demand={total_demand}, "
            f"confidence={confidence:.2f}, safety_stock={safety_stock_pct:.2%}"
        )

        return result

    except InsufficientDataError as e:
        error_msg = f"Insufficient data: {str(e)}"
        logger.error(error_msg)
        return ForecastResult(
            total_demand=0,
            forecast_by_week=[],
            safety_stock_pct=0.50,
            confidence=0.0,
            model_used="none",
            error=error_msg
        )

    except ForecastingError as e:
        error_msg = f"Forecasting failed: {str(e)}"
        logger.error(error_msg)
        return ForecastResult(
            total_demand=0,
            forecast_by_week=[],
            safety_stock_pct=0.50,
            confidence=0.0,
            model_used="none",
            error=error_msg
        )

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return ForecastResult(
            total_demand=0,
            forecast_by_week=[],
            safety_stock_pct=0.50,
            confidence=0.0,
            model_used="none",
            error=error_msg
        )
