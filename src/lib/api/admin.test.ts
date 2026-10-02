import { afterEach, describe, expect, it, vi } from 'vitest';
import { getAdminAnalytics } from './admin';
describe('admin API client', () => { afterEach(() => vi.unstubAllGlobals()); it('uses the authenticated browser session', async () => { const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ totalRevenue: 0 }) }); vi.stubGlobal('fetch', fetchMock); await getAdminAnalytics(); expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/v1/admin/analytics'), { credentials: 'include', headers: {} }); }); });
