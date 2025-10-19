export type ReplenishmentStrategy = 'none' | 'weekly' | 'bi-weekly';

export interface SeasonParameters {
  forecast_horizon_weeks: number;
  season_start_date: string;
  season_end_date: string;
  replenishment_strategy: ReplenishmentStrategy;
  dc_holdback_percentage: number;
  markdown_checkpoint_week?: number;
  markdown_threshold?: number;
  extraction_confidence: 'high' | 'medium' | 'low';
  extraction_reasoning: string;
}
