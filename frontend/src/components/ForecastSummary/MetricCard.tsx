import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  delta?: number; // Percentage change from baseline (e.g., 12.5 means +12.5%)
  trend?: 'up' | 'down' | 'neutral';
  format?: 'number' | 'currency' | 'percentage';
}

export function MetricCard({
  title,
  value,
  delta,
  trend = 'neutral',
  format = 'number',
}: MetricCardProps) {
  const formatValue = (val: string | number): string => {
    if (typeof val === 'string') return val;

    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(val);
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'number':
      default:
        return new Intl.NumberFormat('en-US').format(val);
    }
  };

  const formatDelta = (d: number): string => {
    const sign = d > 0 ? '+' : '';
    return `${sign}${d.toFixed(1)}%`;
  };

  const getDeltaColor = (d: number): string => {
    if (d > 0) return 'text-success';
    if (d < 0) return 'text-error';
    return 'text-text-muted';
  };

  const getTrendIcon = () => {
    if (trend === 'up' || (delta !== undefined && delta > 0)) {
      return <TrendingUp className="w-5 h-5 text-success" />;
    }
    if (trend === 'down' || (delta !== undefined && delta < 0)) {
      return <TrendingDown className="w-5 h-5 text-error" />;
    }
    return null;
  };

  return (
    <div className="p-6 bg-card border border-border rounded-lg hover:border-primary/50 transition-all">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wide">
          {title}
        </h3>
        {getTrendIcon()}
      </div>

      <div className="space-y-2">
        <div className="text-3xl font-bold text-text-primary">
          {formatValue(value)}
        </div>

        {delta !== undefined && (
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium ${getDeltaColor(delta)}`}>
              {formatDelta(delta)}
            </span>
            <span className="text-xs text-text-muted">vs baseline</span>
          </div>
        )}
      </div>
    </div>
  );
}
