/**
 * Historical Data Upload Component
 *
 * Section 0a: Pre-workflow data upload for historical sales and store attributes.
 * Uploads training data required before parameter extraction.
 *
 * @component
 *
 * @features
 * - Dual upload zones: Historical Sales + Store Attributes
 * - Drag-and-drop file upload with visual feedback
 * - Real-time upload progress tracking
 * - Validation error display with download error report
 * - Success statistics (rows imported, categories detected)
 * - File size validation (50MB for sales, 5MB for stores)
 * - Collapsible sections after successful upload
 */

import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, File, X, AlertCircle, CheckCircle2, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { apiClient } from '@/utils/api-client';

interface UploadResponse {
  rows_imported: number;
  date_range: string;
  categories_detected: string[];
}

interface FileUploadSectionProps {
  title: string;
  description: string;
  endpoint: string;
  maxSize: number;
  accept: string;
  onUploadComplete: () => void;
}

const FileUploadSection: React.FC<FileUploadSectionProps> = ({
  title,
  description,
  endpoint,
  maxSize,
  accept,
  onUploadComplete,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

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

    // Validate file size
    if (file.size > maxSize) {
      setError(`File size exceeds maximum allowed size of ${Math.round(maxSize / (1024 * 1024))}MB`);
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

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      // Upload file (browser will automatically set Content-Type with boundary for FormData)
      const response = await apiClient.post<UploadResponse>(endpoint, formData, {
        timeout: 120000, // 2 minutes for large file uploads
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      setUploadResult(response.data);
      setUploadStatus('success');
      setIsCollapsed(true);
      onUploadComplete();
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
    setIsCollapsed(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <Card className="p-6">
      {/* Header with collapse toggle */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
        {uploadStatus === 'success' && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            aria-label={isCollapsed ? 'Expand section' : 'Collapse section'}
          >
            {isCollapsed ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
          </Button>
        )}
      </div>

      {/* Collapsed success state */}
      {isCollapsed && uploadStatus === 'success' && (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <div>
              <p className="text-sm font-medium text-green-900">Upload Successful</p>
              <p className="text-xs text-green-700">
                {uploadResult?.rows_imported} rows imported
                {uploadResult?.categories_detected && ` • ${uploadResult.categories_detected.length} categories`}
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={handleReset}>
            Re-upload
          </Button>
        </div>
      )}

      {/* Upload interface (hidden when collapsed) */}
      {!isCollapsed && (
        <div className="space-y-4">
          {/* Drag and drop zone */}
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
              role="button"
              aria-label={`Upload ${title} CSV file`}
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
                aria-label={`Browse files for ${title}`}
              >
                Browse Files
              </Button>
              <p className="text-xs text-gray-500 mt-3">
                {accept} • Max {Math.round(maxSize / (1024 * 1024))}MB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept={accept}
                onChange={handleFileInputChange}
                className="hidden"
                aria-hidden="true"
              />
            </div>
          )}

          {/* Selected file preview */}
          {selectedFile && uploadStatus === 'idle' && (
            <div className="border border-gray-300 rounded-lg p-4 bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <File className="w-8 h-8 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-xs text-gray-600">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                </div>
                <Button
                  onClick={handleReset}
                  variant="ghost"
                  size="sm"
                  className="text-gray-500 hover:text-gray-700"
                  aria-label="Remove file"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              <div className="mt-4 flex gap-2">
                <Button onClick={handleUpload} className="flex-1" disabled={uploading}>
                  Upload & Validate
                </Button>
                <Button onClick={handleReset} variant="outline">
                  Cancel
                </Button>
              </div>
            </div>
          )}

          {/* Uploading state */}
          {uploadStatus === 'uploading' && (
            <div className="border border-blue-300 rounded-lg p-4 bg-blue-50" role="status" aria-live="polite">
              <div className="flex items-center gap-3 mb-3">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                <div className="flex-1">
                  <p className="font-medium text-blue-900">{selectedFile?.name}</p>
                  <p className="text-xs text-blue-700">Uploading and validating...</p>
                </div>
              </div>

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

          {/* Success state (expanded) */}
          {uploadStatus === 'success' && !isCollapsed && (
            <div className="border border-green-300 rounded-lg p-4 bg-green-50" role="status" aria-live="polite">
              <div className="flex items-center gap-3 mb-3">
                <CheckCircle2 className="w-8 h-8 text-green-600" />
                <div className="flex-1">
                  <p className="font-medium text-green-900">Upload Successful</p>
                  <p className="text-xs text-green-700">{selectedFile?.name}</p>
                </div>
              </div>

              {uploadResult && (
                <div className="bg-white rounded-lg p-3 border border-green-200 mb-3">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Rows Imported:</span>
                      <span className="font-semibold text-gray-900">{uploadResult.rows_imported}</span>
                    </div>
                    {uploadResult.date_range && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Date Range:</span>
                        <span className="font-semibold text-gray-900">{uploadResult.date_range}</span>
                      </div>
                    )}
                    {uploadResult.categories_detected && uploadResult.categories_detected.length > 0 && (
                      <div>
                        <span className="text-gray-600">Categories Detected:</span>
                        <div className="mt-1 flex flex-wrap gap-1">
                          {uploadResult.categories_detected.map((category, idx) => (
                            <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                              {category}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <Button onClick={handleReset} variant="outline" size="sm" className="w-full">
                Upload Another File
              </Button>
            </div>
          )}

          {/* Error state */}
          {uploadStatus === 'error' && (
            <div className="border border-red-300 rounded-lg p-4 bg-red-50" role="alert">
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
      )}
    </Card>
  );
};

export function HistoricalDataUpload() {
  const [salesUploaded, setSalesUploaded] = useState(false);
  const [storesUploaded, setStoresUploaded] = useState(false);

  return (
    <div className="w-full space-y-6 py-8">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-gray-900">
          Step 1: Upload Historical Data
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Upload your historical sales data and store attributes to train the forecasting models.
          Both files are required before proceeding to parameter extraction.
        </p>
      </div>

      <div className="max-w-4xl mx-auto space-y-4">
        <FileUploadSection
          title="Historical Sales Data (2022-2024)"
          description="Upload CSV with columns: date, category, store_id, quantity_sold, revenue"
          endpoint="/api/v1/data/upload-historical-sales"
          maxSize={50 * 1024 * 1024} // 50MB
          accept=".csv"
          onUploadComplete={() => setSalesUploaded(true)}
        />

        <FileUploadSection
          title="Store Attributes"
          description="Upload CSV with store characteristics for clustering (50 stores)"
          endpoint="/api/v1/data/upload-store-attributes"
          maxSize={5 * 1024 * 1024} // 5MB
          accept=".csv"
          onUploadComplete={() => setStoresUploaded(true)}
        />

        {/* Status indicator */}
        {(salesUploaded || storesUploaded) && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              {salesUploaded && storesUploaded ? (
                <>
                  <CheckCircle2 className="w-4 h-4 inline mr-2 text-green-600" />
                  Both files uploaded successfully! You can now proceed to parameter extraction below.
                </>
              ) : (
                <>
                  <Loader2 className="w-4 h-4 inline mr-2 animate-spin" />
                  {salesUploaded ? 'Historical sales uploaded. ' : 'Upload historical sales. '}
                  {storesUploaded ? 'Store attributes uploaded. ' : 'Upload store attributes to continue.'}
                </>
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
