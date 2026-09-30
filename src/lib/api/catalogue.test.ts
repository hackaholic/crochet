import { afterEach, describe, expect, it, vi } from 'vitest';
import { getProducts } from './catalogue';

describe('catalogue API adapter', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('maps Gemini catalogue fields into storefront products', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [{ id: 1, name: 'Rose', slug: 'rose', price: 2599, currency: 'INR', rating: 4.9, reviewCount: 12, image: 'rose.jpg', imageUrls: ['rose.jpg', 'rose-2.jpg'], category: 'Flowers', badge: 'Bestseller', tags: ['romantic'], customizable: true }] }));
    await expect(getProducts()).resolves.toEqual([expect.objectContaining({ id: 1, slug: 'rose', reviews: 12, images: ['rose.jpg', 'rose-2.jpg'], customizable: true })]);
  });

  it('rejects unsuccessful responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await expect(getProducts()).rejects.toThrow('503');
  });
});
