import { act } from '@testing-library/react';
import { hydrateRoot } from 'react-dom/client';
import { renderToString } from 'react-dom/server';
import { describe, it, expect, vi } from 'vitest';
import { StaticRouter, MemoryRouter } from 'react-router';
import { CatalogueProvider } from '../../components/CatalogueProvider';
import ShopPage from '../../pages/ShopPage';
import { PublicBootstrapContext, type PublicBootstrap } from './bootstrap';

vi.mock('../api/catalogue', () => ({
  getProducts: () => new Promise(() => {}), getCategories: () => new Promise(() => {}), getCollections: () => new Promise(() => {}),
}));
describe('public snapshot hydration', () => {
  it('preserves the category-filtered initial HTML and API heading during hydration', async () => {
    const bootstrap = {
      path: '/categories/flowers', products: [
        { id: 1, name: 'API Flower', slug: 'api-flower', price: 2199, category: 'Flowers', rating: 0, reviews: 0, image: '/flower.png', categories: [{ name: 'Flowers', slug: 'flowers' }] },
        { id: 2, name: 'API Bunny', slug: 'api-bunny', price: 500, category: 'Toys', rating: 0, reviews: 0, image: '/bunny.png' },
      ], categories: [], collections: [], metadata: { h1: 'API Flowers' },
    } as unknown as PublicBootstrap;
    const page = <PublicBootstrapContext.Provider value={bootstrap}><CatalogueProvider>
      <ShopPage heading={bootstrap.metadata.h1} onAddToCart={() => {}} onToggleWishlist={() => {}} wishlist={[]} onProductClick={() => {}} />
    </CatalogueProvider></PublicBootstrapContext.Provider>;
    const container = document.createElement('div');
    container.innerHTML = renderToString(<StaticRouter location={bootstrap.path}>{page}</StaticRouter>);
    expect(container.textContent).toContain('API Flower');
    expect(container.textContent).not.toContain('API Bunny');
    const onRecoverableError = vi.fn();
    let root: ReturnType<typeof hydrateRoot>;
    await act(async () => { root = hydrateRoot(container, <MemoryRouter initialEntries={[`${bootstrap.path}/`]}>{page}</MemoryRouter>, { onRecoverableError }); });
    expect(onRecoverableError).not.toHaveBeenCalled();
    expect(container.querySelector('h1')?.textContent).toBe('API Flowers');
    await act(async () => root!.unmount());
  });
});
