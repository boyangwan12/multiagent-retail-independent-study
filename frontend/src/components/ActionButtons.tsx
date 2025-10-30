import { Check, X } from 'lucide-react';
import type { ReplenishmentStatus } from '@/types';

interface ActionButtonsProps {
  itemId: string;
  status: ReplenishmentStatus;
  onApprove: (itemId: string) => void;
  onReject: (itemId: string) => void;
}

export function ActionButtons({ itemId, status, onApprove, onReject }: ActionButtonsProps) {
  // Only show action buttons for Pending items
  if (status !== 'Pending') {
    return <span className="text-xs text-text-secondary">-</span>;
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => onApprove(itemId)}
        className="p-1.5 bg-green-500/10 hover:bg-green-500/20 border border-green-500/20 rounded text-green-400 transition-colors"
        title="Approve"
      >
        <Check className="h-4 w-4" />
      </button>
      <button
        onClick={() => onReject(itemId)}
        className="p-1.5 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded text-red-400 transition-colors"
        title="Reject"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
