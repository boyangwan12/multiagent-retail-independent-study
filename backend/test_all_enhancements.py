"""
Comprehensive Enhancement Testing

Tests multiple valid enhancement approaches:
1. Fixed Exponential Smoothing
2. XGBoost with lag features
3. Optimized Prophet (subtle tuning)
4. Smart model selection
5. Validation-based ensemble
"""

import warnings
warnings.filterwarnings('ignore')

import sys
import io
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing as HoltWinters

# Add path
sys.path.insert(0, str(Path(__file__).parent))
from utils.data_loader import TrainingDataLoader

print("="*80)
print(" COMPREHENSIVE ENHANCEMENT TESTING")
print("="*80)
print()

# ============================================================================
# BASELINE MODELS (for comparison)
# ============================================================================

class ProphetBaseline:
    """Current baseline Prophet."""
    def __init__(self):
        self.model = None
        self.forecast_df = None

    def train(self, df: pd.DataFrame):
        df_p = df.rename(columns={"date": "ds", "quantity_sold": "y"})
        df_p["ds"] = pd.to_datetime(df_p["ds"])

        self.model = Prophet(
            seasonality_mode="multiplicative",
            yearly_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
        )

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        self.model.fit(df_p)
        sys.stdout = old_stdout

    def forecast(self, periods: int):
        future = self.model.make_future_dataframe(periods=periods, freq="W")
        forecast_df = self.model.predict(future)
        self.forecast_df = forecast_df.tail(periods)
        return np.maximum(0, self.forecast_df["yhat"].values).astype(int)


class EnsembleBaseline:
    """Current 60/40 ensemble."""
    def __init__(self):
        self.prophet = ProphetBaseline()
        self.arima = None

    def train(self, df: pd.DataFrame):
        self.prophet.train(df)

        # Train ARIMA
        try:
            y = df["quantity_sold"].values
            best_aic = np.inf
            best_order = (1, 1, 1)

            for p in [0, 1, 2]:
                for d in [0, 1]:
                    for q in [0, 1, 2]:
                        try:
                            model = ARIMA(y, order=(p, d, q))
                            fitted = model.fit()
                            if fitted.aic < best_aic:
                                best_aic = fitted.aic
                                best_order = (p, d, q)
                        except:
                            continue

            self.arima = ARIMA(y, order=best_order).fit()
        except:
            self.arima = None

    def forecast(self, periods: int):
        p_pred = self.prophet.forecast(periods)

        if self.arima:
            try:
                a_pred = self.arima.forecast(steps=periods)
                a_pred = np.maximum(0, np.round(a_pred)).astype(int)
                return np.round(0.6 * p_pred + 0.4 * a_pred).astype(int)
            except:
                pass

        return p_pred


# ============================================================================
# ENHANCEMENT 1: Fixed Exponential Smoothing
# ============================================================================

