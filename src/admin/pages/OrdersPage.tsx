import CustomerPopup, {type CustomerPreviewInput} from '../components/CustomerPopup';
import AdminTable from '../components/AdminTable';
import { useEffect, useState } from 'react';
import type { Order, OrderStatus } from '../types';
import * as api from '../services/api';
import { OrderStatusBadge, PaymentStatusBadge } from '../components/StatusBadge';
import { inr, EmptyState, TableSkeleton, Pagination } from '../components/AdminShared';

interface Props {
  onSelectOrder: (id: string) => void;
  initialSearch?: string;
  initialStatus?: OrderStatus;
  reportingRange?: {from: string; to: string};
}

type FilterStatus = 'ALL' | OrderStatus;

const FILTER_TABS: { id: FilterStatus; label: string }[] = [
  { id: 'ALL', label: 'All Orders' },
  { id: 'PENDING_PAYMENT', label: 'Pending Payment' },
  { id: 'PAID', label: 'Paid' },
  { id: 'CONFIRMED', label: 'Confirmed' },
  { id: 'OUT_FOR_DELIVERY', label: 'Out for Delivery' },
  { id: 'PROCESSING', label: 'Processing' },
  { id: 'READY_TO_SHIP', label: 'Ready to Ship' },
  { id: 'SHIPPED', label: 'Shipped' },
  { id: 'DELIVERED', label: 'Delivered' },
  { id: 'REFUNDED', label: 'Refunded' },
  { id: 'CANCELLED', label: 'Cancelled' },
];

const SORT_OPTIONS = [
  { value: 'date-desc',  label: 'Newest First' },
  { value: 'date-asc',   label: 'Oldest First' },
  { value: 'total-desc', label: 'Value: High to Low' },
  { value: 'total-asc',  label: 'Value: Low to High' },
];

