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
} from 'lucide-react';
import { useState } from 'react';
import type { SeasonParameters } from '@/types/parameters';

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
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-background border-border">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-text-primary">
            Confirm Season Parameters
          </DialogTitle>
          <DialogDescription className="text-text-secondary">
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

          {/* Extraction Reasoning (Expandable) */}
          <div className="border border-border rounded-lg overflow-hidden">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="w-full px-4 py-3 bg-muted hover:bg-muted/80 transition-colors flex items-center justify-between text-left"
            >
              <span className="font-medium text-text-primary">
                Extraction Reasoning
              </span>
              {showReasoning ? (
                <ChevronUp className="w-5 h-5 text-text-secondary" />
              ) : (
                <ChevronDown className="w-5 h-5 text-text-secondary" />
              )}
            </button>
            {showReasoning && (
              <div className="px-4 py-3 bg-card text-sm text-text-secondary">
                {parameters.extraction_reasoning}
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="flex gap-3">
          <button
            onClick={onEdit}
            className="px-6 py-2 border border-border bg-card text-text-primary rounded-lg hover:bg-muted transition-colors"
          >
            Edit Parameters
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
          >
            Confirm & Continue
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
