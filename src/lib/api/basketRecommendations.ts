import { toProduct, type CatalogueProduct } from './catalogue';
import { isSafeMediaUrl } from '../media/image';
import { apiUrl } from './client';
import type { Product } from '../../data/products';

/** Bounded database discovery, not a claim of customer-specific personalization. */
export async function getBasketDiscovery(signal?: AbortSignal): Promise<Product[]> {
  const response = await fetch(apiUrl('/products?sort=newest&limit=8'), { signal });
  if (!response.ok) throw new Error('Basket discovery unavailable');
  const payload: unknown = await response.json();
  if (!Array.isArray(payload)) throw new Error('Invalid basket discovery response');
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
