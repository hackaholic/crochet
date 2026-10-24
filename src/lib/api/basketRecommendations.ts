import { toProduct, type CatalogueProduct } from './catalogue';
import { isSafeMediaUrl } from '../media/image';
import { apiUrl } from './client';
import type { Product } from '../../data/products';

export interface CartRecommendations {
  strategy: 'newest' | 'featured' | 'related' | 'personalized';
  products: Product[];
}
const cartStrategies = new Set(['newest', 'featured', 'related', 'personalized']);

/** Cookie identifies the basket/customer; never send a user ID from the client. */
export async function getCartRecommendations(signal?: AbortSignal): Promise<CartRecommendations | null> {
  const response = await fetch(apiUrl('/cart/recommendations?limit=4'), { signal, credentials: 'include' });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error('Basket discovery unavailable');
  const value: unknown = await response.json();
  if (!value || typeof value !== 'object') throw new Error('Invalid basket discovery response');
  const { strategy, products } = value as Record<string, unknown>;
  if (typeof strategy !== 'string' || !cartStrategies.has(strategy) || !Array.isArray(products) || products.length > 4) throw new Error('Invalid basket discovery response');
  return { strategy: strategy as CartRecommendations['strategy'], products: discoveryProducts(products, 4) };
}

/** Older servers alone may use bounded newest discovery, never fake personalization. */
export async function getBasketDiscovery(signal?: AbortSignal): Promise<Product[]> {
  const cart = await getCartRecommendations(signal);
  if (cart !== null) return cart.products;
  const response = await fetch(apiUrl('/products?sort=newest&limit=8'), { signal });
  if (!response.ok) throw new Error('Basket discovery unavailable');
  const payload: unknown = await response.json();
  if (!Array.isArray(payload) || payload.length > 8) throw new Error('Invalid basket discovery response');
  return discoveryProducts(payload, 8);
}

/** Validate public product data at the discovery boundary. */
export function discoveryProducts(payload: unknown[], limit: number): Product[] {
  const seen = new Set<number>();
  return payload.slice(0, limit).flatMap(item => {
    if (!item || typeof item !== 'object') return [];
    const value = item as CatalogueProduct;
    if (!Number.isSafeInteger(value.id) || seen.has(value.id) ||
        typeof value.name !== 'string' || !value.name.trim() ||
        typeof value.slug !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value.slug) ||
        !Number.isFinite(value.price) || value.price < 0 || value.currency !== 'INR' ||
        typeof value.image !== 'string' || !isSafeMediaUrl(value.image) || value.inStock !== true) return [];
    seen.add(value.id);
    return [toProduct(value)];
  });
}
