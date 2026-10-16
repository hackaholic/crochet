import {socialMetadata} from '../lib/seo/socialMetadata.mjs';
import {useSeoPolicy} from '../lib/seo/bootstrap';
import {canonicalMetadata, type PublicSeoPolicy} from '../lib/seo/urlPolicy.mjs';
import type { Category } from '../lib/api/catalogue';
import { useEffect } from 'react';
import { buildPageSchemas, PAGE_SCHEMA_IDS } from '../lib/seo/pageSchemas';
import { setMeta, setSchema, setLink } from '../lib/seo/head';
import type { Product } from '../data/products';
import type { AppPage } from '../lib/routes';
import { getSeoMetadata, type SeoMetadata } from '../lib/api/seo';

const PRIVATE_PAGES = new Set<AppPage>(['account', 'tracking', 'admin', 'cart', 'checkout', 'wishlist', 'notFound']);

function applyMetadata(metadata: SeoMetadata, product?: Product | null, categories: Category[] = [], policy?: PublicSeoPolicy) {
  metadata = canonicalMetadata(metadata, policy);
  const fallbackUrl = new URL(metadata.canonicalPath.startsWith('/') && !metadata.canonicalPath.startsWith('//') ? metadata.canonicalPath : '/', window.location.origin);
  let canonicalUrl = fallbackUrl.toString();
  if (metadata.canonicalUrl) {
    try { const candidate = new URL(metadata.canonicalUrl); if (['http:', 'https:'].includes(candidate.protocol) && !candidate.username && !candidate.password) canonicalUrl = candidate.toString(); } catch { /* Ignore malformed metadata URLs. */ }
  }
  document.head.querySelectorAll('title').forEach((node, index) => { if (index > 0) node.remove(); });
  document.title = metadata.title;
  setMeta('meta[name="description"]', { name: 'description', content: metadata.description });
  setMeta('meta[name="robots"]', { name: 'robots', content: metadata.robots });
  // Remove the previous route's entire social group, including optional image fields.
  document.head.querySelectorAll('meta[property^="og:"], meta[name^="twitter:"]').forEach(node => node.remove());
  for (const [key, content] of Object.entries(socialMetadata(metadata, canonicalUrl))) {
    const attribute = key.startsWith('og:') ? 'property' : 'name';
    setMeta(`meta[${attribute}="${key}"]`, { [attribute]: key, content });
  }

  if(metadata.httpStatus === 404 || metadata.httpStatus === 410) document.head.querySelectorAll('link[rel="canonical"]').forEach(node=>node.remove());
  else setLink('canonical', { href: canonicalUrl });
  document.head.querySelectorAll('link[rel="alternate"][hreflang]').forEach(node => node.remove());

  const schemas = buildPageSchemas(metadata, canonicalUrl, product, categories);
  for (const id of PAGE_SCHEMA_IDS) setSchema(id, schemas[id]);
}

export default function SeoManager({ page, pathname, product, onMetadata, categories = [] }: { categories?: Category[]; page: AppPage; pathname: string; product?: Product | null; onMetadata?: (metadata: SeoMetadata) => void }) {
  const policy = useSeoPolicy();
  useEffect(() => {
    const controller = new AbortController();
    const fallback: SeoMetadata = {
      title: page === 'admin' ? 'Sulocraft Admin | Store management' : product?.name ? `${product.name} | Sulocraft` : 'Sulocraft',
      description: page === 'admin' ? 'Private Sulocraft store administration.' : PRIVATE_PAGES.has(page) ? '' : product?.description ?? '',
      canonicalPath: pathname,
      httpStatus: page === 'notFound' ? 404 : 200,
      robots: 'noindex,nofollow',
      imageUrl: PRIVATE_PAGES.has(page) ? undefined : product?.images?.[0] ?? product?.image,
      imageAlt: product?.name,
      pageType: product ? 'product' : page === 'shop' ? 'collection' : 'website',
      breadcrumbs: [],
    };
    if (PRIVATE_PAGES.has(page)) { applyMetadata(fallback, product, categories, policy); return () => controller.abort(); }
    getSeoMetadata(pathname, controller.signal).then(metadata => { if (!controller.signal.aborted) { applyMetadata(metadata, product, categories, policy); onMetadata?.(canonicalMetadata(metadata,policy)); } }).catch(error => {
      if (!controller.signal.aborted) applyMetadata(fallback, product, categories, policy);
    });
    return () => controller.abort();
  }, [page, pathname, product, onMetadata, categories, policy]);
  return null;
}
