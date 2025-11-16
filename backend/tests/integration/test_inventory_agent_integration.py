"""Integration tests for Inventory Agent (Phase 7 - Story 004)."""

import pytest
import pandas as pd
import numpy as np
import asyncio
from app.agents.inventory_agent import InventoryAgent
from app.ml.store_clustering import StoreClusterer
from app.schemas.workflow_schemas import SeasonParameters


@pytest.fixture
def historical_data():
    """Create 52 weeks of historical sales data (12 months)."""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=52, freq='W')
    data = pd.DataFrame({
        'date': dates,
        'quantity_sold': np.random.normal(700, 150, 52).astype(int)
    })
    data['quantity_sold'] = data['quantity_sold'].clip(lower=100)  # Ensure positive
    return data


@pytest.fixture
def stores_data():
    """Create sample store data (50 stores × 7 features)."""
    np.random.seed(42)

    # Cluster 1: Fashion_Forward (18 stores)
    cluster1 = pd.DataFrame({
        'store_id': [f'FF_{i:03d}' for i in range(18)],
        'avg_weekly_sales_12mo': np.random.normal(850, 50, 18),
        'store_size_sqft': np.random.normal(50000, 3000, 18),
        'median_income': np.random.normal(125000, 10000, 18),
        'location_tier': ['A'] * 18,
        'fashion_tier': ['Premium'] * 18,
        'store_format': ['Mall'] * 18,
        'region': np.random.choice(['Northeast', 'West'], 18)
    })

    # Cluster 2: Mainstream (20 stores)
    cluster2 = pd.DataFrame({
        'store_id': [f'MS_{i:03d}' for i in range(20)],
        'avg_weekly_sales_12mo': np.random.normal(650, 40, 20),
        'store_size_sqft': np.random.normal(35000, 2000, 20),
        'median_income': np.random.normal(85000, 8000, 20),
        'location_tier': ['B'] * 20,
        'fashion_tier': ['Mainstream'] * 20,
        'store_format': ['Standalone'] * 20,
        'region': np.random.choice(['Southeast', 'Midwest'], 20)
    })

    # Cluster 3: Value_Conscious (12 stores)
    cluster3 = pd.DataFrame({
        'store_id': [f'VC_{i:03d}' for i in range(12)],
        'avg_weekly_sales_12mo': np.random.normal(350, 30, 12),
        'store_size_sqft': np.random.normal(18000, 1500, 12),
        'median_income': np.random.normal(55000, 6000, 12),
        'location_tier': ['C'] * 12,
        'fashion_tier': ['Value'] * 12,
        'store_format': ['Outlet'] * 12,
        'region': ['Midwest'] * 12
    })

    stores_df = pd.concat([cluster1, cluster2, cluster3], ignore_index=True)
    stores_df.set_index('store_id', inplace=True)

    return stores_df


@pytest.fixture
def demand_result_standard():
    """Create demand agent output for standard retail scenario."""
    return {
        'total_demand': 8000,
        'forecast_by_week': [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480],
        'safety_stock_pct': 0.20,
        'confidence': 0.85,
        'model_used': 'prophet_arima_ensemble'
    }


@pytest.fixture
def demand_result_zara():
    """Create demand agent output for fast fashion (Zara) scenario."""
    return {
        'total_demand': 8000,
        'forecast_by_week': [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480],
        'safety_stock_pct': 0.15,
        'confidence': 0.80,
        'model_used': 'prophet_arima_ensemble'
    }


@pytest.fixture
def parameters_standard():
    """Season parameters for standard retail (45% holdback, weekly replenishment)."""
    return SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date='2025-01-01',
        season_end_date='2025-03-31',
        replenishment_strategy='weekly',
        dc_holdback_percentage=0.45,
        markdown_checkpoint_week=8,
        markdown_threshold=0.60
    )


@pytest.fixture
def parameters_zara():
    """Season parameters for fast fashion (0% holdback, no replenishment)."""
    return SeasonParameters(
        forecast_horizon_weeks=12,
        season_start_date='2025-01-01',
        season_end_date='2025-03-31',
        replenishment_strategy='none',
        dc_holdback_percentage=0.0,
        markdown_checkpoint_week=4,
        markdown_threshold=0.60
    )


