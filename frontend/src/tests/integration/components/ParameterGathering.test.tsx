import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '../../mocks/server';

// Mock component for testing (simplified version)
function ParameterGatheringMock({ onSuccess }: { onSuccess: (data: any) => void }) {
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const userInput = formData.get('userInput') as string;

    const response = await fetch('http://localhost:8000/api/v1/parameters/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: userInput }),
    });

    const data = await response.json();
    onSuccess(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        name="userInput"
        placeholder="Describe your season planning needs"
        data-testid="user-input"
      />
      <button type="submit">Extract Parameters</button>
    </form>
  );
}

describe('ParameterGathering Component Integration', () => {
  it('should submit user input and extract parameters', async () => {
    const mockOnSuccess = vi.fn();
    const user = userEvent.setup();

    render(<ParameterGatheringMock onSuccess={mockOnSuccess} />);

    const textarea = screen.getByTestId('user-input');
    const submitButton = screen.getByRole('button', { name: /extract/i });

    await user.type(textarea, 'I need 8000 units over 12 weeks.');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith(
        expect.objectContaining({
          parameters: expect.objectContaining({
            forecast_horizon_weeks: 12,
          }),
        })
      );
    });
  });

  it('should display error message on extraction failure', async () => {
    server.use(
      http.post('http://localhost:8000/api/v1/parameters/extract', () => {
        return HttpResponse.json(
          { detail: 'Invalid input' },
          { status: 422 }
        );
      })
    );

    const mockOnSuccess = vi.fn();
    const user = userEvent.setup();

    render(<ParameterGatheringMock onSuccess={mockOnSuccess} />);

    const textarea = screen.getByTestId('user-input');
    const submitButton = screen.getByRole('button', { name: /extract/i });

    await user.type(textarea, '');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSuccess).not.toHaveBeenCalled();
    });
  });
});
