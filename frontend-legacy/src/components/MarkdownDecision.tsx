import { useState } from 'react';
import { useMarkdown } from '@/hooks/useMarkdown';
import { MarkdownDecisionCard } from './MarkdownDecisionCard';
import type { MarkdownDecision as MarkdownDecisionType } from '@/types';

export function MarkdownDecision() {
  const { data: initialDecision, isLoading, error } = useMarkdown();
  const [decision, setDecision] = useState<MarkdownDecisionType | null>(null);

  // Update local state when data loads
  if (initialDecision && !decision) {
    setDecision(initialDecision);
  }

  const handleApply = (markdown: number) => {
    if (!decision) return;

    setDecision({
      ...decision,
      applied: true,
      override_markdown: markdown !== decision.recommended_markdown ? markdown : undefined,
    });
  };

  const handleReject = () => {
    if (!decision) return;

    setDecision({
      ...decision,
      rejected: true,
    });
  };

  if (isLoading) {
    return (
      <section className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-text-primary mb-6">
          Markdown Decision
        </h2>
        <div className="bg-card border border-border rounded-lg p-6 h-96 animate-pulse">
          <div className="space-y-4">
            <div className="h-6 bg-card-hover rounded w-1/3" />
            <div className="h-20 bg-card-hover rounded" />
            <div className="h-32 bg-card-hover rounded" />
          </div>
        </div>
      </section>
    );
  }

  if (error || !decision) {
    return (
      <section className="container mx-auto px-4 py-8">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">
            Failed to load markdown decision. Please try again.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-text-primary mb-2">
          Markdown Decision
        </h2>
        <p className="text-text-secondary">
          AI-powered clearance strategy to optimize excess stock reduction
        </p>
      </div>

      <MarkdownDecisionCard
        decision={decision}
        onApply={handleApply}
        onReject={handleReject}
      />
    </section>
  );
}
