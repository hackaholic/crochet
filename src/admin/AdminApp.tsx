import AdminPreviewDialog from './components/AdminPreviewDialog';
import ProductPreview from './components/ProductPreview';
import OrderPreview from './components/OrderPreview';
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
  onLogout?: () => Promise<void>;
}

export default function AdminApp({ onExitAdmin, onLogout }: Props) {
  const [page, setPage] = useState<AdminPage>('dashboard');
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [datePreset, setDatePreset] = useState<DateRangePreset>('30d');
  const [globalSearch, setGlobalSearch] = useState('');
  const [orderFilter, setOrderFilter] = useState<{status: OrderStatus; range: {from: string; to: string}}>();
  const [orderView, setOrderView] = useState(0);
  const [selectedProductId,setSelectedProductId]=useState<number>();
  const [preview,setPreview]=useState<{type:'product';id:number}|{type:'order';id:string}>();

  const navigate = useCallback((p: AdminPage) => {
    setPage(p);
    if(p==='products') setSelectedProductId(undefined);
    if (p === 'orders') { setOrderFilter(undefined); setOrderView(v => v + 1); }
    if (p !== 'order-detail') setSelectedOrderId(null);
  }, []);

  const selectOrder = useCallback((id: string) => {
    setPreview({type:'order',id});
  }, []);

  const navigateToOrdersWithSearch = useCallback((q: string) => {
    setGlobalSearch(q);
    setOrderFilter(undefined);
    setPage('orders');
    setOrderView(v => v + 1);
  }, []);

  return (
    <AdminLayout
      currentPage={page}
      onNavigate={navigate}
      onExitAdmin={onExitAdmin} onLogout={onLogout}
      onSearch={setGlobalSearch}
      datePreset={datePreset}
      onDateChange={setDatePreset}
      onSelectOrder={selectOrder}
      onNavigateToOrders={navigateToOrdersWithSearch}
      initialSearch={globalSearch}
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
        <FinancePage datePreset={datePreset} onSelectProduct={id=>setPreview({type:'product',id})} onFilterOrders={(status,range)=>{setOrderFilter({status,range});setOrderView(v=>v+1);setGlobalSearch('');setPage('orders');}} />
      )}

      {page === 'returns' && (
        <ReturnsPage
          onSelectOrder={selectOrder}
        />
      )}

      {page === 'occasions' && <OccasionsPage />}

      {page === 'products' && <ProductsPage initialProductId={selectedProductId} onPreviewProduct={id=>setPreview({type:'product',id})} />}

      {page === 'inventory' && <InventoryPage onSelectProduct={id=>setPreview({type:'product',id})} />}

      {page === 'customers' && <CustomersPage onSelectOrder={selectOrder} />}

      {page === 'settings' && <SettingsPage />}
      {preview && <AdminPreviewDialog key={`${preview.type}-${preview.id}`} title={preview.type==='product'?'Product preview':'Order summary'} onClose={()=>setPreview(undefined)}>{preview.type==='product'?<ProductPreview id={preview.id} onEdit={id=>{setPreview(undefined);setSelectedProductId(id);setPage('products');}}/>:<OrderPreview id={preview.id} onView={id=>{setPreview(undefined);setSelectedOrderId(id);setPage('order-detail');}}/>}</AdminPreviewDialog>}
    </AdminLayout>
  );
}
