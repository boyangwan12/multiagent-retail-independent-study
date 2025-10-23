# Story: ML Pipeline Scaffolding (Prophet, ARIMA, K-Means Placeholders)

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-011
**Status:** Ready for Review
**Estimate:** 3 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-002 (Database Schema & Models)

---

## Story

As a backend developer,
I want to create the ML pipeline folder structure with placeholder models for Prophet, ARIMA, and K-means clustering,
So that the Demand Agent (Phase 5) has a well-defined interface for forecasting and allocation logic, even though actual ML implementation happens later.

**Business Value:** Establishes the ML architecture foundation without blocking backend development. Placeholder models return mock data matching the expected interface, allowing end-to-end workflow testing while actual statistical models are implemented in Phase 5.

**Epic Context:** This is Task 11 of 14 in Phase 3. It decouples backend architecture from ML complexity, enabling parallel development. The interfaces defined here will be consumed by agents in Phases 4-7.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `backend/app/ml/` folder created with 5 modules
2. ✅ `prophet_model.py` returns mock forecast (8000 units total, 12-week curve)
3. ✅ `arima_model.py` returns mock forecast (7500 units total)
4. ✅ `clustering.py` returns 3 mock clusters (fashion_forward, mainstream, value_conscious)
5. ✅ `ensemble.py` combines Prophet + ARIMA forecasts (simple average)
6. ✅ `preprocessing.py` has data cleaning utilities (handle missing dates, outliers)
7. ✅ All functions accept standard input formats (pandas DataFrames)
8. ✅ All functions return structured dicts matching Pydantic schemas

### Quality Requirements

9. ✅ Type hints on all function signatures
10. ✅ Docstrings explain inputs, outputs, and return format
11. ✅ Mock data is realistic (no negative values, reasonable distributions)
12. ✅ Functions run without errors on empty/minimal DataFrames
13. ✅ Interface documented for Phase 5 implementation
14. ✅ Clustering returns exactly 3 clusters (MVP requirement)

---

## Tasks

### Task 1: Create ML Module Structure

**Create folder structure:**
```bash
backend/app/ml/
├── __init__.py          # Export all functions
├── prophet_model.py     # Prophet placeholder
├── arima_model.py       # ARIMA placeholder
├── clustering.py        # K-means clustering placeholder
├── ensemble.py          # Ensemble forecasting
└── preprocessing.py     # Data cleaning utilities
```

**`backend/app/ml/__init__.py`:**
```python
"""
ML Pipeline Module

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
```

---

### Task 2: Implement Prophet Model Placeholder

