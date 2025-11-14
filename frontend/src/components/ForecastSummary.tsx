import { MetricCard } from './MetricCard';
import { useForecast } from '@/hooks/useForecast';
import { useParameters } from '@/contexts/ParametersContext';

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
 * - Real data integration with backend API
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
  const { forecastId } = useParameters();
  const { data: forecast, isLoading, error } = useForecast(forecastId);

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

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="p-4 bg-error/10 border border-error/20 rounded-lg">
          <p className="text-error font-medium">Failed to load forecast data</p>
          <p className="text-sm text-text-secondary mt-1">
            {error instanceof Error ? error.message : 'An error occurred'}
          </p>
        </div>
      </div>
    );
  }

  if (!forecast || !forecastId) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="p-4 bg-muted/50 border border-border rounded-lg">
          <p className="text-text-secondary">
            No forecast data available. Please complete the workflow first.
          </p>
        </div>
      </div>
    );
  }

  // Calculate metrics from forecast data
  const totalUnits = forecast.total_season_demand;

  // TODO: avgUnitPrice should come from backend API (e.g., /api/v1/categories/{id}/pricing)
  // For now, using reasonable default based on fashion retail standards
  const avgUnitPrice = 45;
  const totalRevenue = totalUnits * avgUnitPrice;

  // TODO: Baseline data should come from backend API (e.g., /api/v1/forecasts/{id}/baseline)
  // These values represent historical performance for the same category/season
  // Currently using industry averages as placeholders
  const baselineTotalUnits = 7200;
  const baselineAvgPrice = 42;
  const baselineRevenue = baselineTotalUnits * baselineAvgPrice;
  const baselineMarkdowns = 850000;
  const baselineExcessStock = 15;

  // Calculate deltas (percentage change from baseline)
  const unitsDelta = ((totalUnits - baselineTotalUnits) / baselineTotalUnits) * 100;
  const revenueDelta = ((totalRevenue - baselineRevenue) / baselineRevenue) * 100;

  // TODO: Markdown cost should be calculated from MarkdownDecision API
  // This represents estimated cost of clearance sales
  // Formula: (initial_stock - forecast_demand) * avg_unit_price * markdown_percentage
  const totalMarkdowns = 720000;
  const markdownsDelta = ((totalMarkdowns - baselineMarkdowns) / baselineMarkdowns) * 100;

  // TODO: Excess stock percentage should come from Inventory Agent results
  // This represents (ending_inventory / total_manufactured) * 100
  // Lower is better (indicates accurate demand forecasting)
  const excessStockPct = 8.5;
  const excessStockDelta = ((excessStockPct - baselineExcessStock) / baselineExcessStock) * 100;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-4 mb-6">
        <h2 className="text-2xl font-bold text-text-primary">
          Section 2: Forecast Summary
        </h2>
        <p className="text-text-secondary">
          Key metrics for {forecast.category_name} ({forecast.weekly_demand_curve?.length || 0} weeks forecast)
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
              Using {forecast.forecasting_method || 'ensemble'} method.
              {forecast.prophet_forecast && forecast.arima_forecast && (
                <> Prophet forecasts {forecast.prophet_forecast.toLocaleString()} units,
                ARIMA forecasts {forecast.arima_forecast.toLocaleString()} units.</>
              )}
              {forecast.peak_week && <> Peak demand expected in week {forecast.peak_week}.</>}
              {forecast.adaptation_reasoning && (
                <span className="block mt-2 text-xs italic">
                  {forecast.adaptation_reasoning}
                </span>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
