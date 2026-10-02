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
  primaryCategory?: TaxonomyReference | null;
  categories?: Array<string | TaxonomyReference>;
  collections?: TaxonomyReference[];
  badge?: string | null;
  tags?: string[];
  occasions?: string[];
  description?: string | null;
  customizable?: boolean;
  inStock?: boolean;
  inventoryStatus?: string;
}

export interface TaxonomyReference {
  name: string;
  slug: string;
}

export interface Category extends TaxonomyReference {
  id: number;
  description?: string | null;
  imageUrl?: string | null;
  parentId?: number | null;
  displayOrder: number;
  isActive: boolean;
  productCount: number;
  children: Category[];
}

export interface Collection extends TaxonomyReference {
  id: number;
  description?: string | null;
  imageUrl?: string | null;
  displayOrder: number;
  productCount?: number;
}

function taxonomyReference(value: string | TaxonomyReference): TaxonomyReference {
  return typeof value === 'string'
    ? { name: value, slug: value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') }
    : value;
}

function toProduct(product: CatalogueProduct): Product {
  const categories = (product.categories ?? []).map(taxonomyReference);
  const primaryCategory = product.primaryCategory ?? categories[0];
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
    category: primaryCategory?.name ?? product.category,
    primaryCategory,
    categories,
    collections: product.collections ?? [],
    badge: product.badge ?? undefined,
    tags: product.tags ?? [],
    occasions: product.occasions ?? [],
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

export interface ProductSearchOptions {
  limit?: number;
  signal?: AbortSignal;
}

/** Search the active database catalogue for products matching a query. */
export async function searchProducts(query: string, options: ProductSearchOptions = {}): Promise<Product[]> {
  const normalizedQuery = query.trim();
  if (!normalizedQuery) return [];

  const params = new URLSearchParams({
    q: normalizedQuery,
    limit: String(options.limit ?? 6),
  });
  const response = await fetch(apiUrl(`/products/search?${params.toString()}`), {
    signal: options.signal,
  });
  if (!response.ok) throw new Error(`Product search failed (${response.status})`);
  const payload: unknown = await response.json();
  if (!Array.isArray(payload)) throw new Error('Product search response has an unexpected shape');
  return payload.map(item => toProduct(item as CatalogueProduct));
}

export interface SearchSuggestionKeyword {
  term: string;
}

export interface SearchSuggestions {
  trending_keywords: SearchSuggestionKeyword[];
  trending_products: Product[];
}

/** Fetch backend-ranked search discovery content for the empty search overlay. */
export async function getSearchSuggestions(signal?: AbortSignal): Promise<SearchSuggestions> {
  const response = await fetch(apiUrl('/products/search/suggestions?keyword_limit=6&product_limit=4'), { signal });
  if (!response.ok) throw new Error(`Search suggestions request failed (${response.status})`);
  const payload: unknown = await response.json();
  if (!payload || typeof payload !== 'object') throw new Error('Search suggestions response has an unexpected shape');

  const body = payload as { trending_keywords?: unknown; trending_products?: unknown };
  if (!Array.isArray(body.trending_keywords) || !Array.isArray(body.trending_products)) {
    throw new Error('Search suggestions response has an unexpected shape');
  }
  const keywords = body.trending_keywords.filter((item): item is SearchSuggestionKeyword => (
    Boolean(item) && typeof item === 'object' && typeof (item as SearchSuggestionKeyword).term === 'string'
  ));
  return {
    trending_keywords: keywords,
    trending_products: body.trending_products.map(item => toProduct(item as CatalogueProduct)),
  };
}

/** Record a completed query for anonymous aggregate trends; callers must not await this. */
export async function recordSearchQuery(query: string): Promise<void> {
  const normalizedQuery = query.trim();
  if (!normalizedQuery) return;
  const response = await fetch(apiUrl('/products/search/events'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: normalizedQuery }),
  });
  if (!response.ok) throw new Error(`Search event request failed (${response.status})`);
}

async function getJsonList<T>(path: string, signal?: AbortSignal): Promise<T[]> {
  const response = await fetch(apiUrl(path), { signal });
  if (!response.ok) throw new Error(`Taxonomy request failed (${response.status})`);
  const payload: unknown = await response.json();
  if (!Array.isArray(payload)) throw new Error('Taxonomy response has an unexpected shape');
  return payload as T[];
}

export function getCategories(signal?: AbortSignal): Promise<Category[]> {
  return getJsonList<Category>('/categories?flat=false&includeEmpty=false', signal);
}

export function getCollections(signal?: AbortSignal): Promise<Collection[]> {
  return getJsonList<Collection>('/collections', signal);
}

export function flattenCategories(categories: Category[]): Category[] {
  return categories.flatMap(category => [category, ...flattenCategories(category.children ?? [])]);
}

export interface Occasion {
  id: string;
  name: string;
  icon?: string | null;
  imageUrl?: string | null;
  description?: string | null;
  displayOrder?: number;
}

export function getOccasions(signal?: AbortSignal): Promise<Occasion[]> {
  return getJsonList<Occasion>('/occasions', signal);
}
