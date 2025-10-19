import { useEffect, useState } from 'react';
import { MockWebSocket } from '@/lib/mock-websocket';
import type { AgentState } from '@/types/agent';

export function useAgentStatus() {
  const [agentState, setAgentState] = useState<AgentState | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new MockWebSocket();

    const unsubscribe = ws.onMessage((data) => {
      setAgentState(data);
    });

    ws.connect();
    setIsConnected(true);

    return () => {
      unsubscribe();
      ws.disconnect();
      setIsConnected(false);
    };
  }, []);

  return { agentState, isConnected };
}
