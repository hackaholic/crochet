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

const renderAccount = (props: Parameters<typeof AccountPage>[0]) => render(<MemoryRouter><AccountPage {...props} /></MemoryRouter>);

describe('AccountPage sign out', () => {
  it('shows a sign-out action for signed-in customers and calls the logout handler', async () => {
    const onLogout = vi.fn().mockResolvedValue(undefined);
    renderAccount({ onSignIn: vi.fn(), onLogout });

    fireEvent.click(await screen.findByRole('button', { name: 'Sign out' }));

    await waitFor(() => expect(onLogout).toHaveBeenCalledOnce());
  });
});

it('opens shipment details for the selected persisted order and closes them', async () => {
  api.orders.mockResolvedValue([{ id: 1, orderNumber: 'TEST-1', status: 'SHIPPED', totalAmount: 500 }]);
  renderAccount({ onSignIn: vi.fn(), onLogout: vi.fn() });
  fireEvent.click(await screen.findByRole('button', { name: 'Orders' }));
  fireEvent.click(await screen.findByRole('button', { name: 'View order TEST-1' }));
  expect(screen.getByText('Tracking selected: TEST-1')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Close shipment details' }));
  expect(screen.queryByText('Tracking selected: TEST-1')).not.toBeInTheDocument();
});

it('navigates account sections and hides unrelated private panels', async () => {
  renderAccount({ onSignIn: vi.fn(), onLogout: vi.fn() });
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
  renderAccount({ onSignIn: vi.fn(), onLogout: vi.fn() });
  expect(await screen.findByLabelText('Email')).toHaveAttribute('readonly');
  fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'New Name' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save profile' }));
  await waitFor(() => expect(api.updateProfile).toHaveBeenCalledWith({ name: 'New Name', phone: null }));
});

it('retries account loading after a temporary failure',async()=>{api.overview.mockRejectedValueOnce(new Error('503'));renderAccount({onSignIn:vi.fn(),onLogout:vi.fn()});fireEvent.click(await screen.findByRole('button',{name:'Retry account'}));expect(await screen.findByLabelText('Email')).toBeVisible();expect(api.overview).toHaveBeenCalledTimes(2);});


it('renders accurate API summary counts in four distinct accent cards with accessible destinations', async () => {
  api.overview.mockResolvedValue({ profile: { id: 7, name: 'Anupama', email: 'anupama@example.com' }, totalOrders: 12, activeOrders: 3, savedAddresses: 2, wishlistItemsCount: 0 });
  renderAccount({ onSignIn: vi.fn(), onLogout: vi.fn() });
  const region = await screen.findByRole('region', { name: 'Account overview' });
  expect(region).toHaveClass('grid-cols-2');
  const cards = Array.from(region.children) as HTMLElement[];
  expect(cards.map(card => card.textContent)).toEqual(['12Orders', '3Active orders', '2Saved addresses', '0Wishlist items']);
  expect(new Set(cards.map(card => card.style.background)).size).toBe(4);
  expect(region.querySelectorAll('button')).toHaveLength(3);
  expect(region.querySelector('a')).toHaveAttribute('href', '/wishlist');
  expect(cards.every(card => card.className.includes('hover:-translate-y-0.5') && card.className.includes('hover:shadow-md'))).toBe(true);
  expect(cards.every(card => card.className.includes('focus-visible:outline'))).toBe(true);
  expect(region.querySelectorAll('[aria-hidden="true"] svg')).toHaveLength(4);
});

it('routes overview cards to their matching account content', async () => {
  api.overview.mockResolvedValue({ profile: { id: 7, name: 'Anupama', email: 'anupama@example.com' }, totalOrders: 1, activeOrders: 1, savedAddresses: 0, wishlistItemsCount: 0 });
  api.orders.mockResolvedValue([
    { id: 1, orderNumber: 'CARD-ORDER', status: 'SHIPPED', totalAmount: 500 },
    { id: 2, orderNumber: 'CARD-DELIVERED', status: 'DELIVERED', totalAmount: 700 },
  ]);
  renderAccount({ onSignIn: vi.fn(), onLogout: vi.fn() });

  fireEvent.click(await screen.findByRole('button', { name: 'Orders: 1. View orders' }));
  expect(screen.getByRole('button', { name: 'Orders' })).toHaveAttribute('aria-current', 'page');
  expect(screen.getByRole('table')).toBeVisible();

  fireEvent.click(await screen.findByRole('button', { name: 'Saved addresses: 0. View saved addresses' }));
  expect(screen.getByRole('button', { name: 'Addresses' })).toHaveAttribute('aria-current', 'page');
  expect(screen.getByRole('heading', { name: 'Saved addresses' })).toBeVisible();

  fireEvent.click(screen.getByRole('button', { name: 'Active orders: 1. View active orders' }));
  expect(screen.getByRole('button', { name: 'Orders' })).toHaveAttribute('aria-current', 'page');
  expect(screen.getByRole('heading', { name: 'Active orders' })).toBeVisible();
  expect(screen.getAllByRole('row')).toHaveLength(2);
  expect(screen.getByRole('button', { name: 'View order CARD-ORDER' })).toBeVisible();
  expect(screen.queryByRole('button', { name: 'View order CARD-DELIVERED' })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Orders: 1. View orders' }));
  expect(screen.getByRole('heading', { name: 'Order history' })).toBeVisible();
  expect(screen.getAllByRole('row')).toHaveLength(3);
  expect(screen.getByRole('link', { name: 'Wishlist items: 0. View wishlist' })).toHaveAttribute('href', '/wishlist');
});

it('does not render account summary navigation before authenticated overview data loads', async () => {
  api.overview.mockRejectedValue(new Error('401'));
  const onSignIn = vi.fn();
  renderAccount({ onSignIn, onLogout: vi.fn() });
  await waitFor(() => expect(onSignIn).toHaveBeenCalledOnce());
  expect(screen.queryByRole('region', { name: 'Account overview' })).not.toBeInTheDocument();
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
it('lists multiple orders in a table and opens only the selected timeline',async()=>{
 api.orders.mockResolvedValue([{id:1,orderNumber:'DEMO-1',status:'SHIPPED',totalAmount:500},{id:2,orderNumber:'DEMO-2',status:'DELIVERED',totalAmount:700}]);
 renderAccount({onSignIn:vi.fn(),onLogout:vi.fn()});
 fireEvent.click(await screen.findByRole('button',{name:'Orders'}));
 expect(screen.getByRole('table')).toBeVisible();
 expect(screen.getAllByRole('row')).toHaveLength(3);
 fireEvent.click(screen.getByRole('button',{name:'Track shipment for DEMO-2'}));
 expect(screen.getByText('Tracking selected: DEMO-2')).toBeVisible();
 expect(screen.queryByText('Tracking selected: DEMO-1')).toBeNull();
});
