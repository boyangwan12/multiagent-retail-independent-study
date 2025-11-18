import { TrendingDown, Package } from 'lucide-react';

interface ImpactPreviewProps {
  revenueLoss: number;
  excessReduction: number;
  markdownPercent: number;
}

export function ImpactPreview({ revenueLoss, excessReduction, markdownPercent }: ImpactPreviewProps) {
  return (
    <div className="bg-card-hover rounded-lg p-4 space-y-3">
      <h4 className="text-sm font-semibold text-text-primary mb-3">
        Impact Preview ({markdownPercent}% Markdown)
      </h4>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Revenue Loss */}
        <div className="flex items-start gap-3">
          <div className="p-2 bg-red-500/10 rounded-lg">
            <TrendingDown className="h-5 w-5 text-red-400" />
          </div>
          <div className="flex-1">
            <p className="text-xs text-text-secondary mb-1">Revenue Loss</p>
            <p className="text-lg font-bold text-red-400">
              ${revenueLoss.toLocaleString()}
            </p>
            <p className="text-xs text-text-secondary mt-1">
              Due to price reduction
            </p>
          </div>
        </div>

        {/* Excess Reduction */}
        <div className="flex items-start gap-3">
          <div className="p-2 bg-green-500/10 rounded-lg">
            <Package className="h-5 w-5 text-green-400" />
          </div>
          <div className="flex-1">
            <p className="text-xs text-text-secondary mb-1">Excess Reduction</p>
            <p className="text-lg font-bold text-green-400">
              {excessReduction} units
            </p>
            <p className="text-xs text-text-secondary mt-1">
              Expected clearance
            </p>
          </div>
        </div>
      </div>

      {/* Net Impact */}
      <div className="pt-3 border-t border-border">
        <div className="flex items-center justify-between text-sm">
          <span className="text-text-secondary">Net Impact:</span>
          <span className="text-text-primary font-medium">
            Reduce excess by {excessReduction} units at ${revenueLoss.toLocaleString()} cost
          </span>
        </div>
      </div>
    </div>
  );
}
