import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Breadcrumb } from './Breadcrumb';
import { MobileWarning } from '../MobileWarning';

interface AppLayoutProps {
  children: ReactNode;
  breadcrumbs?: { label: string; href?: string }[];
  showSidebar?: boolean;
}

export const AppLayout = ({
  children,
  breadcrumbs = [{ label: 'Dashboard' }],
  showSidebar = true,
}: AppLayoutProps) => {
  useEffect(() => {
    // Keyboard shortcuts
    const handleKeyPress = (e: KeyboardEvent) => {
      // Alt/Option + number (1-8) to navigate to sections
      if (e.altKey && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
        const num = parseInt(e.key);
        if (num >= 1 && num <= 8) {
          e.preventDefault();
          const sections = [
            'parameters',
            'agents',
            'forecast',
            'clusters',
            'weekly',
            'replenishment',
            'markdown',
            'performance',
          ];
          const sectionId = sections[num - 1];
          const element = document.getElementById(sectionId);
          if (element) {
            const offset = 80;
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;
            window.scrollTo({
              top: offsetPosition,
              behavior: 'smooth',
            });
          }
        }
      }

      // Alt + H to scroll to top (Home)
      if (e.altKey && e.key === 'h') {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <MobileWarning />
      {showSidebar && <Sidebar />}

      <main className={showSidebar ? 'ml-64' : ''}>
        <div className="container mx-auto px-6 py-6">
          {breadcrumbs && breadcrumbs.length > 0 && (
            <Breadcrumb items={breadcrumbs} />
          )}
          {children}
        </div>
      </main>

      {/* Keyboard shortcuts hint (optional, shows on first load) */}
      <div className="fixed bottom-4 right-4 bg-card border border-border rounded-lg p-3 text-xs text-text-secondary shadow-lg hidden md:block">
        <div className="font-semibold text-text-primary mb-2">
          Keyboard Shortcuts
        </div>
        <div className="space-y-1">
          <div>
            <kbd className="px-2 py-1 bg-muted rounded text-xs mr-1">Alt</kbd>
            <kbd className="px-2 py-1 bg-muted rounded text-xs">1-8</kbd>
            <span className="ml-2">Jump to section</span>
          </div>
          <div>
            <kbd className="px-2 py-1 bg-muted rounded text-xs mr-1">Alt</kbd>
            <kbd className="px-2 py-1 bg-muted rounded text-xs">H</kbd>
            <span className="ml-2">Scroll to top</span>
          </div>
        </div>
      </div>
    </div>
  );
};
