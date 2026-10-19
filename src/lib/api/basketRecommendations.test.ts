import { afterEach, expect, it, vi } from 'vitest';
import { getBasketDiscovery } from './basketRecommendations';
const product = { id: 1, name: 'Rose', slug: 'rose', image: '/rose.webp', price: 400, currency: 'INR', inStock: true };
afterEach(() => vi.unstubAllGlobals());
it('uses a bounded API request and rejects duplicate, unavailable, malformed and unsafe-link products', async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => [product, product, { ...product, id: 2, inStock: false }, { ...product, id: 3, slug: 'javascript:alert(1)' }, { ...product, id: 4, price: -1 }, { ...product, id: 5, image: '' }, null] });
  vi.stubGlobal('fetch', fetch);
  const result = await getBasketDiscovery();
  expect(fetch.mock.calls[0][0]).toContain('/products?sort=newest&limit=8');
  expect(result).toEqual([expect.objectContaining({ id: 1, name: 'Rose', price: 400, image: '/rose.webp' })]);
});
it('returns no invented products when empty and rejects unavailable/malformed API responses', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: true, json: async () => [] }).mockResolvedValueOnce({ ok: false }).mockResolvedValueOnce({ ok: true, json: async () => ({ products: [] }) }));
  expect(await getBasketDiscovery()).toEqual([]);
  await expect(getBasketDiscovery()).rejects.toThrow('unavailable');
  await expect(getBasketDiscovery()).rejects.toThrow('Invalid');
});
