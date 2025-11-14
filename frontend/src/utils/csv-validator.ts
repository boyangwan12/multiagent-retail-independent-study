/**
 * CSV Validation Utility
 *
 * Provides real-time validation for CSV files with detailed error messages.
 */

export interface ValidationError {
  row?: number;
  column?: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  rowCount: number;
  columnCount: number;
  preview: string[][];
}

export interface CSVValidationSchema {
  requiredColumns: string[];
  optionalColumns?: string[];
  validators?: {
    [column: string]: (value: string, row: number) => string | null;
  };
  maxRows?: number;
  maxFileSize?: number; // in bytes
}

/**
 * Parse CSV content into 2D array
 */
export function parseCSV(content: string): string[][] {
  const lines = content.trim().split('\n');
  return lines.map(line => {
    // Simple CSV parser (doesn't handle quoted commas)
    // For production, consider using a library like PapaParse
    return line.split(',').map(cell => cell.trim());
  });
}

/**
 * Validate CSV file against a schema
 *
 * @param file - CSV file to validate
 * @param schema - Validation schema
 * @returns Promise resolving to validation result
 *
 * @example
 * ```typescript
 * const result = await validateCSV(file, {
 *   requiredColumns: ['week_number', 'demand_units'],
 *   validators: {
 *     week_number: (value) => {
 *       const num = parseInt(value);
 *       if (isNaN(num) || num < 1 || num > 52) {
 *         return 'Week number must be between 1 and 52';
 *       }
 *       return null;
 *     }
 *   }
 * });
 * ```
 */
export async function validateCSV(
  file: File,
  schema: CSVValidationSchema
): Promise<ValidationResult> {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Validate file type
  if (!file.name.endsWith('.csv')) {
    errors.push({
      message: 'File must be a CSV file (.csv extension)',
      severity: 'error',
    });
    return {
      valid: false,
      errors,
      warnings,
      rowCount: 0,
      columnCount: 0,
      preview: [],
    };
  }

  // Validate file size
  if (schema.maxFileSize && file.size > schema.maxFileSize) {
    errors.push({
      message: `File size (${formatFileSize(file.size)}) exceeds maximum allowed (${formatFileSize(schema.maxFileSize)})`,
      severity: 'error',
    });
  }

  // Read file content
  const content = await file.text();
  const rows = parseCSV(content);

  if (rows.length === 0) {
    errors.push({
      message: 'CSV file is empty',
      severity: 'error',
    });
    return {
      valid: false,
      errors,
      warnings,
      rowCount: 0,
      columnCount: 0,
      preview: [],
    };
  }

  // Validate header row
  const headers = rows[0];
  const columnCount = headers.length;

  // Check required columns
  const missingColumns = schema.requiredColumns.filter(
    col => !headers.includes(col)
  );

  if (missingColumns.length > 0) {
    errors.push({
      message: `Missing required columns: ${missingColumns.join(', ')}`,
      severity: 'error',
    });
  }

  // Check for duplicate columns
  const duplicates = headers.filter(
    (col, index) => headers.indexOf(col) !== index
  );
  if (duplicates.length > 0) {
    warnings.push({
      message: `Duplicate column names found: ${[...new Set(duplicates)].join(', ')}`,
      severity: 'warning',
    });
  }

  // Validate data rows
  const dataRows = rows.slice(1);
  const rowCount = dataRows.length;

  if (schema.maxRows && rowCount > schema.maxRows) {
    warnings.push({
      message: `File contains ${rowCount} rows, exceeding recommended maximum of ${schema.maxRows}`,
      severity: 'warning',
    });
  }

  // Validate each data row
  dataRows.forEach((row, rowIndex) => {
    const actualRowNumber = rowIndex + 2; // +2 because: 0-indexed + header row

    // Check row length
    if (row.length !== columnCount) {
      errors.push({
        row: actualRowNumber,
        message: `Row has ${row.length} columns, expected ${columnCount}`,
        severity: 'error',
      });
      return;
    }

    // Run custom validators
    if (schema.validators) {
      headers.forEach((column, colIndex) => {
        const validator = schema.validators![column];
        if (validator) {
          const value = row[colIndex];
          const error = validator(value, actualRowNumber);
          if (error) {
            errors.push({
              row: actualRowNumber,
              column,
              message: error,
              severity: 'error',
            });
          }
        }
      });
    }

    // Check for empty required values
    schema.requiredColumns.forEach(column => {
      const colIndex = headers.indexOf(column);
      if (colIndex !== -1 && !row[colIndex]) {
        errors.push({
          row: actualRowNumber,
          column,
          message: `Required field '${column}' is empty`,
          severity: 'error',
        });
      }
    });
  });

  // Create preview (first 10 rows)
  const preview = rows.slice(0, 10);

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    rowCount,
    columnCount,
    preview,
  };
}

/**
 * Format file size for display
 */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Common validators for CSV data
 */
export const validators = {
  /**
   * Validate positive integer
   */
  positiveInteger: (fieldName: string) => (value: string, row: number) => {
    const num = parseInt(value);
    if (isNaN(num)) {
      return `${fieldName} must be a number`;
    }
    if (num < 0) {
      return `${fieldName} must be positive`;
    }
    if (!Number.isInteger(num)) {
      return `${fieldName} must be an integer`;
    }
    return null;
  },

  /**
   * Validate date in YYYY-MM-DD format
   */
  isoDate: (fieldName: string) => (value: string, row: number) => {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(value)) {
      return `${fieldName} must be in YYYY-MM-DD format`;
    }
    const date = new Date(value);
    if (isNaN(date.getTime())) {
      return `${fieldName} is not a valid date`;
    }
    return null;
  },

  /**
   * Validate number within range
   */
  numberInRange: (fieldName: string, min: number, max: number) => (value: string, row: number) => {
    const num = parseFloat(value);
    if (isNaN(num)) {
      return `${fieldName} must be a number`;
    }
    if (num < min || num > max) {
      return `${fieldName} must be between ${min} and ${max}`;
    }
    return null;
  },

  /**
   * Validate non-empty string
   */
  required: (fieldName: string) => (value: string, row: number) => {
    if (!value || value.trim() === '') {
      return `${fieldName} is required`;
    }
    return null;
  },
};
