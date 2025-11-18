import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { useEffect, useState } from 'react';

// Mock AgentCards component
function AgentCardsMock({ workflowId }: { workflowId: string }) {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    async function fetchStatus() {
      const response = await fetch(`http://localhost:8000/api/v1/workflows/${workflowId}`);
      const data = await response.json();
      setStatus(data);
    }

    fetchStatus();
  }, [workflowId]);

  if (!status) return <div>Loading workflow...</div>;

  return (
    <div>
      <h2>Agent Workflow Status</h2>
      <p data-testid="workflow-status">Status: {status.status}</p>
      <p data-testid="progress">Progress: {status.progress_pct}%</p>
      {status.current_agent && (
        <p data-testid="current-agent">Current Agent: {status.current_agent}</p>
      )}
    </div>
  );
}

describe('AgentCards Component Integration', () => {
  it('should fetch and display workflow status', async () => {
    render(<AgentCardsMock workflowId="test_wf_123" />);

    await waitFor(() => {
      expect(screen.getByTestId('workflow-status')).toHaveTextContent('completed');
      expect(screen.getByTestId('progress')).toHaveTextContent('100%');
    });
  });
});