class ExponentialSmoothingFixed:
    """Properly implemented Holt-Winters."""
    def __init__(self):
        self.model = None

    def train(self, df: pd.DataFrame):
        y = df["quantity_sold"].values

        # Use correct API for statsmodels
        try:
            self.model = HoltWinters(
                y,
                seasonal='mul',
                trend='add',
                seasonal_periods=min(52, len(y) // 2),
                initialization_method='estimated'
            ).fit(optimized=True)
        except:
            # Fallback to additive
            self.model = HoltWinters(
                y,
                seasonal='add',
                trend='add',
                seasonal_periods=min(52, len(y) // 2),
                initialization_method='estimated'
            ).fit(optimized=True)

    def forecast(self, periods: int):
        pred = self.model.forecast(steps=periods)
        return np.maximum(0, np.round(pred)).astype(int)


# ============================================================================
# ENHANCEMENT 2: XGBoost with Lag Features
# ============================================================================

class XGBoostForecaster:
    """XGBoost with engineered lag features."""
    def __init__(self):
        self.model = None
        self.last_known_values = None

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create lag and rolling features."""
        df = df.copy()
        df['week_of_year'] = pd.to_datetime(df['date']).dt.isocalendar().week

        # Lag features
        df['lag_1'] = df['quantity_sold'].shift(1)
        df['lag_2'] = df['quantity_sold'].shift(2)
        df['lag_4'] = df['quantity_sold'].shift(4)
        df['lag_12'] = df['quantity_sold'].shift(12)
        df['lag_52'] = df['quantity_sold'].shift(52)

        # Rolling statistics
        df['rolling_mean_4'] = df['quantity_sold'].rolling(4, min_periods=1).mean()
        df['rolling_std_4'] = df['quantity_sold'].rolling(4, min_periods=1).std()
        df['rolling_mean_12'] = df['quantity_sold'].rolling(12, min_periods=1).mean()

        return df

    def train(self, df: pd.DataFrame):
        try:
            import xgboost as xgb
        except ImportError:
            raise RuntimeError("XGBoost not installed. Run: pip install xgboost")

        df = self.create_features(df)

        # Drop rows with NaN (from lag features)
        df_clean = df.dropna()

        feature_cols = ['lag_1', 'lag_2', 'lag_4', 'lag_12', 'lag_52',
                       'rolling_mean_4', 'rolling_std_4', 'rolling_mean_12',
                       'week_of_year']

        X = df_clean[feature_cols]
        y = df_clean['quantity_sold']

        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective='reg:squarederror',
            random_state=42
        )
        self.model.fit(X, y)

        # Store last values for forecasting
        self.last_known_values = df['quantity_sold'].values
        self.feature_cols = feature_cols

    def forecast(self, periods: int):
        """Iterative forecasting."""
        predictions = []
        current_values = list(self.last_known_values)

        for i in range(periods):
            # Create features for next period
            features = {
                'lag_1': current_values[-1] if len(current_values) >= 1 else 0,
                'lag_2': current_values[-2] if len(current_values) >= 2 else 0,
                'lag_4': current_values[-4] if len(current_values) >= 4 else 0,
                'lag_12': current_values[-12] if len(current_values) >= 12 else 0,
                'lag_52': current_values[-52] if len(current_values) >= 52 else 0,
                'rolling_mean_4': np.mean(current_values[-4:]) if len(current_values) >= 4 else 0,
                'rolling_std_4': np.std(current_values[-4:]) if len(current_values) >= 4 else 0,
                'rolling_mean_12': np.mean(current_values[-12:]) if len(current_values) >= 12 else 0,
                'week_of_year': ((len(current_values) + i) % 52) + 1,
            }

            X_next = pd.DataFrame([features])[self.feature_cols]
            pred = self.model.predict(X_next)[0]
            pred = max(0, int(round(pred)))

            predictions.append(pred)
            current_values.append(pred)

        return np.array(predictions)


# ============================================================================
# ENHANCEMENT 3: Optimized Prophet
# ============================================================================

class ProphetOptimized:
    """Subtly optimized Prophet (no custom seasonalities)."""
    def __init__(self):
        self.model = None
        self.forecast_df = None

    def train(self, df: pd.DataFrame):
        df_p = df.rename(columns={"date": "ds", "quantity_sold": "y"})
        df_p["ds"] = pd.to_datetime(df_p["ds"])

        # Subtle optimization: slightly higher flexibility
        self.model = Prophet(
            seasonality_mode="multiplicative",
            yearly_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.08,  # Slightly increased from 0.05
            seasonality_prior_scale=12.0,   # Slightly increased from 10.0
            changepoint_range=0.85,         # Allow changepoints in 85% of data
        )

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        self.model.fit(df_p)
        sys.stdout = old_stdout

    def forecast(self, periods: int):
        future = self.model.make_future_dataframe(periods=periods, freq="W")
        forecast_df = self.model.predict(future)
        self.forecast_df = forecast_df.tail(periods)
        return np.maximum(0, self.forecast_df["yhat"].values).astype(int)


# ============================================================================
# ENHANCEMENT 4: Smart Model Selection
# ============================================================================

class SmartSelector:
    """Selects best model based on data characteristics."""
    def __init__(self):
        self.selected_model = None
        self.model_name = None

    def train(self, df: pd.DataFrame):
        y = df["quantity_sold"].values

        # Analyze data characteristics
        cv = np.std(y) / (np.mean(y) + 1e-6)  # Coefficient of variation
        trend_strength = abs(np.corrcoef(np.arange(len(y)), y)[0, 1])

        # Decision logic
        if cv < 0.3 and trend_strength < 0.3:
            # Low variance, weak trend → Use Exponential Smoothing
            self.selected_model = ExponentialSmoothingFixed()
            self.model_name = "ExponentialSmoothing"
        elif cv > 0.5:
            # High variance → Use Prophet (handles volatility well)
            self.selected_model = ProphetOptimized()
            self.model_name = "Prophet"
        else:
            # Medium variance → Use optimized ensemble
            self.selected_model = OptimizedEnsemble()
            self.model_name = "OptimizedEnsemble"

        self.selected_model.train(df)

    def forecast(self, periods: int):
        return self.selected_model.forecast(periods)


# ============================================================================
# ENHANCEMENT 5: Optimized Ensemble (85/15)
# ============================================================================

class OptimizedEnsemble:
    """Ensemble with optimized 85/15 weights."""
    def __init__(self):
        self.prophet = ProphetBaseline()
        self.arima = None

    def train(self, df: pd.DataFrame):
        self.prophet.train(df)

        try:
            y = df["quantity_sold"].values
            best_aic = np.inf
            best_order = (1, 1, 1)

            for p in [0, 1, 2]:
                for d in [0, 1]:
                    for q in [0, 1, 2]:
                        try:
                            model = ARIMA(y, order=(p, d, q))
                            fitted = model.fit()
                            if fitted.aic < best_aic:
                                best_aic = fitted.aic
                                best_order = (p, d, q)
                        except:
                            continue

            self.arima = ARIMA(y, order=best_order).fit()
        except:
            self.arima = None

    def forecast(self, periods: int):
        p_pred = self.prophet.forecast(periods)

        if self.arima:
            try:
                a_pred = self.arima.forecast(steps=periods)
                a_pred = np.maximum(0, np.round(a_pred)).astype(int)
                # Optimized 85/15 weights
                return np.round(0.85 * p_pred + 0.15 * a_pred).astype(int)
            except:
                pass

        return p_pred


# ============================================================================
# ENHANCEMENT 6: Validation-Based Ensemble
# ============================================================================

class ValidationEnsemble:
    """Dynamic weights based on validation performance."""
    def __init__(self):
        self.models = {}
        self.weights = {}

    def train(self, df: pd.DataFrame):
        # Split for validation
        val_size = max(8, len(df) // 5)
        train_df = df.iloc[:-val_size]
        val_df = df.iloc[-val_size:]

        # Train candidate models on training set
        candidates = {
            'prophet': ProphetBaseline(),
            'exp_smooth': ExponentialSmoothingFixed(),
        }

        errors = {}
        for name, model in candidates.items():
            try:
                temp_model = model.__class__()
                temp_model.train(train_df)
                pred = temp_model.forecast(len(val_df))
                actual = val_df['quantity_sold'].values[:len(pred)]
                errors[name] = np.mean(np.abs(actual - pred))
            except Exception as e:
                errors[name] = np.inf

        # Calculate weights
        valid_errors = {k: v for k, v in errors.items() if v < np.inf}

        if len(valid_errors) > 0:
            inv_errors = {k: 1.0/(v+1e-6) for k, v in valid_errors.items()}
            total = sum(inv_errors.values())
            self.weights = {k: v/total for k, v in inv_errors.items()}
        else:
            self.weights = {'prophet': 1.0}

        # Retrain on full data
        for name in self.weights.keys():
            if self.weights[name] > 0.01:  # Only train if weight > 1%
                model = candidates[name].__class__()
                try:
                    model.train(df)
                    self.models[name] = model
                except:
                    self.weights[name] = 0

        # Renormalize weights
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v/total for k, v in self.weights.items()}

    def forecast(self, periods: int):
        predictions = np.zeros(periods)

        for name, model in self.models.items():
            weight = self.weights.get(name, 0)
            if weight > 0:
                try:
                    pred = model.forecast(periods)
                    predictions += weight * pred
                except:
                    pass

        return np.round(predictions).astype(int)


# ============================================================================
# EVALUATION
# ============================================================================

def calculate_metrics(actual, predicted):
    """Calculate performance metrics."""
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    mask = actual != 0
    mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100 if mask.any() else 0

    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return {'mae': mae, 'rmse': rmse, 'mape': mape, 'r2': r2}


def test_model(model_class, df, n_splits=5, test_size=12, min_train=52):
    """Test model with time series CV."""
    total_weeks = len(df)
    results = []

    for i in range(n_splits):
        train_end = total_weeks - (n_splits - i) * test_size
        if train_end < min_train:
            continue

        train_df = df.iloc[:train_end].copy()
        test_df = df.iloc[train_end:train_end + test_size].copy()

        try:
            model = model_class()
            model.train(train_df)
            pred = model.forecast(test_size)
            actual = test_df['quantity_sold'].values[:len(pred)]

            metrics = calculate_metrics(actual, pred)
            results.append(metrics)
        except Exception as e:
            print(f"    Fold {i+1} failed: {str(e)[:50]}")
            continue

    if not results:
        return None

    avg = {}
    for key in ['mae', 'mape', 'r2']:
        values = [r[key] for r in results]
        avg[key] = {'mean': np.mean(values), 'std': np.std(values)}

    return avg


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    loader = TrainingDataLoader()
    categories = loader.get_categories()

    print(f"Testing on {len(categories)} categories with 5-fold CV\n")

    # Define all models
    models = {
        # Baselines
        '1. Prophet (Baseline)': ProphetBaseline,
        '2. Ensemble 60/40 (Baseline)': EnsembleBaseline,

        # Enhancements
        '3. Exponential Smoothing (Fixed)': ExponentialSmoothingFixed,
        '4. XGBoost + Lag Features': XGBoostForecaster,
        '5. Prophet (Optimized)': ProphetOptimized,
        '6. Smart Model Selection': SmartSelector,
        '7. Ensemble 85/15 (Optimized)': OptimizedEnsemble,
        '8. Validation-Based Ensemble': ValidationEnsemble,
    }

    all_results = {}

    # Test each category
    for category in categories:
        print(f"\n{'='*80}")
        print(f"Category: {category}")
        print(f"{'='*80}")

        hist_data = loader.get_historical_sales(category)
        df = pd.DataFrame(hist_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df = df.set_index('date').resample('W').sum().reset_index()

        print(f"Total weeks: {len(df)}\n")

        all_results[category] = {}

        for model_name, model_class in models.items():
            print(f"  {model_name}...", end=' ', flush=True)

            try:
                result = test_model(model_class, df, n_splits=5)

                if result:
                    all_results[category][model_name] = result
                    print(f"MAE={result['mae']['mean']:.1f}, MAPE={result['mape']['mean']:.1f}%, R²={result['r2']['mean']:.3f}")
                else:
                    print("FAILED")

            except Exception as e:
                print(f"ERROR: {str(e)[:50]}")

    # Summary
    print(f"\n\n{'='*80}")
    print(" FINAL RESULTS - AVERAGE ACROSS ALL CATEGORIES")
    print(f"{'='*80}\n")

    print(f"{'Model':<40} {'MAE':>10} {'MAPE':>10} {'R²':>10}")
    print('-'*75)

    model_avgs = {}
    for model_name in models.keys():
        values = {'mae': [], 'mape': [], 'r2': []}

        for category in categories:
            if model_name in all_results[category]:
                result = all_results[category][model_name]
                values['mae'].append(result['mae']['mean'])
                values['mape'].append(result['mape']['mean'])
                values['r2'].append(result['r2']['mean'])

        if values['mae']:
            avg_mae = np.mean(values['mae'])
            avg_mape = np.mean(values['mape'])
            avg_r2 = np.mean(values['r2'])

            model_avgs[model_name] = {'mae': avg_mae, 'mape': avg_mape, 'r2': avg_r2}

            marker = ""
            if avg_mape < 11:
                marker = " ⭐ EXCELLENT"
            elif avg_mape < 13:
                marker = " ✓ GOOD"

            print(f"{model_name:<40} {avg_mae:>10.1f} {avg_mape:>9.1f}% {avg_r2:>10.4f}{marker}")

    # Find best
    if model_avgs:
        print(f"\n{'='*80}")
        best_mape = min(model_avgs.items(), key=lambda x: x[1]['mape'])
        best_r2 = max(model_avgs.items(), key=lambda x: x[1]['r2'])

        print(f"🏆 BEST BY MAPE: {best_mape[0]}")
        print(f"   MAPE: {best_mape[1]['mape']:.2f}%")
        print(f"   R²:   {best_mape[1]['r2']:.4f}")

        print(f"\n🏆 BEST BY R²: {best_r2[0]}")
        print(f"   MAPE: {best_r2[1]['mape']:.2f}%")
        print(f"   R²:   {best_r2[1]['r2']:.4f}")

        # Calculate improvements over baseline
        baseline = model_avgs.get('2. Ensemble 60/40 (Baseline)', None)
        if baseline and best_mape[0] != '2. Ensemble 60/40 (Baseline)':
            improvement = ((baseline['mape'] - best_mape[1]['mape']) / baseline['mape']) * 100
            print(f"\n{'='*80}")
            print(f"📈 IMPROVEMENT OVER BASELINE: {improvement:+.1f}%")
            print(f"   Baseline MAPE: {baseline['mape']:.2f}%")
            print(f"   Best MAPE:     {best_mape[1]['mape']:.2f}%")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
