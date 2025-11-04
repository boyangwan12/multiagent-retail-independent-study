import { http, HttpResponse } from 'msw';

const API_BASE = 'http://localhost:8000/api/v1';

export const handlers = [
  // Parameter extraction
  http.post(`${API_BASE}/parameters/extract`, () => {
    return HttpResponse.json({
      parameters: {
        forecast_horizon_weeks: 12,
        season_start_date: '2025-01-01',
        season_end_date: '2025-03-26',
        replenishment_strategy: 'weekly',
        dc_holdback_percentage: 0.15,
        markdown_checkpoint_week: 6,
        markdown_threshold: 0.40,
        extraction_confidence: 'high',
      },
      confidence: 'high',
      reasoning: 'Successfully extracted all parameters from user input.',
    });
  }),

  // Workflow creation
  http.post(`${API_BASE}/workflows/forecast`, () => {
    return HttpResponse.json({
      workflow_id: 'test_wf_123',
      status: 'pending',
      websocket_url: 'ws://localhost:8000/api/v1/workflows/test_wf_123/stream',
    }, { status: 201 });
  }),

  // Workflow status
  http.get(`${API_BASE}/workflows/:id`, ({ params }) => {
    return HttpResponse.json({
      workflow_id: params.id,
      workflow_type: 'forecast',
      status: 'completed',
      current_agent: null,
      progress_pct: 100,
      started_at: '2025-01-15T10:00:00Z',
      updated_at: '2025-01-15T10:05:00Z',
      completed_at: '2025-01-15T10:05:00Z',
      error_message: null,
    });
  }),

  // Forecast summary
  http.get(`${API_BASE}/forecasts/:id`, ({ params }) => {
    return HttpResponse.json({
      forecast_id: `f_${params.id}`,
      workflow_id: params.id as string,
      total_season_demand: 8000,
      total_demand: 8000,
      safety_stock_percentage: 0.20,
      dc_holdback_percentage: 0.15,
      manufacturing_order: 11040,
      mape_percentage: 12.5,
      forecasting_method: 'ensemble_prophet_arima',
    });
  }),

  // Clusters
  http.get(`${API_BASE}/stores/clusters`, () => {
    return HttpResponse.json({
      clusters: [
        {
          cluster_id: 'Cluster_A',
          cluster_name: 'Fashion Forward',
          store_count: 15,
          allocation_percentage: 0.40,
        },
        {
          cluster_id: 'Cluster_B',
          cluster_name: 'Value Conscious',
          store_count: 20,
          allocation_percentage: 0.35,
        },
        {
          cluster_id: 'Cluster_C',
          cluster_name: 'Premium',
          store_count: 15,
          allocation_percentage: 0.25,
        },
      ],
    });
  }),

  // Variance
  http.get(`${API_BASE}/variance/:workflowId/week/:week`, ({ params }) => {
    return HttpResponse.json({
      week: parseInt(params.week as string),
      forecast_units: 650,
      actual_units: 720,
      variance_percentage: 10.77,
      color: 'green',
    });
  }),

  // Allocations
  http.get(`${API_BASE}/allocations/:id`, ({ params }) => {
    return HttpResponse.json({
      allocation_id: `a_${params.id}`,
      workflow_id: params.id as string,
      total_units_allocated: 8000,
      replenishment_strategy: 'weekly',
      store_allocations: [
        {
          store_id: 'STORE001',
          store_name: 'Fifth Avenue',
          units: 320,
          cluster_id: 'Cluster_A',
        },
      ],
    });
  }),

  // Markdowns
  http.get(`${API_BASE}/markdowns/:id`, ({ params }) => {
    return HttpResponse.json({
      markdown_id: `m_${params.id}`,
      workflow_id: params.id as string,
      markdown_checkpoint_week: 6,
      markdown_threshold: 0.40,
      actual_sell_through: 0.35,
      gap: 0.05,
      elasticity_coefficient: 2.5,
      recommended_markdown_percentage: 0.125,
    });
  }),

  // CSV Upload (Demand Agent)
  http.post(`${API_BASE}/workflows/:workflowId/demand/upload`, () => {
    return HttpResponse.json({
      workflow_id: 'test_wf_123',
      file_type: 'sales_data',
      file_name: 'sales_data.csv',
      file_size_bytes: 2048,
      rows_uploaded: 50,
      columns: ['store_id', 'week', 'sales_units', 'sales_revenue', 'inventory_on_hand'],
      validation_status: 'VALID',
      uploaded_at: '2025-01-15T10:30:00Z',
      message: 'File uploaded successfully',
    });
  }),

  // CSV Upload (Inventory Agent)
  http.post(`${API_BASE}/workflows/:workflowId/inventory/upload`, () => {
    return HttpResponse.json({
      workflow_id: 'test_wf_123',
      file_type: 'dc_inventory',
      file_name: 'dc_inventory.csv',
      file_size_bytes: 1536,
      rows_uploaded: 30,
      columns: ['sku', 'dc_location', 'available_units', 'reserved_units'],
      validation_status: 'VALID',
      uploaded_at: '2025-01-15T10:30:00Z',
      message: 'File uploaded successfully',
    });
  }),

  // CSV Upload (Pricing Agent)
  http.post(`${API_BASE}/workflows/:workflowId/pricing/upload`, () => {
    return HttpResponse.json({
      workflow_id: 'test_wf_123',
      file_type: 'markdown_history',
      file_name: 'markdown_history.csv',
      file_size_bytes: 1024,
      rows_uploaded: 20,
      columns: ['week', 'markdown_pct', 'sell_through_pct', 'demand_lift_pct'],
      validation_status: 'VALID',
      uploaded_at: '2025-01-15T10:30:00Z',
      message: 'File uploaded successfully',
    });
  }),
];
