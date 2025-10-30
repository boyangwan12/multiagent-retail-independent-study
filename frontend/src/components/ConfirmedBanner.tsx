import { CheckCircle, Edit2 } from 'lucide-react';
import type { SeasonParameters } from '@/types';

interface ConfirmedBannerProps {
  parameters: SeasonParameters;
  onEdit: () => void;
}

export function ConfirmedBanner({ parameters, onEdit }: ConfirmedBannerProps) {
  return (
    <div className="w-full max-w-5xl mx-auto p-4 bg-muted border border-border rounded-lg">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <CheckCircle className="w-6 h-6 text-success flex-shrink-0 mt-0.5" />
          <div className="space-y-2 flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-text-primary">
              Season Parameters Confirmed
            </h3>
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-text-secondary">
              <div>
                <span className="font-medium">Duration:</span>{' '}
                {parameters.forecast_horizon_weeks} weeks
              </div>
              <div>
                <span className="font-medium">Start:</span>{' '}
                {parameters.season_start_date}
              </div>
              <div>
                <span className="font-medium">Replenishment:</span>{' '}
                {parameters.replenishment_strategy === 'none'
                  ? 'None'
                  : parameters.replenishment_strategy === 'weekly'
                    ? 'Weekly'
                    : 'Bi-weekly'}
              </div>
              <div>
                <span className="font-medium">DC Holdback:</span>{' '}
                {(parameters.dc_holdback_percentage * 100).toFixed(0)}%
              </div>
              {parameters.markdown_checkpoint_week && (
                <div>
                  <span className="font-medium">Markdown:</span> Week{' '}
                  {parameters.markdown_checkpoint_week}
                </div>
              )}
            </div>
          </div>
        </div>

        <button
          onClick={onEdit}
          className="flex-shrink-0 px-4 py-2 flex items-center gap-2 bg-card text-text-primary border border-border rounded-lg hover:bg-hover transition-colors"
        >
          <Edit2 className="w-4 h-4" />
          Edit
        </button>
      </div>
    </div>
  );
}
