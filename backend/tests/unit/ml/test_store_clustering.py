"""Unit tests for StoreClusterer (Phase 7 - Story 001)."""

import pytest
import pandas as pd
import numpy as np
import os
from app.ml.store_clustering import StoreClusterer
from app.ml.data_mappers import create_diverse_synthetic_dataset


@pytest.fixture
def sample_stores_data():
    """
    Create sample store data for testing (50 stores × 7 features).

    Returns three natural clusters:
    - Fashion_Forward: 18 stores with high sales, premium positioning
    - Mainstream: 20 stores with medium sales
    - Value_Conscious: 12 stores with low sales, outlet format
    """
    np.random.seed(42)

    # Cluster 1: Fashion_Forward (18 stores)
    cluster1 = pd.DataFrame({
        'store_id': [f'FF_{i:03d}' for i in range(18)],
        'avg_weekly_sales_12mo': np.random.normal(850, 50, 18),  # High sales
        'store_size_sqft': np.random.normal(50000, 3000, 18),    # Large stores
        'median_income': np.random.normal(125000, 10000, 18),    # High income
        'location_tier': ['A'] * 18,                             # Premium location
        'fashion_tier': ['Premium'] * 18,                        # Premium positioning
        'store_format': ['Mall'] * 18,                           # Mall format
        'region': np.random.choice(['Northeast', 'West'], 18)    # Urban regions
    })

    # Cluster 2: Mainstream (20 stores)
    cluster2 = pd.DataFrame({
        'store_id': [f'MS_{i:03d}' for i in range(20)],
        'avg_weekly_sales_12mo': np.random.normal(650, 40, 20),  # Medium sales
        'store_size_sqft': np.random.normal(35000, 2000, 20),    # Medium stores
        'median_income': np.random.normal(85000, 8000, 20),      # Medium income
        'location_tier': ['B'] * 20,                             # Standard location
        'fashion_tier': ['Mainstream'] * 20,                     # Mainstream positioning
        'store_format': ['Standalone'] * 20,                     # Standalone format
        'region': np.random.choice(['Southeast', 'Midwest'], 20) # Regional stores
    })

    # Cluster 3: Value_Conscious (12 stores)
    cluster3 = pd.DataFrame({
        'store_id': [f'VC_{i:03d}' for i in range(12)],
        'avg_weekly_sales_12mo': np.random.normal(350, 30, 12),  # Low sales
        'store_size_sqft': np.random.normal(18000, 1500, 12),    # Small stores
        'median_income': np.random.normal(55000, 6000, 12),      # Low income
        'location_tier': ['C'] * 12,                             # Value location
        'fashion_tier': ['Value'] * 12,                          # Value positioning
        'store_format': ['Outlet'] * 12,                         # Outlet format
        'region': ['Midwest'] * 12                               # Rural stores
    })

    # Combine clusters
    stores_df = pd.concat([cluster1, cluster2, cluster3], ignore_index=True)

    return stores_df


@pytest.fixture(params=[
    'mock_clean',
    'realistic_1',
    'realistic_2'
], ids=lambda x: x)
def store_dataset(request):
    """
    Parametrized fixture that loads all 3 datasets.
    Each test using this fixture runs 3 times (once per dataset).

    Datasets:
    - mock_clean: Original clean mock (baseline, artificial separation)
    - realistic_1: Real store attributes mapped to clustering features
    - realistic_2: Synthetic diverse scenario with different distribution
    """
    dataset_type = request.param

    if dataset_type == 'mock_clean':
        # Original mock (clean baseline)
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
        return stores_df

    elif dataset_type == 'realistic_1':
        # Real store attributes mapped
        fixtures_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures')
        dataset_path = os.path.join(fixtures_path, 'realistic_stores_dataset1.csv')

        if not os.path.exists(dataset_path):
            pytest.skip(f"Dataset not found: {dataset_path}")

        return pd.read_csv(dataset_path)

    elif dataset_type == 'realistic_2':
        # Synthetic diverse scenario
        fixtures_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures')
        dataset_path = os.path.join(fixtures_path, 'realistic_stores_dataset2.csv')

        if not os.path.exists(dataset_path):
            # Generate on the fly if file not found
            return create_diverse_synthetic_dataset()

        return pd.read_csv(dataset_path)


