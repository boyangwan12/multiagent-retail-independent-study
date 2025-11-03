import { ApiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type { SeasonParameters } from '@/types/parameters';

interface CreateForecastWorkflowRequest {
  parameters: SeasonParameters;
  category_id: string;
}

interface CreateForecastWorkflowResponse {
  workflow_id: string;
  status: string;
  websocket_url: string;
}

export class WorkflowService {
  static async createForecastWorkflow(
    request: CreateForecastWorkflowRequest
  ): Promise<CreateForecastWorkflowResponse> {
    return ApiClient.post<CreateForecastWorkflowResponse>(
      API_ENDPOINTS.WORKFLOWS_FORECAST,
      request
    );
  }
}