@pytest.mark.asyncio
async def test_end_to_end_phase6_to_phase7(
    demand_result_standard,
    stores_data,
    parameters_standard
):
    """
    Test 1: End-to-end Phase 6 → Phase 7 workflow.

    Verifies:
    - Phase 6 Demand Agent output accepted
    - Phase 7 Inventory Agent processes correctly
    - Output contract validated (InventoryAgentOutput schema)
    - Unit conservation verified
    - Manufacturing calculation correct
    """
    # Initialize Inventory Agent
    inventory_agent = InventoryAgent()

    # Execute allocation
    allocation_result = await inventory_agent.execute(
        forecast_result=demand_result_standard,
        parameters=parameters_standard,
        stores_data=stores_data
    )

    # Verify Phase 6 → Phase 7 handoff working
    assert 'total_demand' in demand_result_standard
    assert 'manufacturing_qty' in allocation_result

    # Verify manufacturing calculation
    expected_manufacturing = int(
        demand_result_standard['total_demand'] * (1 + demand_result_standard['safety_stock_pct'])
    )
    assert allocation_result['manufacturing_qty'] == expected_manufacturing

    # Verify DC holdback (45%)
    assert allocation_result['dc_holdback_total'] == int(expected_manufacturing * 0.45)
    assert allocation_result['initial_allocation_total'] == int(expected_manufacturing * 0.55)

    # Verify unit conservation
    assert (
        allocation_result['initial_allocation_total'] +
        allocation_result['dc_holdback_total']
    ) == expected_manufacturing

    # Verify clusters present
    assert len(allocation_result['clusters']) == 3

    # Verify store allocations sum correctly
    total_store_allocation = sum(
        sum(store['initial_allocation'] for store in cluster['stores'])
        for cluster in allocation_result['clusters']
    )
    assert total_store_allocation == allocation_result['initial_allocation_total']

    print(f"Test 1 PASSED: End-to-end workflow OK")
    print(f"  Manufacturing: {expected_manufacturing} units")
    print(f"  DC Holdback: {allocation_result['dc_holdback_total']} units (45%)")
    print(f"  Store Allocation: {allocation_result['initial_allocation_total']} units (55%)")


@pytest.mark.asyncio
async def test_parameter_driven_0_percent_holdback(
    demand_result_zara,
    stores_data,
    parameters_zara
):
    """
    Test 2: Parameter-driven behavior - 0% holdback (Zara scenario).

    Verifies:
    - 0% DC holdback applied correctly
    - 100% initial allocation
    - Replenishment disabled (strategy='none')
    - No replenishment queue generated
    """
    # Initialize Inventory Agent
    inventory_agent = InventoryAgent()

    # Execute allocation
    allocation_result = await inventory_agent.execute(
        forecast_result=demand_result_zara,
        parameters=parameters_zara,
        stores_data=stores_data
    )

    # Verify 0% DC holdback
    assert allocation_result['dc_holdback_total'] == 0

    # Verify 100% initial allocation
    assert allocation_result['initial_allocation_total'] == allocation_result['manufacturing_qty']

    # Verify replenishment disabled
    assert allocation_result['replenishment_enabled'] == False
    assert allocation_result['replenishment_queue'] == []

    # Verify 100% allocated to stores
    total_store_allocation = sum(
        sum(store['initial_allocation'] for store in cluster['stores'])
        for cluster in allocation_result['clusters']
    )
    assert total_store_allocation == allocation_result['manufacturing_qty']

    print(f"Test 2 PASSED: Zara scenario (0% holdback, no replenishment)")
    print(f"  Manufacturing: {allocation_result['manufacturing_qty']} units")
    print(f"  DC Holdback: {allocation_result['dc_holdback_total']} (0%)")
    print(f"  Store Allocation: {allocation_result['initial_allocation_total']} (100%)")
    print(f"  Replenishment Enabled: {allocation_result['replenishment_enabled']}")


@pytest.mark.asyncio
async def test_parameter_driven_45_percent_holdback(
    demand_result_standard,
    stores_data,
    parameters_standard
):
    """
    Test 3: Parameter-driven behavior - 45% holdback (Standard retail scenario).

    Verifies:
    - 45% DC holdback applied correctly
    - 55% initial allocation
    - Replenishment enabled (strategy='weekly')
    - Parameter-based configuration working
    """
    # Initialize Inventory Agent
    inventory_agent = InventoryAgent()

    # Execute allocation
    allocation_result = await inventory_agent.execute(
        forecast_result=demand_result_standard,
        parameters=parameters_standard,
        stores_data=stores_data
    )

    # Verify 45% DC holdback
    expected_holdback = int(allocation_result['manufacturing_qty'] * 0.45)
    expected_initial = allocation_result['manufacturing_qty'] - expected_holdback
    assert allocation_result['dc_holdback_total'] == expected_holdback
    assert allocation_result['initial_allocation_total'] == expected_initial

    # Verify replenishment enabled
    assert allocation_result['replenishment_enabled'] == True

    # Verify 55% allocated to stores
    total_store_allocation = sum(
        sum(store['initial_allocation'] for store in cluster['stores'])
        for cluster in allocation_result['clusters']
    )
    assert total_store_allocation == expected_initial

    print(f"Test 3 PASSED: Standard retail scenario (45% holdback, weekly replenishment)")
    print(f"  Manufacturing: {allocation_result['manufacturing_qty']} units")
    print(f"  DC Holdback: {expected_holdback} ({45}%)")
    print(f"  Store Allocation: {expected_initial} ({55}%)")
    print(f"  Replenishment Enabled: {allocation_result['replenishment_enabled']}")