**`backend/app/ml/prophet_model.py`:**
```python
"""
Prophet Forecasting Model (Placeholder)

Phase 3: Returns mock forecast data with realistic weekly distribution
Phase 5: Will implement actual Prophet model with seasonality
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any


def run_prophet_forecast(
    historical_sales: pd.DataFrame,
    weeks: int = 12,
    season_start_date: str = None
) -> Dict[str, Any]:
    """
    Run Prophet forecasting model (PLACEHOLDER).

    Args:
        historical_sales: DataFrame with columns ['date', 'units_sold']
        weeks: Forecast horizon in weeks
        season_start_date: ISO 8601 date string (e.g., "2025-03-03")

    Returns:
        dict with:
            - total_season_demand: int (total units forecasted)
            - weekly_demand_curve: list[dict] (week-by-week breakdown)
            - confidence_interval: dict (lower/upper bounds - Phase 5)
            - model_metadata: dict (parameters used)

    Phase 5 Implementation:
        - Load Prophet library
        - Fit on historical_sales['ds', 'y']
        - Use seasonality='weekly', growth='linear'
        - Apply country holidays (US)
        - Return actual forecast with confidence intervals
    """
    # Phase 3: Mock implementation
    if season_start_date is None:
        # Default to next Monday
        today = datetime.now()
        days_ahead = 7 - today.weekday()  # Days until next Monday
        season_start_date = (today + timedelta(days=days_ahead)).date().isoformat()

    # Mock total: 8000 units over 12 weeks
    total_demand = 8000

    # Generate weekly curve with realistic distribution (higher at start)
    weekly_curve = []
    start_date = datetime.fromisoformat(season_start_date)

    # Distribution: 15%, 12%, 10%, 9%, 8%, 7%, 6%, 5%, 5%, 4%, 4%, 3% (totals ~88%)
    # Scale to 100%
    percentages = [0.17, 0.14, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05, 0.04, 0.03]

    for week_num in range(1, weeks + 1):
        week_start = start_date + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6)

        weekly_units = int(total_demand * percentages[week_num - 1])

        weekly_curve.append({
            "week_number": week_num,
            "week_start_date": week_start.strftime("%Y-%m-%d"),
            "week_end_date": week_end.strftime("%Y-%m-%d"),
            "forecasted_units": weekly_units,
            "confidence_lower": int(weekly_units * 0.85),  # Mock ±15%
            "confidence_upper": int(weekly_units * 1.15)
        })

    return {
        "total_season_demand": total_demand,
        "weekly_demand_curve": weekly_curve,
        "confidence_interval": {
            "lower": int(total_demand * 0.85),
            "upper": int(total_demand * 1.15)
        },
        "model_metadata": {
            "model": "prophet_placeholder",
            "seasonality": "weekly",
            "growth": "linear",
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 10.0,
            "note": "Mock data for Phase 3. Actual Prophet model in Phase 5."
        }
    }


def validate_prophet_input(historical_sales: pd.DataFrame) -> bool:
    """
    Validate historical sales data for Prophet.

    Requirements:
        - Must have 'date' and 'units_sold' columns
        - At least 52 weeks (1 year) of data
        - No missing values in critical columns

    Phase 5: Add more sophisticated validation (check for outliers, gaps)
    """
    required_columns = ['date', 'units_sold']

    if not all(col in historical_sales.columns for col in required_columns):
        raise ValueError(f"Missing required columns. Expected: {required_columns}")

    if len(historical_sales) < 52:
        raise ValueError("Insufficient historical data. Need at least 52 weeks (1 year).")

    if historical_sales['units_sold'].isna().any():
        raise ValueError("Missing values in 'units_sold' column.")

    return True
```

**Expected Output (Mock):**
```json
{
  "total_season_demand": 8000,
  "weekly_demand_curve": [
    {"week_number": 1, "week_start_date": "2025-03-03", "week_end_date": "2025-03-09", "forecasted_units": 1360, "confidence_lower": 1156, "confidence_upper": 1564},
    {"week_number": 2, "week_start_date": "2025-03-10", "week_end_date": "2025-03-16", "forecasted_units": 1120, "confidence_lower": 952, "confidence_upper": 1288},
    ...
  ],
  "model_metadata": {"model": "prophet_placeholder", "note": "Mock data for Phase 3"}
}
```

---

### Task 3: Implement ARIMA Model Placeholder

**`backend/app/ml/arima_model.py`:**
```python
"""
ARIMA Forecasting Model (Placeholder)

Phase 3: Returns mock forecast data slightly lower than Prophet (7500 units)
Phase 5: Will implement auto_arima with seasonal configuration
"""

import pandas as pd
from typing import Dict, Any


def run_arima_forecast(
    historical_sales: pd.DataFrame,
    weeks: int = 12
) -> Dict[str, Any]:
    """
    Run ARIMA forecasting model (PLACEHOLDER).

    Args:
        historical_sales: DataFrame with columns ['date', 'units_sold']
        weeks: Forecast horizon in weeks

    Returns:
        dict with:
            - total_season_demand: int
            - arima_order: tuple (p, d, q)
            - seasonal_order: tuple (P, D, Q, m)
            - aic: float (Akaike Information Criterion)

    Phase 5 Implementation:
        - Use pmdarima.auto_arima()
        - Configure seasonal=True, m=52 (weekly data, 52 weeks/year)
        - Fit on historical_sales['units_sold']
        - Return forecast with confidence intervals
    """
    # Phase 3: Mock implementation
    total_demand = 7500  # Slightly different from Prophet to test ensemble

    return {
        "total_season_demand": total_demand,
        "arima_order": (1, 1, 1),  # Mock (p, d, q)
        "seasonal_order": (1, 1, 1, 52),  # Mock (P, D, Q, m)
        "aic": 1234.56,  # Mock AIC score
        "model_metadata": {
            "model": "arima_placeholder",
            "auto_arima_used": True,
            "stepwise": True,
            "note": "Mock data for Phase 3. Actual ARIMA model in Phase 5."
        }
    }


def validate_arima_input(historical_sales: pd.DataFrame) -> bool:
    """
    Validate historical sales data for ARIMA.

    Requirements same as Prophet (52+ weeks, no missing values)
    """
    if 'units_sold' not in historical_sales.columns:
        raise ValueError("Missing 'units_sold' column")

    if len(historical_sales) < 52:
        raise ValueError("Need at least 52 weeks of data for seasonal ARIMA")

    return True
```

