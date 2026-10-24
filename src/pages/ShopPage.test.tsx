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
    expect(screen.getByText('1 creations')).toBeInTheDocument();
    expect(screen.getByLabelText('Sort by:')).toBeInTheDocument();
  });

  it('shows only populated options, supports parent categories, and preserves expanded panels', () => {
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);

    expect(screen.getByRole('button', { name: 'Flowers, 1 products' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Bouquets, 1 products' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Lilies/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Under ₹299/ })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Flowers, 1 products' }));
    expect(screen.getByText('1 creations')).toBeInTheDocument();
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
    expect(sort.closest('.catalogue-summary')).toBeNull();
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

  it('lets a phone user deselect categories in the drawer without active chips', () => {
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: /^Filters$/ }));
    const flowers = screen.getAllByRole('button', { name: 'Flowers, 1 products' })[1];
    fireEvent.click(flowers);
    expect(flowers).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('heading', { name: 'Flowers', level: 1 })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Remove .* filter/ })).not.toBeInTheDocument();
    fireEvent.click(flowers);
    expect(flowers).toHaveAttribute('aria-pressed', 'false');
    expect(screen.getByRole('heading', { name: 'All Products', level: 1 })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Close filters' }));
    expect(screen.queryByRole('button', { name: 'Close filters' })).not.toBeInTheDocument();
  });

  it('shows Filtered Products for multiple shop categories, and clear resets them', () => {
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Flowers, 1 products' }));
    fireEvent.click(screen.getByRole('button', { name: 'Bouquets, 1 products' }));
    expect(screen.getByRole('heading', { name: 'Filtered Products', level: 1 })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Clear all filters (2)' }));
    expect(screen.getByRole('heading', { name: 'All Products', level: 1 })).toBeInTheDocument();
  });

  it('keeps category route scope despite conflicting query and clearing filters', () => {
    catalogue.products.push({ ...catalogue.products[0], id: 2, name: 'Unrelated Toy', slug: 'toy', price: 100, primaryCategory: { name: 'Toys', slug: 'toys' }, categories: [{ name: 'Toys', slug: 'toys' }] });
    window.history.replaceState({}, '', '/categories/flowers?category=toys');
    render(<ShopPage heading="Flowers" wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    expect(screen.getByText('Rose Bouquet')).toBeInTheDocument();
    expect(screen.queryByText('Unrelated Toy')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Flowers, 1 products' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Under ₹299/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Bouquets, 1 products' }));
    fireEvent.click(screen.getByRole('button', { name: 'Clear all filters (1)' }));
    expect(screen.getByText('Rose Bouquet')).toBeInTheDocument();
    expect(screen.queryByText('Unrelated Toy')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Flowers', level: 1 })).toBeInTheDocument();
  });

  it('keeps unknown category routes empty rather than falling back to all products', () => {
    window.history.replaceState({}, '', '/categories/unknown?category=flowers');
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    expect(screen.getByText('No products match your filters')).toBeInTheDocument();
    expect(screen.queryByText('Rose Bouquet')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Clear Filters' }));
    expect(screen.queryByText('Rose Bouquet')).not.toBeInTheDocument();
  });

  it.each([
    ['/categories/flowers', '/categories/bouquets'],
    ['/shop?category=flowers', '/shop?category=bouquets'],
  ])('resets price when listing changes from %s to %s, retaining it for sorting', (from, to) => {
    window.history.replaceState({}, '', from);
    const props = { wishlist: [], onAddToCart: vi.fn(), onToggleWishlist: vi.fn(), onProductClick: vi.fn() };
    const { rerender } = render(<ShopPage {...props} />);
    fireEvent.change(screen.getByLabelText('Max ₹'), { target: { value: '499' } });
    fireEvent.blur(screen.getByLabelText('Max ₹'));
    expect(screen.queryByText('Rose Bouquet')).not.toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Sort by:'), { target: { value: 'Newest' } });
    expect(screen.getByLabelText('Max ₹')).toHaveValue(499);
    window.history.replaceState({}, '', to);
    rerender(<ShopPage {...props} />);
    expect(screen.getByLabelText('Min ₹')).toHaveValue(0);
    expect(screen.getByLabelText('Max ₹')).toHaveValue(100000);
    expect(screen.getByText('Rose Bouquet')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reset price' })).toBeDisabled();
  });

  it('does not cap the unfiltered catalogue at the slider maximum', () => {
    catalogue.products.push({ ...catalogue.products[0], id: 2, name: 'Premium Custom Piece', slug: 'premium', price: 200000 });
    render(<ShopPage wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    expect(screen.getByText('Premium Custom Piece')).toBeInTheDocument();
    fireEvent.change(screen.getByRole('slider', { name: 'Maximum price slider' }), { target: { value: '99999' } });
    expect(screen.queryByText('Premium Custom Piece')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Reset price' }));
    expect(screen.getByText('Premium Custom Piece')).toBeInTheDocument();
  });

  it('filters inclusive numeric prices within category scope and resets only price', () => {
    catalogue.products.push({ ...catalogue.products[0], id: 2, name: 'Affordable Bouquet', slug: 'affordable', price: 499 });
    window.history.replaceState({}, '', '/categories/flowers');
    render(<ShopPage heading="Flowers" wishlist={[]} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    fireEvent.change(screen.getByLabelText('Max ₹'), { target: { value: '499' } });
    fireEvent.blur(screen.getByLabelText('Max ₹'));
    expect(screen.getByText('Affordable Bouquet')).toBeInTheDocument();
    expect(screen.queryByText('Rose Bouquet')).not.toBeInTheDocument();
    expect(screen.getByText('1 creations')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Reset price' }));
    expect(screen.getByText('Rose Bouquet')).toBeInTheDocument();
    expect(screen.getByText('2 creations')).toBeInTheDocument();
    fireEvent.change(screen.getByRole('slider', { name: 'Minimum price slider' }), { target: { value: '900' } });
    expect(screen.getByText('No products match your filters')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Clear all filters (1)' }));
    expect(screen.getByRole('heading', { name: 'Flowers', level: 1 })).toBeInTheDocument();
    expect(screen.getByText('2 creations')).toBeInTheDocument();
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

    expect(screen.getByText('1 creations')).toBeInTheDocument();
    expect(screen.getByText('Crochet Bunny')).toBeInTheDocument();
    expect(screen.queryByText('Rose Bouquet')).not.toBeInTheDocument();
  });
});
