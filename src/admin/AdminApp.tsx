import { useState, useCallback } from 'react';
import type { AdminPage, DateRangePreset } from './types';
import AdminLayout from './layout/AdminLayout';
import DashboardPage from './pages/DashboardPage';
import OrdersPage from './pages/OrdersPage';
import OrderDetailPage from './pages/OrderDetailPage';
import FinancePage from './pages/FinancePage';
import ReturnsPage from './pages/ReturnsPage';
import OccasionsPage from './pages/OccasionsPage';
import PlaceholderPage from './pages/PlaceholderPage';

interface Props {
  onExitAdmin: () => void;
}

export default function AdminApp({ onExitAdmin }: Props) {
  const [page, setPage] = useState<AdminPage>('dashboard');
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [datePreset, setDatePreset] = useState<DateRangePreset>('30d');
  const [globalSearch, setGlobalSearch] = useState('');

  const navigate = useCallback((p: AdminPage) => {
    setPage(p);
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
        />
      )}

      {page === 'orders' && (
        <OrdersPage
          onSelectOrder={selectOrder}
          initialSearch={globalSearch}
        />
      )}

      {page === 'order-detail' && (
        <OrderDetailPage
          orderId={selectedOrderId}
          onBack={() => navigate('orders')}
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

      {(page === 'products' || page === 'inventory' || page === 'customers' || page === 'settings') && (
        <PlaceholderPage page={page} />
      )}
    </AdminLayout>
  );
}
