import { useEffect, useState } from 'react';
import type { Product } from '../data/products';
import { getBasketDiscovery } from '../lib/api/basketRecommendations';

export default function BasketRecommendations({ open, excludedIds, onProductClick }: {
  open: boolean;
  excludedIds: number[];
  onProductClick: (product: Product) => void;
}) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (!open) { setProducts([]); return; }
    let active = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    setLoading(true);
    getBasketDiscovery(controller.signal)
      .then(result => { if (active && !controller.signal.aborted) setProducts(result); })
      .catch(() => { if (active) setProducts([]); })
      .finally(() => { window.clearTimeout(timeout); if (active) setLoading(false); });
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); };
  }, [open]);
  const suggestions = products.filter(product => !excludedIds.includes(product.id)).slice(0, 4);
  if (!open) return null;
  if (loading) return <p role="status" className="py-4 text-sm text-[#5C3D2E]">Finding more handmade creations…</p>;
  if (!suggestions.length) return null;
  return (
    <section aria-labelledby="basket-discovery-title" className="border-t border-[#EDE4D0] pt-5 pb-2">
      <h3 id="basket-discovery-title" className="text-lg font-semibold text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>You may also like</h3>
      <div className="mt-3 grid grid-cols-2 gap-3">
        {suggestions.map(product => (
          <button key={product.id} onClick={() => onProductClick(product)} className="overflow-hidden rounded-2xl border border-[#EDE4D0] bg-white text-left shadow-sm transition-shadow hover:shadow-md focus-visible:outline-offset-2">
            <img src={product.image} alt={product.name} width={180} height={180} loading="lazy" className="aspect-square w-full object-cover" />
            <span className="block p-3">
              <span className="line-clamp-2 min-h-10 text-sm font-semibold leading-5 text-[#2C1810]">{product.name}</span>
              <span className="mt-1 block text-sm font-bold text-[#5C3D2E]">₹{product.price.toLocaleString('en-IN')}</span>
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
