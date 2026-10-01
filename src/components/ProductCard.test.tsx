import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ProductCard from './ProductCard';
import type { Product } from '../data/products';

afterEach(cleanup);

describe('ProductCard', () => {
  it('keeps every product image inside the same square frame', () => {
    const product: Product = {
      id: 1,
      name: 'Crochet Rose Bouquet',
      price: 2599,
      rating: 4.9,
      reviews: 128,
      image: '/rose.webp',
      category: 'Bouquets',
    };

    render(<ProductCard product={product} isWishlisted={false} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);

    expect(screen.getByTestId('product-card')).toHaveClass('flex', 'h-full', 'flex-col');
    expect(screen.getByTestId('product-image-frame')).toHaveClass('aspect-square', 'w-full', 'shrink-0');
    expect(screen.getByRole('img', { name: product.name })).toHaveClass('h-full', 'w-full', 'object-cover');
  });
});