@pytest.mark.asyncio
async def test_performance_under_15_seconds(
    demand_result_standard,
    stores_data,
    parameters_standard
):
    """
    Test 4: Performance test - Phase 6 + Phase 7 completes in <15 seconds.

    Verifies:
    - Entire workflow completes quickly
    - Performance target met
    - No blocking I/O or long operations
    """
    import time

    start_time = time.time()

    # Initialize and execute Inventory Agent
    inventory_agent = InventoryAgent()
    allocation_result = await inventory_agent.execute(
        forecast_result=demand_result_standard,
        parameters=parameters_standard,
        stores_data=stores_data
    )

    elapsed_time = time.time() - start_time

    # Verify performance target
    assert elapsed_time < 15.0, f"Workflow took {elapsed_time:.2f}s (target: <15s)"

    print(f"Test 4 PASSED: Performance test")
    print(f"  Elapsed time: {elapsed_time:.2f} seconds (target: <15s)")
    print(f"  Manufacturing: {allocation_result['manufacturing_qty']} units")
    print(f"  Clusters: {len(allocation_result['clusters'])}")
    print(f"  Stores: 50")


def test_cluster_quality_metrics(stores_data):
    """
    Test 5: Cluster quality validation - silhouette score >0.4.

    Verifies:
    - K-means clustering produces good separation
    - Silhouette score above quality threshold
    """
    clusterer = StoreClusterer(n_clusters=3)
    clusterer.fit(stores_data)

    metrics = clusterer.get_cluster_quality_metrics()
    silhouette = metrics['silhouette_score']

    # Verify quality threshold
    assert silhouette > 0.4, \
        f"Silhouette score {silhouette:.4f} below 0.4 threshold (clusters may overlap)"

    print(f"Test 5 PASSED: Cluster quality metrics")
    print(f"  Silhouette Score: {silhouette:.4f} (target: >0.4)")
    print(f"  Clusters: {metrics['n_clusters']}")


def test_allocation_contract_validation(demand_result_standard, stores_data, parameters_standard):
    """
    Test 6: Output contract validation (InventoryAgentOutput schema).

    Verifies:
    - All required output fields present
    - Correct data types
    - Valid values
    """
    inventory_agent = InventoryAgent()

    # Execute synchronously for this test
    loop = asyncio.new_event_loop()
    allocation_result = loop.run_until_complete(
        inventory_agent.execute(
            forecast_result=demand_result_standard,
            parameters=parameters_standard,
            stores_data=stores_data
        )
    )
    loop.close()

    # Validate required fields
    required_fields = {
        'manufacturing_qty': int,
        'safety_stock_pct': float,
        'initial_allocation_total': int,
        'dc_holdback_total': int,
        'clusters': list,
        'replenishment_enabled': bool,
        'replenishment_queue': list
    }

    for field, expected_type in required_fields.items():
        assert field in allocation_result, f"Missing required field: {field}"
        assert isinstance(allocation_result[field], expected_type), \
            f"Field {field} has wrong type: {type(allocation_result[field])} (expected {expected_type})"

    # Validate cluster structure
    for cluster in allocation_result['clusters']:
        assert 'cluster_id' in cluster
        assert 'cluster_label' in cluster
        assert 'allocation_percentage' in cluster
        assert 'total_units' in cluster
        assert 'stores' in cluster
        assert isinstance(cluster['stores'], list)

    # Validate store structure
    for cluster in allocation_result['clusters']:
        for store in cluster['stores']:
            assert 'store_id' in store
            assert 'cluster' in store
            assert 'initial_allocation' in store
            assert 'allocation_factor' in store

    print(f"Test 6 PASSED: Output contract validation")
    print(f"  Clusters: {len(allocation_result['clusters'])}")
    total_stores = sum(len(c['stores']) for c in allocation_result['clusters'])
    print(f"  Stores: {total_stores}")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short', '--asyncio-mode=auto'])
