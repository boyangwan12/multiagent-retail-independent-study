import { MetricCard } from './MetricCard';
import { useForecast } from '@/hooks/useForecast';

/**
 * ForecastSummary Component
 *
 * Section 2 of the Multi-Agent Retail Forecasting Dashboard.
 * Displays key season forecast metrics with comparison to baseline.
 *
 * @component
 *
 * @features
 * - 4 metric cards: Total Units, Revenue, Markdown Cost, Excess Stock
 * - Delta calculations vs baseline (% change)
 * - Color-coded status (green: positive, red: negative)
 * - Forecast insight panel with method details
 * - Loading skeleton during data fetch
 *
 * @example
 * ```tsx
 * <ForecastSummary />
 * ```
 *
 * @see {@link MetricCard} for individual metric display
 * @see {@link useForecast} for data fetching
 */
export function ForecastSummary() {
  const { data: forecast, isLoading } = useForecast('FORECAST_SPRING_2025');

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-64"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-40 bg-muted rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!forecast) {
    return null;
  }

  // Calculate metrics from forecast data
  const totalUnits = forecast.total_season_demand;
  const avgUnitPrice = 45; // Mock average unit price
  const totalRevenue = totalUnits * avgUnitPrice;

  // Mock baseline data for comparison
  const baselineTotalUnits = 7200;
  const baselineRevenue = baselineTotalUnits * 42;
  const baselineMarkdowns = 850000;
  const baselineExcessStock = 15;

  // Calculate deltas
  const unitsDelta = ((totalUnits - baselineTotalUnits) / baselineTotalUnits) * 100;
  const revenueDelta = ((totalRevenue - baselineRevenue) / baselineRevenue) * 100;

  // Mock markdown and excess stock metrics
  const totalMarkdowns = 720000; // Mock markdown cost
  const markdownsDelta = ((totalMarkdowns - baselineMarkdowns) / baselineMarkdowns) * 100;

  const excessStockPct = 8.5; // Mock excess stock percentage
  const excessStockDelta = ((excessStockPct - baselineExcessStock) / baselineExcessStock) * 100;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-4 mb-6">
        <h2 className="text-2xl font-bold text-text-primary">
          Section 2: Forecast Summary
        </h2>
        <p className="text-text-secondary">
          Key metrics for the {forecast.season} season ({forecast.weekly_demand_curve.length} weeks)
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricCard
          title="Total Units Forecast"
          value={totalUnits}
          delta={unitsDelta}
          format="number"
        />

        <MetricCard
          title="Projected Revenue"
          value={totalRevenue}
          delta={revenueDelta}
          format="currency"
        />

        <MetricCard
          title="Markdown Cost"
          value={totalMarkdowns}
          delta={markdownsDelta}
          format="currency"
        />

        <MetricCard
          title="Excess Stock Risk"
          value={excessStockPct}
          delta={excessStockDelta}
          format="percentage"
        />
      </div>

      {/* Additional Insights */}
      <div className="mt-6 p-4 bg-muted/50 border border-border rounded-lg">
        <div className="flex items-start gap-3">
          <div className="w-1 h-full bg-primary rounded"></div>
          <div>
            <h4 className="font-semibold text-text-primary mb-1">
              Forecast Insight
            </h4>
            <p className="text-sm text-text-secondary">
              Using {forecast.forecasting_method} ensemble method. Prophet forecasts{' '}
              {forecast.prophet_forecast.toLocaleString()} units, ARIMA forecasts{' '}
              {forecast.arima_forecast.toLocaleString()} units. Peak demand expected in
              week {forecast.peak_week}.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
