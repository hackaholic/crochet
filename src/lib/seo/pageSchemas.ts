import type { SeoMetadata } from '../api/seo';
import type { Category } from '../api/catalogue';
import type { Product } from '../../data/products';
import { buildProductSchema } from './productSchema';

function httpUrl(value?: string | null) {
  try {
    const url = new URL(value || '');
    return ['http:', 'https:'].includes(url.protocol) && !url.username && !url.password ? url : undefined;
  } catch { return undefined; }
}
function categoryTrail(categories: Category[], slug: string, depth = 0): Category[] | undefined {
  if (depth > 64) return undefined;
  for (const category of categories) {
    if (category.slug === slug) return [category];
    const child = categoryTrail(category.children ?? [], slug, depth + 1);
    if (child) return [category, ...child];
  }
}
export function publicBreadcrumbs(metadata?: SeoMetadata, categories: Category[] = []) {
  const origin = httpUrl(metadata?.canonicalUrl)?.origin;
  if (!origin) return [];
  const seen = new Set<string>();
  const result = [];
  let items = metadata?.breadcrumbs ?? [];
  const categoryItems = items.filter(item => item.path.startsWith('/categories/'));
  const leaf = categoryItems.at(-1);
  const ancestry = leaf && categoryTrail(categories, leaf.path.slice('/categories/'.length));
  if (ancestry) {
    const first = items.findIndex(item => item.path.startsWith('/categories/'));
    const last = items.findIndex(item => item === leaf);
    items = [...items.slice(0, first), ...ancestry.map(category => ({ name: category.name, path: `/categories/${category.slug}` })), ...items.slice(last + 1)];
  }
  for (const item of items) {
    if (!item.name?.trim() || !/^\/(?:[a-z0-9-]+\/)*[a-z0-9-]*$/.test(item.path)
      || /^\/(admin|account|cart|checkout|auth|wishlist|track)(\/|$)/.test(item.path) || seen.has(item.path)) return [];
    seen.add(item.path);
    result.push({ name: item.name, path: item.path, url: new URL(item.path, origin).href });
  }
  return result;
}
/** One source for initial HTML and runtime. Missing facts stay omitted. */
export function buildPageSchemas(metadata: SeoMetadata, canonical: string, product?: Product | null, categories: Category[] = []) {
  const result: Record<string, object> = {};
  const url = httpUrl(canonical);
  if (!url || metadata.robots.includes('noindex')) return result;
  const trail = publicBreadcrumbs({ ...metadata, canonicalUrl: url.href }, categories);
  if (trail.length > 1 && ['product', 'collection'].includes(metadata.pageType)) result['sulocraft-breadcrumb-schema'] = {
    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
    itemListElement: trail.map((item, index) => ({ '@type': 'ListItem', position: index + 1, name: item.name, item: item.url })),
  };
  const offer = buildProductSchema(metadata, canonical, product);
  if (offer) result['sulocraft-product-schema'] = offer;
  const brand = metadata.brand;
  if (metadata.pageType === 'website' && brand?.name?.trim()) {
    const base = `${url.origin}/`;
    const sameAs = [...new Set((brand.sameAs ?? []).filter(value => value !== brand.whatsappUrl).map(value => httpUrl(value)?.href).filter((value): value is string => Boolean(value)))];
    result['sulocraft-site-schema'] = { '@context': 'https://schema.org', '@graph': [
      { '@type': 'Organization', '@id': `${base}#organization`, name: brand.name,
        url: base,
        ...(httpUrl(brand.logoUrl) ? { logo: httpUrl(brand.logoUrl)!.href } : {}), ...(sameAs.length ? { sameAs } : {}),
      },
      { '@type': 'WebSite', '@id': `${base}#website`, name: brand.name, url: base, publisher: { '@id': `${base}#organization` } },
    ] };
  }
  const entity = metadata.categoryEntity ?? metadata.collectionEntity;
  if (metadata.pageType === 'collection' && entity && entity.name === metadata.h1) {
    result['sulocraft-category-schema'] = { '@context': 'https://schema.org', '@type': 'CollectionPage', '@id': canonical, url: canonical, name: entity.name };
  }
  return result;
}
export const PAGE_SCHEMA_IDS = ['sulocraft-breadcrumb-schema', 'sulocraft-product-schema', 'sulocraft-site-schema', 'sulocraft-category-schema', 'sulocraft-faq-schema'];
