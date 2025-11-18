import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { SeasonParameters } from '@/types';

interface ParametersContextType {
  // Parameters state
  parameters: SeasonParameters | null;
  setParameters: (params: SeasonParameters) => void;
  clearParameters: () => void;

  // Workflow state
  workflowId: string | null;
  setWorkflowId: (id: string) => void;
  workflowComplete: boolean;
  setWorkflowComplete: (complete: boolean) => void;

  // Result IDs from workflow
  forecastId: string | null;
  setForecastId: (id: string | null) => void;
  allocationId: string | null;
  setAllocationId: (id: string | null) => void;
  markdownId: string | null;
  setMarkdownId: (id: string | null) => void;

  // UI state
  isConfirmed: boolean;
  setIsConfirmed: (confirmed: boolean) => void;
  isEditing: boolean;
  setIsEditing: (editing: boolean) => void;

  // Selected category
  categoryId: string | null;
  setCategoryId: (id: string) => void;
}

const ParametersContext = createContext<ParametersContextType | undefined>(
  undefined
);

export function ParametersProvider({ children }: { children: ReactNode }) {
  // Parameters state
  const [parameters, setParameters] = useState<SeasonParameters | null>(null);

  // Workflow state
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [workflowComplete, setWorkflowComplete] = useState<boolean>(false);

  // Result IDs from workflow
  const [forecastId, setForecastId] = useState<string | null>(null);
  const [allocationId, setAllocationId] = useState<string | null>(null);
  const [markdownId, setMarkdownId] = useState<string | null>(null);

  // UI state
  const [isConfirmed, setIsConfirmed] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);

  // Selected category
  const [categoryId, setCategoryId] = useState<string | null>(null);

  const clearParameters = () => {
    setParameters(null);
    setWorkflowId(null);
    setWorkflowComplete(false);
    setForecastId(null);
    setAllocationId(null);
    setMarkdownId(null);
    setIsConfirmed(false);
    setIsEditing(false);
    setCategoryId(null);
  };

  return (
    <ParametersContext.Provider
      value={{
        // Parameters
        parameters,
        setParameters,
        clearParameters,

        // Workflow
        workflowId,
        setWorkflowId,
        workflowComplete,
        setWorkflowComplete,

        // Result IDs
        forecastId,
        setForecastId,
        allocationId,
        setAllocationId,
        markdownId,
        setMarkdownId,

        // UI state
        isConfirmed,
        setIsConfirmed,
        isEditing,
        setIsEditing,

        // Category
        categoryId,
        setCategoryId,
      }}
    >
      {children}
    </ParametersContext.Provider>
  );
}

export function useParameters() {
  const context = useContext(ParametersContext);
  if (!context) {
    throw new Error('useParameters must be used within ParametersProvider');
  }
  return context;
}