**Expected Output (Mock):**
```json
{
  "total_season_demand": 7500,
  "arima_order": [1, 1, 1],
  "seasonal_order": [1, 1, 1, 52],
  "aic": 1234.56,
  "model_metadata": {"model": "arima_placeholder", "note": "Mock data for Phase 3"}
}
```

---

### Task 4: Implement Clustering Placeholder

**`backend/app/ml/clustering.py`:**
```python
"""
Store Clustering (K-Means) - Placeholder

Phase 3: Returns 3 hardcoded clusters based on fashion_tier
Phase 5: Will implement K-means with 7 features + StandardScaler
"""

import pandas as pd
from typing import Dict, List, Any


def cluster_stores(
    stores_df: pd.DataFrame,
    n_clusters: int = 3
) -> pd.DataFrame:
    """
    Cluster stores using K-means (PLACEHOLDER).

    Args:
        stores_df: DataFrame with store attributes
        n_clusters: Number of clusters (default 3 for MVP)

    Returns:
        DataFrame with added 'cluster_id' and 'cluster_name' columns

    Phase 5 Implementation:
        - Encode categorical features (location_tier, fashion_tier, store_format, region)
        - Use 7 features: store_size_sqft, median_income, location_tier_encoded,
          fashion_tier_encoded, avg_weekly_sales_12mo, store_format_encoded, region_encoded
        - Apply StandardScaler (required for K-means)
        - Run KMeans(n_clusters=3, init='k-means++', random_state=42)
        - Assign meaningful cluster names based on characteristics
    """
    # Phase 3: Mock implementation - assign clusters based on fashion_tier
    stores_df = stores_df.copy()

    # Simple rule-based clustering for Phase 3
    def assign_cluster(row):
        if row['fashion_tier'] == 'PREMIUM':
            return 'fashion_forward'
        elif row['fashion_tier'] == 'MAINSTREAM':
            return 'mainstream'
        else:
            return 'value_conscious'

    stores_df['cluster_id'] = stores_df.apply(assign_cluster, axis=1)
    stores_df['cluster_name'] = stores_df['cluster_id'].str.replace('_', ' ').str.title()

    return stores_df


def calculate_cluster_distribution(
    stores_df: pd.DataFrame,
    total_demand: int
) -> List[Dict[str, Any]]:
    """
    Calculate how demand splits across clusters.

    Args:
        stores_df: DataFrame with 'cluster_id' column
        total_demand: Total forecasted units

    Returns:
        list[dict] with cluster allocations

    Logic:
        - Count stores per cluster
        - Sum historical sales per cluster
        - Calculate allocation percentage (based on historical sales)
        - Apply percentage to total_demand
    """
    # Count stores per cluster
    cluster_counts = stores_df.groupby('cluster_id').size().to_dict()

    # Mock: Use avg_weekly_sales_12mo if available, else equal distribution
    if 'avg_weekly_sales_12mo' in stores_df.columns:
        cluster_sales = stores_df.groupby('cluster_id')['avg_weekly_sales_12mo'].sum()
        total_sales = cluster_sales.sum()
        cluster_pcts = cluster_sales / total_sales
    else:
        # Equal distribution if no historical data
        cluster_pcts = pd.Series({
            'fashion_forward': 0.40,
            'mainstream': 0.35,
            'value_conscious': 0.25
        })

    # Build distribution
    distribution = []
    for cluster_id in ['fashion_forward', 'mainstream', 'value_conscious']:
        pct = cluster_pcts.get(cluster_id, 0.33)
        distribution.append({
            'cluster_id': cluster_id,
            'cluster_name': cluster_id.replace('_', ' ').title(),
            'allocation_percentage': float(pct),
            'total_units': int(total_demand * pct),
            'store_count': cluster_counts.get(cluster_id, 0)
        })

    return distribution


def get_cluster_metadata() -> Dict[str, Any]:
    """
    Return metadata about clustering configuration.

    Phase 5: Include actual K-means parameters, feature importance, cluster centers
    """
    return {
        "n_clusters": 3,
        "cluster_names": ["fashion_forward", "mainstream", "value_conscious"],
        "features_used": [
            "store_size_sqft",
            "median_income",
            "location_tier_encoded",
            "fashion_tier_encoded",
            "avg_weekly_sales_12mo",
            "store_format_encoded",
            "region_encoded"
        ],
        "algorithm": "k-means++",
        "note": "Phase 3: Hardcoded clusters. Phase 5: Actual K-means with StandardScaler."
    }
```

