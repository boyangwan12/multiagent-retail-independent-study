import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, File, X, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { UploadService, type ValidationError } from '@/services/upload-service';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface UploadZoneProps {
  workflowId: string;
  agentType: 'demand' | 'inventory' | 'pricing';
  fileType: string;
  fileTypeLabel: string;
  onUploadSuccess: (fileName: string, rows: number) => void;
  onUploadError: (error: string) => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  workflowId,
  agentType,
  fileType,
  fileTypeLabel,
  onUploadSuccess,
  onUploadError,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<
    'idle' | 'uploading' | 'success' | 'error'
  >('idle');
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>(
    []
  );

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ============================================================================
  // DRAG AND DROP HANDLERS
  // ============================================================================

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

  // ============================================================================
  // FILE SELECTION HANDLER
  // ============================================================================

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileSelection = (file: File) => {
    try {
      // Validate file (will throw error if invalid)
      UploadService['validateFile'](file);

      setSelectedFile(file);
      setUploadStatus('idle');
      setValidationErrors([]);
    } catch (error: any) {
      onUploadError(error.message);
      setUploadStatus('error');
    }
  };

  // ============================================================================
  // UPLOAD HANDLER
  // ============================================================================

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      setUploadStatus('uploading');
      setUploadProgress(0);

      // Simulate progress (real implementation would use XMLHttpRequest with onprogress)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      const response = await UploadService.uploadFile(
        workflowId,
        agentType,
        selectedFile,
        fileType
      );

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.validation_status === 'VALID') {
        setUploadStatus('success');
        onUploadSuccess(response.file_name, response.rows_uploaded);
      } else {
        setUploadStatus('error');
        setValidationErrors(response.errors || []);
        onUploadError(
          `Validation failed: ${response.errors?.length || 0} errors found`
        );
      }
    } catch (error: any) {
      setUploadStatus('error');
      onUploadError(error.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // ============================================================================
  // RESET HANDLER
  // ============================================================================

  const handleReset = () => {
    setSelectedFile(null);
    setUploadStatus('idle');
    setUploadProgress(0);
    setValidationErrors([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // ============================================================================
  // DOWNLOAD ERROR REPORT
  // ============================================================================

  const handleDownloadErrorReport = () => {
    if (validationErrors.length > 0) {
      UploadService.downloadErrorReport(
        validationErrors,
        `${fileType}_validation_errors.txt`
      );
    }
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <Card className="p-4">
      <div className="mb-2">
        <h4 className="font-semibold text-gray-900">{fileTypeLabel}</h4>
        <p className="text-xs text-gray-600">Upload CSV file (.csv only, max 10MB)</p>
      </div>

      {/* DRAG AND DROP ZONE */}
      {!selectedFile && (
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
          role="button"
          aria-label={`Upload ${fileTypeLabel} CSV file`}
          tabIndex={0}
        >
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" aria-hidden="true" />
          <p className="text-sm text-gray-600 mb-2">
            Drag and drop your CSV file here, or
          </p>
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            size="sm"
            aria-label={`Browse files for ${fileTypeLabel}`}
          >
            Browse Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileInputChange}
            className="hidden"
            aria-hidden="true"
          />
        </div>
      )}

      {/* SELECTED FILE PREVIEW */}
      {selectedFile && uploadStatus === 'idle' && (
        <div className="border border-gray-300 rounded-lg p-4 bg-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <File className="w-8 h-8 text-blue-600" />
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-xs text-gray-600">
                  {UploadService.formatFileSize(selectedFile.size)}
                </p>
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
            <Button onClick={handleUpload} className="flex-1">
              Upload File
            </Button>
            <Button onClick={handleReset} variant="outline">
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* UPLOADING STATE */}
      {uploadStatus === 'uploading' && (
        <div className="border border-blue-300 rounded-lg p-4 bg-blue-50" role="status" aria-live="polite">
          <div className="flex items-center gap-3 mb-3">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <div className="flex-1">
              <p className="font-medium text-blue-900">{selectedFile?.name}</p>
              <p className="text-xs text-blue-700">Uploading...</p>
            </div>
          </div>

          {/* Progress Bar */}
          <div
            className="w-full bg-blue-200 rounded-full h-2"
            role="progressbar"
            aria-valuenow={uploadProgress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Upload progress"
          >
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-xs text-blue-700 mt-1">{uploadProgress}%</p>
        </div>
      )}

      {/* SUCCESS STATE */}
      {uploadStatus === 'success' && (
        <div className="border border-green-300 rounded-lg p-4 bg-green-50" role="status" aria-live="polite">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-8 h-8 text-green-600" />
            <div className="flex-1">
              <p className="font-medium text-green-900">Upload Successful</p>
              <p className="text-xs text-green-700">{selectedFile?.name}</p>
            </div>
          </div>
          <Button onClick={handleReset} variant="outline" size="sm" className="mt-3">
            Upload Another File
          </Button>
        </div>
      )}

      {/* ERROR STATE */}
      {uploadStatus === 'error' && (
        <div className="border border-red-300 rounded-lg p-4 bg-red-50" role="alert">
          <div className="flex items-center gap-3 mb-3">
            <AlertCircle className="w-8 h-8 text-red-600" />
            <div className="flex-1">
              <p className="font-medium text-red-900">Upload Failed</p>
              <p className="text-xs text-red-700">
                {validationErrors.length > 0
                  ? `${validationErrors.length} validation errors found`
                  : 'An error occurred during upload'}
              </p>
            </div>
          </div>

          {/* Validation Errors List */}
          {validationErrors.length > 0 && (
            <div
              className="max-h-40 overflow-y-auto bg-white rounded p-3 border border-red-200 mb-3"
              aria-label="Validation errors"
              tabIndex={0}
            >
              <ul className="space-y-2">
                {validationErrors.slice(0, 5).map((error, index) => (
                  <li key={index} className="text-xs text-red-800">
                    <strong>{error.error_type}:</strong> {error.message}
                    {error.row && ` (Row ${error.row})`}
                  </li>
                ))}
                {validationErrors.length > 5 && (
                  <li className="text-xs text-red-600 italic">
                    ...and {validationErrors.length - 5} more errors
                  </li>
                )}
              </ul>
            </div>
          )}

          <div className="flex gap-2">
            <Button onClick={handleReset} variant="outline" size="sm">
              Try Again
            </Button>
            {validationErrors.length > 0 && (
              <Button
                onClick={handleDownloadErrorReport}
                variant="outline"
                size="sm"
              >
                Download Error Report
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  );
};
