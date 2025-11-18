import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock UploadZone component for testing
function UploadZoneMock({
  workflowId,
  agentType,
  fileType,
  onUploadSuccess,
  onUploadError,
}: {
  workflowId: string;
  agentType: string;
  fileType: string;
  onUploadSuccess: (fileName: string, rows: number) => void;
  onUploadError: (error: string) => void;
}) {
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/workflows/${workflowId}/${agentType}/upload`,
        {
          method: 'POST',
          body: formData,
        }
      );

      const data = await response.json();

      if (data.validation_status === 'VALID') {
        onUploadSuccess(data.file_name, data.rows_uploaded);
      } else {
        onUploadError('Validation failed');
      }
    } catch (error) {
      onUploadError('Upload failed');
    }
  };

  return (
    <div>
      <label htmlFor="file-input">Browse files</label>
      <input
        id="file-input"
        type="file"
        accept=".csv"
        onChange={handleFileChange}
      />
    </div>
  );
}

describe('UploadZone Component Integration', () => {
  it('should upload CSV file successfully', async () => {
    const mockOnSuccess = vi.fn();
    const mockOnError = vi.fn();
    const user = userEvent.setup();

    render(
      <UploadZoneMock
        workflowId="test_wf_123"
        agentType="demand"
        fileType="sales_data"
        onUploadSuccess={mockOnSuccess}
        onUploadError={mockOnError}
      />
    );

    const file = new File(['store_id,week,sales_units\nS001,1,150'], 'sales_data.csv', {
      type: 'text/csv',
    });

    const input = screen.getByLabelText(/browse files/i);
    await user.upload(input, file);

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('sales_data.csv', 50);
      expect(mockOnError).not.toHaveBeenCalled();
    });
  });
});
