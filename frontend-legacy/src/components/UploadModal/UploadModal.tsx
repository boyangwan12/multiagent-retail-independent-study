import React, { useState } from 'react';
import { useParameters } from '@/contexts/ParametersContext';
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
}
