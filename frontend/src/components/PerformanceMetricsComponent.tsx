import React, { useEffect, useState } from 'react';
import {
  PerformanceService,
  type PerformanceMetrics as PerformanceMetricsType,
  type MetricDetail,
} from '@/services/performance-service';
import { useParameters } from '@/contexts/ParametersContext';
import {
  Activity,
  TrendingUp,
  BarChart3,
  CheckCircle2,
  AlertCircle,
  Info,
  Loader2,
} from 'lucide-react';

export function PerformanceMetricsComponent() {
  const { workflowId, forecastId, workflowComplete } = useParameters();
  const [metricsData, setMetricsData] = useState<PerformanceMetricsType | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Wait for workflow completion before fetching metrics
    if (!workflowComplete || !workflowId || !forecastId) return;

    const fetchPerformanceMetrics = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await PerformanceService.getPerformanceMetrics(workflowId);
        setMetricsData(data);
      } catch (err: any) {
        console.error('Failed to fetch performance metrics:', err);

        // Handle specific error types
        let errorMessage = 'Failed to load performance metrics';
        if (err.status === 404) {
          errorMessage = 'Performance data not available. Workflow may not have completed.';
        } else if (err.status === 500) {
          errorMessage = 'Server error loading performance metrics.';
        } else if (err.status === 0 || !err.status) {
          errorMessage = 'Cannot connect to backend.';
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPerformanceMetrics();
  }, [workflowComplete, workflowId, forecastId]);

  if (!workflowId) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <p className="text-center text-gray-500">
          Complete workflow to view performance metrics
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Section 7: Performance Metrics
        </h2>
        <div className="flex items-center justify-center py-8" role="status" aria-live="polite">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="ml-3 text-gray-600">Loading performance metrics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div
          className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded"
          role="alert"
        >
          <AlertCircle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  if (!metricsData) {
    return null;
  }

  const { forecast_mape, average_variance, sell_through_percentage, system_status } =
    metricsData;

  const metricDetails = PerformanceService.formatMetricDetails(metricsData);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Section 7: Performance Metrics
          </h2>
          <p className="text-sm text-gray-600 mt-2">
            Overall system performance indicators
          </p>
        </div>
        <span
          className={`inline-block px-4 py-2 text-sm font-semibold rounded-full ${PerformanceService.getSystemStatusColor(system_status)}`}
          aria-label={`System status: ${system_status}`}
        >
          System Status: {system_status}
        </span>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Metric 1: Forecast MAPE */}
        <MetricCard
          icon={<BarChart3 className="w-5 h-5" />}
          label="Forecast MAPE"
          detail={metricDetails.mape}
        />

        {/* Metric 2: Average Variance */}
        <MetricCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="Average Variance"
          detail={metricDetails.variance}
        />

        {/* Metric 3: Sell-Through % */}
        <MetricCard
          icon={<CheckCircle2 className="w-5 h-5" />}
          label="Sell-Through %"
          detail={metricDetails.sellThrough}
        />
      </div>

      {/* System Health Summary */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h5 className="font-semibold text-gray-900 mb-2">
          System Health Summary
        </h5>
        <div className="text-sm text-gray-700">
          {system_status === 'Healthy' && (
            <p>
              All metrics are within acceptable ranges. The forecasting
              system is performing well.
            </p>
          )}
          {system_status === 'Moderate' && (
            <p>
              Some metrics are showing moderate deviation. Monitor closely
              and consider adjustments.
            </p>
          )}
          {system_status === 'Needs Attention' && (
            <p>
              One or more metrics are outside acceptable ranges. Review
              forecast parameters and agent configurations.
            </p>
          )}
        </div>

        {/* Detailed Metric Thresholds */}
        <div className="mt-4 text-xs text-gray-600 space-y-1">
          <div>
            <strong>MAPE Thresholds:</strong> Green &lt;15% | Yellow 15-25% |
            Red &gt;25%
          </div>
          <div>
            <strong>Variance Thresholds:</strong> Green &lt;10% | Yellow
            10-20% | Red &gt;20%
          </div>
          <div>
            <strong>Sell-Through Thresholds:</strong> Green &gt;60% | Yellow
            40-60% | Red &lt;40%
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// METRIC CARD COMPONENT
// ============================================================================

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  detail: MetricDetail;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, detail }) => {
  const statusColorClass = PerformanceService.getMetricStatusColor(detail.status);

  const statusLabel =
    detail.status === 'healthy'
      ? 'Healthy'
      : detail.status === 'warning'
        ? 'Moderate'
        : 'Critical';

  return (
    <div
      className={`rounded-lg border p-4 transition-colors ${statusColorClass}`}
      role="region"
      aria-label={`${label}: ${detail.displayValue} - ${statusLabel}`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium">{label}</span>
        </div>

        <div
          className="cursor-help"
          title={detail.tooltip}
          aria-describedby={`tooltip-${label.replace(/\s+/g, '-')}`}
        >
          <Info className="w-4 h-4 text-gray-400 hover:text-gray-600" />
        </div>
      </div>

      <div className="text-3xl font-bold">{detail.displayValue}</div>

      <div className="mt-2 text-xs font-semibold uppercase">
        {statusLabel}
      </div>

      <div
        id={`tooltip-${label.replace(/\s+/g, '-')}`}
        className="sr-only"
      >
        {detail.tooltip}
      </div>
    </div>
  );
};
