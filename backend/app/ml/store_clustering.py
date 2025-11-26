"""K-means clustering for store segmentation (Phase 7 - Story 001)."""

from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import logging

logger = logging.getLogger("fashion_forecast")


class StoreClusterer:
    """
    Weighted K-means clustering for store segmentation.

    Segments stores into performance tiers using 7 features with weighted importance:
    - Sales feature (70% weight) - primary allocation driver
    - Other features (30% weight combined) - secondary influence

    **Features:**
    1. avg_weekly_sales_12mo - 12-month average weekly sales
    2. store_size_sqft - Store square footage
    3. median_income - Median income of surrounding area
    4. location_tier - Location tier (A/B/C ordinal: 3/2/1)
    5. fashion_tier - Fashion positioning (Premium/Mainstream/Value: 3/2/1)
    6. store_format - Store format (Mall/Standalone/ShoppingCenter/Outlet: 4/3/2/1)
    7. region - Geographic region (Northeast/Southeast/Midwest/West: 1/2/3/4)

    **Attributes:**
        n_clusters: Number of clusters (default: 3)
        random_state: Random seed for reproducibility
        adaptive_k: If True, test K=2,3,4,5 and recommend optimal K
        feature_weights: Dict mapping features to importance weights
        kmeans: Trained KMeans model instance
        scaler: StandardScaler instance for normalization
        cluster_labels_: Dict mapping cluster IDs to labels
        silhouette_score_: Silhouette score for cluster quality
        training_data_: Original training data with cluster assignments
        optimal_k_info_: Information from adaptive K selection
    """

    # Required features for clustering
    REQUIRED_FEATURES = [
        'avg_weekly_sales_12mo',
        'store_size_sqft',
        'median_income',
        'location_tier',
        'fashion_tier',
        'store_format',
        'region'
    ]

    # Ordinal encoding mappings
    LOCATION_TIER_MAP = {'A': 3, 'B': 2, 'C': 1}
    FASHION_TIER_MAP = {'Premium': 3, 'Mainstream': 2, 'Value': 1}
    STORE_FORMAT_MAP = {'Mall': 4, 'Standalone': 3, 'ShoppingCenter': 2, 'Outlet': 1}
    REGION_MAP = {'Northeast': 1, 'Southeast': 2, 'Midwest': 3, 'West': 4}

    # Default feature weights (sales-first approach for balanced allocation)
    DEFAULT_FEATURE_WEIGHTS = {
        'avg_weekly_sales_12mo': 0.70,  # Primary: allocation driver
        'store_size_sqft': 0.05,        # Secondary: capacity
        'median_income': 0.10,          # Secondary: market tier
        'location_tier': 0.05,          # Tertiary: location quality
        'fashion_tier': 0.05,           # Tertiary: positioning
        'store_format': 0.03,           # Tertiary: format type
        'region': 0.02                  # Tertiary: geographic distribution
    }

    def __init__(
        self,
        n_clusters: int = 3,
        random_state: int = 42,
        adaptive_k: bool = True,
        feature_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize StoreClusterer with weighted K-means parameters.

        Args:
            n_clusters: Initial K (default: 3, may be adjusted if adaptive_k=True)
            random_state: Random seed for reproducibility (default: 42)
            adaptive_k: If True, test K=2,3,4,5 and recommend best K (default: True)
            feature_weights: Dict of feature → weight (default: sales-first weighting)
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.adaptive_k = adaptive_k
        self.feature_weights = feature_weights or self.DEFAULT_FEATURE_WEIGHTS
        self.kmeans: Optional[KMeans] = None
        self.scaler: Optional[StandardScaler] = None
        self.cluster_labels_: Optional[Dict[int, str]] = None
        self.silhouette_score_: Optional[float] = None
        self.training_data_: Optional[pd.DataFrame] = None
        self.optimal_k_info_: Optional[Dict] = None
        logger.info(
            f"StoreClusterer initialized (K={n_clusters}, adaptive_k={adaptive_k}, "
            f"random_state={random_state})"
        )
        logger.info(f"Feature weights: {self.feature_weights}")

    def fit(self, store_features: pd.DataFrame) -> None:
        """
        Fit weighted K-means clustering on store features.

        **Process:**
        1. Validate input DataFrame has required columns
        2. Extract and encode features (ordinal encoding for categoricals)
        3. Apply StandardScaler normalization (mean=0, std=1)
        4. Apply feature weights (sales=70%, others=30% distributed)
        5. [ADAPTIVE] Find optimal K if enabled (test K=2,3,4,5)
        6. Train K-means++ with chosen K
        7. Calculate silhouette score
        8. Assign cluster labels (by avg_weekly_sales)

        **Feature Weighting:**
        Sales feature (avg_weekly_sales_12mo) gets 70% weight to drive
        cluster separation, while other features (size, income, tiers) get
        30% combined weight. This prevents equal-weighting issues that cause
        extreme allocation imbalances.

        Args:
            store_features: DataFrame with 7 required columns (rows = stores)

        Raises:
            ValueError: If required columns missing or insufficient data

        Example:
            >>> clusterer = StoreClusterer(adaptive_k=False)
            >>> clusterer.fit(stores_df)  # 50 stores × 7 features
            >>> labels = clusterer.get_cluster_labels()
            >>> stats = clusterer.get_cluster_stats()
        """
        logger.info(f"Fitting weighted K-means clustering on {len(store_features)} stores...")

        # Validate input
        missing_cols = set(self.REQUIRED_FEATURES) - set(store_features.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        if len(store_features) < self.n_clusters:
            raise ValueError(
                f"Insufficient stores ({len(store_features)}) for {self.n_clusters} clusters"
            )

        # Extract features
        features_df = store_features[self.REQUIRED_FEATURES].copy()

        # Encode categorical features (ordinal)
        if 'location_tier' in features_df.columns:
            features_df['location_tier'] = features_df['location_tier'].map(self.LOCATION_TIER_MAP)

        if 'fashion_tier' in features_df.columns:
            features_df['fashion_tier'] = features_df['fashion_tier'].map(self.FASHION_TIER_MAP)

        if 'store_format' in features_df.columns:
            features_df['store_format'] = features_df['store_format'].map(self.STORE_FORMAT_MAP)

        if 'region' in features_df.columns:
            features_df['region'] = features_df['region'].map(self.REGION_MAP)

        # Normalize features with StandardScaler
        logger.info("Applying StandardScaler normalization (mean=0, std=1)...")
        self.scaler = StandardScaler()
        features_scaled = self.scaler.fit_transform(features_df)

        # Apply feature weights (NEW: weighted clustering)
        logger.info("Applying feature weights to normalized features...")
        features_scaled_weighted = self._apply_feature_weights(features_scaled, features_df.columns)

        # [ADAPTIVE] Find optimal K if enabled
        if self.adaptive_k:
            self.optimal_k_info_ = self._find_optimal_k(features_scaled_weighted)
            optimal_k = self.optimal_k_info_['recommended_k']
            logger.info(
                f"Adaptive K selection: Recommended K={optimal_k} "
                f"(rationale: {self.optimal_k_info_['rationale']})"
            )
            self.n_clusters = optimal_k

        # Train K-means with chosen K
        logger.info(f"Training K-means++ (K={self.n_clusters}, n_init=10)...")
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            init='k-means++',
            random_state=self.random_state,
            n_init=10,  # Run 10 times, pick best
            verbose=0
        )
        self.kmeans.fit(features_scaled_weighted)

        # Calculate silhouette score
        cluster_labels = self.kmeans.labels_
        self.silhouette_score_ = silhouette_score(features_scaled_weighted, cluster_labels)
        logger.info(f"Silhouette score: {self.silhouette_score_:.4f} (target: >0.3 for realistic data)")

        if self.silhouette_score_ < 0.3:
            logger.warning(
                f"Silhouette score {self.silhouette_score_:.4f} below 0.3 - "
                "clusters overlap significantly (expected with real data)"
            )

        # Store training data with cluster assignments
        self.training_data_ = store_features.copy()
        self.training_data_['cluster_id'] = cluster_labels

        # Assign cluster labels based on average sales
        self._assign_cluster_labels()

        logger.info("Weighted K-means clustering complete")

    def _assign_cluster_labels(self) -> None:
        """
        Automatically assign meaningful labels to clusters.

        **Labels assigned by avg_weekly_sales (descending):**
        - Highest sales → Fashion_Forward
        - Medium sales → Mainstream (if K=3)
        - Lowest sales → Value_Conscious

        **Internal method - called by fit().**
        Handles variable K (adaptive K may choose K≠3).
        """
        if self.training_data_ is None or self.kmeans is None:
            raise RuntimeError("Must call fit() before assigning labels")

        # Create a copy with numeric only columns for mean calculation
        numeric_data = self.training_data_[['cluster_id', 'avg_weekly_sales_12mo', 'median_income']].copy()

        # Calculate cluster means for key numeric features
        cluster_means = numeric_data.groupby('cluster_id').agg({
            'avg_weekly_sales_12mo': 'mean',
            'median_income': 'mean'
        })

        # Sort clusters by avg_weekly_sales (descending)
        sorted_clusters = cluster_means.sort_values('avg_weekly_sales_12mo', ascending=False)

        # Assign labels based on number of clusters
        label_names = ["Fashion_Forward", "Mainstream", "Value_Conscious"]
        self.cluster_labels_ = {}

        for i, cluster_id in enumerate(sorted_clusters.index):
            # Map to label based on position and K value
            if len(sorted_clusters) == 2:
                # For K=2: top cluster is Fashion_Forward, bottom is Value_Conscious
                label = "Fashion_Forward" if i == 0 else "Value_Conscious"
            elif len(sorted_clusters) == 3:
                # For K=3: standard 3-tier system
                label = label_names[i]
            else:
                # For K>3: use first 3 names, then generic tier labels
                if i < 3:
                    label = label_names[i]
                else:
                    label = f"Tier_{i+1}"

            self.cluster_labels_[cluster_id] = label

        # Log assignments
        for cluster_id, label in self.cluster_labels_.items():
            avg_sales = cluster_means.loc[cluster_id, 'avg_weekly_sales_12mo']
            store_count = len(self.training_data_[self.training_data_['cluster_id'] == cluster_id])
            logger.info(
                f"Cluster {cluster_id} → {label} "
                f"({store_count} stores, avg sales: ${avg_sales:,.0f})"
            )

    def _apply_feature_weights(self, features_scaled: np.ndarray, feature_names: pd.Index) -> np.ndarray:
        """
        Apply feature weights to scaled features.

        Multiplies each scaled feature by its weight to increase importance
        in K-means distance calculations. Sales feature (70% weight) dominates,
        while other features have secondary influence (30% combined).

        Args:
            features_scaled: StandardScaler normalized features (shape: n_stores × 7)
            feature_names: Column names (to match with weight dict)

        Returns:
            Weighted features (same shape, scaled by importance)

        Example:
            Without weighting: All features treated equally → extreme allocation imbalance
            With weighting: Sales prioritized → balanced allocation
        """
        features_weighted = features_scaled.copy()
        for i, feature_name in enumerate(feature_names):
            if feature_name in self.feature_weights:
                weight = self.feature_weights[feature_name]
                features_weighted[:, i] *= weight
                logger.debug(f"  {feature_name}: weight={weight:.2f}")

        return features_weighted

    def _find_optimal_k(self, features_scaled_weighted: np.ndarray) -> Dict:
        """
        Find optimal K using Elbow Method + Silhouette Analysis.

        Tests K=2,3,4,5 and recommends K that:
        1. Maximizes silhouette score (cluster separation quality)
        2. Produces balanced allocations (no cluster >70%)

        Returns:
            Dict with:
            - recommended_k: Optimal K value
            - scores: {K: silhouette_score}
            - allocations: {K: [cluster_percentages]}
            - rationale: Explanation of choice
        """
        logger.info("Adaptive K selection: Testing K=2,3,4,5...")

        results = {}
        for k in range(2, 6):
            km = KMeans(
                n_clusters=k,
                init='k-means++',
                random_state=self.random_state,
                n_init=10
            )
            labels = km.fit_predict(features_scaled_weighted)
            sil_score = silhouette_score(features_scaled_weighted, labels)

            # Calculate allocation percentages
            unique, counts = np.unique(labels, return_counts=True)
            allocations = (counts / len(labels) * 100).tolist()
            max_allocation = max(allocations)

            results[k] = {
                'silhouette': sil_score,
                'allocations': allocations,
                'max_allocation': max_allocation
            }

            logger.info(
                f"  K={k}: silhouette={sil_score:.4f}, max_allocation={max_allocation:.1f}%, "
                f"allocations={[f'{a:.1f}%' for a in allocations]}"
            )

        # Choose K: prioritize silhouette, but penalize extreme allocations (>70%)
        best_k = None
        best_score = -1

        for k, metrics in results.items():
            sil = metrics['silhouette']
            max_alloc = metrics['max_allocation']

            # If max allocation >70%, reduce score penalty
            allocation_penalty = 0
            if max_alloc > 70:
                allocation_penalty = 0.1 * (max_alloc - 70) / 30

            score = sil - allocation_penalty

            if score > best_score:
                best_score = score
                best_k = k

        return {
            'recommended_k': best_k,
            'scores': {k: v['silhouette'] for k, v in results.items()},
            'allocations': {k: v['allocations'] for k, v in results.items()},
            'rationale': (
                f"K={best_k} chosen: silhouette={results[best_k]['silhouette']:.4f}, "
                f"max_allocation={results[best_k]['max_allocation']:.1f}%"
            )
        }

    def predict_cluster(self, store_features: pd.DataFrame) -> np.ndarray:
        """
        Predict cluster assignments for stores.

        Args:
            store_features: DataFrame with same features as training

        Returns:
            Array of cluster IDs (0, 1, 2, ...)

        Raises:
            RuntimeError: If model not trained yet
            ValueError: If required columns missing

        Example:
            >>> clusterer = StoreClusterer()
            >>> clusterer.fit(train_stores)
            >>> cluster_ids = clusterer.predict_cluster(new_stores)  # [0, 1, 2, 0, ...]
        """
        if self.kmeans is None or self.scaler is None:
            raise RuntimeError("Must call fit() before predict_cluster()")

        # Validate input
        missing_cols = set(self.REQUIRED_FEATURES) - set(store_features.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Extract features
        features_df = store_features[self.REQUIRED_FEATURES].copy()

        # Apply same ordinal encoding as training
        if 'location_tier' in features_df.columns:
            features_df['location_tier'] = features_df['location_tier'].map(self.LOCATION_TIER_MAP)

        if 'fashion_tier' in features_df.columns:
            features_df['fashion_tier'] = features_df['fashion_tier'].map(self.FASHION_TIER_MAP)

        if 'store_format' in features_df.columns:
            features_df['store_format'] = features_df['store_format'].map(self.STORE_FORMAT_MAP)

        if 'region' in features_df.columns:
            features_df['region'] = features_df['region'].map(self.REGION_MAP)

        # Apply scaler transformation (same as training)
        features_scaled = self.scaler.transform(features_df)

        # Apply feature weights (same as training)
        features_scaled_weighted = self._apply_feature_weights(features_scaled, features_df.columns)

        # Predict clusters
        cluster_ids = self.kmeans.predict(features_scaled_weighted)

        return cluster_ids

    def get_cluster_labels(self) -> Dict[int, str]:
        """
        Get cluster labels mapping.

        Returns:
            Dict mapping cluster IDs to labels:
            {
                0: "Fashion_Forward",
                1: "Mainstream",
                2: "Value_Conscious"
            }

        Raises:
            RuntimeError: If model not trained yet
        """
        if self.cluster_labels_ is None:
            raise RuntimeError("Must call fit() before get_cluster_labels()")

        return self.cluster_labels_

    def get_cluster_stats(self) -> pd.DataFrame:
        """
        Get cluster statistics (means, sizes, percentages).

        Returns:
            DataFrame with cluster characteristics:
            - cluster_label: Cluster name
            - store_count: Number of stores in cluster
            - allocation_percentage: Percentage of total sales
            - avg_weekly_sales: Average weekly sales
            - avg_store_size: Average store size (sqft)
            - avg_median_income: Average median income

        Example output:
            ```
            cluster_label    store_count  allocation_pct  avg_weekly_sales  avg_store_size
            Fashion_Forward  18           45.2            850               52000
            Mainstream       20           35.1            650               38000
            Value_Conscious  12           19.7            350               20000
            ```

        Raises:
            RuntimeError: If model not trained yet
        """
        if self.training_data_ is None or self.kmeans is None:
            raise RuntimeError("Must call fit() before get_cluster_stats()")

        # Calculate cluster sizes
        cluster_sizes = self.training_data_.groupby('cluster_id').size()

        # Calculate cluster means (numeric columns only)
        numeric_features = ['avg_weekly_sales_12mo', 'store_size_sqft', 'median_income']
        cluster_means = self.training_data_.groupby('cluster_id')[numeric_features].mean()

        # Calculate cluster total sales (allocation basis)
        cluster_totals = self.training_data_.groupby('cluster_id')['avg_weekly_sales_12mo'].sum()

        # Calculate allocation percentages
        total_sales = cluster_totals.sum()
        cluster_percentages = (cluster_totals / total_sales * 100).round(1)

        # Validate percentages sum to 100%
        if abs(cluster_percentages.sum() - 100.0) > 0.1:
            logger.warning(
                f"Cluster percentages don't sum to 100%: {cluster_percentages.sum():.1f}%"
            )

        # Build stats DataFrame
        stats_df = pd.DataFrame({
            'cluster_label': [self.cluster_labels_[i] for i in cluster_means.index],
            'store_count': cluster_sizes,
            'allocation_percentage': cluster_percentages,
            'avg_weekly_sales': cluster_means['avg_weekly_sales_12mo'].round(0),
            'avg_store_size': cluster_means['store_size_sqft'].round(0),
            'avg_median_income': cluster_means['median_income'].round(0)
        })

        logger.info(f"Cluster stats:\n{stats_df.to_string()}")

        return stats_df

    def get_cluster_quality_metrics(self) -> Dict[str, float]:
        """
        Get clustering quality metrics.

        Returns:
            Dictionary with:
            - silhouette_score: Silhouette score (target: >0.3 for realistic data)
            - inertia: Sum of squared distances to cluster centers
            - n_clusters: Number of clusters

        Example:
            >>> metrics = clusterer.get_cluster_quality_metrics()
            >>> if metrics['silhouette_score'] > 0.3:
            ...     print("Good clustering quality")
        """
        if self.kmeans is None:
            raise RuntimeError("Must call fit() before get_cluster_quality_metrics()")

        return {
            'silhouette_score': self.silhouette_score_,
            'inertia': self.kmeans.inertia_,
            'n_clusters': self.n_clusters
        }
