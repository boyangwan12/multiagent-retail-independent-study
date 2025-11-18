// Variance types for weekly performance tracking

export interface StoreVariance {
  store_id: string;
  store_name: string;
  forecasted: number;
  actual: number;
  variance_pct: number;
}

export interface WeeklyVariance {
  forecast_id: string;
  week_number: number;
  forecasted_cumulative: number;
  actual_cumulative: number;
  variance_pct: number;
  threshold_exceeded: boolean;
  action_taken: string | null;
  store_level_variance: StoreVariance[];
}
