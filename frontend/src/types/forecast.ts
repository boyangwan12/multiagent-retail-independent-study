import type { StoreCluster } from './store';

export interface WeeklyDemand {
  week_number: number;
  demand_units: number;
  forecasted_units?: number;
  actual_units?: number | null;
  variance_pct?: number | null;
}

export interface ForecastResult {
  forecast_id: string;
  category_id: string;
  season: string;
  total_season_demand: number;
  weekly_demand_curve: WeeklyDemand[];
  peak_week: number;
  forecasting_method: 'ensemble_prophet_arima';
  prophet_forecast: number;
  arima_forecast: number;
  cluster_distribution: StoreCluster[];
}
