# PHASE4-007: CSV Upload Workflows Integration

**Story ID:** PHASE4-007
**Story Name:** Integrate CSV Upload Workflows for Agent Data Input
**Phase:** Phase 4 - Frontend/Backend Integration
**Dependencies:** PHASE4-001, PHASE4-002, PHASE4-003
**Estimated Effort:** 9 hours
**Assigned To:** Developer (Frontend + Backend Integration)
**Status:** Not Started

**Planning References:**
- PRD v3.3: Section 4.3 (CSV Data Upload & Validation)
- Technical Architecture v3.3: Section 4.7 (Upload Endpoints & File Storage)
- Frontend Spec v3.3: Section 3.9 (Upload UI Components)

---

## User Story

**As a** retail planner using the Multi-Agent Forecasting System,
**I want** to upload CSV files containing historical sales data, store profiles, and constraints,
**So that** agents can process real data and generate accurate forecasts and recommendations.

---

## Context & Background

### What This Story Covers

This story integrates CSV file upload workflows for all three agents:

1. **Demand Agent CSV Uploads:**
   - Historical sales data (sales_data.csv)
   - Store profiles (store_profiles.csv)
   - Optional: External factors (weather, promotions)

2. **Inventory Agent CSV Uploads:**
   - DC inventory levels (dc_inventory.csv)
   - Lead times by store (lead_times.csv)
   - Safety stock policies (safety_stock.csv)

3. **Pricing Agent CSV Uploads:**
   - Historical markdown data (markdown_history.csv)
   - Price elasticity coefficients (elasticity.csv)
   - Competitive pricing (competitor_prices.csv)

### Why CSV Uploads are Critical

In Phase 4, we're integrating the frontend with backend endpoints. CSV uploads enable:
- **Real Data Processing:** Agents use actual historical data instead of mock data
- **User Flexibility:** Users can update datasets without code changes
- **Validation:** Backend validates CSV format and content before processing
- **Error Reporting:** Clear feedback if uploads fail (missing columns, wrong formats)

### Backend Endpoints

**General Upload Endpoint:**
- **Endpoint:** `POST /api/workflows/{workflow_id}/upload`
- **Body:** `multipart/form-data` with file and metadata
- **Returns:** Upload confirmation with validation results

**Agent-Specific Endpoints:**
- `POST /api/workflows/{id}/demand/upload` - Demand Agent CSVs
- `POST /api/workflows/{id}/inventory/upload` - Inventory Agent CSVs
- `POST /api/workflows/{id}/pricing/upload` - Pricing Agent CSVs

### Expected CSV Formats

**Historical Sales Data (sales_data.csv):**
```csv
store_id,week,sales_units,sales_revenue,inventory_on_hand
S001,1,150,3750,500
S001,2,180,4500,470
```

**Store Profiles (store_profiles.csv):**
```csv
store_id,store_name,region,size_sqft,cluster_id
S001,Downtown LA,West,5000,Cluster_A
S002,Brooklyn Center,East,7500,Cluster_B
```

**DC Inventory (dc_inventory.csv):**
```csv
sku,dc_location,available_units,reserved_units
SKU123,DC_West,5000,1200
SKU456,DC_East,3000,800
```

### Frontend Upload Flow

1. User completes parameter extraction (Section 0)
2. Workflow is created with workflow_id
3. User clicks "Upload Data" button for each agent
4. Drag-and-drop or file picker opens
5. User selects CSV file(s)
6. Frontend validates file size/type
7. POST to backend with multipart/form-data
8. Backend validates CSV format and content
9. Success: Display confirmation message
10. Error: Display specific validation errors

---

## Acceptance Criteria

### Context Integration & Data Flow

- [ ] **AC1:** Components use workflowId from ParameterContext (not props)
- [ ] **AC2:** Category from Context validated against uploaded store profiles
- [ ] **AC3:** Upload button only enabled when workflowId exists

### Backend Integration

- [ ] **AC4:** POST /api/workflows/{id}/demand/upload accepts multipart/form-data
- [ ] **AC2:** Backend validates CSV format (headers, data types, required columns)
- [ ] **AC3:** Backend returns validation errors with specific row/column details
- [ ] **AC4:** POST /api/workflows/{id}/inventory/upload accepts DC inventory CSVs
- [ ] **AC5:** POST /api/workflows/{id}/pricing/upload accepts markdown history CSVs
- [ ] **AC6:** Backend stores uploaded files in workflow-specific directory
- [ ] **AC7:** Backend returns upload confirmation with file metadata (size, rows, timestamp)

