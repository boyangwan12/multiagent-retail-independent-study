"""
Demand Forecasting Tools for OpenAI Agents SDK

This module provides the run_demand_forecast tool that uses an ensemble
of Prophet and ARIMA models to generate demand forecasts.

STRUCTURE:
  Sections 1-5: Internal implementation (classes, helpers)
  Section 6: AGENT TOOL - run_demand_forecast() ← This is what the agent calls

SDK Pattern:
    @function_tool
    def run_demand_forecast(
        ctx: RunContextWrapper[ForecastingContext],
        category: str,
        forecast_horizon_weeks: int
    ) -> ForecastToolResult:
        ...
"""

# ============================================================================
# SECTION 1: Imports & Exceptions
# ============================================================================

from typing import Annotated, Dict, List, Optional, Tuple
import logging
import warnings
import sys
import io

import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from pydantic import BaseModel, Field, ConfigDict
from agents import function_tool, RunContextWrapper

# Import context type for type hints
from utils.context import ForecastingContext

logger = logging.getLogger("demand_tools")


# ============================================================================
# SECTION 2: Tool Output Schema
# ============================================================================

class ForecastToolResult(BaseModel):
    """
    Output from run_demand_forecast tool.

    Note: This is the TOOL output, not the AGENT output.
    The agent receives this from the tool, then constructs its own
    ForecastResult (with output_type) that includes explanation/reasoning.
    """
    model_config = ConfigDict(extra='forbid')

    total_demand: int = Field(description="Sum of all weekly forecasts")
    forecast_by_week: List[int] = Field(description="List of weekly demand predictions")
    safety_stock_pct: float = Field(
        description="Recommended safety stock percentage (0.10-0.50)",
        ge=0.10,
        le=0.50,
    )
    confidence: float = Field(
        description="Forecast confidence score (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    model_used: str = Field(
        description="Model(s) used: 'prophet_arima_ensemble', 'prophet', or 'arima'"
    )
    lower_bound: List[int] = Field(
        default_factory=list,
        description="Lower confidence bounds per week (5th percentile)",
    )
    upper_bound: List[int] = Field(
        default_factory=list,
        description="Upper confidence bounds per week (95th percentile)",
    )
    weekly_average: Optional[int] = Field(
        default=None,
        description="Average weekly demand",
    )
    data_quality: str = Field(
        default="good",
        description="Data quality: 'excellent', 'good', or 'poor'",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if forecasting failed",
    )


# ============================================================================
# SECTION 3: Custom Exceptions
# ============================================================================

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
# SECTION 4: ProphetWrapper - Seasonality forecasting
# ============================================================================

