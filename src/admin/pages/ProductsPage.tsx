import { useEffect, useState } from 'react';
import { getAdminProducts, type AdminProductList } from '../../lib/api/admin';
import { getCategories, getProduct, type CatalogueProduct, type TaxonomyOption } from '../services/catalogue';
import ProductEditor from '../components/ProductEditor';
import ProductVisibility from '../components/ProductVisibility';
import { actionClass, controlClass } from '../components/CatalogueFields';
import { EmptyState, TableSkeleton } from '../components/AdminShared';

export default function ProductsPage() {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState<AdminProductList>();
  const [categories, setCategories] = useState<TaxonomyOption[]>([]);
  const [categoriesReady, setCategoriesReady] = useState(false);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  const [editing, setEditing] = useState(false);
  const [product, setProduct] = useState<CatalogueProduct>();
  const [detailBusy, setDetailBusy] = useState(false);
  const [notice, setNotice] = useState('');
  useEffect(() => {
    let active = true; setCategoriesLoading(true);
    getCategories().then(rows => { if (active) { setCategories(rows); setCategoriesReady(true); } }).catch(() => { if (active) setCategoriesReady(false); }).finally(() => { if (active) setCategoriesLoading(false); });
    return () => { active = false; };
  }, [retry]);
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError('');
    const timer = window.setTimeout(() => {
      getAdminProducts({ q: query.trim(), status, categoryId: category ? Number(category) : undefined, page }, controller.signal)
        .then(rows => { if (!controller.signal.aborted) setData(rows); })
        .catch(() => { if (!controller.signal.aborted) { setData(undefined); setError('Catalogue could not be loaded. Try again.'); } })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 275);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [query, status, category, page, retry]);
  if (editing) return <ProductEditor key={product?.id ?? 'new'} product={product} categories={categories} onClose={() => { setEditing(false); setProduct(undefined); }} onSaved={() => {
    setEditing(false); setProduct(undefined); setNotice('Product saved.'); setRetry(value => value + 1);
  }} />;
  return <div className="space-y-5">
    <div className="flex flex-wrap items-center justify-between gap-3"><div><h1 className="font-serif text-2xl font-bold">Products</h1><p className="mt-1 text-sm text-[#6B5B4E]">Manage your Sulocraft catalogue, prices, photos, tags and variants.</p></div><button className={actionClass} disabled={!categoriesReady || detailBusy} onClick={() => { setProduct(undefined); setEditing(true); setNotice(''); }}>Add product</button></div>
    {notice && <p role="status" className="text-sm text-emerald-700">{notice}</p>}
    {!categoriesReady && !categoriesLoading && <p role="status" className="text-sm">Category data is unavailable; editing is paused to protect existing associations. <button className="underline" onClick={() => setRetry(x => x + 1)}>Retry categories</button></p>}
    <div className="flex flex-wrap gap-3"><label className="grow text-sm">Search products or SKU<input type="search" className={controlClass} value={query} onChange={e => { setQuery(e.target.value); setPage(1); }} /></label>
      <label className="text-sm">Status<select className={controlClass} value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}><option value="">All statuses</option><option value="ACTIVE">Active</option><option value="DRAFT">Draft</option><option value="ARCHIVED">Archived</option></select></label>
      <label className="text-sm">Category<select className={controlClass} value={category} onChange={e => { setCategory(e.target.value); setPage(1); }}><option value="">All categories</option>{categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
    </div>
    <div className="rounded-xl border border-[#E8E0D8] bg-white p-4">
      {loading ? <TableSkeleton /> : error ? <div role="alert"><p>{error}</p><button className="mt-3 underline" onClick={() => setRetry(value => value + 1)}>Try again</button></div> : !data?.items.length ? <EmptyState title="No products found" desc="Try another search or add your first listing." /> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr className="border-b border-[#E8E0D8]"><th className="p-3">Product</th><th className="p-3">Categories</th><th className="p-3">Price from</th><th className="p-3">Stock</th><th className="p-3">Status</th><th className="p-3">Actions</th></tr></thead><tbody>{data.items.map(p => <tr key={p.id} className="border-b border-[#F5F0EA]"><td className="p-3"><div className="flex items-center gap-3"><img src={p.primaryImageUrl || (/^https?:\/\//.test(p.primaryImage) ? p.primaryImage : undefined)} alt={p.name} className="h-14 w-14 rounded-lg object-cover" /><span>{p.name}</span></div></td><td className="p-3">{p.categoryNames.join(', ')}</td><td className="p-3">₹{p.minPrice}</td><td className="p-3">{p.totalStock}</td><td className="p-3">{p.status}</td><td className="p-3"><button disabled={!categoriesReady || detailBusy} className="underline disabled:opacity-50" onClick={async () => {
        setDetailBusy(true); setError('');
        try { setProduct(await getProduct(p.id)); setEditing(true); setNotice(''); } catch { setError('Product details could not be loaded. Try again.'); } finally { setDetailBusy(false); }
      }} aria-label={`Edit ${p.name}`}>Edit</button><ProductVisibility product={p} onSaved={() => { setNotice('Product visibility updated.'); setRetry(value => value + 1); }} /></td></tr>)}</tbody></table></div>}
      {data && !loading && <nav aria-label="Catalogue pages" className="mt-4 flex items-center justify-between text-sm"><button disabled={page === 1} className="underline disabled:opacity-50" onClick={() => setPage(value => value - 1)}>Previous</button><span>Page {data.page} · {data.total} products</span><button disabled={data.page * data.pageSize >= data.total} className="underline disabled:opacity-50" onClick={() => setPage(value => value + 1)}>Next</button></nav>}
    </div>
  </div>;
}