### Frontend Upload Component

- [ ] **AC8:** UploadZone component supports drag-and-drop
- [ ] **AC9:** UploadZone component supports file picker (click to browse)
- [ ] **AC10:** Frontend validates file size before upload (max 10MB)
- [ ] **AC11:** Frontend validates file extension (.csv only)
- [ ] **AC12:** Upload progress indicator displays during file upload
- [ ] **AC13:** Success message displays with file name and row count
- [ ] **AC14:** Error message displays with specific validation errors
- [ ] **AC15:** Multiple file upload supported (e.g., sales_data.csv + store_profiles.csv together)

### Dashboard Integration

- [ ] **AC16:** "Upload Data" button appears below Agent Cards (Section 1)
- [ ] **AC17:** Upload modal opens with tabs for each agent:
  - Demand Agent tab (sales_data.csv, store_profiles.csv)
  - Inventory Agent tab (dc_inventory.csv, lead_times.csv)
  - Pricing Agent tab (markdown_history.csv, elasticity.csv)
- [ ] **AC18:** Upload status persists after modal closes (shows "Uploaded ✓" badge)
- [ ] **AC19:** User can re-upload files to replace previous uploads
- [ ] **AC20:** CSV upload is optional (workflow can run with default/mock data)

### Validation & Error Handling

- [ ] **AC21:** Backend detects missing required columns:
  - Example: sales_data.csv missing "store_id" column
  - Error: "Missing required column: 'store_id' in sales_data.csv"
- [ ] **AC22:** Backend detects data type mismatches:
  - Example: "sales_units" contains non-numeric value "N/A" in row 5
  - Error: "Invalid data type in row 5, column 'sales_units': expected number, got 'N/A'"
- [ ] **AC23:** Backend detects empty files:
  - Error: "CSV file is empty or contains only headers"
- [ ] **AC24:** Frontend displays validation errors in a scrollable list
- [ ] **AC25:** User can download error report as .txt file

### Accessibility

- [ ] **AC26:** Drag-and-drop zone has aria-label describing purpose
- [ ] **AC27:** File picker button has aria-label
- [ ] **AC28:** Upload progress has role="progressbar" with aria-valuenow
- [ ] **AC29:** Success/error messages have role="status" or role="alert"
- [ ] **AC30:** Validation error list has aria-label and is keyboard navigable
- [ ] **AC31:** Modal has proper focus trap and ESC key closes it
- [ ] **AC32:** Tab navigation works correctly within upload modal

### Testing

- [ ] **AC33:** Backend upload endpoints tested in Postman:
  - Test Case 1: Valid CSV upload (all required columns, correct data types)
  - Test Case 2: Invalid CSV (missing required column)
  - Test Case 3: Invalid CSV (wrong data type in row)
  - Test Case 4: File too large (>10MB)
  - Test Case 5: Wrong file extension (.xlsx instead of .csv)
- [ ] **AC27:** Frontend upload component manually tested:
  - Drag-and-drop functionality
  - File picker functionality
  - Progress indicator
  - Success/error messages
- [ ] **AC28:** Multiple file upload tested (2-3 CSVs uploaded together)

---

## Tasks

### Task 1: Test Backend Upload Endpoints in Postman

**Objective:** Verify POST /api/workflows/{id}/demand/upload accepts CSV files and validates correctly.

**Subtasks:**

1. **Test Case 1: Valid CSV Upload (Demand Agent - Sales Data)**
   - Create valid sales_data.csv:
     ```csv
     store_id,week,sales_units,sales_revenue,inventory_on_hand
     S001,1,150,3750,500
     S001,2,180,4500,470
     S002,1,120,3000,400
     S002,2,135,3375,385
     ```
   - Postman Request:
     - Method: POST
     - URL: http://localhost:8000/api/workflows/{workflow_id}/demand/upload
     - Body: form-data
       - Key: "file" (type: File)
       - Value: sales_data.csv
       - Key: "file_type" (type: Text)
       - Value: "sales_data"
   - Expected Response (200 OK):
     ```json
     {
       "workflow_id": "wf_abc123",
       "file_type": "sales_data",
       "file_name": "sales_data.csv",
       "file_size_bytes": 256,
       "rows_uploaded": 4,
       "columns": ["store_id", "week", "sales_units", "sales_revenue", "inventory_on_hand"],
       "validation_status": "VALID",
       "uploaded_at": "2025-01-15T10:30:00Z",
       "message": "File uploaded successfully"
     }
     ```
   - Validation:
     - [ ] rows_uploaded = 4 (excluding header)
     - [ ] validation_status = "VALID"
     - [ ] columns array matches expected headers

