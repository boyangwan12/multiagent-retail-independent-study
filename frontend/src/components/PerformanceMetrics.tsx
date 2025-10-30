import { Link } from 'react-router-dom';
import { usePerformance } from '../hooks/usePerformance';
import { MetricCard } from './MetricCard';
import { HistoricalChart } from './HistoricalChart';
import { AgentContribution } from './AgentContribution';
import { ExternalLink, Download } from 'lucide-react';

export const PerformanceMetrics = () => {
  const { data, isLoading, error } = usePerformance();

  if (isLoading) {
    return (
      <section className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-card rounded w-64 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-64 bg-card rounded"></div>
            <div className="h-64 bg-card rounded"></div>
            <div className="h-64 bg-card rounded"></div>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="container mx-auto px-4 py-8">
        <div className="bg-card border border-error rounded-lg p-6">
          <p className="text-error">
            Failed to load performance metrics. Please try again.
          </p>
        </div>
      </section>
    );
  }

  if (!data) return null;

  return (
    <section className="container mx-auto px-4 py-8">
      {/* Section Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-text-primary mb-2">
          Season Performance Metrics
        </h2>
        <p className="text-text-secondary text-sm">
          Weekly updated forecasting accuracy, business impact, and system health
        </p>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {data.cards.map((card, index) => (
          <MetricCard key={index} data={card} />
        ))}
      </div>

      {/* Historical Performance & Agent Contributions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Historical MAPE Trend */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Historical MAPE Trend
          </h3>
          <HistoricalChart data={data.historical} />
          <div className="mt-4 text-xs text-text-secondary">
            Quarterly performance comparison showing continuous improvement
          </div>
        </div>

        {/* Agent Contributions */}
        <div className="bg-card border border-border rounded-lg p-6">
          <AgentContribution data={data.agentContributions} />
          <div className="mt-4 text-xs text-text-secondary">
            Multi-agent system contribution breakdown with trend indicators
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <Link
          to="/reports/spring-2025"
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          View Detailed Report
        </Link>

        <button
          className="flex items-center gap-2 px-4 py-2 bg-muted border border-border text-text-primary rounded-lg hover:bg-muted/80 transition-colors"
          onClick={() => {
            // Export metrics to CSV
            const csvContent = [
              ['Metric', 'Value', 'Target', 'Status'],
              ...data.cards.flatMap((card) =>
                card.metrics.map((m) => [
                  `${card.title} - ${m.label}`,
                  m.value,
                  m.target,
                  m.status,
                ])
              ),
            ]
              .map((row) => row.join(','))
              .join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'performance-metrics.csv';
            a.click();
            window.URL.revokeObjectURL(url);
          }}
        >
          <Download className="w-4 h-4" />
          Export Metrics CSV
        </button>
      </div>
    </section>
  );
};
