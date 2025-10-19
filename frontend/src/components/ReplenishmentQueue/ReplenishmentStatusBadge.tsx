import type { ReplenishmentStatus } from '@/types/replenishment';

interface ReplenishmentStatusBadgeProps {
  status: ReplenishmentStatus;
}

export function ReplenishmentStatusBadge({ status }: ReplenishmentStatusBadgeProps) {
  const getStyles = () => {
    switch (status) {
      case 'Pending':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
      case 'In Progress':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'Approved':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'Rejected':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
    }
  };

  return (
    <span
      className={`px-2 py-1 text-xs font-medium rounded-md border ${getStyles()}`}
    >
      {status}
    </span>
  );
}
