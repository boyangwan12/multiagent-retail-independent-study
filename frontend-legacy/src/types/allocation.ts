// Allocation and replenishment types

export interface StoreAllocation {
  store_id: string;
  cluster_id: string;
  season_total: number;
  initial_allocation: number;
  dc_holdback: number;
  current_inventory: number;
  weeks_of_supply: number;
}

export interface ReplenishmentShipment {
  store_id: string;
  quantity: number;
  reason: string;
}

export interface WeeklyReplenishment {
  week_number: number;
  shipments: ReplenishmentShipment[];
  total_shipped: number;
  dc_remaining: number;
}

export interface DCInventoryWarning {
  week_number: number;
  dc_remaining: number;
  message: string;
  severity: 'info' | 'warning' | 'critical';
}

export interface AllocationPlan {
  allocation_id: string;
  forecast_id: string;
  manufacturing_order: number;
  safety_stock_pct: number;
  dc_holdback_pct: number;
  replenishment_strategy: 'none' | 'weekly' | 'bi-weekly';
  initial_allocation_total: number;
  dc_holdback_total: number;
  store_allocations: StoreAllocation[];
  replenishment_plan: WeeklyReplenishment[];
  dc_inventory_warnings: DCInventoryWarning[];
}
