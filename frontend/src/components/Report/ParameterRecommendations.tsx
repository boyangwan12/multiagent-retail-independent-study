import { Lightbulb, ArrowRight } from 'lucide-react';

interface Recommendation {
  parameter: string;
  current: string;
  suggested: string;
  reasoning: string;
}

interface ParameterRecommendationsProps {
  recommendations: Recommendation[];
}

export function ParameterRecommendations({ recommendations }: ParameterRecommendationsProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <Lightbulb className="h-5 w-5 text-warning" />
        <p className="text-text-secondary text-sm">
          AI-generated recommendations based on this season's performance
        </p>
      </div>

      <div className="space-y-4">
        {recommendations.map((rec, index) => (
          <div
            key={index}
            className="bg-background border border-border rounded-lg p-4 hover:border-primary/30 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="text-text-primary font-medium">{rec.parameter}</h4>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-text-secondary font-mono">{rec.current}</span>
                <ArrowRight className="h-4 w-4 text-text-muted" />
                <span className="text-primary font-mono font-semibold">{rec.suggested}</span>
              </div>
            </div>
            <p className="text-text-secondary text-sm">{rec.reasoning}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-6 border-t border-border">
        <p className="text-text-muted text-xs">
          Note: These recommendations are for informational purposes only.
          Parameter changes should be reviewed by domain experts before implementation.
        </p>
      </div>
    </div>
  );
}
