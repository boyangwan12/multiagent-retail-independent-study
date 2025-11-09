/**
 * Weekly Actuals Upload Modal
 *
 * Modal for uploading weekly actual sales data during the active season.
 * Calculates variance against forecast and triggers re-forecast if variance >20%.
 *
 * @component
 *
 * @features
 * - Week-specific upload with date range display
 * - Drag-and-drop CSV file upload
 * - Real-time upload progress
 * - Variance calculation and color-coded results
 * - Re-forecast alert for high variance (>20%)
 * - Expected format documentation
 */

import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, File, X, AlertCircle, CheckCircle2, Loader2, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/utils/api-client';

interface WeeklyActualsUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  weekNumber: number;
  weekStartDate: string;
  weekEndDate: string;
  forecastId: string;
  onUploadSuccess: (result: UploadResult) => void;
}

interface UploadResult {
  rows_imported: number;
  week_number: number;
  variance_check: {
    variance_pct: number;
    variance_status: 'NORMAL' | 'ELEVATED' | 'HIGH';
    variance_color: string;
    reforecast_triggered: boolean;
    message?: string;
  };
}

export function WeeklyActualsUploadModal({
  isOpen,
  onClose,
  weekNumber,
  weekStartDate,
  weekEndDate,
  forecastId,
  onUploadSuccess,
}: WeeklyActualsUploadModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  // Format dates for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  // Drag and drop handlers
  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileSelection = (file: File) => {
    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Invalid file type. Only CSV files are accepted.');
      setUploadStatus('error');
      return;
    }

    // Validate file size (max 5MB for weekly data)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File size exceeds maximum allowed size of 5MB');
      setUploadStatus('error');
      return;
    }

    setSelectedFile(file);
    setUploadStatus('idle');
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      setUploadStatus('uploading');
      setUploadProgress(0);
      setError(null);

      // Create FormData
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('forecast_id', forecastId);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      // Upload file (browser will automatically set Content-Type with boundary for FormData)
      const response = await apiClient.post<UploadResult>(
        '/api/v1/data/upload-weekly-sales',
        formData,
        {
          timeout: 60000, // 1 minute timeout for weekly uploads
        }
      );

      clearInterval(progressInterval);
      setUploadProgress(100);

      setUploadResult(response.data);
      setUploadStatus('success');
      onUploadSuccess(response.data);
    } catch (err: any) {
      setUploadStatus('error');
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setUploadStatus('idle');
    setUploadProgress(0);
    setError(null);
    setUploadResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getVarianceColor = (status: string) => {
    switch (status) {
      case 'NORMAL':
        return 'text-green-600';
      case 'ELEVATED':
        return 'text-amber-600';
      case 'HIGH':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getVarianceIcon = (status: string) => {
    switch (status) {
      case 'NORMAL':
        return <CheckCircle2 className="w-6 h-6 text-green-600" />;
      case 'ELEVATED':
        return <AlertTriangle className="w-6 h-6 text-amber-600" />;
      case 'HIGH':
        return <AlertCircle className="w-6 h-6 text-red-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={handleClose}>
      <div
        className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Upload Week {weekNumber} Actuals</h2>
            <p className="text-sm text-gray-600 mt-1">
              {formatDate(weekStartDate)} - {formatDate(weekEndDate)}
            </p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Expected Format */}
          {uploadStatus === 'idle' && !selectedFile && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">Expected CSV Format:</h3>
              <pre className="text-xs bg-white border border-blue-200 rounded p-3 overflow-x-auto">
                <code>
                  {`date,store_id,quantity_sold\n${weekStartDate},S001,18\n${weekStartDate},S002,22\n...\n${weekEndDate},S050,19`}
                </code>
              </pre>
              <p className="text-sm text-blue-800 mt-2">
                Expected: ~350 rows (50 stores × 7 days)
              </p>
            </div>
          )}

          {/* Upload Zone */}
          {!selectedFile && uploadStatus !== 'success' && (
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isDragging
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 bg-gray-50 hover:border-gray-400'
              }`}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-sm text-gray-600 mb-2">
                Drag and drop your CSV file here, or
              </p>
              <Button
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                size="sm"
              >
                Browse Files
              </Button>
              <p className="text-xs text-gray-500 mt-3">CSV only • Max 5MB</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileInputChange}
                className="hidden"
              />
            </div>
          )}

          {/* Selected File */}
          {selectedFile && uploadStatus === 'idle' && (
            <div className="border border-gray-300 rounded-lg p-4 bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <File className="w-8 h-8 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-xs text-gray-600">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <Button
                  onClick={handleReset}
                  variant="ghost"
                  size="sm"
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              <div className="mt-4 flex gap-2">
                <Button onClick={handleUpload} className="flex-1" disabled={uploading}>
                  Upload & Calculate Variance
                </Button>
                <Button onClick={handleReset} variant="outline">
                  Cancel
                </Button>
              </div>
            </div>
          )}

          {/* Uploading State */}
          {uploadStatus === 'uploading' && (
            <div className="border border-blue-300 rounded-lg p-4 bg-blue-50">
              <div className="flex items-center gap-3 mb-3">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                <div className="flex-1">
                  <p className="font-medium text-blue-900">{selectedFile?.name}</p>
                  <p className="text-xs text-blue-700">Uploading and calculating variance...</p>
                </div>
              </div>

              <div className="w-full bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-xs text-blue-700 mt-1">{uploadProgress}%</p>
            </div>
          )}

          {/* Success State */}
          {uploadStatus === 'success' && uploadResult && (
            <div className="space-y-4">
              <div className="border border-green-300 rounded-lg p-4 bg-green-50">
                <div className="flex items-center gap-3 mb-3">
                  <CheckCircle2 className="w-8 h-8 text-green-600" />
                  <div className="flex-1">
                    <p className="font-medium text-green-900">Upload Successful</p>
                    <p className="text-xs text-green-700">
                      Week {uploadResult.week_number} • {uploadResult.rows_imported} rows imported
                    </p>
                  </div>
                </div>
              </div>

              {/* Variance Results */}
              <div className={`border rounded-lg p-4 ${
                uploadResult.variance_check.variance_status === 'HIGH' ? 'border-red-300 bg-red-50' :
                uploadResult.variance_check.variance_status === 'ELEVATED' ? 'border-amber-300 bg-amber-50' :
                'border-green-300 bg-green-50'
              }`}>
                <div className="flex items-center gap-3 mb-3">
                  {getVarianceIcon(uploadResult.variance_check.variance_status)}
                  <div className="flex-1">
                    <p className={`font-semibold ${getVarianceColor(uploadResult.variance_check.variance_status)}`}>
                      Variance: {uploadResult.variance_check.variance_pct > 0 ? '+' : ''}
                      {(uploadResult.variance_check.variance_pct * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-700">
                      {uploadResult.variance_check.variance_status === 'NORMAL' && '🟢 Tracking well'}
                      {uploadResult.variance_check.variance_status === 'ELEVATED' && '🟡 Elevated variance'}
                      {uploadResult.variance_check.variance_status === 'HIGH' && '🔴 High variance'}
                    </p>
                  </div>
                </div>

                {/* Re-forecast Alert */}
                {uploadResult.variance_check.reforecast_triggered && (
                  <div className="mt-3 p-3 bg-red-100 border border-red-300 rounded">
                    <p className="font-semibold text-red-900 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      Re-forecast Triggered
                    </p>
                    <p className="text-sm text-red-800 mt-1">
                      {uploadResult.variance_check.message ||
                       'Variance exceeds 20% threshold. Re-forecasting remaining weeks...'}
                    </p>
                  </div>
                )}
              </div>

              <Button onClick={handleClose} className="w-full">
                Close
              </Button>
            </div>
          )}

          {/* Error State */}
          {uploadStatus === 'error' && (
            <div className="border border-red-300 rounded-lg p-4 bg-red-50">
              <div className="flex items-center gap-3 mb-3">
                <AlertCircle className="w-8 h-8 text-red-600" />
                <div className="flex-1">
                  <p className="font-medium text-red-900">Upload Failed</p>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>

              <Button onClick={handleReset} variant="outline" size="sm" className="w-full">
                Try Again
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
