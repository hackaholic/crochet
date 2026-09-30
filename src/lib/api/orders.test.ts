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
});
