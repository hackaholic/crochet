import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ProductsPage from './ProductsPage';
import * as api from '../../lib/api/admin';
import * as catalogue from '../services/catalogue';
vi.mock('../../lib/api/admin', () => ({ getAdminProducts: vi.fn() }));
vi.mock('../services/catalogue', () => ({ getCategories: vi.fn(), getProduct: vi.fn() }));
vi.mock('../components/ProductEditor', () => ({ default: () => <div>Editor opened</div> }));
const product = { id: 42, name: 'Test bunny', slug: 'test-bunny', status: 'ACTIVE', primaryImage: '/test.webp', totalStock: 3, minPrice: 100, variants: [], categoryNames: ['Animals'] };
afterEach(cleanup);
describe('Products catalogue', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(catalogue.getCategories).mockResolvedValue([{ id: 8, name: 'Animals' }]);
    vi.mocked(api.getAdminProducts).mockResolvedValue({ items: [product], total: 21, page: 1, pageSize: 20 });
  });
  it('renders API products and fetches another page with the selected filter', async () => {
    render(<ProductsPage />);
    expect(await screen.findByText('Test bunny')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Category'), { target: { value: '8' } });
    await waitFor(() => expect(api.getAdminProducts).toHaveBeenLastCalledWith(expect.objectContaining({ categoryId: 8, page: 1 }), expect.any(AbortSignal)));
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    await waitFor(() => expect(api.getAdminProducts).toHaveBeenLastCalledWith(expect.objectContaining({ categoryId: 8, page: 2 }), expect.any(AbortSignal)));
  });
  it('reports load failure and lets the owner retry', async () => {
    vi.mocked(api.getAdminProducts).mockRejectedValueOnce(new Error('offline'));
    render(<ProductsPage />);
    expect(await screen.findByRole('alert')).toHaveTextContent('Catalogue could not be loaded');
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(await screen.findByText('Test bunny')).toBeInTheDocument();
  });
  it('loads full persisted product details before opening editor', async () => {
    vi.mocked(catalogue.getProduct).mockResolvedValue({ ...product, categoryIds: [8], tagIds: [], tagNames: [], galleryImages: [] });
    render(<ProductsPage />);
    fireEvent.click(await screen.findByRole('button', { name: 'Edit Test bunny' }));
    expect(await screen.findByText('Editor opened')).toBeInTheDocument();
    expect(catalogue.getProduct).toHaveBeenCalledWith(42);
  });
  it('does not allow editing with missing category data', async () => {
    vi.mocked(catalogue.getCategories).mockRejectedValue(new Error('offline'));
    render(<ProductsPage />);
    expect(await screen.findByRole('button', { name: 'Edit Test bunny' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Add product' })).toBeDisabled();
  });
});
