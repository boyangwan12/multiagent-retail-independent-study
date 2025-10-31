import { useState } from 'react';
import { ParameterTextarea } from './ParameterTextarea';
import { ParameterConfirmationModal } from './ParameterConfirmationModal';
import { ConfirmedBanner } from './ConfirmedBanner';
import { AgentReasoningPreview } from './AgentReasoningPreview';
import { ParameterService } from '@/services/parameter-service';
import { useParameters } from '@/contexts/ParametersContext';
import { isAPIError, API_ERROR_TYPES } from '@/utils/api-client';
import { AlertCircle } from 'lucide-react';
import type { SeasonParameters } from '@/types';

/**
 * ParameterGathering Component
 *
 * Section 0 of the Multi-Agent Retail Forecasting Dashboard.
 * Allows users to input season parameters in natural language and extracts
 * structured parameters using backend LLM (Azure OpenAI via FastAPI).
 *
 * @component
 *
 * @features
 * - Natural language input with 500 character limit
 * - Real LLM extraction via backend API (GPT-4o-mini)
 * - Parameter confirmation modal with confidence levels and reasoning
 * - Edit/confirm workflow
 * - Collapsed banner after confirmation
 * - Integration with ParametersContext for global state
 * - Comprehensive error handling for all API failure modes
 *
 * @example
 * ```tsx
 * <ParameterGathering />
 * ```
 *
 * @see {@link ParameterTextarea} for input component
 * @see {@link ParameterConfirmationModal} for confirmation UI
 * @see {@link ParameterService} for API integration
 */
export function ParameterGathering() {
  const { parameters, setParameters, clearParameters } = useParameters();
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [extractedParams, setExtractedParams] =
    useState<SeasonParameters | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [lastInput, setLastInput] = useState<string>('');

  const handleExtract = async (input: string) => {
    setIsLoading(true);
    setError(null);
    setLastInput(input);

    try {
      // Call real backend API with LLM extraction
      const result = await ParameterService.extractParameters(input);

      // Successfully extracted parameters
      setExtractedParams(result);
      setShowModal(true);
      setRetryCount(0); // Reset retry count on success
    } catch (err) {
      // Handle different types of API errors with user-friendly messages
      if (isAPIError(err)) {
        switch (err.errorType) {
          case API_ERROR_TYPES.VALIDATION_ERROR:
            setError(
              `Invalid input: ${err.message}. Please check your input and try again.`
            );
            break;

          case API_ERROR_TYPES.AUTHENTICATION_ERROR:
            setError(
              'Authentication error. Please check your API configuration.'
            );
            break;

          case API_ERROR_TYPES.SERVER_ERROR:
            setError(
              'Server error. The backend service is temporarily unavailable. Please try again later.'
            );
            break;

          case API_ERROR_TYPES.NETWORK_ERROR:
            setError(
              'Network error. Please check your internet connection and ensure the backend server is running.'
            );
            break;

          case API_ERROR_TYPES.RATE_LIMIT_ERROR:
            setError(
              'Too many requests. Please wait a moment and try again.'
            );
            break;

          default:
            setError(err.message || 'An unexpected error occurred.');
        }
      } else {
        setError(
          'An unexpected error occurred during parameter extraction. Please try again.'
        );
      }

      console.error('Parameter extraction error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = () => {
    if (extractedParams) {
      setParameters(extractedParams);
      setShowModal(false);
    }
  };

  const handleEdit = () => {
    setShowModal(false);
    setExtractedParams(null);
  };

  const handleEditFromBanner = () => {
    clearParameters();
  };

  const handleRetry = () => {
    if (lastInput && retryCount < 3) {
      setRetryCount(retryCount + 1);
      handleExtract(lastInput);
    }
  };

  return (
    <div className="w-full space-y-8 py-8">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-text-primary">
          Section 0: Parameter Gathering
        </h2>
        <p className="text-text-secondary max-w-2xl mx-auto">
          Describe your season parameters in natural language, and our AI will
          extract the key forecasting parameters.
        </p>
      </div>

      {!parameters ? (
        <>
          <ParameterTextarea onExtract={handleExtract} isLoading={isLoading} />

          {error && (
            <div className="w-full max-w-3xl mx-auto">
              <div
                role="alert"
                aria-live="assertive"
                aria-atomic="true"
                className="flex items-start gap-3 p-4 bg-error/10 border border-error/20 rounded-lg"
              >
                <AlertCircle
                  className="w-5 h-5 text-error flex-shrink-0 mt-0.5"
                  aria-hidden="true"
                />
                <div className="flex-1">
                  <p className="font-medium text-error">Extraction Error</p>
                  <p className="text-sm text-text-secondary mt-1">{error}</p>
                  {retryCount < 3 && lastInput && (
                    <button
                      onClick={handleRetry}
                      aria-label="Retry parameter extraction"
                      className="mt-3 px-4 py-2 text-sm bg-error/20 hover:bg-error/30 text-error rounded-lg transition-colors"
                    >
                      Retry {retryCount > 0 && `(Attempt ${retryCount + 1}/3)`}
                    </button>
                  )}
                  {retryCount >= 3 && (
                    <p className="text-xs text-text-secondary mt-2">
                      Maximum retry attempts reached. Please check your input
                      or contact support.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          <AgentReasoningPreview
            parameters={
              extractedParams || {
                forecast_horizon_weeks: 12,
                season_start_date: '2025-03-01',
                season_end_date: '2025-05-24',
                replenishment_strategy: 'none',
                dc_holdback_percentage: 0,
                markdown_checkpoint_week: 6,
                markdown_threshold: 0.6,
                extraction_confidence: 'high',
                extraction_reasoning: 'Example preview',
              }
            }
          />
        </>
      ) : (
        <>
          <ConfirmedBanner
            parameters={parameters}
            onEdit={handleEditFromBanner}
          />
          <AgentReasoningPreview parameters={parameters} />
        </>
      )}

      <ParameterConfirmationModal
        open={showModal}
        onOpenChange={setShowModal}
        parameters={extractedParams}
        onConfirm={handleConfirm}
        onEdit={handleEdit}
      />
    </div>
  );
}
