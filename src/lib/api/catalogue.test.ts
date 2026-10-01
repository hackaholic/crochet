import { afterEach, describe, expect, it, vi } from 'vitest';
import { flattenCategories, getCategories, getCollections, getProducts } from './catalogue';

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
});
