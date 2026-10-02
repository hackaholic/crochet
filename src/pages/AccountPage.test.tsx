import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AccountPage from './AccountPage';

const api = vi.hoisted(() => ({ overview: vi.fn(), addresses: vi.fn(), orders: vi.fn() }));

vi.mock('../lib/api/account', () => ({ accountProfileApi: { overview: api.overview, updateProfile: vi.fn() } }));
vi.mock('../lib/api/orders', () => ({ accountApi: { addresses: api.addresses, orders: api.orders, createAddress: vi.fn() } }));

beforeEach(() => {
  api.overview.mockResolvedValue({ profile: { id: 7, name: 'Anupama', email: 'anupama@example.com' }, totalOrders: 0, activeOrders: 0, savedAddresses: 0, wishlistItemsCount: 0 });
  api.addresses.mockResolvedValue([]);
  api.orders.mockResolvedValue([]);
});

afterEach(() => { cleanup(); vi.clearAllMocks(); });

describe('AccountPage sign out', () => {
  it('shows a sign-out action for signed-in customers and calls the logout handler', async () => {
    const onLogout = vi.fn().mockResolvedValue(undefined);
    render(<AccountPage onSignIn={vi.fn()} onLogout={onLogout} />);

    fireEvent.click(await screen.findByRole('button', { name: 'Sign out' }));

    await waitFor(() => expect(onLogout).toHaveBeenCalledOnce());
  });
});