class ProphetWrapper:
    """Wrapper for Facebook Prophet time series forecasting."""

    def __init__(self, config: Optional[Dict] = None):
        self.model: Optional[Prophet] = None
        self.forecast_df: Optional[pd.DataFrame] = None
        self.config = config or {
            "seasonality_mode": "multiplicative",
            "yearly_seasonality": True,
            "weekly_seasonality": True,
            "daily_seasonality": False,
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 10.0,
        }

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train Prophet model on historical sales data."""
        required_columns = ["date", "quantity_sold"]
        if not all(col in historical_data.columns for col in required_columns):
            raise ValueError(f"Missing required columns: {required_columns}")

        if len(historical_data) < 26:
            raise InsufficientDataError(
                f"Prophet requires at least 26 weeks of data. Provided: {len(historical_data)}"
            )

        df_prophet = historical_data.copy()
        df_prophet = df_prophet.rename(columns={"date": "ds", "quantity_sold": "y"})

        if df_prophet["y"].isna().any():
            df_prophet["y"] = df_prophet["y"].ffill()

        if not pd.api.types.is_datetime64_any_dtype(df_prophet["ds"]):
            df_prophet["ds"] = pd.to_datetime(df_prophet["ds"])

        try:
            self.model = Prophet(
                seasonality_mode=self.config["seasonality_mode"],
                yearly_seasonality=self.config["yearly_seasonality"],
                weekly_seasonality=self.config["weekly_seasonality"],
                daily_seasonality=self.config["daily_seasonality"],
                changepoint_prior_scale=self.config["changepoint_prior_scale"],
                seasonality_prior_scale=self.config["seasonality_prior_scale"],
            )

            # Suppress Prophet's output
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            self.model.fit(df_prophet)
            sys.stdout = old_stdout

            logger.info(f"Prophet trained on {len(df_prophet)} data points")
        except Exception as e:
            raise ModelTrainingError(f"Prophet training failed: {str(e)}")

    def forecast(self, periods: int) -> Dict:
        """Generate forecast for specified number of periods."""
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        future = self.model.make_future_dataframe(periods=periods, freq="W")
        forecast_df = self.model.predict(future)
        forecast_future = forecast_df.tail(periods)
        self.forecast_df = forecast_future

        return {
            "predictions": [max(0, int(round(val))) for val in forecast_future["yhat"].tolist()],
            "lower_bound": [max(0, int(round(val))) for val in forecast_future["yhat_lower"].tolist()],
            "upper_bound": [max(0, int(round(val))) for val in forecast_future["yhat_upper"].tolist()],
            "dates": forecast_future["ds"].dt.strftime("%Y-%m-%d").tolist(),
        }

    def get_confidence(self, forecast_df: pd.DataFrame) -> float:
        """Calculate confidence from prediction intervals."""
        interval_width = forecast_df["yhat_upper"] - forecast_df["yhat_lower"]
        avg_width = interval_width.mean()
        avg_prediction = forecast_df["yhat"].mean()

        if avg_prediction == 0:
            return 0.0

        confidence = 1.0 - (avg_width / avg_prediction)
        return max(0.0, min(1.0, confidence))


# ============================================================================
# SECTION 5: ARIMAWrapper - Trend forecasting
# ============================================================================

class ARIMAWrapper:
    """Wrapper for ARIMA time series forecasting with auto parameter selection."""

    def __init__(self, config: Optional[Dict] = None):
        self.model = None
        self.forecast_result: Optional[Dict] = None
        self.config = config or {
            "start_p": 0,
            "max_p": 5,
            "start_q": 0,
            "max_q": 5,
            "stepwise": True,
        }
        self.selected_order: Optional[Tuple[int, int, int]] = None

    def _determine_d(self, y: np.ndarray) -> int:
        """Determine differencing order using ADF test."""
        try:
            result = adfuller(y, autolag="AIC")
            if result[1] < 0.05:
                return 0

            y_diff = np.diff(y)
            result = adfuller(y_diff, autolag="AIC")
            if result[1] < 0.05:
                return 1

            return 2
        except Exception:
            return 1

    def _select_parameters_stepwise(self, y: np.ndarray, d: int) -> Tuple[int, int, int]:
        """Select ARIMA parameters using stepwise search."""
        best_aic = np.inf
        best_order = (1, d, 1)

        search_space = [
            (0, d, 0), (1, d, 0), (0, d, 1), (1, d, 1),
            (2, d, 1), (1, d, 2), (2, d, 2),
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

        return best_order

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train ARIMA model using auto parameter selection."""
        required_columns = ["date", "quantity_sold"]
        if not all(col in historical_data.columns for col in required_columns):
            raise ValueError(f"Missing required columns: {required_columns}")

        if len(historical_data) < 26:
            raise InsufficientDataError(
                f"ARIMA requires at least 26 weeks of data. Provided: {len(historical_data)}"
            )

        y = historical_data["quantity_sold"].values

        if np.isnan(y).any():
            y = pd.Series(y).ffill().values

        try:
            d = self._determine_d(y)
            p, d, q = self._select_parameters_stepwise(y, d)
            self.selected_order = (p, d, q)

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                model = ARIMA(y, order=self.selected_order)
                self.model = model.fit()

            logger.info(f"ARIMA trained with order {self.selected_order}")
        except Exception as e:
            # Fallback to ARIMA(1,1,1)
            try:
                self.selected_order = (1, 1, 1)
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    model = ARIMA(y, order=self.selected_order)
                    self.model = model.fit()
            except Exception as fallback_error:
                raise ModelTrainingError(f"ARIMA training failed: {fallback_error}")

    def forecast(self, periods: int) -> Dict:
        """Generate forecast for specified number of periods."""
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        try:
            forecast_result = self.model.forecast(steps=periods)
            forecast_obj = self.model.get_forecast(steps=periods)
            pred_int = forecast_obj.conf_int()

            if isinstance(forecast_result, np.ndarray):
                predictions = forecast_result
            else:
                predictions = forecast_result.values

            if isinstance(pred_int, pd.DataFrame):
                lower_bound = pred_int.iloc[:, 0].values
                upper_bound = pred_int.iloc[:, 1].values
            else:
                lower_bound = pred_int[:, 0]
                upper_bound = pred_int[:, 1]

            predictions = np.maximum(np.round(predictions), 0).astype(int)
            lower_bound = np.maximum(np.round(lower_bound), 0).astype(int)
            upper_bound = np.maximum(np.round(upper_bound), 0).astype(int)

            result = {
                "predictions": predictions.tolist(),
                "lower_bound": lower_bound.tolist(),
                "upper_bound": upper_bound.tolist(),
            }
            self.forecast_result = result
            return result
        except Exception as e:
            raise ModelTrainingError(f"Forecast generation failed: {e}")

    def get_confidence(self, forecast_result: Dict) -> float:
        """Calculate confidence from prediction intervals."""
        predictions = np.array(forecast_result["predictions"])
        lower_bound = np.array(forecast_result["lower_bound"])
        upper_bound = np.array(forecast_result["upper_bound"])

        interval_width = upper_bound - lower_bound
        avg_width = interval_width.mean()
        avg_prediction = predictions.mean()

        if avg_prediction == 0:
            return 0.0

        confidence = 1.0 - (avg_width / avg_prediction)
        return max(0.0, min(1.0, confidence))