2. **Test Case 2: Invalid CSV - Missing Required Column**
   - Create invalid sales_data.csv (missing "sales_units"):
     ```csv
     store_id,week,sales_revenue,inventory_on_hand
     S001,1,3750,500
     S001,2,4500,470
     ```
   - Postman Request: (same as Test Case 1)
   - Expected Response (400 Bad Request):
     ```json
     {
       "workflow_id": "wf_abc123",
       "file_type": "sales_data",
       "file_name": "sales_data.csv",
       "validation_status": "INVALID",
       "errors": [
         {
           "error_type": "MISSING_COLUMN",
           "column": "sales_units",
           "message": "Required column 'sales_units' is missing from CSV file"
         }
       ],
       "uploaded_at": "2025-01-15T10:30:00Z"
     }
     ```
   - Validation:
     - [ ] HTTP status 400
     - [ ] validation_status = "INVALID"
     - [ ] errors array explains missing column

3. **Test Case 3: Invalid CSV - Wrong Data Type**
   - Create invalid sales_data.csv (non-numeric sales_units):
     ```csv
     store_id,week,sales_units,sales_revenue,inventory_on_hand
     S001,1,150,3750,500
     S001,2,N/A,4500,470
     S002,1,120,3000,400
     ```
   - Postman Request: (same as Test Case 1)
   - Expected Response (400 Bad Request):
     ```json
     {
       "workflow_id": "wf_abc123",
       "file_type": "sales_data",
       "file_name": "sales_data.csv",
       "validation_status": "INVALID",
       "errors": [
         {
           "error_type": "DATA_TYPE_MISMATCH",
           "row": 3,
           "column": "sales_units",
           "expected_type": "integer",
           "actual_value": "N/A",
           "message": "Row 3, column 'sales_units': expected integer, got 'N/A'"
         }
       ],
       "uploaded_at": "2025-01-15T10:30:00Z"
     }
     ```
   - Validation:
     - [ ] HTTP status 400
     - [ ] errors array specifies row 3, column sales_units
     - [ ] expected_type and actual_value clearly stated

4. **Test Case 4: File Too Large**
   - Create large CSV file (>10MB)
   - Postman Request: (same as Test Case 1)
   - Expected Response (413 Payload Too Large):
     ```json
     {
       "detail": "File size exceeds maximum allowed size of 10MB"
     }
     ```
   - Validation:
     - [ ] HTTP status 413
     - [ ] Clear error message about file size limit

5. **Test Case 5: Wrong File Extension**
   - Upload .xlsx file instead of .csv
   - Postman Request:
     - Body: form-data
       - Key: "file"
       - Value: sales_data.xlsx
   - Expected Response (400 Bad Request):
     ```json
     {
       "detail": "Invalid file type. Only .csv files are accepted."
     }
     ```
   - Validation:
     - [ ] HTTP status 400
     - [ ] Error message mentions .csv requirement

6. **Test Case 6: Multiple File Upload (Demand Agent)**
   - Upload both sales_data.csv and store_profiles.csv together
   - Postman Request:
     - Method: POST
     - URL: http://localhost:8000/api/workflows/{workflow_id}/demand/upload
     - Body: form-data
       - Key: "files" (type: File, multiple files enabled)
       - Value: sales_data.csv, store_profiles.csv
   - Expected Response (200 OK):
     ```json
     {
       "workflow_id": "wf_abc123",
       "files_uploaded": [
         {
           "file_type": "sales_data",
           "file_name": "sales_data.csv",
           "rows_uploaded": 50,
           "validation_status": "VALID"
         },
         {
           "file_type": "store_profiles",
           "file_name": "store_profiles.csv",
           "rows_uploaded": 50,
           "validation_status": "VALID"
         }
       ],
       "uploaded_at": "2025-01-15T10:30:00Z",
       "message": "2 files uploaded successfully"
     }
     ```
   - Validation:
     - [ ] Both files processed successfully
     - [ ] Separate validation status for each file

