import { ApiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface MarkdownAnalysis {
  workflow_id: string;
  markdown_checkpoint_week: number | null;
  markdown_threshold: number | null;
  actual_sell_through: number;
  gap: number;
  elasticity_coefficient: number;
  expected_impact: number;
  recommended_markdown_percentage: number;
  expected_sell_through_after_markdown: number;
  expected_margin_reduction: number;
  decision: 'APPLY_MARKDOWN' | 'NO_MARKDOWN_NEEDED' | 'NOT_APPLICABLE';
  justification: string;
  risk_assessment: string;
  timestamp: string;
}

// ============================================================================
// MARKDOWN SERVICE
// ============================================================================

export class MarkdownService {
  /**
   * Fetch markdown analysis for a specific workflow
   * @param workflowId - The workflow ID to fetch markdown analysis for
   * @returns Promise<MarkdownAnalysis | null> - null if markdown not applicable
   */
  static async getMarkdownAnalysis(workflowId: string): Promise<MarkdownAnalysis | null> {
    try {
      const response = await ApiClient.get<MarkdownAnalysis>(
        API_ENDPOINTS.markdowns.getById(workflowId)
      );

      // If decision is NOT_APPLICABLE, return null to hide Section 6
      if (response.decision === 'NOT_APPLICABLE') {
        return null;
      }

      return response;
    } catch (error: any) {
      // 404 means markdown checkpoint week was not set - this is normal
      if (error.status === 404) {
        console.log('Markdown analysis not applicable for this workflow');
        return null;
      }

      // Other errors should be thrown
      throw error;
    }
  }

  /**
   * Format markdown percentage for display
   * @param percentage - Decimal markdown percentage (e.g., 0.20)
   * @returns Formatted string (e.g., "20%")
   */
  static formatMarkdownPercentage(percentage: number): string {
    return `${(percentage * 100).toFixed(0)}%`;
  }

  /**
   * Format sell-through percentage for display
   * @param sellThrough - Decimal sell-through (e.g., 0.35)
   * @returns Formatted string (e.g., "35%")
   */
  static formatSellThrough(sellThrough: number): string {
    return `${(sellThrough * 100).toFixed(1)}%`;
  }

  /**
   * Format currency for display
   * @param amount - Dollar amount (e.g., 15000)
   * @returns Formatted string (e.g., "$15,000")
   */
  static formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  /**
   * Get badge color for markdown decision
   * @param decision - Markdown decision type
   * @returns Tailwind color classes
   */
  static getDecisionBadgeColor(
    decision: 'APPLY_MARKDOWN' | 'NO_MARKDOWN_NEEDED' | 'NOT_APPLICABLE'
  ): string {
    switch (decision) {
      case 'APPLY_MARKDOWN':
        return 'bg-orange-100 text-orange-800 border border-orange-300';
      case 'NO_MARKDOWN_NEEDED':
        return 'bg-green-100 text-green-800 border border-green-300';
      case 'NOT_APPLICABLE':
        return 'bg-gray-100 text-gray-600 border border-gray-300';
      default:
        return 'bg-gray-100 text-gray-600 border border-gray-300';
    }
  }

  /**
   * Get human-readable decision label
   * @param decision - Markdown decision type
   * @returns Display label
   */
  static getDecisionLabel(
    decision: 'APPLY_MARKDOWN' | 'NO_MARKDOWN_NEEDED' | 'NOT_APPLICABLE'
  ): string {
    switch (decision) {
      case 'APPLY_MARKDOWN':
        return 'Markdown Recommended';
      case 'NO_MARKDOWN_NEEDED':
        return 'No Markdown Needed';
      case 'NOT_APPLICABLE':
        return 'Not Applicable';
      default:
        return 'Unknown';
    }
  }
}
