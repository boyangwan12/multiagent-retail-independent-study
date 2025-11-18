/**
 * Parameter Service
 *
 * Handles API calls related to parameter extraction and validation
 */

import { apiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  ParameterExtractionRequest,
  ParameterExtractionResponse,
  ParameterValidationResult,
  ParameterValidationError,
  ParameterValidationWarning,
} from '@/types/parameters';
import { PARAMETER_CONSTRAINTS } from '@/types/parameters';
import type { SeasonParameters } from '@/types/index';

export class ParameterService {
  /**
   * Extract parameters from natural language input using backend LLM
   *
   * @param naturalLanguageInput - User's natural language description of parameters
   * @returns Extracted parameters with confidence and reasoning
   * @throws {APIError} If extraction fails or validation errors occur
   */
  static async extractParameters(
    naturalLanguageInput: string
  ): Promise<SeasonParameters> {
    const requestBody: ParameterExtractionRequest = {
      user_input: naturalLanguageInput,
    };

    const response = await apiClient.post<ParameterExtractionResponse>(
      API_ENDPOINTS.parameters.extract(),
      requestBody
    );

    // Map backend response to frontend SeasonParameters type
    // Backend returns confidence and reasoning at response level,
    // but frontend expects them inside the parameters object
    const parameters: SeasonParameters = {
      ...response.data.parameters,
      // Ensure dates are strings (backend may return Date objects)
      season_start_date: String(response.data.parameters.season_start_date),
      season_end_date: String(response.data.parameters.season_end_date),
      // Map response-level fields into parameters object
      extraction_confidence: response.data.confidence,
      extraction_reasoning: response.data.reasoning,
    };

    return parameters;
  }

  /**
   * Validate extracted parameters client-side
   */
  static validateParameters(
    parameters: SeasonParameters
  ): ParameterValidationResult {
    const errors: ParameterValidationError[] = [];
    const warnings: ParameterValidationWarning[] = [];

    // Validate forecast_horizon_weeks
    if (
      parameters.forecast_horizon_weeks <
        PARAMETER_CONSTRAINTS.forecast_horizon_weeks.min ||
      parameters.forecast_horizon_weeks >
        PARAMETER_CONSTRAINTS.forecast_horizon_weeks.max
    ) {
      errors.push({
        field: 'forecast_horizon_weeks',
        message: `Forecast horizon must be between ${PARAMETER_CONSTRAINTS.forecast_horizon_weeks.min} and ${PARAMETER_CONSTRAINTS.forecast_horizon_weeks.max} weeks`,
        currentValue: parameters.forecast_horizon_weeks,
      });
    }

    // Validate dates
    const startDate = new Date(parameters.season_start_date);
    const endDate = new Date(parameters.season_end_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (isNaN(startDate.getTime())) {
      errors.push({
        field: 'season_start_date',
        message: 'Invalid start date format',
        currentValue: parameters.season_start_date,
      });
    }

    if (isNaN(endDate.getTime())) {
      errors.push({
        field: 'season_end_date',
        message: 'Invalid end date format',
        currentValue: parameters.season_end_date,
      });
    }

    if (startDate < today) {
      warnings.push({
        field: 'season_start_date',
        message: 'Season start date is in the past',
        suggestion: 'Consider using a future date for forecasting',
      });
    }

    if (endDate <= startDate) {
      errors.push({
        field: 'season_end_date',
        message: 'Season end date must be after start date',
        currentValue: parameters.season_end_date,
      });
    }

    // Validate dc_holdback_percentage
    if (
      parameters.dc_holdback_percentage <
        PARAMETER_CONSTRAINTS.dc_holdback_percentage.min ||
      parameters.dc_holdback_percentage >
        PARAMETER_CONSTRAINTS.dc_holdback_percentage.max
    ) {
      errors.push({
        field: 'dc_holdback_percentage',
        message: `DC holdback percentage must be between ${PARAMETER_CONSTRAINTS.dc_holdback_percentage.min} and ${PARAMETER_CONSTRAINTS.dc_holdback_percentage.max}`,
        currentValue: parameters.dc_holdback_percentage,
      });
    }

    // Validate markdown parameters (if present)
    if (parameters.markdown_checkpoint_week !== undefined && parameters.markdown_checkpoint_week !== null) {
      if (
        parameters.markdown_checkpoint_week <
        PARAMETER_CONSTRAINTS.markdown_checkpoint_week.min
      ) {
        errors.push({
          field: 'markdown_checkpoint_week',
          message: `Markdown checkpoint week must be at least ${PARAMETER_CONSTRAINTS.markdown_checkpoint_week.min}`,
          currentValue: parameters.markdown_checkpoint_week,
        });
      }

      if (
        parameters.markdown_checkpoint_week > parameters.forecast_horizon_weeks
      ) {
        errors.push({
          field: 'markdown_checkpoint_week',
          message:
            'Markdown checkpoint week cannot exceed forecast horizon',
          currentValue: parameters.markdown_checkpoint_week,
        });
      }
    }

    if (parameters.markdown_threshold !== undefined && parameters.markdown_threshold !== null) {
      if (
        parameters.markdown_threshold <
          PARAMETER_CONSTRAINTS.markdown_threshold.min ||
        parameters.markdown_threshold >
          PARAMETER_CONSTRAINTS.markdown_threshold.max
      ) {
        errors.push({
          field: 'markdown_threshold',
          message: `Markdown threshold must be between ${PARAMETER_CONSTRAINTS.markdown_threshold.min} and ${PARAMETER_CONSTRAINTS.markdown_threshold.max}`,
          currentValue: parameters.markdown_threshold,
        });
      }
    }

    // Check for markdown consistency
    const hasCheckpoint = parameters.markdown_checkpoint_week !== undefined && parameters.markdown_checkpoint_week !== null;
    const hasThreshold = parameters.markdown_threshold !== undefined && parameters.markdown_threshold !== null;

    if (hasCheckpoint && !hasThreshold) {
      warnings.push({
        field: 'markdown_threshold',
        message: 'Markdown checkpoint week is set but threshold is missing',
        suggestion: 'Consider setting a markdown threshold',
      });
    }

    if (!hasCheckpoint && hasThreshold) {
      warnings.push({
        field: 'markdown_checkpoint_week',
        message: 'Markdown threshold is set but checkpoint week is missing',
        suggestion: 'Consider setting a markdown checkpoint week',
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Format date for display
   */
  static formatDate(dateString: string): string {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  }

  /**
   * Format percentage for display
   */
  static formatPercentage(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }

  /**
   * Get replenishment strategy display label
   */
  static getReplenishmentStrategyLabel(
    strategy: SeasonParameters['replenishment_strategy']
  ): string {
    const labels = {
      none: 'No Replenishment',
      weekly: 'Weekly Replenishment',
      'bi-weekly': 'Bi-Weekly Replenishment',
    };
    return labels[strategy] || strategy;
  }
}
