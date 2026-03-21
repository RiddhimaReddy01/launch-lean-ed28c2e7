import { useEffect, useRef, useCallback } from 'react';

export function useScrollReveal(staggerMs = 0) {
  const ref = useRef<HTMLDivElement>(null);

  const observe = useCallback(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            el.classList.add('visible');
          }, staggerMs);
          observer.unobserve(el);
        }
      },
      { threshold: 0.2 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [staggerMs]);

  useEffect(() => {
    return observe();
  }, [observe]);

  return ref;
}
