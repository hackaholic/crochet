import { useState } from 'react';
import type { AdminProduct } from '../../lib/api/admin';
import { setProductStatus } from '../services/catalogue';

export default function ProductVisibility({ product, onSaved }: { product: AdminProduct; onSaved: () => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  if (product.status !== 'ACTIVE' && product.status !== 'DRAFT') return null;
  const enabled = product.status === 'ACTIVE';
  return <div className="mt-2">
    <button type="button" disabled={busy} className="underline disabled:opacity-50" aria-label={`${enabled ? 'Disable' : 'Enable'} ${product.name}`} onClick={async () => {
      if (busy) return;
      setBusy(true); setError('');
      try { await setProductStatus(product.id, enabled ? 'DRAFT' : 'ACTIVE'); onSaved(); }
      catch { setError('Visibility could not be changed. Try again.'); }
      finally { setBusy(false); }
    }}>{busy ? 'Saving…' : enabled ? 'Disable' : 'Enable'}</button>
    {error && <p role="alert" className="mt-1 text-xs text-red-700">{error}</p>}
  </div>;
}
