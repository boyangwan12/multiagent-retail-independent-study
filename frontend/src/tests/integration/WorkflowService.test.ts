import { describe, it, expect } from 'vitest';

describe('WorkflowService Integration', () => {
  it('should create forecast workflow', async () => {
    const requestData = {
      category_id: 'womens_dresses',
      parameters: {
        forecast_horizon_weeks: 12,
        season_start_date: '2025-01-01',
        season_end_date: '2025-03-26',
        replenishment_strategy: 'weekly',
        dc_holdback_percentage: 0.15,
        markdown_checkpoint_week: 6,
        markdown_threshold: 0.40,
        extraction_confidence: 'high',
      },
    };

    const response = await fetch('http://localhost:8001/api/v1/workflows/forecast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData),
    });

    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data.workflow_id).toBe('test_wf_123');
    expect(data.status).toBe('pending');
  });

  it('should get workflow status', async () => {
    const workflowId = 'test_wf_123';

    const response = await fetch(`http://localhost:8001/api/v1/workflows/${workflowId}`);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.workflow_id).toBe(workflowId);
    expect(data.workflow_type).toBe('forecast');
    expect(data.status).toBe('completed');
  });
});
