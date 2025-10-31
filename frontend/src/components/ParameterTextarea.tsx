import { useState } from 'react';
import { Loader2 } from 'lucide-react';

interface ParameterTextareaProps {
  onExtract: (input: string) => void;
  isLoading?: boolean;
}

const MAX_CHARS = 500;

export function ParameterTextarea({
  onExtract,
  isLoading = false,
}: ParameterTextareaProps) {
  const [input, setInput] = useState('');
  const remainingChars = MAX_CHARS - input.length;

  const handleExtract = () => {
    if (input.trim().length > 0 && !isLoading) {
      onExtract(input.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && !isLoading) {
      handleExtract();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-4">
      <div className="space-y-2">
        <label
          htmlFor="parameter-input"
          className="block text-sm font-medium text-text-primary"
        >
          Describe your season parameters
        </label>
        <textarea
          id="parameter-input"
          value={input}
          onChange={(e) => setInput(e.target.value.slice(0, MAX_CHARS))}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          aria-label="Parameter description input"
          aria-describedby="char-count keyboard-hint"
          aria-invalid={input.trim().length === 0 && input.length > 0}
          placeholder='Example: "12-week spring season starting March 1st. No replenishment, 0% holdback. Markdown at week 6 if below 60% sell-through."'
          className="w-full h-32 px-4 py-3 bg-card text-text-primary border border-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-text-muted"
        />
        <div className="flex items-center justify-between text-sm">
          <span
            id="char-count"
            role="status"
            aria-live="polite"
            aria-atomic="true"
            className={`text-text-secondary ${
              remainingChars < 50 ? 'text-warning' : ''
            } ${remainingChars === 0 ? 'text-error' : ''}`}
          >
            {remainingChars} characters remaining
          </span>
          <span id="keyboard-hint" className="text-text-muted">
            Press ⌘+Enter (Mac) or Ctrl+Enter (Windows) to extract
          </span>
        </div>
      </div>

      <button
        onClick={handleExtract}
        disabled={isLoading || input.trim().length === 0}
        aria-label={
          isLoading
            ? 'Extracting parameters, please wait'
            : input.trim().length === 0
              ? 'Extract button disabled, please enter parameters'
              : 'Extract parameters from input'
        }
        aria-busy={isLoading}
        className="w-full px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
            Extracting Parameters...
          </>
        ) : (
          'Extract Parameters'
        )}
      </button>

      <div className="text-xs text-text-muted space-y-1">
        <p className="font-medium">Tips for better extraction:</p>
        <ul className="list-disc list-inside space-y-0.5 ml-2">
          <li>Mention forecast duration (e.g., "12 weeks")</li>
          <li>Include start date (e.g., "starting March 1st")</li>
          <li>Specify replenishment strategy (e.g., "no replenishment")</li>
          <li>State DC holdback % (e.g., "0% holdback")</li>
          <li>
            Optional: Markdown checkpoint (e.g., "markdown at week 6 if below
            60%")
          </li>
        </ul>
      </div>
    </div>
  );
}
