export interface NavigationSection {
  id: string;
  label: string;
  icon?: string;
  href: string;
}

export const DASHBOARD_SECTIONS: NavigationSection[] = [
  {
    id: 'parameters',
    label: 'Parameters',
    icon: '⚙️',
    href: '#parameters',
  },
  {
    id: 'agents',
    label: 'Agent Workflow',
    icon: '🤖',
    href: '#agents',
  },
  {
    id: 'forecast',
    label: 'Forecast Summary',
    icon: '📊',
    href: '#forecast',
  },
  {
    id: 'clusters',
    label: 'Cluster Distribution',
    icon: '🏪',
    href: '#clusters',
  },
  {
    id: 'weekly',
    label: 'Weekly Performance',
    icon: '📈',
    href: '#weekly',
  },
  {
    id: 'replenishment',
    label: 'Replenishment Queue',
    icon: '📦',
    href: '#replenishment',
  },
  {
    id: 'markdown',
    label: 'Markdown Decision',
    icon: '💰',
    href: '#markdown',
  },
  {
    id: 'performance',
    label: 'Performance Metrics',
    icon: '🎯',
    href: '#performance',
  },
];
