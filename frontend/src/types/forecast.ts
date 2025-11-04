// Forecast types for backend integration

export interface ForecastData {
  forecast_id: string;
  workflow_id?: string;
  category_name: string;
  season_parameters?: {
    forecast_horizon_weeks: number;
    season_start_date: string;
    season_end_date: string;
    replenishment_strategy: string;
    dc_holdback_percentage: number;
    markdown_checkpoint_week?: number;
    markdown_threshold?: number;
  };
  total_season_demand: number;
  prophet_forecast?: number;
  arima_forecast?: number;
  forecasting_method: string;
  safety_stock_pct?: number;
  adaptation_reasoning?: string;
  weekly_demand_curve: number[];
  peak_week?: number;
  cluster_distribution?: {
    Fashion_Forward?: number;
    Mainstream?: number;
    Value_Conscious?: number;
  };
  created_at?: string;
  mape_percentage?: number;
}

export interface ForecastSummary {
  forecast_id: string;
  workflow_id?: string;
  category_name: string;
  total_season_demand: number;
  forecasting_method: string;
  mape_percentage: number;
  created_at?: string;
}

export interface StoreCluster {
  cluster_id: string;
  cluster_name: string;
  store_count: number;
  allocation_percentage: number;
  allocation_units: number;
  stores: Store[];
}

export interface Store {
  store_id: string;
  store_name: string;
  size_sqft: number;
  income_level: number;
  foot_traffic: number;
  allocated_units: number;
}
