import { useState } from 'react';
import type { AdminProductVariant } from '../../lib/api/admin';
import { saveVariant, type VariantDraft } from '../services/catalogue';
import { actionClass, controlClass, Field } from './CatalogueFields';
export function VariantFields({ draft, onChange }: { draft: VariantDraft; onChange: (draft: VariantDraft) => void }) {
  return <div className="grid gap-3 sm:grid-cols-2">
    <Field label="SKU"><input required value={draft.sku} className={controlClass} onChange={e => onChange({ ...draft, sku: e.target.value })} /></Field>
    <Field label="Variant name"><input required value={draft.name} className={controlClass} onChange={e => onChange({ ...draft, name: e.target.value })} /></Field>
    <Field label="Price (₹)"><input required type="number" min="0" step="1" value={draft.price} className={controlClass} onChange={e => onChange({ ...draft, price: e.target.valueAsNumber })} /></Field>
    <Field label="Stock quantity"><input required type="number" min="0" step="1" value={draft.stockQuantity} className={controlClass} onChange={e => onChange({ ...draft, stockQuantity: e.target.valueAsNumber })} /></Field>
  </div>;
}
export default function VariantEditor({ productId, variants, onSaved }: { productId: number; variants: AdminProductVariant[]; onSaved: () => void }) {
  const [selected, setSelected] = useState<number | undefined>();
  const [draft, setDraft] = useState<VariantDraft>({ sku: '', name: '', price: 0, stockQuantity: 0 });
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  return <section className="mt-6 border-t border-[#E8E0D8] pt-5"><h3 className="font-semibold">Variants and pricing</h3>
    <ul>{variants.map(v => <li key={v.id} className="flex items-center justify-between gap-3 py-3 text-sm"><span>{v.name} · {v.sku} · ₹{v.price} · {v.stockQuantity} in stock</span><button type="button" className="underline" onClick={() => { setSelected(v.id); setDraft({ sku: v.sku, name: v.name, price: v.price, stockQuantity: v.stockQuantity }); setEditing(true); setError(''); }}>Edit variant</button></li>)}</ul>
    <button type="button" className="text-sm underline" onClick={() => { setSelected(undefined); setDraft({ sku: '', name: '', price: 0, stockQuantity: 0 }); setEditing(true); setError(''); }}>Add variant</button>
    {editing && <form className="mt-4 space-y-3" onSubmit={async event => {
      event.preventDefault(); if (busy) return; setBusy(true); setError('');
      try { await saveVariant(productId, draft, selected); setEditing(false); onSaved(); }
      catch { setError('Variant could not be saved. Check the SKU and values, then try again.'); }
      finally { setBusy(false); }
    }}><fieldset disabled={busy}><VariantFields draft={draft} onChange={setDraft} /></fieldset>
      {error && <p role="alert">{error}</p>}<button className={actionClass} disabled={busy}>Save variant</button><button type="button" className="ml-3 text-sm underline" disabled={busy} onClick={() => setEditing(false)}>Cancel variant</button>
    </form>}
  </section>;
}
