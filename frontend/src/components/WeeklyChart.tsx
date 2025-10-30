import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Label,
} from 'recharts';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { useForecast } from '@/hooks/useForecast';
import { useParameters } from '@/contexts/ParametersContext';
import { CustomTooltip } from './CustomTooltip';

export function WeeklyChart() {
  const { parameters } = useParameters();
  const { data: forecast, isLoading, error } = useForecast(
    parameters ? 'FORECAST_SPRING_2025' : undefined
  );
  const [reforecastTriggered, setReforecastTriggered] = useState(false);

  if (isLoading) {
    return (
      <section className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-text-primary mb-6">
          Weekly Performance
        </h2>
        <div className="bg-card border border-border rounded-lg p-6 h-96 animate-pulse">
          <div className="h-full bg-card-hover rounded" />
        </div>
      </section>
    );
  }

  if (error || !forecast) {
    return (
      <section className="container mx-auto px-4 py-8">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">
            Failed to load forecast data. Please try again.
          </p>
        </div>
      </section>
    );
  }

  const weeklyData = forecast.weekly_demand_curve;

  // Find weeks with variance > 20%
  const highVarianceWeeks = weeklyData.filter(
    (week) => week.variance_pct !== null && week.variance_pct !== undefined && Math.abs(week.variance_pct) > 20
  );

  const hasHighVariance = highVarianceWeeks.length > 0;

  const handleReforecast = () => {
    setReforecastTriggered(true);
    // In a real app, this would trigger an API call to re-run the forecast
    setTimeout(() => {
      alert('Re-forecast initiated! The system will update predictions based on latest actuals.');
    }, 300);
  };

  return (
    <section className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-text-primary mb-2">
          Weekly Performance: Forecast vs Actuals
        </h2>
        <p className="text-text-secondary">
          {forecast.season} - {forecast.category_id}
        </p>
      </div>

      {/* High Variance Warning */}
      {hasHighVariance && !reforecastTriggered && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-yellow-400 mb-1">
              High Variance Detected
            </h3>
            <p className="text-sm text-text-secondary mb-3">
              {highVarianceWeeks.length} week(s) show variance &gt;20%. Consider
              triggering a re-forecast to adjust predictions.
            </p>
            <button
              onClick={handleReforecast}
              className="flex items-center gap-2 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 border border-yellow-500/30 rounded-lg text-sm font-medium text-yellow-400 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Trigger Re-forecast
            </button>
          </div>
        </div>
      )}

      {reforecastTriggered && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 mb-6 flex items-center gap-3">
          <RefreshCw className="h-5 w-5 text-green-400" />
          <p className="text-sm text-green-400">
            Re-forecast triggered successfully. The system is updating predictions...
          </p>
        </div>
      )}

      {/* Chart */}
      <div className="bg-card border border-border rounded-lg p-6">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={weeklyData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3c" />
            <XAxis
              dataKey="week_number"
              stroke="#8b92a7"
              tick={{ fill: '#8b92a7' }}
              label={{ value: 'Week', position: 'insideBottom', offset: -10, fill: '#8b92a7' }}
            />
            <YAxis
              stroke="#8b92a7"
              tick={{ fill: '#8b92a7' }}
              label={{ value: 'Units', angle: -90, position: 'insideLeft', fill: '#8b92a7' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="line"
            />

            {/* Forecast Line */}
            <Line
              type="monotone"
              dataKey="forecasted_units"
              stroke="#5e6ad2"
              strokeWidth={2}
              dot={{ fill: '#5e6ad2', r: 4 }}
              activeDot={{ r: 6 }}
              name="Forecast"
              connectNulls
            />

            {/* Actuals Line */}
            <Line
              type="monotone"
              dataKey="actual_units"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ fill: '#10b981', r: 4 }}
              activeDot={{ r: 6 }}
              name="Actuals"
              connectNulls
            />

            {/* Variance Annotations for weeks > 20% */}
            {highVarianceWeeks.map((week) => (
              <ReferenceLine
                key={`variance-${week.week_number}`}
                x={week.week_number}
                stroke="#ef4444"
                strokeDasharray="3 3"
                strokeWidth={1}
              >
                <Label
                  value={`${week.variance_pct?.toFixed(0)}%`}
                  position="top"
                  fill="#ef4444"
                  fontSize={12}
                  fontWeight="bold"
                />
              </ReferenceLine>
            ))}
          </LineChart>
        </ResponsiveContainer>

        {/* Chart Footer Info */}
        <div className="mt-4 pt-4 border-t border-border">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-text-secondary">Forecasting Method: </span>
              <span className="text-text-primary font-medium">
                {forecast.forecasting_method.replace(/_/g, ' ').toUpperCase()}
              </span>
            </div>
            <div>
              <span className="text-text-secondary">Peak Week: </span>
              <span className="text-text-primary font-medium">
                Week {forecast.peak_week}
              </span>
            </div>
            <div>
              <span className="text-text-secondary">Total Season Demand: </span>
              <span className="text-text-primary font-medium">
                {forecast.total_season_demand.toLocaleString()} units
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
