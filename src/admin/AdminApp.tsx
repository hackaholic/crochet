import { dateRange } from './services/dateRange';
import { useState, useCallback } from 'react';
import type { AdminPage, OrderStatus, DateRangePreset } from './types';
import AdminLayout from './layout/AdminLayout';
import DashboardPage from './pages/DashboardPage';
import OrdersPage from './pages/OrdersPage';
import OrderDetailPage from './pages/OrderDetailPage';
import FinancePage from './pages/FinancePage';
import ReturnsPage from './pages/ReturnsPage';
import OccasionsPage from './pages/OccasionsPage';
import ProductsPage from './pages/ProductsPage';
import InventoryPage from './pages/InventoryPage';
import CustomersPage from './pages/CustomersPage';
import SettingsPage from './pages/SettingsPage';

interface Props {
  onExitAdmin: () => void;
}

export default function AdminApp({ onExitAdmin }: Props) {
  const [page, setPage] = useState<AdminPage>('dashboard');
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [datePreset, setDatePreset] = useState<DateRangePreset>('30d');
  const [globalSearch, setGlobalSearch] = useState('');
  const [orderFilter, setOrderFilter] = useState<{status: OrderStatus; range: {from: string; to: string}}>();
  const [orderView, setOrderView] = useState(0);

  const navigate = useCallback((p: AdminPage) => {
    setPage(p);
    if (p === 'orders') { setOrderFilter(undefined); setOrderView(v => v + 1); }
    if (p !== 'order-detail') setSelectedOrderId(null);
  }, []);

  const selectOrder = useCallback((id: string) => {
    setSelectedOrderId(id);
    setPage('order-detail');
  }, []);

  return (
    <AdminLayout
      currentPage={page}
      onNavigate={navigate}
      onExitAdmin={onExitAdmin}
      onSearch={setGlobalSearch}
      datePreset={datePreset}
      onDateChange={setDatePreset}
    >
      {page === 'dashboard' && (
        <DashboardPage
          onNavigate={(p) => navigate(p)}
          onSelectOrder={selectOrder}
          datePreset={datePreset}
          onFilterOrders={status => { setOrderFilter({status, range: dateRange(datePreset)}); setOrderView(v => v + 1); setGlobalSearch(''); setPage('orders'); }}
        />
      )}

      {page === 'orders' && (
        <OrdersPage
          key={orderView}
          initialStatus={orderFilter?.status}
          reportingRange={orderFilter?.range}
          onSelectOrder={selectOrder}
          initialSearch={globalSearch}
        />
      )}

      {page === 'order-detail' && (
        <OrderDetailPage
          orderId={selectedOrderId}
          onBack={() => { setSelectedOrderId(null); setPage('orders'); }}
        />
      )}

      {page === 'finance' && (
        <FinancePage datePreset={datePreset} />
      )}

      {page === 'returns' && (
        <ReturnsPage
          onSelectOrder={(id) => { setSelectedOrderId(id); navigate('order-detail'); }}
        />
      )}

      {page === 'occasions' && <OccasionsPage />}

      {page === 'products' && <ProductsPage />}

      {page === 'inventory' && <InventoryPage />}

      {page === 'customers' && <CustomersPage onSelectOrder={selectOrder} />}

      {page === 'settings' && <SettingsPage />}
    </AdminLayout>
  );
}
