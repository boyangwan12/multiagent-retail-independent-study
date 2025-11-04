import React, { useEffect, useState } from 'react';
import { MarkdownService, type MarkdownAnalysis } from '@/services/markdown-service';
import { useParameters } from '@/contexts/ParametersContext';
import { AlertCircle, TrendingDown, DollarSign, Target, Loader2 } from 'lucide-react';

export function MarkdownDecisionComponent() {
  const { workflowId, forecastId, parameters, workflowComplete } = useParameters();
  const [markdownData, setMarkdownData] = useState<MarkdownAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Wait for workflow completion and check if markdown checkpoint is set
    if (!workflowComplete || !workflowId || !parameters) return;

    // If no markdown checkpoint week, don't fetch (Section 6 will be hidden)
    if (!parameters.markdown_checkpoint_week) {
      setMarkdownData(null);
      return;
    }

    const fetchMarkdownAnalysis = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await MarkdownService.getMarkdownAnalysis(workflowId);

        // Validate markdown checkpoint week matches parameters
        if (
          data &&
          parameters.markdown_checkpoint_week &&
          data.markdown_checkpoint_week !== parameters.markdown_checkpoint_week
        ) {
          console.warn(
            `Markdown checkpoint week mismatch: expected ${parameters.markdown_checkpoint_week}, got ${data.markdown_checkpoint_week}`
          );
        }

        setMarkdownData(data);
      } catch (err: any) {
        console.error('Failed to fetch markdown analysis:', err);

        // Handle specific error types
        let errorMessage = 'Failed to load markdown analysis';
        if (err.status === 404) {
          errorMessage = 'Markdown analysis not available. Workflow may not have completed.';
        } else if (err.status === 500) {
          errorMessage = 'Server error loading markdown analysis.';
        } else if (err.status === 0 || !err.status) {
          errorMessage = 'Cannot connect to backend.';
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMarkdownAnalysis();
  }, [workflowComplete, workflowId, forecastId, parameters]);

  // If markdown is not applicable (checkpoint week not set), don't render anything
  if (!isLoading && !markdownData && !parameters?.markdown_checkpoint_week) {
    return null; // Section 6 hidden
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <TrendingDown className="w-5 h-5" />
          Section 6: Markdown Decision
        </h2>
        <div className="flex items-center justify-center py-8" role="status" aria-live="polite">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="ml-3 text-gray-600">Loading markdown analysis...</span>
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

  if (!markdownData) {
    return null; // Should not reach here, but safety check
  }

  const {
    markdown_checkpoint_week,
    markdown_threshold,
    actual_sell_through,
    gap,
    elasticity_coefficient,
    expected_impact,
    recommended_markdown_percentage,
    expected_sell_through_after_markdown,
    expected_margin_reduction,
    decision,
    justification,
    risk_assessment,
  } = markdownData;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <TrendingDown className="w-5 h-5" />
            Section 6: Markdown Decision
          </h2>
          <p className="text-sm text-gray-600 mt-2">
            Analysis at Week {markdown_checkpoint_week} of season (Threshold:{' '}
            {MarkdownService.formatSellThrough(markdown_threshold || 0)})
          </p>
        </div>
        <span
          className={`inline-block px-4 py-2 text-sm font-semibold rounded-full ${MarkdownService.getDecisionBadgeColor(decision)}`}
          aria-label={`Markdown decision: ${MarkdownService.getDecisionLabel(decision)}`}
        >
          {MarkdownService.getDecisionLabel(decision)}
        </span>
      </div>

      {/* Gap × Elasticity Formula */}
      <div
        className="bg-blue-50 border border-blue-200 rounded-lg p-4"
        role="region"
        aria-label="Gap times Elasticity analysis formula"
      >
        <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
          <Target className="w-4 h-4" />
          Gap × Elasticity Analysis
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Gap Calculation */}
          <div className="bg-white rounded p-3 border border-blue-100">
            <div className="text-xs text-gray-600 mb-1">Gap</div>
            <div className="text-lg font-bold text-blue-900">
              {MarkdownService.formatSellThrough(gap)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Threshold ({MarkdownService.formatSellThrough(markdown_threshold || 0)}) - Actual
              ({MarkdownService.formatSellThrough(actual_sell_through)})
            </div>
          </div>

          {/* Elasticity Coefficient */}
          <div className="bg-white rounded p-3 border border-blue-100">
            <div className="text-xs text-gray-600 mb-1">
              Elasticity Coefficient
            </div>
            <div className="text-lg font-bold text-blue-900">
              {elasticity_coefficient.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Price sensitivity factor
            </div>
          </div>

          {/* Expected Impact */}
          <div className="bg-white rounded p-3 border border-blue-100">
            <div className="text-xs text-gray-600 mb-1">Expected Impact</div>
            <div className="text-lg font-bold text-blue-900">
              {MarkdownService.formatSellThrough(expected_impact)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Gap × Elasticity = {gap.toFixed(3)} × {elasticity_coefficient.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      <div className="border-t pt-4">
        <h4 className="font-semibold text-gray-900 mb-3">Recommendation</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Markdown Percentage */}
          <div className="flex items-center gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="bg-orange-100 rounded-full p-2">
              <TrendingDown className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-xs text-gray-600">
                Recommended Markdown
              </div>
              <div className="text-2xl font-bold text-orange-900">
                {MarkdownService.formatMarkdownPercentage(
                  recommended_markdown_percentage
                )}
              </div>
            </div>
          </div>

          {/* Expected Outcome */}
          <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="bg-green-100 rounded-full p-2">
              <Target className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-xs text-gray-600">
                Expected Sell-Through
              </div>
              <div className="text-2xl font-bold text-green-900">
                {MarkdownService.formatSellThrough(
                  expected_sell_through_after_markdown
                )}
              </div>
              <div className="text-xs text-gray-500">
                Up from {MarkdownService.formatSellThrough(actual_sell_through)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Justification */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h5 className="font-semibold text-gray-900 mb-2">Justification</h5>
        <p className="text-sm text-gray-700">{justification}</p>
      </div>

      {/* Risk Assessment */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h5 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          Risk Assessment
        </h5>
        <div className="text-sm text-yellow-800 mb-2">{risk_assessment}</div>

        {expected_margin_reduction > 0 && (
          <div className="flex items-center gap-2 text-yellow-900 font-semibold mt-3">
            <DollarSign className="w-4 h-4" />
            Estimated Margin Reduction:{' '}
            {MarkdownService.formatCurrency(expected_margin_reduction)}
          </div>
        )}
      </div>
    </div>
  );
}
