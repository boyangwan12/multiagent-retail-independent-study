"""ML Pipeline Module

This module contains placeholder implementations for:
- Prophet forecasting
- ARIMA forecasting
- K-means store clustering
- Ensemble forecasting (Prophet + ARIMA)
- Data preprocessing

Actual statistical models will be implemented in Phase 5.
For now, all functions return mock data matching the expected interface.
"""

from .prophet_model import run_prophet_forecast
from .arima_model import run_arima_forecast
from .clustering import cluster_stores, calculate_cluster_distribution
from .ensemble import forecast_category_demand
from .preprocessing import clean_historical_sales, validate_sales_data

__all__ = [
    "run_prophet_forecast",
    "run_arima_forecast",
    "cluster_stores",
    "calculate_cluster_distribution",
    "forecast_category_demand",
    "clean_historical_sales",
    "validate_sales_data",
]