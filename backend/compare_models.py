"""
Complete Model Comparison: Baseline vs Enhanced

This script runs both baseline and enhanced models and provides
a comprehensive performance comparison.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import logging
import warnings
warnings.filterwarnings('ignore')

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from test_demand_models import ModelEvaluator
from utils.data_loader import TrainingDataLoader

# Import baseline models
from agent_tools.demand_tools import (
    ProphetWrapper,
    ARIMAWrapper,
    EnsembleForecaster,
)

# Import enhanced models
from agent_tools.demand_tools_enhanced import (
    EnhancedProphetWrapper,
    EnhancedARIMAWrapper,
    ExponentialSmoothingWrapper,
    DynamicEnsembleForecaster,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text, char='='):
    """Print formatted header."""
    print(f"\n{char * 80}")
    print(f" {text}")
    print(f"{char * 80}\n")


def compare_all_models():
    """Run comprehensive comparison of all models."""
    print_header("COMPREHENSIVE MODEL COMPARISON", '#')

    data_loader = TrainingDataLoader()
    evaluator = ModelEvaluator(data_loader)

    categories = data_loader.get_categories()
    print(f"Testing categories: {', '.join(categories)}\n")

    # Define all models to test
    models = {
        'BASELINE MODELS': {
            'Prophet (Baseline)': ProphetWrapper,
            'ARIMA (Baseline)': ARIMAWrapper,
            'Ensemble 60/40 (Baseline)': EnsembleForecaster,
        },
        'ENHANCED MODELS': {
            'Prophet (Enhanced)': EnhancedProphetWrapper,
            'ARIMA (Enhanced)': EnhancedARIMAWrapper,
            'Exponential Smoothing': ExponentialSmoothingWrapper,
            'Dynamic Ensemble': DynamicEnsembleForecaster,
        }
    }

    all_results = {}

    # Test all models
    for group_name, group_models in models.items():
        print_header(group_name, '-')

        for category in categories:
            if category not in all_results:
                all_results[category] = {}

            for model_name, model_class in group_models.items():
                logger.info(f"\nTesting: {model_name} on {category}")
                try:
                    result = evaluator.evaluate_model_cv(
                        model_class, category, n_splits=5
                    )
                    all_results[category][model_name] = result
                except Exception as e:
                    logger.error(f"Failed: {e}")
                    all_results[category][model_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }

    # Generate comparison report
    print_header("PERFORMANCE COMPARISON REPORT", '=')

    for category in categories:
        print(f"\n{'='*80}")
        print(f"Category: {category}")
        print(f"{'='*80}")
        print(f"{'Model':<35} {'MAE':>10} {'MAPE':>10} {'SMAPE':>10} {'R²':>10}")
        print('-' * 80)

        results_list = []
        for model_name, result in all_results[category].items():
            if result['status'] == 'success':
                metrics = result['avg_metrics']
                mae_mean = metrics['mae']['mean']
                mape_mean = metrics['mape']['mean']
                smape_mean = metrics['smape']['mean']
                r2_mean = metrics['r2']['mean']

                print(
                    f"{model_name:<35} "
                    f"{mae_mean:>10.2f} "
                    f"{mape_mean:>9.2f}% "
                    f"{smape_mean:>9.2f}% "
                    f"{r2_mean:>10.4f}"
                )

                results_list.append({
                    'model': model_name,
                    'mae': mae_mean,
                    'mape': mape_mean,
                    'smape': smape_mean,
                    'r2': r2_mean,
                })

        # Find best model
        if results_list:
            best_by_mape = min(results_list, key=lambda x: x['mape'])
            best_by_r2 = max(results_list, key=lambda x: x['r2'])

            print(f"\n  Best by MAPE: {best_by_mape['model']} ({best_by_mape['mape']:.2f}%)")
            print(f"  Best by R²:   {best_by_r2['model']} ({best_by_r2['r2']:.4f})")

    # Overall summary
    print_header("OVERALL SUMMARY ACROSS ALL CATEGORIES", '=')

    model_aggregates = {}
    for category, model_results in all_results.items():
        for model_name, result in model_results.items():
            if result['status'] == 'success':
                if model_name not in model_aggregates:
                    model_aggregates[model_name] = {
                        'mae': [],
                        'mape': [],
                        'smape': [],
                        'r2': []
                    }
                metrics = result['avg_metrics']
                model_aggregates[model_name]['mae'].append(metrics['mae']['mean'])
                model_aggregates[model_name]['mape'].append(metrics['mape']['mean'])
                model_aggregates[model_name]['smape'].append(metrics['smape']['mean'])
                model_aggregates[model_name]['r2'].append(metrics['r2']['mean'])

    print(f"{'Model':<35} {'Avg MAE':>10} {'Avg MAPE':>10} {'Avg SMAPE':>10} {'Avg R²':>10}")
    print('-' * 80)

    summary_list = []
    for model_name, metrics in model_aggregates.items():
        avg_mae = np.mean(metrics['mae'])
        avg_mape = np.mean(metrics['mape'])
        avg_smape = np.mean(metrics['smape'])
        avg_r2 = np.mean(metrics['r2'])

        print(
            f"{model_name:<35} "
            f"{avg_mae:>10.2f} "
            f"{avg_mape:>9.2f}% "
            f"{avg_smape:>9.2f}% "
            f"{avg_r2:>10.4f}"
        )

        summary_list.append({
            'model': model_name,
            'avg_mae': avg_mae,
            'avg_mape': avg_mape,
            'avg_smape': avg_smape,
            'avg_r2': avg_r2,
        })

    # Overall winners
    print("\n" + "="*80)
    if summary_list:
        overall_best_mape = min(summary_list, key=lambda x: x['avg_mape'])
        overall_best_r2 = max(summary_list, key=lambda x: x['avg_r2'])

        print(f"OVERALL BEST MODEL BY MAPE: {overall_best_mape['model']}")
        print(f"  Average MAPE: {overall_best_mape['avg_mape']:.2f}%")
        print(f"  Average R²:   {overall_best_mape['avg_r2']:.4f}")
        print()
        print(f"OVERALL BEST MODEL BY R²: {overall_best_r2['model']}")
        print(f"  Average MAPE: {overall_best_r2['avg_mape']:.2f}%")
        print(f"  Average R²:   {overall_best_r2['avg_r2']:.4f}")

    # Calculate improvements
    print_header("IMPROVEMENT ANALYSIS", '=')

    baseline_ensemble = model_aggregates.get('Ensemble 60/40 (Baseline)', None)
    enhanced_ensemble = model_aggregates.get('Dynamic Ensemble', None)

    if baseline_ensemble and enhanced_ensemble:
        baseline_mape = np.mean(baseline_ensemble['mape'])
        enhanced_mape = np.mean(enhanced_ensemble['mape'])
        mape_improvement = ((baseline_mape - enhanced_mape) / baseline_mape) * 100

        baseline_r2 = np.mean(baseline_ensemble['r2'])
        enhanced_r2 = np.mean(enhanced_ensemble['r2'])
        r2_improvement = ((enhanced_r2 - baseline_r2) / abs(baseline_r2)) * 100

        print(f"Baseline Ensemble vs Dynamic Ensemble:")
        print(f"  MAPE Improvement: {mape_improvement:+.2f}%")
        print(f"  R² Improvement:   {r2_improvement:+.2f}%")

    # Save results
    output_dir = backend_dir / "evaluation_results"
    output_dir.mkdir(exist_ok=True)

    import json
    results_file = output_dir / "comparison_results.json"

    json_results = {}
    for category, model_results in all_results.items():
        json_results[category] = {}
        for model_name, result in model_results.items():
            if result['status'] == 'success':
                json_results[category][model_name] = {
                    'mae': {
                        'mean': float(result['avg_metrics']['mae']['mean']),
                        'std': float(result['avg_metrics']['mae']['std']),
                    },
                    'mape': {
                        'mean': float(result['avg_metrics']['mape']['mean']),
                        'std': float(result['avg_metrics']['mape']['std']),
                    },
                    'r2': {
                        'mean': float(result['avg_metrics']['r2']['mean']),
                        'std': float(result['avg_metrics']['r2']['std']),
                    },
                    'n_folds': result['n_folds'],
                }

    with open(results_file, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f"\n\nResults saved to: {results_file}")
    print("="*80)


if __name__ == "__main__":
    compare_all_models()
