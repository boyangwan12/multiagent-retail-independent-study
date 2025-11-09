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
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    switch (agentType) {
      case 'demand':
        return `${baseUrl}/api/v1/workflows/${workflowId}/demand/upload`;
      case 'inventory':
        return `${baseUrl}/api/v1/workflows/${workflowId}/inventory/upload`;
      case 'pricing':
        return `${baseUrl}/api/v1/workflows/${workflowId}/pricing/upload`;
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
