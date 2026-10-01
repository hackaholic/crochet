import { apiUrl } from './client';

export interface SeoBreadcrumb { name: string; path: string; }
export interface SeoMetadata {
  title: string;
  description: string;
  canonicalPath: string;
  robots: 'index,follow' | 'noindex,nofollow';
  imageUrl?: string | null;
  imageAlt?: string | null;
  pageType: 'website' | 'product' | 'collection' | 'article';
  breadcrumbs: SeoBreadcrumb[];
}

export async function getSeoMetadata(path: string, signal?: AbortSignal): Promise<SeoMetadata> {
  const response = await fetch(`${apiUrl('/seo/resolve')}?path=${encodeURIComponent(path)}`, { signal });
  if (!response.ok) throw new Error(`SEO metadata request failed (${response.status})`);
  return response.json() as Promise<SeoMetadata>;
}
