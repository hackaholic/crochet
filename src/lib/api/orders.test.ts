import { afterEach, describe, expect, it, vi } from 'vitest';
import { accountApi } from './orders';

describe('account address API', () => {
  afterEach(() => vi.unstubAllGlobals());
  it('creates a saved address with session cookies', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 1 }) });
    vi.stubGlobal('fetch', fetchMock);
    await accountApi.createAddress({ name: 'Anu', phone: '9999999999', line1: 'MG Road', city: 'Bengaluru', state: 'Karnataka', postalCode: '560001' });
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/v1/addresses'), expect.objectContaining({ method: 'POST', credentials: 'include' }));
  });

  it('updates a saved address with PATCH and session cookies', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 1, line1: 'Updated Road' }) });
    vi.stubGlobal('fetch', fetchMock);
    await accountApi.updateAddress(1, { line1: 'Updated Road', city: 'Bengaluru' });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/addresses/1'),
      expect.objectContaining({
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ line1: 'Updated Road', city: 'Bengaluru' }),
      })
    );
  });

  it('deletes a saved address with DELETE and session cookies', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 204 });
    vi.stubGlobal('fetch', fetchMock);
    await accountApi.deleteAddress(1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/addresses/1'),
      expect.objectContaining({ method: 'DELETE', credentials: 'include' })
    );
  });

  it('sets a default address with POST and session cookies', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 1, isDefault: true }) });
    vi.stubGlobal('fetch', fetchMock);
    await accountApi.setDefaultAddress(1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/addresses/1/default'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })
    );
  });
});
