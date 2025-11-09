import { apiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type { AllocationPlan } from '@/types/allocation';

export class AllocationService {
  /**
   * Get allocation plan for a workflow
   * @param forecastId - The forecast ID
   * @returns Promise<AllocationPlan>
   */
  static async getAllocation(forecastId: string): Promise<AllocationPlan> {
    return apiClient.get<AllocationPlan>(
      API_ENDPOINTS.allocations.getById(forecastId)
    );
  }

  /**
   * Approve replenishment for a specific week
   * @param workflowId - The workflow ID
   * @param weekNumber - The week number to approve
   * @returns Promise with approval response
   */
  static async approveReplenishment(
    workflowId: string,
    weekNumber: number
  ) {
    return apiClient.post(
      API_ENDPOINTS.allocations.approve(workflowId),
      {
        week_number: weekNumber,
      }
    );
  }

  /**
   * Reject replenishment for a specific week
   * @param workflowId - The workflow ID
   * @param weekNumber - The week number to reject
   * @returns Promise with rejection response
   */
  static async rejectReplenishment(
    workflowId: string,
    weekNumber: number
  ) {
    return apiClient.post(
      API_ENDPOINTS.allocations.reject(workflowId),
      {
        week_number: weekNumber,
      }
    );
  }
}
