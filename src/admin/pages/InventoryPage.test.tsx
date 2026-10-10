import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import InventoryPage from './InventoryPage';
import { getAdminProducts } from '../../lib/api/admin';
import { adjustStock } from '../services/inventory';
vi.mock('../../lib/api/admin', () => ({ getAdminProducts: vi.fn() }));
vi.mock('../services/inventory', () => ({ adjustStock: vi.fn() }));
const variant = { id: 3, name: 'Standard', sku: 'TEST-SKU', stockQuantity: 4, price: 10, status: 'ACTIVE' };
const data = { items: [{ id: 1, name: 'Test product', slug: 'test', primaryImage: '', totalStock: 4, minPrice: 10, categoryNames: [], status: 'ACTIVE', variants: [variant] }], page: 1, pageSize: 20, total: 25 };
afterEach(cleanup);
beforeEach(() => { vi.resetAllMocks(); vi.mocked(getAdminProducts).mockResolvedValue(data); vi.mocked(adjustStock).mockResolvedValue(variant); });
describe('Inventory integration', () => {
  it('shows the backend image and retains identification when its loading fails', async () => {
    vi.mocked(getAdminProducts).mockResolvedValue({ ...data, items: [{ ...data.items[0], primaryImage: 'products/key.webp', primaryImageUrl: 'https://images.example/product.webp' }] });
    render(<InventoryPage />);
    const photo = await screen.findByRole('img', { name: /^Test product$/ });
    expect(photo).toHaveAttribute('src', 'https://images.example/product.webp');
    expect(photo).toHaveAttribute('width', '64');
    fireEvent.error(photo);
    expect(screen.getByRole('img', { name: 'Photo unavailable for Test product' })).toBeInTheDocument();
    expect(screen.getByText('TEST-SKU')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Adjust TEST-SKU' })).toBeEnabled();
  });
  it('does not turn a storage key into an image path', async () => {
    vi.mocked(getAdminProducts).mockResolvedValue({ ...data, items: [{ ...data.items[0], primaryImage: 'products/key.webp' }] });
    render(<InventoryPage />);
    expect(await screen.findByRole('img', { name: 'Photo unavailable for Test product' })).toBeInTheDocument();
    expect(screen.queryByRole('img', { name: /^Test product$/ })).not.toBeInTheDocument();
  });
  it('loads variant stock and pages using the API', async () => {
    render(<InventoryPage />);
    expect(await screen.findByText('TEST-SKU')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    await waitFor(() => expect(getAdminProducts).toHaveBeenLastCalledWith({ q: '', page: 2 }, expect.any(AbortSignal)));
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'bunny' } });
    await waitFor(() => expect(getAdminProducts).toHaveBeenLastCalledWith({ q: 'bunny', page: 1 }, expect.any(AbortSignal)));
  });
  it('rejects a negative resulting stock then saves a relative delta and reloads', async () => {
    render(<InventoryPage />);
    fireEvent.click(await screen.findByRole('button', { name: 'Adjust TEST-SKU' }));
    fireEvent.change(screen.getByLabelText('Stock adjustment'), { target: { value: '-5' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save adjustment' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('non-zero whole number');
    expect(adjustStock).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText('Stock adjustment'), { target: { value: '2' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save adjustment' }));
    await waitFor(() => expect(adjustStock).toHaveBeenCalledWith(3, 2));
    expect(await screen.findByText('Stock updated.')).toBeInTheDocument();
    await waitFor(() => expect(getAdminProducts).toHaveBeenCalledTimes(2));
  });
  it('preserves adjustment on failure and provides load retry', async () => {
    vi.mocked(getAdminProducts).mockRejectedValueOnce(new Error('offline'));
    render(<InventoryPage />);
    fireEvent.click(await screen.findByRole('button', { name: 'Try again' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Adjust TEST-SKU' }));
    vi.mocked(adjustStock).mockRejectedValue(new Error('forbidden'));
    fireEvent.change(screen.getByLabelText('Stock adjustment'), { target: { value: '2' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save adjustment' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('preserved');
    expect(screen.getByLabelText('Stock adjustment')).toHaveValue(2);
  });
});
