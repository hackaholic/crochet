import { useEffect, useState } from 'react';
import { getAdminProducts, type AdminProductList, type AdminProductVariant } from '../../lib/api/admin';
import StockAdjustment from '../components/StockAdjustment';
import ProductThumbnail from '../components/ProductThumbnail';
import { controlClass } from '../components/CatalogueFields';
import { EmptyState, TableSkeleton } from '../components/AdminShared';
export default function InventoryPage() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState<AdminProductList>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  const [editing, setEditing] = useState<AdminProductVariant>();
  const [notice, setNotice] = useState('');
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError('');
    const timer = window.setTimeout(() => {
      getAdminProducts({ q: query.trim(), page }, controller.signal)
        .then(result => { if (!controller.signal.aborted) setData(result); })
        .catch(() => { if (!controller.signal.aborted) { setData(undefined); setError('Inventory could not be loaded.'); } })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 275);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [query, page, revision]);
  if (editing) return <StockAdjustment variant={editing} onClose={() => setEditing(undefined)} onSaved={() => {
    setEditing(undefined); setNotice('Stock updated.'); setRevision(x => x + 1);
  }} />;
  const rows = data?.items.flatMap(product => product.variants.map(variant => ({ product, variant }))) || [];
  return <div className="space-y-5">
    <div><h1 className="font-serif text-2xl font-bold">Inventory</h1><p className="mt-1 text-sm text-[#6B5B4E]">Manage stock for each catalogue variant.</p></div>
    {notice && <p role="status" className="text-sm text-emerald-700">{notice}</p>}
    <label className="block text-sm">Search products or SKU<input type="search" className={controlClass} value={query} onChange={e => { setQuery(e.target.value); setPage(1); setNotice(''); }} /></label>
    <div className="rounded-xl border border-[#E8E0D8] bg-white p-4">
      {loading ? <TableSkeleton /> : error ? <div role="alert">{error} <button className="underline" onClick={() => setRevision(x => x + 1)}>Try again</button></div> : !rows.length ? <EmptyState title="No inventory found" desc="Try another search or create a product variant." /> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr className="border-b border-[#E8E0D8]"><th className="p-3">Product / variant</th><th className="p-3">SKU</th><th className="p-3">Stock</th><th className="p-3">Status</th><th className="p-3">Actions</th></tr></thead><tbody>{rows.map(({ product, variant }) => <tr key={variant.id} className="border-b border-[#F5F0EA]"><td className="p-3"><div className="flex items-center gap-3"><ProductThumbnail product={product} /><div>{product.name}<span className="block text-xs text-[#6B5B4E]">{variant.name}</span></div></div></td><td className="p-3">{variant.sku}</td><td className="p-3">{variant.stockQuantity}</td><td className="p-3">{variant.status}</td><td className="p-3"><button className="underline" aria-label={`Adjust ${variant.sku}`} onClick={() => setEditing(variant)}>Adjust stock</button></td></tr>)}</tbody></table></div>}
      {data && !loading && <nav aria-label="Inventory pages" className="mt-4 flex items-center justify-between text-sm"><button className="underline disabled:opacity-50" disabled={page === 1} onClick={() => setPage(x => x - 1)}>Previous</button><span>Page {data.page} · {data.total} products</span><button className="underline disabled:opacity-50" disabled={data.page * data.pageSize >= data.total} onClick={() => setPage(x => x + 1)}>Next</button></nav>}
    </div>
  </div>;
}
