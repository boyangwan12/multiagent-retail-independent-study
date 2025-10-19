import { Calendar, Package, TrendingUp, Percent, Tag } from 'lucide-react';
import type { ReactNode } from 'react';

interface ParameterCardProps {
  name: string;
  value: string | number;
  icon?: 'calendar' | 'package' | 'trending' | 'percent' | 'tag';
  tooltip?: string;
}

const iconMap: Record<string, ReactNode> = {
  calendar: <Calendar className="w-5 h-5" />,
  package: <Package className="w-5 h-5" />,
  trending: <TrendingUp className="w-5 h-5" />,
  percent: <Percent className="w-5 h-5" />,
  tag: <Tag className="w-5 h-5" />,
};

export function ParameterCard({
  name,
  value,
  icon = 'tag',
  tooltip,
}: ParameterCardProps) {
  return (
    <div
      className="relative p-4 bg-card border border-border rounded-lg hover:border-primary transition-colors group"
      title={tooltip}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-muted rounded-lg text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
          {iconMap[icon]}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-text-secondary mb-1">{name}</p>
          <p className="text-lg font-semibold text-text-primary truncate">
            {value}
          </p>
        </div>
      </div>

      {tooltip && (
        <div className="absolute invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-opacity bg-card border border-border rounded-lg shadow-lg p-3 text-sm text-text-secondary bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 z-10">
          {tooltip}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1 border-4 border-transparent border-t-border"></div>
        </div>
      )}
    </div>
  );
}
