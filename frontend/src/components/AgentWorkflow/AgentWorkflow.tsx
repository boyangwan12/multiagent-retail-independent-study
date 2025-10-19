import { useEffect, useState } from 'react';
import { FixedHeader } from './FixedHeader';
import { AgentCard } from './AgentCard';
import { useAgentStatus } from '@/hooks/useAgentStatus';
import { useParameters } from '@/contexts/ParametersContext';
import type { AgentStatus } from '@/types/agent';

interface AgentState {
  name: 'Demand Agent' | 'Inventory Agent' | 'Pricing Agent';
  status: AgentStatus;
  progress: number;
  message: string;
}

/**
 * AgentWorkflow Component
 *
 * Section 1 of the Multi-Agent Retail Forecasting Dashboard.
 * Displays the multi-agent workflow with three specialized agents:
 * - Demand Agent (forecasting)
 * - Inventory Agent (allocation)
 * - Pricing Agent (markdown strategy)
 *
 * @component
 *
 * @features
 * - Real-time agent status updates via mock WebSocket
 * - Progress tracking for each agent (0-100%)
 * - Status animations (idle → running → success → error)
 * - Overall progress calculation
 * - Workflow completion message
 * - Fixed header with season parameters
 *
 * @example
 * ```tsx
 * <AgentWorkflow />
 * ```
 *
 * @see {@link AgentCard} for individual agent display
 * @see {@link useAgentStatus} for WebSocket integration
 */
export function AgentWorkflow() {
  const { parameters } = useParameters();
  const { agentState } = useAgentStatus();

  const [agents, setAgents] = useState<AgentState[]>([
    {
      name: 'Demand Agent',
      status: 'idle',
      progress: 0,
      message: 'Waiting to start forecast analysis...',
    },
    {
      name: 'Inventory Agent',
      status: 'idle',
      progress: 0,
      message: 'Waiting for demand forecast...',
    },
    {
      name: 'Pricing Agent',
      status: 'idle',
      progress: 0,
      message: 'Waiting for inventory allocation...',
    },
  ]);

  // Update agent states based on WebSocket updates
  useEffect(() => {
    if (agentState) {
      setAgents((prev) => {
        const updated = prev.map((agent) => {
          if (agent.name === agentState.agent_name) {
            return {
              ...agent,
              status: agentState.status,
              progress: agentState.progress_pct,
              message: agentState.message,
            };
          }
          return agent;
        });
        return updated;
      });
    }
  }, [agentState]);

  // Calculate overall progress
  const overallProgress = Math.round(
    agents.reduce((sum, agent) => sum + agent.progress, 0) / agents.length
  );

  if (!parameters) {
    return null;
  }

  return (
    <div className="w-full">
      <FixedHeader parameters={parameters} overallProgress={overallProgress} />

      <div className="container mx-auto px-4 py-8">
        <div className="space-y-4 mb-8">
          <h2 className="text-2xl font-bold text-text-primary">
            Section 1: Multi-Agent Workflow
          </h2>
          <p className="text-text-secondary">
            Watch as our three specialized agents collaborate to generate your
            forecast.
          </p>
        </div>

        {/* Agent Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <AgentCard
              key={agent.name}
              name={agent.name}
              status={agent.status}
              progress={agent.progress}
              message={agent.message}
            />
          ))}
        </div>

        {/* Workflow Complete Message */}
        {overallProgress === 100 && (
          <div className="mt-8 p-6 bg-success/10 border-2 border-success/30 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-success rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-success">
                  Workflow Complete!
                </h3>
                <p className="text-sm text-text-secondary">
                  All agents have finished processing. Your forecast is ready.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
