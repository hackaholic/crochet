import { apiUrl } from './client';
import type { Product } from '../../data/products';

export interface HomepageCampaign {
  id: number;
  title: string;
  emphasis?: string | null;
  description: string;
  eyebrow?: string | null;
  imageUrl: string;
  imageAlt: string;
  destination?: string | null;
  priority: number;
  startsAt?: string | null;
  endsAt?: string | null;
}

export interface StorefrontContent {
  brand: { name: string; ownerName: string; instagramUrl?: string | null; whatsappUrl?: string | null };
  heroCampaigns: HomepageCampaign[];
}

export interface CategorySummary { id: number; name: string; slug: string; description?: string | null; imageUrl: string; }
export interface ReviewSummary { id: number; authorName: string; location?: string | null; rating: number; text: string; avatarUrl?: string | null; }
interface BaseSection { id: number; order: number; enabled: boolean; }
export interface CategoryGridSection extends BaseSection { type: 'category_grid'; title: string; eyebrow?: string | null; categories: CategorySummary[]; }
export interface ProductCollectionSection extends BaseSection { type: 'product_collection'; title: string; eyebrow?: string | null; collectionSlug: string; products: Product[]; }
export interface PromoBannerSection extends BaseSection { type: 'promo_banner'; title: string; description?: string | null; imageUrl?: string | null; imageAlt?: string | null; ctaText?: string | null; ctaUrl?: string | null; }
export interface ReviewSectionData extends BaseSection { type: 'review_section'; title: string; reviews: ReviewSummary[]; }
export interface ImageTextSectionData extends BaseSection { type: 'image_text'; title: string; description: string; imageUrl: string; imageAlt: string; imagePosition: 'left' | 'right'; ctaText?: string | null; ctaUrl?: string | null; }
export type HomepageSection = CategoryGridSection | ProductCollectionSection | PromoBannerSection | ReviewSectionData | ImageTextSectionData;
export interface StorefrontHomeContent { brand: StorefrontContent['brand']; hero: HomepageCampaign[]; sections: HomepageSection[]; }

export async function getStorefrontContent(signal?: AbortSignal): Promise<StorefrontContent> {
  const response = await fetch(apiUrl('/storefront'), { signal });
  if (!response.ok) throw new Error(`Storefront request failed (${response.status})`);
  const payload = await response.json() as StorefrontContent;
  if (!Array.isArray(payload.heroCampaigns)) throw new Error('Storefront response has an unexpected shape');
  return payload;
}

export async function getStorefrontHome(signal?: AbortSignal): Promise<StorefrontHomeContent> {
  const response = await fetch(apiUrl('/storefront/home'), { signal });
  if (response.ok) {
    const payload = await response.json() as StorefrontHomeContent;
    if (!Array.isArray(payload.hero) || !Array.isArray(payload.sections)) throw new Error('Storefront home response has an unexpected shape');
    return payload;
  }
  if (response.status !== 404) throw new Error(`Storefront home request failed (${response.status})`);
  const compatibility = await getStorefrontContent(signal);
  return { brand: compatibility.brand, hero: compatibility.heroCampaigns, sections: [] };
}
