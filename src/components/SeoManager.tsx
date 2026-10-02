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

function setLink(rel: string, attributes: Record<string, string>) {
  const selector = `link[rel="${rel}"]${attributes.hreflang ? `[hreflang="${attributes.hreflang}"]` : ''}`;
  let element = document.head.querySelector<HTMLLinkElement>(selector);
  if (!element) {
    element = document.createElement('link');
    element.rel = rel;
    document.head.appendChild(element);
  }
  Object.entries(attributes).forEach(([name, value]) => element!.setAttribute(name, value));
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

  setLink('canonical', { href: canonicalUrl });
  setLink('alternate', { hreflang: 'en-IN', href: canonicalUrl });
  setLink('alternate', { hreflang: 'x-default', href: canonicalUrl });

  setSchema('sulocraft-breadcrumb-schema', metadata.breadcrumbs.length ? {
    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
    itemListElement: metadata.breadcrumbs.map((item, index) => ({ '@type': 'ListItem', position: index + 1, name: item.name, item: new URL(item.path, window.location.origin).toString() })),
  } : undefined);

  const freeThreshold = metadata.shippingInfo?.freeShippingThreshold ?? 999;
  const standardFee = metadata.shippingInfo?.standardFee ?? 100;
  const returnDays = metadata.returnPolicy?.returnWindowDays ?? 7;

  setSchema('sulocraft-product-schema', product ? {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.images ?? [product.image],
    sku: String(product.id),
    category: product.category,
    brand: { '@type': 'Brand', name: 'Sulocraft' },
    itemCondition: 'https://schema.org/NewCondition',
    aggregateRating: product.reviews > 0 ? {
      '@type': 'AggregateRating',
      ratingValue: product.rating,
      reviewCount: product.reviews,
    } : undefined,
    offers: {
      '@type': 'Offer',
      priceCurrency: 'INR',
      price: product.price,
      priceValidUntil: '2027-12-31',
      itemCondition: 'https://schema.org/NewCondition',
      availability: product.inStock === false ? 'https://schema.org/OutOfStock' : 'https://schema.org/InStock',
      url: canonicalUrl,
      hasMerchantReturnPolicy: {
        '@type': 'MerchantReturnPolicy',
        applicableCountry: 'IN',
        returnPolicyCategory: 'https://schema.org/MerchantReturnFiniteReturnWindow',
        merchantReturnDays: returnDays,
        returnMethod: 'https://schema.org/ReturnByMail',
        returnFees: 'https://schema.org/FreeReturn',
      },
      shippingDetails: {
        '@type': 'OfferShippingDetails',
        shippingRate: {
          '@type': 'MonetaryAmount',
          value: product.price >= freeThreshold ? 0 : standardFee,
          currency: 'INR',
        },
        shippingDestination: {
          '@type': 'DefinedRegion',
          addressCountry: 'IN',
        },
        deliveryTime: {
          '@type': 'ShippingDeliveryTime',
          handlingTime: { '@type': 'QuantitativeValue', minValue: 1, maxValue: 2, unitCode: 'd' },
          transitTime: { '@type': 'QuantitativeValue', minValue: 3, maxValue: 5, unitCode: 'd' },
        },
      },
    },
  } : undefined);

  setSchema('sulocraft-faq-schema', metadata.faqs?.length ? {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: metadata.faqs.map(faq => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  } : undefined);

  setSchema('sulocraft-site-schema', metadata.pageType === 'website' && !metadata.robots.includes('noindex') ? {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Organization',
        '@id': `${window.location.origin}/#organization`,
        name: 'Sulocraft',
        url: window.location.origin,
        logo: 'https://images.sulocraft.com/brand/logo.png',
        founder: {
          '@type': 'Person',
          name: 'Anupama Sharma',
        },
        foundingDate: '2026',
        sameAs: [
          'https://instagram.com/sulocraft',
          'https://facebook.com/sulocraft',
          'https://pinterest.com/sulocraft',
        ],
      },
      {
        '@type': 'WebSite',
        '@id': `${window.location.origin}/#website`,
        name: 'Sulocraft',
        url: window.location.origin,
        publisher: { '@id': `${window.location.origin}/#organization` },
        potentialAction: {
          '@type': 'SearchAction',
          target: `${window.location.origin}/shop?q={search_term_string}`,
          'query-input': 'required name=search_term_string',
        },
      },
    ],
  } : undefined);
}

export default function SeoManager({ page, pathname, product }: { page: AppPage; pathname: string; product?: Product | null }) {
  useEffect(() => {
    const controller = new AbortController();
    const fallback: SeoMetadata = {
      title: page === 'admin' ? 'Sulocraft Admin | Store management' : product?.name ? `${product.name} | Sulocraft` : document.title,
      description: page === 'admin' ? 'Private Sulocraft store administration.' : product?.description ?? document.querySelector<HTMLMetaElement>('meta[name="description"]')?.content ?? '',
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
