import { TrendingUp, Package, DollarSign, CheckCircle, Loader2 } from 'lucide-react';
import type { AgentStatus } from '@/types/agent';
import type { ReactNode } from 'react';

interface AgentCardProps {
  name: 'Demand Agent' | 'Inventory Agent' | 'Pricing Agent';
  status: AgentStatus;
  progress: number;
  message: string;
}

const agentConfig: Record<
  'Demand Agent' | 'Inventory Agent' | 'Pricing Agent',
  {
    icon: ReactNode;
    color: string;
    bgColor: string;
    borderColor: string;
  }
> = {
  'Demand Agent': {
    icon: <TrendingUp className="w-6 h-6" />,
    color: 'text-agent-demand',
    bgColor: 'bg-agent-demand/10',
    borderColor: 'border-agent-demand/30',
  },
  'Inventory Agent': {
    icon: <Package className="w-6 h-6" />,
    color: 'text-agent-inventory',
    bgColor: 'bg-agent-inventory/10',
    borderColor: 'border-agent-inventory/30',
  },
  'Pricing Agent': {
    icon: <DollarSign className="w-6 h-6" />,
    color: 'text-agent-pricing',
    bgColor: 'bg-agent-pricing/10',
    borderColor: 'border-agent-pricing/30',
  },
};

const statusConfig: Record<
  AgentStatus,
  {
    label: string;
    color: string;
    bgColor: string;
    icon?: ReactNode;
  }
> = {
  idle: {
    label: 'Idle',
    color: 'text-text-muted',
    bgColor: 'bg-muted',
  },
  thinking: {
    label: 'Thinking',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    icon: <Loader2 className="w-4 h-4 animate-spin" />,
  },
  complete: {
    label: 'Complete',
    color: 'text-success',
    bgColor: 'bg-success/10',
    icon: <CheckCircle className="w-4 h-4" />,
  },
  error: {
    label: 'Error',
    color: 'text-error',
    bgColor: 'bg-error/10',
  },
};

export function AgentCard({ name, status, progress, message }: AgentCardProps) {
  const agent = agentConfig[name];
  const statusInfo = statusConfig[status];

  return (
    <div
      className={`relative p-6 rounded-lg border-2 transition-all duration-300 ${
        status === 'thinking'
          ? `${agent.borderColor} ${agent.bgColor} animate-pulse`
          : status === 'complete'
            ? 'border-success/30 bg-success/5'
            : 'border-border bg-card'
      }`}
    >
      {/* Agent Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className={`p-3 rounded-lg ${agent.bgColor} ${agent.color} transition-colors`}
          >
            {agent.icon}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary">{name}</h3>
            <div className="flex items-center gap-2 mt-1">
              {statusInfo.icon && (
                <span className={statusInfo.color}>{statusInfo.icon}</span>
              )}
              <span
                className={`text-sm font-medium px-2 py-0.5 rounded ${statusInfo.bgColor} ${statusInfo.color}`}
              >
                {statusInfo.label}
              </span>
            </div>
          </div>
        </div>

        {/* Progress Percentage */}
        <div className="text-right">
          <div className="text-2xl font-bold text-text-primary">
            {progress}%
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-3">
        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ease-out ${
              status === 'complete'
                ? 'bg-success'
                : status === 'thinking'
                  ? 'bg-primary'
                  : 'bg-text-muted'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Status Message */}
      <p className="text-sm text-text-secondary">{message}</p>
    </div>
  );
}
