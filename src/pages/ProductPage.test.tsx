import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ProductPage from './ProductPage';
import type { Product } from '../data/products';

vi.mock('../components/CatalogueProvider', () => ({ useCatalogue: () => ({ products: [] }) }));

const product: Product = {
  id: 42,
  name: 'Crochet Rose Bouquet',
  slug: 'crochet-rose-bouquet',
  price: 1299,
  rating: 4.8,
  reviews: 12,
  image: '/rose.webp',
  images: ['/rose.webp'],
  category: 'Flowers',
  customizable: true,
};

afterEach(cleanup);

describe('ProductPage options', () => {
  it('does not show hardcoded color choices while product color variants are unavailable', () => {
    render(
      <ProductPage
        product={product}
        onAddToCart={vi.fn()}
        onToggleWishlist={vi.fn()}
        wishlist={[]}
        onProductClick={vi.fn()}
        onNavigate={vi.fn()}
      />,
    );

    expect(screen.queryByText('Flower Color')).not.toBeInTheDocument();
    expect(screen.queryByText('50+ options available')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: product.name })).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'Add to Basket' })).toHaveLength(2);
  });
});
