import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { VarianceService } from '@/services/variance-service';
import { useParameters } from '@/contexts/ParametersContext';
import { AlertCircle, Loader2, ChevronUp, ChevronDown, Upload as UploadIcon, RefreshCw } from 'lucide-react';
import { API_ENDPOINTS } from '@/config/api';
import { apiClient } from '@/utils/api-client';
import { WeeklyActualsUploadModal } from './WeeklyActualsUploadModal';
import { Button } from '@/components/ui/button';
import type { WeeklyVariance } from '@/types/variance';

// Custom tooltip for the chart
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const hasActual = data.actual !== null && data.actual !== undefined;
    const hasVariance = data.variance_pct !== null && data.variance_pct !== undefined;

    return (
      <div className="bg-gray-800 border border-gray-700 rounded p-3 text-white text-sm">
        <p className="font-semibold">Week {data.week}</p>
        <p className="text-blue-400">Forecast: {Math.round(data.forecast).toLocaleString()}</p>
        {hasActual ? (
          <>
            <p className="text-green-400">Actual: {Math.round(data.actual).toLocaleString()}</p>
            {hasVariance && (
              <p className={data.variance_pct > 0 ? 'text-red-400' : 'text-green-400'}>
                Variance: {data.variance_pct > 0 ? '+' : ''}{data.variance_pct.toFixed(1)}%
              </p>
            )}
          </>
        ) : (
          <p className="text-gray-400">Actual: No data yet</p>
        )}
      </div>
    );
  }
  return null;
};

