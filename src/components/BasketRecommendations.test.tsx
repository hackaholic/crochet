import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import BasketRecommendations from './BasketRecommendations';
import { getBasketDiscovery } from '../lib/api/basketRecommendations';
vi.mock('../lib/api/basketRecommendations', () => ({ getBasketDiscovery: vi.fn() }));
const rose = { id: 1, name: 'Rose', slug: 'rose', image: '/rose.webp', price: 400, category: 'Flowers', rating: 0, reviews: 0 };
afterEach(() => { cleanup(); vi.resetAllMocks(); });
it('requests only when open, excludes current basket and opens the selected API product', async () => {
  vi.mocked(getBasketDiscovery).mockResolvedValue([rose, { ...rose, id: 2, name: '<Tulip>' }]);
  const onProductClick = vi.fn();
  const { rerender } = render(<BasketRecommendations open={false} excludedIds={[]} onProductClick={onProductClick} />);
  expect(getBasketDiscovery).not.toHaveBeenCalled();
  rerender(<BasketRecommendations open excludedIds={[1]} onProductClick={onProductClick} />);
  expect(await screen.findByRole('heading', { name: 'You may also like' })).toBeVisible();
  expect(screen.queryByText('Rose')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: /<Tulip>/ }));
  expect(onProductClick).toHaveBeenCalledWith(expect.objectContaining({ id: 2 }));
  expect(document.querySelector('Tulip')).toBeNull();
});
it('omits empty or failed suggestions and aborts work on close', async () => {
  vi.mocked(getBasketDiscovery).mockRejectedValue(new Error('offline'));
  const { rerender } = render(<BasketRecommendations open excludedIds={[]} onProductClick={vi.fn()} />);
  await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument());
  expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  const signal = vi.mocked(getBasketDiscovery).mock.calls[0][0];
  rerender(<BasketRecommendations open={false} excludedIds={[]} onProductClick={vi.fn()} />);
  expect(signal?.aborted).toBe(true);
});
