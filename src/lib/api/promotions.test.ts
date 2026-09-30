import { afterEach, describe, expect, it, vi } from 'vitest';
import { applyCoupon } from './promotions';

describe('coupon API', () => {
  afterEach(() => vi.unstubAllGlobals());
  it('applies a coupon using the guest or authenticated cookie session', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ code: 'SAVE10' }) });
    vi.stubGlobal('fetch', fetchMock);
    await applyCoupon('SAVE10');
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/v1/cart/apply-coupon'), expect.objectContaining({ method: 'POST', credentials: 'include', body: JSON.stringify({ code: 'SAVE10' }) }));
  });
});