**Postman Collection Setup:**
- Create "PHASE4-007 CSV Upload Tests" folder
- Save all 6 test cases with assertions
- Export collection to `docs/04_MVP_Development/implementation/phase_4_integration/postman/`

**Validation Checklist:**
- [ ] Test Case 1: Valid upload returns 200 OK with metadata
- [ ] Test Case 2: Missing column returns 400 with MISSING_COLUMN error
- [ ] Test Case 3: Wrong data type returns 400 with DATA_TYPE_MISMATCH error
- [ ] Test Case 4: Large file returns 413 Payload Too Large
- [ ] Test Case 5: Wrong extension returns 400
- [ ] Test Case 6: Multiple files upload successfully

---

### Task 2: Create Frontend UploadService

**Objective:** Create service to handle CSV file uploads to backend.

**File:** `frontend/src/services/upload-service.ts`

**Implementation:**

```typescript
import { API_ENDPOINTS } from '@/config/api';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface UploadResponse {
  workflow_id: string;
  file_type: string;
  file_name: string;
  file_size_bytes: number;
  rows_uploaded: number;
  columns: string[];
  validation_status: 'VALID' | 'INVALID';
  errors?: ValidationError[];
  uploaded_at: string;
  message: string;
}

export interface ValidationError {
  error_type: 'MISSING_COLUMN' | 'DATA_TYPE_MISMATCH' | 'EMPTY_FILE' | 'DUPLICATE_ROWS' | 'OTHER';
  row?: number;
  column?: string;
  expected_type?: string;
  actual_value?: string;
  message: string;
}

export interface MultipleUploadResponse {
  workflow_id: string;
  files_uploaded: Array<{
    file_type: string;
    file_name: string;
    rows_uploaded: number;
    validation_status: 'VALID' | 'INVALID';
    errors?: ValidationError[];
  }>;
  uploaded_at: string;
  message: string;
}

export type AgentType = 'demand' | 'inventory' | 'pricing';

// ============================================================================
// UPLOAD SERVICE
// ============================================================================

export class UploadService {
  /**
   * Maximum file size allowed (10MB)
   */
  static readonly MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

  /**
   * Upload single CSV file for an agent
   * @param workflowId - The workflow ID
   * @param agentType - Agent type (demand, inventory, pricing)
   * @param file - File object from input
   * @param fileType - Type of file (e.g., "sales_data", "store_profiles")
   * @returns Promise<UploadResponse>
   */
  static async uploadFile(
    workflowId: string,
    agentType: AgentType,
    file: File,
    fileType: string
  ): Promise<UploadResponse> {
    // Validate file before upload
    UploadService.validateFile(file);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    const endpoint = UploadService.getUploadEndpoint(workflowId, agentType);

    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData,
      // Note: Do NOT set Content-Type header - browser sets it automatically with boundary
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'File upload failed');
    }

    return await response.json();
  }

  /**
   * Upload multiple CSV files for an agent
   * @param workflowId - The workflow ID
   * @param agentType - Agent type (demand, inventory, pricing)
   * @param files - Array of File objects with their types
   * @returns Promise<MultipleUploadResponse>
   */
  static async uploadMultipleFiles(
    workflowId: string,
    agentType: AgentType,
    files: Array<{ file: File; fileType: string }>
  ): Promise<MultipleUploadResponse> {
    // Validate all files before upload
    files.forEach(({ file }) => UploadService.validateFile(file));

    const formData = new FormData();

    files.forEach(({ file, fileType }) => {
      formData.append('files', file);
      formData.append('file_types', fileType);
    });

    const endpoint = UploadService.getUploadEndpoint(workflowId, agentType);

    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Multiple file upload failed');
    }

    return await response.json();
  }

  /**
   * Validate file before upload
   * @throws Error if file is invalid
   */
  private static validateFile(file: File): void {
    // Check file extension
    if (!file.name.toLowerCase().endsWith('.csv')) {
      throw new Error(
        `Invalid file type: ${file.name}. Only .csv files are accepted.`
      );
    }

    // Check file size
    if (file.size > UploadService.MAX_FILE_SIZE_BYTES) {
      const maxSizeMB = UploadService.MAX_FILE_SIZE_BYTES / (1024 * 1024);
      throw new Error(
        `File size exceeds maximum allowed size of ${maxSizeMB}MB`
      );
    }

    // Check if file is empty
    if (file.size === 0) {
      throw new Error('File is empty');
    }
  }

  /**
   * Get upload endpoint URL for agent type
   */
  private static getUploadEndpoint(
    workflowId: string,
    agentType: AgentType
  ): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    switch (agentType) {
      case 'demand':
        return `${baseUrl}/api/workflows/${workflowId}/demand/upload`;
      case 'inventory':
        return `${baseUrl}/api/workflows/${workflowId}/inventory/upload`;
      case 'pricing':
        return `${baseUrl}/api/workflows/${workflowId}/pricing/upload`;
      default:
        throw new Error(`Unknown agent type: ${agentType}`);
    }
  }

  /**
   * Format file size for display
   * @param bytes - File size in bytes
   * @returns Formatted string (e.g., "2.5 MB")
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Get file type display name
   */
  static getFileTypeLabel(fileType: string): string {
    const labels: Record<string, string> = {
      sales_data: 'Historical Sales Data',
      store_profiles: 'Store Profiles',
      dc_inventory: 'DC Inventory Levels',
      lead_times: 'Lead Times by Store',
      safety_stock: 'Safety Stock Policies',
      markdown_history: 'Historical Markdown Data',
      elasticity: 'Price Elasticity Coefficients',
      competitor_prices: 'Competitive Pricing Data',
    };

    return labels[fileType] || fileType;
  }

  /**
   * Download validation error report as .txt file
   */
  static downloadErrorReport(errors: ValidationError[], fileName: string): void {
    const errorText = errors
      .map((error, index) => {
        let text = `Error ${index + 1}: ${error.error_type}\n`;
        if (error.row) text += `  Row: ${error.row}\n`;
        if (error.column) text += `  Column: ${error.column}\n`;
        if (error.expected_type)
          text += `  Expected Type: ${error.expected_type}\n`;
        if (error.actual_value) text += `  Actual Value: ${error.actual_value}\n`;
        text += `  Message: ${error.message}\n\n`;
        return text;
      })
      .join('');

    const blob = new Blob([errorText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName || 'validation_errors.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}
```

