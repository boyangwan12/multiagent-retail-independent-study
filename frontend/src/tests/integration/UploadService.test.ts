import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

describe('UploadService Integration', () => {
  it('should upload CSV file successfully', async () => {
    const workflowId = 'test_wf_123';
    const file = new File(['store_id,week,sales_units\nS001,1,150'], 'sales_data.csv', {
      type: 'text/csv',
    });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', 'sales_data');

    const response = await fetch(
      `http://localhost:8000/api/v1/workflows/${workflowId}/demand/upload`,
      {
        method: 'POST',
        body: formData,
      }
    );

    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.validation_status).toBe('VALID');
    expect(data.rows_uploaded).toBe(50);
    expect(data.file_name).toBe('sales_data.csv');
  });

  it('should handle validation errors', async () => {
    server.use(
      http.post('http://localhost:8000/api/v1/workflows/:workflowId/demand/upload', () => {
        return HttpResponse.json({
          workflow_id: 'test_wf_123',
          file_type: 'sales_data',
          file_name: 'sales_data.csv',
          file_size_bytes: 1024,
          rows_uploaded: 10,
          columns: ['store_id', 'week'],
          validation_status: 'INVALID',
          errors: [
            {
              error_type: 'MISSING_COLUMN',
              column: 'sales_units',
              message: "Required column 'sales_units' is missing",
            },
          ],
          uploaded_at: '2025-01-15T10:30:00Z',
          message: 'Validation failed: 1 errors found',
        });
      })
    );

    const file = new File(['store_id,week\nS001,1'], 'sales_data.csv', {
      type: 'text/csv',
    });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', 'sales_data');

    const response = await fetch(
      'http://localhost:8000/api/v1/workflows/test_wf_123/demand/upload',
      {
        method: 'POST',
        body: formData,
      }
    );

    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.validation_status).toBe('INVALID');
    expect(data.errors.length).toBeGreaterThan(0);
    expect(data.errors[0].error_type).toBe('MISSING_COLUMN');
  });
});