export function WeeklyPerformanceChart() {
  const { forecastId, parameters, workflowComplete } = useParameters();
  const [weeklyData, setWeeklyData] = useState<WeeklyVariance[]>([]);
  const [forecastData, setForecastData] = useState<any>(null);
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadWeekNumber, setUploadWeekNumber] = useState<number>(1);
  const [viewMode, setViewMode] = useState<'cumulative' | 'weekly'>('cumulative');


  // Calculate week dates based on season start and week number
  const calculateWeekDates = (weekNum: number) => {
    if (!parameters?.season_start_date) {
      return { start: '', end: '' };
    }

    const seasonStart = new Date(parameters.season_start_date);
    const weekStartDate = new Date(seasonStart);
    weekStartDate.setDate(seasonStart.getDate() + (weekNum - 1) * 7);

    const weekEndDate = new Date(weekStartDate);
    weekEndDate.setDate(weekStartDate.getDate() + 6);

    return {
      start: weekStartDate.toISOString().split('T')[0],
      end: weekEndDate.toISOString().split('T')[0],
    };
  };

  const handleUploadSuccess = async (result: any) => {
    // Increment week number for next upload
    if (uploadWeekNumber < (parameters?.forecast_horizon_weeks || 12)) {
      setUploadWeekNumber(prev => prev + 1);
    }

    // Refresh both forecast and variance data
    try {
      await fetchForecastData();
      const data = await VarianceService.getAllWeeks(
        forecastId!,
        parameters!.forecast_horizon_weeks
      );
      setWeeklyData(data);
    } catch (err) {
      console.error('[handleUploadSuccess] Failed to refresh data:', err);
    }

    setIsUploadModalOpen(false);
  };

  // Fetch forecast data function
  const fetchForecastData = async () => {
    if (!forecastId) {
      return;
    }

    try {
      const response = await apiClient.get(API_ENDPOINTS.forecasts.getById(forecastId));
      setForecastData(response.data);
    } catch (err: any) {
      console.error('Failed to fetch forecast data:', err);
      // Don't set error state - forecast is optional for display
    }
  };

  // Fetch variance data function
  const fetchVarianceData = async () => {
    if (!workflowComplete || !forecastId || !parameters) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await VarianceService.getAllWeeks(
        forecastId,
        parameters.forecast_horizon_weeks
      );
      setWeeklyData(data);
    } catch (err: any) {
      console.error('Failed to fetch variance data:', err);

      // Handle specific error types
      let errorMessage = 'Failed to load variance data';
      if (err.status === 404) {
        errorMessage = 'Variance data not found. Workflow may not have completed.';
      } else if (err.status === 500) {
        errorMessage = 'Server error loading variance data.';
      } else if (err.status === 0 || !err.status) {
        errorMessage = 'Cannot connect to backend.';
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Combined refresh function for both forecast and variance data
  const refreshData = async () => {
    await fetchForecastData();
    await fetchVarianceData();
  };

  // Fetch both forecast and variance data
  useEffect(() => {
    fetchForecastData();
    fetchVarianceData();
  }, [workflowComplete, forecastId, parameters]);

  if (!forecastId) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <p className="text-center text-gray-500">
          Complete workflow to view weekly performance
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-center gap-2">
          <Loader2 className="h-5 w-5 animate-spin" />
          <p>Loading variance data...</p>
        </div>
      </div>
    );
  }

  // Prepare chart data - filter out any incomplete week data
  const validWeeklyData = weeklyData.filter(week =>
    week &&
    week.week_number !== undefined &&
    week.forecasted_cumulative !== undefined &&
    week.actual_cumulative !== undefined &&
    week.variance_pct !== undefined
  );

  if (error || validWeeklyData.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Section 4: Weekly Performance - Forecast vs Actuals
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Upload weekly actual sales data to begin variance tracking
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={refreshData}
              className="flex items-center gap-2"
              disabled={!forecastId || isLoading}
              variant="outline"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              onClick={() => setIsUploadModalOpen(true)}
              className="flex items-center gap-2"
              disabled={!forecastId}
            >
              <UploadIcon className="w-4 h-4" />
              Upload Week {uploadWeekNumber} Actuals
            </Button>
          </div>
        </div>

        <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded">
          <AlertCircle className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-blue-700 font-medium">No variance data available yet</p>
            <p className="text-blue-600 text-sm mt-1">
              Upload weekly actual sales data using the button above to start tracking forecast accuracy.
            </p>
          </div>
        </div>

        {/* Weekly Actuals Upload Modal */}
        <WeeklyActualsUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          weekNumber={uploadWeekNumber}
          weekStartDate={calculateWeekDates(uploadWeekNumber).start}
          weekEndDate={calculateWeekDates(uploadWeekNumber).end}
          forecastId={forecastId || ''}
          onUploadSuccess={handleUploadSuccess}
        />
      </div>
    );
  }

  // Calculate chart data for ALL weeks (showing forecast for all, actuals only where available)
  const calculateChartData = () => {
    if (!parameters) {
      return [];
    }

    const totalWeeks = parameters.forecast_horizon_weeks;
    const weeksWithActuals = new Map(validWeeklyData.map(w => [w.week_number, w]));

    // Build cumulative forecast - prefer forecastData, fallback to variance data
    let cumulativeForecast = 0;
    const forecastByWeek = Array.from({ length: totalWeeks }, (_, i) => {
      const weekNum = i + 1;
      let weekDemand = 0;

      if (forecastData && forecastData.weekly_demand_curve) {
        // Use forecast data if available
        weekDemand = forecastData.weekly_demand_curve[i]?.demand_units || 0;
      } else {
        // Fallback: reconstruct from variance data
        const weekData = weeksWithActuals.get(weekNum);
        if (weekData) {
          const prevWeekData = weekNum > 1 ? weeksWithActuals.get(weekNum - 1) : null;
          weekDemand = prevWeekData
            ? weekData.forecasted_cumulative - prevWeekData.forecasted_cumulative
            : weekData.forecasted_cumulative;
        }
      }

      cumulativeForecast += weekDemand;
      return { weekly: weekDemand, cumulative: cumulativeForecast };
    });

    return Array.from({ length: totalWeeks }, (_, i) => {
      const weekNum = i + 1;
      const weekData = weeksWithActuals.get(weekNum);
      const forecast = forecastByWeek[i];

      if (viewMode === 'cumulative') {
        return {
          week: weekNum,
          forecast: forecast.cumulative,
          actual: weekData?.actual_cumulative ?? null, // null instead of 0 to not show on chart
          variance_pct: weekData?.variance_pct ?? null,
        };
      } else {
        // Calculate weekly actual
        const prevWeekData = weekNum > 1 ? weeksWithActuals.get(weekNum - 1) : null;
        const weeklyActual = weekData && prevWeekData
          ? weekData.actual_cumulative - prevWeekData.actual_cumulative
          : weekData ? weekData.actual_cumulative : null;

        const weeklyVariancePct = forecast.weekly > 0 && weeklyActual !== null
          ? ((weeklyActual - forecast.weekly) / forecast.weekly) * 100
          : null;

        return {
          week: weekNum,
          forecast: forecast.weekly,
          actual: weeklyActual,
          variance_pct: weeklyVariancePct,
        };
      }
    });
  };

  const chartData = calculateChartData();

  const weekDates = calculateWeekDates(uploadWeekNumber);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Section 4: Weekly Performance - Forecast vs Actuals
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Monitor forecast accuracy and variance trends across all {parameters?.forecast_horizon_weeks} weeks
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('cumulative')}
              className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                viewMode === 'cumulative'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Cumulative
            </button>
            <button
              onClick={() => setViewMode('weekly')}
              className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                viewMode === 'weekly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Weekly
            </button>
          </div>
          <Button
            onClick={refreshData}
            className="flex items-center gap-2"
            disabled={!forecastId || isLoading}
            variant="outline"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-2"
            disabled={!forecastId}
          >
            <UploadIcon className="w-4 h-4" />
            Upload Week {uploadWeekNumber} Actuals
          </Button>
        </div>
      </div>

      {/* Chart */}
      <div
        role="img"
        aria-label={`Weekly performance chart showing forecast vs actual sales over ${parameters?.forecast_horizon_weeks} weeks`}
      >
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 60, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="week"
              label={{ value: 'Week', position: 'insideBottom', offset: -5 }}
              tick={{ fill: '#6b7280', fontSize: 12 }}
            />
            <YAxis
              label={{
                value: viewMode === 'cumulative' ? 'Units (Cumulative)' : 'Units (Weekly)',
                angle: -90,
                position: 'insideLeft'
              }}
              tick={{ fill: '#6b7280', fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#3b82f6"
              strokeWidth={2}
              name={viewMode === 'cumulative' ? 'Forecast (Cumulative)' : 'Forecast (Weekly)'}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#10b981"
              strokeWidth={2}
              name={viewMode === 'cumulative' ? 'Actual (Cumulative)' : 'Actual (Weekly)'}
              dot={true}
              connectNulls={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Interactive Variance Table */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Week-by-Week Breakdown</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-gray-600 font-medium">Week</th>
                <th className="px-4 py-3 text-right text-gray-600 font-medium">
                  Forecast {viewMode === 'cumulative' ? '(Cumulative)' : ''}
                </th>
                <th className="px-4 py-3 text-right text-gray-600 font-medium">
                  Actual {viewMode === 'cumulative' ? '(Cumulative)' : ''}
                </th>
                <th className="px-4 py-3 text-right text-gray-600 font-medium">Variance</th>
                <th className="px-4 py-3 text-center text-gray-600 font-medium">Status</th>
                <th className="px-4 py-3 text-center text-gray-600 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {chartData.filter(w => w.actual !== null).map((weekData) => {
                const originalWeek = validWeeklyData.find(v => v.week_number === weekData.week);
                return (
                  <React.Fragment key={weekData.week}>
                    <tr className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">
                        Week {weekData.week}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-700">
                        {Math.round(weekData.forecast).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-700">
                        {weekData.actual !== null ? Math.round(weekData.actual).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {weekData.variance_pct !== null ? (
                          <span
                            className={
                              Math.abs(weekData.variance_pct) > 20
                                ? 'text-red-600 font-semibold'
                                : Math.abs(weekData.variance_pct) > 10
                                  ? 'text-yellow-600 font-semibold'
                                  : 'text-green-600'
                            }
                          >
                            {weekData.variance_pct > 0 ? '+' : ''}{weekData.variance_pct.toFixed(1)}%
                          </span>
                        ) : (
                          <span className="text-gray-400">N/A</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {weekData.variance_pct !== null ? (
                          <span
                            className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${
                              Math.abs(weekData.variance_pct) > 20
                                ? 'bg-red-100 text-red-800'
                                : Math.abs(weekData.variance_pct) > 10
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-green-100 text-green-800'
                            }`}
                          >
                            {Math.abs(weekData.variance_pct) > 20
                              ? 'High Variance'
                              : Math.abs(weekData.variance_pct) > 10
                                ? 'Medium Variance'
                                : 'Low Variance'}
                          </span>
                        ) : (
                          <span className="text-gray-400 text-xs">No data</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-center">
                        {originalWeek && (
                          <button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              setSelectedWeek(
                                selectedWeek === weekData.week ? null : weekData.week
                              )
                            }
                            aria-expanded={selectedWeek === weekData.week}
                            aria-controls={`week-${weekData.week}-details`}
                            aria-label={`${selectedWeek === weekData.week ? 'Collapse' : 'Expand'} store-level variance for Week ${weekData.week}`}
                            className="p-2 hover:bg-gray-200 rounded transition-colors"
                          >
                            {selectedWeek === weekData.week ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <ChevronDown className="h-4 w-4" />
                            )}
                          </button>
                        )}
                      </td>
                    </tr>

                    {/* Store-Level Variance (Expandable) */}
                    {selectedWeek === weekData.week && originalWeek && (
                    <tr>
                      <td colSpan={6} className="bg-gray-50 px-0">
                        <div className="py-4 px-4" id={`week-${weekData.week}-details`}>
                          <h4 className="font-semibold text-gray-900 mb-3">
                            Store-Level Variance - Week {weekData.week}
                          </h4>
                          <div className="max-h-60 overflow-y-auto">
                            <table className="w-full text-xs">
                              <thead>
                                <tr className="border-b border-gray-200">
                                  <th className="px-3 py-2 text-left text-gray-600 font-medium">
                                    Store
                                  </th>
                                  <th className="px-3 py-2 text-right text-gray-600 font-medium">
                                    Forecast
                                  </th>
                                  <th className="px-3 py-2 text-right text-gray-600 font-medium">
                                    Actual
                                  </th>
                                  <th className="px-3 py-2 text-right text-gray-600 font-medium">
                                    Variance
                                  </th>
                                </tr>
                              </thead>
                              <tbody>
                                {originalWeek.store_level_variance.map((store) => (
                                  <tr key={store.store_id} className="border-b border-gray-100">
                                    <td className="px-3 py-2 text-gray-900">
                                      {store.store_name}
                                    </td>
                                    <td className="px-3 py-2 text-right text-gray-700">
                                      {store.forecasted}
                                    </td>
                                    <td className="px-3 py-2 text-right text-gray-700">
                                      {store.actual}
                                    </td>
                                    <td
                                      className={`px-3 py-2 text-right ${
                                        Math.abs(store.variance_pct) > 20
                                          ? 'text-red-600'
                                          : Math.abs(store.variance_pct) > 10
                                            ? 'text-yellow-600'
                                            : 'text-green-600'
                                      }`}
                                    >
                                      {store.variance_pct > 0 ? '+' : ''}
                                      {store.variance_pct.toFixed(1)}%
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </td>
                    </tr>
                    )}
                  </React.Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Weekly Actuals Upload Modal */}
      <WeeklyActualsUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        weekNumber={uploadWeekNumber}
        weekStartDate={weekDates.start}
        weekEndDate={weekDates.end}
        forecastId={forecastId || ''}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}
