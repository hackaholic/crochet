import { afterEach, expect, it, vi } from 'vitest';
afterEach(() => { vi.unstubAllEnvs(); vi.resetModules(); });
it('uses same-origin API paths for any local browser hostname when base is unset', async () => {
  vi.stubEnv('VITE_API_BASE_URL', '');
  vi.resetModules();
  const { apiUrl } = await import('./client');
  for (const path of ['/products', '/cart/items', '/auth/logout', '/orders']) {
    expect(apiUrl(path)).toBe(`/api/v1${path}`);
  }
});
it('retains the configured remote API base for deployed environments', async () => {
  vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.test/api/v1/');
  vi.resetModules();
  const { apiUrl } = await import('./client');
  expect(apiUrl('/products')).toBe('https://api.example.test/api/v1/products');
});
