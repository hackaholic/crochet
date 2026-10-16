import type { AnchorHTMLAttributes, MouseEvent } from 'react';

export function safeDestination(href: string): boolean {
  if (!href || /[\u0000-\u0020\\]/.test(href) || href.startsWith('//')) return false;
  if (href.startsWith('/')) return true;
  try { const url = new URL(href); return ['http:', 'https:'].includes(url.protocol) && !url.username && !url.password; }
  catch { return false; }
}

/** Native href remains available to crawlers, keyboard and new-tab actions. */
export default function DestinationLink({ href, onNavigate, children, ...props }: Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'onClick'> & { href: string; onNavigate?: () => void }) {
  if (!safeDestination(href)) return <span className={props.className} aria-disabled="true">{children}</span>;
  const click = (event: MouseEvent<HTMLAnchorElement>) => {
    if (!onNavigate || !href.startsWith('/') || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || props.target === '_blank' || props.download !== undefined) return;
    event.preventDefault();
    onNavigate();
  };
  return <a {...props} href={href} onClick={click}>{children}</a>;
}