# ============================================================================
# SECTION 6: EnsembleForecaster - Combines Prophet + ARIMA
# ============================================================================

class EnsembleForecaster:
    """Ensemble forecaster combining Prophet and ARIMA."""

    def __init__(
        self,
        prophet_wrapper: Optional[ProphetWrapper] = None,
        arima_wrapper: Optional[ARIMAWrapper] = None,
        weights: Optional[Tuple[float, float]] = None,
    ):
        self.prophet = prophet_wrapper or ProphetWrapper()
        self.arima = arima_wrapper or ARIMAWrapper()
        self.weights = weights or (0.6, 0.4)  # 60% Prophet, 40% ARIMA
        self.model_used = "prophet_arima_ensemble"

    def train(self, historical_data: pd.DataFrame) -> None:
        """Train both models with fallback handling."""
        prophet_success = False
        arima_success = False

        try:
            self.prophet.train(historical_data)
            prophet_success = True
        except Exception as e:
            logger.warning(f"Prophet training failed: {e}")
            self.prophet = None

        try:
            self.arima.train(historical_data)
            arima_success = True
        except Exception as e:
            logger.warning(f"ARIMA training failed: {e}")
            self.arima = None

        if not prophet_success and not arima_success:
            raise ForecastingError("Both Prophet and ARIMA training failed")

        if prophet_success and arima_success:
            self.model_used = "prophet_arima_ensemble"
        elif prophet_success:
            self.model_used = "prophet"
        else:
            self.model_used = "arima"

    def _weighted_average(
        self, prophet_pred: List, arima_pred: List, weights: Tuple[float, float]
    ) -> List:
        """Compute weighted average of two forecasts."""
        prophet_arr = np.array(prophet_pred, dtype=float)
        arima_arr = np.array(arima_pred, dtype=float)

        prophet_arr = np.maximum(prophet_arr, 0)
        arima_arr = np.maximum(arima_arr, 0)

        w1, w2 = weights
        ensemble = w1 * prophet_arr + w2 * arima_arr
        return np.round(ensemble).astype(int).tolist()

    def forecast(self, periods: int) -> Dict:
        """Generate ensemble forecast with fallback logic."""
        prophet_forecast = None
        arima_forecast = None

        if self.prophet:
            try:
                prophet_forecast = self.prophet.forecast(periods)
            except Exception as e:
                logger.warning(f"Prophet forecast failed: {e}")

        if self.arima:
            try:
                arima_forecast = self.arima.forecast(periods)
            except Exception as e:
                logger.warning(f"ARIMA forecast failed: {e}")

        if prophet_forecast and arima_forecast:
            predictions = self._weighted_average(
                prophet_forecast["predictions"],
                arima_forecast["predictions"],
                self.weights,
            )
            confidence = min(
                self.prophet.get_confidence(self.prophet.forecast_df),
                self.arima.get_confidence(self.arima.forecast_result),
            )
            self.model_used = "prophet_arima_ensemble"

            lower_bound = self._weighted_average(
                prophet_forecast["lower_bound"],
                arima_forecast["lower_bound"],
                self.weights,
            )
            upper_bound = self._weighted_average(
                prophet_forecast["upper_bound"],
                arima_forecast["upper_bound"],
                self.weights,
            )

            return {
                "predictions": predictions,
                "confidence": confidence,
                "model_used": self.model_used,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
            }

        elif prophet_forecast:
            self.model_used = "prophet"
            return {
                "predictions": prophet_forecast["predictions"],
                "confidence": self.prophet.get_confidence(self.prophet.forecast_df),
                "model_used": self.model_used,
                "lower_bound": prophet_forecast["lower_bound"],
                "upper_bound": prophet_forecast["upper_bound"],
            }

        elif arima_forecast:
            self.model_used = "arima"
            return {
                "predictions": arima_forecast["predictions"],
                "confidence": self.arima.get_confidence(self.arima.forecast_result),
                "model_used": self.model_used,
                "lower_bound": arima_forecast["lower_bound"],
                "upper_bound": arima_forecast["upper_bound"],
            }

        else:
            raise ForecastingError("Both Prophet and ARIMA forecasts failed")