**Expected Output (Mock):**
```json
[
  {
    "cluster_id": "fashion_forward",
    "cluster_name": "Fashion Forward",
    "allocation_percentage": 0.40,
    "total_units": 3200,
    "store_count": 15
  },
  {
    "cluster_id": "mainstream",
    "cluster_name": "Mainstream",
    "allocation_percentage": 0.35,
    "total_units": 2800,
    "store_count": 20
  },
  {
    "cluster_id": "value_conscious",
    "cluster_name": "Value Conscious",
    "allocation_percentage": 0.25,
    "total_units": 2000,
    "store_count": 15
  }
]
```

---

### Task 5: Implement Ensemble Forecasting

**`backend/app/ml/ensemble.py`:**
```python
"""
Ensemble Forecasting (Prophet + ARIMA)

Combines Prophet and ARIMA forecasts using simple averaging.
Phase 5: Could add weighted averaging based on confidence scores.
"""

import pandas as pd
from typing import Dict, Any

from .prophet_model import run_prophet_forecast
from .arima_model import run_arima_forecast


def forecast_category_demand(
    historical_sales: pd.DataFrame,
    weeks: int = 12,
    season_start_date: str = None
) -> Dict[str, Any]:
    """
    Ensemble forecast: Average Prophet + ARIMA results.

    Args:
        historical_sales: DataFrame with ['date', 'units_sold']
        weeks: Forecast horizon
        season_start_date: ISO 8601 date string

    Returns:
        dict with:
            - total_season_demand: int (ensemble average)
            - prophet_forecast: int (Prophet result)
            - arima_forecast: int (ARIMA result)
            - weekly_demand_curve: list[dict] (from Prophet)
            - forecasting_method: str ("ensemble_prophet_arima")
            - models_used: list[str]

    Design Decisions:
        - Simple average (no confidence weighting in Phase 3)
        - Use Prophet's weekly curve for distribution
        - Store both model outputs for post-hoc analysis
    """
    # Run both models in parallel (async in Phase 5)
    prophet_result = run_prophet_forecast(historical_sales, weeks, season_start_date)
    arima_result = run_arima_forecast(historical_sales, weeks)

    # Simple average
    prophet_total = prophet_result['total_season_demand']
    arima_total = arima_result['total_season_demand']
    ensemble_total = (prophet_total + arima_total) // 2

    # Use Prophet's weekly curve, scaled to ensemble total
    weekly_curve = prophet_result['weekly_demand_curve']
    scale_factor = ensemble_total / prophet_total

    for week in weekly_curve:
        week['forecasted_units'] = int(week['forecasted_units'] * scale_factor)
        week['confidence_lower'] = int(week['confidence_lower'] * scale_factor)
        week['confidence_upper'] = int(week['confidence_upper'] * scale_factor)

    return {
        "total_season_demand": ensemble_total,
        "prophet_forecast": prophet_total,
        "arima_forecast": arima_total,
        "weekly_demand_curve": weekly_curve,
        "forecasting_method": "ensemble_prophet_arima",
        "models_used": ["prophet", "arima"],
        "ensemble_metadata": {
            "averaging_method": "simple_average",
            "prophet_weight": 0.5,
            "arima_weight": 0.5,
            "note": "Phase 5: Could add confidence-weighted averaging"
        }
    }


def calculate_forecast_variance(
    prophet_forecast: int,
    arima_forecast: int
) -> Dict[str, Any]:
    """
    Calculate variance between two models.

    High variance (>20%) may indicate uncertainty or data issues.
    """
    diff = abs(prophet_forecast - arima_forecast)
    avg = (prophet_forecast + arima_forecast) / 2
    variance_pct = diff / avg if avg > 0 else 0

    return {
        "prophet_forecast": prophet_forecast,
        "arima_forecast": arima_forecast,
        "difference": diff,
        "variance_pct": variance_pct,
        "high_variance": variance_pct > 0.20  # Flag if >20% difference
    }
```

