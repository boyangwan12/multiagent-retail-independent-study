import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbProps {
  items: { label: string; href?: string }[];
}

export const Breadcrumb = ({ items }: BreadcrumbProps) => {
  return (
    <nav className="flex items-center gap-2 text-sm text-text-secondary mb-4">
      <a
        href="/"
        className="flex items-center gap-1 hover:text-text-primary transition-colors"
      >
        <Home className="w-4 h-4" />
        <span>Home</span>
      </a>

      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          <ChevronRight className="w-4 h-4" />
          {item.href ? (
            <a
              href={item.href}
              className="hover:text-text-primary transition-colors"
            >
              {item.label}
            </a>
          ) : (
            <span className="text-text-primary font-medium">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
};
