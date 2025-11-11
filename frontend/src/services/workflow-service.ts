import { apiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type { SeasonParameters } from '@/types/parameters';

interface CreateForecastWorkflowRequest {
  parameters: SeasonParameters;
  category_id: string;
}

interface CreateForecastWorkflowResponse {
  workflow_id: string;
  status: string;
}

interface WorkflowStatusResponse {
  workflow_id: string;
  workflow_type: string;
  status: string;
  current_agent: string | null;
  progress_pct: number;
  started_at: string | null;
  updated_at: string;
  completed_at: string | null;
  error_message: string | null;
  workflow_status?: string; // Alias for status field
}

interface WorkflowResultsResponse {
  workflow_id: string;
  status: string;
  output_data: {
    demand?: {
      forecast_id: string;
      total_forecast: number;
    };
    inventory?: {
      allocation_id: string;
    };
    pricing?: {
      markdown_id: string;
    };
  };
  started_at: string | null;
  completed_at: string | null;
}

export class WorkflowService {
  static async createForecastWorkflow(
    request: CreateForecastWorkflowRequest
  ): Promise<CreateForecastWorkflowResponse> {
    const response = await apiClient.post<CreateForecastWorkflowResponse>(
      API_ENDPOINTS.WORKFLOWS_FORECAST,
      request
    );
    return response.data;
  }

  static async executeWorkflow(workflowId: string): Promise<WorkflowStatusResponse> {
    const response = await apiClient.post<WorkflowStatusResponse>(
      API_ENDPOINTS.workflows.execute(workflowId),
      {}
    );
    return response.data;
  }

  static async getWorkflowStatus(workflowId: string): Promise<WorkflowStatusResponse> {
    const response = await apiClient.get<WorkflowStatusResponse>(
      API_ENDPOINTS.workflows.getById(workflowId)
    );
    return response.data;
  }

  static async getWorkflowResults(workflowId: string): Promise<WorkflowResultsResponse> {
    const response = await apiClient.get<WorkflowResultsResponse>(
      API_ENDPOINTS.workflows.getResults(workflowId)
    );
    return response.data;
  }
}
