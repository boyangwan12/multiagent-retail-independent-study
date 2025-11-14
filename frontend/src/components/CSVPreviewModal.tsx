import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { FileText, AlertCircle } from 'lucide-react';
import type { ValidationResult } from '@/utils/csv-validator';

interface CSVPreviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  validationResult: ValidationResult | null;
  fileName?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isUploading?: boolean;
}

/**
 * CSVPreviewModal Component
 *
 * Displays a preview of CSV file contents before upload, including:
 * - First 10 rows in table format
 * - Row and column counts
 * - Validation errors and warnings
 * - Confirm/Cancel actions
 *
 * @component
 * @example
 * ```tsx
 * <CSVPreviewModal
 *   open={isOpen}
 *   onOpenChange={setIsOpen}
 *   validationResult={result}
 *   fileName="forecast_data.csv"
 *   onConfirm={handleUpload}
 *   onCancel={handleCancel}
 * />
 * ```
 */
export function CSVPreviewModal({
  open,
  onOpenChange,
  validationResult,
  fileName,
  onConfirm,
  onCancel,
  isUploading = false,
}: CSVPreviewModalProps) {
  if (!validationResult) return null;

  const { preview, rowCount, columnCount, errors, warnings, valid } = validationResult;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            CSV Preview
          </DialogTitle>
          <DialogDescription>
            Review your data before uploading{fileName && `: ${fileName}`}
          </DialogDescription>
        </DialogHeader>

        {/* File Stats */}
        <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
          <div>
            <p className="text-xs text-text-secondary uppercase tracking-wide">Rows</p>
            <p className="text-2xl font-bold text-text-primary">{rowCount}</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary uppercase tracking-wide">Columns</p>
            <p className="text-2xl font-bold text-text-primary">{columnCount}</p>
          </div>
          <div>
            <p className="text-xs text-text-secondary uppercase tracking-wide">Status</p>
            <p className={`text-2xl font-bold ${valid ? 'text-success' : 'text-error'}`}>
              {valid ? 'Valid' : 'Invalid'}
            </p>
          </div>
        </div>

        {/* Errors */}
        {errors.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-error flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Errors ({errors.length})
            </h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {errors.map((error, index) => (
                <div
                  key={index}
                  className="text-xs p-2 bg-error/10 border border-error/20 rounded text-error"
                >
                  {error.row && <span className="font-medium">Row {error.row}: </span>}
                  {error.column && <span className="font-medium">{error.column} - </span>}
                  {error.message}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Warnings */}
        {warnings.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-warning flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Warnings ({warnings.length})
            </h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {warnings.map((warning, index) => (
                <div
                  key={index}
                  className="text-xs p-2 bg-warning/10 border border-warning/20 rounded text-warning"
                >
                  {warning.row && <span className="font-medium">Row {warning.row}: </span>}
                  {warning.column && <span className="font-medium">{warning.column} - </span>}
                  {warning.message}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Preview Table */}
        <div>
          <h4 className="text-sm font-semibold text-text-primary mb-2">
            Preview (First {Math.min(preview.length - 1, 10)} rows)
          </h4>
          <div className="overflow-x-auto border border-border rounded-lg">
            <table className="w-full text-xs">
              <thead className="bg-muted">
                <tr>
                  {preview[0]?.map((header, index) => (
                    <th
                      key={index}
                      className="px-3 py-2 text-left font-semibold text-text-primary border-b border-border"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.slice(1).map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className="border-b border-border hover:bg-muted/50 transition-colors"
                  >
                    {row.map((cell, cellIndex) => (
                      <td
                        key={cellIndex}
                        className="px-3 py-2 text-text-secondary"
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {preview.length > 11 && (
            <p className="text-xs text-text-secondary mt-2 text-center">
              ... and {rowCount - 10} more rows
            </p>
          )}
        </div>

        <DialogFooter className="flex gap-2">
          <Button
            variant="outline"
            onClick={onCancel}
            disabled={isUploading}
          >
            Cancel
          </Button>
          <Button
            onClick={onConfirm}
            disabled={!valid || isUploading}
            loading={isUploading}
          >
            {valid ? 'Upload File' : 'Cannot Upload (Fix Errors)'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
