export type MarkdownConfidence = 'High' | 'Medium' | 'Low';

export interface MarkdownDecision {
  id: string;
  product_category: string;
  recommended_markdown: number; // percentage (0-50)
  confidence: MarkdownConfidence;
  current_stock: number;
  forecast_demand: number;
  excess_stock: number;
  estimated_revenue_loss: number;
  estimated_excess_reduction: number;
  applied: boolean;
  rejected: boolean;
  override_markdown?: number;
}
