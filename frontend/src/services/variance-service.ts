import { apiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type { WeeklyVariance } from '@/types/variance';

export class VarianceService {
  /**
   * Get weekly variance for a specific week
   * @param forecastId - The forecast ID
   * @param weekNumber - The week number (1-indexed)
   * @returns Promise<WeeklyVariance>
   */
  static async getWeeklyVariance(
    forecastId: string,
    weekNumber: number
  ): Promise<WeeklyVariance> {
    return apiClient.get<WeeklyVariance>(
      API_ENDPOINTS.variance.getByWeek(forecastId, weekNumber)
    );
  }

  /**
   * Get variance data for all weeks
   * @param forecastId - The forecast ID
   * @param totalWeeks - Total number of weeks in forecast
   * @returns Promise<WeeklyVariance[]>
   */
  static async getAllWeeks(forecastId: string, totalWeeks: number): Promise<WeeklyVariance[]> {
    const promises = Array.from({ length: totalWeeks }, (_, i) =>
      this.getWeeklyVariance(forecastId, i + 1)
    );
    return Promise.all(promises);
  }

  /**
   * Get variance summary
   * @param forecastId - The forecast ID
   * @returns Promise<VarianceSummary>
   */
  static async getVarianceSummary(forecastId: string) {
    const response = await apiClient.get(API_ENDPOINTS.variance.getSummary(forecastId));
    return response.data;
  }
}
