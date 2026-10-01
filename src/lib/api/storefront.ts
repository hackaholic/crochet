import { apiUrl } from './client';

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

export async function getStorefrontContent(signal?: AbortSignal): Promise<StorefrontContent> {
  const response = await fetch(apiUrl('/storefront'), { signal });
  if (!response.ok) throw new Error(`Storefront request failed (${response.status})`);
  const payload = await response.json() as StorefrontContent;
  if (!Array.isArray(payload.heroCampaigns)) throw new Error('Storefront response has an unexpected shape');
  return payload;
}
