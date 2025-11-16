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
    K-means clustering for store segmentation.

    Segments stores into 3 performance tiers (Fashion_Forward, Mainstream,
    Value_Conscious) using 7 features with StandardScaler normalization.

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
        kmeans: Trained KMeans model instance
        scaler: StandardScaler instance for normalization
        cluster_labels_: Dict mapping cluster IDs to labels
        silhouette_score_: Silhouette score for cluster quality
        training_data_: Original training data with cluster assignments
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

    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        """
        Initialize StoreClusterer with K-means parameters.

        Args:
            n_clusters: Number of clusters (default: 3)
            random_state: Random seed for reproducibility (default: 42)
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans: Optional[KMeans] = None
        self.scaler: Optional[StandardScaler] = None
        self.cluster_labels_: Optional[Dict[int, str]] = None
        self.silhouette_score_: Optional[float] = None
        self.training_data_: Optional[pd.DataFrame] = None
        logger.info(f"StoreClusterer initialized (K={n_clusters}, random_state={random_state})")

    def fit(self, store_features: pd.DataFrame) -> None:
        """
        Fit K-means clustering on store features.

        **Process:**
        1. Validate input DataFrame has required columns
        2. Extract and encode features (ordinal encoding for categoricals)
        3. Apply StandardScaler normalization (mean=0, std=1)
        4. Train K-means++ with K=3
        5. Calculate silhouette score
        6. Assign cluster labels (by avg_weekly_sales)

        Args:
            store_features: DataFrame with 7 required columns (rows = stores)

        Raises:
            ValueError: If required columns missing or insufficient data

        Example:
            >>> clusterer = StoreClusterer()
            >>> clusterer.fit(stores_df)  # 50 stores × 7 features
            >>> labels = clusterer.get_cluster_labels()
            >>> stats = clusterer.get_cluster_stats()
        """
        logger.info(f"Fitting K-means clustering on {len(store_features)} stores...")

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

        # Train K-means with K-means++ initialization
        logger.info(f"Training K-means++ (K={self.n_clusters}, n_init=10)...")
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            init='k-means++',
            random_state=self.random_state,
            n_init=10,  # Run 10 times, pick best
            verbose=0
        )
        self.kmeans.fit(features_scaled)

        # Calculate silhouette score
        cluster_labels = self.kmeans.labels_
        self.silhouette_score_ = silhouette_score(features_scaled, cluster_labels)
        logger.info(f"Silhouette score: {self.silhouette_score_:.4f}")

        if self.silhouette_score_ < 0.4:
            logger.warning(
                f"Silhouette score {self.silhouette_score_:.4f} below 0.4 - "
                "clusters may overlap, consider manual review"
            )

        # Store training data with cluster assignments
        self.training_data_ = store_features.copy()
        self.training_data_['cluster_id'] = cluster_labels

        # Assign cluster labels based on average sales
        self._assign_cluster_labels()

        logger.info("K-means clustering complete")

    def _assign_cluster_labels(self) -> None:
        """
        Automatically assign meaningful labels to clusters.

        **Labels assigned by avg_weekly_sales (descending):**
        - Highest sales → Fashion_Forward
        - Medium sales → Mainstream
        - Lowest sales → Value_Conscious

        **Internal method - called by fit().**
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

        # Assign labels
        self.cluster_labels_ = {
            sorted_clusters.index[0]: "Fashion_Forward",   # Highest sales
            sorted_clusters.index[1]: "Mainstream",        # Medium sales
            sorted_clusters.index[2]: "Value_Conscious"    # Lowest sales
        }

        # Log assignments
        for cluster_id, label in self.cluster_labels_.items():
            avg_sales = cluster_means.loc[cluster_id, 'avg_weekly_sales_12mo']
            store_count = len(self.training_data_[self.training_data_['cluster_id'] == cluster_id])
            logger.info(
                f"Cluster {cluster_id} → {label} "
                f"({store_count} stores, avg sales: ${avg_sales:,.0f})"
            )

    def predict_cluster(self, store_features: pd.DataFrame) -> np.ndarray:
        """
        Predict cluster assignments for stores.

        Args:
            store_features: DataFrame with same features as training

        Returns:
            Array of cluster IDs (0, 1, 2)

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

        # Predict clusters
        cluster_ids = self.kmeans.predict(features_scaled)

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
            - silhouette_score: Silhouette score (target: >0.4)
            - inertia: Sum of squared distances to cluster centers
            - n_clusters: Number of clusters

        Example:
            >>> metrics = clusterer.get_cluster_quality_metrics()
            >>> if metrics['silhouette_score'] > 0.4:
            ...     print("Good clustering quality")
        """
        if self.kmeans is None:
            raise RuntimeError("Must call fit() before get_cluster_quality_metrics()")

        return {
            'silhouette_score': self.silhouette_score_,
            'inertia': self.kmeans.inertia_,
            'n_clusters': self.n_clusters
        }
