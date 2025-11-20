"""
Inventory Agent Tools - Store Clustering and Inventory Allocation

This module contains:
1. StoreClusterer - K-means clustering for store segmentation
2. cluster_stores() - Tool for running store clustering analysis
3. allocate_inventory() - Tool for hierarchical inventory allocation
"""

from agents import function_tool, RunContextWrapper
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import logging

# Import ForecastResult from demand_tools
from agent_tools.demand_tools import ForecastResult

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS - Tool Outputs
# ============================================================================

class ClusterQualityMetrics(BaseModel):
    """Clustering quality metrics"""
    model_config = ConfigDict(extra='forbid')

    silhouette_score: float  # Target: > 0.4
    inertia: float
    n_clusters: int


class ClusterStats(BaseModel):
    """Statistics for a single cluster"""
    model_config = ConfigDict(extra='forbid')

    cluster_id: int
    cluster_label: str  # "Fashion_Forward", "Mainstream", "Value_Conscious"
    store_count: int
    allocation_percentage: float  # % of total sales
    avg_weekly_sales: float
    avg_store_size: float
    avg_median_income: float


class ClusteringResult(BaseModel):
    """Output from cluster_stores tool"""
    model_config = ConfigDict(extra='forbid')

    # NOTE: cluster_labels removed - info is in cluster_stats[].cluster_label
    # cluster_labels was Dict[int, str] which violates strict schema (no dynamic keys allowed)
    cluster_stats: List[ClusterStats]
    quality_metrics: ClusterQualityMetrics
    total_stores: int


class StoreAllocation(BaseModel):
    """Allocation for a single store"""
    model_config = ConfigDict(extra='forbid')

    store_id: str
    cluster: str
    initial_allocation: int
    allocation_factor: float


class ClusterAllocation(BaseModel):
    """Allocation for a cluster with all its stores"""
    model_config = ConfigDict(extra='forbid')

    cluster_id: int
    cluster_label: str
    allocation_percentage: float
    total_units: int
    stores: List[StoreAllocation]


class InventoryAllocationResult(BaseModel):
    """Output from allocate_inventory tool"""
    model_config = ConfigDict(extra='forbid')

    manufacturing_qty: int
    safety_stock_pct: float
    dc_holdback_total: int
    initial_allocation_total: int
    clusters: List[ClusterAllocation]
    replenishment_enabled: bool


# ============================================================================
# STORE CLUSTERER - K-means Clustering for Store Segmentation
# ============================================================================

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
        """Initialize StoreClusterer with K-means parameters."""
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

    def get_cluster_labels(self) -> Dict[int, str]:
        """Get cluster labels mapping."""
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
        """Get clustering quality metrics."""
        if self.kmeans is None:
            raise RuntimeError("Must call fit() before get_cluster_quality_metrics()")

        return {
            'silhouette_score': self.silhouette_score_,
            'inertia': self.kmeans.inertia_,
            'n_clusters': self.n_clusters
        }


# ============================================================================
# HELPER FUNCTIONS - Allocation Logic
# ============================================================================

def _validate_unit_conservation(expected: int, actual: int, step: str) -> None:
    """
    Validate unit conservation (no units lost or gained).

    Args:
        expected: Expected total units
        actual: Actual total units after allocation
        step: Step name for error message

    Raises:
        ValueError: If expected != actual
    """
    if expected != actual:
        raise ValueError(
            f"Unit conservation failed at {step}: "
            f"expected {expected}, got {actual} (diff: {actual - expected})"
        )
    logger.debug(f"Unit conservation OK at {step}: {expected} units")


