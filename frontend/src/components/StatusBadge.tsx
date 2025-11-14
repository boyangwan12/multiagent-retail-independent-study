interface StatusBadgeProps {
  status: 'Active' | 'Warning' | 'Low Stock';
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const getStyles = () => {
    switch (status) {
      case 'Active':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'Warning':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'Low Stock':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
    }
  };

  return (
    <span
      className={`px-2 py-1 text-xs font-medium rounded-md border transition-all duration-300 ${getStyles()}`}
    >
      {status}
    </span>
  );
}
