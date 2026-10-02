import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import HomepageSections from './HomepageSections';
import { uniqueProductsByImage } from './ProductGrid';
import type { HomepageSection } from '../../lib/api/storefront';

afterEach(cleanup);

describe('HomepageSections', () => {
  it('does not repeat products with the same primary image in a collection row', () => {
    const unique = uniqueProductsByImage([
      { id: 1, name: 'Bunny', price: 1, rating: 5, reviews: 1, image: 'https://images.example/bunny.webp?width=300', category: 'Amigurumi' },
      { id: 2, name: 'Panda', price: 1, rating: 5, reviews: 1, image: 'https://images.example/bunny.webp?width=600', category: 'Amigurumi' },
      { id: 3, name: 'Bear', price: 1, rating: 5, reviews: 1, image: 'https://images.example/bear.webp', category: 'Amigurumi' },
    ]);
    expect(unique.map(product => product.name)).toEqual(['Bunny', 'Bear']);
  });

  it('omits Gift by Occasion when no enabled occasions are returned by the API', () => {
    const sections: HomepageSection[] = [
      { id: 5, type: 'occasion_grid', order: 1, enabled: true, title: 'Gift by Occasion', occasions: [] },
    ];
    render(<HomepageSections sections={sections} wishlist={[]} onNavigate={vi.fn()} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    expect(screen.queryByRole('heading', { name: 'Gift by Occasion' })).not.toBeInTheDocument();
  });

  it('renders enabled approved section types in backend order', () => {
    const sections: HomepageSection[] = [
      { id: 2, type: 'promo_banner', order: 4, enabled: true, title: 'Festival offer' },
      { id: 1, type: 'category_grid', order: 1, enabled: true, title: 'Shop by Category', categories: [] },
      { id: 4, type: 'product_collection', order: 2, enabled: true, title: 'Most Loved Creations', eyebrow: 'Customer Favourites', description: 'Loved crochet made for everyday gifting.', collectionSlug: 'bestsellers', products: [] },
      { id: 5, type: 'occasion_grid', order: 3, enabled: true, title: 'Gift by Occasion', occasions: [{ id: 'birthday', name: 'Birthday', icon: '🎂', imageUrl: 'https://images.example/birthday.webp' }, { id: 'valentine', name: 'Valentine', icon: '❤️', imageUrl: 'https://images.example/valentine.webp' }, { id: 'wedding', name: 'Wedding', icon: '💐', imageUrl: 'https://images.example/birthday.webp?width=600' }] },
      { id: 3, type: 'image_text', order: 4, enabled: false, title: 'Hidden', description: 'Hidden', imageUrl: '/hidden.webp', imageAlt: 'Hidden', imagePosition: 'left' },
    ];
    render(<HomepageSections sections={sections} wishlist={[]} onNavigate={vi.fn()} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    const headings = screen.getAllByRole('heading').map(heading => heading.textContent);
    expect(headings).toEqual(['Shop by Category', 'Most Loved Creations', 'Gift by Occasion', 'Festival offer']);
    expect(screen.getByRole('button', { name: /show all categories/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Shop by Category' }).closest('section')).toHaveClass('storefront-shell');
    expect(screen.getByRole('heading', { name: 'Most Loved Creations' }).parentElement).toHaveClass('text-center');
    expect(screen.getByText('Loved crochet made for everyday gifting.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Shop gifts for Birthday' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Shop gifts for Wedding' })).not.toBeInTheDocument();
    expect(screen.getByTestId('product-grid')).toHaveClass('grid-cols-2', 'md:grid-cols-4');
    expect(screen.getByRole('heading', { name: 'Festival offer' }).closest('section')).toHaveClass('w-full');
    expect(screen.queryByText('Hidden')).not.toBeInTheDocument();
  });
});
