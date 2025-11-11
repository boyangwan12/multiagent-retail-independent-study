"""Ensemble Forecaster combining Prophet and ARIMA with weighted averaging.

This module provides an ensemble forecasting approach that combines Prophet and ARIMA
models to produce more accurate forecasts than either model alone. The ensemble uses
weighted averaging with dynamic weight calculation based on validation accuracy.
"""

from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
import logging
from app.ml.prophet_wrapper import ProphetWrapper, ModelTrainingError as ProphetError
from app.ml.arima_wrapper import ARIMAWrapper, ModelTrainingError as ARIMAError

logger = logging.getLogger("fashion_forecast")


class ForecastingError(Exception):
    """Raised when both Prophet and ARIMA forecasting fails."""
    pass


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
        except (ProphetError, Exception) as e:
            logger.warning(f"Prophet training failed: {e}")
            self.prophet = None

        # Train ARIMA
        try:
            self.arima.train(historical_data)
            logger.info("ARIMA trained successfully")
            arima_success = True
        except (ARIMAError, Exception) as e:
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

    def _calculate_dynamic_weights(
        self,
        validation_data: pd.DataFrame
    ) -> Tuple[float, float]:
        """Calculate optimal weights based on validation MAPE.

        Uses inverse MAPE weighting: models with lower MAPE get higher weight.

        Args:
            validation_data: DataFrame with columns ['date', 'quantity_sold']

        Returns:
            Tuple of (prophet_weight, arima_weight) summing to 1.0

        Raises:
            ValueError: If validation data is insufficient
        """
        if len(validation_data) < 5:
            logger.warning("Insufficient validation data. Using default weights.")
            return self.weights

        logger.info("Calculating dynamic weights based on validation MAPE...")

        try:
            # Generate forecasts on validation set
            prophet_forecast = self.prophet.forecast(len(validation_data))
            arima_forecast = self.arima.forecast(len(validation_data))

            # Get actual values
            actual = validation_data['quantity_sold'].values

            # Calculate MAPE for each model
            mape_prophet = self._calculate_mape(actual, prophet_forecast['predictions'])
            mape_arima = self._calculate_mape(actual, arima_forecast['predictions'])

            logger.info(f"Validation MAPE - Prophet: {mape_prophet:.2f}%, ARIMA: {mape_arima:.2f}%")

            # Avoid division by zero
            if mape_prophet == 0 or mape_arima == 0:
                logger.warning("Zero MAPE detected. Using default weights.")
                return self.weights

            # Calculate inverse weights
            inv_mape_prophet = 1.0 / mape_prophet
            inv_mape_arima = 1.0 / mape_arima
            total_inv_mape = inv_mape_prophet + inv_mape_arima

            w_prophet = inv_mape_prophet / total_inv_mape
            w_arima = inv_mape_arima / total_inv_mape

            # Ensure weights are in reasonable range [0.3, 0.7]
            w_prophet = max(0.3, min(0.7, w_prophet))
            w_arima = 1.0 - w_prophet

            logger.info(f"Dynamic weights calculated: Prophet={w_prophet:.2f}, ARIMA={w_arima:.2f}")

            return (w_prophet, w_arima)

        except Exception as e:
            logger.warning(f"Dynamic weight calculation failed: {e}. Using default weights.")
            return self.weights

    def _calculate_mape(self, actual: np.ndarray, predicted: list) -> float:
        """Calculate Mean Absolute Percentage Error.

        Args:
            actual: Array of actual values
            predicted: List of predicted values

        Returns:
            MAPE as percentage
        """
        actual = np.array(actual, dtype=float)
        predicted = np.array(predicted, dtype=float)

        # Avoid division by zero
        mask = actual != 0
        if not np.any(mask):
            return 0.0

        mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        return mape

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
                self.prophet.get_confidence(prophet_forecast),
                self.arima.get_confidence(arima_forecast)
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
            confidence = self.prophet.get_confidence(prophet_forecast)
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
            confidence = self.arima.get_confidence(arima_forecast)
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
