import { useState } from 'react';
import { Check, X, AlertCircle } from 'lucide-react';
import type { MarkdownDecision } from '@/types';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { ImpactPreview } from './ImpactPreview';

interface MarkdownDecisionCardProps {
  decision: MarkdownDecision;
  onApply: (markdown: number) => void;
  onReject: () => void;
}

export function MarkdownDecisionCard({ decision, onApply, onReject }: MarkdownDecisionCardProps) {
  const [overrideValue, setOverrideValue] = useState<string>('');
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [error, setError] = useState<string>('');

  const currentMarkdown = overrideValue ? parseFloat(overrideValue) : decision.recommended_markdown;
  const isOverriding = overrideValue !== '';

  // Calculate dynamic impact based on current markdown
  const impactMultiplier = currentMarkdown / decision.recommended_markdown;
  const adjustedRevenueLoss = Math.round(decision.estimated_revenue_loss * impactMultiplier);
  const adjustedExcessReduction = Math.round(decision.estimated_excess_reduction * impactMultiplier);

  const handleOverrideChange = (value: string) => {
    setError('');
    setOverrideValue(value);

    if (value !== '') {
      const num = parseFloat(value);
      if (isNaN(num)) {
        setError('Please enter a valid number');
      } else if (num < 0 || num > 50) {
        setError('Markdown must be between 0% and 50%');
      }
    }
  };

  const handleApply = () => {
    if (error) return;
    setShowConfirmation(true);
  };

  const confirmApply = () => {
    onApply(currentMarkdown);
    setShowConfirmation(false);
  };

  const handleReject = () => {
    onReject();
  };

  if (decision.applied) {
    return (
      <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-2">
          <Check className="h-6 w-6 text-green-400" />
          <h3 className="text-lg font-semibold text-green-400">Markdown Applied</h3>
        </div>
        <p className="text-text-secondary">
          {decision.override_markdown
            ? `Applied ${decision.override_markdown}% markdown (override)`
            : `Applied recommended ${decision.recommended_markdown}% markdown`}
        </p>
      </div>
    );
  }

  if (decision.rejected) {
    return (
      <div className="bg-gray-500/10 border border-gray-500/20 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-2">
          <X className="h-6 w-6 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-400">Markdown Rejected</h3>
        </div>
        <p className="text-text-secondary">
          Markdown recommendation has been rejected
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-semibold text-text-primary mb-1">
            Markdown Recommendation
          </h3>
          <p className="text-sm text-text-secondary">{decision.product_category}</p>
        </div>
        <ConfidenceIndicator confidence={decision.confidence} />
      </div>

      {/* Recommended Markdown */}
      <div className="bg-card-hover rounded-lg p-4">
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-3xl font-bold text-accent">
            {decision.recommended_markdown}%
          </span>
          <span className="text-sm text-text-secondary">Recommended Markdown</span>
        </div>
        <p className="text-xs text-text-secondary">
          AI-optimized clearance strategy based on excess stock analysis
        </p>
      </div>

      {/* Stock Info */}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs text-text-secondary uppercase tracking-wide mb-1">
            Current Stock
          </p>
          <p className="text-lg font-semibold text-text-primary">
            {decision.current_stock}
          </p>
        </div>
        <div>
          <p className="text-xs text-text-secondary uppercase tracking-wide mb-1">
            Forecast Demand
          </p>
          <p className="text-lg font-semibold text-text-primary">
            {decision.forecast_demand}
          </p>
        </div>
        <div>
          <p className="text-xs text-text-secondary uppercase tracking-wide mb-1">
            Excess Stock
          </p>
          <p className="text-lg font-semibold text-red-400">
            {decision.excess_stock}
          </p>
        </div>
      </div>

      {/* Manual Override */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-text-primary">
          Manual Override (Optional)
        </label>
        <div className="flex items-start gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="0"
                max="50"
                step="0.5"
                value={overrideValue}
                onChange={(e) => handleOverrideChange(e.target.value)}
                placeholder={`${decision.recommended_markdown}%`}
                className={`w-full px-3 py-2 bg-card border ${
                  error ? 'border-red-500' : 'border-border'
                } rounded-lg text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent`}
              />
              <span className="text-text-secondary text-sm">%</span>
            </div>
            {error && (
              <p className="text-xs text-red-400 mt-1 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {error}
              </p>
            )}
            <p className="text-xs text-text-secondary mt-1">
              Enter a value between 0% and 50%
            </p>
          </div>
          {isOverriding && (
            <button
              onClick={() => {
                setOverrideValue('');
                setError('');
              }}
              className="px-3 py-2 text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Impact Preview */}
      <ImpactPreview
        revenueLoss={adjustedRevenueLoss}
        excessReduction={adjustedExcessReduction}
        markdownPercent={currentMarkdown}
      />

      {/* Action Buttons */}
      <div className="flex items-center gap-3 pt-4 border-t border-border">
        <button
          onClick={handleApply}
          disabled={!!error}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-accent hover:bg-accent/90 disabled:bg-accent/50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
        >
          <Check className="h-4 w-4" />
          Apply Markdown
        </button>
        <button
          onClick={handleReject}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 rounded-lg font-medium transition-colors"
        >
          <X className="h-4 w-4" />
          Reject
        </button>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg p-6 max-w-md mx-4">
            <h4 className="text-lg font-semibold text-text-primary mb-2">
              Confirm Markdown Application
            </h4>
            <p className="text-sm text-text-secondary mb-4">
              {isOverriding ? (
                <>
                  You are applying a <strong>{currentMarkdown}%</strong> markdown (override).
                  This will result in an estimated revenue loss of{' '}
                  <strong className="text-red-400">${adjustedRevenueLoss.toLocaleString()}</strong>{' '}
                  and clear approximately{' '}
                  <strong className="text-green-400">{adjustedExcessReduction} units</strong> of excess stock.
                </>
              ) : (
                <>
                  You are applying the recommended <strong>{currentMarkdown}%</strong> markdown.
                  This will result in an estimated revenue loss of{' '}
                  <strong className="text-red-400">${adjustedRevenueLoss.toLocaleString()}</strong>{' '}
                  and clear approximately{' '}
                  <strong className="text-green-400">{adjustedExcessReduction} units</strong> of excess stock.
                </>
              )}
            </p>
            <div className="flex items-center gap-3">
              <button
                onClick={confirmApply}
                className="flex-1 px-4 py-2 bg-accent hover:bg-accent/90 text-white rounded-lg font-medium transition-colors"
              >
                Confirm
              </button>
              <button
                onClick={() => setShowConfirmation(false)}
                className="flex-1 px-4 py-2 bg-card-hover hover:bg-card border border-border text-text-primary rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