**Validation:**
- [ ] uploadFile validates file extension and size
- [ ] uploadMultipleFiles handles array of files
- [ ] FormData appended correctly with file and file_type
- [ ] Error handling throws descriptive messages
- [ ] Utility methods (formatFileSize, downloadErrorReport) work correctly

---

### Task 3: Create UploadZone Component (Drag-and-Drop)

**Objective:** Create reusable component for CSV file uploads with drag-and-drop.

**File:** `frontend/src/components/UploadZone/UploadZone.tsx`

**Implementation:**

```typescript
import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, File, X, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { UploadService, ValidationError } from '@/services/upload-service';
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
```

**Validation:**
- [ ] Drag-and-drop zone highlights when dragging file over it
- [ ] File picker opens when "Browse Files" button clicked
- [ ] Selected file preview shows file name and size
- [ ] Upload button triggers file upload
- [ ] Progress bar animates during upload
- [ ] Success state displays with green checkmark
- [ ] Error state displays validation errors
- [ ] "Download Error Report" downloads .txt file with errors

---

### Task 4: Create UploadModal Component with Agent Tabs

**Objective:** Create modal with tabs for each agent's CSV uploads.

**File:** `frontend/src/components/UploadModal/UploadModal.tsx`

**Implementation:**

```typescript
import React, { useState } from 'react';
import { useParameters } from '@/contexts/ParameterContext';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { UploadZone } from '@/components/UploadZone';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2 } from 'lucide-react';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface UploadStatus {
  [agentType: string]: {
    [fileType: string]: {
      uploaded: boolean;
      fileName?: string;
      rows?: number;
    };
  };
}

export function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const { workflowId } = useParameters();
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    demand: {},
    inventory: {},
    pricing: {},
  });

  // If no workflowId, don't render modal
  if (!workflowId) {
    return null;
  }

  const handleUploadSuccess = (
    agentType: string,
    fileType: string,
    fileName: string,
    rows: number
  ) => {
    setUploadStatus((prev) => ({
      ...prev,
      [agentType]: {
        ...prev[agentType],
        [fileType]: {
          uploaded: true,
          fileName,
          rows,
        },
      },
    }));
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
    // Error is already handled by UploadZone component
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Upload CSV Data Files</DialogTitle>
          <p className="text-sm text-gray-600 mt-2">
            Upload historical data for agents to process. All uploads are optional.
          </p>
        </DialogHeader>

        <Tabs defaultValue="demand" className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="demand" className="relative">
              Demand Agent
              {Object.values(uploadStatus.demand).some((s) => s.uploaded) && (
                <CheckCircle2 className="w-4 h-4 text-green-600 absolute -top-1 -right-1" />
              )}
            </TabsTrigger>
            <TabsTrigger value="inventory" className="relative">
              Inventory Agent
              {Object.values(uploadStatus.inventory).some((s) => s.uploaded) && (
                <CheckCircle2 className="w-4 h-4 text-green-600 absolute -top-1 -right-1" />
              )}
            </TabsTrigger>
            <TabsTrigger value="pricing" className="relative">
              Pricing Agent
              {Object.values(uploadStatus.pricing).some((s) => s.uploaded) && (
                <CheckCircle2 className="w-4 h-4 text-green-600 absolute -top-1 -right-1" />
              )}
            </TabsTrigger>
          </TabsList>

          {/* DEMAND AGENT TAB */}
          <TabsContent value="demand" className="space-y-4 mt-4">
            <UploadZone
              workflowId={workflowId}
              agentType="demand"
              fileType="sales_data"
              fileTypeLabel="Historical Sales Data (sales_data.csv)"
              onUploadSuccess={(fileName, rows) =>
                handleUploadSuccess('demand', 'sales_data', fileName, rows)
              }
              onUploadError={handleUploadError}
            />

            <UploadZone
              workflowId={workflowId}
              agentType="demand"
              fileType="store_profiles"
              fileTypeLabel="Store Profiles (store_profiles.csv)"
              onUploadSuccess={(fileName, rows) =>
                handleUploadSuccess('demand', 'store_profiles', fileName, rows)
              }
              onUploadError={handleUploadError}
            />

            {/* Upload Status Summary */}
            {Object.entries(uploadStatus.demand).some(([_, s]) => s.uploaded) && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm font-semibold text-green-900 mb-2">
                  Uploaded Files:
                </p>
                <ul className="text-xs text-green-800 space-y-1">
                  {Object.entries(uploadStatus.demand).map(([fileType, status]) =>
                    status.uploaded ? (
                      <li key={fileType}>
                        ✓ {status.fileName} ({status.rows} rows)
                      </li>
                    ) : null
                  )}
                </ul>
              </div>
            )}
          </TabsContent>

          {/* INVENTORY AGENT TAB */}
          <TabsContent value="inventory" className="space-y-4 mt-4">
            <UploadZone
              workflowId={workflowId}
              agentType="inventory"
              fileType="dc_inventory"
              fileTypeLabel="DC Inventory Levels (dc_inventory.csv)"
              onUploadSuccess={(fileName, rows) =>
                handleUploadSuccess('inventory', 'dc_inventory', fileName, rows)
              }
              onUploadError={handleUploadError}
            />

            <UploadZone
              workflowId={workflowId}
              agentType="inventory"
              fileType="lead_times"
              fileTypeLabel="Lead Times by Store (lead_times.csv)"
              onUploadSuccess={(fileName, rows) =>
                handleUploadSuccess('inventory', 'lead_times', fileName, rows)
              }
              onUploadError={handleUploadError}
            />

            <UploadZone
              workflowId={workflowId}
              agentType="inventory"
              fileType="safety_stock"
              fileTypeLabel="Safety Stock Policies (safety_stock.csv)"
              onUploadSuccess={(fileName, rows) =>
                handleUploadSuccess('inventory', 'safety_stock', fileName, rows)
              }
              onUploadError={handleUploadError}
            />

            {/* Upload Status Summary */}
            {Object.entries(uploadStatus.inventory).some(([_, s]) => s.uploaded) && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm font-semibold text-green-900 mb-2">
                  Uploaded Files:
                </p>
                <ul className="text-xs text-green-800 space-y-1">
                  {Object.entries(uploadStatus.inventory).map(([fileType, status]) =>
                    status.uploaded ? (
                      <li key={fileType}>
                        ✓ {status.fileName} ({status.rows} rows)
                      </li>
                    ) : null
                  )}
                </ul>
              </div>
            )}
          </TabsContent>

          {/* PRICING AGENT TAB */}
          <TabsContent value="pricing" className="space-y-4 mt-4">
            <UploadZone
              workflowId={workflowId}
              agentType="pricing"
              fileType="markdown_history"
              fileTypeLabel="Historical Markdown Data (markdown_history.csv)"
              onUploadSuccess={(fileName, rows) =>
                handleUploadSuccess('pricing', 'markdown_history', fileName, rows)
              }
              onUploadError={handleUploadError}
            />

            <UploadZone
              workflowId={workflowId}
              agentType="pricing"
              fileType="elasticity"
              fileTypeLabel="Price Elasticity Coefficients (elasticity.csv)"
              onUploadSuccess={(fileName, rows) =>
                handleUploadSuccess('pricing', 'elasticity', fileName, rows)
              }
              onUploadError={handleUploadError}
            />

            {/* Upload Status Summary */}
            {Object.entries(uploadStatus.pricing).some(([_, s]) => s.uploaded) && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm font-semibold text-green-900 mb-2">
                  Uploaded Files:
                </p>
                <ul className="text-xs text-green-800 space-y-1">
                  {Object.entries(uploadStatus.pricing).map(([fileType, status]) =>
                    status.uploaded ? (
                      <li key={fileType}>
                        ✓ {status.fileName} ({status.rows} rows)
                      </li>
                    ) : null
                  )}
                </ul>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
```