def test_clustering_produces_3_clusters(sample_stores_data):
    """Test 1: K-means produces exactly 3 clusters."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(sample_stores_data)

    cluster_ids = clusterer.kmeans.labels_
    unique_clusters = np.unique(cluster_ids)

    assert len(unique_clusters) == 3, f"Expected 3 clusters, got {len(unique_clusters)}"
    assert set(unique_clusters) == {0, 1, 2}, f"Expected cluster IDs {{0, 1, 2}}, got {set(unique_clusters)}"


def test_standardscaler_normalization(sample_stores_data):
    """Test 2: StandardScaler applied correctly (mean≈0, std≈1)."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(sample_stores_data)

    # Get scaled features from scaler
    features = sample_stores_data[clusterer.REQUIRED_FEATURES].copy()

    # Apply ordinal encoding (same as fit)
    features['location_tier'] = features['location_tier'].map(clusterer.LOCATION_TIER_MAP)
    features['fashion_tier'] = features['fashion_tier'].map(clusterer.FASHION_TIER_MAP)
    features['store_format'] = features['store_format'].map(clusterer.STORE_FORMAT_MAP)
    features['region'] = features['region'].map(clusterer.REGION_MAP)

    scaled = clusterer.scaler.transform(features)

    # Check mean ≈ 0 and std ≈ 1 for each feature
    scaled_mean = np.abs(np.mean(scaled, axis=0))
    scaled_std = np.std(scaled, axis=0)

    assert np.all(scaled_mean < 0.01), f"Scaled mean not close to 0: {scaled_mean}"
    assert np.all(np.abs(scaled_std - 1.0) < 0.01), f"Scaled std not close to 1: {scaled_std}"


def test_cluster_labels_assigned_correctly(sample_stores_data):
    """Test 3: Cluster labels assigned by average sales."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(sample_stores_data)

    labels = clusterer.get_cluster_labels()

    # Verify all 3 labels present
    assert len(labels) == 3, f"Expected 3 labels, got {len(labels)}"
    assert set(labels.values()) == {
        "Fashion_Forward", "Mainstream", "Value_Conscious"
    }, f"Unexpected labels: {set(labels.values())}"

    # Verify Fashion_Forward has highest average sales
    training_data = clusterer.training_data_
    for cluster_id, label in labels.items():
        cluster_sales = training_data[training_data['cluster_id'] == cluster_id]['avg_weekly_sales_12mo'].mean()
        print(f"{label}: ${cluster_sales:.0f} avg sales")

    # Fashion_Forward should have highest sales
    fashion_forward_id = [k for k, v in labels.items() if v == "Fashion_Forward"][0]
    fashion_sales = training_data[training_data['cluster_id'] == fashion_forward_id]['avg_weekly_sales_12mo'].mean()

    value_conscious_id = [k for k, v in labels.items() if v == "Value_Conscious"][0]
    value_sales = training_data[training_data['cluster_id'] == value_conscious_id]['avg_weekly_sales_12mo'].mean()

    assert fashion_sales > value_sales, \
        f"Fashion_Forward (${fashion_sales:.0f}) should have higher sales than Value_Conscious (${value_sales:.0f})"


def test_silhouette_score_above_threshold(sample_stores_data):
    """Test 4: Silhouette score above 0.3 (good separation)."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(sample_stores_data)

    metrics = clusterer.get_cluster_quality_metrics()
    silhouette = metrics['silhouette_score']

    assert silhouette > 0.3, \
        f"Silhouette score {silhouette:.4f} below 0.3 threshold (clusters may overlap)"

    print(f"Silhouette score: {silhouette:.4f} (target: >0.3)")


def test_cluster_percentages_sum_to_100(sample_stores_data):
    """Test 5: Cluster allocation percentages sum to exactly 100%."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(sample_stores_data)

    stats = clusterer.get_cluster_stats()
    percentages = stats['allocation_percentage'].values

    total = percentages.sum()
    assert abs(total - 100.0) < 0.1, \
        f"Cluster percentages sum to {total:.1f}%, expected 100.0%"

    print(f"Cluster allocation percentages:\n{stats[['cluster_label', 'allocation_percentage']].to_string()}")
    print(f"Sum: {total:.1f}%")


def test_predict_cluster_consistency(sample_stores_data):
    """Test 6: Predict cluster returns same assignments as training."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(sample_stores_data)

    # Predict on same data
    predictions = clusterer.predict_cluster(sample_stores_data)
    training_clusters = clusterer.kmeans.labels_

    # Clusters should match (same stores should get same cluster IDs)
    assert np.array_equal(predictions, training_clusters), \
        "Predictions don't match training assignments"

    print(f"Prediction consistency: OK")


