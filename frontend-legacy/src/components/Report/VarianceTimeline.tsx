import { AlertCircle, TrendingUp, DollarSign } from 'lucide-react';

interface VarianceEvent {
  week: number;
  type: 'variance' | 're-forecast' | 'markdown';
  description: string;
  impact: string;
}

interface VarianceTimelineProps {
  events: VarianceEvent[];
}

export function VarianceTimeline({ events }: VarianceTimelineProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'variance':
        return <AlertCircle className="h-5 w-5 text-error" />;
      case 're-forecast':
        return <TrendingUp className="h-5 w-5 text-info" />;
      case 'markdown':
        return <DollarSign className="h-5 w-5 text-warning" />;
      default:
        return <AlertCircle className="h-5 w-5 text-text-secondary" />;
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'variance':
        return 'border-error';
      case 're-forecast':
        return 'border-info';
      case 'markdown':
        return 'border-warning';
      default:
        return 'border-border';
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="space-y-6">
        {events.map((event, index) => (
          <div key={index} className="flex gap-4">
            {/* Timeline marker */}
            <div className="flex flex-col items-center">
              <div className={`p-2 rounded-full bg-background border-2 ${getColor(event.type)}`}>
                {getIcon(event.type)}
              </div>
              {index < events.length - 1 && (
                <div className="w-0.5 flex-1 bg-border my-2"></div>
              )}
            </div>

            {/* Event details */}
            <div className="flex-1 pb-8">
              <div className="flex items-baseline gap-2 mb-1">
                <span className="text-text-secondary text-sm font-mono">Week {event.week}</span>
                <span className="text-text-primary font-medium">{event.description}</span>
              </div>
              <p className="text-text-secondary text-sm">{event.impact}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-6 border-t border-border flex gap-6 text-xs text-text-secondary">
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-error" />
          <span>Variance Detected</span>
        </div>
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-info" />
          <span>Re-forecast Applied</span>
        </div>
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4 text-warning" />
          <span>Markdown Applied</span>
        </div>
      </div>
    </div>
  );
}
