import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

describe('ForecastService Integration', () => {
  it('should fetch forecast summary', async () => {
    const workflowId = 'test_wf_123';

    const response = await fetch(`http://localhost:8000/api/v1/forecasts/${workflowId}`);
    const forecast = await response.json();

    expect(response.status).toBe(200);
    expect(forecast.total_demand).toBe(8000);
    expect(forecast.manufacturing_order).toBe(11040);
    expect(forecast.mape_percentage).toBe(12.5);
  });

  it('should handle 404 errors', async () => {
    server.use(
      http.get('http://localhost:8000/api/v1/forecasts/:id', () => {
        return HttpResponse.json(
          { detail: 'Workflow not found' },
          { status: 404 }
        );
      })
    );

    const response = await fetch('http://localhost:8000/api/v1/forecasts/invalid_id');

    expect(response.status).toBe(404);
    const data = await response.json();
    expect(data.detail).toBe('Workflow not found');
  });
});
