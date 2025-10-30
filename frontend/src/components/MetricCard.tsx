import { Check, X } from 'lucide-react';
import type { MetricCardData } from '../types';

interface MetricCardProps {
  data: MetricCardData;
}

export const MetricCard = ({ data }: MetricCardProps) => {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-text-primary mb-4">
        {data.title}
      </h3>

      <div className="space-y-3">
        {data.metrics.map((metric, index) => (
          <div key={index} className="flex items-start justify-between">
            <div className="flex-1">
              <div className="text-sm text-text-secondary mb-1">
                {metric.label}
              </div>
              <div className="font-mono text-lg text-text-primary font-semibold">
                {metric.value}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-text-secondary font-mono">
                Target: {metric.target}
              </span>
              {metric.status === 'success' ? (
                <Check className="w-4 h-4 text-success" />
              ) : metric.status === 'warning' ? (
                <span className="text-warning text-lg">⚠</span>
              ) : (
                <X className="w-4 h-4 text-error" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
