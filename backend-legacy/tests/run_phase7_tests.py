#!/usr/bin/env python
"""
Phase 7 Integration Test Runner

This script runs Phase 7 tests using credentials from environment variables.
Credentials are NEVER written to code or files - they're loaded from the shell environment.

Usage:
    export OPENAI_API_KEY="your-actual-key-here"
    python backend/tests/run_phase7_tests.py

The script will:
1. Verify OPENAI_API_KEY is set in environment
2. Run PHASE7-001 unit tests (StoreClusterer)
3. Run PHASE7-002/003 functionality tests (InventoryAgent)
4. Run PHASE7-004 integration tests
5. Generate test report

Security:
- API key is never logged or displayed
- Credentials are passed via environment variables only
- No credentials stored in files
"""

import os
import sys
import asyncio
import pandas as pd
import numpy as np
from pathlib import Path

# Ensure we can import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_api_key():
    """Verify OPENAI_API_KEY is set in environment."""
    if not os.environ.get('OPENAI_API_KEY'):
        print("[ERROR] OPENAI_API_KEY environment variable not set")
        print("")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-actual-key-here'")
        print("")
        sys.exit(1)

    print("[OK] OPENAI_API_KEY is set in environment (not displayed for security)")
    print("")


def test_phase7_001():
    """Test PHASE7-001: K-means Store Clustering"""
    print("=" * 60)
    print("PHASE7-001: K-means Store Clustering")
    print("=" * 60)

    try:
        from app.ml.store_clustering import StoreClusterer

        print("Creating realistic store data (50 stores × 7 features)...")
        np.random.seed(42)

        # Cluster 1: Fashion_Forward (18 stores - high sales, premium)
        cluster1 = pd.DataFrame({
            'store_id': [f'FF_{i:02d}' for i in range(18)],
            'avg_weekly_sales_12mo': np.random.normal(850, 50, 18),
            'store_size_sqft': np.random.normal(50000, 3000, 18),
            'median_income': np.random.normal(125000, 10000, 18),
            'location_tier': ['A'] * 18,
            'fashion_tier': ['Premium'] * 18,
            'store_format': ['Mall'] * 18,
            'region': np.random.choice(['Northeast', 'West'], 18)
        })

        # Cluster 2: Mainstream (20 stores - medium sales)
        cluster2 = pd.DataFrame({
            'store_id': [f'MS_{i:02d}' for i in range(20)],
            'avg_weekly_sales_12mo': np.random.normal(650, 40, 20),
            'store_size_sqft': np.random.normal(35000, 2000, 20),
            'median_income': np.random.normal(85000, 8000, 20),
            'location_tier': ['B'] * 20,
            'fashion_tier': ['Mainstream'] * 20,
            'store_format': ['Standalone'] * 20,
            'region': np.random.choice(['Southeast', 'Midwest'], 20)
        })

        # Cluster 3: Value_Conscious (12 stores - low sales, outlet)
        cluster3 = pd.DataFrame({
            'store_id': [f'VC_{i:02d}' for i in range(12)],
            'avg_weekly_sales_12mo': np.random.normal(350, 30, 12),
            'store_size_sqft': np.random.normal(18000, 1500, 12),
            'median_income': np.random.normal(55000, 6000, 12),
            'location_tier': ['C'] * 12,
            'fashion_tier': ['Value'] * 12,
            'store_format': ['Outlet'] * 12,
            'region': ['Midwest'] * 12
        })

        stores = pd.concat([cluster1, cluster2, cluster3], ignore_index=True)
        print(f"[OK] Created {len(stores)} stores in 3 natural clusters")

        # Test clustering
        print("\nFitting K-means clustering...")
        clusterer = StoreClusterer(n_clusters=3, random_state=42)
        clusterer.fit(stores)
        print("[OK] K-means clustering complete")

        # Check silhouette score
        metrics = clusterer.get_cluster_quality_metrics()
        silhouette = metrics['silhouette_score']
        print(f"[OK] Silhouette Score: {silhouette:.4f}")
        assert silhouette > 0.4, f"Silhouette score {silhouette:.4f} below 0.4 threshold"
        print("[PASS] Silhouette score meets quality threshold (>0.4)")

        # Check cluster labels
        labels = clusterer.get_cluster_labels()
        print(f"\n[OK] Cluster Labels: {labels}")
        expected_labels = {"Fashion_Forward", "Mainstream", "Value_Conscious"}
        assert set(labels.values()) == expected_labels
        print("[PASS] Cluster labels assigned correctly")

        # Check cluster statistics
        stats = clusterer.get_cluster_stats()
        print("\n[OK] Cluster Statistics:")
        for idx, row in stats.iterrows():
            print(f"  {row['cluster_label']:<20} {row['store_count']:>2} stores, {row['allocation_percentage']:>5.1f}% allocation")

        # Check percentages sum to 100%
        total_pct = stats['allocation_percentage'].sum()
        assert abs(total_pct - 100.0) < 0.1, f"Percentages sum to {total_pct:.1f}%"
        print(f"[PASS] Allocation percentages sum to 100% ({total_pct:.1f}%)")

        print("\n" + "=" * 60)
        print("PHASE7-001: PASSED")
        print("=" * 60)
        print("")

        return True

    except Exception as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def test_phase7_002_003():
    """Test PHASE7-002/003: Inventory Allocation and Replenishment"""
    print("=" * 60)
    print("PHASE7-002 & PHASE7-003: Allocation and Replenishment")
    print("=" * 60)

    try:
        from app.ml.store_clustering import StoreClusterer
        from app.agents.inventory_agent import InventoryAgent
        from app.schemas.workflow_schemas import SeasonParameters

        print("Creating test data...")
        np.random.seed(42)

        # Create stores data
        cluster1 = pd.DataFrame({
            'store_id': [f'FF_{i:02d}' for i in range(18)],
            'avg_weekly_sales_12mo': np.random.normal(850, 50, 18),
            'store_size_sqft': np.random.normal(50000, 3000, 18),
            'median_income': np.random.normal(125000, 10000, 18),
            'location_tier': ['A'] * 18,
            'fashion_tier': ['Premium'] * 18,
            'store_format': ['Mall'] * 18,
            'region': np.random.choice(['Northeast', 'West'], 18)
        })

        cluster2 = pd.DataFrame({
            'store_id': [f'MS_{i:02d}' for i in range(20)],
            'avg_weekly_sales_12mo': np.random.normal(650, 40, 20),
            'store_size_sqft': np.random.normal(35000, 2000, 20),
            'median_income': np.random.normal(85000, 8000, 20),
            'location_tier': ['B'] * 20,
            'fashion_tier': ['Mainstream'] * 20,
            'store_format': ['Standalone'] * 20,
            'region': np.random.choice(['Southeast', 'Midwest'], 20)
        })

        cluster3 = pd.DataFrame({
            'store_id': [f'VC_{i:02d}' for i in range(12)],
            'avg_weekly_sales_12mo': np.random.normal(350, 30, 12),
            'store_size_sqft': np.random.normal(18000, 1500, 12),
            'median_income': np.random.normal(55000, 6000, 12),
            'location_tier': ['C'] * 12,
            'fashion_tier': ['Value'] * 12,
            'store_format': ['Outlet'] * 12,
            'region': ['Midwest'] * 12
        })

        stores = pd.concat([cluster1, cluster2, cluster3], ignore_index=True)
        stores.set_index('store_id', inplace=True)
        print(f"[OK] Created {len(stores)} stores")

        # Create forecast result (from Phase 6 Demand Agent)
        forecast_result = {
            'total_demand': 8000,
            'forecast_by_week': [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480],
            'safety_stock_pct': 0.20,
            'confidence': 0.85,
            'model_used': 'prophet_arima_ensemble'
        }
        print("[OK] Created forecast result (Phase 6 output)")

        # Test 1: Standard retail scenario (45% holdback, weekly replenishment)
        print("\nTest 1: Standard retail (45% holdback, weekly replenishment)")
        parameters_standard = SeasonParameters(
            forecast_horizon_weeks=12,
            season_start_date='2025-01-01',
            season_end_date='2025-03-31',
            replenishment_strategy='weekly',
            dc_holdback_percentage=0.45,
            markdown_checkpoint_week=8,
            markdown_threshold=0.60
        )

        inventory_agent = InventoryAgent()

        # Run async execute
        loop = asyncio.new_event_loop()
        allocation_result = loop.run_until_complete(
            inventory_agent.execute(
                forecast_result=forecast_result,
                parameters=parameters_standard,
                stores_data=stores
            )
        )
        loop.close()

        # Verify results
        expected_mfg = int(8000 * (1 + 0.20))  # 9600
        assert allocation_result['manufacturing_qty'] == expected_mfg
        print(f"[PASS] Manufacturing qty correct: {allocation_result['manufacturing_qty']} units")

        expected_holdback = int(9600 * 0.45)  # 4320
        assert allocation_result['dc_holdback_total'] == expected_holdback
        print(f"[PASS] DC holdback correct: {expected_holdback} units (45%)")

        expected_initial = 9600 - 4320  # 5280
        assert allocation_result['initial_allocation_total'] == expected_initial
        print(f"[PASS] Initial allocation correct: {expected_initial} units (55%)")

        # Verify replenishment enabled
        assert allocation_result['replenishment_enabled'] == True
        print("[PASS] Replenishment enabled (strategy='weekly')")

        # Test 2: Fast fashion scenario (0% holdback, no replenishment)
        print("\nTest 2: Fast fashion/Zara (0% holdback, no replenishment)")
        parameters_zara = SeasonParameters(
            forecast_horizon_weeks=12,
            season_start_date='2025-01-01',
            season_end_date='2025-03-31',
            replenishment_strategy='none',
            dc_holdback_percentage=0.0,
            markdown_checkpoint_week=4,
            markdown_threshold=0.60
        )

        inventory_agent2 = InventoryAgent()
        loop2 = asyncio.new_event_loop()
        allocation_result2 = loop2.run_until_complete(
            inventory_agent2.execute(
                forecast_result=forecast_result,
                parameters=parameters_zara,
                stores_data=stores
            )
        )
        loop2.close()

        assert allocation_result2['dc_holdback_total'] == 0
        print("[PASS] DC holdback is 0% (all to stores)")

        assert allocation_result2['initial_allocation_total'] == allocation_result2['manufacturing_qty']
        print(f"[PASS] 100% allocated to stores: {allocation_result2['initial_allocation_total']} units")

        assert allocation_result2['replenishment_enabled'] == False
        print("[PASS] Replenishment disabled (strategy='none')")

        print("\n" + "=" * 60)
        print("PHASE7-002 & PHASE7-003: PASSED")
        print("=" * 60)
        print("")

        return True

    except Exception as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " Phase 7 Inventory Agent Test Suite".center(58) + "║")
    print("║" + " Credentials from environment variables (not displayed)".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    # Check API key
    check_api_key()

    # Run tests
    results = {
        "PHASE7-001": test_phase7_001(),
        "PHASE7-002/003": test_phase7_002_003(),
    }

    # Summary
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " Test Summary".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print("")

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:<20} {status}")

    print("")
    print("Overall Status:", "✓ ALL TESTS PASSED" if all(results.values()) else "✗ SOME TESTS FAILED")
    print("")

    if all(results.values()):
        print("Next steps:")
        print("  1. Run pytest for full unit test coverage:")
        print("     pytest backend/tests/unit/ml/test_store_clustering.py -v")
        print("")
        print("  2. Run integration tests (requires full app setup):")
        print("     export OPENAI_API_KEY='your-key'")
        print("     pytest backend/tests/integration/test_inventory_agent_integration.py -v")
        print("")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
