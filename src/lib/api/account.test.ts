import { afterEach, describe, expect, it, vi } from 'vitest';
import { accountProfileApi } from './account';

describe('account profile API', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('updates profile data with the authenticated browser session', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 1, status: 'ACTIVE', identities: [], createdAt: '' }) });
    vi.stubGlobal('fetch', fetchMock);

    await accountProfileApi.updateProfile({ name: 'Anu', email: 'anu@example.com' });

    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/v1/account/profile'), expect.objectContaining({
      method: 'PATCH',
      credentials: 'include',
      body: JSON.stringify({ name: 'Anu', email: 'anu@example.com' }),
    }));
  });
});
