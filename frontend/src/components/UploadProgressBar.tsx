import { useEffect, useState } from 'react';
import { CheckCircle, Loader2, XCircle } from 'lucide-react';

interface UploadProgressBarProps {
  progress: number;
  uploadedBytes?: number;
  totalBytes?: number;
  speed?: number; // bytes per second
  status?: 'uploading' | 'success' | 'error';
  fileName?: string;
  onCancel?: () => void;
}

/**
 * UploadProgressBar Component
 *
 * Displays real-time upload progress with percentage, file size, speed, and ETA.
 * Provides visual feedback for CSV file uploads.
 *
 * @component
 * @example
 * ```tsx
 * <UploadProgressBar
 *   progress={75}
 *   uploadedBytes={3.2 * 1024 * 1024}
 *   totalBytes={4.3 * 1024 * 1024}
 *   speed={1.2 * 1024 * 1024}
 *   status="uploading"
 *   fileName="forecast_data.csv"
 * />
 * ```
 */
export function UploadProgressBar({
  progress,
  uploadedBytes,
  totalBytes,
  speed,
  status = 'uploading',
  fileName,
  onCancel,
}: UploadProgressBarProps) {
  const [eta, setEta] = useState<number | null>(null);

  // Calculate ETA
  useEffect(() => {
    if (speed && uploadedBytes !== undefined && totalBytes !== undefined) {
      const remainingBytes = totalBytes - uploadedBytes;
      const secondsRemaining = remainingBytes / speed;
      setEta(secondsRemaining);
    } else {
      setEta(null);
    }
  }, [speed, uploadedBytes, totalBytes]);

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-success" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-error" />;
      case 'uploading':
      default:
        return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'success':
        return 'Upload complete!';
      case 'error':
        return 'Upload failed';
      case 'uploading':
      default:
        return 'Uploading...';
    }
  };

  const getProgressBarColor = () => {
    switch (status) {
      case 'success':
        return 'bg-success';
      case 'error':
        return 'bg-error';
      case 'uploading':
      default:
        return 'bg-primary';
    }
  };

  return (
    <div className="space-y-3 p-4 bg-card border border-border rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <div>
            <p className="text-sm font-medium text-text-primary">
              {getStatusText()}
            </p>
            {fileName && (
              <p className="text-xs text-text-secondary mt-0.5">{fileName}</p>
            )}
          </div>
        </div>

        {/* Progress Percentage */}
        <div className="text-right">
          <p className="text-2xl font-bold text-text-primary">
            {Math.round(progress)}%
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative">
        <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ease-out ${getProgressBarColor()}`}
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      </div>

      {/* Details */}
      <div className="flex items-center justify-between text-xs text-text-secondary">
        <div className="flex items-center gap-4">
          {/* File Size */}
          {uploadedBytes !== undefined && totalBytes !== undefined && (
            <span>
              {formatBytes(uploadedBytes)} / {formatBytes(totalBytes)}
            </span>
          )}

          {/* Upload Speed */}
          {speed !== undefined && status === 'uploading' && (
            <span className="flex items-center gap-1">
              <span>Speed:</span>
              <span className="font-medium text-text-primary">
                {formatBytes(speed)}/s
              </span>
            </span>
          )}
        </div>

        {/* ETA */}
        {eta !== null && status === 'uploading' && (
          <span className="flex items-center gap-1">
            <span>Time remaining:</span>
            <span className="font-medium text-text-primary">
              {formatTime(eta)}
            </span>
          </span>
        )}

        {/* Cancel Button */}
        {onCancel && status === 'uploading' && (
          <button
            onClick={onCancel}
            className="text-error hover:text-error/80 font-medium transition-colors"
            type="button"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}
