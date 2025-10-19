interface ExecutiveSummaryProps {
  summary: {
    totalForecast: number;
    totalActual: number;
    accuracy: number;
    revenue: string;
    inventoryTurnover: string;
  };
}

export function ExecutiveSummary({ summary }: ExecutiveSummaryProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Total Forecast */}
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-text-secondary text-sm mb-1">Total Forecast</p>
        <p className="text-text-primary text-2xl font-mono font-bold">
          {summary.totalForecast.toLocaleString()}
        </p>
        <p className="text-text-muted text-xs mt-1">units</p>
      </div>

      {/* Total Actual */}
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-text-secondary text-sm mb-1">Total Actual</p>
        <p className="text-text-primary text-2xl font-mono font-bold">
          {summary.totalActual.toLocaleString()}
        </p>
        <p className="text-text-muted text-xs mt-1">units</p>
      </div>

      {/* Accuracy */}
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-text-secondary text-sm mb-1">Accuracy</p>
        <p className="text-success text-2xl font-mono font-bold">
          {summary.accuracy}%
        </p>
        <p className="text-text-muted text-xs mt-1">forecast vs actual</p>
      </div>

      {/* Revenue */}
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-text-secondary text-sm mb-1">Total Revenue</p>
        <p className="text-text-primary text-2xl font-mono font-bold">
          {summary.revenue}
        </p>
        <p className="text-text-muted text-xs mt-1">season total</p>
      </div>

      {/* Inventory Turnover */}
      <div className="bg-card border border-border rounded-lg p-6">
        <p className="text-text-secondary text-sm mb-1">Inventory Turnover</p>
        <p className="text-success text-2xl font-mono font-bold">
          {summary.inventoryTurnover}
        </p>
        <p className="text-text-muted text-xs mt-1">vs previous season</p>
      </div>
    </div>
  );
}
