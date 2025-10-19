import { Calendar } from 'lucide-react';
import type { SeasonParameters } from '@/types/parameters';

interface FixedHeaderProps {
  parameters: SeasonParameters;
  overallProgress: number;
}

export function FixedHeader({ parameters, overallProgress }: FixedHeaderProps) {
  return (
    <div className="sticky top-0 z-40 bg-background/95 backdrop-blur-sm border-b border-border">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-6 mb-3">
          {/* Scenario Info */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Calendar className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-text-primary">
                Spring 2025 Forecast
              </h2>
              <p className="text-sm text-text-secondary">
                {parameters.season_start_date} to {parameters.season_end_date} (
                {parameters.forecast_horizon_weeks} weeks)
              </p>
            </div>
          </div>

          {/* Overall Progress */}
          <div className="text-right min-w-[120px]">
            <div className="text-sm text-text-secondary mb-1">
              Overall Progress
            </div>
            <div className="text-2xl font-bold text-text-primary">
              {overallProgress}%
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary via-agent-inventory to-success transition-all duration-700 ease-out"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>
    </div>
  );
}
