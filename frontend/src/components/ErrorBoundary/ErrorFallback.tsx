import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

export const ErrorFallback = ({ error, resetErrorBoundary }: ErrorFallbackProps) => {
  return (
    <div
      role="alert"
      className="min-h-[400px] flex items-center justify-center p-8"
    >
      <div className="max-w-md w-full bg-card border border-error rounded-lg p-8 text-center">
        <AlertTriangle className="w-16 h-16 text-error mx-auto mb-4" />

        <h2 className="text-xl font-bold text-text-primary mb-2">
          Something went wrong
        </h2>

        <p className="text-text-secondary mb-4">
          We encountered an unexpected error while loading this section.
        </p>

        <details className="mb-6 text-left">
          <summary className="cursor-pointer text-sm text-text-secondary hover:text-text-primary mb-2">
            Error details
          </summary>
          <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-40 text-error">
            {error.message}
          </pre>
        </details>

        <button
          onClick={resetErrorBoundary}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors mx-auto"
        >
          <RefreshCw className="w-4 h-4" />
          Try again
        </button>
      </div>
    </div>
  );
};
