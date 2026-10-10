import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import CustomersPage from './CustomersPage';
import * as api from '../services/customers';
vi.mock('../services/customers', () => ({ getCustomers: vi.fn(), getCustomer: vi.fn(), getCustomerOrders: vi.fn() }));
const customer = { id: 2, name: 'Test customer', email: null, phone: null, status: 'ACTIVE', createdAt: null, lastLoginAt: null, orderCount: 0 };
const list = { items: [customer], total: 21, page: 1, pageSize: 20 };
afterEach(cleanup);
beforeEach(() => {
  vi.resetAllMocks(); vi.mocked(api.getCustomers).mockResolvedValue(list);
  vi.mocked(api.getCustomer).mockResolvedValue(customer);
  vi.mocked(api.getCustomerOrders).mockResolvedValue({ items: [], total: 0, page: 1, pageSize: 20 });
});
it('lists, searches and pages customer API data', async () => {
  render(<CustomersPage onSelectOrder={vi.fn()} />);
  expect(await screen.findByText('Test customer')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Next' }));
  await waitFor(() => expect(api.getCustomers).toHaveBeenLastCalledWith('', 2, expect.any(AbortSignal)));
  fireEvent.change(screen.getByRole('searchbox'), { target: { value: ' bunny ' } });
  await waitFor(() => expect(api.getCustomers).toHaveBeenLastCalledWith('bunny', 1, expect.any(AbortSignal)));
});
it('shows nullable profile fields and empty history then returns to list', async () => {
  render(<CustomersPage onSelectOrder={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'View customer Test customer' }));
  expect(await screen.findByText('No linked orders')).toBeInTheDocument();
  expect(screen.getAllByText('Not provided')).toHaveLength(2);
  expect(api.getCustomer).toHaveBeenCalledWith(2, expect.any(AbortSignal));
  expect(api.getCustomerOrders).toHaveBeenCalledWith(2, 1, expect.any(AbortSignal));
  fireEvent.click(screen.getByRole('button', { name: 'Back to customers' }));
  expect(await screen.findByRole('searchbox')).toBeInTheDocument();
});
it('navigates using the linked order number and pages history', async () => {
  vi.mocked(api.getCustomerOrders).mockResolvedValue({ items: [{ id: 1, orderNumber: 'ORDER-1', status: 'PAID', paymentStatus: 'PAID' } as never], total: 21, page: 1, pageSize: 20 });
  const select = vi.fn();render(<CustomersPage onSelectOrder={select} />);
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
it('renders HTML-like customer text safely and retries list failures', async () => {
  vi.mocked(api.getCustomers).mockRejectedValueOnce(new Error('offline')).mockResolvedValue({ ...list, items: [{ ...customer, name: '<script>bad()</script>' }] });
  const { container } = render(<CustomersPage onSelectOrder={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: 'Try again' }));
  expect(await screen.findByText('<script>bad()</script>')).toBeInTheDocument();
  expect(container.querySelector('script')).toBeNull();
});
it('ignores stale search responses', async () => {
  let finish!: (value: api.CustomerList) => void;
  vi.mocked(api.getCustomers).mockReturnValueOnce(new Promise(resolve => { finish = resolve; })).mockResolvedValue({ ...list, items: [{ ...customer, name: 'Current result' }] });
  render(<CustomersPage onSelectOrder={vi.fn()} />);
  await waitFor(() => expect(api.getCustomers).toHaveBeenCalledTimes(1));
  fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'new' } });
  expect(await screen.findByText('Current result')).toBeInTheDocument();
  finish(list);
  await waitFor(() => expect(screen.queryByText('Test customer')).not.toBeInTheDocument());
});
