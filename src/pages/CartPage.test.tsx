import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import CartPage from './CartPage';
import type { CartItem } from '../components/CartDrawer';

const item: CartItem = {
  product: {
    id: 42,
    name: 'Crochet Rose Bouquet',
    price: 1299,
    rating: 4.8,
    reviews: 12,
    image: '/rose.webp',
    category: 'Flowers',
    customizable: true,
  },
  quantity: 1,
};

afterEach(cleanup);

describe('CartPage item details', () => {
  it('does not invent a selected color or gift-wrap choice for customizable products', () => {
    render(
      <CartPage
        items={[item]}
        onUpdateQty={vi.fn()}
        onRemove={vi.fn()}
        onWishlist={vi.fn()}
        onCheckout={vi.fn()}
        onNavigate={vi.fn()}
        onCouponChange={vi.fn()}
      />,
    );

    expect(screen.queryByText(/Color: Blush Pink/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Gift wrapped/)).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: item.product.name })).toBeInTheDocument();
  });
});
