import { afterEach, describe, expect, it, vi } from 'vitest';
import { saveProduct, uploadPhoto } from './catalogue';
afterEach(() => vi.unstubAllGlobals());
describe('Admin catalogue transport', () => {
  it('sends uploaded bytes as multipart with session credentials and no JSON content type', async () => {
    const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ key: 'products/new.webp', url: 'https://images.example/photo.webp' }) });
    vi.stubGlobal('fetch', fetch);
    const file = new File(['bytes'], 'photo.webp', { type: 'image/webp' });
    expect(await uploadPhoto(file)).toEqual({ key: 'products/new.webp', url: 'https://images.example/photo.webp' });
    const init = fetch.mock.calls[0][1];
    expect(init.credentials).toBe('include'); expect(init.body.get('file')).toBe(file);
    expect(init.headers['Content-Type']).toBeUndefined();
  });
  it('rejects unauthorized product mutation instead of reporting success', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 403 }));
    await expect(saveProduct({ name: 'Test', description: '', primaryImage: '/test', galleryImages: [], categoryIds: [], tagIds: [] }, 1)).rejects.toThrow('403');
  });
});
