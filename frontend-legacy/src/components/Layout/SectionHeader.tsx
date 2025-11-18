interface SectionHeaderProps {
  id: string;
  title: string;
  description?: string;
  icon?: string;
}

export const SectionHeader = ({
  id,
  title,
  description,
  icon,
}: SectionHeaderProps) => {
  return (
    <div
      id={id}
      className="sticky top-0 z-30 bg-background/95 backdrop-blur-sm border-b border-border mb-6 py-4"
    >
      <div className="flex items-center gap-3">
        {icon && <span className="text-2xl">{icon}</span>}
        <div>
          <h2 className="text-2xl font-bold text-text-primary">{title}</h2>
          {description && (
            <p className="text-sm text-text-secondary mt-1">{description}</p>
          )}
        </div>
      </div>
    </div>
  );
};
