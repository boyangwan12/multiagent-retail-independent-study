// Markdown analysis types

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

export interface VarianceSummary {
  workflow_id: string;
  average_variance_percentage: number;
  max_variance_percentage: number;
  min_variance_percentage: number;
  stores_above_threshold: number;
  total_stores: number;
  high_variance_stores: Array<{
    store_id: string;
    store_name: string;
    variance_percentage: number;
  }>;
  timestamp: string;
}
