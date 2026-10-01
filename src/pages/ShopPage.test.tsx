import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ShopPage from './ShopPage';

const catalogue = vi.hoisted(() => ({
  products: [
    {
      id: 1,
      name: 'Rose Bouquet',
      slug: 'rose-bouquet',
      price: 899,
      rating: 5,
      reviews: 4,
      image: '/rose.webp',
      category: 'Bouquets',
      primaryCategory: { name: 'Bouquets', slug: 'bouquets' },
      categories: [{ name: 'Bouquets', slug: 'bouquets' }],
      collections: [{ name: 'Birthday Gifts', slug: 'birthday-gifts' }],
      customizable: true,
    },
  ],
  categories: [
    {
      id: 1,
      name: 'Flowers',
      slug: 'flowers',
      displayOrder: 1,
      isActive: true,
      productCount: 1,
      children: [
        { id: 2, name: 'Bouquets', slug: 'bouquets', parentId: 1, displayOrder: 1, isActive: true, productCount: 1, children: [] },
        { id: 3, name: 'Lilies', slug: 'lilies', parentId: 1, displayOrder: 2, isActive: true, productCount: 0, children: [] },
      ],
    },
  ],
  collections: [
    { id: 1, name: 'Birthday Gifts', slug: 'birthday-gifts', displayOrder: 1, productCount: 1 },
    { id: 2, name: 'Gifts for Him', slug: 'gifts-for-him', displayOrder: 2, productCount: 0 },
  ],
}));

vi.mock('../components/CatalogueProvider', () => ({ useCatalogue: () => catalogue }));

afterEach(() => {
  cleanup();
  window.history.replaceState({}, '', '/');
});

describe('ShopPage filters', () => {
  it('keeps the listing title, result count, and sort control together in the compact toolbar', () => {
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);

    expect(screen.getByRole('heading', { name: 'All Products' })).toBeInTheDocument();
    expect(screen.getByText('1 handmade creations')).toBeInTheDocument();
    expect(screen.getByLabelText('Sort by:')).toBeInTheDocument();
  });

  it('shows only populated options, supports parent categories, and preserves expanded panels', () => {
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);

    expect(screen.getByRole('button', { name: 'Flowers, 1 products' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Bouquets, 1 products' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Lilies/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Under ₹299/ })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Flowers, 1 products' }));
    expect(screen.getByText('1 handmade creations')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Flowers, 1 products' }));

    fireEvent.click(screen.getByRole('button', { name: 'Occasion' }));
    fireEvent.click(screen.getByRole('button', { name: 'Birthday Gifts, 1 products' }));
    expect(screen.getByRole('button', { name: 'Birthday Gifts, 1 products' })).toBeVisible();
    expect(screen.queryByRole('button', { name: /Gifts for Him/ })).not.toBeInTheDocument();
  });
});