def _calculate_allocation_factor(
    store: pd.Series,
    cluster_avg: Dict[str, float],
    location_tier_map: Dict[str, int]
) -> float:
    """
    Calculate store allocation factor (70% historical + 30% attributes).

    **Formula:**
    - historical_score = store_avg_sales / cluster_avg_sales
    - attribute_score = 0.5×size_score + 0.3×income_score + 0.2×tier_score
    - allocation_factor = 0.7×historical_score + 0.3×attribute_score

    Args:
        store: Store row with features
        cluster_avg: Cluster average features for normalization
        location_tier_map: Mapping for location tier encoding

    Returns:
        Normalized allocation factor (typically 0.5-1.5)
    """
    # Calculate historical performance score
    if cluster_avg['avg_weekly_sales_12mo'] > 0:
        historical_score = store['avg_weekly_sales_12mo'] / cluster_avg['avg_weekly_sales_12mo']
    else:
        historical_score = 1.0

    # Calculate attribute score
    if cluster_avg['store_size_sqft'] > 0:
        size_score = store['store_size_sqft'] / cluster_avg['store_size_sqft']
    else:
        size_score = 1.0

    if cluster_avg['median_income'] > 0:
        income_score = store['median_income'] / cluster_avg['median_income']
    else:
        income_score = 1.0

    # Normalize location tier (A=1.0, B=0.67, C=0.33)
    location_tier_numeric = location_tier_map.get(store['location_tier'], 1)
    tier_score = location_tier_numeric / 3.0

    # Weighted average of attribute scores
    attribute_score = (0.5 * size_score + 0.3 * income_score + 0.2 * tier_score)

    # Final allocation factor (70% historical + 30% attributes)
    allocation_factor = 0.7 * historical_score + 0.3 * attribute_score

    return allocation_factor


