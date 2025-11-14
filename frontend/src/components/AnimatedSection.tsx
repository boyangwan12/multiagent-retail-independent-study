import type { ReactNode } from 'react';
import { useInViewAnimation } from '@/hooks/useInViewAnimation';

interface AnimatedSectionProps {
  id: string;
  children: ReactNode;
  className?: string;
  delay?: number;
}

/**
 * AnimatedSection Component
 *
 * Wraps dashboard sections with fade-in-up animation when they enter viewport.
 * Uses Intersection Observer API for performant scroll detection.
 *
 * @component
 * @example
 * ```tsx
 * <AnimatedSection id="forecast" className="mb-12">
 *   <ForecastSummary />
 * </AnimatedSection>
 * ```
 */
export function AnimatedSection({
  id,
  children,
  className = '',
  delay = 0,
}: AnimatedSectionProps) {
  const { ref, isInView } = useInViewAnimation<HTMLElement>({
    threshold: 0.1,
    triggerOnce: true,
  });

  return (
    <section
      id={id}
      ref={ref}
      className={`${className} ${
        isInView ? 'animate-fade-in-up' : 'opacity-0'
      }`}
      style={{
        animationDelay: `${delay}ms`,
      }}
    >
      {children}
    </section>
  );
}
