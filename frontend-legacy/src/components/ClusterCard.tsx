import type { ClusterWithStores } from '@/types';
import { ClusterTable } from './ClusterTable';

interface ClusterCardProps {
  cluster: ClusterWithStores;
}

export function ClusterCard({ cluster }: ClusterCardProps) {
  // Determine tier badge color
  const getTierColor = () => {
    switch (cluster.fashion_tier) {
      case 'PREMIUM':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'MAINSTREAM':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'VALUE':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
    }
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h3 className="text-xl font-semibold text-text-primary">
            {cluster.cluster_name}
          </h3>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 text-xs font-medium rounded border ${getTierColor()}`}>
              {cluster.fashion_tier}
            </span>
            <span className="text-sm text-text-secondary">
              {cluster.store_count} stores
            </span>
          </div>
        </div>
      </div>

      {/* Summary Metrics */}
      {cluster.total_units !== undefined && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-text-secondary uppercase tracking-wide">
              Total Forecast
            </p>
            <p className="text-2xl font-bold text-text-primary">
              {cluster.total_units?.toLocaleString() ?? 'N/A'}
            </p>
            <p className="text-xs text-text-secondary">units</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-text-secondary uppercase tracking-wide">
              Allocation
            </p>
            <p className="text-2xl font-bold text-text-primary">
              {cluster.allocation_percentage?.toFixed(1) ?? 'N/A'}%
            </p>
            <p className="text-xs text-text-secondary">of total</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-text-secondary uppercase tracking-wide">
              Avg per Store
            </p>
            <p className="text-2xl font-bold text-text-primary">
              {cluster.total_units && cluster.store_count
                ? Math.round(cluster.total_units / cluster.store_count).toLocaleString()
                : 'N/A'}
            </p>
            <p className="text-xs text-text-secondary">units</p>
          </div>
        </div>
      )}

      {/* Divider */}
      {cluster.stores && cluster.stores.length > 0 && (
        <div className="border-t border-border" />
      )}

      {/* Store Table or Store List */}
      {cluster.stores && cluster.stores.length > 0 && (
        <>
          {typeof cluster.stores[0] === 'string' ? (
            // Simple list of store IDs
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-text-secondary uppercase tracking-wide">
                Stores in this cluster
              </h4>
              <div className="flex flex-wrap gap-2">
                {cluster.stores.map((storeId) => (
                  <span
                    key={storeId}
                    className="px-2 py-1 text-xs font-mono bg-muted text-text-primary rounded border border-border"
                  >
                    {storeId}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            // Full table with store details
            <ClusterTable stores={cluster.stores} />
          )}
        </>
      )}
    </div>
  );
}
