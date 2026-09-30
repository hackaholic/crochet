import { afterEach, describe, expect, it, vi } from 'vitest';
import { wishlistApi } from './wishlist';

describe('wishlist API client', () => {
  afterEach(() => vi.unstubAllGlobals());
  it('adds by product ID with session cookies', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ items: [], totalItems: 0 }) });
    vi.stubGlobal('fetch', fetchMock);
    await wishlistApi.add(7);
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/v1/wishlist/items'), expect.objectContaining({ method: 'POST', credentials: 'include', body: JSON.stringify({ productId: 7 }) }));
  });
});
