import { useClustersWithStores } from '@/hooks/useClustersWithStores';
import { ClusterCard } from './ClusterCard';

export function ClusterCards() {
  const { data: clusters, isLoading, error } = useClustersWithStores();

  if (isLoading) {
    return (
      <section className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-text-primary mb-6">
          Store Cluster Distribution
        </h2>
        <div className="space-y-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-card border border-border rounded-lg p-6 h-96 animate-pulse"
            >
              <div className="h-6 bg-card-hover rounded w-1/3 mb-4" />
              <div className="h-4 bg-card-hover rounded w-1/4 mb-8" />
              <div className="space-y-3">
                <div className="h-4 bg-card-hover rounded" />
                <div className="h-4 bg-card-hover rounded" />
                <div className="h-4 bg-card-hover rounded" />
              </div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="container mx-auto px-4 py-8">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">
            Failed to load cluster data. Please try again.
          </p>
        </div>
      </section>
    );
  }

  if (!clusters || clusters.length === 0) {
    return null;
  }

  return (
    <section className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-text-primary mb-2">
          Store Cluster Distribution
        </h2>
        <p className="text-text-secondary">
          Forecast allocation across {clusters.reduce((sum, c) => sum + c.store_count, 0)} stores in {clusters.length} segments
        </p>
      </div>

      <div className="space-y-6">
        {clusters.map((cluster) => (
          <ClusterCard key={cluster.cluster_id} cluster={cluster} />
        ))}
      </div>
    </section>
  );
}
