import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ProductEditor from './ProductEditor';
import * as api from '../services/catalogue';
vi.mock('../services/catalogue', () => ({ getTags: vi.fn(), saveProduct: vi.fn(), createTag: vi.fn(), uploadPhoto: vi.fn(), saveVariant: vi.fn() }));
const product = { id: 42, name: 'Test bunny', slug: 'test', status: 'ACTIVE', primaryImage: '/test.webp', totalStock: 3, minPrice: 100, categoryNames: ['Animals'], categoryIds: [8], tagIds: [7], tagNames: ['Soft toy'], galleryImages: [], variants: [] };
afterEach(cleanup);
describe('Product editor', () => {
  beforeEach(() => { vi.resetAllMocks(); vi.mocked(api.getTags).mockRejectedValue(new Error('no endpoint')); });
  it('preserves existing tags when unavailable and saves selected categories and edits', async () => {
    const onSaved = vi.fn(); vi.mocked(api.saveProduct).mockResolvedValue(product);
    render(<ProductEditor product={product} categories={[{ id: 8, name: 'Animals' }]} onClose={vi.fn()} onSaved={onSaved} />);
    expect(await screen.findByText(/existing product tags will be preserved/i)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Product name'), { target: { value: 'Updated bunny' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save product' }));
    await waitFor(() => expect(api.saveProduct).toHaveBeenCalledWith(expect.objectContaining({ name: 'Updated bunny', tagIds: [7], categoryIds: [8] }), 42, undefined));
    expect(onSaved).toHaveBeenCalledWith(product);
  });
  it('selects a returned existing tag without duplicating it and persists its association', async () => {
    vi.mocked(api.getTags).mockResolvedValue([{ id: 7, name: 'Soft toy' }]);
    vi.mocked(api.createTag).mockResolvedValue({ id: 7, name: 'Soft toy' });
    vi.mocked(api.saveProduct).mockResolvedValue(product);
    render(<ProductEditor product={product} categories={[{ id: 8, name: 'Animals' }]} onClose={vi.fn()} onSaved={vi.fn()} />);
    await screen.findByRole('checkbox', { name: 'Soft toy' });
    fireEvent.change(screen.getByLabelText('New tag'), { target: { value: ' soft toy ' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add tag' }));
    await waitFor(() => expect(screen.getByLabelText('New tag')).toHaveValue(''));
    expect(api.createTag).toHaveBeenCalledWith('soft toy');
    expect(screen.getAllByRole('checkbox', { name: 'Soft toy' })).toHaveLength(1);
    fireEvent.click(screen.getByRole('button', { name: 'Save product' }));
    await waitFor(() => expect(api.saveProduct).toHaveBeenCalledWith(expect.objectContaining({ tagIds: [7] }), 42, undefined));
  });
  it('preserves tag input and product associations when tag creation fails', async () => {
    vi.mocked(api.getTags).mockResolvedValue([{ id: 7, name: 'Soft toy' }]);
    vi.mocked(api.createTag).mockRejectedValue(new Error('unavailable'));
    render(<ProductEditor product={product} categories={[]} onClose={vi.fn()} onSaved={vi.fn()} />);
    await screen.findByRole('checkbox', { name: 'Soft toy' });
    fireEvent.change(screen.getByLabelText('New tag'), { target: { value: 'New label' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add tag' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Tag could not be created');
    expect(screen.getByLabelText('New tag')).toHaveValue('New label');
    expect(screen.getByRole('checkbox', { name: 'Soft toy' })).toBeChecked();
  });
  it('keeps edits when a save fails', async () => {
    vi.mocked(api.saveProduct).mockRejectedValue(new Error('offline'));
    render(<ProductEditor product={product} categories={[]} onClose={vi.fn()} onSaved={vi.fn()} />);
    fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'My unsaved edit' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save product' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Product could not be saved');
    expect(screen.getByLabelText('Description')).toHaveValue('My unsaved edit');
  });
  it('uploads a photo and persists the returned storage key when creating a listing', async () => {
    vi.mocked(api.uploadPhoto).mockResolvedValue({ key: 'products/new.webp', url: 'https://images.example/new.webp' });
    render(<ProductEditor categories={[{ id: 8, name: 'Animals' }]} onClose={vi.fn()} onSaved={vi.fn()} />);
    fireEvent.click(screen.getByRole('checkbox', { name: 'Animals' }));
    fireEvent.change(screen.getByLabelText('Upload a photo'), { target: { files: [new File(['data'], 'photo.webp', { type: 'image/webp' })] } });
    await screen.findByRole('img', { name: 'Product photo' });
    fireEvent.change(screen.getByLabelText('Product name'), { target: { value: 'New listing' } });
    fireEvent.change(screen.getByLabelText('SKU'), { target: { value: 'TEST-SKU' } });
    fireEvent.change(screen.getByLabelText('Variant name'), { target: { value: 'Standard' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save product' }));
    await waitFor(() => expect(api.saveProduct).toHaveBeenCalledWith(expect.objectContaining({ primaryImage: 'products/new.webp' }), undefined, [expect.objectContaining({ sku: 'TEST-SKU' })]));
  });
  it('saves changed variant pricing without sending unrelated product fields', async () => {
    render(<ProductEditor product={{ ...product, variants: [{ id: 5, name: 'Standard', sku: 'BUNNY', price: 100, stockQuantity: 3, status: 'ACTIVE' }] }} categories={[]} onClose={vi.fn()} onSaved={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Edit variant' }));
    fireEvent.change(screen.getByLabelText('Price (₹)'), { target: { value: '250' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save variant' }));
    await waitFor(() => expect(api.saveVariant).toHaveBeenCalledWith(42, { name: 'Standard', sku: 'BUNNY', price: 250, stockQuantity: 3 }, 5));
  });
});
