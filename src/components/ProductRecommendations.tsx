import './productDiscovery.css';
import { useEffect, useId, useRef, useState } from 'react';
import ProductCard from './ProductCard';
import { useDiscoveryFeed } from '../hooks/useDiscoveryFeed';
import type { Product } from '../data/products';
import { getBasketDiscovery } from '../lib/api/basketRecommendations';

export default function ProductRecommendations({ open, excludedIds, onProductClick, onAddToCart, onToggleWishlist, wishlistIds = [], layout = 'basket', openProductInNewTab = false, extended = false, context }: {
  layout?: 'basket' | 'checkout';
  extended?: boolean;
  context?: 'checkout' | 'basket' | 'wishlist';
  openProductInNewTab?: boolean;
  open: boolean;
  excludedIds: number[];
  onProductClick: (product: Product) => void;
  onAddToCart: (product: Product) => Promise<void>;
  onToggleWishlist?: (product: Product) => void;
  wishlistIds?: number[];
}) {
  const titleId = useId();
  const feed = useDiscoveryFeed(open && extended, context ?? (layout === 'checkout' ? 'checkout' : 'basket'));
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [addingId, setAddingId] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const adding = useRef(false);
  const addProduct = async (product: Product) => {
    if (adding.current) return;
    adding.current = true;
    setAddingId(product.id);
    setError('');
    setNotice('');
    try {
      await onAddToCart(product);
      setNotice(`${product.name} added to your basket.`);
    } catch {
      setError('Could not add this item. Please try again.');
    } finally {
      adding.current = false;
      setAddingId(null);
    }
  };
  useEffect(() => {
    if (!open || extended) { setProducts([]); setError(''); setNotice(''); return; }
    let active = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    setLoading(true);
    getBasketDiscovery(controller.signal)
      .then(result => { if (active && !controller.signal.aborted) setProducts(result); })
      .catch(() => { if (active) setProducts([]); })
      .finally(() => { window.clearTimeout(timeout); if (active) setLoading(false); });
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); };
  }, [open, extended]);
  // Compatibility pages all share newest ordering: fill the first row after cart exclusions.
  const eligible = feed.sections.flatMap(row=>row.products).filter(product=>!excludedIds.includes(product.id));
  const feedRows = feed.compatibility ? feed.sections.map((row,index)=>({...row,products:index === 0 ? eligible.slice(0,4) : eligible.slice(4)})) : feed.sections;
  const rows = (extended ? feedRows : [{id:'suggestions',title:'You may also like',products:products.slice(0,8)}])
    .map(row=>({...row,products:row.products.filter(product=>!excludedIds.includes(product.id)).slice(0,extended ? undefined : 4)}))
    .filter(row=>row.products.length);
  if (!open) return null;
  if (!extended && loading) return <p role="status" className="py-4 text-sm text-[#5C3D2E]">Finding more handmade creations…</p>;
  if (!extended && !rows.length) return null;
  return (
    <div className={layout === 'checkout' ? 'checkout-discovery' : 'border-t border-[#EDE4D0] pt-5 pb-2'}>
      {error && <p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}
      {notice && <p role="status" className="mt-2 text-sm text-[#5C3D2E]">{notice}</p>}
      {rows.map(row=><section key={row.id} aria-labelledby={`${titleId}-${row.id}`} className="discovery-section">
        <h3 id={`${titleId}-${row.id}`} className="text-lg font-semibold text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{row.title}</h3>
        <div className={layout === 'checkout' ? 'mt-3 grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4' : 'mt-3 grid grid-cols-2 gap-3'}>
          {row.products.map(product => (
            <ProductCard key={product.id} product={product}
              onProductClick={onProductClick} openProductInNewTab={openProductInNewTab}
              onToggleWishlist={onToggleWishlist} isWishlisted={wishlistIds.includes(product.id)}
              onAddToCart={product => { void addProduct(product); }}
              addPending={addingId === product.id} addDisabled={addingId !== null}
              addLabel={`Add ${product.name} to basket`} />
          ))}
        </div>
      </section>)}
      {extended && <div ref={feed.sentinel} className="discovery-pagination">
        {feed.loading && <p role="status">Finding more handmade creations…</p>}
        {feed.failed && <p role="alert">More creations could not load. Please try again.</p>}
        {!feed.loading && (feed.hasMore || feed.failed) && <button type="button" className="discovery-more" onClick={()=>{void feed.load();}}>{feed.failed ? 'Try loading products again' : 'Load more products'}</button>}
      </div>}
    </div>
  );
}
