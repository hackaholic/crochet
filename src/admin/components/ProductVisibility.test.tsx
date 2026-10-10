import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import ProductVisibility from './ProductVisibility';
import { setProductStatus } from '../services/catalogue';
vi.mock('../services/catalogue', () => ({ setProductStatus: vi.fn() }));
const product = { id: 42, name: 'Test bunny', slug: 'test', status: 'ACTIVE', primaryImage: '', totalStock: 3, minPrice: 10, variants: [], categoryNames: [] };
afterEach(cleanup);
beforeEach(() => vi.resetAllMocks());
it('disables through a narrow status change and guards duplicate clicks', async () => {
  let resolve!: (value: never) => void;
  vi.mocked(setProductStatus).mockReturnValue(new Promise(r => { resolve = r; }));
  const saved = vi.fn(); render(<ProductVisibility product={product} onSaved={saved} />);
  const button = screen.getByRole('button', { name: 'Disable Test bunny' });
  fireEvent.click(button); fireEvent.click(button);
  expect(button).toBeDisabled();
  expect(setProductStatus).toHaveBeenCalledTimes(1);
  expect(setProductStatus).toHaveBeenCalledWith(42, 'DRAFT');
  resolve({} as never); await waitFor(() => expect(saved).toHaveBeenCalledTimes(1));
});
it('enables drafts but preserves archived products', async () => {
  vi.mocked(setProductStatus).mockResolvedValue({} as never);
  const view = render(<ProductVisibility product={{ ...product, status: 'DRAFT' }} onSaved={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Enable Test bunny' }));
  await waitFor(() => expect(setProductStatus).toHaveBeenCalledWith(42, 'ACTIVE'));
  view.rerender(<ProductVisibility product={{ ...product, status: 'ARCHIVED' }} onSaved={vi.fn()} />);
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});
it('keeps current state after failed save and supports retry', async () => {
  vi.mocked(setProductStatus).mockRejectedValue(new Error('forbidden'));
  const saved = vi.fn();render(<ProductVisibility product={product} onSaved={saved} />);
  fireEvent.click(screen.getByRole('button', { name: 'Disable Test bunny' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be changed');
  expect(saved).not.toHaveBeenCalled();
  expect(screen.getByRole('button', { name: 'Disable Test bunny' })).toBeEnabled();
});