**Expected Output (Mock):**
```json
{
  "total_season_demand": 7750,  // (8000 + 7500) / 2
  "prophet_forecast": 8000,
  "arima_forecast": 7500,
  "weekly_demand_curve": [...],  // Prophet's curve, scaled
  "forecasting_method": "ensemble_prophet_arima",
  "models_used": ["prophet", "arima"]
}
```

---

### Task 6: Implement Data Preprocessing Utilities

**`backend/app/ml/preprocessing.py`:**
```python
"""
Data Preprocessing Utilities

Functions for cleaning and validating historical sales data before forecasting.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple


def clean_historical_sales(
    df: pd.DataFrame,
    date_column: str = 'date',
    value_column: str = 'units_sold'
) -> pd.DataFrame:
    """
    Clean historical sales data.

    Steps:
        1. Convert date column to datetime
        2. Sort by date
        3. Remove duplicates
        4. Fill missing dates with 0 (no sales)
        5. Handle outliers (cap at 99th percentile)
        6. Remove negative values

    Args:
        df: Raw sales DataFrame
        date_column: Name of date column
        value_column: Name of sales column

    Returns:
        Cleaned DataFrame
    """
    df = df.copy()

    # 1. Convert date to datetime
    df[date_column] = pd.to_datetime(df[date_column])

    # 2. Sort by date
    df = df.sort_values(date_column)

    # 3. Remove duplicates (keep last)
    df = df.drop_duplicates(subset=[date_column], keep='last')

    # 4. Fill missing dates
    date_range = pd.date_range(
        start=df[date_column].min(),
        end=df[date_column].max(),
        freq='W-MON'  # Weekly data starting Monday
    )
    df = df.set_index(date_column).reindex(date_range, fill_value=0).reset_index()
    df.rename(columns={'index': date_column}, inplace=True)

    # 5. Handle outliers (cap at 99th percentile)
    p99 = df[value_column].quantile(0.99)
    df[value_column] = df[value_column].clip(upper=p99)

    # 6. Remove negative values
    df[value_column] = df[value_column].clip(lower=0)

    return df


def validate_sales_data(
    df: pd.DataFrame,
    min_weeks: int = 52
) -> Tuple[bool, str]:
    """
    Validate historical sales data.

    Requirements:
        - At least min_weeks of data
        - No NaN values
        - No negative values
        - Date column is datetime type

    Returns:
        (is_valid: bool, error_message: str)
    """
    # Check row count
    if len(df) < min_weeks:
        return False, f"Insufficient data: {len(df)} weeks, need {min_weeks}"

    # Check for NaN
    if df['units_sold'].isna().any():
        return False, "Missing values in 'units_sold' column"

    # Check for negatives
    if (df['units_sold'] < 0).any():
        return False, "Negative values found in 'units_sold'"

    # Check date type
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        return False, "'date' column must be datetime type"

    return True, "Data validation passed"


def aggregate_to_weekly(
    df: pd.DataFrame,
    date_column: str = 'date',
    value_column: str = 'units_sold',
    week_start: str = 'MON'
) -> pd.DataFrame:
    """
    Aggregate daily sales to weekly.

    Args:
        df: Daily sales DataFrame
        date_column: Name of date column
        value_column: Name of sales column
        week_start: Start of week ('MON', 'SUN')

    Returns:
        Weekly aggregated DataFrame
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])

    # Set date as index
    df = df.set_index(date_column)

    # Resample to weekly (sum sales per week)
    weekly = df[value_column].resample(f'W-{week_start}').sum().reset_index()
    weekly.columns = [date_column, value_column]

    return weekly


def detect_seasonality(
    df: pd.DataFrame,
    value_column: str = 'units_sold'
) -> dict:
    """
    Detect seasonality in sales data.

    Returns:
        dict with seasonality indicators (weekly, monthly, quarterly)

    Phase 5: Use statsmodels.seasonal_decompose() for actual detection
    """
    # Phase 3: Mock implementation
    return {
        "weekly_seasonality": True,
        "monthly_seasonality": False,
        "quarterly_seasonality": False,
        "note": "Phase 3: Hardcoded. Phase 5: Use seasonal_decompose()"
    }
```

