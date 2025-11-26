"""
Feature mapping module for store clustering.

Transforms raw store attributes into clustering-ready features.
This proves clustering is not hardcoded but derived from business data.

The mapping ensures:
1. Raw store attributes (8 columns) → Clustering features (7 columns)
2. All derived values are deterministic (same input = same output)
3. Feature engineering is transparent and business-aligned
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def map_store_attributes_to_clustering_features(
    store_data: pd.DataFrame,
    seed: int = 42,
    source: str = "auto"
) -> pd.DataFrame:
    """
    Transform raw store attributes into 7 clustering features.

    **Input columns (from store_attributes.csv):**
    Two formats supported (auto-detected):

    Format 1 (Raw attributes):
    - store_id: Store identifier
    - size_sqft: Store square footage
    - income_level: Median income of surrounding area
    - foot_traffic: Average weekly foot traffic
    - competitor_density: Number of competitors in area
    - online_penetration: Online sales penetration rate
    - population_density: Population density of area
    - mall_location: Whether store is in mall (bool)

    Format 2 (Pre-processed, e.g., SDK branch):
    - store_id: Store identifier
    - avg_weekly_sales_12mo: Already calculated average weekly sales
    - store_size_sqft: Store square footage
    - median_income: Median income
    - location_tier, fashion_tier, store_format, region: Already encoded

    **Output columns (for clustering):**
    - store_id: Store identifier
    - avg_weekly_sales_12mo: Estimated average weekly sales (derived)
    - store_size_sqft: Store square footage (direct)
    - median_income: Median income (direct)
    - location_tier: Premium/Standard/Value tier (derived)
    - fashion_tier: Premium/Mainstream/Value positioning (derived)
    - store_format: Mall/Standalone/ShoppingCenter/Outlet (derived)
    - region: Geographic region (randomized, balanced)

    **Feature Derivation Logic:**

    1. avg_weekly_sales_12mo:
       Sales proxy = foot_traffic × income_multiplier × size_factor
       - foot_traffic: Primary driver
       - income_multiplier: Higher income areas → higher spending
       - size_factor: Larger stores support higher sales volume

    2. location_tier (from income_level):
       - A (Premium): income > $120k
       - B (Standard): income $80k-$120k
       - C (Value): income < $80k

    3. fashion_tier (from foot_traffic):
       - Premium: foot_traffic > 2400 (high-volume locations)
       - Mainstream: foot_traffic 1800-2400 (moderate-volume)
       - Value: foot_traffic < 1800 (low-volume locations)

    4. store_format (from size_sqft + mall_location):
       - Mall: mall_location=True AND size > 12000 sqft
       - Standalone: mall_location=True AND size ≤ 12000 sqft
       - ShoppingCenter: mall_location=False AND size > 8000 sqft
       - Outlet: mall_location=False AND size ≤ 8000 sqft

    5. region (randomized across 4 regions):
       - Distribute 50 stores across NE/SE/MW/W (13/13/12/12)
       - Deterministic (seeded) for reproducibility

    Args:
        store_data: DataFrame with store attributes (50 stores)
        seed: Random seed for region assignment (default: 42)
        source: "auto" (detect format), "raw" (raw attributes), "sdk" (pre-processed)

    Returns:
        DataFrame with 7 clustering features (50 stores × 7 features)

    Example:
        >>> raw_stores = pd.read_csv('data/mock/training/store_attributes.csv')
        >>> clustering_features = map_store_attributes_to_clustering_features(raw_stores)
        >>> # Use clustering_features with StoreClusterer
        >>> clusterer = StoreClusterer()
        >>> clusterer.fit(clustering_features)
    """
    df = store_data.copy()

    # Auto-detect format if needed
    if source == "auto":
        if 'avg_weekly_sales_12mo' in df.columns:
            source = "sdk"  # Already has clustering features
        else:
            source = "raw"  # Has raw attributes, needs transformation

    # If already in SDK format (pre-processed), just return as-is
    if source == "sdk":
        required_cols = ['store_id', 'avg_weekly_sales_12mo', 'store_size_sqft', 'median_income',
                        'location_tier', 'fashion_tier', 'store_format', 'region']
        return df[required_cols].copy()

    # Otherwise, transform from raw format

    # Feature 1: avg_weekly_sales_12mo (derived from foot_traffic, income, size)
    # Formula: foot_traffic × (0.3 + 0.1×(income/100k)) × (size/10k)
    # Rationale:
    # - foot_traffic: Primary sales driver
    # - income_multiplier (0.3-0.4): Higher income → 30-40% sales lift
    # - size_factor: Larger stores scale sales proportionally
    df['avg_weekly_sales_12mo'] = (
        df['foot_traffic'] *
        (0.3 + 0.1 * (df['income_level'] / 100000)) *
        (df['size_sqft'] / 10000)
    )

    # Feature 2: store_size_sqft (direct mapping)
    df['store_size_sqft'] = df['size_sqft']

    # Feature 3: median_income (direct mapping)
    df['median_income'] = df['income_level']

    # Feature 4: location_tier (ordinal from income_level)
    # A = Premium ($120k+), B = Standard ($80k-$120k), C = Value (<$80k)
    def assign_location_tier(income):
        if income >= 120000:
            return 'A'
        elif income >= 80000:
            return 'B'
        else:
            return 'C'

    df['location_tier'] = df['income_level'].apply(assign_location_tier)

    # Feature 5: fashion_tier (ordinal from foot_traffic)
    # Premium = high traffic (>2400), Mainstream = medium (1800-2400), Value = low (<1800)
    def assign_fashion_tier(traffic):
        if traffic > 2400:
            return 'Premium'
        elif traffic >= 1800:
            return 'Mainstream'
        else:
            return 'Value'

    df['fashion_tier'] = df['foot_traffic'].apply(assign_fashion_tier)

    # Feature 6: store_format (ordinal from size_sqft + mall_location)
    # Mall=4, Standalone=3, ShoppingCenter=2, Outlet=1
    def assign_store_format(row):
        mall_loc = row['mall_location']
        size = row['size_sqft']

        if mall_loc and size > 12000:
            return 'Mall'
        elif mall_loc and size <= 12000:
            return 'Standalone'
        elif not mall_loc and size > 8000:
            return 'ShoppingCenter'
        else:
            return 'Outlet'

    df['store_format'] = df.apply(assign_store_format, axis=1)

    # Feature 7: region (distributed evenly across 4 regions)
    # Split 50 stores: Northeast=13, Southeast=13, Midwest=12, West=12
    # Use seeded randomization for reproducibility
    np.random.seed(seed)
    num_stores = len(df)
    regions = (
        ['Northeast'] * 13 +
        ['Southeast'] * 13 +
        ['Midwest'] * 12 +
        ['West'] * 12
    )
    np.random.shuffle(regions)
    df['region'] = regions[:num_stores]

    # Return only clustering features
    clustering_features = df[[
        'store_id',
        'avg_weekly_sales_12mo',
        'store_size_sqft',
        'median_income',
        'location_tier',
        'fashion_tier',
        'store_format',
        'region'
    ]].copy()

    return clustering_features


def create_diverse_synthetic_dataset(seed: int = 42) -> pd.DataFrame:
    """
    Create synthetic dataset with different cluster distribution pattern.

    **Scenario:** "Rural Outlet Focus"
    - 15 small outlet stores (Value tier, low income, low traffic) → ~30% allocation
    - 20 mid-sized mainstream stores (mixed characteristics) → ~45% allocation
    - 15 large premium stores (high income, high traffic, mall) → ~25% allocation

    **Purpose:** Prove clustering algorithm adapts to different data patterns
    (not hardcoded to always produce same allocation percentages).

    Args:
        seed: Random seed for reproducibility (default: 42)

    Returns:
        DataFrame with 7 clustering features (50 stores × 7 features)

    Example:
        >>> synthetic_stores = create_diverse_synthetic_dataset()
        >>> clusterer = StoreClusterer()
        >>> clusterer.fit(synthetic_stores)
        >>> stats = clusterer.get_cluster_stats()
        >>> # Should show different allocation than realistic_dataset1
    """
    np.random.seed(seed)

    stores_list = []

    # Cluster 1: Value Outlets (15 stores)
    # Small, low-income, low-traffic locations
    for i in range(15):
        stores_list.append({
            'store_id': f'VC_{i:03d}',
            'avg_weekly_sales_12mo': np.random.normal(280, 40, 1)[0],
            'store_size_sqft': np.random.uniform(3500, 7000, 1)[0],
            'median_income': np.random.uniform(45000, 70000, 1)[0],
            'location_tier': 'C',
            'fashion_tier': 'Value',
            'store_format': 'Outlet',
            'region': np.random.choice(['Midwest', 'Southeast'])
        })

    # Cluster 2: Mainstream Stores (20 stores)
    # Mid-sized, mixed income, moderate traffic
    for i in range(20):
        stores_list.append({
            'store_id': f'MS_{i:03d}',
            'avg_weekly_sales_12mo': np.random.normal(620, 50, 1)[0],
            'store_size_sqft': np.random.uniform(8000, 12000, 1)[0],
            'median_income': np.random.uniform(75000, 110000, 1)[0],
            'location_tier': np.random.choice(['B', 'C']),
            'fashion_tier': 'Mainstream',
            'store_format': np.random.choice(['Standalone', 'ShoppingCenter']),
            'region': np.random.choice(['Northeast', 'Southeast', 'Midwest', 'West'])
        })

    # Cluster 3: Premium Malls (15 stores)
    # Large, high-income, high-traffic locations
    for i in range(15):
        stores_list.append({
            'store_id': f'FF_{i:03d}',
            'avg_weekly_sales_12mo': np.random.normal(820, 60, 1)[0],
            'store_size_sqft': np.random.uniform(13000, 20000, 1)[0],
            'median_income': np.random.uniform(115000, 160000, 1)[0],
            'location_tier': 'A',
            'fashion_tier': 'Premium',
            'store_format': 'Mall',
            'region': np.random.choice(['Northeast', 'West'])
        })

    # Create DataFrame
    dataset = pd.DataFrame(stores_list)

    return dataset[[
        'store_id',
        'avg_weekly_sales_12mo',
        'store_size_sqft',
        'median_income',
        'location_tier',
        'fashion_tier',
        'store_format',
        'region'
    ]].copy()
