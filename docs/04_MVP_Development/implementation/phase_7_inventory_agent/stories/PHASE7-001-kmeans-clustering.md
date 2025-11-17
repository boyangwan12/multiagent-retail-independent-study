# Story: Implement K-means Store Clustering

**Epic:** Phase 7 - Inventory Agent
**Story ID:** PHASE7-001
**Status:** ✅ Complete
**Estimate:** 8 hours
**Agent:** `*agent dev`
**Dependencies:** Phase 6 complete

**Planning References:**
- PRD v3.3: Section 5.2 (Store Clustering)
- Technical Architecture v3.3: Section 4.5 (ML Pipeline - K-means)
- technical_decisions.md: TD-7.1 (K-means K=3), TD-7.2 (7 Features), TD-7.3 (StandardScaler), TD-7.4 (Cluster Labeling)

---

## Story

As a backend developer,
I want to implement K-means clustering to segment 50 stores into 3 performance tiers,
So that the system can intelligently allocate inventory based on store characteristics and historical performance.

**Business Value:** Store clustering enables hierarchical allocation (category → cluster → store) which improves allocation accuracy compared to uniform distribution. K-means with 7 features captures performance, capacity, and demographic patterns, reducing stockouts in high-demand stores and overstock in low-demand stores.

**Epic Context:** This is Story 1 of 4 in Phase 7. K-means clustering is the foundation for allocation logic (Story 2). The clusters produced here (Fashion_Forward, Mainstream, Value_Conscious) will be used throughout the allocation and replenishment workflows.

---

## Acceptance Criteria

### Functional Requirements

1. ☐ StoreClusterer class created in `backend/app/ml/store_clustering.py`
2. ☐ K-means clustering uses K=3 (fixed) with K-means++ initialization
3. ☐ 7 features loaded from store attributes:
   - avg_weekly_sales_12mo (most important)
   - store_size_sqft
   - median_income
   - location_tier (ordinal: A=3, B=2, C=1)
   - fashion_tier (ordinal: Premium=3, Mainstream=2, Value=1)
   - store_format (ordinal: Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1)
   - region (ordinal: Northeast=1, Southeast=2, Midwest=3, West=4)
4. ☐ StandardScaler normalization applied (mean=0, std=1)
5. ☐ Cluster labels assigned automatically:
   - Fashion_Forward (highest avg_weekly_sales)
   - Mainstream (medium avg_weekly_sales)
   - Value_Conscious (lowest avg_weekly_sales)
6. ☐ Cluster allocation percentages calculated based on cluster total sales
7. ☐ Silhouette score calculated and validated (>0.4 target)

### Quality Requirements

8. ☐ Clustering completes in <1 second (50 stores)
9. ☐ Silhouette score >0.4 on test data (good separation)
10. ☐ Cluster percentages sum to 100%
11. ☐ All docstrings complete (Google style)
12. ☐ 5 unit tests written and passing
13. ☐ Type hints on all methods
14. ☐ Logging informative (cluster assignments, scores)

---

## Prerequisites

**Phase 6 Complete:**
- [x] Demand Agent operational
- [x] Forecast output available

**Python Libraries:**
- [ ] scikit-learn installed (`uv add scikit-learn`)
- [ ] Test import: `from sklearn.cluster import KMeans; from sklearn.preprocessing import StandardScaler`

**Data Available:**
- [ ] Store attributes CSV with 50 stores × 7 features
- [ ] Store attributes loaded into database or DataFrame

---

## Tasks

### Task 1: Create StoreClusterer Class Skeleton

**Goal:** Define class structure and method signatures

**Subtasks:**
- [ ] Create file: `backend/app/ml/store_clustering.py`
- [ ] Define `StoreClusterer` class
- [ ] Add `__init__(self, n_clusters=3, random_state=42)` method
- [ ] Add `fit(self, store_features: pd.DataFrame) -> None` method stub
- [ ] Add `predict_cluster(self, store_features: pd.DataFrame) -> np.ndarray` method stub
- [ ] Add `get_cluster_labels(self) -> Dict[int, str]` method stub
- [ ] Add `get_cluster_stats(self) -> pd.DataFrame` method stub
- [ ] Add type hints and docstrings

