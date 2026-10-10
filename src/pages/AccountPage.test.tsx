import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AccountPage from './AccountPage';

const api = vi.hoisted(() => ({ overview: vi.fn(), addresses: vi.fn(), orders: vi.fn() }));

vi.mock('../components/orders/OrderTrackingPanel', () => ({ default: ({ orderNumber }: { orderNumber: string }) => <div>Tracking selected: {orderNumber}</div> }));

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

it('opens shipment details for the selected persisted order and closes them', async () => {
  api.orders.mockResolvedValue([{ id: 1, orderNumber: 'TEST-1', status: 'SHIPPED', totalAmount: 500 }]);
  render(<AccountPage onSignIn={vi.fn()} onLogout={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'Track shipment for TEST-1' }));
  expect(screen.getByText('Tracking selected: TEST-1')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Close shipment details' }));
  expect(screen.queryByText('Tracking selected: TEST-1')).not.toBeInTheDocument();
});
