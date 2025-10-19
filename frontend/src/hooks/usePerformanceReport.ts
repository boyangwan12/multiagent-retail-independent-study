import { useQuery } from '@tanstack/react-query';

/**
 * Performance report data structure
 */
export interface PerformanceReportData {
  // Executive Summary
  summary: {
    totalForecast: number;
    totalActual: number;
    accuracy: number;
    revenue: string;
    inventoryTurnover: string;
  };

  // MAPE by Week
  mapeByWeek: Array<{
    week: number;
    mape: number;
    target: number;
  }>;

  // MAPE by Cluster
  mapeByCluster: Array<{
    clusterName: string;
    mape: number;
    bias: number;
    accuracy: number;
  }>;

  // Variance Events Timeline
  varianceEvents: Array<{
    week: number;
    type: 'variance' | 're-forecast' | 'markdown';
    description: string;
    impact: string;
  }>;

  // Stockout/Overstock Analysis
  stockAnalysis: {
    stockouts: {
      count: number;
      stores: number;
      cost: string;
    };
    overstock: {
      units: number;
      stores: number;
      cost: string;
    };
  };

  // Markdown Impact
  markdownImpact: {
    applied: boolean;
    week: number;
    depth: number;
    revenueLift: string;
    inventoryReduction: number;
    costSavings: string;
  };

  // System Performance
  systemPerformance: {
    runtime: string;
    approvalRate: number;
    uptime: string;
    avgResponseTime: string;
  };

  // Parameter Recommendations
  recommendations: Array<{
    parameter: string;
    current: string;
    suggested: string;
    reasoning: string;
  }>;
}

/**
 * Fetches performance report data from mock JSON
 * In production, this would fetch from API using the seasonId parameter
 */
async function fetchPerformanceReport(): Promise<PerformanceReportData> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));

  // Import mock data - in real implementation, performanceData would be used
  // const performanceData = await import('../mocks/performance.json');
  const forecastData = await import('../mocks/forecast.json');
  const clustersData = await import('../mocks/clusters.json');

  // Transform mock data into report structure
  return {
    summary: {
      totalForecast: forecastData.total_season_demand,
      totalActual: Math.round(forecastData.total_season_demand * 0.98), // 98% of forecast
      accuracy: 98,
      revenue: '$1.2M',
      inventoryTurnover: '+8%',
    },
    mapeByWeek: Array.from({ length: 12 }, (_, i) => ({
      week: i + 1,
      mape: 12 + Math.random() * 8, // Random between 12-20%
      target: 20,
    })),
    mapeByCluster: clustersData.map((cluster: { cluster_name: string }) => ({
      clusterName: cluster.cluster_name,
      mape: 10 + Math.random() * 10, // Random 10-20%
      bias: (Math.random() - 0.5) * 10, // Random -5% to +5%
      accuracy: 85 + Math.random() * 10, // Random 85-95%
    })),
    varianceEvents: [
      {
        week: 1,
        type: 'variance',
        description: 'Week 1: High variance detected (31%)',
        impact: 'Triggered re-forecast',
      },
      {
        week: 2,
        type: 're-forecast',
        description: 'Re-forecast completed',
        impact: 'Updated forecast: 10,500 units (+31%)',
      },
      {
        week: 6,
        type: 'markdown',
        description: 'Markdown applied (15% discount)',
        impact: 'Revenue lift: +18%, Inventory cleared',
      },
    ],
    stockAnalysis: {
      stockouts: {
        count: 3,
        stores: 2,
        cost: '$12K',
      },
      overstock: {
        units: 1800,
        stores: 8,
        cost: '$24K',
      },
    },
    markdownImpact: {
      applied: true,
      week: 6,
      depth: 15,
      revenueLift: '+18%',
      inventoryReduction: 85,
      costSavings: '$36K',
    },
    systemPerformance: {
      runtime: '58s',
      approvalRate: 85,
      uptime: '99.2%',
      avgResponseTime: '2.3s',
    },
    recommendations: [
      {
        parameter: 'Safety Stock',
        current: '20%',
        suggested: '18%',
        reasoning: 'Consistent forecast accuracy allows lower safety buffer',
      },
      {
        parameter: 'Markdown Threshold',
        current: '60%',
        suggested: '65%',
        reasoning: 'Earlier markdown trigger could reduce overstock costs',
      },
      {
        parameter: 'Re-forecast Trigger',
        current: '20%',
        suggested: '25%',
        reasoning: 'Higher threshold reduces unnecessary re-forecasts',
      },
    ],
  };
}

/**
 * Custom hook to fetch performance report data
 * @param seasonId - Season identifier (used for query key caching)
 */
export function usePerformanceReport(seasonId: string) {
  return useQuery({
    queryKey: ['performance-report', seasonId],
    queryFn: () => fetchPerformanceReport(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
