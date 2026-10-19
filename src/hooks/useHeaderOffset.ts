import { useEffect, type RefObject } from 'react';

/** Share persistent fixed-header height without counting its expanded menu. */
export function useHeaderOffset(header: RefObject<HTMLElement | null>, menu: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const element = header.current;
    if (!element) return;
    const style = document.documentElement.style;
    const property = '--storefront-header-height';
    const previous = style.getPropertyValue(property);
    const measure = () => {
      const height = Math.ceil(element.getBoundingClientRect().height - (menu.current?.getBoundingClientRect().height ?? 0));
      if (height > 0) style.setProperty(property, `${height}px`);
    };
    measure();
    const observer = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(measure) : undefined;
    observer?.observe(element);
    window.addEventListener('resize', measure);
    return () => {
      observer?.disconnect();
      window.removeEventListener('resize', measure);
      if (previous) style.setProperty(property, previous);
      else style.removeProperty(property);
    };
  }, [header, menu]);
}
