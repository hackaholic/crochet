import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import WishlistPage from './WishlistPage';
import { useCatalogue } from '../components/CatalogueProvider';
import { getProductDiscovery } from '../lib/api/productDiscovery';

vi.mock('../components/CatalogueProvider', () => ({ useCatalogue: vi.fn() }));
vi.mock('../lib/api/productDiscovery', () => ({ getProductDiscovery: vi.fn() }));

const product = (id: number) => ({ id, name: `Product ${id}`, slug: `product-${id}`, price: 400, image: '/rose.webp', category: 'Flowers', rating: 0, reviews: 0 });
const props = (wishlist: number[]) => ({ wishlist, onAddToCart: vi.fn(), onToggleWishlist: vi.fn(), onProductClick: vi.fn(), onNavigate: vi.fn() as never });

afterEach(() => { cleanup(); vi.resetAllMocks(); });

it('renders API discovery beneath saved products and excludes saved IDs', async () => {
  vi.mocked(useCatalogue).mockReturnValue({ products: [product(1)], categories: [], collections: [], loading: false, error: false, retry: vi.fn() });
  vi.mocked(getProductDiscovery).mockResolvedValue({ sections: [{ id: 'newest', title: 'New arrivals', strategy: 'newest', products: [product(1), product(2)] }], nextCursor: null });
  render(<WishlistPage {...props([1])} />);
  expect(await screen.findByRole('heading', { name: 'New arrivals' })).toBeVisible();
  expect(screen.getByText('Product 1')).toBeVisible();
  expect(screen.getAllByText('Product 2')).toHaveLength(1);
  expect(screen.queryByRole('heading', { name: 'Your wishlist is empty' })).not.toBeInTheDocument();
  expect(getProductDiscovery).toHaveBeenCalledWith('wishlist', null, expect.any(AbortSignal));
});

it('keeps the empty state and retries failed public discovery without hiding it', async () => {
  vi.mocked(useCatalogue).mockReturnValue({ products: [], categories: [], collections: [], loading: false, error: false, retry: vi.fn() });
  vi.mocked(getProductDiscovery).mockRejectedValue(new Error('upstream detail'));
  render(<WishlistPage {...props([])} />);
  const emptyHeading = screen.getByRole('heading', { name: 'Your wishlist is empty' });
  expect(emptyHeading).toBeVisible();
  const compactEmptyState = emptyHeading.parentElement?.parentElement;
  expect(compactEmptyState).toHaveClass('flex', 'py-2');
  expect(compactEmptyState?.parentElement).toHaveClass('pt-4');
  expect(compactEmptyState?.parentElement?.firstElementChild).toHaveClass('mb-3');
  expect(await screen.findByRole('alert')).toHaveTextContent('More creations could not load. Please try again.');
  expect(screen.queryByText('upstream detail')).not.toBeInTheDocument();
});
