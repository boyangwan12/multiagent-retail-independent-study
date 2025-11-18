import { ErrorBoundary as ReactErrorBoundary } from 'react-error-boundary';
import type { ReactNode } from 'react';
import { ErrorFallback } from './ErrorFallback';

interface ErrorBoundaryProps {
  children: ReactNode;
  onReset?: () => void;
}

export const ErrorBoundary = ({ children, onReset }: ErrorBoundaryProps) => {
  const handleReset = () => {
    // Optional custom reset logic
    if (onReset) {
      onReset();
    }
    // Reload the page as fallback
    window.location.reload();
  };

  return (
    <ReactErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={handleReset}
      onError={(error, errorInfo) => {
        // Log error to console (in production, send to error tracking service)
        console.error('Error caught by boundary:', error, errorInfo);
      }}
    >
      {children}
    </ReactErrorBoundary>
  );
};
