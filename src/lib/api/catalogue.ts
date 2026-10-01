import type { Product } from '../../data/products';
import { apiUrl } from './client';

export interface CatalogueProduct {
  id: number;
  name: string;
  slug: string;
  price: number;
  pricePaise?: number | null;
  currency: 'INR';
  compareAtPrice?: number | null;
  originalPrice?: number | null;
  rating?: number;
  reviews?: number;
  reviewCount?: number;
  image: string;
  imageUrls?: string[];
  category: string;
  categories?: string[];
  badge?: string | null;
  tags?: string[];
  description?: string | null;
  customizable?: boolean;
  inStock?: boolean;
  inventoryStatus?: string;
}

function toProduct(product: CatalogueProduct): Product {
  return {
    id: product.id,
    name: product.name,
    slug: product.slug,
    price: product.price,
    originalPrice: product.originalPrice ?? product.compareAtPrice ?? undefined,
    rating: product.rating ?? 5,
    reviews: product.reviewCount ?? product.reviews ?? 0,
    image: product.image,
    images: product.imageUrls?.length ? product.imageUrls : [product.image],
    category: product.category,
    badge: product.badge ?? undefined,
    tags: product.tags ?? [],
    description: product.description ?? undefined,
    customizable: product.customizable ?? false,
    inStock: product.inStock ?? product.inventoryStatus !== 'OUT_OF_STOCK',
  };
}

export async function getProducts(signal?: AbortSignal): Promise<Product[]> {
  const response = await fetch(`${apiUrl('/products')}?limit=100`, { signal });
  if (!response.ok) throw new Error(`Catalogue request failed (${response.status})`);
  const payload: unknown = await response.json();
  if (!Array.isArray(payload)) throw new Error('Catalogue response has an unexpected shape');
  return payload.map(item => toProduct(item as CatalogueProduct));
}
