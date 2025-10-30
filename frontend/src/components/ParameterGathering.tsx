import { useState } from 'react';
import { ParameterTextarea } from './ParameterTextarea';
import { ParameterConfirmationModal } from './ParameterConfirmationModal';
import { ConfirmedBanner } from './ConfirmedBanner';
import { AgentReasoningPreview } from './AgentReasoningPreview';
import { extractParameters } from '@/utils/extractParameters';
import { useParameters } from '@/contexts/ParametersContext';
import { mockDelay } from '@/lib/mock-api';
import { AlertCircle } from 'lucide-react';
import type { SeasonParameters } from '@/types';

/**
 * ParameterGathering Component
 *
 * Section 0 of the Multi-Agent Retail Forecasting Dashboard.
 * Allows users to input season parameters in natural language and extracts
 * structured parameters using mock LLM extraction (regex-based).
 *
 * @component
 *
 * @features
 * - Natural language input with 500 character limit
 * - Mock LLM extraction (2-5s delay simulating API call)
 * - Parameter confirmation modal with reasoning disclosure
 * - Edit/confirm workflow
 * - Collapsed banner after confirmation
 * - Integration with ParametersContext for global state
 *
 * @example
 * ```tsx
 * <ParameterGathering />
 * ```
 *
 * @see {@link ParameterTextarea} for input component
 * @see {@link ParameterConfirmationModal} for confirmation UI
 * @see {@link extractParameters} for extraction logic
 */
export function ParameterGathering() {
  const { parameters, setParameters, clearParameters } = useParameters();
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [extractedParams, setExtractedParams] =
    useState<SeasonParameters | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExtract = async (input: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Simulate API delay (2-5 seconds)
      await mockDelay(2000, 5000);

      const result = extractParameters(input);

      if (result.success && result.parameters) {
        setExtractedParams(result.parameters);
        setShowModal(true);
      } else {
        setError(
          `Could not extract all required parameters. Missing: ${result.missingFields.join(', ')}. Please provide more information.`
        );
      }
    } catch (err) {
      setError(
        'An error occurred during parameter extraction. Please try again.'
      );
      console.error('Extraction error:', err);
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
              <div className="flex items-start gap-3 p-4 bg-error/10 border border-error/20 rounded-lg">
                <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-error">Extraction Error</p>
                  <p className="text-sm text-text-secondary mt-1">{error}</p>
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
