"""Prophet Wrapper for Time Series Forecasting

This module provides a wrapper around Facebook Prophet for demand forecasting.
Prophet is used to capture seasonality patterns (weekly, yearly) in retail sales data.
"""

from prophet import Prophet
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger("fashion_forecast")


class InsufficientDataError(Exception):
    """Raised when insufficient historical data is provided for training."""
    pass


class ModelTrainingError(Exception):
    """Raised when Prophet model training fails."""
    pass


class ProphetWrapper:
    """Wrapper for Facebook Prophet time series forecasting.

    This class provides a simplified interface to Prophet for demand forecasting
    with pre-configured hyperparameters optimized for retail sales data.

    Attributes:
        model: Trained Prophet model instance
        config: Configuration dict for hyperparameters
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize ProphetWrapper with optional configuration.

        Args:
            config: Optional configuration dictionary. If not provided, uses default
                   hyperparameters optimized for retail demand forecasting.
        """
        self.model: Optional[Prophet] = None
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
            import sys
            import io
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
