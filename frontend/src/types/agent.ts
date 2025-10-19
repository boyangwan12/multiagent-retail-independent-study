export type AgentStatus = 'idle' | 'thinking' | 'complete' | 'error';

export interface AgentState {
  agent_name: 'Demand Agent' | 'Inventory Agent' | 'Pricing Agent';
  status: AgentStatus;
  progress_pct: number;
  message: string;
  timestamp: string;
}