export default function OrdersPage({ onSelectOrder, initialSearch = '', initialStatus, reportingRange }: Props) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [previewCustomer,setPreviewCustomer]=useState<CustomerPreviewInput>();
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<FilterStatus>(initialStatus ?? 'ALL');
  const [search, setSearch] = useState(initialSearch);
  const [sort, setSort] = useState('date-desc');
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;
  const [error,setError] = useState(false);
  const [attempt,setAttempt] = useState(0);

  useEffect(() => { setPage(1); }, [statusFilter, search, sort]);
  useEffect(() => {
    let active = true;
    setLoading(true); setError(false); setOrders([]); setTotal(0);
    const [sortBy, sortDir] = sort.split('-') as [string, 'asc' | 'desc'];
    api.getOrders({ status: statusFilter, dateFrom: reportingRange?.from, dateTo: reportingRange?.to, search: search.trim() || undefined, sortBy, sortDir, page, pageSize: PAGE_SIZE })
      .then(res => { if (active) { setOrders(res.orders); setTotal(res.total); } })
      .catch(() => { if (active) setError(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [statusFilter, search, sort, page, attempt, reportingRange?.from, reportingRange?.to]);

  function relDate(ts: string) {
    const d = new Date(ts);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' });
  }

  return (
    <div className="space-y-4">
      {previewCustomer && <CustomerPopup customer={previewCustomer} onClose={()=>setPreviewCustomer(undefined)} onSelectOrder={id=>{setPreviewCustomer(undefined);onSelectOrder?.(id);}}/>}
      {error && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm">Orders could not be loaded. <button className="underline" onClick={()=>setAttempt(v=>v+1)}>Retry orders</button></div>}
      {reportingRange && <p className="text-sm text-[#6B5B4E]">Reporting period: {reportingRange.from} to {reportingRange.to} (IST, inclusive). Open Orders from the sidebar to view all dates.</p>}
      {/* Filter tabs */}
      <div className="flex gap-1 bg-white rounded-xl border border-[#E8E0D8] p-1 overflow-x-auto">
        {FILTER_TABS.map(tab => (
          <button
            key={tab.id}
            aria-pressed={statusFilter === tab.id}
            onClick={() => setStatusFilter(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${statusFilter === tab.id ? 'bg-[#C4622D] text-white shadow-sm' : 'text-[#6B5B4E] hover:text-[#1A1108] hover:bg-[#F5F0EA]'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search + sort bar */}
      <div className="flex flex-wrap gap-3 items-center bg-white rounded-xl border border-[#E8E0D8] p-3">
        <div className="relative flex-1 min-w-48">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9C8B7E] text-sm">🔍</span>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Order number, customer, email, SKU…"
            className="w-full pl-9 pr-4 py-2 text-sm border border-[#E8E0D8] rounded-lg bg-[#FDFAF7] focus:outline-none focus:border-[#C4622D] transition-colors"
          />
          {search && <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9C8B7E] text-xs">✕</button>}
        </div>
        <select aria-label="Sort orders"
          value={sort}
          onChange={e => setSort(e.target.value)}
          className="px-3 py-2 text-sm border border-[#E8E0D8] rounded-lg bg-white focus:outline-none focus:border-[#C4622D] text-[#6B5B4E]"
        >
          {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <span className="text-xs text-[#9C8B7E] ml-auto">{total} order{total !== 1 ? 's' : ''}</span>
        <button disabled title="Export is unavailable until the backend provides an orders export endpoint." className="flex cursor-not-allowed items-center gap-1.5 rounded-lg border border-[#E8E0D8] px-3 py-2 text-xs font-medium text-[#B7AAA0]">↓ Export CSV</button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-[#E8E0D8] overflow-hidden">
        <div className="overflow-x-auto">
          <AdminTable className="w-full text-xs min-w-[900px]">
            <thead className="bg-[#F8F4EF] border-b border-[#E8E0D8] sticky top-0">
              <tr>
                {[
                  { label: 'Order', w: 90 }, { label: 'Date', w: 80 }, { label: 'Customer', w: 160 },
                  { label: 'Items', w: 50 }, { label: 'Total', w: 80 }, { label: 'Payment', w: 100 },
                  { label: 'Status', w: 130 }, { label: 'Issue', w: 150 }, { label: '', w: 60 },
                ].map(({ label, w }) => (
                  <th scope="col" key={label} className="text-left py-2.5 px-3 text-[#9C8B7E] font-semibold uppercase tracking-wider text-[10px] whitespace-nowrap" style={{ width: w }}>
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="p-4"><TableSkeleton rows={8} cols={8} /></td></tr>
              ) : error ? (
                <tr><td colSpan={9} className="p-4">Orders unavailable.</td></tr>
              ) : orders.length === 0 ? (
                <tr><td colSpan={9}><EmptyState icon="📋" title="No orders found" desc="Try adjusting your filters or search term." /></td></tr>
              ) : orders.map(order => (
                <tr
                  key={order.id}
                  className={`border-b border-[#F8F4EF] hover:bg-[#FDFAF7] transition-colors ${order.issueFlag ? 'border-l-2 border-l-[#F59E0B]' : ''}`}
                >
                  <td className="py-2.5 px-3">
                    <button type="button" className="admin-entity-link block w-full font-mono font-bold" onClick={()=>onSelectOrder(order.id)}>{order.orderNumber}</button>
                  </td>
                  <td className="py-2.5 px-3 text-[#6B5B4E] whitespace-nowrap">{relDate(order.date)}</td>
                  <td className="py-2.5 px-3">
                    <button type="button" className="admin-entity-link block w-full" aria-label={`View customer ${order.customer.name}`} onClick={()=>setPreviewCustomer(order.customer)}><span className="block font-medium">{order.customer.name}</span><span className="block text-[#9C8B7E]">{order.customer.email}</span></button>
                  </td>
                  <td className="py-2.5 px-3 text-center text-[#6B5B4E] font-medium">{order.items.length}</td>
                  <td className="py-2.5 px-3 font-bold text-[#1A1108] whitespace-nowrap">{inr(order.total)}</td>
                  <td className="py-2.5 px-3">
                    <PaymentStatusBadge status={order.paymentStatus} size="sm" />
                  </td>
                  <td className="py-2.5 px-3">
                    <OrderStatusBadge status={order.orderStatus} size="sm" />
                  </td>
                  <td className="py-2.5 px-3">
                    {order.issueFlag ? (
                      <span className="inline-flex items-center gap-1 text-[10px] text-[#92400E] bg-[#FFFBEB] px-2 py-0.5 rounded-full border border-[#FDE68A]">
                        ⚠ {order.issueFlag}
                      </span>
                    ) : (
                      <span className="text-[#D0C5BC]">—</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3">
                    <button
                      onClick={e => { e.stopPropagation(); onSelectOrder(order.id); }}
                      className="text-[#C4622D] hover:underline font-semibold"
                    >
                      View →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </AdminTable>
        </div>

        {/* Pagination */}
        {!loading && orders.length > 0 && (
          <div className="px-4 py-3 border-t border-[#F0EAE3]">
            <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPage={setPage} />
          </div>
        )}
      </div>
    </div>
  );
}
