/**
 * Retry Utility with Exponential Backoff
 *
 * Implements automatic retry logic for failed operations with exponential backoff.
 * Useful for API calls that may fail due to temporary network issues.
 */

interface RetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  onRetry?: (attempt: number, error: Error) => void;
  shouldRetry?: (error: Error) => boolean;
}

/**
 * Retries an async function with exponential backoff
 *
 * @param fn - The async function to retry
 * @param options - Retry configuration options
 * @returns Promise that resolves with the function result or rejects after max retries
 *
 * @example
 * ```typescript
 * const data = await retryWithBackoff(
 *   () => fetch('/api/data').then(r => r.json()),
 *   {
 *     maxRetries: 3,
 *     baseDelay: 1000,
 *     onRetry: (attempt, error) => {
 *       console.log(`Retry attempt ${attempt}: ${error.message}`);
 *     }
 *   }
 * );
 * ```
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    onRetry,
    shouldRetry = () => true,
  } = options;

  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Check if we should retry this error
      if (!shouldRetry(lastError)) {
        throw lastError;
      }

      // If this was the last attempt, throw the error
      if (attempt === maxRetries) {
        throw lastError;
      }

      // Calculate delay with exponential backoff
      const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);

      // Call retry callback if provided
      if (onRetry) {
        onRetry(attempt + 1, lastError);
      }

      // Wait before retrying
      await sleep(delay);
    }
  }

  // This should never be reached, but TypeScript needs it
  throw lastError!;
}

/**
 * Sleep for a specified duration
 * @param ms - Milliseconds to sleep
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Default retry predicate for HTTP errors
 * Retries on network errors and 5xx server errors
 */
export function isRetryableError(error: Error): boolean {
  // Network errors
  if (error.message.includes('network') || error.message.includes('fetch')) {
    return true;
  }

  // Check for HTTP status codes
  if ('statusCode' in error) {
    const statusCode = (error as any).statusCode;
    // Retry on 5xx server errors and 429 (rate limit)
    return statusCode >= 500 || statusCode === 429;
  }

  return false;
}

/**
 * Retry wrapper specifically for API calls
 *
 * @example
 * ```typescript
 * const result = await retryApiCall(
 *   () => apiClient.get('/forecast/123'),
 *   { maxRetries: 3 }
 * );
 * ```
 */
export async function retryApiCall<T>(
  apiCall: () => Promise<T>,
  options: Omit<RetryOptions, 'shouldRetry'> & { shouldRetry?: (error: Error) => boolean } = {}
): Promise<T> {
  return retryWithBackoff(apiCall, {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 8000,
    shouldRetry: isRetryableError,
    ...options,
  });
}
