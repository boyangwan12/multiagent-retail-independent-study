import type { ReplenishmentUrgency } from '@/types/replenishment';

interface UrgencyBadgeProps {
  urgency: ReplenishmentUrgency;
}

export function UrgencyBadge({ urgency }: UrgencyBadgeProps) {
  const getStyles = () => {
    switch (urgency) {
      case 'High':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'Medium':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'Low':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
    }
  };

  return (
    <span
      className={`px-2 py-1 text-xs font-medium rounded-md border ${getStyles()}`}
    >
      {urgency}
    </span>
  );
}
