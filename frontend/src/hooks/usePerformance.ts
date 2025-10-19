import { useQuery } from '@tanstack/react-query';
import type { PerformanceMetrics } from '../types/performance';

export const usePerformance = () => {
  return useQuery<PerformanceMetrics>({
    queryKey: ['performance'],
    queryFn: async () => {
      const response = await fetch('/src/mocks/performance.json');
      if (!response.ok) {
        throw new Error('Failed to fetch performance metrics');
      }
      return response.json();
    },
  });
};
