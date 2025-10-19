/**
 * Performance Report Page
 *
 * Post-season comprehensive analysis page displaying forecast accuracy,
 * business impact, and system performance metrics.
 *
 * @component
 * @features
 * - Executive summary with key metrics
 * - MAPE analysis by week and cluster
 * - Variance events timeline
 * - Stockout/overstock analysis
 * - Markdown impact assessment
 * - System performance metrics
 * - Parameter recommendations
 *
 * @example
 * ```tsx
 * // Accessed via route /reports/:seasonId
 * <Route path="/reports/:seasonId" element={<ReportPage />} />
 * ```
 *
 * @see {@link usePerformanceReport} for data fetching
 */

import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { usePerformanceReport } from '../hooks/usePerformanceReport';
import { AppLayout } from '../components/Layout';
import { ExecutiveSummary } from '../components/Report/ExecutiveSummary';
import { MapeByWeekChart } from '../components/Report/MapeByWeekChart';
import { MapeByClusterTable } from '../components/Report/MapeByClusterTable';
import { VarianceTimeline } from '../components/Report/VarianceTimeline';
import { StockAnalysis } from '../components/Report/StockAnalysis';
import { MarkdownImpact } from '../components/Report/MarkdownImpact';
import { SystemMetrics } from '../components/Report/SystemMetrics';
import { ParameterRecommendations } from '../components/Report/ParameterRecommendations';

export function ReportPage() {
  const { seasonId } = useParams<{ seasonId: string }>();
  const { data: report, isLoading, error } = usePerformanceReport(seasonId || 'spring-2025');

  // Loading state
  if (isLoading) {
    return (
      <AppLayout showSidebar={false} breadcrumbs={[{ label: 'Loading Report...' }]}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-text-secondary">Loading performance report...</p>
            </div>
          </div>
        </div>
      </AppLayout>
    );
  }

  // Error state
  if (error || !report) {
    return (
      <AppLayout showSidebar={false} breadcrumbs={[{ label: 'Error' }]}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <p className="text-error mb-4">Failed to load performance report</p>
              <Link
                to="/"
                className="inline-flex items-center gap-2 text-primary hover:text-primary/80"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout
      showSidebar={false}
      breadcrumbs={[
        { label: 'Dashboard', href: '/' },
        { label: `Performance Report - ${seasonId || 'Spring 2025'}` }
      ]}
    >
      <div className="max-w-7xl mx-auto">
        {/* Header with back button */}
        <div className="mb-8">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-text-secondary hover:text-text-primary mb-4 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Performance Report
          </h1>
          <p className="text-text-secondary">
            Comprehensive post-season analysis for {seasonId?.replace('-', ' ').toUpperCase() || 'Spring 2025'}
          </p>
        </div>

        {/* Report Sections */}
        <div className="space-y-8">
          {/* Section 1: Executive Summary */}
          <section id="executive-summary">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Executive Summary
            </h2>
            <ExecutiveSummary summary={report.summary} />
          </section>

          {/* Section 2: MAPE by Week Chart */}
          <section id="mape-by-week">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Forecast Accuracy by Week
            </h2>
            <MapeByWeekChart data={report.mapeByWeek} />
          </section>

          {/* Section 3: MAPE by Cluster Table */}
          <section id="mape-by-cluster">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Forecast Accuracy by Cluster
            </h2>
            <MapeByClusterTable data={report.mapeByCluster} />
          </section>

          {/* Section 4: Variance Timeline */}
          <section id="variance-timeline">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Key Events Timeline
            </h2>
            <VarianceTimeline events={report.varianceEvents} />
          </section>

          {/* Section 5: Stock Analysis */}
          <section id="stock-analysis">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Inventory Analysis
            </h2>
            <StockAnalysis analysis={report.stockAnalysis} />
          </section>

          {/* Section 6: Markdown Impact */}
          <section id="markdown-impact">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Markdown Impact
            </h2>
            <MarkdownImpact impact={report.markdownImpact} />
          </section>

          {/* Section 7: System Performance */}
          <section id="system-metrics">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              System Performance
            </h2>
            <SystemMetrics metrics={report.systemPerformance} />
          </section>

          {/* Section 8: Parameter Recommendations */}
          <section id="recommendations">
            <h2 className="text-2xl font-semibold text-text-primary mb-4">
              Parameter Recommendations
            </h2>
            <ParameterRecommendations recommendations={report.recommendations} />
          </section>
        </div>

        {/* Footer with back button */}
        <div className="mt-12 pt-8 border-t border-border">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    </AppLayout>
  );
}