**Code Template:**
```python
from typing import Dict, Optional
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import logging

logger = logging.getLogger(__name__)

class StoreClusterer:
    """K-means clustering for store segmentation.

    Segments stores into 3 performance tiers (Fashion_Forward, Mainstream,
    Value_Conscious) using 7 features with StandardScaler normalization.

    Attributes:
        n_clusters: Number of clusters (default: 3)
        random_state: Random seed for reproducibility
        kmeans: Trained KMeans model instance
        scaler: StandardScaler instance for normalization
        cluster_labels_: Dict mapping cluster IDs to labels
        silhouette_score_: Silhouette score for cluster quality
    """

    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        """Initialize StoreClusterer with K-means parameters."""
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans: Optional[KMeans] = None
        self.scaler: Optional[StandardScaler] = None
        self.cluster_labels_: Optional[Dict[int, str]] = None
        self.silhouette_score_: Optional[float] = None
        logger.info(f"StoreClusterer initialized (K={n_clusters})")

    def fit(self, store_features: pd.DataFrame) -> None:
        """Fit K-means clustering on store features.

        Args:
            store_features: DataFrame with 7 required columns
        """
        pass

    def predict_cluster(self, store_features: pd.DataFrame) -> np.ndarray:
        """Predict cluster assignments for stores.

        Args:
            store_features: DataFrame with same features as training

        Returns:
            Array of cluster IDs (0, 1, 2)
        """
        pass

    def get_cluster_labels(self) -> Dict[int, str]:
        """Get cluster labels mapping (0 → Fashion_Forward, etc.).

        Returns:
            Dict mapping cluster IDs to labels
        """
        pass

    def get_cluster_stats(self) -> pd.DataFrame:
        """Get cluster statistics (means, sizes, percentages).

        Returns:
            DataFrame with cluster characteristics
        """
        pass
```

---

### Task 2: Implement fit() Method with StandardScaler

**Goal:** Train K-means model with proper normalization

**Subtasks:**
- [ ] Validate input DataFrame has 7 required columns
- [ ] Extract 7 features:
  ```python
  required_features = [
      'avg_weekly_sales_12mo',
      'store_size_sqft',
      'median_income',
      'location_tier',
      'fashion_tier',
      'store_format',
      'region'
  ]
  features_df = store_features[required_features].copy()
  ```
- [ ] Apply ordinal encoding for categorical features:
  ```python
  # Encode location_tier: A=3, B=2, C=1
  tier_map = {'A': 3, 'B': 2, 'C': 1}
  features_df['location_tier'] = features_df['location_tier'].map(tier_map)

  # Encode fashion_tier: Premium=3, Mainstream=2, Value=1
  fashion_map = {'Premium': 3, 'Mainstream': 2, 'Value': 1}
  features_df['fashion_tier'] = features_df['fashion_tier'].map(fashion_map)

  # Encode store_format: Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1
  format_map = {'Mall': 4, 'Standalone': 3, 'ShoppingCenter': 2, 'Outlet': 1}
  features_df['store_format'] = features_df['store_format'].map(format_map)

  # Encode region: Northeast=1, Southeast=2, Midwest=3, West=4
  region_map = {'Northeast': 1, 'Southeast': 2, 'Midwest': 3, 'West': 4}
  features_df['region'] = features_df['region'].map(region_map)
  ```
- [ ] Initialize and fit StandardScaler:
  ```python
  self.scaler = StandardScaler()
  features_scaled = self.scaler.fit_transform(features_df)
  ```
- [ ] Initialize and fit K-means with K-means++:
  ```python
  self.kmeans = KMeans(
      n_clusters=self.n_clusters,
      init='k-means++',
      random_state=self.random_state,
      n_init=10  # Run 10 times, pick best
  )
  self.kmeans.fit(features_scaled)
  ```
