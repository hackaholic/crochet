import type { ProductInformation } from '../products/information';
import type { MediaMetadata } from '../media/image';
import { apiUrl } from './client';

export interface SeoBreadcrumb { name: string; path: string; }
export interface SeoFaqItem { question: string; answer: string; }
export interface SeoShippingInfo {
  freeShippingThreshold: number;
  standardFee: number;
  currency: string;
  transitTime: string;
  country: string;
}
export interface SeoReturnPolicy {
  returnWindowDays: number;
  policyUrl: string;
  returnFees: string;
}
export interface SeoProductEntity extends ProductInformation {
  id: number; name: string; slug: string; sku: string; price: number; currency: string;
  inStock: boolean; inventoryStatus: string; brand: string;
  description?: string | null;
  media?: MediaMetadata[];
  primaryCategoryName?: string | null; imageUrls: string[];
  variants: Array<{ id: number; sku: string; name: string; price: number; inStock: boolean }>;
  aggregateRating?: { ratingValue: number; reviewCount: number; provenance?: string } | null;
}
export interface SeoBrand {
  name: string; legalName?: string | null; logoUrl?: string | null; ownerName?: string | null;
  sameAs?: string[]; whatsappUrl?: string | null;
}
export interface SeoMetadata {
  httpStatus?: 200 | 301 | 404 | 410;
  redirectTo?: string | null;
  brand?: SeoBrand | null;
  categoryEntity?: { id: number; name: string; slug: string; description?: string | null; parentName?: string | null; parentSlug?: string | null } | null;
  collectionEntity?: { id: number; name: string; slug: string; description?: string | null } | null;
  title: string;
  description: string;
  canonicalPath: string;
  canonicalUrl?: string | null;
  h1?: string | null;
  productEntity?: SeoProductEntity | null;
  robots: 'index,follow' | 'noindex,nofollow';
  imageUrl?: string | null;
  imageAlt?: string | null;
  imageWidth?: number | null;
  imageHeight?: number | null;
  imageType?: string | null;
  pageType: 'website' | 'product' | 'collection' | 'article';
  breadcrumbs: SeoBreadcrumb[];
  faqs?: SeoFaqItem[];
  shippingInfo?: SeoShippingInfo | null;
  returnPolicy?: SeoReturnPolicy | null;
}

export async function getSeoMetadata(path: string, signal?: AbortSignal): Promise<SeoMetadata> {
  const response = await fetch(`${apiUrl('/seo/resolve')}?path=${encodeURIComponent(path)}`, { signal });
  if (!response.ok) throw new Error(`SEO metadata request failed (${response.status})`);
  return response.json() as Promise<SeoMetadata>;
}
