import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import Header from './Header';
import { MemoryRouter } from 'react-router';

vi.mock('./CatalogueProvider', () => ({ useCatalogue: () => ({ categories: [] }) }));

vi.mock('./BrandLogo', () => ({ default: () => <img alt="Sulocraft logo" /> }));

afterEach(cleanup);

describe('Header account navigation', () => {
  it('uses only the official logo in the home brand button', () => {
    render(<MemoryRouter><Header currentPage="home" onNavigate={vi.fn()} cartCount={0} wishlistCount={0} onSearchOpen={vi.fn()} onCartOpen={vi.fn()} onAccountOpen={vi.fn()} /></MemoryRouter>);
    const brand = screen.getByRole('link', { name: 'Sulocraft home' });
    expect(brand).toHaveTextContent('');
    expect(brand.querySelector('img')).toHaveAttribute('alt', 'Sulocraft logo');
  });
  it('makes the account page reachable from the mobile menu', () => {
    const onAccountOpen = vi.fn();
    render(<MemoryRouter><Header currentPage="home" onNavigate={vi.fn()} cartCount={0} wishlistCount={0} onSearchOpen={vi.fn()} onCartOpen={vi.fn()} onAccountOpen={onAccountOpen} /></MemoryRouter>);

    const menu = screen.getByRole('button', { name: 'Menu' });
    expect(menu).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(menu);
    expect(menu).toHaveAttribute('aria-expanded', 'true');
    expect(menu).toHaveAttribute('aria-controls', 'storefront-mobile-menu');
    fireEvent.click(screen.getAllByRole('button', { name: 'Account' }).at(-1)!);

    expect(onAccountOpen).toHaveBeenCalledOnce();
    expect(menu).toHaveAttribute('aria-expanded', 'false');
  });
});

it('keeps search and basket actions working in the compact navigation', () => {
  const onSearchOpen = vi.fn(); const onCartOpen = vi.fn();
  render(<MemoryRouter><Header currentPage="home" onNavigate={vi.fn()} cartCount={2} wishlistCount={1} onSearchOpen={onSearchOpen} onCartOpen={onCartOpen} onAccountOpen={vi.fn()} /></MemoryRouter>);
  fireEvent.click(screen.getByRole('button', {name:'Search'}));
  fireEvent.click(screen.getByRole('button', {name:'Cart'}));
  expect(onSearchOpen).toHaveBeenCalledOnce();
  expect(onCartOpen).toHaveBeenCalledOnce();
  expect(screen.getByRole('button', {name:'Cart'})).toHaveTextContent('2');
});
