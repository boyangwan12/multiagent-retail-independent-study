import type { WeeklyDemand } from '@/types/forecast';

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    dataKey: string;
    payload: WeeklyDemand;
  }>;
}

export function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const data = payload[0].payload;
  const forecast = data.forecasted_units || data.demand_units;
  const actual = data.actual_units;
  const variance = data.variance_pct;

  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
      <p className="text-sm font-semibold text-text-primary mb-2">
        Week {data.week_number}
      </p>
      <div className="space-y-1 text-xs">
        <div className="flex items-center justify-between gap-4">
          <span className="text-text-secondary">Forecast:</span>
          <span className="font-medium text-blue-400">
            {forecast?.toLocaleString() || 'N/A'} units
          </span>
        </div>
        {actual !== null && actual !== undefined && (
          <>
            <div className="flex items-center justify-between gap-4">
              <span className="text-text-secondary">Actual:</span>
              <span className="font-medium text-green-400">
                {actual.toLocaleString()} units
              </span>
            </div>
            {variance !== null && variance !== undefined && (
              <div className="flex items-center justify-between gap-4 pt-1 border-t border-border mt-1">
                <span className="text-text-secondary">Variance:</span>
                <span
                  className={`font-medium ${
                    variance > 20
                      ? 'text-red-400'
                      : variance > 10
                        ? 'text-yellow-400'
                        : 'text-green-400'
                  }`}
                >
                  {variance > 0 ? '+' : ''}
                  {variance.toFixed(1)}%
                </span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
