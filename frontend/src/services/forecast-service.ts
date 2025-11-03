import { ApiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type { ForecastData, StoreCluster } from '@/types/forecast';

export class ForecastService {
  /**
   * Get forecast by ID
   */
  static async getForecast(forecastId: string): Promise<ForecastData> {
    const url = API_ENDPOINTS.forecasts.getById(forecastId);
    return ApiClient.get<ForecastData>(url);
  }

  /**
   * Get store clusters
   */
  static async getClusters(): Promise<StoreCluster[]> {
    const url = API_ENDPOINTS.stores.getClusters();
    return ApiClient.get<StoreCluster[]>(url);
  }
}
