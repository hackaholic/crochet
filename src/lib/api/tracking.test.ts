import { afterEach, expect, it, vi } from 'vitest';
import { getOrderTracking } from './tracking';
afterEach(() => vi.unstubAllGlobals());
it('uses encoded order ID, credentialed no-store request and guest header instead of token URL', async () => {
  const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ orderNumber: 'A/B' }) });
  vi.stubGlobal('fetch', fetcher);
  const signal = new AbortController().signal;
  await getOrderTracking('A/B', signal, 'secret-test-token');
  expect(fetcher).toHaveBeenCalledWith('/api/v1/orders/A%2FB/tracking', { credentials: 'include', cache: 'no-store', signal, headers: { 'X-Guest-Order-Token': 'secret-test-token' } });
});
it('returns generic error instead of exposing denied response data', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));
  await expect(getOrderTracking('other-order', new AbortController().signal)).rejects.toThrow('Tracking unavailable');
});
it('requests recovery without exposing a development link response', async () => {
  const fetcher = vi.fn().mockResolvedValue({ ok: true });
  vi.stubGlobal('fetch', fetcher);
  const { requestTrackingLink } = await import('./tracking');
  expect(await requestTrackingLink(' TEST-1 ', ' guest@example.com ')).toBeUndefined();
  expect(fetcher).toHaveBeenCalledWith('/api/v1/orders/tracking/request-link', expect.objectContaining({ method: 'POST', cache: 'no-store', body: JSON.stringify({ orderNumber: 'TEST-1', email: 'guest@example.com' }) }));
});
