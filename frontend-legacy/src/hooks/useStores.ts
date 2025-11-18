import { useQuery } from '@tanstack/react-query';
import { mockFetch } from '@/lib/mock-api';
import storesData from '@/mocks/stores.json';
import type { Store } from '@/types';

export function useStores() {
  return useQuery({
    queryKey: ['stores'],
    queryFn: async () => {
      const data = await mockFetch<Store[]>(storesData as Store[]);
      return data;
    },
  });
}
