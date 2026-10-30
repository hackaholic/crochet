import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { getProductDiscovery } from '../lib/api/productDiscovery';
import { afterEach, describe, expect, it, vi } from 'vitest';
import CartPage from './CartPage';
import type { CartItem } from '../components/CartDrawer';

vi.mock('../lib/api/productDiscovery', () => ({ getProductDiscovery: vi.fn().mockResolvedValue({sections:[],nextCursor:null}) }));

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
        onAddToCart={vi.fn().mockResolvedValue(undefined)} onProductClick={vi.fn()}
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

it('uses the shared dynamic feed in an empty basket and adds through the real cart callback',async()=>{
  const suggestion={...item.product,id:99,slug:'crochet-bunny',name:'Crochet Bunny'};
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'new-arrivals',title:'New arrivals',strategy:'newest',products:[suggestion]}],nextCursor:null});
  const add=vi.fn().mockResolvedValue(undefined);const checkout=vi.fn();const toggle=vi.fn();
  render(<CartPage items={[]} wishlist={[99]} onAddToCart={add} onProductClick={vi.fn()} onUpdateQty={vi.fn()} onRemove={vi.fn()} onWishlist={toggle} onCheckout={checkout} onNavigate={vi.fn()} onCouponChange={vi.fn()}/>);
  expect(screen.getByRole('heading',{name:'Your basket is empty'})).toBeVisible();
  const heart=await screen.findByRole('button',{name:'Remove Crochet Bunny from wishlist'});
  expect(heart).toHaveAttribute('aria-pressed','true');
  fireEvent.click(heart);
  expect(toggle).toHaveBeenCalledWith(suggestion);
  fireEvent.click(await screen.findByRole('button',{name:'Add Crochet Bunny to basket'}));
  await waitFor(()=>expect(add).toHaveBeenCalledExactlyOnceWith(suggestion));
  expect(checkout).not.toHaveBeenCalled();
  expect(getProductDiscovery).toHaveBeenLastCalledWith('basket',null,expect.any(AbortSignal));
});
