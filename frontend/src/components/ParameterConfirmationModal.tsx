import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ParameterCard } from './ParameterCard';
import {
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  AlertTriangle,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import type { SeasonParameters } from '@/types';
import { ParameterService } from '@/services/parameter-service';
import type { ParameterValidationResult } from '@/types/parameters';

interface ParameterConfirmationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  parameters: SeasonParameters | null;
  onConfirm: () => void;
  onEdit: () => void;
}

export function ParameterConfirmationModal({
  open,
  onOpenChange,
  parameters,
  onConfirm,
  onEdit,
}: ParameterConfirmationModalProps) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [validationResult, setValidationResult] =
    useState<ParameterValidationResult | null>(null);

  // Run validation when parameters change or modal opens
  useEffect(() => {
    if (parameters && open) {
      const result = ParameterService.validateParameters(parameters);
      setValidationResult(result);
    }
  }, [parameters, open]);

  if (!parameters) return null;

  const confidenceColor = {
    high: 'text-success',
    medium: 'text-warning',
    low: 'text-error',
  }[parameters.extraction_confidence];

  const confidenceIcon = {
    high: <CheckCircle className="w-5 h-5" />,
    medium: <AlertCircle className="w-5 h-5" />,
    low: <AlertCircle className="w-5 h-5" />,
  }[parameters.extraction_confidence];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="max-w-4xl max-h-[90vh] overflow-y-auto bg-background border-border"
        aria-describedby="modal-description"
      >
        <DialogHeader>
          <DialogTitle
            id="modal-title"
            className="text-2xl font-bold text-text-primary"
          >
            Confirm Season Parameters
          </DialogTitle>
          <DialogDescription
            id="modal-description"
            className="text-text-secondary"
          >
            Review the extracted parameters before proceeding with the forecast
            workflow.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Extraction Confidence */}
          <div
            className={`flex items-center gap-2 px-4 py-3 rounded-lg border ${
              parameters.extraction_confidence === 'high'
                ? 'bg-success/10 border-success/20'
                : parameters.extraction_confidence === 'medium'
                  ? 'bg-warning/10 border-warning/20'
                  : 'bg-error/10 border-error/20'
            }`}
          >
            <span className={confidenceColor}>{confidenceIcon}</span>
            <span className={`font-medium ${confidenceColor}`}>
              Extraction Confidence:{' '}
              {parameters.extraction_confidence.toUpperCase()}
            </span>
          </div>

          {/* Parameter Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ParameterCard
              name="Forecast Horizon"
              value={`${parameters.forecast_horizon_weeks} weeks`}
              icon="calendar"
              tooltip="Duration of the forecast period"
            />
            <ParameterCard
              name="Season Start Date"
              value={parameters.season_start_date}
              icon="calendar"
              tooltip="First day of the season"
            />
            <ParameterCard
              name="Replenishment Strategy"
              value={
                parameters.replenishment_strategy === 'none'
                  ? 'None (One-time drop)'
                  : parameters.replenishment_strategy === 'weekly'
                    ? 'Weekly'
                    : 'Bi-weekly'
              }
              icon="package"
              tooltip="How often inventory will be replenished"
            />
            <ParameterCard
              name="DC Holdback"
              value={`${(parameters.dc_holdback_percentage * 100).toFixed(0)}%`}
              icon="percent"
              tooltip="Percentage of inventory held back at distribution center"
            />
            {parameters.markdown_checkpoint_week && (
              <ParameterCard
                name="Markdown Checkpoint"
                value={`Week ${parameters.markdown_checkpoint_week}${
                  parameters.markdown_threshold
                    ? ` (< ${(parameters.markdown_threshold * 100).toFixed(0)}%)`
                    : ''
                }`}
                icon="trending"
                tooltip="When to evaluate markdown decisions based on sell-through rate"
              />
            )}
          </div>

          {/* Validation Errors */}
          {validationResult && validationResult.errors.length > 0 && (
            <div
              role="alert"
              aria-live="polite"
              aria-atomic="true"
              className="flex items-start gap-3 px-4 py-3 rounded-lg border border-error/20 bg-error/10"
            >
              <XCircle
                className="w-5 h-5 text-error flex-shrink-0 mt-0.5"
                aria-hidden="true"
              />
              <div className="flex-1">
                <h4 className="font-semibold text-error mb-2">
                  Validation Errors
                </h4>
                <ul className="space-y-2 text-sm text-text-secondary">
                  {validationResult.errors.map((error, index) => (
                    <li key={index} className="flex flex-col gap-1">
                      <span className="font-medium text-text-primary">
                        {error.field}:
                      </span>
                      <span>{error.message}</span>
                      {error.currentValue !== undefined &&
                        error.currentValue !== null && (
                          <span className="text-xs text-text-secondary">
                            Current value: {String(error.currentValue)}
                          </span>
                        )}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Validation Warnings */}
          {validationResult && validationResult.warnings.length > 0 && (
            <div
              role="status"
              aria-live="polite"
              aria-atomic="true"
              className="flex items-start gap-3 px-4 py-3 rounded-lg border border-warning/20 bg-warning/10"
            >
              <AlertTriangle
                className="w-5 h-5 text-warning flex-shrink-0 mt-0.5"
                aria-hidden="true"
              />
              <div className="flex-1">
                <h4 className="font-semibold text-warning mb-2">
                  Validation Warnings
                </h4>
                <ul className="space-y-2 text-sm text-text-secondary">
                  {validationResult.warnings.map((warning, index) => (
                    <li key={index} className="flex flex-col gap-1">
                      <span className="font-medium text-text-primary">
                        {warning.field}:
                      </span>
                      <span>{warning.message}</span>
                      {warning.suggestion && (
                        <span className="text-xs text-warning">
                          💡 {warning.suggestion}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Extraction Reasoning (Expandable) */}
          <div className="border border-border rounded-lg overflow-hidden">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              aria-expanded={showReasoning}
              aria-controls="extraction-reasoning-content"
              className="w-full px-4 py-3 bg-muted hover:bg-muted/80 transition-colors flex items-center justify-between text-left"
            >
              <span className="font-medium text-text-primary">
                Extraction Reasoning
              </span>
              {showReasoning ? (
                <ChevronUp
                  className="w-5 h-5 text-text-secondary"
                  aria-hidden="true"
                />
              ) : (
                <ChevronDown
                  className="w-5 h-5 text-text-secondary"
                  aria-hidden="true"
                />
              )}
            </button>
            {showReasoning && (
              <div
                id="extraction-reasoning-content"
                className="px-4 py-3 bg-card text-sm text-text-secondary"
                role="region"
                aria-label="Extraction reasoning details"
              >
                {parameters.extraction_reasoning}
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="flex gap-3">
          <button
            onClick={onEdit}
            aria-label="Edit parameters and return to input form"
            className="px-6 py-2 border border-border bg-card text-text-primary rounded-lg hover:bg-muted transition-colors"
          >
            Edit Parameters
          </button>
          <button
            onClick={onConfirm}
            disabled={validationResult && !validationResult.isValid}
            aria-label={
              validationResult && !validationResult.isValid
                ? 'Confirm button disabled due to validation errors'
                : 'Confirm parameters and proceed with forecast workflow'
            }
            aria-disabled={validationResult && !validationResult.isValid}
            className={`px-6 py-2 rounded-lg transition-opacity ${
              validationResult && !validationResult.isValid
                ? 'bg-muted text-text-secondary cursor-not-allowed opacity-50'
                : 'bg-primary text-primary-foreground hover:opacity-90'
            }`}
            title={
              validationResult && !validationResult.isValid
                ? 'Please fix validation errors before confirming'
                : 'Confirm parameters and continue'
            }
          >
            Confirm & Continue
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
