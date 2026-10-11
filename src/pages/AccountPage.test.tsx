import { MemoryRouter } from 'react-router';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AccountPage from './AccountPage';

const api = vi.hoisted(() => ({ overview: vi.fn(), addresses: vi.fn(), orders: vi.fn(), updateProfile: vi.fn() }));

vi.mock('../components/orders/OrderTrackingPanel', () => ({ default: ({ orderNumber }: { orderNumber: string }) => <div>Tracking selected: {orderNumber}</div> }));

vi.mock('../lib/api/account', () => ({ accountProfileApi: { overview: api.overview, updateProfile: api.updateProfile } }));
vi.mock('../lib/api/orders', () => ({ accountApi: { addresses: api.addresses, orders: api.orders, createAddress: vi.fn(), order: vi.fn().mockResolvedValue({items:[]}) } }));

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
  fireEvent.click(await screen.findByRole('button', { name: 'Orders' }));
  fireEvent.click(await screen.findByRole('button', { name: 'View order TEST-1' }));
  expect(screen.getByText('Tracking selected: TEST-1')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Close shipment details' }));
  expect(screen.queryByText('Tracking selected: TEST-1')).not.toBeInTheDocument();
});

it('navigates account sections and hides unrelated private panels', async () => {
  render(<AccountPage onSignIn={vi.fn()} onLogout={vi.fn()} />);
  const profile = await screen.findByRole('button', { name: 'Profile' });
  expect(profile).toHaveAttribute('aria-current', 'page');
  fireEvent.click(screen.getByRole('button', { name: 'Addresses' }));
  expect(screen.getByRole('heading', { name: 'Saved addresses' })).toBeVisible();
  expect(screen.queryByLabelText('Email')).not.toBeInTheDocument();
  fireEvent.click(profile);
  expect(screen.getByLabelText('Email')).toBeVisible();
});

it('keeps login email read-only and sends only editable profile data', async () => {
  api.updateProfile.mockResolvedValue({ id: 7, name: 'New Name', email: 'anupama@example.com' });
  render(<AccountPage onSignIn={vi.fn()} onLogout={vi.fn()} />);
  expect(await screen.findByLabelText('Email')).toHaveAttribute('readonly');
  fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'New Name' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save profile' }));
  await waitFor(() => expect(api.updateProfile).toHaveBeenCalledWith({ name: 'New Name', phone: null }));
});

it('retries account loading after a temporary failure',async()=>{api.overview.mockRejectedValueOnce(new Error('503'));render(<AccountPage onSignIn={vi.fn()} onLogout={vi.fn()}/>);fireEvent.click(await screen.findByRole('button',{name:'Retry account'}));expect(await screen.findByLabelText('Email')).toBeVisible();expect(api.overview).toHaveBeenCalledTimes(2);});


it('renders accurate API summary counts in four distinct accent cards without interactive decoration', async () => {
  api.overview.mockResolvedValue({ profile: { id: 7, name: 'Anupama', email: 'anupama@example.com' }, totalOrders: 12, activeOrders: 3, savedAddresses: 2, wishlistItemsCount: 0 });
  render(<AccountPage onSignIn={vi.fn()} onLogout={vi.fn()} />);
  const region = await screen.findByRole('region', { name: 'Account overview' });
  expect(region).toHaveClass('grid-cols-2');
  const cards = Array.from(region.children) as HTMLElement[];
  expect(cards.map(card => card.textContent)).toEqual(['12Orders', '3Active orders', '2Saved addresses', '0Wishlist items']);
  expect(new Set(cards.map(card => card.style.background)).size).toBe(4);
  expect(region.querySelectorAll('svg[aria-hidden],button,a')).toHaveLength(0);
  expect(region.querySelectorAll('[aria-hidden="true"] svg')).toHaveLength(4);
});
it('simplifies admin accounts without hiding profile, addresses or sign out',async()=>{
 render(<MemoryRouter><AccountPage isAdmin onSignIn={vi.fn()} onLogout={vi.fn()}/></MemoryRouter>);
 expect(await screen.findByRole('link',{name:'Admin Dashboard'})).toHaveAttribute('href','/admin');
 expect(screen.queryByRole('region',{name:'Account overview'})).toBeNull();
 expect(screen.queryByRole('button',{name:'Orders'})).toBeNull();
 expect(screen.getByRole('button',{name:'Profile'})).toBeVisible();
 expect(screen.getByRole('button',{name:'Addresses'})).toBeVisible();
 expect(screen.getByRole('button',{name:'Sign out'})).toBeVisible();
});
