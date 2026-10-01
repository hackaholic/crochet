import { useEffect } from 'react';
import type { Product } from '../data/products';
import type { AppPage } from '../lib/routes';
import { getSeoMetadata, type SeoMetadata } from '../lib/api/seo';

const PRIVATE_PAGES = new Set<AppPage>(['account', 'admin', 'cart', 'checkout', 'wishlist', 'notFound']);

function setMeta(selector: string, attributes: Record<string, string>) {
  let element = document.head.querySelector<HTMLMetaElement>(selector);
  if (!element) { element = document.createElement('meta'); document.head.appendChild(element); }
  Object.entries(attributes).forEach(([name, value]) => element!.setAttribute(name, value));
}

function removeMeta(selector: string) { document.head.querySelector(selector)?.remove(); }

function setSchema(id: string, value?: object) {
  document.getElementById(id)?.remove();
  if (!value) return;
  const script = document.createElement('script');
  script.id = id;
  script.type = 'application/ld+json';
  script.text = JSON.stringify(value).replace(/</g, '\\u003c');
  document.head.appendChild(script);
}

function applyMetadata(metadata: SeoMetadata, product?: Product | null) {
  const canonicalUrl = new URL(metadata.canonicalPath, window.location.origin).toString();
  document.title = metadata.title;
  setMeta('meta[name="description"]', { name: 'description', content: metadata.description });
  setMeta('meta[name="robots"]', { name: 'robots', content: metadata.robots });
  setMeta('meta[property="og:title"]', { property: 'og:title', content: metadata.title });
  setMeta('meta[property="og:description"]', { property: 'og:description', content: metadata.description });
  setMeta('meta[property="og:type"]', { property: 'og:type', content: metadata.pageType === 'product' ? 'product' : 'website' });
  setMeta('meta[property="og:url"]', { property: 'og:url', content: canonicalUrl });
  setMeta('meta[name="twitter:card"]', { name: 'twitter:card', content: metadata.imageUrl ? 'summary_large_image' : 'summary' });
  setMeta('meta[name="twitter:title"]', { name: 'twitter:title', content: metadata.title });
  setMeta('meta[name="twitter:description"]', { name: 'twitter:description', content: metadata.description });
  if (metadata.imageUrl) {
    setMeta('meta[property="og:image"]', { property: 'og:image', content: metadata.imageUrl });
    setMeta('meta[property="og:image:alt"]', { property: 'og:image:alt', content: metadata.imageAlt ?? metadata.title });
    setMeta('meta[name="twitter:image"]', { name: 'twitter:image', content: metadata.imageUrl });
  } else {
    removeMeta('meta[property="og:image"]'); removeMeta('meta[property="og:image:alt"]'); removeMeta('meta[name="twitter:image"]');
  }
  let canonical = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
  if (!canonical) { canonical = document.createElement('link'); canonical.rel = 'canonical'; document.head.appendChild(canonical); }
  canonical.href = canonicalUrl;

  setSchema('sulocraft-breadcrumb-schema', metadata.breadcrumbs.length ? {
    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
    itemListElement: metadata.breadcrumbs.map((item, index) => ({ '@type': 'ListItem', position: index + 1, name: item.name, item: new URL(item.path, window.location.origin).toString() })),
  } : undefined);
  setSchema('sulocraft-product-schema', product ? {
    '@context': 'https://schema.org', '@type': 'Product', name: product.name,
    description: product.description, image: product.images ?? [product.image], sku: String(product.id),
    category: product.category, brand: { '@type': 'Brand', name: 'Sulocraft' },
    aggregateRating: product.reviews > 0 ? { '@type': 'AggregateRating', ratingValue: product.rating, reviewCount: product.reviews } : undefined,
    offers: { '@type': 'Offer', priceCurrency: 'INR', price: product.price, availability: product.inStock === false ? 'https://schema.org/OutOfStock' : 'https://schema.org/InStock', url: canonicalUrl },
  } : undefined);
  setSchema('sulocraft-site-schema', metadata.pageType === 'website' ? {
    '@context': 'https://schema.org', '@graph': [
      { '@type': 'Organization', '@id': `${window.location.origin}/#organization`, name: 'Sulocraft', url: window.location.origin },
      { '@type': 'WebSite', '@id': `${window.location.origin}/#website`, name: 'Sulocraft', url: window.location.origin, publisher: { '@id': `${window.location.origin}/#organization` } },
    ],
  } : undefined);
}

export default function SeoManager({ page, pathname, product }: { page: AppPage; pathname: string; product?: Product | null }) {
  useEffect(() => {
    const controller = new AbortController();
    const fallback: SeoMetadata = {
      title: product?.name ? `${product.name} | Sulocraft` : document.title,
      description: product?.description ?? document.querySelector<HTMLMetaElement>('meta[name="description"]')?.content ?? '',
      canonicalPath: pathname,
      robots: PRIVATE_PAGES.has(page) ? 'noindex,nofollow' : 'index,follow',
      imageUrl: product?.images?.[0] ?? product?.image,
      imageAlt: product?.name,
      pageType: product ? 'product' : page === 'shop' ? 'collection' : 'website',
      breadcrumbs: [],
    };
    if (PRIVATE_PAGES.has(page)) { applyMetadata(fallback, product); return () => controller.abort(); }
    getSeoMetadata(pathname, controller.signal).then(metadata => applyMetadata(metadata, product)).catch(error => {
      if (!(error instanceof DOMException && error.name === 'AbortError')) applyMetadata(fallback, product);
    });
    return () => controller.abort();
  }, [page, pathname, product]);
  return null;
}
