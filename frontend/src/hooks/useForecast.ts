import { useQuery } from '@tanstack/react-query';
import { mockFetch } from '@/lib/mock-api';
import forecastData from '@/mocks/forecast.json';
import type { ForecastResult } from '@/types';

export function useForecast(forecastId?: string) {
  return useQuery({
    queryKey: ['forecast', forecastId],
    queryFn: async () => {
      const data = await mockFetch<ForecastResult>(
        forecastData as ForecastResult
      );
      return data;
    },
    enabled: !!forecastId,
  });
}
