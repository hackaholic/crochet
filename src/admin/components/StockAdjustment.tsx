import { useState } from 'react';
import type { AdminProductVariant } from '../../lib/api/admin';
import { adjustStock } from '../services/inventory';
import { actionClass, controlClass, Field } from './CatalogueFields';
export default function StockAdjustment({ variant, onSaved, onClose }: {
  variant: AdminProductVariant; onSaved: () => void; onClose: () => void;
}) {
  const [value, setValue] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const delta = Number(value);
  return <section aria-label="Adjust stock" className="rounded-xl border border-[#E8E0D8] bg-white p-5">
    <h2 className="font-serif text-xl">Adjust stock · {variant.sku}</h2>
    <p className="my-3 text-sm">Current stock: {variant.stockQuantity}. Enter a positive number to add units or a negative number to remove units.</p>
    <form className="space-y-3" onSubmit={async event => {
      event.preventDefault(); if (busy) return;
      if (!value.trim() || !Number.isSafeInteger(delta) || delta === 0 || variant.stockQuantity + delta < 0) {
        setError('Enter a non-zero whole number that leaves stock at zero or above.'); return;
      }
      setBusy(true); setError('');
      try { await adjustStock(variant.id, delta); onSaved(); }
      catch { setError('Stock could not be updated. Your adjustment is preserved. Reload current stock before retrying if it has changed.'); }
      finally { setBusy(false); }
    }}>
      <Field label="Stock adjustment"><input required type="number" step="1" className={controlClass} value={value} disabled={busy} onChange={e => setValue(e.target.value)} /></Field>
      {value && Number.isSafeInteger(delta) && <p className="text-sm">Expected stock: {variant.stockQuantity + delta}. The server applies this change to the latest stock.</p>}
      {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
      <div className="flex gap-4"><button className={actionClass} disabled={busy}>{busy ? 'Saving…' : 'Save adjustment'}</button><button type="button" disabled={busy} className="underline" onClick={onClose}>Cancel</button></div>
    </form>
  </section>;
}
