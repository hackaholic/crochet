import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import CartDrawer from './CartDrawer';
const callbacks = () => ({ onClose: vi.fn(), onUpdateQty: vi.fn(), onRemove: vi.fn(), onWishlist: vi.fn(), onCheckout: vi.fn() });
afterEach(cleanup);
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
