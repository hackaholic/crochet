import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import Header from './Header';

vi.mock('./CatalogueProvider', () => ({ useCatalogue: () => ({ categories: [] }) }));

afterEach(cleanup);

describe('Header account navigation', () => {
  it('makes the account page reachable from the mobile menu', () => {
    const onAccountOpen = vi.fn();
    render(<Header currentPage="home" onNavigate={vi.fn()} cartCount={0} wishlistCount={0} onSearchOpen={vi.fn()} onCartOpen={vi.fn()} onAccountOpen={onAccountOpen} />);

    fireEvent.click(screen.getByRole('button', { name: 'Menu' }));
    fireEvent.click(screen.getAllByRole('button', { name: 'Account' }).at(-1)!);

    expect(onAccountOpen).toHaveBeenCalledOnce();
  });
});
