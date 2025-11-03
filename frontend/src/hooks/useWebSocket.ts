import { useEffect, useRef, useState } from 'react';
import { WebSocketService } from '@/services/websocket-service';
import { useParameters } from '@/contexts/ParametersContext';
import type { WebSocketMessageType, AgentState } from '@/types/websocket';

export function useWebSocket(workflowId: string | null) {
  const wsRef = useRef<WebSocketService | null>(null);
  const { setWorkflowComplete, setForecastId, setAllocationId, setMarkdownId } = useParameters();
  const [isConnected, setIsConnected] = useState(false);
  const [agents, setAgents] = useState<AgentState[]>([
    { name: 'Demand Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
    { name: 'Inventory Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
    { name: 'Pricing Agent', status: 'idle', progress: 0, messages: [], duration: null, result: null },
  ]);
  const [workflowCompleteLocal, setWorkflowCompleteLocal] = useState(false);
  const [workflowResult, setWorkflowResult] = useState<any>(null);

  useEffect(() => {
    // Validate workflowId
    if (!workflowId) {
      console.warn('useWebSocket: No workflow ID provided');
      return;
    }

    if (!workflowId.startsWith('wf_')) {
      console.error('useWebSocket: Invalid workflow ID format:', workflowId);
      return;
    }

    // Create WebSocket service
    const ws = new WebSocketService();
    wsRef.current = ws;

    // Handle incoming messages
    ws.onMessage((message: WebSocketMessageType) => {
      handleMessage(message);
    });

    // Connect to WebSocket
    ws.connect(workflowId);
    setIsConnected(true);

    // Cleanup on unmount
    return () => {
      ws.disconnect();
      setIsConnected(false);
    };
  }, [workflowId]);

  const handleMessage = (message: WebSocketMessageType) => {
    switch (message.type) {
      case 'agent_started':
        setAgents(prev =>
          prev.map(agent =>
            agent.name === message.agent
              ? { ...agent, status: 'running', progress: 0, messages: ['Started'] }
              : agent
          )
        );
        break;

      case 'agent_progress':
        setAgents(prev =>
          prev.map(agent =>
            agent.name === message.agent
              ? {
                  ...agent,
                  status: 'running',
                  progress: message.progress_pct,
                  messages: [...agent.messages, message.message],
                }
              : agent
          )
        );
        break;

      case 'agent_completed':
        setAgents(prev =>
          prev.map(agent =>
            agent.name === message.agent
              ? {
                  ...agent,
                  status: 'complete',
                  progress: 100,
                  duration: message.duration_seconds,
                  result: message.result,
                  messages: [...agent.messages, 'Completed'],
                }
              : agent
          )
        );
        break;

      case 'workflow_complete':
        setWorkflowCompleteLocal(true);
        setWorkflowResult(message.result);

        // Update context with result IDs
        setWorkflowComplete(true);
        if (message.result?.forecast_id) {
          setForecastId(message.result.forecast_id);
        }
        if (message.result?.allocation_id) {
          setAllocationId(message.result.allocation_id);
        }
        if (message.result?.markdown_id) {
          setMarkdownId(message.result.markdown_id);
        }
        break;

      case 'error':
        setAgents(prev =>
          prev.map(agent =>
            agent.name === message.agent
              ? {
                  ...agent,
                  status: 'error',
                  messages: [...agent.messages, `Error: ${message.error_message}`],
                }
              : agent
          )
        );
        break;

      case 'human_input_required':
        // TODO: Future story - Display approval modal for manufacturing orders and markdown decisions
        // For now, update agent state with pending approval message
        setAgents(prev =>
          prev.map(agent =>
            agent.name === message.agent
              ? {
                  ...agent,
                  messages: [
                    ...agent.messages,
                    `⏸️ Waiting for human approval: ${message.action}`,
                  ],
                }
              : agent
          )
        );
        console.log('Human input required:', message);
        break;
    }
  };

  return {
    isConnected,
    agents,
    workflowComplete: workflowCompleteLocal,
    workflowResult,
  };
}
