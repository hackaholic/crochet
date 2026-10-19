import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import CartDrawer from './CartDrawer';
import { getProductDiscovery } from '../lib/api/productDiscovery';
vi.mock('../lib/api/productDiscovery', () => ({ getProductDiscovery: vi.fn().mockResolvedValue({sections:[],nextCursor:null}) }));
const callbacks = () => ({ onClose: vi.fn(), onUpdateQty: vi.fn(), onRemove: vi.fn(), onWishlist: vi.fn(), onCheckout: vi.fn(), onAddToCart: vi.fn().mockResolvedValue(undefined) });
afterEach(() => { cleanup(); vi.resetAllMocks(); });
it('opens an accessible basket, closes by Escape/backdrop and releases page scrolling', () => {
  const props = callbacks();
  const { rerender } = render(<CartDrawer open items={[]} {...props} />);
  const dialog = screen.getByRole('dialog', { name: 'Your Basket' });
  expect(screen.getByText('Your basket is empty')).toBeVisible();
  expect(document.body.style.overflow).toBe('hidden');
  fireEvent(dialog, new Event('cancel', { bubbles: false, cancelable: true }));
  expect(props.onClose).toHaveBeenCalledTimes(1);
  fireEvent.click(dialog);
  expect(props.onClose).toHaveBeenCalledTimes(2);
  fireEvent.click(screen.getByRole('heading', { name: 'Your Basket' }));
  expect(props.onClose).toHaveBeenCalledTimes(2);
  rerender(<CartDrawer open={false} items={[]} {...props} />);
  expect(dialog).not.toHaveAttribute('open');
  expect(document.body.style.overflow).toBe('');
});
it('keeps filled-basket notes, totals and checkout available', () => {
  const props = callbacks();
  render(<CartDrawer open items={[{ product: { id: 1, name: 'Rose', image: '/rose.webp', price: 500, category: 'Flowers', rating: 0, reviews: 0 }, quantity: 2, personalization: { note: '<gift>' } }]} {...props} />);
  expect(screen.getByText('Note: <gift>')).toBeVisible();
  expect(screen.getAllByText('₹1000').length).toBeGreaterThan(0);
  fireEvent.click(screen.getByRole('button', { name: 'Proceed to Checkout →' }));
  expect(props.onCheckout).toHaveBeenCalledTimes(1);
});

it('keeps the basket open when its recommendation is added', async () => {
  const product = { id: 7, name: 'Tulip', slug: 'tulip', image: '/tulip.webp', price: 500, category: 'Flowers', rating: 0, reviews: 0 };
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'suggestions',title:'You may also like',strategy:'newest',products:[product]}],nextCursor:null});
  const props = callbacks();
  const onProductClick = vi.fn();
  render(<CartDrawer open items={[]} {...props} onProductClick={onProductClick} />);
  fireEvent.click(await screen.findByRole('button', {name:'Add Tulip to basket'}));
  await waitFor(() => expect(props.onAddToCart).toHaveBeenCalledWith(product));
  expect(screen.getByRole('dialog', {name:'Your Basket'})).toBeVisible();
  expect(props.onClose).not.toHaveBeenCalled();
  expect(onProductClick).not.toHaveBeenCalled();
});
