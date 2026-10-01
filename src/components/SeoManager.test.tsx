import { cleanup, render, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import SeoManager from './SeoManager';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe('SeoManager', () => {
  it('marks private routes noindex without requesting public metadata', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    render(<SeoManager page="checkout" pathname="/checkout" />);
    await waitFor(() => expect(document.querySelector('meta[name="robots"]')).toHaveAttribute('content', 'noindex,nofollow'));
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('renders backend metadata, social tags, canonical URL, and breadcrumbs', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
      title: 'Crochet Flowers | Sulocraft', description: 'Handmade crochet flower gifts', canonicalPath: '/shop/flowers',
      robots: 'index,follow', imageUrl: 'https://images.sulocraft.com/seo/flowers.webp', imageAlt: 'Crochet flowers',
      pageType: 'collection', breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Flowers', path: '/shop/flowers' }],
    }) }));
    render(<SeoManager page="shop" pathname="/shop/flowers" />);
    await waitFor(() => expect(document.title).toBe('Crochet Flowers | Sulocraft'));
    expect(document.querySelector('meta[property="og:image"]')).toHaveAttribute('content', 'https://images.sulocraft.com/seo/flowers.webp');
    expect(document.querySelector('link[rel="canonical"]')).toHaveAttribute('href', expect.stringContaining('/shop/flowers'));
    expect(document.getElementById('sulocraft-breadcrumb-schema')?.textContent).toContain('BreadcrumbList');
  });
});
