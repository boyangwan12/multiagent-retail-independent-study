import { useQuery } from '@tanstack/react-query';
import { mockFetch } from '@/lib/mock-api';
import markdownData from '@/mocks/markdown.json';
import type { MarkdownDecision } from '@/types/markdown';

export function useMarkdown() {
  return useQuery({
    queryKey: ['markdown'],
    queryFn: async () => {
      const data = await mockFetch<MarkdownDecision>(
        markdownData as MarkdownDecision
      );
      return data;
    },
  });
}
