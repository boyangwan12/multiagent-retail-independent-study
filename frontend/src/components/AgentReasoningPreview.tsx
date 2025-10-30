import { TrendingUp, Package, DollarSign } from 'lucide-react';
import type { SeasonParameters } from '@/types';

interface AgentReasoningPreviewProps {
  parameters: SeasonParameters;
}

export function AgentReasoningPreview({
  parameters,
}: AgentReasoningPreviewProps) {
  const agents = [
    {
      name: 'Demand Agent',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'text-agent-demand',
      bgColor: 'bg-agent-demand/10',
      borderColor: 'border-agent-demand/20',
      reasoning: `Will forecast demand over ${parameters.forecast_horizon_weeks} weeks using Prophet + ARIMA ensemble. ${
        parameters.replenishment_strategy === 'none'
          ? 'Single drop strategy - no safety stock needed.'
          : `${parameters.replenishment_strategy} replenishment requires safety stock buffer.`
      }`,
    },
    {
      name: 'Inventory Agent',
      icon: <Package className="w-5 h-5" />,
      color: 'text-agent-inventory',
      bgColor: 'bg-agent-inventory/10',
      borderColor: 'border-agent-inventory/20',
      reasoning: `Will allocate inventory across 50 stores with ${(parameters.dc_holdback_percentage * 100).toFixed(0)}% DC holdback. ${
        parameters.dc_holdback_percentage === 0
          ? 'All inventory pushed to stores immediately.'
          : 'Reserved stock available for mid-season replenishment.'
      }`,
    },
    {
      name: 'Pricing Agent',
      icon: <DollarSign className="w-5 h-5" />,
      color: 'text-agent-pricing',
      bgColor: 'bg-agent-pricing/10',
      borderColor: 'border-agent-pricing/20',
      reasoning: parameters.markdown_checkpoint_week
        ? `Will monitor sell-through and trigger markdown evaluation at week ${parameters.markdown_checkpoint_week}${
            parameters.markdown_threshold
              ? ` if below ${(parameters.markdown_threshold * 100).toFixed(0)}% sell-through`
              : ''
          }.`
        : 'Will monitor continuous pricing optimization without fixed markdown checkpoint.',
    },
  ];

  return (
    <div className="w-full max-w-5xl mx-auto space-y-3">
      <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">
        How Agents Will Adapt
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`p-4 rounded-lg border ${agent.bgColor} ${agent.borderColor}`}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className={`${agent.color}`}>{agent.icon}</div>
              <h4 className={`font-semibold ${agent.color}`}>{agent.name}</h4>
            </div>
            <p className="text-sm text-text-secondary leading-relaxed">
              {agent.reasoning}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
