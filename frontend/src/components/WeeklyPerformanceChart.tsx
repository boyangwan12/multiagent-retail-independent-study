import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { VarianceService } from '@/services/variance-service';
import { useParameters } from '@/contexts/ParametersContext';
import { AlertCircle, Loader2, ChevronUp, ChevronDown, Upload as UploadIcon } from 'lucide-react';
import { WeeklyActualsUploadModal } from './WeeklyActualsUploadModal';
import { Button } from '@/components/ui/button';
import type { WeeklyVariance } from '@/types/variance';

// Custom tooltip for the chart
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-gray-800 border border-gray-700 rounded p-3 text-white text-sm">
        <p className="font-semibold">Week {data.week}</p>
        <p className="text-blue-400">Forecast: {data.forecast.toLocaleString()}</p>
        <p className="text-green-400">Actual: {data.actual.toLocaleString()}</p>
        <p className={data.variance_pct > 0 ? 'text-red-400' : 'text-green-400'}>
          Variance: {data.variance_pct > 0 ? '+' : ''}{data.variance_pct.toFixed(1)}%
        </p>
      </div>
    );
  }
  return null;
};

export function WeeklyPerformanceChart() {
  const { forecastId, parameters, workflowComplete } = useParameters();
  const [weeklyData, setWeeklyData] = useState<WeeklyVariance[]>([]);
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadWeekNumber, setUploadWeekNumber] = useState<number>(1);

  useEffect(() => {
    // Wait for workflow completion and validate parameters
    if (!workflowComplete || !forecastId || !parameters) return;

    const fetchVarianceData = async () => {
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

  if (error || weeklyData.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded">
          <AlertCircle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-700">{error || 'No variance data available'}</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const chartData = weeklyData.map((week) => ({
    week: week.week_number,
    forecast: week.forecasted_cumulative,
    actual: week.actual_cumulative,
    variance_pct: week.variance_pct,
  }));

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

  const weekDates = calculateWeekDates(uploadWeekNumber);

  const handleUploadSuccess = async (result: any) => {
    console.log('Upload successful:', result);

    // Increment week number for next upload
    if (uploadWeekNumber < (parameters?.forecast_horizon_weeks || 12)) {
      setUploadWeekNumber(prev => prev + 1);
    }

    // Refresh variance data
    try {
      const data = await VarianceService.getAllWeeks(
        forecastId!,
        parameters!.forecast_horizon_weeks
      );
      setWeeklyData(data);
    } catch (err) {
      console.error('Failed to refresh variance data:', err);
    }

    setIsUploadModalOpen(false);
  };

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
        <Button
          onClick={() => setIsUploadModalOpen(true)}
          className="flex items-center gap-2"
          disabled={!forecastId}
        >
          <UploadIcon className="w-4 h-4" />
          Upload Week {uploadWeekNumber} Actuals
        </Button>
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
              label={{ value: 'Units (Cumulative)', angle: -90, position: 'insideLeft' }}
              tick={{ fill: '#6b7280', fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Forecast (Cumulative)"
              dot={false}
            />
            <Bar
              dataKey="actual"
              fill="#10b981"
              name="Actual (Cumulative)"
              opacity={0.8}
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
                <th className="px-4 py-3 text-right text-gray-600 font-medium">Forecast</th>
                <th className="px-4 py-3 text-right text-gray-600 font-medium">Actual</th>
                <th className="px-4 py-3 text-right text-gray-600 font-medium">Variance</th>
                <th className="px-4 py-3 text-center text-gray-600 font-medium">Status</th>
                <th className="px-4 py-3 text-center text-gray-600 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {weeklyData.map((week) => (
                <React.Fragment key={week.week_number}>
                  <tr className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">
                      Week {week.week_number}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {week.forecasted_cumulative.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {week.actual_cumulative.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span
                        className={
                          week.variance_pct > 20
                            ? 'text-red-600 font-semibold'
                            : week.variance_pct > 10
                              ? 'text-yellow-600 font-semibold'
                              : 'text-green-600'
                        }
                      >
                        {week.variance_pct > 0 ? '+' : ''}{week.variance_pct.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${
                          week.variance_pct > 20
                            ? 'bg-red-100 text-red-800'
                            : week.variance_pct > 10
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {week.variance_pct > 20
                          ? 'High Variance'
                          : week.variance_pct > 10
                            ? 'Medium Variance'
                            : 'Low Variance'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setSelectedWeek(
                            selectedWeek === week.week_number ? null : week.week_number
                          )
                        }
                        aria-expanded={selectedWeek === week.week_number}
                        aria-controls={`week-${week.week_number}-details`}
                        aria-label={`${selectedWeek === week.week_number ? 'Collapse' : 'Expand'} store-level variance for Week ${week.week_number}`}
                        className="p-2 hover:bg-gray-200 rounded transition-colors"
                      >
                        {selectedWeek === week.week_number ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </button>
                    </td>
                  </tr>

                  {/* Store-Level Variance (Expandable) */}
                  {selectedWeek === week.week_number && (
                    <tr>
                      <td colSpan={6} className="bg-gray-50 px-0">
                        <div className="py-4 px-4" id={`week-${week.week_number}-details`}>
                          <h4 className="font-semibold text-gray-900 mb-3">
                            Store-Level Variance - Week {week.week_number}
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
                                {week.store_level_variance.map((store) => (
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
                                        store.variance_pct > 20
                                          ? 'text-red-600'
                                          : store.variance_pct > 10
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
              ))}
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
