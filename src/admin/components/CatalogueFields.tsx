import type { ReactNode } from 'react';
import type { TaxonomyOption } from '../services/catalogue';
export const controlClass = 'mt-1 w-full rounded-lg border border-[#E8E0D8] bg-white px-3 py-2 text-sm';
export const actionClass = 'rounded-lg bg-[#C4622D] px-4 py-2 text-sm font-medium text-white disabled:opacity-50';
export function Field({ label, children }: { label: string; children: ReactNode }) {
  return <label className="block text-sm font-medium text-[#6B5B4E]">{label}{children}</label>;
}
export function TaxonomySelect({ title, options, selected, onChange }: {
  title: string; options: TaxonomyOption[]; selected: number[]; onChange: (ids: number[]) => void;
}) {
  return <fieldset className="rounded-lg border border-[#E8E0D8] p-3"><legend className="px-1 text-sm font-medium">{title}</legend>
    <div className="flex max-h-40 flex-wrap gap-3 overflow-auto">{options.map(option => <label key={option.id} className="flex items-center gap-2 text-sm">
      <input type="checkbox" checked={selected.includes(option.id)} onChange={event => onChange(event.target.checked ? [...selected, option.id] : selected.filter(id => id !== option.id))} />{option.name}
    </label>)}</div></fieldset>;
}
