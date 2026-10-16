import { cleanup, render, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import SeoManager from './SeoManager';

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); document.head.innerHTML = ''; });

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
    expect(document.querySelector('link[rel="alternate"][hreflang="en-IN"]')).toBeNull();
    expect(document.querySelector('link[rel="alternate"][hreflang="x-default"]')).toBeNull();
    expect(document.getElementById('sulocraft-breadcrumb-schema')?.textContent).toContain('BreadcrumbList');
  });

  it('deduplicates stale head tags and uses the configured API canonical and heading', async () => {
    document.head.innerHTML = '<meta name="robots" content="index,follow"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="https://old.example"><link rel="canonical" href="https://duplicate.example"><link rel="alternate" hreflang="en-US" href="https://old.example">';
    const onMetadata = vi.fn();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ title: 'Flowers', description: 'Actual category', h1: 'Flowers', canonicalPath: '/categories/flowers', canonicalUrl: 'https://sulocraft.com/categories/flowers', robots: 'index,follow', pageType: 'collection', breadcrumbs: [] }) }));
    render(<SeoManager page="shop" pathname="/categories/flowers" onMetadata={onMetadata} />);
    await waitFor(() => expect(onMetadata).toHaveBeenCalledWith(expect.objectContaining({ h1: 'Flowers' })));
    expect(document.querySelectorAll('meta[name="robots"]')).toHaveLength(1);
    expect(document.querySelectorAll('link[rel="canonical"]')).toHaveLength(1);
    expect(document.querySelector('link[rel="canonical"]')).toHaveAttribute('href', 'https://sulocraft.com/categories/flowers');
    expect(document.querySelectorAll('link[rel="alternate"][hreflang]')).toHaveLength(0);
  });

  it('fails conservatively when the public metadata request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('unavailable')));
    render(<SeoManager page="shop" pathname="/categories/flowers" />);
    await waitFor(() => expect(document.querySelector('meta[name="robots"]')).toHaveAttribute('content', 'noindex,nofollow'));
  });

  it('ignores a stale response after changing route and rejects unsafe canonical protocols', async () => {
    let resolveOld!: (value: unknown) => void;
    const body = { title: 'New category', description: '', canonicalPath: '/categories/new', canonicalUrl: 'javascript:alert(1)', robots: 'index,follow', pageType: 'collection', breadcrumbs: [] };
    vi.stubGlobal('fetch', vi.fn().mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve; })).mockResolvedValueOnce({ ok: true, json: async () => body }));
    const view = render(<SeoManager page="shop" pathname="/categories/old" />);
    view.rerender(<SeoManager page="shop" pathname="/categories/new" />);
    await waitFor(() => expect(document.title).toBe('New category'));
    resolveOld({ ok: true, json: async () => ({ ...body, title: 'Old category' }) });
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(document.title).toBe('New category');
    expect(document.querySelector('link[rel="canonical"]')?.getAttribute('href')).not.toMatch(/^javascript:/);
  });

  it('renders the real Product offer and omits unproven policies, ratings and invisible FAQs', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      title: 'Forever Rose Bouquet | Sulocraft',
      description: 'Handcrafted rose bouquet',
      canonicalPath: '/products/forever-rose-bouquet',
      productEntity: { id: 101, name: 'Forever Rose Bouquet', slug: 'forever-rose-bouquet', sku: 'ROSE-REAL-001', price: 1599, currency: 'INR', inStock: true, inventoryStatus: 'IN_STOCK', brand: 'Sulocraft', imageUrls: ['https://images.sulocraft.com/products/rose.png'], variants: [], aggregateRating: {ratingValue: 4.9, reviewCount: 12} },
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
    expect(productSchema.sku).toBe('ROSE-REAL-001');
    expect(productSchema.offers.price).toBe(1599);
    expect(productSchema.offers.hasMerchantReturnPolicy).toBeUndefined();
    expect(productSchema.offers.shippingDetails).toBeUndefined();
    expect(productSchema.offers.priceValidUntil).toBeUndefined();
    expect(productSchema.aggregateRating).toBeUndefined();
    expect(document.getElementById('sulocraft-faq-schema')).toBeNull();
  });
});

describe('social navigation parity', () => {
  it('uses the shared initial-HTML contract and removes stale image fields on image-less/private routes', async () => {
    const metadata = {title:'Actual bouquet',description:'Saved summary',canonicalPath:'/products/bouquet',canonicalUrl:'https://store.test/products/bouquet',robots:'index,follow',pageType:'product',breadcrumbs:[],imageUrl:'https://media.test/bouquet.png',imageAlt:'Red crochet roses',imageWidth:1086,imageHeight:1448,imageType:'image/png'};
    vi.stubGlobal('fetch',vi.fn().mockResolvedValueOnce({ok:true,json:async()=>metadata}).mockResolvedValueOnce({ok:true,json:async()=>({...metadata,title:'Flowers',canonicalPath:'/categories/flowers',imageUrl:null})}));
    const view=render(<SeoManager page="product" pathname="/products/bouquet" />);
    await waitFor(()=>expect(document.title).toBe(metadata.title));
    const {socialMetadata}=await import('../lib/seo/socialMetadata.mjs');
    for(const [key,value] of Object.entries(socialMetadata(metadata as any,metadata.canonicalUrl))) {
      expect(document.querySelector(`meta[${key.startsWith('og:')?'property':'name'}="${key}"]`)).toHaveAttribute('content',value);
    }
    view.rerender(<SeoManager page="shop" pathname="/categories/flowers" />);
    await waitFor(()=>expect(document.title).toBe('Flowers'));
    expect(document.querySelectorAll('meta[property^="og:image"],meta[name^="twitter:image"]')).toHaveLength(0);
    expect(document.querySelector('meta[name="twitter:card"]')).toHaveAttribute('content','summary');
    view.rerender(<SeoManager page="account" pathname="/account" />);
    await waitFor(()=>expect(document.title).toBe('Sulocraft'));
    expect(document.querySelector('meta[property="og:description"]')).toHaveAttribute('content','');
    expect(document.querySelectorAll('meta[property="og:title"]')).toHaveLength(1);
  });
});
