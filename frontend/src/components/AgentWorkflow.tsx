import { FixedHeader } from './FixedHeader';
import { AgentCard } from './AgentCard';
import { useWorkflowPolling } from '@/hooks/useWorkflowPolling';
import { useParameters } from '@/contexts/ParametersContext';
import { WorkflowService } from '@/services/workflow-service';
import { Button } from './ui/button';
import { Play, Loader2 } from 'lucide-react';
import { useState } from 'react';
import type { AgentStatus } from '@/types';
import type { AgentState as WSAgentState } from '@/types/websocket';

interface AgentState {
  name: 'Demand Agent' | 'Inventory Agent' | 'Pricing Agent';
  status: AgentStatus;
  progress: number;
  message: string;
}

// Map WebSocket agent status to UI agent status
function mapWebSocketStatus(wsStatus: WSAgentState['status']): AgentStatus {
  switch (wsStatus) {
    case 'running':
      return 'thinking';
    case 'complete':
      return 'complete';
    case 'error':
      return 'error';
    default:
      return 'idle';
  }
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
 * - Real-time agent status updates via polling (1-second intervals)
 * - Progress tracking for each agent (0-100%)
 * - Status animations (idle → running → success → error)
 * - Overall progress calculation
 * - Workflow completion message
 * - Connection status indicator
 * - Fixed header with season parameters
 *
 * @example
 * ```tsx
 * <AgentWorkflow workflowId="wf_abc123" />
 * ```
 *
 * @see {@link AgentCard} for individual agent display
 * @see {@link useWorkflowPolling} for polling integration
 */
export function AgentWorkflow({ workflowId }: { workflowId: string | null }) {
  const { parameters } = useParameters();
  const { isConnected, agents: wsAgents, workflowComplete, workflowResult } = useWorkflowPolling(workflowId);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executeError, setExecuteError] = useState<string | null>(null);

  // Map WebSocket agents to UI agents
  const agents: AgentState[] = wsAgents.map(wsAgent => ({
    name: wsAgent.name,
    status: mapWebSocketStatus(wsAgent.status),
    progress: wsAgent.progress,
    message: wsAgent.messages[wsAgent.messages.length - 1] || 'Waiting...',
  }));

  // Calculate overall progress
  const overallProgress = Math.round(
    agents.reduce((sum, agent) => sum + agent.progress, 0) / agents.length
  );

  const handleExecuteWorkflow = async () => {
    if (!workflowId) return;

    setIsExecuting(true);
    setExecuteError(null);

    try {
      await WorkflowService.executeWorkflow(workflowId);
      // Polling will handle status updates
    } catch (error: any) {
      setExecuteError(error.message || 'Failed to execute workflow');
      console.error('Execute workflow error:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  if (!parameters) {
    return null;
  }

  return (
    <div className="w-full">
      <FixedHeader parameters={parameters} overallProgress={overallProgress} />

      <div className="container mx-auto px-4 py-8" id="section-1-agent-cards">
        <div className="space-y-4 mb-8">
          <h2 className="text-2xl font-bold text-text-primary">
            Section 1: Multi-Agent Workflow
          </h2>
          <p className="text-text-secondary">
            Watch as our three specialized agents collaborate to generate your
            forecast.
          </p>
        </div>

        {/* Connection Status Indicator */}
        {workflowId && (
          <div className="flex items-center gap-2 px-4 py-2 bg-muted rounded-lg border mb-6">
            <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-success' : 'bg-error'}`} />
            <span className="text-xs text-text-secondary">
              {isConnected ? '✅ Connected to workflow' : '❌ Disconnected'}
            </span>
            {workflowId && (
              <span className="text-xs text-text-muted ml-auto">
                ID: {workflowId}
              </span>
            )}
          </div>
        )}

        {/* Run Forecast Button */}
        {workflowId && !workflowComplete && (
          <div className="mb-6 flex flex-col items-center gap-3">
            <Button
              onClick={handleExecuteWorkflow}
              disabled={isExecuting}
              size="lg"
              className="gap-2 px-8"
            >
              {isExecuting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Executing Workflow...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Run Forecast
                </>
              )}
            </Button>
            {executeError && (
              <div className="text-sm text-error bg-error/10 px-4 py-2 rounded-lg">
                {executeError}
              </div>
            )}
          </div>
        )}

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
        {workflowComplete && (
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
                {workflowResult && (
                  <p className="text-xs text-text-muted mt-1">
                    Forecast ID: {workflowResult.forecast_id}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
