import { useState, useEffect } from 'react';
import { DASHBOARD_SECTIONS } from '../../types/navigation';

export const Sidebar = () => {
  const [activeSection, setActiveSection] = useState('parameters');

  useEffect(() => {
    // Intersection Observer to track which section is visible
    const observerOptions = {
      root: null,
      rootMargin: '-20% 0px -60% 0px',
      threshold: 0,
    };

    const observerCallback = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const sectionId = entry.target.id;
          setActiveSection(sectionId);
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    // Observe all sections
    DASHBOARD_SECTIONS.forEach((section) => {
      const element = document.getElementById(section.id);
      if (element) {
        observer.observe(element);
      }
    });

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const offset = 80; // Account for sticky header
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      });
    }
  };

  return (
    <aside
      className="fixed left-0 top-0 h-screen w-64 bg-card border-r border-border overflow-y-auto z-40"
      role="navigation"
      aria-label="Main navigation"
    >
      {/* Logo/Header */}
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-bold text-text-primary">
          Multi-Agent Retail
        </h1>
        <p className="text-xs text-text-secondary mt-1">
          Forecasting Dashboard
        </p>
      </div>

      {/* Navigation */}
      <nav className="p-4" aria-label="Dashboard sections">
        <div className="space-y-1" role="list">
          {DASHBOARD_SECTIONS.map((section) => (
            <button
              key={section.id}
              onClick={() => scrollToSection(section.id)}
              aria-label={`Navigate to ${section.label}`}
              aria-current={activeSection === section.id ? 'page' : undefined}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left
                transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary
                ${
                  activeSection === section.id
                    ? 'bg-primary/10 text-primary border-l-2 border-primary'
                    : 'text-text-secondary hover:bg-muted hover:text-text-primary'
                }
              `}
            >
              <span className="text-lg" aria-hidden="true">{section.icon}</span>
              <span className="text-sm font-medium">{section.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border bg-card">
        <div className="text-xs text-text-secondary">
          <div className="mb-1">Phase 2 - Frontend MVP</div>
          <div className="font-mono">v1.0.0</div>
        </div>
      </div>
    </aside>
  );
};
