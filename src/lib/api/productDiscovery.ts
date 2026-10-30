import { apiUrl } from './client';
import { discoveryProducts, getCartRecommendations } from './basketRecommendations';
import type { Product } from '../../data/products';

export interface DiscoverySection { id: string; title: string; strategy: string; products: Product[]; }
export interface DiscoveryPage { sections: DiscoverySection[]; nextCursor: string | null; compatibility?: boolean; }
export type DiscoveryContext = 'checkout' | 'basket' | 'wishlist';
const strategies = new Set(['related', 'newest', 'featured', 'trending', 'popular']);
const validCursor = (value: unknown): value is string => typeof value === 'string' && value.length > 0 && value.length <= 512 && !/[\u0000-\u001f]/.test(value);

/** Cart-aware lead is loaded once; later ranked pages retain their server cursor. */
export async function getProductDiscovery(context: DiscoveryContext, cursor: string | null, signal: AbortSignal): Promise<DiscoveryPage> {
  if (context !== 'basket' || cursor !== null) return getRankedDiscovery(context, cursor, signal);
  const cart = await getCartRecommendations(signal);
  const page = await getRankedDiscovery(context, cursor, signal);
  if (!cart?.products.length) return page;
  const seen = new Set(cart.products.map(product => product.id));
  const sections = page.sections.map(section => ({ ...section, products: section.products.filter(product => {
    if (seen.has(product.id)) return false;
    seen.add(product.id); return true;
  }) }));
  const remaining = page.compatibility ? [{ id: 'new-arrivals', title: 'New arrivals', strategy: 'newest', products: sections.flatMap(section => section.products) }] : sections;
  return { ...page, sections: [{ id: 'basket-suggestions', title: 'You may also like', strategy: cart.strategy, products: cart.products }, ...remaining], compatibility: false };
}

/** Missing new API falls back only to honest, bounded newest-catalogue pages. */
async function getRankedDiscovery(context: DiscoveryContext, cursor: string | null, signal: AbortSignal): Promise<DiscoveryPage> {
  if (cursor !== null && !validCursor(cursor)) throw new Error('Invalid discovery cursor');
  if (!cursor?.startsWith('catalogue:')) {
    const params = new URLSearchParams({context, limit:'16'});
    if (cursor) params.set('cursor',cursor);
    const response = await fetch(apiUrl(`/storefront/discovery?${params}`), {signal, credentials:'include'});
    if (response.ok) {
      const value: unknown = await response.json();
      if (!value || typeof value !== 'object') throw new Error('Invalid discovery response');
      const {sections, nextCursor} = value as {sections:unknown;nextCursor:unknown};
      if (!Array.isArray(sections) || sections.length > 5 || (nextCursor !== null && !validCursor(nextCursor))) throw new Error('Invalid discovery response');
      let count = 0;
      const ids = new Set<string>();
      const parsed = sections.map(section => {
        if (!section || typeof section !== 'object') throw new Error('Invalid discovery section');
        const row = section as Record<string,unknown>;
        if (typeof row.id !== 'string' || !/^[a-z0-9-]{1,64}$/.test(row.id) || ids.has(row.id) || typeof row.title !== 'string' || !row.title.trim() || row.title.length > 100 || typeof row.strategy !== 'string' || !strategies.has(row.strategy) || !Array.isArray(row.products) || row.products.length > 8) throw new Error('Invalid discovery section');
        ids.add(row.id); count += row.products.length;
        if (count > 16) throw new Error('Discovery page exceeds limit');
        return {id:row.id,title:row.title,strategy:row.strategy,products:discoveryProducts(row.products,8)};
      });
      return {sections:parsed,nextCursor:nextCursor as string|null};
    }
    if (response.status !== 404 || cursor) throw new Error('Discovery unavailable');
  }
  const offset = cursor ? Number(cursor.slice('catalogue:'.length)) : 0;
  if (!Number.isSafeInteger(offset) || offset < 0 || offset > 10000) throw new Error('Invalid catalogue cursor');
  const response = await fetch(apiUrl(`/products?sort=newest&limit=8&offset=${offset}`),{signal});
  if (!response.ok) throw new Error('Discovery unavailable');
  const raw:unknown = await response.json();
  if (!Array.isArray(raw) || raw.length > 8) throw new Error('Invalid catalogue response');
  const products=discoveryProducts(raw,8);
  return {
    compatibility:true,
    sections: offset === 0 ? [
      {id:'suggestions',title:'You may also like',strategy:'newest',products:products.slice(0,4)},
      {id:'new-arrivals',title:'New arrivals',strategy:'newest',products:products.slice(4)},
    ] : [{id:'new-arrivals',title:'New arrivals',strategy:'newest',products}],
    nextCursor:raw.length === 8 && offset < 10000 ? `catalogue:${offset+8}` : null,
  };
}
