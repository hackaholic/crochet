import type { SeoMetadata } from '../api/seo';
import type { Product } from '../../data/products';

/** Emit only the current, visible DB-backed offer; never seed counters or policy defaults. */
export function buildProductSchema(metadata: SeoMetadata, url: string, visibleProduct?: Product | null) {
  const entity = metadata.productEntity;
  if (metadata.robots.includes('noindex') || metadata.pageType !== 'product' || !entity || !visibleProduct) return undefined;
  if (entity.id !== visibleProduct.id || entity.price !== visibleProduct.price || entity.name !== visibleProduct.name) return undefined;
  if (!entity.sku || !Number.isFinite(entity.price) || entity.price < 0 || !entity.currency) return undefined;
  return {
    '@context': 'https://schema.org', '@type': 'Product',
    name: entity.name, description: visibleProduct.description || metadata.description,
    image: entity.imageUrls.filter(image => /^https?:\/\//i.test(image)),
    sku: entity.sku, brand: { '@type': 'Brand', name: entity.brand },
    category: entity.primaryCategoryName || undefined,
    offers: {
      '@type': 'Offer', priceCurrency: entity.currency, price: entity.price,
      availability: entity.inStock ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock', url,
    },
    // Genuine review provenance must be returned by5.22 before ratings are published.
    // Approved shipping/return schema belongs to the merchant policy contract, not defaults.
  };
}
