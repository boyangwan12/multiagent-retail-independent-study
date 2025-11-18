import { describe, it, expect, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

describe('ParameterService Integration', () => {
  it('should extract parameters from user input', async () => {
    const userInput = 'I need 8000 units over 12 weeks starting Jan 1, 2025.';

    const response = await fetch('http://localhost:8000/api/v1/parameters/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: userInput }),
    });

    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.parameters.forecast_horizon_weeks).toBe(12);
    expect(data.parameters.season_start_date).toBe('2025-01-01');
    expect(data.confidence).toBe('high');
  });

  it('should handle extraction errors', async () => {
    // Override MSW handler for error case
    server.use(
      http.post('http://localhost:8000/api/v1/parameters/extract', () => {
        return HttpResponse.json(
          { detail: 'Invalid input' },
          { status: 422 }
        );
      })
    );

    const response = await fetch('http://localhost:8000/api/v1/parameters/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: '' }),
    });

    expect(response.status).toBe(422);
    const data = await response.json();
    expect(data.detail).toBe('Invalid input');
  });
});