**Validation:**
- [ ] Modal reads workflowId from Context (no prop needed)
- [ ] Modal opens/closes correctly
- [ ] ESC key closes modal (focus trap works)
- [ ] Three tabs render (Demand, Inventory, Pricing)
- [ ] Tab navigation works with keyboard (Tab, Arrow keys)
- [ ] Each tab shows relevant UploadZone components
- [ ] Green checkmark appears on tab when file uploaded
- [ ] Upload status summary displays uploaded files
- [ ] Modal is scrollable if content exceeds viewport height

---

### Task 5: Integrate Upload Button into Dashboard

**Objective:** Add "Upload Data" button to dashboard below Agent Cards (Section 1).

**File:** `frontend/src/pages/Dashboard.tsx` (or equivalent)

**Implementation:**

```typescript
import React, { useState } from 'react';
import { useParameters } from '@/contexts/ParameterContext';
import { UploadModal } from '@/components/UploadModal';
import { Button } from '@/components/ui/button';
import { Upload } from 'lucide-react';

export function Dashboard() {
  const { workflowId } = useParameters();
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  return (
    <ParameterProvider>
      <div className="container mx-auto p-6 space-y-6">
        {/* Section 0: Parameter Gathering */}
        <ParameterGathering />

        {/* Section 1: Agent Cards */}
        <AgentCards />

        {/* Upload Data Button (only visible when workflowId exists) */}
        {workflowId && (
          <div className="flex justify-center">
            <Button
              onClick={() => setUploadModalOpen(true)}
              variant="outline"
              size="lg"
              className="gap-2"
              aria-label="Upload CSV data files for agents"
            >
              <Upload className="w-5 h-5" />
              Upload CSV Data (Optional)
            </Button>
          </div>
        )}

        {/* Remaining Sections... */}
        <ForecastSummary />
        <ClusterCards />
        <WeeklyPerformanceChart />
        <ReplenishmentQueue />
        <MarkdownDecision />
        <PerformanceMetrics />
      </div>

      {/* Upload Modal */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
      />
    </ParameterProvider>
  );
}
```

