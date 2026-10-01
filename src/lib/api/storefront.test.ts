import { afterEach, describe, expect, it, vi } from 'vitest';
import { getStorefrontContent } from './storefront';

afterEach(() => vi.restoreAllMocks());

describe('getStorefrontContent', () => {
  it('returns database-managed brand settings and hero campaigns', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        brand: { name: 'Sulocraft', ownerName: 'Anupama' },
        heroCampaigns: [{
          id: 1,
          title: 'Festival collection',
          description: 'A scheduled campaign',
          imageUrl: 'https://images.sulocraft.com/campaigns/festival.webp',
          imageAlt: 'Festival crochet collection',
          priority: 1,
        }],
      }),
    }));

    const content = await getStorefrontContent();

    expect(content.brand.ownerName).toBe('Anupama');
    expect(content.heroCampaigns[0].imageUrl).toBe('https://images.sulocraft.com/campaigns/festival.webp');
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/storefront'), { signal: undefined });
  });

  it('rejects an invalid campaign response instead of silently hardcoding content', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ brand: {}, heroCampaigns: null }) }));
    await expect(getStorefrontContent()).rejects.toThrow('unexpected shape');
  });
});
