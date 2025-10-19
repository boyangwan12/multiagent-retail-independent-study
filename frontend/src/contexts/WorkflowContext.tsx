import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { AgentState } from '@/types/agent';

interface WorkflowContextType {
  currentAgent: AgentState | null;
  setCurrentAgent: (agent: AgentState) => void;
  workflowStatus: 'idle' | 'running' | 'complete' | 'error';
  setWorkflowStatus: (
    status: 'idle' | 'running' | 'complete' | 'error'
  ) => void;
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(
  undefined
);

export function WorkflowProvider({ children }: { children: ReactNode }) {
  const [currentAgent, setCurrentAgent] = useState<AgentState | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<
    'idle' | 'running' | 'complete' | 'error'
  >('idle');

  return (
    <WorkflowContext.Provider
      value={{
        currentAgent,
        setCurrentAgent,
        workflowStatus,
        setWorkflowStatus,
      }}
    >
      {children}
    </WorkflowContext.Provider>
  );
}

export function useWorkflow() {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within WorkflowProvider');
  }
  return context;
}
