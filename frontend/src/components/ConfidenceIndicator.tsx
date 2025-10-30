import type { MarkdownConfidence } from '@/types';

interface ConfidenceIndicatorProps {
  confidence: MarkdownConfidence;
}

export function ConfidenceIndicator({ confidence }: ConfidenceIndicatorProps) {
  const getStyles = () => {
    switch (confidence) {
      case 'High':
        return {
          container: 'bg-green-500/10 border-green-500/20',
          dot: 'bg-green-500',
          text: 'text-green-400',
        };
      case 'Medium':
        return {
          container: 'bg-yellow-500/10 border-yellow-500/20',
          dot: 'bg-yellow-500',
          text: 'text-yellow-400',
        };
      case 'Low':
        return {
          container: 'bg-red-500/10 border-red-500/20',
          dot: 'bg-red-500',
          text: 'text-red-400',
        };
    }
  };

  const styles = getStyles();

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${styles.container}`}>
      <div className="flex items-center gap-1.5">
        <div className={`w-2 h-2 rounded-full ${styles.dot} animate-pulse`} />
        <span className={`text-sm font-medium ${styles.text}`}>
          {confidence} Confidence
        </span>
      </div>
    </div>
  );
}
