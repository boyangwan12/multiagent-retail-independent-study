import { useQuery } from '@tanstack/react-query';
import { ForecastService } from '@/services/forecast-service';
import type { ForecastData } from '@/types/forecast';

export function useForecast(forecastId?: string | null) {
  return useQuery({
    queryKey: ['forecast', forecastId],
    queryFn: async () => {
      if (!forecastId) {
        throw new Error('Forecast ID is required');
      }
      return ForecastService.getForecast(forecastId);
    },
    enabled: !!forecastId,
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
