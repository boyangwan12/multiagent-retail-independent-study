import { TrendingUp, TrendingDown } from 'lucide-react';
import type { MetricCardData } from '../types';

interface SimpleMetricCardProps {
  title: string;
  value: number;
  delta: number;
  format: 'number' | 'currency' | 'percentage';
}

interface DetailedMetricCardProps {
  data: MetricCardData;
}

type MetricCardProps = SimpleMetricCardProps | DetailedMetricCardProps;

function isDetailedProps(props: MetricCardProps): props is DetailedMetricCardProps {
  return 'data' in props;
}

export const MetricCard = (props: MetricCardProps) => {
  // Handle detailed metric card (with data object)
  if (isDetailedProps(props)) {
    const { data } = props;
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
                  <TrendingUp className="w-4 h-4 text-success" />
                ) : metric.status === 'warning' ? (
                  <span className="text-warning text-lg">⚠</span>
                ) : (
                  <TrendingDown className="w-4 h-4 text-error" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Handle simple metric card (with individual props)
  const { title, value, delta, format } = props;

  const formatValue = (val: number, fmt: string) => {
    switch (fmt) {
      case 'currency':
        return `$${val.toLocaleString()}`;
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'number':
      default:
        return val.toLocaleString();
    }
  };

  const isPositive = delta > 0;
  const deltaColor = isPositive ? 'text-success' : 'text-error';

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-sm font-medium text-text-secondary mb-2">
        {title}
      </h3>
      <div className="flex items-end justify-between">
        <div className="text-3xl font-bold text-text-primary">
          {formatValue(value, format)}
        </div>
        <div className={`flex items-center gap-1 ${deltaColor} text-sm font-medium`}>
          {isPositive ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span>{Math.abs(delta).toFixed(1)}%</span>
        </div>
      </div>
      <div className="mt-2 text-xs text-text-secondary">
        vs. baseline
      </div>
    </div>
  );
};
