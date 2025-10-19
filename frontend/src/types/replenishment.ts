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