def test_missing_required_columns_raises_error():
    """Test 7: Fit raises error if required columns missing."""
    clusterer = StoreClusterer(n_clusters=3)

    # Create DataFrame with missing column
    bad_data = pd.DataFrame({
        'store_id': ['S001', 'S002', 'S003'],
        'avg_weekly_sales_12mo': [100, 200, 300],
        # Missing: store_size_sqft, median_income, location_tier, fashion_tier, store_format, region
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        clusterer.fit(bad_data)


def test_insufficient_data_raises_error():
    """Test 8: Fit raises error if fewer stores than clusters."""
    clusterer = StoreClusterer(n_clusters=3)

    # Create DataFrame with only 2 stores
    small_data = pd.DataFrame({
        'store_id': ['S001', 'S002'],
        'avg_weekly_sales_12mo': [100, 200],
        'store_size_sqft': [10000, 15000],
        'median_income': [50000, 60000],
        'location_tier': ['A', 'B'],
        'fashion_tier': ['Premium', 'Mainstream'],
        'store_format': ['Mall', 'Standalone'],
        'region': ['Northeast', 'Southeast']
    })

    with pytest.raises(ValueError, match="Insufficient stores"):
        clusterer.fit(small_data)


def test_predict_before_fit_raises_error(sample_stores_data):
    """Test 9: Predict before fit raises error."""
    clusterer = StoreClusterer(n_clusters=3)

    with pytest.raises(RuntimeError, match="Must call fit"):
        clusterer.predict_cluster(sample_stores_data)


def test_get_cluster_stats_format(sample_stores_data):
    """Test 10: get_cluster_stats returns correct DataFrame format."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(sample_stores_data)

    stats = clusterer.get_cluster_stats()

    # Check structure
    assert isinstance(stats, pd.DataFrame), "Stats should be DataFrame"
    assert len(stats) == 3, f"Stats should have 3 rows (one per cluster), got {len(stats)}"

    expected_cols = {
        'cluster_label', 'store_count', 'allocation_percentage',
        'avg_weekly_sales', 'avg_store_size', 'avg_median_income'
    }
    assert set(stats.columns) == expected_cols, \
        f"Stats columns don't match. Expected {expected_cols}, got {set(stats.columns)}"

    # Check cluster labels are correct
    labels = set(stats['cluster_label'])
    assert labels == {"Fashion_Forward", "Mainstream", "Value_Conscious"}, \
        f"Unexpected cluster labels: {labels}"

    # Check store_count sums to 50
    total_stores = stats['store_count'].sum()
    assert total_stores == 50, f"Total stores should be 50, got {total_stores}"

    # Check percentages sum to 100%
    total_pct = stats['allocation_percentage'].sum()
    assert abs(total_pct - 100.0) < 0.1, f"Percentages should sum to 100%, got {total_pct:.1f}%"

    print(f"Cluster stats format: OK")
    print(f"\n{stats.to_string()}")


def test_weighted_kmeans_produces_balanced_allocation(store_dataset):
    """Test with parametrized datasets: Weighted K-means produces balanced allocations."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(store_dataset)

    stats = clusterer.get_cluster_stats()
    allocations = stats['allocation_percentage'].values

    # No cluster should exceed 70% (prevents extreme imbalance)
    max_allocation = max(allocations)
    assert max_allocation < 70, \
        f"Cluster allocation too extreme: {max_allocation:.1f}% (should be <70%)"

    # All clusters should have meaningful size (>5%)
    min_allocation = min(allocations)
    assert min_allocation > 5, \
        f"Cluster too small: {min_allocation:.1f}% (should be >5%)"

    print(f"Allocations (balanced): {[f'{a:.1f}%' for a in allocations]}")


def test_feature_weights_applied(store_dataset):
    """Test: Feature weights are applied during clustering."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(store_dataset)

    # Verify weights are set
    assert clusterer.feature_weights is not None
    assert clusterer.feature_weights['avg_weekly_sales_12mo'] == 0.70, \
        "Sales should have 70% weight"
    assert sum(clusterer.feature_weights.values()) > 0.99, \
        "Weights should sum to ~1.0"


def test_adaptive_k_selection(store_dataset):
    """Test: Adaptive K-selection tests multiple K values."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=True)
    clusterer.fit(store_dataset)

    # Verify adaptive K info is populated
    assert clusterer.optimal_k_info_ is not None
    assert 'recommended_k' in clusterer.optimal_k_info_
    assert 'scores' in clusterer.optimal_k_info_
    assert len(clusterer.optimal_k_info_['scores']) >= 4  # At least K=2,3,4,5

    print(f"Adaptive K: {clusterer.optimal_k_info_['rationale']}")


def test_silhouette_acceptable_for_all_datasets(store_dataset):
    """Test with all datasets: Silhouette score >0.3 (realistic threshold)."""
    clusterer = StoreClusterer(n_clusters=3, adaptive_k=False)
    clusterer.fit(store_dataset)

    assert clusterer.silhouette_score_ > 0.3, \
        f"Silhouette {clusterer.silhouette_score_:.4f} below 0.3 threshold"

    print(f"Silhouette score: {clusterer.silhouette_score_:.4f} (target: >0.3)")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
