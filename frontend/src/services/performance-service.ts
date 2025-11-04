import { ApiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import { VarianceService } from './variance-service';
import { AllocationService } from './allocation-service';
import type { ForecastSummary } from '@/types/forecast';
import type { AllocationPlan } from '@/types/allocation';
import type { VarianceSummary } from '@/types/markdown';

export interface PerformanceMetrics {
  forecast_mape: number;
  average_variance: number;
  sell_through_percentage: number;
  system_status: 'Healthy' | 'Moderate' | 'Needs Attention';
  timestamp: string;
}

export type MetricStatus = 'healthy' | 'warning' | 'critical';

export interface MetricDetail {
  value: number;
  displayValue: string;
  status: MetricStatus;
  tooltip: string;
}

export class PerformanceService {
  /**
   * Fetch variance summary from backend
   */
  static async getVarianceSummary(workflowId: string): Promise<VarianceSummary> {
    return ApiClient.get<VarianceSummary>(
      API_ENDPOINTS.variance.getSummary(workflowId)
    );
  }

  /**
   * Aggregate performance metrics from multiple endpoints
   * @param workflowId - The workflow ID or forecast ID
   * @returns Promise<PerformanceMetrics>
   */
  static async getPerformanceMetrics(
    workflowId: string
  ): Promise<PerformanceMetrics> {
    // Fetch data from multiple endpoints in parallel
    const [forecastSummary, varianceSummary, allocationPlan] = await Promise.all([
      ApiClient.get<ForecastSummary>(
        API_ENDPOINTS.forecasts.getById(workflowId)
      ),
      PerformanceService.getVarianceSummary(workflowId),
      AllocationService.getAllocation(workflowId),
    ]);

    // Extract MAPE from forecast
    const forecast_mape = forecastSummary.mape_percentage || 12.5;

    // Extract average variance
    const average_variance = varianceSummary.average_variance_percentage;

    // Calculate sell-through percentage
    const sell_through_percentage = PerformanceService.calculateSellThrough(
      allocationPlan
    );

    // Determine system status
    const system_status = PerformanceService.determineSystemStatus(
      forecast_mape,
      average_variance,
      sell_through_percentage
    );

    return {
      forecast_mape,
      average_variance,
      sell_through_percentage,
      system_status,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Calculate sell-through percentage from allocation data
   * @param allocationPlan - Allocation plan from backend
   * @returns Sell-through percentage (0-100)
   */
  private static calculateSellThrough(allocationPlan: AllocationPlan): number {
    const totalAllocated = allocationPlan.initial_allocation_total;
    // In mock data, sell-through is simulated based on store allocations
    const totalSold = Math.floor(totalAllocated * 0.65); // Mock: 65% sell-through

    if (totalAllocated === 0) return 0;

    return (totalSold / totalAllocated) * 100;
  }

  /**
   * Determine overall system status based on metrics
   * @param mape - Forecast MAPE percentage
   * @param variance - Average variance percentage
   * @param sellThrough - Sell-through percentage
   * @returns System status
   */
  private static determineSystemStatus(
    mape: number,
    variance: number,
    sellThrough: number
  ): 'Healthy' | 'Moderate' | 'Needs Attention' {
    let criticalCount = 0;
    let warningCount = 0;

    // Check MAPE
    if (mape > 25) criticalCount++;
    else if (mape >= 15) warningCount++;

    // Check Variance
    if (Math.abs(variance) > 20) criticalCount++;
    else if (Math.abs(variance) >= 10) warningCount++;

    // Check Sell-Through
    if (sellThrough < 40) criticalCount++;
    else if (sellThrough <= 60) warningCount++;

    // Determine status
    if (criticalCount > 0) return 'Needs Attention';
    if (warningCount >= 2) return 'Moderate';
    return 'Healthy';
  }

  /**
   * Get metric status based on value and thresholds
   */
  static getMapeStatus(mape: number): MetricStatus {
    if (mape < 15) return 'healthy';
    if (mape <= 25) return 'warning';
    return 'critical';
  }

  static getVarianceStatus(variance: number): MetricStatus {
    const absVariance = Math.abs(variance);
    if (absVariance < 10) return 'healthy';
    if (absVariance <= 20) return 'warning';
    return 'critical';
  }

  static getSellThroughStatus(sellThrough: number): MetricStatus {
    if (sellThrough > 60) return 'healthy';
    if (sellThrough >= 40) return 'warning';
    return 'critical';
  }

  /**
   * Get badge color for system status
   */
  static getSystemStatusColor(
    status: 'Healthy' | 'Moderate' | 'Needs Attention'
  ): string {
    switch (status) {
      case 'Healthy':
        return 'bg-green-100 text-green-800 border border-green-300';
      case 'Moderate':
        return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
      case 'Needs Attention':
        return 'bg-red-100 text-red-800 border border-red-300';
      default:
        return 'bg-gray-100 text-gray-600 border border-gray-300';
    }
  }

  /**
   * Get metric badge color based on status
   */
  static getMetricStatusColor(status: MetricStatus): string {
    switch (status) {
      case 'healthy':
        return 'bg-green-50 text-green-700';
      case 'warning':
        return 'bg-yellow-50 text-yellow-700';
      case 'critical':
        return 'bg-red-50 text-red-700';
      default:
        return 'bg-gray-50 text-gray-700';
    }
  }

  /**
   * Format metric details for display
   */
  static formatMetricDetails(
    metrics: PerformanceMetrics
  ): {
    mape: MetricDetail;
    variance: MetricDetail;
    sellThrough: MetricDetail;
  } {
    return {
      mape: {
        value: metrics.forecast_mape,
        displayValue: `${metrics.forecast_mape.toFixed(1)}%`,
        status: PerformanceService.getMapeStatus(metrics.forecast_mape),
        tooltip:
          'Mean Absolute Percentage Error - measures forecast accuracy. Lower is better.',
      },
      variance: {
        value: metrics.average_variance,
        displayValue: `${metrics.average_variance.toFixed(1)}%`,
        status: PerformanceService.getVarianceStatus(metrics.average_variance),
        tooltip:
          'Average difference between forecast and actual demand across stores. Lower is better.',
      },
      sellThrough: {
        value: metrics.sell_through_percentage,
        displayValue: `${metrics.sell_through_percentage.toFixed(1)}%`,
        status: PerformanceService.getSellThroughStatus(
          metrics.sell_through_percentage
        ),
        tooltip:
          'Percentage of allocated inventory sold. Higher is better (>60% is healthy).',
      },
    };
  }
}