- [ ] Calculate silhouette score:
  ```python
  cluster_labels = self.kmeans.labels_
  self.silhouette_score_ = silhouette_score(features_scaled, cluster_labels)
  logger.info(f"Silhouette score: {self.silhouette_score_:.2f}")
  ```
- [ ] Warn if silhouette <0.4:
  ```python
  if self.silhouette_score_ < 0.4:
      logger.warning(f"Silhouette score {self.silhouette_score_:.2f} below 0.4 - clusters may overlap")
  ```
- [ ] Store training data for cluster stats calculation
- [ ] Log clustering complete

**Acceptance:**
- fit() runs successfully with 50 stores
- Silhouette score >0.4 on test data
- StandardScaler applied correctly

---

### Task 3: Implement predict_cluster() Method

**Goal:** Predict cluster assignments for new stores

**Subtasks:**
- [ ] Check if model is trained (raise error if not)
- [ ] Extract and encode features (same as fit())
- [ ] Apply scaler transformation:
  ```python
  features_scaled = self.scaler.transform(features_df)
  ```
- [ ] Predict clusters:
  ```python
  cluster_ids = self.kmeans.predict(features_scaled)
  ```
- [ ] Return cluster IDs as numpy array

**Acceptance:**
- predict_cluster() returns correct cluster IDs
- Works with both single store and multiple stores
- Raises error if model not trained

---

### Task 4: Implement get_cluster_labels() Method

**Goal:** Automatically assign meaningful labels to clusters

**Subtasks:**
- [ ] Extract cluster assignments from training data
- [ ] Calculate cluster means for key features:
  ```python
  cluster_means = training_data.groupby('cluster_id').agg({
      'avg_weekly_sales_12mo': 'mean',
      'fashion_tier': 'mean',
      'median_income': 'mean'
  })
  ```
- [ ] Sort clusters by avg_weekly_sales (descending):
  ```python
  sorted_clusters = cluster_means.sort_values('avg_weekly_sales_12mo', ascending=False)
  ```
- [ ] Assign labels:
  ```python
  self.cluster_labels_ = {
      sorted_clusters.index[0]: "Fashion_Forward",   # Highest sales
      sorted_clusters.index[1]: "Mainstream",        # Medium sales
      sorted_clusters.index[2]: "Value_Conscious"    # Lowest sales
  }
  ```
- [ ] Log cluster assignments:
  ```python
  for cluster_id, label in self.cluster_labels_.items():
      avg_sales = cluster_means.loc[cluster_id, 'avg_weekly_sales_12mo']
      logger.info(f"Cluster {cluster_id} → {label} (avg sales: {avg_sales:.0f})")
  ```
- [ ] Return cluster labels dict

**Acceptance:**
- Cluster labels assigned correctly (highest sales = Fashion_Forward)
- Labels logged for transparency
- Dict returned with correct format

---

### Task 5: Implement get_cluster_stats() Method

**Goal:** Calculate cluster characteristics and allocation percentages

**Subtasks:**
- [ ] Calculate cluster sizes (store counts):
  ```python
  cluster_sizes = training_data.groupby('cluster_id').size()
  ```
- [ ] Calculate cluster means for all 7 features:
  ```python
  cluster_means = training_data.groupby('cluster_id')[required_features].mean()
  ```
- [ ] Calculate cluster total sales:
  ```python
  cluster_totals = training_data.groupby('cluster_id')['avg_weekly_sales_12mo'].sum()
  ```
- [ ] Calculate cluster allocation percentages:
  ```python
  total_sales = cluster_totals.sum()
  cluster_percentages = (cluster_totals / total_sales * 100).round(1)
  ```
- [ ] Validate percentages sum to 100%:
  ```python
  assert abs(cluster_percentages.sum() - 100.0) < 0.1, "Percentages must sum to 100%"
  ```
- [ ] Combine into stats DataFrame:
  ```python
  stats_df = pd.DataFrame({
      'cluster_label': [self.cluster_labels_[i] for i in cluster_means.index],
      'store_count': cluster_sizes,
      'allocation_percentage': cluster_percentages,
      'avg_weekly_sales': cluster_means['avg_weekly_sales_12mo'],
      'avg_store_size': cluster_means['store_size_sqft'],
      'avg_median_income': cluster_means['median_income']
  })
  ```
