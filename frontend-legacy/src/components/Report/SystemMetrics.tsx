import { Clock, CheckCircle, Activity, Zap } from 'lucide-react';

interface SystemMetricsProps {
  metrics: {
    runtime: string;
    approvalRate: number;
    uptime: string;
    avgResponseTime: string;
  };
}

export function SystemMetrics({ metrics }: SystemMetricsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Runtime */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-3">
          <Clock className="h-4 w-4 text-primary" />
          <span className="text-text-secondary text-sm">Avg Runtime</span>
        </div>
        <p className="text-text-primary text-2xl font-mono font-bold mb-1">
          {metrics.runtime}
        </p>
        <p className="text-success text-xs">Target: &lt;60s</p>
      </div>

      {/* Approval Rate */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle className="h-4 w-4 text-success" />
          <span className="text-text-secondary text-sm">Approval Rate</span>
        </div>
        <p className="text-text-primary text-2xl font-mono font-bold mb-1">
          {metrics.approvalRate}%
        </p>
        <p className="text-success text-xs">Target: &gt;80%</p>
      </div>

      {/* Uptime */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="h-4 w-4 text-info" />
          <span className="text-text-secondary text-sm">System Uptime</span>
        </div>
        <p className="text-text-primary text-2xl font-mono font-bold mb-1">
          {metrics.uptime}
        </p>
        <p className="text-success text-xs">Target: &gt;99%</p>
      </div>

      {/* Avg Response Time */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="h-4 w-4 text-warning" />
          <span className="text-text-secondary text-sm">Avg Response</span>
        </div>
        <p className="text-text-primary text-2xl font-mono font-bold mb-1">
          {metrics.avgResponseTime}
        </p>
        <p className="text-success text-xs">Target: &lt;3s</p>
      </div>
    </div>
  );
}
