/**
 * Custom hook to track active section using Intersection Observer.
 *
 * Watches section elements as they enter/exit the viewport and returns
 * the ID of the currently visible section.
 */
import { useEffect, useState, useRef } from 'react';

interface UseActiveSectionOptions {
  /** Root margin for intersection observer (default: '-20% 0px -35% 0px') */
  rootMargin?: string;
  /** Threshold for intersection (default: 0) */
  threshold?: number | number[];
}

export const useActiveSection = (
  sectionIds: string[],
  options: UseActiveSectionOptions = {}
): string | null => {
  const [activeId, setActiveId] = useState<string | null>(null);
  const observer = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const {
      rootMargin = '-20% 0px -35% 0px',
      threshold = 0,
    } = options;

    // Cleanup previous observer
    if (observer.current) {
      observer.current.disconnect();
    }

    // Track which sections are currently intersecting
    const intersectingSections = new Map<string, IntersectionObserverEntry>();

    observer.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const sectionId = entry.target.getAttribute('data-section-id');
          if (!sectionId) return;

          if (entry.isIntersecting) {
            intersectingSections.set(sectionId, entry);
          } else {
            intersectingSections.delete(sectionId);
          }
        });

        // Find the section with the highest intersection ratio
        // or the topmost one if multiple sections are visible
        if (intersectingSections.size > 0) {
          const topSection = Array.from(intersectingSections.entries())
            .sort((a, b) => {
              // Sort by intersection ratio (descending)
              const ratioA = a[1].intersectionRatio;
              const ratioB = b[1].intersectionRatio;
              if (ratioA !== ratioB) {
                return ratioB - ratioA;
              }
              // If equal, sort by position (ascending)
              return a[1].boundingClientRect.top - b[1].boundingClientRect.top;
            })[0];

          setActiveId(topSection[0]);
        } else {
          setActiveId(null);
        }
      },
      {
        rootMargin,
        threshold,
      }
    );

    // Observe all section elements
    sectionIds.forEach((id) => {
      const element = document.querySelector(`[data-section-id="${id}"]`);
      if (element && observer.current) {
        observer.current.observe(element);
      }
    });

    // Cleanup
    return () => {
      if (observer.current) {
        observer.current.disconnect();
      }
    };
  }, [sectionIds, options.rootMargin, options.threshold]);

  return activeId;
};
