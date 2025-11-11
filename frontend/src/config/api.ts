/**
 * API Configuration
 *
 * Centralized API endpoint definitions for the Fashion Forecast application.
 * All endpoints are relative to the API base URL defined in environment variables.
 */

// Get environment variables (Vite exposes these as import.meta.env)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

/**
 * API Base URLs
 */
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  WS_BASE_URL: WS_BASE_URL,
  API_VERSION: 'v1',
} as const;

/**
 * Full API base path (includes version)
 */
export const API_BASE = `${API_CONFIG.BASE_URL}/api/${API_CONFIG.API_VERSION}`;

/**
 * API Endpoints
 *
 * Organized by feature/resource area. Each endpoint is a function that
 * accepts parameters and returns the full URL path.
 */
export const API_ENDPOINTS = {
  // ============================================
  // Health & System
  // ============================================
  health: () => `${API_BASE}/health`,

  // ============================================
  // Section 0: Parameter Extraction
  // ============================================
  categories: {
    list: () => `${API_BASE}/categories`,
    getById: (id: string) => `${API_BASE}/categories/${id}`,
  },

  parameters: {
    extract: () => `${API_BASE}/parameters/extract`,
    validate: () => `${API_BASE}/parameters/validate`,
  },

  // ============================================
  // Workflow Management
  // ============================================
  WORKFLOWS_FORECAST: `${API_BASE}/workflows/forecast`,
  workflows: {
    create: () => `${API_BASE}/workflows`,
    getById: (id: string) => `${API_BASE}/workflows/${id}`,
    getStatus: (id: string) => `${API_BASE}/workflows/${id}/status`,
    getResults: (id: string) => `${API_BASE}/workflows/${id}/results`,
    execute: (id: string) => `${API_BASE}/workflows/${id}/execute`,
    cancel: (id: string) => `${API_BASE}/workflows/${id}/cancel`,
    // WebSocket endpoint for real-time updates
    stream: (id: string) => `${API_CONFIG.WS_BASE_URL}/api/${API_CONFIG.API_VERSION}/workflows/${id}/stream`,
  },

  // ============================================
  // Section 2: Demand Forecasting
  // ============================================
  forecasts: {
    getById: (id: string) => `${API_BASE}/forecasts/${id}`,
    getMetrics: (id: string) => `${API_BASE}/forecasts/${id}/metrics`,
    getTimeSeries: (id: string) => `${API_BASE}/forecasts/${id}/timeseries`,
  },

  // ============================================
  // Section 3: Store Clustering
  // ============================================
  stores: {
    list: () => `${API_BASE}/stores`,
    getById: (id: string) => `${API_BASE}/stores/${id}`,
    getClusters: () => `${API_BASE}/stores/clusters`,
    getClusterById: (clusterId: string) => `${API_BASE}/stores/clusters/${clusterId}`,
  },

  // ============================================
  // Section 4: Variance Analysis
  // ============================================
  variance: {
    getByWeek: (workflowId: string, week: number) =>
      `${API_BASE}/variance/${workflowId}/week/${week}`,
    getSummary: (workflowId: string) =>
      `${API_BASE}/variance/${workflowId}/summary`,
  },

  // ============================================
  // Section 5: Replenishment (Inventory Agent)
  // ============================================
  allocations: {
    getById: (workflowId: string) => `${API_BASE}/allocations/${workflowId}`,
    getByStore: (workflowId: string, storeId: string) =>
      `${API_BASE}/allocations/${workflowId}/store/${storeId}`,
    approve: (workflowId: string) => `${API_BASE}/allocations/${workflowId}/approve`,
    reject: (workflowId: string) => `${API_BASE}/allocations/${workflowId}/reject`,
  },

  // ============================================
  // Section 6: Markdown Decisions (Pricing Agent)
  // ============================================
  markdowns: {
    getById: (workflowId: string) => `${API_BASE}/markdowns/${workflowId}`,
    approve: (workflowId: string) => `${API_BASE}/markdowns/${workflowId}/approve`,
    reject: (workflowId: string) => `${API_BASE}/markdowns/${workflowId}/reject`,
  },

  // ============================================
  // Section 8: CSV Upload
  // ============================================
  uploads: {
    demandAgent: (workflowId: string) => `${API_BASE}/workflows/${workflowId}/demand/upload`,
    inventoryAgent: (workflowId: string) => `${API_BASE}/workflows/${workflowId}/inventory/upload`,
    pricingAgent: (workflowId: string) => `${API_BASE}/workflows/${workflowId}/pricing/upload`,
  },

  // ============================================
  // Human-in-the-Loop Approvals
  // ============================================
  approvals: {
    list: (workflowId: string) => `${API_BASE}/workflows/${workflowId}/approvals`,
    getById: (workflowId: string, approvalId: string) =>
      `${API_BASE}/workflows/${workflowId}/approvals/${approvalId}`,
    respond: (workflowId: string, approvalId: string) =>
      `${API_BASE}/workflows/${workflowId}/approvals/${approvalId}/respond`,
    replenishment: () => `${API_BASE}/approvals/replenishment`,
  },
} as const;

/**
 * HTTP Status Codes
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

/**
 * API Error Types
 */
export const API_ERROR_TYPES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  NOT_FOUND_ERROR: 'NOT_FOUND_ERROR',
  RATE_LIMIT_ERROR: 'RATE_LIMIT_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
} as const;

/**
 * Request Timeout (in milliseconds)
 */
export const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000');

/**
 * WebSocket Configuration
 */
export const WS_CONFIG = {
  MAX_RECONNECT_ATTEMPTS: parseInt(import.meta.env.VITE_WS_MAX_RECONNECT_ATTEMPTS || '5'),
  RECONNECT_DELAY: 2000, // 2 seconds
  HEARTBEAT_INTERVAL: 30000, // 30 seconds
} as const;

/**
 * Build WebSocket URL
 * Helper function to construct WebSocket URLs for workflow streams
 */
export const buildWsUrl = (path: string): string => {
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_CONFIG.WS_BASE_URL}/${cleanPath}`;
};
