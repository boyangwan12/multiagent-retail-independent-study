import { AlertTriangle, TrendingDown } from 'lucide-react';

interface StockAnalysisProps {
  analysis: {
    stockouts: {
      count: number;
      stores: number;
      cost: string;
    };
    overstock: {
      units: number;
      stores: number;
      cost: string;
    };
  };
}

export function StockAnalysis({ analysis }: StockAnalysisProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Stockouts */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="p-2 rounded-lg bg-error/10">
            <AlertTriangle className="h-5 w-5 text-error" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary">Stockouts</h3>
            <p className="text-text-secondary text-sm">Items unavailable for sale</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between items-baseline">
            <span className="text-text-secondary text-sm">Stockout Events</span>
            <span className="text-text-primary text-2xl font-mono font-bold">
              {analysis.stockouts.count}
            </span>
          </div>
          <div className="flex justify-between items-baseline">
            <span className="text-text-secondary text-sm">Affected Stores</span>
            <span className="text-text-primary text-lg font-mono">
              {analysis.stockouts.stores}
            </span>
          </div>
          <div className="flex justify-between items-baseline pt-4 border-t border-border">
            <span className="text-text-secondary text-sm">Lost Revenue</span>
            <span className="text-error text-lg font-mono font-bold">
              {analysis.stockouts.cost}
            </span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-text-secondary text-xs">
            Target: &lt;5 stockout events per season
          </p>
        </div>
      </div>

      {/* Overstock */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="p-2 rounded-lg bg-warning/10">
            <TrendingDown className="h-5 w-5 text-warning" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary">Overstock</h3>
            <p className="text-text-secondary text-sm">Excess inventory at season end</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between items-baseline">
            <span className="text-text-secondary text-sm">Excess Units</span>
            <span className="text-text-primary text-2xl font-mono font-bold">
              {analysis.overstock.units.toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between items-baseline">
            <span className="text-text-secondary text-sm">Affected Stores</span>
            <span className="text-text-primary text-lg font-mono">
              {analysis.overstock.stores}
            </span>
          </div>
          <div className="flex justify-between items-baseline pt-4 border-t border-border">
            <span className="text-text-secondary text-sm">Markdown Cost</span>
            <span className="text-warning text-lg font-mono font-bold">
              {analysis.overstock.cost}
            </span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-text-secondary text-xs">
            Target: &lt;2,000 excess units per season
          </p>
        </div>
      </div>
    </div>
  );
}