def _allocate_to_stores(
    cluster_id: int,
    cluster_label: str,
    cluster_units: int,
    stores_data: pd.DataFrame,
    cluster_stores: pd.DataFrame,
    forecast_by_week: List[int],
    location_tier_map: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Distribute cluster allocation to stores with 2-week minimum enforcement.

    Args:
        cluster_id: Cluster ID
        cluster_label: Cluster label (e.g., "Fashion_Forward")
        cluster_units: Units allocated to this cluster
        stores_data: All store attributes
        cluster_stores: Stores in this cluster
        forecast_by_week: Weekly forecasts for minimum calculation
        location_tier_map: Mapping for location tier encoding

    Returns:
        List of store allocations
    """
    # Calculate cluster averages for reference
    cluster_avg = cluster_stores[[
        'avg_weekly_sales_12mo', 'store_size_sqft', 'median_income'
    ]].mean().to_dict()

    # Calculate allocation factor for each store
    store_factors = {}
    for store_id, store_row in cluster_stores.iterrows():
        factor = _calculate_allocation_factor(store_row, cluster_avg, location_tier_map)
        store_factors[store_id] = factor

    # Normalize factors to sum to 1.0
    total_factor = sum(store_factors.values())
    if total_factor > 0:
        normalized_factors = {sid: f / total_factor for sid, f in store_factors.items()}
    else:
        # Equal allocation if all factors are zero
        normalized_factors = {sid: 1.0 / len(store_factors) for sid in store_factors.keys()}

    # Allocate to stores with proper remainder handling
    store_allocations = []
    min_allocation_units = forecast_by_week[0] * 2 if forecast_by_week else 0

    # Calculate base allocations
    base_allocations = []
    total_allocated = 0

    for store_id, factor in normalized_factors.items():
        base_allocation = int(cluster_units * factor)

        # Enforce 2-week minimum
        final_allocation = max(base_allocation, min_allocation_units)

        base_allocations.append({
            'store_id': store_id,
            'allocation': final_allocation,
            'factor': factor
        })
        total_allocated += final_allocation

    # Handle unit conservation
    diff = cluster_units - total_allocated

    if diff != 0:
        # If we allocated too many (due to minimums), reduce from largest allocations
        # If we allocated too few, add to largest allocations
        sorted_stores = sorted(base_allocations, key=lambda x: x['factor'], reverse=True)

        if diff < 0:
            # Allocated too many - reduce from stores above minimum
            units_to_remove = abs(diff)
            for store in sorted_stores:
                if units_to_remove == 0:
                    break
                # Only reduce if above minimum
                can_reduce = store['allocation'] - min_allocation_units
                if can_reduce > 0:
                    reduction = min(can_reduce, units_to_remove)
                    store['allocation'] -= reduction
                    units_to_remove -= reduction
                    logger.debug(f"Reduced store {store['store_id']} by {reduction} units")
        else:
            # Allocated too few - distribute remainder
            for i in range(diff):
                sorted_stores[i % len(sorted_stores)]['allocation'] += 1

        logger.debug(f"Adjusted store allocations by {diff} units for conservation")

    # Build final allocations
    for store_data in base_allocations:
        store_allocations.append({
            "store_id": str(store_data['store_id']),
            "cluster": cluster_label,
            "initial_allocation": store_data['allocation'],
            "allocation_factor": float(store_data['factor'])
        })

    return store_allocations


# ============================================================================
# TOOL 1: cluster_stores - K-means Store Clustering
# ============================================================================

@function_tool
def cluster_stores(
    ctx: RunContextWrapper,
    n_clusters: int = 3
) -> ClusteringResult:
    """
    Segment stores into performance tiers using K-means clustering.

    This tool automatically fetches store data from the system and runs K-means
    clustering to identify 3 performance tiers:
    - Fashion_Forward: High-performing stores (highest sales, premium locations)
    - Mainstream: Mid-tier stores (average performance)
    - Value_Conscious: Budget-oriented stores (lower sales, value positioning)

    The clustering uses 7 features:
    1. avg_weekly_sales_12mo (historical performance)
    2. store_size_sqft (store capacity)
    3. median_income (market affluence)
    4. location_tier (A/B/C - foot traffic quality)
    5. fashion_tier (Premium/Mainstream/Value positioning)
    6. store_format (Mall/Standalone/ShoppingCenter/Outlet)
    7. region (Northeast/Southeast/Midwest/West)

    Features are normalized using StandardScaler and clustered using K-means++.

    Args:
        ctx: Run context wrapper (provides access to data_loader)
        n_clusters: Number of clusters (default: 3)

    Returns:
        ClusteringResult with cluster labels, statistics, and quality metrics

    Example:
        >>> result = cluster_stores(ctx)
        >>> print(result.cluster_labels)
        {0: "Fashion_Forward", 1: "Mainstream", 2: "Value_Conscious"}
        >>> print(result.quality_metrics.silhouette_score)
        0.68  # Good clustering quality
    """
    logger.info("=" * 80)
    logger.info("TOOL: cluster_stores - K-means Store Clustering")
    logger.info("=" * 80)

    # Get store data from context
    try:
        data_loader = ctx.context.data_loader
        stores_df = data_loader.get_store_attributes_df()
    except AttributeError as e:
        logger.error("data_loader not found in context")
        raise RuntimeError(
            "Store data not available. Please ensure training data has been uploaded through the UI."
        ) from e

    logger.info(f"Fetched {len(stores_df)} stores from data_loader")
    logger.info(f"Available columns: {list(stores_df.columns)}")

    # Validate required columns before attempting clustering
    required_features = StoreClusterer.REQUIRED_FEATURES
    missing_cols = set(required_features) - set(stores_df.columns)

    if missing_cols:
        logger.error(f"Missing required store features: {missing_cols}")
        available_cols = list(stores_df.columns)
        raise ValueError(
            f"Store data is missing required columns for clustering.\n\n"
            f"Missing: {', '.join(missing_cols)}\n\n"
            f"Available: {', '.join(available_cols)}\n\n"
            f"Required features:\n" +
            "\n".join(f"  - {feat}" for feat in required_features) +
            "\n\nPlease ensure the store_attributes.csv file contains all required columns."
        )

    # Initialize and fit clusterer
    clusterer = StoreClusterer(n_clusters=n_clusters, random_state=42)
    clusterer.fit(stores_df)

    # Get cluster stats (includes cluster labels in each ClusterStats object)
    cluster_stats_df = clusterer.get_cluster_stats()

    # Get quality metrics
    quality_metrics = clusterer.get_cluster_quality_metrics()

    # Convert cluster stats DataFrame to list of ClusterStats objects
    cluster_stats_list = []
    for idx, row in cluster_stats_df.iterrows():
        cluster_stats_list.append(ClusterStats(
            cluster_id=int(idx),
            cluster_label=row['cluster_label'],
            store_count=int(row['store_count']),
            allocation_percentage=float(row['allocation_percentage']),
            avg_weekly_sales=float(row['avg_weekly_sales']),
            avg_store_size=float(row['avg_store_size']),
            avg_median_income=float(row['avg_median_income'])
        ))

    # Build result (cluster_labels removed - info is in cluster_stats)
    result = ClusteringResult(
        cluster_stats=cluster_stats_list,
        quality_metrics=ClusterQualityMetrics(**quality_metrics),
        total_stores=len(stores_df)
    )

    logger.info(f"Clustering complete: {result.total_stores} stores in {n_clusters} clusters")
    logger.info(f"Silhouette score: {result.quality_metrics.silhouette_score:.4f}")

    return result


# ============================================================================
# TOOL 2: allocate_inventory - Hierarchical Inventory Allocation
# ============================================================================

@function_tool
def allocate_inventory(
    ctx: RunContextWrapper,
    forecast_result: ForecastResult,
    clustering_result: ClusteringResult,
    dc_holdback_percentage: float = 0.45,
    replenishment_strategy: str = "weekly"
) -> InventoryAllocationResult:
    """
    Perform hierarchical inventory allocation to clusters and stores.

    This tool executes a 3-layer allocation hierarchy:

    Layer 1 - Manufacturing Split:
      - Calculate manufacturing qty = total_demand × (1 + safety_stock_pct)
      - Split into: DC holdback (e.g., 45%) vs initial store allocation (55%)

    Layer 2 - Cluster Allocation:
      - Allocate initial allocation to clusters using K-means percentages
      - Example: Fashion_Forward gets 45%, Mainstream 35%, Value_Conscious 20%

    Layer 3 - Store Allocation:
      - Allocate cluster units to stores using hybrid factors:
        * 70% based on historical sales performance
        * 30% based on store attributes (size, income, tier)
      - Enforce 2-week minimum inventory per store

    Unit conservation is validated at each step to ensure no units lost/gained.

    Args:
        ctx: Run context wrapper (provides access to data_loader)
        forecast_result: ForecastResult from demand agent with total_demand,
            safety_stock_pct, forecast_by_week, etc.
        clustering_result: ClusteringResult from cluster_stores tool with
            cluster_labels, cluster_stats, and quality_metrics
        dc_holdback_percentage: % of manufacturing held at DC (default: 0.45 = 45%)
        replenishment_strategy: "none", "weekly", or "bi-weekly" (default: "weekly")

    Returns:
        InventoryAllocationResult with complete allocation plan

    Example:
        >>> result = allocate_inventory(ctx, forecast_result, clustering_result)
        >>> print(result.manufacturing_qty)
        9600  # 8000 demand + 20% safety stock
        >>> print(result.dc_holdback_total)
        4320  # 45% held at DC
        >>> print(result.clusters[0].cluster_label)
        "Fashion_Forward"
    """
    logger.info("=" * 80)
    logger.info("TOOL: allocate_inventory - Hierarchical Allocation")
    logger.info("=" * 80)

    # Extract forecast inputs
    total_demand = forecast_result.total_demand
    safety_stock_pct = forecast_result.safety_stock_pct
    forecast_by_week = forecast_result.forecast_by_week

    logger.info(f"Forecast inputs: demand={total_demand}, safety_stock={safety_stock_pct:.2f}")

    # Step 1: Calculate manufacturing quantity
    logger.info("Step 1: Calculating manufacturing quantity...")
    manufacturing_qty = int(total_demand * (1 + safety_stock_pct))
    logger.info(f"Manufacturing: {total_demand} × (1 + {safety_stock_pct:.2f}) = {manufacturing_qty} units")

    # Step 2: Split into DC holdback and initial allocation
    logger.info("Step 2: Splitting manufacturing into DC holdback and initial allocation...")
    initial_allocation_pct = 1.0 - dc_holdback_percentage
    initial_allocation_total = int(manufacturing_qty * initial_allocation_pct)
    dc_holdback_total = manufacturing_qty - initial_allocation_total

    # Validate unit conservation at manufacturing split
    _validate_unit_conservation(
        expected=manufacturing_qty,
        actual=initial_allocation_total + dc_holdback_total,
        step="manufacturing_split"
    )

    logger.info(
        f"DC Holdback: {dc_holdback_percentage*100:.0f}% = {dc_holdback_total} units, "
        f"Initial Allocation: {initial_allocation_pct*100:.0f}% = {initial_allocation_total} units"
    )

    # Get store data from context
    data_loader = ctx.context.data_loader
    stores_df = data_loader.get_store_attributes_df()

    # Re-run clustering to get cluster assignments (we need cluster_id column)
    clusterer = StoreClusterer(n_clusters=3, random_state=42)
    clusterer.fit(stores_df)
    stores_with_clusters = clusterer.training_data_  # Has cluster_id column

    # Extract clustering info (cluster labels are in cluster_stats)
    cluster_stats_list = clustering_result.cluster_stats

    # Step 3: Allocate to clusters with remainder distribution
    logger.info("Step 3: Allocating inventory to clusters...")
    cluster_allocations = []

    # Calculate base allocations with rounding
    cluster_base_allocations = []
    total_allocated = 0

    for cluster_stat in cluster_stats_list:
        cluster_id = cluster_stat.cluster_id
        cluster_label = cluster_stat.cluster_label
        allocation_pct = cluster_stat.allocation_percentage / 100.0

        cluster_units = int(initial_allocation_total * allocation_pct)
        cluster_base_allocations.append({
            'cluster_id': cluster_id,
            'cluster_label': cluster_label,
            'units': cluster_units,
            'pct': allocation_pct
        })
        total_allocated += cluster_units

    # Distribute remainder units to largest clusters
    remainder = initial_allocation_total - total_allocated
    if remainder > 0:
        # Sort by percentage (largest first) and distribute remainder
        sorted_clusters = sorted(cluster_base_allocations, key=lambda x: x['pct'], reverse=True)
        for i in range(remainder):
            sorted_clusters[i % len(sorted_clusters)]['units'] += 1
        logger.info(f"Distributed {remainder} remainder units to ensure conservation")

    # Now allocate to stores using the adjusted cluster units
    for i, cluster_stat in enumerate(cluster_stats_list):
        cluster_id = cluster_stat.cluster_id
        cluster_label = cluster_stat.cluster_label

        # Get adjusted cluster units
        cluster_units = next(c['units'] for c in cluster_base_allocations if c['cluster_id'] == cluster_id)

        logger.info(
            f"Cluster {cluster_id} ({cluster_label}): "
            f"{cluster_stat.allocation_percentage:.1f}% = {cluster_units} units"
        )

        # Get stores in this cluster
        cluster_stores = stores_with_clusters[
            stores_with_clusters['cluster_id'] == cluster_id
        ].copy()

        # Calculate store allocations within cluster
        store_allocations = _allocate_to_stores(
            cluster_id=cluster_id,
            cluster_label=cluster_label,
            cluster_units=cluster_units,
            stores_data=stores_df,
            cluster_stores=cluster_stores,
            forecast_by_week=forecast_by_week,
            location_tier_map=StoreClusterer.LOCATION_TIER_MAP
        )

        cluster_allocations.append(ClusterAllocation(
            cluster_id=cluster_id,
            cluster_label=cluster_label,
            allocation_percentage=cluster_stat.allocation_percentage,
            total_units=cluster_units,
            stores=[StoreAllocation(**s) for s in store_allocations]
        ))

    # Validate cluster allocations sum to initial_allocation_total
    actual_cluster_sum = sum(c.total_units for c in cluster_allocations)
    _validate_unit_conservation(
        expected=initial_allocation_total,
        actual=actual_cluster_sum,
        step="cluster_allocation"
    )

    # Validate store allocations sum correctly
    total_store_allocation = sum(
        sum(s.initial_allocation for s in c.stores)
        for c in cluster_allocations
    )
    _validate_unit_conservation(
        expected=initial_allocation_total,
        actual=total_store_allocation,
        step="store_allocation"
    )

    # Determine replenishment status
    replenishment_enabled = replenishment_strategy != "none"

    # Build result
    result = InventoryAllocationResult(
        manufacturing_qty=manufacturing_qty,
        safety_stock_pct=safety_stock_pct,
        dc_holdback_total=dc_holdback_total,
        initial_allocation_total=initial_allocation_total,
        clusters=cluster_allocations,
        replenishment_enabled=replenishment_enabled
    )

    logger.info(
        f"Allocation complete: {initial_allocation_total} to stores, "
        f"{dc_holdback_total} to DC"
    )
    logger.info(f"Replenishment: {'Enabled' if replenishment_enabled else 'Disabled'}")

    return result