**Notes:**
- UploadModal reads workflowId from Context (no prop needed)
- Button only visible when workflowId exists
- All components use Context for data flow

**Validation:**
- [ ] "Upload Data" button appears below Section 1 (Agent Cards)
- [ ] Button only visible when workflowId exists in Context
- [ ] Clicking button opens UploadModal
- [ ] Modal closes correctly when user clicks outside or presses ESC
- [ ] Button has aria-label for accessibility

---

## Validation Checklist

### Backend Integration
- [ ] POST /api/workflows/{id}/demand/upload tested in Postman (6 test cases)
- [ ] Backend validates CSV headers and data types
- [ ] Backend returns descriptive validation errors (row, column, expected type)
- [ ] Backend handles file size limit (max 10MB)
- [ ] Backend handles wrong file extensions (.xlsx rejected)
- [ ] Multiple file upload works correctly

### Frontend Services
- [ ] UploadService created with uploadFile and uploadMultipleFiles
- [ ] File validation (size, extension) happens before upload
- [ ] FormData constructed correctly with file and file_type
- [ ] Error handling throws descriptive messages
- [ ] Utility methods (formatFileSize, downloadErrorReport) work

### Frontend Components
- [ ] UploadZone supports drag-and-drop
- [ ] UploadZone supports file picker (click to browse)
- [ ] Progress bar animates during upload
- [ ] Success state displays with file name and row count
- [ ] Error state displays validation errors in scrollable list
- [ ] "Download Error Report" generates .txt file
- [ ] UploadModal has 3 tabs (Demand, Inventory, Pricing)
- [ ] Green checkmark appears on tab when file uploaded
- [ ] Upload status summary shows uploaded files

