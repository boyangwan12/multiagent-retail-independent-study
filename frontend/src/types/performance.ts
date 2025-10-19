export interface MetricItem {
  label: string;
  value: string;
  target: string;
  status: 'success' | 'warning' | 'error';
}

export interface MetricCardData {
  title: string;
  metrics: MetricItem[];
}

export interface QuarterlyData {
  quarter: string;
  mape: number;
  bias: number;
}

export interface AgentContribution {
  name: string;
  percentage: number;
  color: string;
  trend: number[]; // Sparkline data
}

export interface PerformanceMetrics {
  cards: MetricCardData[];
  historical: QuarterlyData[];
  agentContributions: AgentContribution[];
}
