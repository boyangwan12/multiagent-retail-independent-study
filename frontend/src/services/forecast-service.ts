import { apiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type { ForecastData, StoreCluster } from '@/types/forecast';

export class ForecastService {
  /**
   * Get forecast by ID
   */
  static async getForecast(forecastId: string): Promise<ForecastData> {
    const url = API_ENDPOINTS.forecasts.getById(forecastId);
    const response = await apiClient.get<ForecastData>(url);
    return response.data;
  }

  /**
   * Get store clusters
   */
  static async getClusters(): Promise<StoreCluster[]> {
    const url = API_ENDPOINTS.stores.getClusters();
    const response = await apiClient.get<StoreCluster[]>(url);
    return response.data;
  }
}
