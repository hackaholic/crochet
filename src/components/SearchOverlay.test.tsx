import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useState } from 'react';
import type { Product } from '../data/products';
import SearchOverlay from './SearchOverlay';

const catalogueApi = vi.hoisted(() => ({ searchProducts: vi.fn(), getSearchSuggestions: vi.fn(), recordSearchQuery: vi.fn() }));
vi.mock('../lib/api/catalogue', () => catalogueApi);

const rose: Product = {
  id: 42,
  name: 'Crochet Rose Bouquet',
  slug: 'crochet-rose-bouquet',
  price: 499,
  rating: 5,
  reviews: 0,
  image: 'https://images.sulocraft.com/rose.webp',
  images: ['https://images.sulocraft.com/rose.webp'],
  category: 'Flowers',
  tags: ['birthday'],
  customizable: false,
  inStock: true,
};
const tulip: Product = { ...rose, id: 43, name: 'Crochet Tulip Bouquet', slug: 'crochet-tulip-bouquet' };

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  vi.useRealTimers();
});

beforeEach(() => {
  catalogueApi.getSearchSuggestions.mockResolvedValue({ trending_keywords: [], trending_products: [] });
  catalogueApi.recordSearchQuery.mockResolvedValue(undefined);
});

describe('SearchOverlay', () => {
  it('loads database-backed trending keywords and products, and keyword chips launch a search', async () => {
    vi.useFakeTimers();
    catalogueApi.getSearchSuggestions.mockResolvedValue({ trending_keywords: [{ term: 'crochet flowers' }], trending_products: [rose] });
    catalogueApi.searchProducts.mockResolvedValue([rose]);
    render(<SearchOverlay open onClose={vi.fn()} onProductClick={vi.fn()} />);

    await act(async () => { await Promise.resolve(); });
    expect(screen.getByRole('heading', { name: 'Trending searches' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'crochet flowers' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Trending products' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Crochet Rose Bouquet/ })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'crochet flowers' }));
    await act(async () => { await vi.advanceTimersByTimeAsync(275); });
    expect(catalogueApi.searchProducts).toHaveBeenCalledWith('crochet flowers', expect.any(Object));
  });

  it('shows neutral guidance when the backend has no trend data', async () => {
    catalogueApi.getSearchSuggestions.mockResolvedValue({ trending_keywords: [], trending_products: [] });
    render(<SearchOverlay open onClose={vi.fn()} onProductClick={vi.fn()} />);
    await act(async () => { await Promise.resolve(); });
    expect(screen.getByText('Search products by name, category, occasion, or details.')).toBeInTheDocument();
    expect(screen.queryByText('Trending searches')).not.toBeInTheDocument();
  });

  it('waits for a two-character query and debounce before searching the backend', async () => {
    vi.useFakeTimers();
    catalogueApi.searchProducts.mockResolvedValue([rose]);
    render(<SearchOverlay open onClose={vi.fn()} onProductClick={vi.fn()} />);
    const input = screen.getByRole('searchbox', { name: 'Search products' });

    fireEvent.change(input, { target: { value: 'r' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(400); });
    expect(catalogueApi.searchProducts).not.toHaveBeenCalled();

    fireEvent.change(input, { target: { value: ' rose ' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(274); });
    expect(catalogueApi.searchProducts).not.toHaveBeenCalled();

    await act(async () => { await vi.advanceTimersByTimeAsync(1); });
    expect(catalogueApi.searchProducts).toHaveBeenCalledWith('rose', expect.objectContaining({ limit: 6, signal: expect.any(AbortSignal) }));
    expect(screen.getByRole('option', { name: /Crochet Rose Bouquet/ })).toBeInTheDocument();
  });

  it('aborts an earlier request when the query changes and selects with the keyboard', async () => {
    vi.useFakeTimers();
    let resolveRose!: (products: Product[]) => void;
    catalogueApi.searchProducts.mockImplementationOnce((_query: string, { signal }: { signal: AbortSignal }) => {
      return new Promise<Product[]>(resolve => {
        resolveRose = resolve;
        signal.addEventListener('abort', () => resolve([]), { once: true });
      });
    }).mockResolvedValueOnce([rose, tulip]);
    const onProductClick = vi.fn();
    const onClose = vi.fn();
    render(<SearchOverlay open onClose={onClose} onProductClick={onProductClick} />);
    const input = screen.getByRole('searchbox', { name: 'Search products' });

    fireEvent.change(input, { target: { value: 'ro' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(275); });
    const firstSignal = catalogueApi.searchProducts.mock.calls[0][1].signal;
    fireEvent.change(input, { target: { value: 'rose' } });
    expect(firstSignal.aborted).toBe(true);

    await act(async () => { await vi.advanceTimersByTimeAsync(275); });
    await act(async () => { await Promise.resolve(); });
    expect(screen.getByRole('option', { name: /Crochet Rose Bouquet/ })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /Crochet Rose Bouquet/ })).toHaveAttribute('aria-selected', 'true');
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    expect(screen.getByRole('option', { name: /Crochet Tulip Bouquet/ })).toHaveAttribute('aria-selected', 'true');
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(onProductClick).toHaveBeenCalledWith(tulip);
    expect(onClose).toHaveBeenCalledOnce();
    resolveRose([]);
  });

  it('shows no-results and recoverable error states instead of stale catalogue results', async () => {
    vi.useFakeTimers();
    catalogueApi.searchProducts.mockResolvedValueOnce([]).mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce([rose]);
    render(<SearchOverlay open onClose={vi.fn()} onProductClick={vi.fn()} />);
    const input = screen.getByRole('searchbox', { name: 'Search products' });

    fireEvent.change(input, { target: { value: 'xyz' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(275); });
    expect(screen.getByText(/No products found for “xyz”/)).toBeInTheDocument();

    fireEvent.change(input, { target: { value: 'rose' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(275); });
    expect(screen.getByRole('alert')).toHaveTextContent(/temporarily unavailable/);
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    await act(async () => { await vi.advanceTimersByTimeAsync(275); });
    expect(screen.getByRole('option', { name: /Crochet Rose Bouquet/ })).toBeInTheDocument();
  });

  it('focuses the search field when opened and returns focus to its trigger on Escape', () => {
    function SearchHarness() {
      const [open, setOpen] = useState(false);
      return <>
        <button type="button" onClick={() => setOpen(true)}>Open search</button>
        <SearchOverlay open={open} onClose={() => setOpen(false)} onProductClick={vi.fn()} />
      </>;
    }

    render(<SearchHarness />);
    const trigger = screen.getByRole('button', { name: 'Open search' });
    trigger.focus();
    fireEvent.click(trigger);
    const input = screen.getByRole('searchbox', { name: 'Search products' });
    expect(document.activeElement).toBe(input);
    fireEvent.keyDown(input, { key: 'Escape' });
    expect(screen.queryByRole('dialog', { name: 'Search products' })).not.toBeInTheDocument();
    expect(document.activeElement).toBe(trigger);
  });

  it('navigates via onProductClick and closes overlay when clicking a trending product card', async () => {
    catalogueApi.getSearchSuggestions.mockResolvedValue({
      trending_keywords: [],
      trending_products: [rose],
    });
    const onProductClick = vi.fn();
    const onClose = vi.fn();
    render(<SearchOverlay open onClose={onClose} onProductClick={onProductClick} />);

    await act(async () => { await Promise.resolve(); });
    const productButton = screen.getByRole('button', { name: /Crochet Rose Bouquet/ });
    expect(productButton).toBeInTheDocument();

    fireEvent.click(productButton);
    expect(onProductClick).toHaveBeenCalledWith(rose);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('retries loading search suggestions when the retry button is clicked after network failure', async () => {
    catalogueApi.getSearchSuggestions
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        trending_keywords: [{ term: 'crochet flowers' }],
        trending_products: [rose],
      });

    render(<SearchOverlay open onClose={vi.fn()} onProductClick={vi.fn()} />);

    await act(async () => { await Promise.resolve(); });
    expect(screen.getByRole('alert')).toHaveTextContent('Search suggestions are temporarily unavailable.');
    const retryButton = screen.getByRole('button', { name: 'Try again' });
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    await act(async () => { await Promise.resolve(); });

    expect(catalogueApi.getSearchSuggestions).toHaveBeenCalledTimes(2);
    expect(screen.getByRole('heading', { name: 'Trending searches' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'crochet flowers' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Trending products' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Crochet Rose Bouquet/ })).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('does not degrade or crash live search results when telemetry API rejects', async () => {
    vi.useFakeTimers();
    catalogueApi.searchProducts.mockResolvedValue([rose]);
    catalogueApi.recordSearchQuery.mockRejectedValue(new Error('Telemetry service unavailable (500)'));

    render(<SearchOverlay open onClose={vi.fn()} onProductClick={vi.fn()} />);
    const input = screen.getByRole('searchbox', { name: 'Search products' });

    fireEvent.change(input, { target: { value: 'rose' } });
    await act(async () => { await vi.advanceTimersByTimeAsync(275); });
    await act(async () => { await Promise.resolve(); });

    expect(catalogueApi.searchProducts).toHaveBeenCalledWith('rose', expect.any(Object));
    expect(catalogueApi.recordSearchQuery).toHaveBeenCalledWith('rose');
    expect(screen.getByRole('option', { name: /Crochet Rose Bouquet/ })).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
});

