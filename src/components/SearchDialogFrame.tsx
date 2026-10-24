import { useEffect, useRef, type KeyboardEventHandler, type ReactNode, type Ref } from 'react';
import { SearchIcon, XIcon } from './Icons';
import './searchDialog.css';

interface Props {
  children: ReactNode;
  onClose: () => void;
  dialogRef?: Ref<HTMLDivElement>;
  onKeyDown?: KeyboardEventHandler<HTMLDivElement>;
}

/** Eagerly shared by the lazy-loading placeholder and the live search dialog. */
export default function SearchDialogFrame({ children, onClose, dialogRef, onKeyDown }: Props) {
  return <div className="search-dialog-layer" role="dialog" aria-modal="true" aria-label="Search products"
    onKeyDown={onKeyDown ?? (event => { if (event.key === 'Escape') onClose(); })}>
    <button type="button" tabIndex={-1} aria-label="Close search" className="absolute inset-0 h-full w-full cursor-default bg-black/50 backdrop-blur-sm" onClick={onClose} />
    <div ref={dialogRef} className="search-dialog-frame bg-white rounded-2xl shadow-2xl">{children}</div>
  </div>;
}

export function SearchLoading({ onClose }: { onClose: () => void }) {
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    closeRef.current?.focus({ preventScroll: true });
    return () => { if (previous?.isConnected) previous.focus({ preventScroll: true }); };
  }, []);
  return <SearchDialogFrame onClose={onClose}>
    <div className="search-dialog-header flex items-center gap-3 border-b border-[#EDE4D0] px-4 py-4 sm:px-6">
      <SearchIcon size={22} className="shrink-0 text-[#8B6B4A]" />
      <div className="min-w-0 flex-1 text-sm text-[#806F61]">Search products</div>
      <button ref={closeRef} type="button" onClick={onClose} aria-label="Close search" className="shrink-0 rounded-full p-2 text-[#8B6B4A]"><XIcon size={22} /></button>
    </div>
    <div className="search-dialog-results px-4 py-5 sm:px-6"><p role="status" className="py-8 text-center text-sm text-[#806F61]">Loading search…</p></div>
  </SearchDialogFrame>;
}
