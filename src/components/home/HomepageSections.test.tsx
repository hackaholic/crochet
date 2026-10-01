import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import HomepageSections from './HomepageSections';
import type { HomepageSection } from '../../lib/api/storefront';

afterEach(cleanup);

describe('HomepageSections', () => {
  it('renders enabled approved section types in backend order', () => {
    const sections: HomepageSection[] = [
      { id: 2, type: 'promo_banner', order: 3, enabled: true, title: 'Festival offer' },
      { id: 1, type: 'category_grid', order: 1, enabled: true, title: 'Shop by Category', categories: [] },
      { id: 4, type: 'product_collection', order: 2, enabled: true, title: 'Most Loved Creations', eyebrow: 'Customer Favourites', collectionSlug: 'bestsellers', products: [] },
      { id: 3, type: 'image_text', order: 4, enabled: false, title: 'Hidden', description: 'Hidden', imageUrl: '/hidden.webp', imageAlt: 'Hidden', imagePosition: 'left' },
    ];
    render(<HomepageSections sections={sections} wishlist={[]} onNavigate={vi.fn()} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} onProductClick={vi.fn()} />);
    const headings = screen.getAllByRole('heading').map(heading => heading.textContent);
    expect(headings).toEqual(['Shop by Category', 'Most Loved Creations', 'Festival offer']);
    expect(screen.getByRole('button', { name: /show all categories/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Shop by Category' }).closest('section')).toHaveClass('storefront-shell');
    expect(screen.getByRole('heading', { name: 'Most Loved Creations' }).parentElement).toHaveClass('text-center');
    expect(screen.getByRole('heading', { name: 'Festival offer' }).closest('section')).toHaveClass('w-full');
    expect(screen.queryByText('Hidden')).not.toBeInTheDocument();
  });
});
