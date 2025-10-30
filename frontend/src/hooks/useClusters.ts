import { useQuery } from '@tanstack/react-query';
import { mockFetch } from '@/lib/mock-api';
import clustersData from '@/mocks/clusters.json';
import type { StoreCluster } from '@/types';

export function useClusters() {
  return useQuery({
    queryKey: ['clusters'],
    queryFn: async () => {
      const data = await mockFetch<StoreCluster[]>(
        clustersData as StoreCluster[]
      );
      return data;
    },
  });
}
