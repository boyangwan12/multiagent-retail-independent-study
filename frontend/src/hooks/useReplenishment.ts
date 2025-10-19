import { useQuery } from '@tanstack/react-query';
import { mockFetch } from '@/lib/mock-api';
import replenishmentData from '@/mocks/replenishment.json';
import type { ReplenishmentItem } from '@/types/replenishment';

export function useReplenishment() {
  return useQuery({
    queryKey: ['replenishment'],
    queryFn: async () => {
      const data = await mockFetch<ReplenishmentItem[]>(
        replenishmentData as ReplenishmentItem[]
      );
      return data;
    },
  });
}
