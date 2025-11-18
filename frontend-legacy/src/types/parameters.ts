/**
 * Parameter Extraction Type Definitions
 *
 * Types for parameter extraction requests and responses
 */

import type { SeasonParameters, ReplenishmentStrategy } from './index';

/**
 * Request body for parameter extraction
 * Matches backend API schema
 */
export interface ParameterExtractionRequest {
  user_input: string;
}

/**
 * Backend parameter type (without frontend-specific fields)
 */
type BackendSeasonParameters = Omit<
  SeasonParameters,
  'extraction_confidence' | 'extraction_reasoning'
>;

/**
 * Response from parameter extraction endpoint
 * Matches backend API schema
 */
export interface ParameterExtractionResponse {
  parameters: BackendSeasonParameters;
  confidence: 'high' | 'medium' | 'low';
  reasoning: string;
  raw_llm_output?: string;
}

/**
 * Validation result for extracted parameters
 */
export interface ParameterValidationResult {
  isValid: boolean;
  errors: ParameterValidationError[];
  warnings: ParameterValidationWarning[];
}

/**
 * Validation error for a specific parameter
 */
export interface ParameterValidationError {
  field: keyof SeasonParameters;
  message: string;
  currentValue: any;
}

/**
 * Validation warning for a specific parameter
 */
export interface ParameterValidationWarning {
  field: keyof SeasonParameters;
  message: string;
  suggestion?: string;
}

/**
 * Helper type for parameter field labels
 */
export const PARAMETER_LABELS: Record<keyof SeasonParameters, string> = {
  forecast_horizon_weeks: 'Forecast Horizon (weeks)',
  season_start_date: 'Season Start Date',
  season_end_date: 'Season End Date',
  replenishment_strategy: 'Replenishment Strategy',
  dc_holdback_percentage: 'DC Holdback Percentage',
  markdown_checkpoint_week: 'Markdown Checkpoint Week',
  markdown_threshold: 'Markdown Threshold',
  extraction_confidence: 'Extraction Confidence',
  extraction_reasoning: 'Extraction Reasoning',
} as const;

/**
 * Parameter constraints for validation
 */
export const PARAMETER_CONSTRAINTS = {
  forecast_horizon_weeks: {
    min: 1,
    max: 52,
    description: 'Must be between 1 and 52 weeks',
  },
  dc_holdback_percentage: {
    min: 0,
    max: 1,
    description: 'Must be between 0 and 1 (0% to 100%)',
  },
  markdown_threshold: {
    min: 0,
    max: 1,
    description: 'Must be between 0 and 1 (0% to 100%)',
  },
  markdown_checkpoint_week: {
    min: 1,
    description: 'Must be at least week 1',
  },
} as const;

/**
 * Replenishment strategy options with display labels
 */
export const REPLENISHMENT_STRATEGY_OPTIONS: Array<{
  value: ReplenishmentStrategy;
  label: string;
  description: string;
}> = [
  {
    value: 'none',
    label: 'No Replenishment',
    description: 'Single initial allocation only',
  },
  {
    value: 'weekly',
    label: 'Weekly Replenishment',
    description: 'Weekly store replenishment from DC',
  },
  {
    value: 'bi-weekly',
    label: 'Bi-Weekly Replenishment',
    description: 'Replenishment every two weeks',
  },
] as const;

/**
 * Confidence level display config
 */
export const CONFIDENCE_DISPLAY = {
  high: {
    label: 'High',
    color: 'green',
    description: 'All parameters extracted with high confidence',
  },
  medium: {
    label: 'Medium',
    color: 'yellow',
    description: 'Some parameters may need review',
  },
  low: {
    label: 'Low',
    color: 'red',
    description: 'Please review and adjust parameters',
  },
} as const;