# ============================================================================
# SECTION 7: Data validation helpers
# ============================================================================

def validate_historical_data(data: pd.DataFrame, min_weeks: int = 26) -> bool:
    """Validate historical sales data."""
    required_columns = ["date", "quantity_sold"]

    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Missing required columns. Expected: {required_columns}")

    if len(data) < min_weeks:
        raise ValueError(
            f"Insufficient historical data. Need at least {min_weeks} weeks, got {len(data)}."
        )

    return True


def clean_historical_sales(data: pd.DataFrame) -> pd.DataFrame:
    """Clean historical sales data."""
    if data is None or len(data) == 0:
        return pd.DataFrame(columns=["date", "quantity_sold"])

    data = data.drop_duplicates(subset=["date"], keep="first")

    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"])
        data = data.sort_values("date")

    if "quantity_sold" in data.columns:
        data["quantity_sold"] = data["quantity_sold"].fillna(0)

    return data


def aggregate_to_weekly(data: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily sales data to weekly totals for Prophet training.

    Prophet expects weekly data when forecasting weekly periods.
    This ensures forecast output matches actual weekly sales.

    Args:
        data: DataFrame with 'date' and 'quantity_sold' columns (daily data)

    Returns:
        DataFrame with weekly aggregated data
    """
    if data is None or len(data) == 0:
        return pd.DataFrame(columns=["date", "quantity_sold"])

    df = data.copy()
    df["date"] = pd.to_datetime(df["date"])

    # Resample to weekly (Week ending Sunday)
    df = df.set_index("date")
    weekly = df.resample("W").sum().reset_index()

    logger.info(f"Aggregated {len(data)} daily records to {len(weekly)} weekly records")

    return weekly


# ============================================================================
# SECTION 8: AGENT TOOL - run_demand_forecast
# ============================================================================

@function_tool
def run_demand_forecast(
    ctx: RunContextWrapper[ForecastingContext],
    category: Annotated[str, "Product category name (e.g., 'Women's Dresses')"],
    forecast_horizon_weeks: Annotated[int, "Number of weeks to forecast (1-52, recommended 12)"],
) -> ForecastToolResult:
    """
    Generate demand forecasts using ensemble of Prophet and ARIMA models.

    Automatically fetches historical sales data from the context and generates
    weekly demand predictions with confidence scores and safety stock recommendations.

    The tool uses:
    - Prophet for seasonality patterns
    - ARIMA for trend patterns
    - Weighted ensemble (60% Prophet, 40% ARIMA) for final forecast

    Args:
        ctx: Run context with data_loader for fetching historical data
        category: Product category to forecast
        forecast_horizon_weeks: Number of weeks ahead to forecast

    Returns:
        ForecastToolResult with predictions, confidence, and safety stock recommendation
    """
    logger.info(
        f"run_demand_forecast called: category={category}, horizon={forecast_horizon_weeks}"
    )

    try:
        # Access data_loader from context
        data_loader = ctx.context.data_loader

        if data_loader is None:
            return ForecastToolResult(
                total_demand=0,
                forecast_by_week=[],
                safety_stock_pct=0.50,
                confidence=0.0,
                model_used="none",
                error="No data_loader in context",
            )

        # Fetch historical sales data
        historical_data = data_loader.get_historical_sales(category)

        if not historical_data or len(historical_data.get("date", [])) == 0:
            return ForecastToolResult(
                total_demand=0,
                forecast_by_week=[],
                safety_stock_pct=0.50,
                confidence=0.0,
                model_used="none",
                error=f"No historical sales data found for category: {category}",
            )

        # Convert to DataFrame
        df = pd.DataFrame(historical_data)

        # Clean daily data first
        df = clean_historical_sales(df)

        # Aggregate daily data to weekly for proper forecasting
        # This ensures forecast values match actual weekly sales totals
        df = aggregate_to_weekly(df)

        # Validate (now checking for 26 weeks minimum)
        validate_historical_data(df, min_weeks=26)

        # Train ensemble
        ensemble = EnsembleForecaster()
        ensemble.train(df)

        # Generate forecast
        forecast_result = ensemble.forecast(forecast_horizon_weeks)

        # Calculate totals
        total_demand = sum(forecast_result["predictions"])
        weekly_average = total_demand // forecast_horizon_weeks if forecast_horizon_weeks > 0 else 0

        # Calculate safety stock (inverse of confidence, clamped)
        confidence = forecast_result["confidence"]
        safety_stock_pct = 1.0 - confidence
        safety_stock_pct = max(0.10, min(0.50, safety_stock_pct))

        # Assess data quality
        data_quality = "excellent" if confidence >= 0.7 else "good" if confidence >= 0.5 else "poor"

        result = ForecastToolResult(
            total_demand=total_demand,
            forecast_by_week=forecast_result["predictions"],
            safety_stock_pct=round(safety_stock_pct, 2),
            confidence=round(confidence, 2),
            model_used=forecast_result["model_used"],
            lower_bound=forecast_result.get("lower_bound", []),
            upper_bound=forecast_result.get("upper_bound", []),
            weekly_average=weekly_average,
            data_quality=data_quality,
        )

        logger.info(
            f"Forecast complete: total={total_demand}, confidence={confidence:.2f}"
        )

        return result

    except InsufficientDataError as e:
        return ForecastToolResult(
            total_demand=0,
            forecast_by_week=[],
            safety_stock_pct=0.50,
            confidence=0.0,
            model_used="none",
            error=f"Insufficient data: {str(e)}",
        )

    except ForecastingError as e:
        return ForecastToolResult(
            total_demand=0,
            forecast_by_week=[],
            safety_stock_pct=0.50,
            confidence=0.0,
            model_used="none",
            error=f"Forecasting failed: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error in run_demand_forecast: {e}")
        return ForecastToolResult(
            total_demand=0,
            forecast_by_week=[],
            safety_stock_pct=0.50,
            confidence=0.0,
            model_used="none",
            error=f"Unexpected error: {str(e)}",
        )