---

### Task 7: Document ML Interfaces for Phase 5

**Create `backend/app/ml/README.md`:**
```markdown
# ML Pipeline Documentation

## Overview

This module contains placeholder implementations for the Fashion Forecast MVP ML pipeline:

1. **Prophet Forecasting** (`prophet_model.py`)
2. **ARIMA Forecasting** (`arima_model.py`)
3. **K-means Clustering** (`clustering.py`)
4. **Ensemble Forecasting** (`ensemble.py`)
5. **Data Preprocessing** (`preprocessing.py`)

**Current Status (Phase 3):** All functions return mock data matching the expected interface.

**Future Implementation (Phase 5):** Actual statistical models will replace placeholders.

---

## Function Interfaces

### 1. Ensemble Forecasting (Primary Entry Point)

```python
from app.ml import forecast_category_demand

result = forecast_category_demand(
    historical_sales=df,      # pd.DataFrame with ['date', 'units_sold']
    weeks=12,                 # Forecast horizon
    season_start_date="2025-03-03"  # ISO 8601 date
)

# Returns:
{
    "total_season_demand": 7750,
    "prophet_forecast": 8000,
    "arima_forecast": 7500,
    "weekly_demand_curve": [
        {
            "week_number": 1,
            "week_start_date": "2025-03-03",
            "week_end_date": "2025-03-09",
            "forecasted_units": 1320,
            "confidence_lower": 1122,
            "confidence_upper": 1518
        },
        ...
    ],
    "forecasting_method": "ensemble_prophet_arima",
    "models_used": ["prophet", "arima"]
}
```

### 2. Store Clustering

```python
from app.ml import cluster_stores, calculate_cluster_distribution

# Step 1: Assign clusters
stores_df = cluster_stores(stores_df, n_clusters=3)

# Step 2: Calculate distribution
distribution = calculate_cluster_distribution(stores_df, total_demand=7750)

# Returns:
[
    {
        "cluster_id": "fashion_forward",
        "cluster_name": "Fashion Forward",
        "allocation_percentage": 0.40,
        "total_units": 3100,
        "store_count": 15
    },
    ...
]
```

### 3. Data Preprocessing

```python
from app.ml import clean_historical_sales, validate_sales_data

# Clean data
df_clean = clean_historical_sales(df)

# Validate
is_valid, message = validate_sales_data(df_clean, min_weeks=52)
```

---

## Phase 5 Implementation Checklist

### Prophet Model (`prophet_model.py`)

- [ ] Install `prophet>=1.1.6`
- [ ] Replace mock data with actual Prophet model
- [ ] Configure seasonality (weekly, yearly)
- [ ] Add country holidays (US)
- [ ] Return confidence intervals from Prophet
- [ ] Handle edge cases (insufficient data, flat trends)

### ARIMA Model (`arima_model.py`)

- [ ] Install `pmdarima>=2.0.4`
- [ ] Replace mock data with `auto_arima()`
- [ ] Configure `seasonal=True, m=52`
- [ ] Return AIC/BIC scores
- [ ] Handle non-stationary data (differencing)

### K-means Clustering (`clustering.py`)

- [ ] Install `scikit-learn>=1.5.0`
- [ ] Encode categorical features (location_tier, fashion_tier, store_format, region)
- [ ] Apply `StandardScaler` to 7 features
- [ ] Run `KMeans(n_clusters=3, init='k-means++', random_state=42)`
- [ ] Analyze cluster centers to assign meaningful names
- [ ] Validate cluster assignments (no empty clusters)

### Ensemble (`ensemble.py`)

- [ ] Add parallel execution (run Prophet + ARIMA concurrently)
- [ ] Optional: Implement confidence-weighted averaging
- [ ] Add variance detection (flag if models disagree >20%)

### Preprocessing (`preprocessing.py`)

- [ ] Add outlier detection (Z-score or IQR method)
- [ ] Implement `seasonal_decompose()` for seasonality detection
- [ ] Add data quality reports (missing dates, gaps, anomalies)

---

## Testing Strategy

### Phase 3 Tests (Current)

```python
# Test that functions run without errors
def test_prophet_placeholder():
    df = pd.DataFrame({'date': [...], 'units_sold': [...]})
    result = run_prophet_forecast(df, weeks=12)
    assert result['total_season_demand'] == 8000

