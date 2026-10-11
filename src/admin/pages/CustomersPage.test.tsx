import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import CustomersPage from './CustomersPage';
import * as api from '../services/customers';

vi.mock('../services/customers', () => ({
  getCustomers: vi.fn(),
  getCustomer: vi.fn(),
  getCustomerOrders: vi.fn(),
}));

const customer = {
  id: 2,
  name: 'Test customer',
  email: null,
  phone: null,
  status: 'ACTIVE',
  createdAt: null,
  lastLoginAt: null,
  orderCount: 0,
};

const customerDetail: api.CustomerDetail = {
  ...customer,
  addresses: [],
};

const list: api.CustomerList = { items: [customer], total: 21, page: 1, pageSize: 20 };

afterEach(cleanup);

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(api.getCustomers).mockResolvedValue(list);
  vi.mocked(api.getCustomer).mockResolvedValue(customerDetail);
  vi.mocked(api.getCustomerOrders).mockResolvedValue({ items: [], total: 0, page: 1, pageSize: 20 });
});

it('lists, searches and pages customer API data with clickable customer name and no Actions column (TC01)', async () => {
  render(<CustomersPage onSelectOrder={vi.fn()} />);
  // Name is rendered as a button link
  const nameBtn = await screen.findByRole('button', { name: 'View customer Test customer' });
  expect(nameBtn).toBeInTheDocument();
  // Actions column header and generic View button are absent
  expect(screen.queryByText('Actions')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /^View$/ })).not.toBeInTheDocument();

  // Pagination Next
  fireEvent.click(screen.getByRole('button', { name: 'Next' }));
  await waitFor(() => expect(api.getCustomers).toHaveBeenLastCalledWith('', 2, expect.any(AbortSignal)));

  // Search
  fireEvent.change(screen.getByRole('searchbox'), { target: { value: ' bunny ' } });
  await waitFor(() => expect(api.getCustomers).toHaveBeenLastCalledWith('bunny', 1, expect.any(AbortSignal)));
});

it('shows nullable profile fields, empty addresses, and empty history then returns to list (TC02 & TC03)', async () => {
  render(<CustomersPage onSelectOrder={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'View customer Test customer' }));

  expect(await screen.findByText('No linked orders')).toBeInTheDocument();
  expect(await screen.findByText('No saved addresses')).toBeInTheDocument();
  expect(screen.getAllByText('Not provided')).toHaveLength(2); // email and account phone
  expect(api.getCustomer).toHaveBeenCalledWith(2, expect.any(AbortSignal));
  expect(api.getCustomerOrders).toHaveBeenCalledWith(2, 1, expect.any(AbortSignal));

  fireEvent.click(screen.getByRole('button', { name: 'Back to customers' }));
  expect(await screen.findByRole('searchbox')).toBeInTheDocument();
});

it('renders multiple saved addresses with default label, address details and distinct phones without duplication (TC02)', async () => {
  const detailWithAddresses: api.CustomerDetail = {
    ...customer,
    name: 'Aarav Sharma',
    email: 'aarav@example.com',
    phone: '9999900000', // Account phone
    addresses: [
      {
        id: 101,
        name: 'Aarav Home',
        phone: '9888811111', // Address contact phone
        line1: '123 MG Road',
        line2: 'Apartment 4B',
        landmark: 'Near Metro',
        city: 'Bengaluru',
        state: 'Karnataka',
        postalCode: '560001',
        country: 'IN',
        isDefault: true,
      },
      {
        id: 102,
        name: 'Aarav Work',
        phone: '9777722222',
        line1: '456 Tech Park',
        line2: null,
        landmark: null,
        city: 'Bengaluru',
        state: 'Karnataka',
        postalCode: '560100',
        country: 'IN',
        isDefault: false,
      },
    ],
  };

  vi.mocked(api.getCustomers).mockResolvedValue({
    items: [{ ...customer, name: 'Aarav Sharma' }],
    total: 1,
    page: 1,
    pageSize: 20,
  });
  vi.mocked(api.getCustomer).mockResolvedValue(detailWithAddresses);

  render(<CustomersPage onSelectOrder={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'View customer Aarav Sharma' }));

  // Account phone separate
  expect(await screen.findByText('Account Phone')).toBeInTheDocument();
  expect(screen.getByText('9999900000')).toBeInTheDocument();

  // Saved addresses
  expect(screen.getByText('Saved addresses')).toBeInTheDocument();
  expect(screen.getByText('Aarav Home')).toBeInTheDocument();
  expect(screen.getByText('Default')).toBeInTheDocument();
  expect(screen.getByText('9888811111')).toBeInTheDocument();
  expect(screen.getByText('123 MG Road')).toBeInTheDocument();
  expect(screen.getByText('Apartment 4B')).toBeInTheDocument();
  expect(screen.getByText('Near Metro')).toBeInTheDocument();
  expect(screen.getByText('Bengaluru, Karnataka 560001')).toBeInTheDocument();

  expect(screen.getByText('Aarav Work')).toBeInTheDocument();
  expect(screen.getByText('9777722222')).toBeInTheDocument();
  expect(screen.getByText('456 Tech Park')).toBeInTheDocument();
  expect(screen.getByText('Bengaluru, Karnataka 560100')).toBeInTheDocument();
});

