import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import AdminPage from './AdminPage';

const adminApi = vi.hoisted(() => ({ getAdminAnalytics: vi.fn() }));
const adminScreens = vi.hoisted(() => ({
  getDashboardSummary: vi.fn(), getOrderStatusCountsForPeriod: vi.fn(), getAttentionItems: vi.fn(),
  getActivityFeed: vi.fn(), getInventoryAlerts: vi.fn(), getSalesChart: vi.fn(), getOrders: vi.fn(),
}));

vi.mock('../lib/api/admin', () => adminApi);
vi.mock('../admin/services/api', () => adminScreens);

const analytics = {
  totalRevenue: 1860, totalRevenuePaise: 186000, totalOrders: 4, pendingOrders: 2,
  deliveredOrders: 1, cancelledOrders: 1, totalCustomers: 3, totalProducts: 8, lowStockCount: 0,
  lowStockItems: [], recentOrders: [], topSellingProducts: [],
};

afterEach(() => { cleanup(); vi.clearAllMocks(); });

function prepareAdmin() {
  adminApi.getAdminAnalytics.mockResolvedValue(analytics);
  adminScreens.getDashboardSummary.mockResolvedValue({ period: 'period', totalSales: 1860, totalRevenue: 1860, netRevenue: 1860, orders: 4, avgOrderValue: 465, refunds: 0, statusCounts: {}, comparison: null });
  adminScreens.getOrderStatusCountsForPeriod.mockResolvedValue([]);
  adminScreens.getAttentionItems.mockResolvedValue([]);
  adminScreens.getActivityFeed.mockResolvedValue([]);
  adminScreens.getInventoryAlerts.mockResolvedValue([]);
  adminScreens.getSalesChart.mockResolvedValue([]);
  adminScreens.getOrders.mockResolvedValue({ orders: [], total: 0, page: 1, pageSize: 20 });
}

describe('AdminPage', () => {
  it('uses the supplied Sulocraft admin layout and real admin dashboard service', async () => {
    prepareAdmin();
    render(<AdminPage onSignIn={vi.fn()} onExitAdmin={vi.fn()} />);

    expect(await screen.findByText('Sulocraft')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument();
    expect(await screen.findByText('Recent Orders')).toBeInTheDocument();
    expect(screen.queryByText('Kavya Reddy')).not.toBeInTheDocument();
    expect(screen.queryByText('SC-10044')).not.toBeInTheDocument();
  });

  it('opens the supplied orders screen and shows its live empty state', async () => {
    prepareAdmin();
    render(<AdminPage onSignIn={vi.fn()} onExitAdmin={vi.fn()} />);

    fireEvent.click(await screen.findByRole('button', { name: 'Orders' }));
    expect(await screen.findByText('No orders found')).toBeInTheDocument();
    expect(adminScreens.getOrders).toHaveBeenCalledWith(expect.objectContaining({ page: 1, pageSize: 20 }));
  });

  it('requires administrator access before showing the supplied screens', async () => {
    adminApi.getAdminAnalytics.mockRejectedValue(new Error('Admin request failed (403)'));
    const onSignIn = vi.fn();
    render(<AdminPage onSignIn={onSignIn} onExitAdmin={vi.fn()} />);

    fireEvent.click(await screen.findByRole('button', { name: 'Sign in to admin' }));
    expect(onSignIn).toHaveBeenCalledOnce();
    expect(screen.queryByText('Recent Orders')).not.toBeInTheDocument();
  });
});
