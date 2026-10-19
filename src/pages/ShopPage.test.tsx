import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ShopPage from './ShopPage';
import type { SeoMetadata } from '../lib/api/seo';

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
      tags: ['birthday'],
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
  catalogue.products.splice(1);
  window.history.replaceState({}, '', '/');
});

describe('ShopPage filters', () => {
  it('renders the backend-provided category heading without changing the layout', () => {
    render(<ShopPage heading="Flowers" wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    expect(screen.getByRole('heading', { name: 'Flowers', level: 1 })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'All Products' })).not.toBeInTheDocument();
  });
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

  it('sorts products from the compact control beside breadcrumbs', () => {
    catalogue.products.push({ ...catalogue.products[0], id: 2, name: 'Affordable Bouquet', slug: 'affordable-bouquet', price: 499 });
    const { container } = render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    const sort = screen.getByLabelText('Sort by:');
    expect(sort.closest('.catalogue-navigation')).toBeInTheDocument();
    expect(sort.parentElement).toHaveClass('catalogue-sort');
    expect(container.querySelector('.catalogue-sort-value')).toBeNull();
    expect(screen.getByText('Sort by:')).toBeVisible();
    expect(container.querySelector('.catalogue-sort-display')).toHaveTextContent('Featured');
    expect(sort.closest('.catalogue-toolbar')).toBeNull();
    fireEvent.change(sort, { target: { value: 'Price: Low to High' } });
    expect(container.querySelector('[data-testid="catalogue-results"] h3')).toHaveTextContent('Affordable Bouquet');
    expect(container.querySelector('.catalogue-sort-display')).toHaveTextContent('Price: Low to High');
    fireEvent.change(sort, { target: { value: 'Price: High to Low' } });
    expect(container.querySelector('[data-testid="catalogue-results"] h3')).toHaveTextContent('Rose Bouquet');
  });

  it('keeps the full escaped category description after products', () => {
    window.history.replaceState({}, '', '/categories/flowers');
    const description = 'Full database description <img src=x onerror=alert(1)>';
    const metadata = { categoryEntity: { id: 1, name: 'Flowers', slug: 'flowers', description } } as SeoMetadata;
    const { container } = render(<ShopPage seoMetadata={metadata} heading="Flowers" wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    const copy = screen.getByText(description);
    expect(screen.getByTestId('catalogue-results').compareDocumentPosition(copy) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(container.querySelector('img[src="x"]')).toBeNull();
    expect(screen.getByText('Rose Bouquet')).toBeInTheDocument();
  });

  it('lets a phone user open filters, apply and remove a category, and close the drawer', () => {
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /^Filters$/ }));
    fireEvent.click(screen.getAllByRole('button', { name: 'Flowers, 1 products' })[1]);
    fireEvent.click(screen.getByRole('button', { name: 'Show 1 results' }));
    expect(screen.queryByRole('button', { name: 'Close filters' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Remove Flowers filter' }));
    expect(screen.queryByRole('button', { name: 'Remove Flowers filter' })).not.toBeInTheDocument();
    expect(screen.getByText('1 handmade creations')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^Filters$/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Close filters' }));
    expect(screen.queryByRole('button', { name: 'Close filters' })).not.toBeInTheDocument();
  });

  it('uses database-provided product tags for homepage occasion links', () => {
    catalogue.products.push({
      id: 2,
      name: 'Crochet Bunny',
      slug: 'crochet-bunny',
      price: 499,
      rating: 5,
      reviews: 0,
      image: '/bunny.webp',
      category: 'Amigurumi',
      primaryCategory: { name: 'Amigurumi', slug: 'amigurumi' },
      categories: [{ name: 'Amigurumi', slug: 'amigurumi' }],
      collections: [],
      tags: ['birthday', 'valentine'],
      customizable: false,
    });
    window.history.replaceState({}, '', '/shop?occasion=valentine');

    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);

    expect(screen.getByText('1 handmade creations')).toBeInTheDocument();
    expect(screen.getByText('Crochet Bunny')).toBeInTheDocument();
    expect(screen.queryByText('Rose Bouquet')).not.toBeInTheDocument();
  });
});