def test_ensemble_forecast():
    df = pd.DataFrame({'date': [...], 'units_sold': [...]})
    result = forecast_category_demand(df, weeks=12)
    assert result['total_season_demand'] == 7750  # (8000 + 7500) / 2
```

### Phase 5 Tests (Future)

- Validate Prophet predictions on historical test set
- Compare ARIMA accuracy vs baseline (naive forecast)
- Evaluate clustering quality (silhouette score, within-cluster sum of squares)
- Test ensemble performance vs individual models

---

## Dependencies

### Phase 3 (Current)

```toml
pandas = "^2.2.0"
numpy = "^1.26.0"
```

### Phase 5 (Future)

```toml
prophet = "^1.1.6"
pmdarima = "^2.0.4"
scikit-learn = "^1.5.0"
statsmodels = "^0.14.0"  # For seasonal_decompose
```

---

## References

- **Planning Spec:** `planning/3_technical_architecture_v3.3.md` lines 900-1100 (ML approaches)
- **Implementation Plan:** `implementation_plan.md` Task 11 (lines 368-383)
- **Prophet Docs:** https://facebook.github.io/prophet/
- **pmdarima Docs:** http://alkaline-ml.com/pmdarima/
- **scikit-learn K-means:** https://scikit-learn.org/stable/modules/clustering.html#k-means

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Phase 3 Complete (Placeholders) | Phase 5 Pending (Actual Models)
```

---

### Task 8: Add Type Hints and Validation

**Ensure all functions have:**
- Type hints on parameters and return values
- Docstrings with Args, Returns, and Phase 5 notes
- Input validation (check DataFrame columns, data types)
- Error handling (raise ValueError with clear messages)

**Example validation pattern:**
```python
def run_prophet_forecast(
    historical_sales: pd.DataFrame,
    weeks: int = 12,
    season_start_date: str = None
) -> Dict[str, Any]:
    # Validate inputs
    if not isinstance(historical_sales, pd.DataFrame):
        raise TypeError("historical_sales must be a pandas DataFrame")

    if 'units_sold' not in historical_sales.columns:
        raise ValueError("DataFrame must have 'units_sold' column")

    if weeks < 1 or weeks > 52:
        raise ValueError("weeks must be between 1 and 52")

    # ... rest of implementation
```

---

## Dev Notes

### Why Placeholders?

**Problem:** Full ML implementation (Prophet, ARIMA, K-means) takes 10-15 hours. Backend architecture needs to proceed without blocking.

**Solution:** Create interfaces now, implement models later. This enables:
1. End-to-end workflow testing with mock data
2. Frontend integration (agents return realistic responses)
3. Parallel development (Phase 3 backend while Phase 5 ML)
4. Interface stability (contract established upfront)

### Ensemble Forecasting Rationale

**Why Prophet + ARIMA?**
- Prophet: Handles trend + seasonality automatically (ideal for retail)
- ARIMA: Captures short-term autocorrelation (week-to-week patterns)
- Ensemble: Reduces overfitting to one model's assumptions

**Simple Average vs Weighted:**
- Phase 3: Equal weight (0.5 each) for simplicity
- Phase 5: Could add confidence-based weighting if models provide uncertainty scores

### K-means Clustering Design

**7 Features (Research-Backed):**
1. `store_size_sqft` (capacity)
2. `median_income` (demographics)
3. `location_tier_encoded` (A=3, B=2, C=1)
4. `fashion_tier_encoded` (PREMIUM=3, MAINSTREAM=2, VALUE=1)
5. `avg_weekly_sales_12mo` (historical performance - MOST IMPORTANT)
6. `store_format_encoded` (MALL=4, STANDALONE=3, SHOPPING_CENTER=2, OUTLET=1)
7. `region_encoded` (NORTHEAST=1, SOUTHEAST=2, MIDWEST=3, WEST=4)

**K=3 Clusters (MVP Scope):**
- Fashion Forward (40% of demand)
- Mainstream (35% of demand)
- Value Conscious (25% of demand)

**StandardScaler Required:** K-means uses Euclidean distance, so features must be normalized.

### Data Preprocessing Strategy

