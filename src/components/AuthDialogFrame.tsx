import { useEffect, useRef, type KeyboardEvent, type ReactNode } from 'react';
import { XIcon, YarnLogo } from './Icons';
import './authDialog.css';

export default function AuthDialogFrame({ children, onClose }: { children: ReactNode; onClose: () => void }) {
  const frame = useRef<HTMLElement>(null);
  useEffect(() => {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    frame.current?.querySelector<HTMLElement>('[data-auth-close]')?.focus({ preventScroll: true });
    return () => { if (previous?.isConnected) previous.focus({ preventScroll: true }); };
  }, []);
  const keyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') { event.preventDefault(); onClose(); return; }
    if (event.key !== 'Tab') return;
    const items = frame.current?.querySelectorAll<HTMLElement>('button:not(:disabled), input:not(:disabled), a[href]');
    if (!items?.length) return;
    const first = items[0], last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus({ preventScroll: true }); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus({ preventScroll: true }); }
  };
  return <div className="auth-dialog-layer" role="dialog" aria-modal="true" aria-labelledby="sign-in-title" onKeyDown={keyDown}>
    <button type="button" tabIndex={-1} className="absolute inset-0 bg-[#2C1810]/55 backdrop-blur-sm" onClick={onClose} aria-label="Close sign in" />
    <section ref={frame} className="auth-dialog-frame rounded-[2rem] bg-white shadow-2xl">{children}</section>
  </div>;
}

export function AuthDialogHeader({ onClose, sent = false }: { onClose: () => void; sent?: boolean }) {
  return <div className="auth-dialog-header bg-[#FAF7F2] px-7 pb-6 pt-7 text-center">
    <button type="button" data-auth-close onClick={onClose} className="absolute right-5 top-5 rounded-full p-1.5 text-[#8B6B4A] hover:bg-[#F5EDE0]" aria-label="Close sign in"><XIcon size={20} /></button>
    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm"><YarnLogo size={32} /></div>
    <h2 id="sign-in-title" className="mt-4 text-3xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{sent ? 'Check your email' : 'Welcome to Sulocraft'}</h2>
    <p className="mt-2 text-sm leading-6 text-[#8B6B4A]">{sent ? 'Use the secure link we sent to continue.' : 'Sign in to save your favourites, addresses, and orders.'}</p>
  </div>;
}

export function AuthLoading({ onClose }: { onClose: () => void }) {
  return <AuthDialogFrame onClose={onClose}><AuthDialogHeader onClose={onClose} /><div className="auth-dialog-body px-7 py-6"><p role="status" className="py-8 text-center text-sm text-[#8B6B4A]">Loading sign-in…</p></div></AuthDialogFrame>;
}
