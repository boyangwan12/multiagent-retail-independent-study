"""K-Means Store Clustering (Placeholder for Phase 3)"""

import pandas as pd
from typing import Dict, List, Any


def cluster_stores(
    store_data: pd.DataFrame,
    n_clusters: int = 3
) -> Dict[str, Any]:
    """Cluster stores based on attributes (PLACEHOLDER)."""
    if store_data is None or len(store_data) == 0:
        store_data = pd.DataFrame([
            {"store_id": f"store_{i}", "size_sqft": 5000 + i*500, "median_income": 50000 + i*5000}
            for i in range(50)
        ])

    # Mock clustering: fashion_forward, mainstream, value_conscious
    clusters = {
        "fashion_forward": [],
        "mainstream": [],
        "value_conscious": []
    }

    for i, store in store_data.iterrows():
        store_id = store.get("store_id", f"store_{i}")
        if i % 3 == 0:
            clusters["fashion_forward"].append(store_id)
        elif i % 3 == 1:
            clusters["mainstream"].append(store_id)
        else:
            clusters["value_conscious"].append(store_id)

    return {
        "clusters": clusters,
        "cluster_count": 3,
        "model_metadata": {
            "algorithm": "kmeans_placeholder",
            "n_clusters": 3,
            "note": "Mock clustering for Phase 3. Actual K-means in Phase 5."
        }
    }


def calculate_cluster_distribution(
    total_allocation: int,
    cluster_sizes: Dict[str, int]
) -> Dict[str, int]:
    """Calculate allocation per cluster (PLACEHOLDER)."""
    total_stores = sum(cluster_sizes.values())
    if total_stores == 0:
        return {"fashion_forward": 0, "mainstream": 0, "value_conscious": 0}

    distribution = {}
    for cluster_name, store_count in cluster_sizes.items():
        pct = store_count / total_stores
        distribution[cluster_name] = int(total_allocation * pct)

    return distribution