- [ ] Return stats DataFrame

**Acceptance:**
- Cluster stats calculated correctly
- Allocation percentages sum to 100%
- Stats DataFrame format matches expected structure

---

### Task 6: Write Unit Tests

**Goal:** Verify StoreClusterer functionality

**Subtasks:**
- [ ] Create file: `backend/tests/unit/ml/test_store_clustering.py`
- [ ] Create test fixture with sample store data (50 stores)
- [ ] **Test 1:** `test_clustering_produces_3_clusters()`
  - Train clusterer, assert 3 unique cluster IDs
- [ ] **Test 2:** `test_standardscaler_normalization()`
  - Verify scaler applied, check mean≈0, std≈1
- [ ] **Test 3:** `test_cluster_labels_assigned_correctly()`
  - Verify Fashion_Forward has highest avg sales
  - Verify Value_Conscious has lowest avg sales
- [ ] **Test 4:** `test_silhouette_score_above_threshold()`
  - Assert silhouette score >0.4
- [ ] **Test 5:** `test_cluster_percentages_sum_to_100()`
  - Get cluster stats, assert sum(percentages) == 100.0

**Acceptance:**
- All 5 tests pass
- Test coverage >90% for StoreClusterer

---

## Testing Strategy

### Unit Tests (This Story)
- Test clustering with valid data
- Test StandardScaler normalization
- Test cluster label assignment
- Test silhouette score calculation
- Test cluster stats calculation

### Integration Tests (Story 4)
- Integration with Inventory Agent
- Integration with Phase 6 Demand Agent

### Performance Tests
- Clustering time: <1 second (50 stores)

---

## Definition of Done

**Code Complete:**
- [ ] StoreClusterer class implemented
- [ ] fit() method with StandardScaler working
- [ ] predict_cluster() method working
- [ ] get_cluster_labels() method working
- [ ] get_cluster_stats() method working
- [ ] Type hints and docstrings complete

**Testing Complete:**
- [ ] 5 unit tests passing
- [ ] Silhouette score >0.4 on test data
- [ ] Test coverage >90%

**Quality Checks:**
- [ ] Code follows project style
- [ ] Error handling complete
- [ ] Logging informative
- [ ] No print statements

**Documentation:**
- [ ] Docstrings complete
- [ ] Clustering algorithm explained in code comments
- [ ] Ready for Story 2 (Allocation Logic)

---

## Notes

**K-means++ Initialization:**
- K-means++ improves initial centroid selection
- Results in better clustering quality and faster convergence
- Compared to random initialization, K-means++ reduces iterations by ~50%

**Silhouette Score Interpretation:**
- **>0.7:** Excellent separation (clusters well-defined)
- **0.5-0.7:** Good separation (reasonable clustering)
- **0.4-0.5:** Fair separation (acceptable for MVP)
- **<0.4:** Poor separation (clusters overlap) → Flag for review

**Feature Importance (Expected):**
- `avg_weekly_sales_12mo`: Primary differentiator (60-70% weight)
- `store_size_sqft`: Secondary (capacity constraint)
- `median_income`, `location_tier`, `fashion_tier`: Tertiary (10-20% combined)
- `store_format`, `region`: Minor (regional patterns)

**Ordinal Encoding Rationale:**
- Location Tier: A > B > C (clear hierarchy)
- Fashion Tier: Premium > Mainstream > Value (positioning hierarchy)
- Store Format: Mall > Standalone > ShoppingCenter > Outlet (foot traffic/sales potential)
- Region: Arbitrary (1-4 encoding, captures regional differences)

**Common Issues:**
- **Low Silhouette Score (<0.4):** May need to adjust K or add/remove features
- **Uneven Cluster Sizes:** Normal - reflects real store distribution
- **Cluster Labels Swapped:** Automatic labeling by sales may assign different IDs each run

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