### Dashboard Integration
- [ ] "Upload Data" button added below Agent Cards
- [ ] Button opens UploadModal
- [ ] Modal closes correctly

### Manual Testing
- [ ] Drag-and-drop file into UploadZone
- [ ] Click "Browse Files" to select file
- [ ] Upload valid CSV (success state displayed)
- [ ] Upload invalid CSV with missing column (error displayed)
- [ ] Upload invalid CSV with wrong data type (error displayed with row number)
- [ ] Upload file >10MB (rejected with error message)
- [ ] Upload .xlsx file (rejected with error message)
- [ ] Download error report as .txt file
- [ ] Upload multiple files in Demand Agent tab

---

## Definition of Done

- [ ] All 5 tasks completed and validated
- [ ] Backend upload endpoints tested in Postman (6 test cases passing)
- [ ] UploadService created with complete type definitions and validation
- [ ] Components use Context (workflowId from ParameterContext, not props)
- [ ] UploadZone component supports drag-and-drop and file picker
- [ ] UploadModal has 3 tabs with UploadZone components for each agent
- [ ] UploadModal reads workflowId from Context (no prop needed)
- [ ] "Upload Data" button integrated into Dashboard using Context
- [ ] Validation errors displayed with specific row/column details
- [ ] Error report download functionality works
- [ ] Accessibility requirements met:
  - [ ] Drag-and-drop zone has aria-label
  - [ ] Progress bar has role="progressbar" with aria-valuenow
  - [ ] Success/error messages have role="status" or role="alert"
  - [ ] Validation error list is keyboard navigable with aria-label
  - [ ] Modal has focus trap and ESC key support
  - [ ] Tab navigation works correctly
- [ ] Manual testing completed with all scenarios
- [ ] No console errors or warnings
- [ ] Code reviewed by team member

---

## Notes

### CSV Validation Rules

**Required Columns by File Type:**

1. **sales_data.csv:**
   - store_id (string)
   - week (integer)
   - sales_units (integer)
   - sales_revenue (float)
   - inventory_on_hand (integer)

2. **store_profiles.csv:**
   - store_id (string)
   - store_name (string)
   - region (string)
   - size_sqft (integer)
   - cluster_id (string)

3. **dc_inventory.csv:**
   - sku (string)
   - dc_location (string)
   - available_units (integer)
   - reserved_units (integer)

### File Size Limits

- Maximum file size: 10MB per file
- Maximum total upload size: 50MB (for multiple files)
- Estimated rows: ~100,000 rows per 10MB CSV file

### Error Message Examples

```
ERROR: Missing required column 'sales_units' in sales_data.csv

ERROR: Row 23, column 'sales_revenue': expected float, got 'N/A'

ERROR: File size exceeds maximum allowed size of 10MB

ERROR: Invalid file type. Only .csv files are accepted.

ERROR: CSV file is empty or contains only headers
```

---

## Related Stories

- **PHASE4-001:** Environment Configuration
- **PHASE4-002:** Section 0 - Parameter Gathering
- **PHASE4-003:** Section 1 - Agent Cards + WebSocket
- **PHASE4-006:** Sections 6-7 - Markdown Decision + Performance Metrics
- **PHASE4-008:** Integration Tests (next)
- **PHASE4-009:** Documentation & README Updates
