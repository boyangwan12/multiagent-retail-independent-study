/**
 * Consolidated Type Definitions
 * All types in one place for better maintainability
 */

// ============================================================================
// WORKFLOW & AGENT TYPES
// ============================================================================

export type AgentStatus = 'idle' | 'thinking' | 'complete' | 'error';

export interface AgentState {
  agent_name: 'Demand Agent' | 'Inventory Agent' | 'Pricing Agent';
  status: AgentStatus;
  progress_pct: number;
  message: string;
  timestamp: string;
}

export type ReplenishmentStrategy = 'none' | 'weekly' | 'bi-weekly';

export interface SeasonParameters {
  forecast_horizon_weeks: number;
  season_start_date: string;
  season_end_date: string;
  replenishment_strategy: ReplenishmentStrategy;
  dc_holdback_percentage: number;
  markdown_checkpoint_week?: number;
  markdown_threshold?: number;
  extraction_confidence: 'high' | 'medium' | 'low';
  extraction_reasoning: string;
}

// ============================================================================
// FORECAST & BUSINESS DOMAIN TYPES
// ============================================================================

export interface WeeklyDemand {
  week_number: number;
  demand_units: number;
  forecasted_units?: number;
  actual_units?: number | null;
  variance_pct?: number | null;
}

export interface ForecastResult {
  forecast_id: string;
  category_id: string;
  season: string;
  total_season_demand: number;
  weekly_demand_curve: WeeklyDemand[];
  peak_week: number;
  forecasting_method: 'ensemble_prophet_arima';
  prophet_forecast: number;
  arima_forecast: number;
  cluster_distribution: StoreCluster[];
}

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

export type ReplenishmentUrgency = 'High' | 'Medium' | 'Low';
export type ReplenishmentStatus = 'Pending' | 'In Progress' | 'Approved' | 'Rejected';

export interface ReplenishmentItem {
  id: string;
  store_id: string;
  store_name: string;
  sku: string;
  product_name: string;
  quantity: number;
  urgency: ReplenishmentUrgency;
  status: ReplenishmentStatus;
  recommended_date: string;
  current_stock: number;
  forecast_demand: number;
}

// ============================================================================
// STORE & DATA TYPES
// ============================================================================

export interface Store {
  store_id: string;
  size_sqft: number;
  income_level: number;
  foot_traffic: number;
  competitor_density: number;
  online_penetration: number;
  population_density: number;
  mall_location: boolean;
}

export interface StoreCluster {
  cluster_id: string;
  cluster_name: string;
  fashion_tier: 'PREMIUM' | 'MAINSTREAM' | 'VALUE';
  store_count: number;
  total_units: number;
  allocation_percentage: number;
}

export interface StoreForecast {
  store_id: string;
  store_name: string;
  forecast_units: number;
  confidence: number; // 0-100
  status: 'Active' | 'Warning' | 'Low Stock';
  location: string;
  size_tier: 'Large' | 'Medium' | 'Small';
  // Original store attributes for expandable details
  size_sqft: number;
  income_level: number;
  foot_traffic: number;
  mall_location: boolean;
}

export interface ClusterWithStores extends StoreCluster {
  stores: StoreForecast[];
}

export interface HistoricalSale {
  date: string;
  store_id: string;
  category: string;
  quantity_sold: number;
  revenue: number;
}

// ============================================================================
// PERFORMANCE & METRICS TYPES
// ============================================================================

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

// ============================================================================
// UI & NAVIGATION TYPES
// ============================================================================

export interface NavigationSection {
  id: string;
  label: string;
  icon?: string;
  href: string;
}

export const DASHBOARD_SECTIONS: NavigationSection[] = [
  {
    id: 'parameters',
    label: 'Parameters',
    icon: '⚙️',
    href: '#parameters',
  },
  {
    id: 'agents',
    label: 'Agent Workflow',
    icon: '🤖',
    href: '#agents',
  },
  {
    id: 'forecast',
    label: 'Forecast Summary',
    icon: '📊',
    href: '#forecast',
  },
  {
    id: 'clusters',
    label: 'Cluster Distribution',
    icon: '🏪',
    href: '#clusters',
  },
  {
    id: 'weekly',
    label: 'Weekly Performance',
    icon: '📈',
    href: '#weekly',
  },
  {
    id: 'replenishment',
    label: 'Replenishment Queue',
    icon: '📦',
    href: '#replenishment',
  },
  {
    id: 'markdown',
    label: 'Markdown Decision',
    icon: '💰',
    href: '#markdown',
  },
  {
    id: 'performance',
    label: 'Performance Metrics',
    icon: '🎯',
    href: '#performance',
  },
];
