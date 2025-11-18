/**
 * @deprecated This file contains mock/regex-based parameter extraction logic.
 *
 * As of PHASE4-002, parameter extraction now uses real LLM via backend API.
 * Use ParameterService.extractParameters() instead.
 *
 * This file is kept for reference only and should not be used in production code.
 *
 * @see {@link ParameterService.extractParameters} for the real implementation
 */

import type { SeasonParameters } from '@/types';

export interface ExtractionResult {
  success: boolean;
  parameters: SeasonParameters | null;
  missingFields: string[];
}

/**
 * @deprecated Use ParameterService.extractParameters() instead
 *
 * Mock LLM parameter extraction from natural language input
 * Uses regex patterns to extract 5 key parameters
 *
 * This function is no longer used after PHASE4-002 integration.
 */
export function extractParameters(input: string): ExtractionResult {
  const parameters: Partial<SeasonParameters> = {};
  const missingFields: string[] = [];
  let reasoning = '';

  // Pattern 1: Extract forecast horizon (e.g., "12 weeks", "8-week", "10 week")
  const weeksMatch = input.match(/(\d+)[\s-]?weeks?/i);
  if (weeksMatch) {
    parameters.forecast_horizon_weeks = parseInt(weeksMatch[1]);
    reasoning += `Found ${weeksMatch[1]}-week forecast horizon. `;
  } else {
    missingFields.push('forecast_horizon_weeks');
  }

  // Pattern 2: Extract start date (e.g., "March 1st", "starting 2025-03-01", "begins March 1")
  const dateMatch = input.match(
    /(?:starting|begins?|from)\s+(?:on\s+)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?|\d{4}-\d{2}-\d{2})/i
  );
  if (dateMatch) {
    const dateStr = dateMatch[1];
    parameters.season_start_date = parseDate(dateStr);
    reasoning += `Season starts on ${parameters.season_start_date}. `;
  } else {
    missingFields.push('season_start_date');
  }

  // Calculate end date based on start date and forecast horizon
  if (parameters.season_start_date && parameters.forecast_horizon_weeks) {
    const startDate = new Date(parameters.season_start_date);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + parameters.forecast_horizon_weeks * 7);
    parameters.season_end_date = endDate.toISOString().split('T')[0];
  }

  // Pattern 3: Extract replenishment strategy (e.g., "no replenishment", "weekly replenishment")
  const replenishmentMatch = input.match(
    /(?:no|without|zero)\s+replenishment|weekly\s+replenishment|bi-weekly\s+replenishment/i
  );
  if (replenishmentMatch) {
    const match = replenishmentMatch[0].toLowerCase();
    if (match.includes('no') || match.includes('without') || match.includes('zero')) {
      parameters.replenishment_strategy = 'none';
      reasoning += 'No replenishment strategy (one-time drop). ';
    } else if (match.includes('bi-weekly')) {
      parameters.replenishment_strategy = 'bi-weekly';
      reasoning += 'Bi-weekly replenishment enabled. ';
    } else {
      parameters.replenishment_strategy = 'weekly';
      reasoning += 'Weekly replenishment enabled. ';
    }
  } else {
    missingFields.push('replenishment_strategy');
  }

  // Pattern 4: Extract DC holdback percentage (e.g., "0% holdback", "15% DC reserve")
  const holdbackMatch = input.match(/(\d+)%\s+(?:holdback|DC\s+reserve|DC\s+holdback)/i);
  if (holdbackMatch) {
    parameters.dc_holdback_percentage = parseInt(holdbackMatch[1]) / 100;
    reasoning += `DC holdback at ${holdbackMatch[1]}%. `;
  } else {
    // Check for "no holdback" or "0% holdback"
    if (/(?:no|zero|0%?)\s+holdback/i.test(input)) {
      parameters.dc_holdback_percentage = 0.0;
      reasoning += 'No DC holdback (0%). ';
    } else {
      missingFields.push('dc_holdback_percentage');
    }
  }

  // Pattern 5: Extract markdown checkpoint (e.g., "markdown at week 6", "week 8 markdown")
  const markdownMatch = input.match(
    /(?:markdown|price\s+reduction)(?:\s+at)?\s+week\s+(\d+)|week\s+(\d+)\s+markdown/i
  );
  if (markdownMatch) {
    const weekNum = parseInt(markdownMatch[1] || markdownMatch[2]);
    parameters.markdown_checkpoint_week = weekNum;
    reasoning += `Markdown checkpoint at week ${weekNum}. `;

    // Extract markdown threshold (e.g., "below 60%", "if under 70% sell-through")
    const thresholdMatch = input.match(
      /(?:below|under|if\s+below|if\s+under)\s+(\d+)%\s+(?:sell-through|sellthrough)/i
    );
    if (thresholdMatch) {
      parameters.markdown_threshold = parseInt(thresholdMatch[1]) / 100;
      reasoning += `Trigger if below ${thresholdMatch[1]}% sell-through. `;
    }
  }

  // Determine confidence level
  let confidence: 'high' | 'medium' | 'low';
  if (missingFields.length === 0) {
    confidence = 'high';
    reasoning += 'All parameters extracted with high confidence.';
  } else if (missingFields.length <= 2) {
    confidence = 'medium';
    reasoning += `Some parameters missing: ${missingFields.join(', ')}.`;
  } else {
    confidence = 'low';
    reasoning += `Multiple parameters missing: ${missingFields.join(', ')}.`;
  }

  parameters.extraction_confidence = confidence;
  parameters.extraction_reasoning = reasoning.trim();

  return {
    success: missingFields.length <= 2, // Success if at most 2 fields missing
    parameters: parameters as SeasonParameters,
    missingFields,
  };
}

/**
 * Parse various date formats to ISO format (YYYY-MM-DD)
 */
function parseDate(dateStr: string): string {
  // Handle ISO format (2025-03-01)
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    return dateStr;
  }

  // Handle natural language (e.g., "March 1st", "March 1, 2025")
  const months: { [key: string]: number } = {
    january: 0,
    february: 1,
    march: 2,
    april: 3,
    may: 4,
    june: 5,
    july: 6,
    august: 7,
    september: 8,
    october: 9,
    november: 10,
    december: 11,
  };

  const parts = dateStr.match(/([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?/);
  if (parts) {
    const monthName = parts[1].toLowerCase();
    const day = parseInt(parts[2]);
    const year = parts[3] ? parseInt(parts[3]) : 2025; // Default to 2025

    const month = months[monthName];
    if (month !== undefined) {
      const date = new Date(year, month, day);
      return date.toISOString().split('T')[0];
    }
  }

  // Fallback: return current date
  return new Date().toISOString().split('T')[0];
}
