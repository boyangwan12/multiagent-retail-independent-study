import { useQuery } from '@tanstack/react-query';
import { mockFetch } from '@/lib/mock-api';
import clustersData from '@/mocks/clusters.json';
import storesData from '@/mocks/stores.json';
import type { Store, StoreCluster } from '@/types/store';
import { transformStoresToClusters } from '@/utils/clusterUtils';

export function useClustersWithStores() {
  return useQuery({
    queryKey: ['clustersWithStores'],
    queryFn: async () => {
      // Simulate API delay
      await mockFetch(null, 800);

      const stores = storesData as Store[];
      const clusters = clustersData as StoreCluster[];

      // Transform stores into cluster groups with forecast details
      const clustersWithStores = transformStoresToClusters(stores, clusters);

      return clustersWithStores;
    },
  });
}
