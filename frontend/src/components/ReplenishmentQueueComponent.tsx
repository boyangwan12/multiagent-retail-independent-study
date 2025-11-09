import React, { useEffect, useState } from 'react';
import { AllocationService } from '@/services/allocation-service';
import { ApprovalService } from '@/services/approval-service';
import { useParameters } from '@/contexts/ParametersContext';
import { getCurrentWeekNumber } from '@/utils/date-utils';
import { AlertCircle, Loader2, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import type { AllocationPlan, WeeklyReplenishment } from '@/types/allocation';

export function ReplenishmentQueueComponent() {
  const { forecastId, parameters, workflowComplete } = useParameters();
  const [allocation, setAllocation] = useState<AllocationPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isApprovingShipments, setIsApprovingShipments] = useState(false);
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);

  // Calculate current week from season_start_date
  const currentWeek = parameters?.season_start_date
    ? getCurrentWeekNumber(parameters.season_start_date)
    : 1;

  // Handle approval button click
  const handleApproveShipments = async () => {
    if (!forecastId) return;

    setIsApprovingShipments(true);
    setApprovalSuccess(null);
    setError(null);

    try {
      // Use ApprovalService to approve replenishment
      await ApprovalService.approveReplenishment({
        forecast_id: forecastId,
        week_number: currentWeek,
      });

      setApprovalSuccess(`Week ${currentWeek} shipments approved successfully`);
    } catch (err: any) {
      console.error('Failed to approve shipments:', err);

      let errorMessage = 'Failed to approve shipments';
      if (err.status === 404) {
        errorMessage = 'Replenishment plan not found.';
      } else if (err.status === 500) {
        errorMessage = 'Server error approving shipments.';
      } else if (err.status === 0 || !err.status) {
        errorMessage = 'Cannot connect to backend.';
      }

      setError(errorMessage);
    } finally {
      setIsApprovingShipments(false);
    }
  };

  useEffect(() => {
    // Wait for workflow completion and validate parameters
    if (!workflowComplete || !forecastId || !parameters) return;

    const fetchAllocation = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await AllocationService.getAllocation(forecastId);

        // Validate replenishment strategy matches parameters
        if (
          parameters &&
          data.replenishment_strategy !== parameters.replenishment_strategy
        ) {
          console.warn(
            `Replenishment strategy mismatch: expected ${parameters.replenishment_strategy}, got ${data.replenishment_strategy}`
          );
        }

        setAllocation(data);
      } catch (err: any) {
        console.error('Failed to fetch allocation:', err);

        // Handle specific error types
        let errorMessage = 'Failed to load replenishment data';
        if (err.status === 404) {
          errorMessage = 'Allocation data not found. Workflow may not have completed.';
        } else if (err.status === 500) {
          errorMessage = 'Server error loading allocation data.';
        } else if (err.status === 0 || !err.status) {
          errorMessage = 'Cannot connect to backend.';
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllocation();
  }, [workflowComplete, forecastId, parameters]);

  if (!forecastId) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-gray-500">
            Complete workflow to view replenishment queue
          </p>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="flex items-center justify-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            <p>Loading replenishment data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !allocation) {
    return (
      <Card>
        <CardContent className="pt-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || 'No replenishment data'}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Handle "none" replenishment strategy
  if (allocation.replenishment_strategy === 'none') {
    return (
      <Card>
        <CardContent className="py-8">
          <Alert>
            <Info className="h-4 w-4" />
            <AlertTitle>No Replenishment</AlertTitle>
            <AlertDescription>
              All {allocation.manufacturing_order.toLocaleString()} units were allocated to stores at Week 0.
              No replenishment shipments planned.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Get current week's shipments
  const currentWeekShipments = allocation.replenishment_plan.find(
    (plan) => plan.week_number === currentWeek
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Replenishment Queue - Week {currentWeek}</CardTitle>
        <p className="text-sm text-gray-600">
          Strategy: {allocation.replenishment_strategy} • DC Remaining: {currentWeekShipments?.dc_remaining.toLocaleString() || 0} units
        </p>
      </CardHeader>
      <CardContent>
        {/* Approval Success Message */}
        {approvalSuccess && (
          <Alert variant="success" className="mb-4" role="status">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>{approvalSuccess}</AlertDescription>
          </Alert>
        )}

        {/* DC Inventory Warnings */}
        {allocation.dc_inventory_warnings.length > 0 && (
          <Alert variant="warning" className="mb-4" role="alert">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>DC Inventory Warning</AlertTitle>
            <AlertDescription>
              {allocation.dc_inventory_warnings[0].message}
            </AlertDescription>
          </Alert>
        )}

        {/* Current Week Shipments */}
        {currentWeekShipments ? (
          <>
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                Total to ship: <span className="font-semibold">{currentWeekShipments.total_shipped.toLocaleString()}</span> units to{' '}
                <span className="font-semibold">{currentWeekShipments.shipments.length}</span> stores
              </p>
            </div>

            <div className="max-h-96 overflow-y-auto mb-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="px-4 py-3 text-left text-gray-600 font-medium">Store ID</th>
                    <th className="px-4 py-3 text-right text-gray-600 font-medium">Quantity</th>
                    <th className="px-4 py-3 text-left text-gray-600 font-medium">Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {currentWeekShipments.shipments.map((shipment) => (
                    <tr key={shipment.store_id} className="border-b border-gray-100">
                      <td className="px-4 py-3 font-medium">{shipment.store_id}</td>
                      <td className="px-4 py-3 text-right">{shipment.quantity.toLocaleString()}</td>
                      <td className="px-4 py-3">
                        <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                          {shipment.reason.replace(/_/g, ' ')}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4">
              <Button
                onClick={handleApproveShipments}
                disabled={isApprovingShipments}
                aria-label={`Approve ${currentWeekShipments.total_shipped} units for Week ${currentWeek}`}
              >
                {isApprovingShipments ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Approving...
                  </>
                ) : (
                  'Approve Shipments'
                )}
              </Button>
            </div>
          </>
        ) : (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              No shipments scheduled for Week {currentWeek}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
