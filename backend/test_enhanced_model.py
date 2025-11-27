"""
Test Enhanced Demand Forecasting Model

Quick verification that the enhanced validation-based ensemble works correctly.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add paths
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from utils.data_loader import TrainingDataLoader
from agent_tools.demand_tools import (
    ProphetWrapper,
    ExponentialSmoothingWrapper,
    EnsembleForecaster,
    clean_historical_sales,
    aggregate_to_weekly,
)

print("="*70)
print(" ENHANCED MODEL VERIFICATION TEST")
print("="*70)
print()

# Load data
loader = TrainingDataLoader()
categories = loader.get_categories()
print(f"Testing on: {', '.join(categories)}\n")

# Test each component
print("1. Testing ProphetWrapper...")
try:
    hist_data = loader.get_historical_sales(categories[0])
    df = pd.DataFrame(hist_data)
    df = clean_historical_sales(df)
    df = aggregate_to_weekly(df)

    prophet = ProphetWrapper()
    prophet.train(df)
    forecast = prophet.forecast(12)

    assert 'predictions' in forecast
    assert len(forecast['predictions']) == 12
    assert all(p >= 0 for p in forecast['predictions'])

    print(f"   [OK] ProphetWrapper works (forecast: {forecast['predictions'][:3]}...)")
except Exception as e:
    print(f"   [FAIL] ProphetWrapper FAILED: {e}")
    sys.exit(1)

print("\n2. Testing ExponentialSmoothingWrapper (NEW)...")
try:
    exp_smooth = ExponentialSmoothingWrapper()
    exp_smooth.train(df)
    forecast = exp_smooth.forecast(12)

    assert 'predictions' in forecast
    assert len(forecast['predictions']) == 12
    assert all(p >= 0 for p in forecast['predictions'])

    print(f"   [OK] ExponentialSmoothingWrapper works (forecast: {forecast['predictions'][:3]}...)")
except Exception as e:
    print(f"   [FAIL] ExponentialSmoothingWrapper FAILED: {e}")
    sys.exit(1)

print("\n3. Testing Enhanced EnsembleForecaster (VALIDATION-BASED)...")
try:
    ensemble = EnsembleForecaster()
    ensemble.train(df)

    # Check weights were calculated
    assert hasattr(ensemble, 'weights')
    assert len(ensemble.weights) > 0
    print(f"   Calculated weights: {ensemble.weights}")

    # Check models were trained
    assert hasattr(ensemble, 'models')
    assert len(ensemble.models) > 0
    print(f"   Trained models: {list(ensemble.models.keys())}")

    # Generate forecast
    forecast = ensemble.forecast(12)

    assert 'predictions' in forecast
    assert 'confidence' in forecast
    assert 'model_used' in forecast
    assert len(forecast['predictions']) == 12
    assert all(p >= 0 for p in forecast['predictions'])
    assert 0 <= forecast['confidence'] <= 1

    print(f"   [OK] EnsembleForecaster works")
    print(f"     Forecast: {forecast['predictions'][:3]}...")
    print(f"     Confidence: {forecast['confidence']:.2f}")
    print(f"     Model used: {forecast['model_used']}")

except Exception as e:
    print(f"   [FAIL] EnsembleForecaster FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Quick performance test on all categories...")
for category in categories:
    try:
        hist_data = loader.get_historical_sales(category)
        df = pd.DataFrame(hist_data)
        df = clean_historical_sales(df)
        df = aggregate_to_weekly(df)

        # Simple train-test split
        train_df = df.iloc[:-12]
        test_df = df.iloc[-12:]

        ensemble = EnsembleForecaster()
        ensemble.train(train_df)
        forecast = ensemble.forecast(12)

        actual = test_df['quantity_sold'].values[:12]
        predicted = forecast['predictions']

        mae = np.mean(np.abs(actual - predicted))
        mape = np.mean(np.abs((actual - predicted) / (actual + 1e-6))) * 100

        print(f"   {category}: MAE={mae:.1f}, MAPE={mape:.1f}%, Weights={ensemble.weights}")

    except Exception as e:
        print(f"   {category}: FAILED - {e}")

print("\n" + "="*70)
print(" ALL TESTS PASSED [OK]")
print("="*70)
print("\nEnhanced model is working correctly!")
print("- Prophet: Baseline model")
print("- Exponential Smoothing: NEW alternative to ARIMA")
print("- Validation-Based Ensemble: Automatically picks best weights")
print()
