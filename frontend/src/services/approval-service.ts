import { ApiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';

/**
 * Approval Service
 * Handles replenishment approvals and rejections
 */

export interface ApprovalRequest {
  forecast_id: string;
  week_number: number;
}

export interface ApprovalResponse {
  approval_id: string;
  forecast_id: string;
  week_number: number;
  total_units_approved: number;
  stores_affected: number;
  approved_at: string;
  status: 'approved';
}

export class ApprovalService {
  /**
   * Approve replenishment shipments for a specific week
   * @param request - Approval request with forecast_id and week_number
   * @returns Promise<ApprovalResponse>
   */
  static async approveReplenishment(
    request: ApprovalRequest
  ): Promise<ApprovalResponse> {
    return ApiClient.post<ApprovalResponse>(
      API_ENDPOINTS.approvals.replenishment(),
      request
    );
  }
}
