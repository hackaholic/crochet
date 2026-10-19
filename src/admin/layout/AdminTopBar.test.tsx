import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AdminTopBar from './AdminTopBar';
import * as api from '../services/api';
import type { Order } from '../types';

vi.mock('../services/api');

const mockOrder = (id: string, num: string, customerName = 'Dev Buyer'): Order => ({
  id,
  orderNumber: num,
  date: '2026-10-19T10:00:00Z',
  customer: {
    id: 10,
    name: customerName,
    email: 'buyer@example.com',
    phone: '9876543210',
  },
  shippingAddress: {
    line1: '100ft Road',
    city: 'Bengaluru',
    state: 'Karnataka',
    pinCode: '560038',
    country: 'IN',
  },
  items: [],
  subtotal: 1500,
  shipping: 0,
  discount: 0,
  gst: 0,
  total: 1500,
  paymentStatus: 'PAID',
  paymentMethod: 'UPI',
  orderStatus: 'CONFIRMED',
  timeline: [],
});

describe('AdminTopBar dynamic order search (Task 1.18)', () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('1.18-TC01: fetches matching orders dynamically and renders dropdown with details', async () => {
    const orders = [
      mockOrder('1', 'SLC-LOCAL-001', 'Aarav Sharma'),
      mockOrder('2', 'SLC-LOCAL-002', 'Bhavna Patel'),
    ];
    vi.mocked(api.getOrders).mockResolvedValueOnce({
      orders,
      total: 2,
      page: 1,
      pageSize: 6,
    });

    render(<AdminTopBar currentPage="dashboard" />);

    const searchInput = screen.getByRole('searchbox', { name: 'Search orders' });
    fireEvent.change(searchInput, { target: { value: 'SLC-LOCAL' } });

    // Shows loading or debounces
    await waitFor(() => {
      expect(api.getOrders).toHaveBeenCalledWith({
        search: 'SLC-LOCAL',
        pageSize: 6,
      });
    });

    // Dropdown shows matching orders
    expect(await screen.findByText('SLC-LOCAL-001')).toBeInTheDocument();
    expect(screen.getByText('SLC-LOCAL-002')).toBeInTheDocument();
    expect(screen.getByText(/Aarav Sharma/)).toBeInTheDocument();
    expect(screen.getByText(/Bhavna Patel/)).toBeInTheDocument();
    expect(screen.getByText(/View all 2 matching orders/)).toBeInTheDocument();
  });

  it('1.18-TC02: clicking an order in dropdown invokes onSelectOrder and closes dropdown', async () => {
    const orders = [mockOrder('42', 'SLC-TARGET-42', 'Target Customer')];
    vi.mocked(api.getOrders).mockResolvedValueOnce({
      orders,
      total: 1,
      page: 1,
      pageSize: 6,
    });

    const onSelectOrder = vi.fn();
    render(<AdminTopBar currentPage="dashboard" onSelectOrder={onSelectOrder} />);

    const searchInput = screen.getByRole('searchbox', { name: 'Search orders' });
    fireEvent.change(searchInput, { target: { value: '42' } });

    const orderBtn = await screen.findByRole('button', { name: /SLC-TARGET-42/i });
    fireEvent.click(orderBtn);

    expect(onSelectOrder).toHaveBeenCalledWith('42');
    expect(screen.queryByRole('region', { name: 'Search results' })).not.toBeInTheDocument();
  });

  it('1.18-TC03: pressing Enter navigates to Orders with query', async () => {
    const onNavigateToOrders = vi.fn();
    render(<AdminTopBar currentPage="dashboard" onNavigateToOrders={onNavigateToOrders} />);

    const searchInput = screen.getByRole('searchbox', { name: 'Search orders' });
    fireEvent.change(searchInput, { target: { value: '9876543210' } });
    fireEvent.keyDown(searchInput, { key: 'Enter' });

    expect(onNavigateToOrders).toHaveBeenCalledWith('9876543210');
  });

  it('1.18-TC04: clicking View all matching orders navigates to Orders', async () => {
    const orders = [mockOrder('1', 'SLC-001')];
    vi.mocked(api.getOrders).mockResolvedValueOnce({
      orders,
      total: 10,
      page: 1,
      pageSize: 6,
    });

    const onNavigateToOrders = vi.fn();
    render(<AdminTopBar currentPage="dashboard" onNavigateToOrders={onNavigateToOrders} />);

    const searchInput = screen.getByRole('searchbox', { name: 'Search orders' });
    fireEvent.change(searchInput, { target: { value: 'SLC' } });

    const viewAllBtn = await screen.findByRole('button', { name: /View all 10 matching orders/i });
    fireEvent.click(viewAllBtn);

    expect(onNavigateToOrders).toHaveBeenCalledWith('SLC');
  });

  it('1.18-TC05: renders empty state when no matching orders found', async () => {
    vi.mocked(api.getOrders).mockResolvedValueOnce({
      orders: [],
      total: 0,
      page: 1,
      pageSize: 6,
    });

    render(<AdminTopBar currentPage="dashboard" />);

    const searchInput = screen.getByRole('searchbox', { name: 'Search orders' });
    fireEvent.change(searchInput, { target: { value: 'NONEXISTENT' } });

    expect(await screen.findByText(/No orders found for "NONEXISTENT"/i)).toBeInTheDocument();
  });

  it('1.18-TC06: pressing Escape closes search dropdown', async () => {
    const orders = [mockOrder('1', 'SLC-001')];
    vi.mocked(api.getOrders).mockResolvedValueOnce({
      orders,
      total: 1,
      page: 1,
      pageSize: 6,
    });

    render(<AdminTopBar currentPage="dashboard" />);

    const searchInput = screen.getByRole('searchbox', { name: 'Search orders' });
    fireEvent.change(searchInput, { target: { value: 'SLC' } });

    await screen.findByText('SLC-001');
    fireEvent.keyDown(searchInput, { key: 'Escape' });

    expect(screen.queryByRole('region', { name: 'Search results' })).not.toBeInTheDocument();
  });

  it('1.18-TC07: searches successfully with 10-digit phone number (e.g. 9999900991)', async () => {
    const orders = [mockOrder('8', 'QA-W018-GUEST', 'QA Guest')];
    orders[0].customer.phone = '9999900991';
    vi.mocked(api.getOrders).mockResolvedValueOnce({
      orders,
      total: 1,
      page: 1,
      pageSize: 6,
    });

    render(<AdminTopBar currentPage="dashboard" />);

    const searchInput = screen.getByRole('searchbox', { name: 'Search orders' });
    fireEvent.change(searchInput, { target: { value: '9999900991' } });

    await waitFor(() => {
      expect(api.getOrders).toHaveBeenCalledWith({
        search: '9999900991',
        pageSize: 6,
      });
    });

    expect(await screen.findByText('QA-W018-GUEST')).toBeInTheDocument();
    expect(screen.getByText(/9999900991/)).toBeInTheDocument();
  });
});
