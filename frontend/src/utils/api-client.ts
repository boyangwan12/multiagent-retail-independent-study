/**
 * API Client Utility
 *
 * Centralized HTTP client for making API requests with error handling,
 * request/response interceptors, and TypeScript support.
 */

import { API_TIMEOUT, HTTP_STATUS, API_ERROR_TYPES } from '@/config/api';

// Re-export for convenience
export { API_ERROR_TYPES };

/**
 * Custom API Error class
 */
export class APIError extends Error {
  statusCode?: number;
  errorType?: string;
  details?: any;

  constructor(
    message: string,
    statusCode?: number,
    errorType?: string,
    details?: any
  ) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.errorType = errorType;
    this.details = details;
  }
}

/**
 * API Request Options
 */
export interface APIRequestOptions extends RequestInit {
  timeout?: number;
  params?: Record<string, string | number | boolean>;
}

/**
 * API Response wrapper
 */
export interface APIResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Headers;
}

/**
 * Make an HTTP request with error handling
 */
async function request<T = any>(
  url: string,
  options: APIRequestOptions = {}
): Promise<APIResponse<T>> {
  const {
    timeout = API_TIMEOUT,
    params,
    headers = {},
    ...fetchOptions
  } = options;

  // Build URL with query parameters
  let fullUrl = url;
  if (params) {
    const queryString = new URLSearchParams(
      Object.entries(params).reduce((acc, [key, value]) => {
        acc[key] = String(value);
        return acc;
      }, {} as Record<string, string>)
    ).toString();
    fullUrl = `${url}${queryString ? `?${queryString}` : ''}`;
  }

  // Set default headers
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers as Record<string, string>,
  };

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(fullUrl, {
      ...fetchOptions,
      headers: defaultHeaders,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Parse response body
    let data: T;
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = (await response.text()) as any;
    }

    // Handle error responses
    if (!response.ok) {
      throw createAPIError(response.status, data);
    }

    return {
      data,
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    };
  } catch (error: any) {
    clearTimeout(timeoutId);

    // Handle abort (timeout)
    if (error.name === 'AbortError') {
      throw new APIError(
        'Request timeout. Please try again.',
        undefined,
        API_ERROR_TYPES.NETWORK_ERROR
      );
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw new APIError(
        'Network error. Please check your connection.',
        undefined,
        API_ERROR_TYPES.NETWORK_ERROR
      );
    }

    // Re-throw API errors
    if (error instanceof APIError) {
      throw error;
    }

    // Unknown error
    throw new APIError(
      error.message || 'An unknown error occurred',
      undefined,
      API_ERROR_TYPES.UNKNOWN_ERROR
    );
  }
}

/**
 * Create a typed API error from response
 */
function createAPIError(status: number, data: any): APIError {
  const message = data?.message || data?.detail || 'An error occurred';
  const details = data?.details || data;

  switch (status) {
    case HTTP_STATUS.BAD_REQUEST:
      return new APIError(
        message,
        status,
        API_ERROR_TYPES.VALIDATION_ERROR,
        details
      );

    case HTTP_STATUS.UNAUTHORIZED:
      return new APIError(
        'Unauthorized. Please check your API credentials.',
        status,
        API_ERROR_TYPES.AUTHENTICATION_ERROR,
        details
      );

    case HTTP_STATUS.FORBIDDEN:
      return new APIError(
        'Forbidden. You do not have permission to access this resource.',
        status,
        API_ERROR_TYPES.AUTHENTICATION_ERROR,
        details
      );

    case HTTP_STATUS.NOT_FOUND:
      return new APIError(
        'Resource not found.',
        status,
        API_ERROR_TYPES.NOT_FOUND_ERROR,
        details
      );

    case HTTP_STATUS.UNPROCESSABLE_ENTITY:
      return new APIError(
        message,
        status,
        API_ERROR_TYPES.VALIDATION_ERROR,
        details
      );

    case HTTP_STATUS.TOO_MANY_REQUESTS:
      return new APIError(
        'Too many requests. Please try again later.',
        status,
        API_ERROR_TYPES.RATE_LIMIT_ERROR,
        details
      );

    case HTTP_STATUS.INTERNAL_SERVER_ERROR:
    case HTTP_STATUS.SERVICE_UNAVAILABLE:
      return new APIError(
        'Server error. Please try again later.',
        status,
        API_ERROR_TYPES.SERVER_ERROR,
        details
      );

    default:
      return new APIError(
        message,
        status,
        API_ERROR_TYPES.UNKNOWN_ERROR,
        details
      );
  }
}

/**
 * HTTP Methods
 */
export const apiClient = {
  /**
   * GET request
   */
  async get<T = any>(
    url: string,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return request<T>(url, {
      ...options,
      method: 'GET',
    });
  },

  /**
   * POST request
   */
  async post<T = any>(
    url: string,
    body?: any,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return request<T>(url, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PUT request
   */
  async put<T = any>(
    url: string,
    body?: any,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return request<T>(url, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PATCH request
   */
  async patch<T = any>(
    url: string,
    body?: any,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return request<T>(url, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * DELETE request
   */
  async delete<T = any>(
    url: string,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return request<T>(url, {
      ...options,
      method: 'DELETE',
    });
  },

  /**
   * Upload file (multipart/form-data)
   */
  async upload<T = any>(
    url: string,
    file: File,
    additionalFields?: Record<string, string>,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    if (additionalFields) {
      Object.entries(additionalFields).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    // Remove Content-Type header to let browser set it with boundary
    const { headers, ...restOptions } = options;
    const uploadHeaders = { ...(headers as Record<string, string>) };
    delete uploadHeaders['Content-Type'];

    return request<T>(url, {
      ...restOptions,
      method: 'POST',
      headers: uploadHeaders,
      body: formData,
    });
  },
};

/**
 * Helper to check if error is an API error
 */
export function isAPIError(error: any): error is APIError {
  return error instanceof APIError;
}

/**
 * Helper to get user-friendly error message
 */
export function getErrorMessage(error: any): string {
  if (isAPIError(error)) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unknown error occurred';
}

/**
 * Helper to check if error is a specific type
 */
export function isErrorType(error: any, type: string): boolean {
  return isAPIError(error) && error.errorType === type;
}
