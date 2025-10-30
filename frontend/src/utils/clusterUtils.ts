import type { Store, StoreCluster, StoreForecast, ClusterWithStores } from '@/types';

// City names for generating store locations
const CITIES = [
  'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
  'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Austin',
  'San Jose', 'Fort Worth', 'Jacksonville', 'Columbus', 'Charlotte',
  'Indianapolis', 'Seattle', 'Denver', 'Boston', 'Nashville',
  'Portland', 'Las Vegas', 'Detroit', 'Memphis', 'Louisville',
  'Baltimore', 'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno',
  'Sacramento', 'Kansas City', 'Atlanta', 'Miami', 'Cleveland',
  'Oakland', 'Omaha', 'Raleigh', 'Minneapolis', 'Virginia Beach',
  'Tampa', 'Colorado Springs', 'St. Louis', 'Pittsburgh', 'Cincinnati',
  'Anchorage', 'Riverside', 'Stockton', 'Corpus Christi', 'Newark'
];

// Store name templates
const STORE_NAME_PREFIXES = [
  'Fashion Valley', 'Style Plaza', 'Trend Center', 'Chic Boutique',
  'Urban Outlet', 'Metro Fashion', 'Downtown', 'Uptown', 'Riverside',
  'Lakeside', 'Parkside', 'Central', 'Grand', 'Premier', 'Elite'
];

const STORE_NAME_SUFFIXES = [
  'Mall', 'Plaza', 'Center', 'Boutique', 'Outlet', 'Gallery', 'Emporium'
];

/**
 * Assigns a store to a cluster based on its attributes
 */
export function assignStoreToCluster(store: Store): 'premium' | 'mainstream' | 'value' {
  // Calculate composite score (0-1 range)
  const sizeScore = Math.min(store.size_sqft / 15000, 1);
  const incomeScore = Math.min(store.income_level / 150000, 1);
  const trafficScore = Math.min(store.foot_traffic / 3000, 1);
  const onlineScore = 1 - store.online_penetration; // Lower online penetration = better for physical stores
  const densityScore = Math.min(store.population_density / 15000, 1);

  const compositeScore =
    sizeScore * 0.3 +
    incomeScore * 0.3 +
    trafficScore * 0.2 +
    onlineScore * 0.1 +
    densityScore * 0.1;

  // Assign based on score thresholds
  if (compositeScore > 0.65) return 'premium';
  if (compositeScore > 0.45) return 'mainstream';
  return 'value';
}

/**
 * Generates a friendly store name
 */
function generateStoreName(storeIndex: number): string {
  const prefix = STORE_NAME_PREFIXES[storeIndex % STORE_NAME_PREFIXES.length];
  const suffix = STORE_NAME_SUFFIXES[storeIndex % STORE_NAME_SUFFIXES.length];
  return `${prefix} ${suffix}`;
}

/**
 * Generates a location based on store attributes
 */
function generateLocation(storeIndex: number): string {
  return CITIES[storeIndex % CITIES.length];
}

/**
 * Determines size tier based on square footage
 */
function determineSizeTier(sizeSqft: number): 'Large' | 'Medium' | 'Small' {
  if (sizeSqft > 12000) return 'Large';
  if (sizeSqft > 7000) return 'Medium';
  return 'Small';
}

/**
 * Calculates confidence score (70-95%) based on store quality metrics
 */
function calculateConfidence(store: Store): number {
  // Higher scores = better data quality = higher confidence
  const sizeConfidence = store.size_sqft > 5000 ? 10 : 5;
  const trafficConfidence = store.foot_traffic > 1000 ? 10 : 5;
  const locationConfidence = store.mall_location ? 5 : 3;
  const competitorConfidence = store.competitor_density < 5 ? 5 : 3;

  const baseConfidence = 70;
  const bonus = sizeConfidence + trafficConfidence + locationConfidence + competitorConfidence;

  return Math.min(baseConfidence + bonus, 95);
}

/**
 * Determines store status based on inventory and performance
 */
function determineStatus(store: Store, confidence: number): 'Active' | 'Warning' | 'Low Stock' {
  // High online penetration + low traffic = potential low stock warning
  if (store.online_penetration > 0.5 && store.foot_traffic < 1000) {
    return 'Low Stock';
  }

  // Low confidence = warning
  if (confidence < 75) {
    return 'Warning';
  }

  return 'Active';
}

/**
 * Converts raw stores to ClusterWithStores objects
 */
export function transformStoresToClusters(
  stores: Store[],
  clusters: StoreCluster[]
): ClusterWithStores[] {
  // Group stores by cluster
  const storesByCluster = new Map<string, Store[]>();

  stores.forEach((store) => {
    const clusterId = assignStoreToCluster(store);
    if (!storesByCluster.has(clusterId)) {
      storesByCluster.set(clusterId, []);
    }
    storesByCluster.get(clusterId)!.push(store);
  });

  // Transform each cluster
  return clusters.map((cluster) => {
    const clusterStores = storesByCluster.get(cluster.cluster_id) || [];

    // Calculate per-store forecast allocation
    const avgUnitsPerStore = clusterStores.length > 0
      ? cluster.total_units / clusterStores.length
      : 0;

    const transformedStores: StoreForecast[] = clusterStores.map((store) => {
      const confidence = calculateConfidence(store);
      const status = determineStatus(store, confidence);

      // Add variance to forecast units (±15%)
      const variance = 0.85 + Math.random() * 0.3; // 0.85 to 1.15
      const forecastUnits = Math.round(avgUnitsPerStore * variance);

      const storeIndex = stores.indexOf(store);

      return {
        store_id: store.store_id,
        store_name: generateStoreName(storeIndex),
        forecast_units: forecastUnits,
        confidence,
        status,
        location: generateLocation(storeIndex),
        size_tier: determineSizeTier(store.size_sqft),
        // Include original attributes for expandable details
        size_sqft: store.size_sqft,
        income_level: store.income_level,
        foot_traffic: store.foot_traffic,
        mall_location: store.mall_location,
      };
    });

    // Sort stores by forecast_units descending
    transformedStores.sort((a, b) => b.forecast_units - a.forecast_units);

    return {
      ...cluster,
      stores: transformedStores,
    };
  });
}