it('navigates using the linked order number and pages history', async () => {
  vi.mocked(api.getCustomerOrders).mockResolvedValue({
    items: [{ id: 1, orderNumber: 'ORDER-1', status: 'PAID', paymentStatus: 'PAID' } as never],
    total: 21,
    page: 1,
    pageSize: 20,
  });
  const select = vi.fn();
  render(<CustomersPage onSelectOrder={select} />);
  fireEvent.click(await screen.findByRole('button', { name: 'View customer Test customer' }));
  fireEvent.click(await screen.findByRole('button', { name: 'View order ORDER-1' }));
  expect(select).toHaveBeenCalledWith('ORDER-1');
  fireEvent.click(screen.getByRole('button', { name: 'Next' }));
  await waitFor(() => expect(api.getCustomerOrders).toHaveBeenLastCalledWith(2, 2, expect.any(AbortSignal)));
});

it('does not retain profile data when history fails and allows retry', async () => {
  vi.mocked(api.getCustomerOrders).mockRejectedValueOnce(new Error('403'));
  render(<CustomersPage onSelectOrder={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'View customer Test customer' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('details could not be loaded');
  expect(screen.queryByText('Test customer')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
  expect(await screen.findByText('No linked orders')).toBeInTheDocument();
});

it('renders HTML-like customer text safely and retries list failures (TC04)', async () => {
  vi.mocked(api.getCustomers)
    .mockRejectedValueOnce(new Error('offline'))
    .mockResolvedValue({ ...list, items: [{ ...customer, name: '<script>bad()</script>' }] });
  const { container } = render(<CustomersPage onSelectOrder={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'Try again' }));
  expect(await screen.findByText('<script>bad()</script>')).toBeInTheDocument();
  expect(container.querySelector('script')).toBeNull();
});

it('ignores stale search responses', async () => {
  let finish!: (value: api.CustomerList) => void;
  vi.mocked(api.getCustomers)
    .mockReturnValueOnce(new Promise(resolve => { finish = resolve; }))
    .mockResolvedValue({ ...list, items: [{ ...customer, name: 'Current result' }] });
  render(<CustomersPage onSelectOrder={vi.fn()} />);
  await waitFor(() => expect(api.getCustomers).toHaveBeenCalledTimes(1));
  fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'new' } });
  expect(await screen.findByText('Current result')).toBeInTheDocument();
  finish(list);
  await waitFor(() => expect(screen.queryByText('Test customer')).not.toBeInTheDocument());
});


it('escapes address content and keeps long address text within the profile layout', async () => {
  const text = '<script>private-address()</script>';
  vi.mocked(api.getCustomer).mockResolvedValue({ ...customerDetail, addresses: [{
    id: 1, name: text, phone: '9999900123', line1: 'X'.repeat(300), line2: null,
    landmark: null, city: 'Delhi', state: 'Delhi', postalCode: '110001', country: 'IN', isDefault: true,
  }] });
  const { container } = render(<CustomersPage onSelectOrder={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'View customer Test customer' }));
  expect(await screen.findByText(text)).toBeVisible();
  expect(container.querySelector('script')).toBeNull();
  expect(screen.getByText('X'.repeat(300)).closest('.min-w-0')).not.toBeNull();
});