**Key Steps:**
1. **Fill missing dates:** Prophet requires continuous time series
2. **Remove outliers:** Cap at 99th percentile to prevent skew
3. **Aggregate to weekly:** Most retail data is daily, models need weekly
4. **Validate:** Check for sufficient history (52+ weeks)

**Phase 5 Additions:**
- Seasonal decomposition (statsmodels)
- Anomaly detection (Z-score, isolation forest)
- Data quality reports

---

## Testing

### Manual Testing Checklist

- [ ] Import all functions without errors
- [ ] `forecast_category_demand()` returns dict with expected keys
- [ ] Prophet forecast returns 8000 units (mock)
- [ ] ARIMA forecast returns 7500 units (mock)
- [ ] Ensemble returns 7750 units ((8000 + 7500) / 2)
- [ ] `cluster_stores()` returns DataFrame with 'cluster_id' column
- [ ] `calculate_cluster_distribution()` returns 3 clusters
- [ ] Cluster allocation percentages sum to ~1.0
- [ ] `clean_historical_sales()` handles missing dates
- [ ] `validate_sales_data()` detects insufficient data

### Verification Commands

```bash
# Test imports
python -c "from app.ml import forecast_category_demand, cluster_stores; print('Imports OK')"

# Run sample forecast
python -c "
import pandas as pd
from datetime import datetime, timedelta
from app.ml import forecast_category_demand

# Mock historical data
dates = [datetime(2024, 1, 1) + timedelta(weeks=i) for i in range(52)]
sales = [100 + i * 2 for i in range(52)]
df = pd.DataFrame({'date': dates, 'units_sold': sales})

result = forecast_category_demand(df, weeks=12)
print(f\"Total forecast: {result['total_season_demand']} units\")
print(f\"Models used: {result['models_used']}\")
"

# Test clustering
python -c "
import pandas as pd
from app.ml import cluster_stores

stores = pd.DataFrame({
    'store_id': range(1, 11),
    'fashion_tier': ['PREMIUM', 'MAINSTREAM', 'VALUE'] * 3 + ['PREMIUM'],
    'avg_weekly_sales_12mo': [1000, 800, 600] * 3 + [1200]
})

stores_clustered = cluster_stores(stores)
print(stores_clustered[['store_id', 'fashion_tier', 'cluster_id']])
"
```

---

## File List

**Files to Create:**

1. `backend/app/ml/__init__.py` - Module exports
2. `backend/app/ml/prophet_model.py` - Prophet placeholder (200 lines)
3. `backend/app/ml/arima_model.py` - ARIMA placeholder (80 lines)
4. `backend/app/ml/clustering.py` - K-means placeholder (150 lines)
5. `backend/app/ml/ensemble.py` - Ensemble logic (120 lines)
6. `backend/app/ml/preprocessing.py` - Data cleaning utilities (150 lines)
7. `backend/app/ml/README.md` - ML documentation (150 lines)

**Total Lines of Code:** ~850 lines

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial story creation | Product Owner |
| 2025-10-19 | 1.1 | Added Change Log and QA Results sections for template compliance | Product Owner |

---

## Dev Agent Record

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

---

## Definition of Done

- [ ] `backend/app/ml/` folder created with all 6 modules
- [ ] Prophet placeholder returns mock forecast (8000 units)
- [ ] ARIMA placeholder returns mock forecast (7500 units)
- [ ] Clustering placeholder returns 3 clusters (fashion_forward, mainstream, value_conscious)
- [ ] Ensemble function combines Prophet + ARIMA (simple average)
- [ ] Preprocessing utilities handle missing dates and outliers
- [ ] All functions have type hints and docstrings
- [ ] README.md documents interfaces for Phase 5
- [ ] Mock data is realistic (no negatives, reasonable distributions)
- [ ] Functions run without errors on minimal DataFrames
- [ ] Ready for Phase 5 actual ML implementation

---

## QA Results

_This section will be populated by QA Agent after story implementation and testing_

**QA Status:** Pending
**QA Agent:** TBD
**QA Date:** TBD

### Test Execution Results
- TBD

### Issues Found
- TBD

### Sign-Off
- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No critical issues found
- [ ] Story approved for deployment

---

**Created:** 2025-10-19
**Last Updated:** 2025-10-21 (Implementation completed)
**Story Points:** 3
**Priority:** P1 (Required for Demand Agent in Phase 5)
