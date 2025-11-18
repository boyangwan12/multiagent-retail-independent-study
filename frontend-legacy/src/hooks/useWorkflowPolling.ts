import { useEffect, useRef, useState } from 'react';
import { useParameters } from '@/contexts/ParametersContext';
import { WorkflowService } from '@/services/workflow-service';
import type { AgentState } from '@/types/websocket';

/**
 * Polling-based workflow monitoring hook (replaces WebSocket)
 *
 * Polls GET /api/v1/workflows/{workflowId} every 1 second to check status.
 * Provides the same interface as useWebSocket for drop-in replacement.
 */
export function useWorkflowPolling(workflowId: string | null) {
  const { setWorkflowComplete, setForecastId, setAllocationId, setMarkdownId } = useParameters();
  const [isConnected, setIsConnected] = useState(false);
  const [agents, setAgents] = useState<AgentState[]>([
    { name: 'Demand Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
    { name: 'Inventory Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
    { name: 'Pricing Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
  ]);
  const [workflowCompleteLocal, setWorkflowCompleteLocal] = useState(false);
  const [workflowResult, setWorkflowResult] = useState<any>(null);
  const pollIntervalRef = useRef<number | null>(null);
  const previousStatusRef = useRef<string>('');
  const previousAgentRef = useRef<string>('');

  useEffect(() => {
    // Validate workflowId
    if (!workflowId) {
      console.warn('useWorkflowPolling: No workflow ID provided');
      return;
    }

    if (!workflowId.startsWith('wf_')) {
      console.error('useWorkflowPolling: Invalid workflow ID format:', workflowId);
      return;
    }

    console.log('[POLLING] Starting polling for workflow:', workflowId);
    setIsConnected(true);

    // Start polling
    const poll = async () => {
      try {
        const status = await WorkflowService.getWorkflowStatus(workflowId);

        // Update agent states based on workflow status
        updateAgentStates(status);

        // If workflow is complete or failed, stop polling
        if (status.status === 'completed' || status.status === 'failed') {
          console.log('[POLLING] Workflow finished, stopping poll');

          if (status.status === 'completed') {
            // Fetch full results
            try {
              const results = await WorkflowService.getWorkflowResults(workflowId);
              setWorkflowCompleteLocal(true);
              setWorkflowResult(results);
              setWorkflowComplete(true);

              // Extract forecast_id from the demand agent result
              if (results.output_data?.demand?.forecast_id) {
                setForecastId(results.output_data.demand.forecast_id);
              }
            } catch (error) {
              console.error('[POLLING] Failed to fetch results:', error);
            }
          }

          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
        }
      } catch (error) {
        console.error('[POLLING] Poll error:', error);
      }
    };

    // Poll immediately, then every 1 second
    poll();
    pollIntervalRef.current = window.setInterval(poll, 1000);

    // Cleanup on unmount
    return () => {
      console.log('[POLLING] Cleanup - stopping poll');
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      setIsConnected(false);
    };
  }, [workflowId]);

  const updateAgentStates = (status: any) => {
    const { status: workflow_status, current_agent, progress_pct } = status;

    // Map agent names
    const agentNameMap: Record<string, 'Demand Agent' | 'Inventory Agent' | 'Pricing Agent'> = {
      'Demand Agent': 'Demand Agent',
      'Inventory Agent': 'Inventory Agent',
      'Pricing Agent': 'Pricing Agent',
    };

    setAgents(prev => {
      return prev.map(agent => {
        const isCurrentAgent = current_agent && agentNameMap[current_agent] === agent.name;

        // Determine agent status based on workflow state
        let agentStatus: AgentState['status'] = 'idle';
        let agentProgress = 0;
        let messages = agent.messages;

        if (workflow_status === 'running' && isCurrentAgent) {
          agentStatus = 'running';
          agentProgress = progress_pct || 0;

          // Add message if agent just started
          if (previousAgentRef.current !== current_agent) {
            messages = [...messages, `Started ${agent.name}`];
          }
        } else if (workflow_status === 'completed') {
          // All agents complete
          agentStatus = 'complete';
          agentProgress = 100;
          if (!messages.includes('Completed')) {
            messages = [...messages, 'Completed'];
          }
        } else if (workflow_status === 'failed') {
          agentStatus = 'error';
          messages = [...messages, 'Workflow failed'];
        } else {
          // Check if this agent was completed before current agent
          const agentOrder = ['Demand Agent', 'Inventory Agent', 'Pricing Agent'];
          const currentIndex = current_agent ? agentOrder.indexOf(agentNameMap[current_agent] || '') : -1;
          const thisIndex = agentOrder.indexOf(agent.name);

          if (currentIndex > thisIndex) {
            // This agent ran before the current one, so it's complete
            agentStatus = 'complete';
            agentProgress = 100;
            if (!messages.includes('Completed')) {
              messages = [...messages, 'Completed'];
            }
          }
        }

        return {
          ...agent,
          status: agentStatus,
          progress: agentProgress,
          messages,
        };
      });
    });

    // Update previous state for change detection
    previousStatusRef.current = workflow_status;
    previousAgentRef.current = current_agent || '';
  };

  return {
    isConnected,
    agents,
    workflowComplete: workflowCompleteLocal,
    workflowResult,
  };
}
