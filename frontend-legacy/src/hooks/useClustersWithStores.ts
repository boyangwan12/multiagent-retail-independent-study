import { useQuery } from '@tanstack/react-query';
import { ForecastService } from '@/services/forecast-service';
import { useParameters } from '@/contexts/ParametersContext';

export function useClustersWithStores() {
  const { workflowComplete } = useParameters();

  return useQuery({
    queryKey: ['clustersWithStores'],
    queryFn: async () => {
      return ForecastService.getClusters();
    },
    enabled: workflowComplete, // Only fetch after workflow completes
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
