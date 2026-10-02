import { cleanup, render, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import SeoManager from './SeoManager';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe('SeoManager', () => {
  it('marks private routes noindex without requesting public metadata', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    render(<SeoManager page="checkout" pathname="/checkout" />);
    await waitFor(() => expect(document.querySelector('meta[name="robots"]')).toHaveAttribute('content', 'noindex,nofollow'));
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('renders backend metadata, social tags, canonical URL, and breadcrumbs', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      title: 'Crochet Flowers | Sulocraft', description: 'Handmade crochet flower gifts', canonicalPath: '/shop/flowers',
      robots: 'index,follow', imageUrl: 'https://images.sulocraft.com/seo/flowers.webp', imageAlt: 'Crochet flowers',
      pageType: 'collection', breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Flowers', path: '/shop/flowers' }],
    }) }));
    render(<SeoManager page="shop" pathname="/shop/flowers" />);
    await waitFor(() => expect(document.title).toBe('Crochet Flowers | Sulocraft'));
    expect(document.querySelector('meta[property="og:image"]')).toHaveAttribute('content', 'https://images.sulocraft.com/seo/flowers.webp');
    expect(document.querySelector('link[rel="canonical"]')).toHaveAttribute('href', expect.stringContaining('/shop/flowers'));
    expect(document.querySelector('link[rel="alternate"][hreflang="en-IN"]')).toHaveAttribute('href', expect.stringContaining('/shop/flowers'));
    expect(document.querySelector('link[rel="alternate"][hreflang="x-default"]')).toHaveAttribute('href', expect.stringContaining('/shop/flowers'));
    expect(document.getElementById('sulocraft-breadcrumb-schema')?.textContent).toContain('BreadcrumbList');
  });

  it('renders Product schema with return policy, shipping details, and FAQ schema', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      title: 'Forever Rose Bouquet | Sulocraft',
      description: 'Handcrafted rose bouquet',
      canonicalPath: '/products/forever-rose-bouquet',
      robots: 'index,follow',
      imageUrl: 'https://images.sulocraft.com/products/rose.png',
      pageType: 'product',
      breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Flowers', path: '/categories/flowers' }],
      faqs: [
        { question: 'How do I care for this bouquet?', answer: 'Spot clean with mild damp cloth.' },
      ],
      shippingInfo: { freeShippingThreshold: 999, standardFee: 100, currency: 'INR', transitTime: '3-5 business days', country: 'IN' },
      returnPolicy: { returnWindowDays: 7, policyUrl: '/info/refund', returnFees: 'Free for damaged items' },
    }) }));

    const mockProduct = {
      id: 101,
      name: 'Forever Rose Bouquet',
      description: '100% handcrafted crochet flower bouquet',
      price: 1599,
      category: 'Flowers',
      image: 'https://images.sulocraft.com/products/rose.png',
      images: ['https://images.sulocraft.com/products/rose.png'],
      rating: 4.9,
      reviews: 12,
      inStock: true,
    } as any;

    render(<SeoManager page="product" pathname="/products/forever-rose-bouquet" product={mockProduct} />);

    await waitFor(() => expect(document.title).toBe('Forever Rose Bouquet | Sulocraft'));

    const productSchema = JSON.parse(document.getElementById('sulocraft-product-schema')!.textContent!);
    expect(productSchema['@type']).toBe('Product');
    expect(productSchema.offers.hasMerchantReturnPolicy.merchantReturnDays).toBe(7);
    expect(productSchema.offers.shippingDetails.shippingRate.value).toBe(0); // free above 999

    const faqSchema = JSON.parse(document.getElementById('sulocraft-faq-schema')!.textContent!);
    expect(faqSchema['@type']).toBe('FAQPage');
    expect(faqSchema.mainEntity[0].name).toBe('How do I care for this bouquet?');
    expect(faqSchema.mainEntity[0].acceptedAnswer.text).toBe('Spot clean with mild damp cloth.');
  });
});
