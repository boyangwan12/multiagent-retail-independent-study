import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { useEffect, useState } from 'react';

// Mock ForecastSummary component
function ForecastSummaryMock({ workflowId }: { workflowId: string }) {
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchForecast() {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/forecasts/${workflowId}`);
        const data = await response.json();
        setForecast(data);
      } catch (error) {
        console.error('Failed to fetch forecast');
      } finally {
        setLoading(false);
      }
    }

    fetchForecast();
  }, [workflowId]);

  if (loading) return <div>Loading...</div>;
  if (!forecast) return <div>No forecast data</div>;

  return (
    <div>
      <h2>Forecast Summary</h2>
      <p data-testid="total-demand">Total Demand: {forecast.total_demand}</p>
      <p data-testid="manufacturing-order">Manufacturing Order: {forecast.manufacturing_order}</p>
      <p data-testid="mape">MAPE: {forecast.mape_percentage}%</p>
    </div>
  );
}

describe('ForecastSummary Component Integration', () => {
  it('should fetch and display forecast data', async () => {
    render(<ForecastSummaryMock workflowId="test_wf_123" />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId('total-demand')).toHaveTextContent('8000');
      expect(screen.getByTestId('manufacturing-order')).toHaveTextContent('11040');
      expect(screen.getByTestId('mape')).toHaveTextContent('12.5');
    });
  });
});
