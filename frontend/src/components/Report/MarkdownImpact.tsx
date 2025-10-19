import { DollarSign, TrendingUp, Package, Sparkles } from 'lucide-react';

interface MarkdownImpactProps {
  impact: {
    applied: boolean;
    week: number;
    depth: number;
    revenueLift: string;
    inventoryReduction: number;
    costSavings: string;
  };
}

export function MarkdownImpact({ impact }: MarkdownImpactProps) {
  if (!impact.applied) {
    return (
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-text-secondary text-center py-8">
          No markdown was applied this season
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-warning/10">
          <DollarSign className="h-6 w-6 text-warning" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-text-primary">
            Markdown Applied - Week {impact.week}
          </h3>
          <p className="text-text-secondary text-sm">
            {impact.depth}% discount applied to clear excess inventory
          </p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Revenue Lift */}
        <div className="bg-background border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-4 w-4 text-success" />
            <span className="text-text-secondary text-sm">Revenue Lift</span>
          </div>
          <p className="text-success text-2xl font-mono font-bold">
            {impact.revenueLift}
          </p>
          <p className="text-text-muted text-xs mt-1">vs no markdown</p>
        </div>

        {/* Inventory Reduction */}
        <div className="bg-background border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Package className="h-4 w-4 text-info" />
            <span className="text-text-secondary text-sm">Inventory Cleared</span>
          </div>
          <p className="text-info text-2xl font-mono font-bold">
            {impact.inventoryReduction}%
          </p>
          <p className="text-text-muted text-xs mt-1">of excess stock</p>
        </div>

        {/* Cost Savings */}
        <div className="bg-background border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-text-secondary text-sm">Cost Savings</span>
          </div>
          <p className="text-primary text-2xl font-mono font-bold">
            {impact.costSavings}
          </p>
          <p className="text-text-muted text-xs mt-1">avoided holding costs</p>
        </div>
      </div>

      {/* Summary */}
      <div className="mt-6 pt-6 border-t border-border">
        <p className="text-text-secondary text-sm">
          The markdown strategy successfully cleared {impact.inventoryReduction}% of excess inventory
          while generating {impact.revenueLift} additional revenue compared to waiting until season end.
          Total cost savings from avoided holding costs: {impact.costSavings}.
        </p>
      </div>
    </div>
  );
}
