interface ConfidenceBarProps {
  confidence: number; // 0-100
}

export function ConfidenceBar({ confidence }: ConfidenceBarProps) {
  // Determine color based on confidence level
  const getColor = () => {
    if (confidence >= 85) return 'bg-green-500';
    if (confidence >= 75) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getTextColor = () => {
    if (confidence >= 85) return 'text-green-400';
    if (confidence >= 75) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="flex-1 h-2 bg-card-hover rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor()} transition-all duration-300`}
          style={{ width: `${confidence}%` }}
        />
      </div>
      <span className={`text-sm font-medium ${getTextColor()} min-w-[40px] text-right`}>
        {confidence}%
      </span>
    </div>
  );
}
