/**
 * Calculate current week number from season start date
 * @param seasonStartDate - ISO 8601 date string (e.g., "2025-01-01")
 * @returns Week number (1-indexed)
 */
export function getCurrentWeekNumber(seasonStartDate: string): number {
  const startDate = new Date(seasonStartDate);
  const today = new Date();

  // Calculate days elapsed since season start
  const daysElapsed = Math.floor((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

  // Convert to weeks (1-indexed)
  const weekNumber = Math.floor(daysElapsed / 7) + 1;

  // Return at least 1 (season hasn't started yet returns week 1)
  return Math.max(1, weekNumber);
}

/**
 * Format a date to a readable string
 * @param dateString - ISO 8601 date string
 * @returns Formatted date string (e.g., "Jan 1, 2025")
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Calculate the number of days between two dates
 * @param startDate - ISO 8601 date string
 * @param endDate - ISO 8601 date string
 * @returns Number of days between dates
 */
export function daysBetween(startDate: string, endDate: string): number {
  const start = new Date(startDate);
  const end = new Date(endDate);
  return Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
}
