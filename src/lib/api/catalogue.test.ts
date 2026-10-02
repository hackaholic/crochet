import { afterEach, describe, expect, it, vi } from 'vitest';
import { flattenCategories, getCategories, getCollections, getProducts, getSearchSuggestions, recordSearchQuery, searchProducts } from './catalogue';

describe('catalogue API adapter', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('maps Gemini catalogue fields into storefront products', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [{ id: 1, name: 'Rose', slug: 'rose', price: 2599, currency: 'INR', rating: 4.9, reviewCount: 12, image: 'rose.jpg', imageUrls: ['rose.jpg', 'rose-2.jpg'], category: 'Flowers', primaryCategory: { name: 'Bouquets', slug: 'bouquets' }, categories: [{ name: 'Flowers', slug: 'flowers' }, { name: 'Bouquets', slug: 'bouquets' }], collections: [{ name: 'Birthday Gifts', slug: 'birthday-gifts' }], badge: 'Bestseller', tags: ['romantic'], customizable: true }] }));
    await expect(getProducts()).resolves.toEqual([expect.objectContaining({ id: 1, slug: 'rose', reviews: 12, images: ['rose.jpg', 'rose-2.jpg'], category: 'Bouquets', primaryCategory: { name: 'Bouquets', slug: 'bouquets' }, collections: [{ name: 'Birthday Gifts', slug: 'birthday-gifts' },], customizable: true })]);
  });

  it('loads and flattens backend-managed category trees', async () => {
    const tree = [{ id: 1, name: 'Flowers', slug: 'flowers', displayOrder: 1, isActive: true, productCount: 1, children: [{ id: 2, name: 'Bouquets', slug: 'bouquets', displayOrder: 1, isActive: true, productCount: 1, children: [] }] }];
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => tree }));
    await expect(getCategories()).resolves.toEqual(tree);
    expect(flattenCategories(tree)).toHaveLength(2);
  });

  it('loads gift and merchandising collections independently from categories', async () => {
    const collections = [{ id: 1, name: 'Birthday Gifts', slug: 'birthday-gifts', displayOrder: 1 }];
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => collections }));
    await expect(getCollections()).resolves.toEqual(collections);
  });

  it('rejects unsuccessful responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await expect(getProducts()).rejects.toThrow('503');
  });

  it('searches the backend catalogue and maps returned products', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ id: 2, name: 'Crochet Rose', slug: 'crochet-rose', price: 499, currency: 'INR', image: 'rose.webp', category: 'Flowers' }],
    });
    vi.stubGlobal('fetch', fetchMock);
    const controller = new AbortController();

    const results = await searchProducts('  rose bouquet  ', { limit: 6, signal: controller.signal });

    expect(fetchMock).toHaveBeenCalledWith('/api/v1/products/search?q=rose+bouquet&limit=6', { signal: controller.signal });
    expect(results).toEqual([expect.objectContaining({ id: 2, slug: 'crochet-rose', name: 'Crochet Rose', image: 'rose.webp' })]);
  });

  it('does not send a request for a blank product search', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    await expect(searchProducts('   ')).resolves.toEqual([]);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('reports database search errors without swallowing them', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await expect(searchProducts('rose')).rejects.toThrow('Product search failed (503)');
  });

  it('loads backend-ranked suggestion terms and maps suggested products', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        trending_keywords: [{ term: 'crochet flowers' }],
        trending_products: [{ id: 9, name: 'Sunflower Bouquet', slug: 'sunflower-bouquet', price: 699, currency: 'INR', image: 'sunflower.webp', category: 'Flowers' }],
      }),
    });
    vi.stubGlobal('fetch', fetchMock);
    const controller = new AbortController();
    await expect(getSearchSuggestions(controller.signal)).resolves.toEqual({
      trending_keywords: [{ term: 'crochet flowers' }],
      trending_products: [expect.objectContaining({ id: 9, name: 'Sunflower Bouquet', category: 'Flowers' })],
    });
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/products/search/suggestions?keyword_limit=6&product_limit=4', { signal: controller.signal });
  });

  it('sends search analytics as a best-effort API event', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal('fetch', fetchMock);
    await recordSearchQuery(' crochet flowers ');
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/products/search/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'crochet flowers' }),
    });
  });
});
