import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ProductCard from './ProductCard';
import type { Product } from '../data/products';

afterEach(cleanup);

describe('ProductCard', () => {
  it('keeps every product image inside the same portrait frame used by category highlights', () => {
    const product: Product = {
      id: 1,
      name: 'Crochet Rose Bouquet',
      price: 2599,
      rating: 4.9,
      reviews: 128,
      image: '/rose.webp',
      primaryImageMetadata: { url: '/rose.webp', width: 1086, height: 1448 },
      category: 'Bouquets',
    };

    const open = vi.fn(); const add = vi.fn(); const toggle = vi.fn();
    render(<ProductCard product={product} isWishlisted={false} onAddToCart={add} onToggleWishlist={toggle} onProductClick={open} />);

    expect(screen.getByRole('link', { name: product.name })).toHaveAttribute('href', '/products/crochet-rose-bouquet');
    fireEvent.click(screen.getByRole('button', { name: 'Quick Add' }));
    expect(add).toHaveBeenCalledOnce(); expect(open).not.toHaveBeenCalled();
    const wishlistButton = screen.getByRole('button', { name: 'Save Crochet Rose Bouquet to wishlist' });
    expect(wishlistButton).toHaveAttribute('aria-pressed', 'false');
    fireEvent.click(wishlistButton);
    expect(toggle).toHaveBeenCalledWith(product);
    fireEvent.click(screen.getByRole('link', { name: product.name })); expect(open).toHaveBeenCalledWith(product);
    expect(screen.queryByText('(128)')).not.toBeInTheDocument();
    const image = screen.getByRole('img', { name: product.name });
    expect(image).toHaveAttribute('width', '1086');
    expect(image).toHaveAttribute('height', '1448');
    expect(image).toHaveAttribute('loading', 'lazy');
    expect(image).not.toHaveAttribute('srcset');
    expect(screen.getByTestId('product-card')).toHaveClass('flex', 'h-full', 'flex-col');
    expect(screen.getByTestId('product-image-frame')).toHaveClass('aspect-[3/4]', 'w-full', 'shrink-0');
    expect(screen.getByRole('img', { name: product.name })).toHaveClass('h-full', 'w-full', 'object-cover');
  });
});
