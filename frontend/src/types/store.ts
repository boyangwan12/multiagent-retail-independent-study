// Store attributes from CSV data
export interface Store {
  store_id: string;
  size_sqft: number;
  income_level: number;
  foot_traffic: number;
  competitor_density: number;
  online_penetration: number;
  population_density: number;
  mall_location: boolean;
}

// Store cluster grouping
export interface StoreCluster {
  cluster_id: string;
  cluster_name: string;
  fashion_tier: 'PREMIUM' | 'MAINSTREAM' | 'VALUE';
  store_count: number;
  total_units: number;
  allocation_percentage: number;
}

// Store forecast details for cluster table
export interface StoreForecast {
  store_id: string;
  store_name: string;
  forecast_units: number;
  confidence: number; // 0-100
  status: 'Active' | 'Warning' | 'Low Stock';
  location: string;
  size_tier: 'Large' | 'Medium' | 'Small';
  // Original store attributes for expandable details
  size_sqft: number;
  income_level: number;
  foot_traffic: number;
  mall_location: boolean;
}

// Extended cluster with store-level details
export interface ClusterWithStores extends StoreCluster {
  stores: StoreForecast[];
}

// Historical sales data
export interface HistoricalSale {
  date: string;
  store_id: string;
  category: string;
  quantity_sold: number;
  revenue: number;
}
