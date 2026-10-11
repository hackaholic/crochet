import { useEffect, useRef, type ReactNode } from 'react';

export default function AdminPreviewDialog({title,onClose,children}:{title:string;onClose:()=>void;children:ReactNode}) {
  const ref=useRef<HTMLDialogElement>(null);
  const trigger=useRef(document.activeElement as HTMLElement|null);
  useEffect(()=>{
    const previous=trigger.current;
    const dialog=ref.current!;dialog.showModal();
    const overflow=document.body.style.overflow;document.body.style.overflow='hidden';
    return()=>{dialog.close();document.body.style.overflow=overflow;previous?.focus();};
  },[]);
  return <dialog ref={ref} aria-label={title} onCancel={e=>{e.preventDefault();onClose();}} onClick={e=>{if(e.target===e.currentTarget)onClose();}} className="open:flex open:flex-col fixed inset-0 m-auto h-[min(42rem,90dvh)] max-h-[90dvh] w-[calc(100%_-_2rem)] max-w-3xl overflow-hidden rounded-2xl border border-[#E8E0D8] bg-[#FAF7F4] p-6 text-[#1A1108] shadow-2xl backdrop:bg-black/40">
    <header className="mb-5 shrink-0 flex items-center justify-between gap-3"><h2 className="font-serif text-xl font-bold">{title}</h2><button type="button" autoFocus onClick={onClose} aria-label={`Close ${title}`} className="rounded-lg border border-[#D6C5B5] bg-white px-3 py-2 text-sm font-semibold hover:bg-[#F3E0C9] focus-visible:outline-2 focus-visible:outline-[#C4622D]">Close</button></header><div className="min-h-0 flex-1 overflow-y-auto [overflow-wrap:anywhere]">{children}</div>
  </dialog>;
}
