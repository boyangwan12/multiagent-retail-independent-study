"""Unit tests for StoreClusterer (Phase 7 - Story 001)."""

import pytest
import pandas as pd
import numpy as np
from app.ml.store_clustering import StoreClusterer


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


def test_clustering_produces_3_clusters(sample_stores_data):
    """Test 1: K-means produces exactly 3 clusters."""
    clusterer = StoreClusterer(n_clusters=3)
    clusterer.fit(sample_stores_data)

    cluster_ids = clusterer.kmeans.labels_
    unique_clusters = np.unique(cluster_ids)

    assert len(unique_clusters) == 3, f"Expected 3 clusters, got {len(unique_clusters)}"
    assert set(unique_clusters) == {0, 1, 2}, f"Expected cluster IDs {{0, 1, 2}}, got {set(unique_clusters)}"


def test_standardscaler_normalization(sample_stores_data):
    """Test 2: StandardScaler applied correctly (mean≈0, std≈1)."""
    clusterer = StoreClusterer(n_clusters=3)
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
    clusterer = StoreClusterer(n_clusters=3)
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
    """Test 4: Silhouette score above 0.4 (good separation)."""
    clusterer = StoreClusterer(n_clusters=3)
    clusterer.fit(sample_stores_data)

    metrics = clusterer.get_cluster_quality_metrics()
    silhouette = metrics['silhouette_score']

    assert silhouette > 0.4, \
        f"Silhouette score {silhouette:.4f} below 0.4 threshold (clusters may overlap)"

    print(f"Silhouette score: {silhouette:.4f} (target: >0.4) ✓")


def test_cluster_percentages_sum_to_100(sample_stores_data):
    """Test 5: Cluster allocation percentages sum to exactly 100%."""
    clusterer = StoreClusterer(n_clusters=3)
    clusterer.fit(sample_stores_data)

    stats = clusterer.get_cluster_stats()
    percentages = stats['allocation_percentage'].values

    total = percentages.sum()
    assert abs(total - 100.0) < 0.1, \
        f"Cluster percentages sum to {total:.1f}%, expected 100.0%"

    print(f"Cluster allocation percentages:\n{stats[['cluster_label', 'allocation_percentage']].to_string()}")
    print(f"Sum: {total:.1f}% ✓")


def test_predict_cluster_consistency(sample_stores_data):
    """Test 6: Predict cluster returns same assignments as training."""
    clusterer = StoreClusterer(n_clusters=3)
    clusterer.fit(sample_stores_data)

    # Predict on same data
    predictions = clusterer.predict_cluster(sample_stores_data)
    training_clusters = clusterer.kmeans.labels_

    # Clusters should match (same stores should get same cluster IDs)
    assert np.array_equal(predictions, training_clusters), \
        "Predictions don't match training assignments"

    print(f"Prediction consistency: ✓")


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
    clusterer = StoreClusterer(n_clusters=3)
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

    print(f"Cluster stats format: ✓")
    print(f"\n{stats.to_string()}")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
