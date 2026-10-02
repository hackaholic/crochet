import { useEffect, useState, useCallback } from 'react';
import type { Order, OrderStatus } from '../types';
import * as api from '../services/api';
import { OrderStatusBadge, PaymentStatusBadge } from '../components/StatusBadge';
import { inr, EmptyState, TableSkeleton, Pagination } from '../components/AdminShared';

interface Props {
  onSelectOrder: (id: string) => void;
  initialSearch?: string;
}

type FilterStatus = 'ALL' | OrderStatus;

const FILTER_TABS: { id: FilterStatus; label: string }[] = [
  { id: 'ALL', label: 'All Orders' },
  { id: 'PENDING_PAYMENT', label: 'Pending Payment' },
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

export default function OrdersPage({ onSelectOrder, initialSearch = '' }: Props) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('ALL');
  const [search, setSearch] = useState(initialSearch);
  const [sort, setSort] = useState('date-desc');
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;

  const load = useCallback(() => {
    setLoading(true);
    const [sortBy, sortDir] = sort.split('-') as [string, 'asc' | 'desc'];
    api.getOrders({
      status: statusFilter === 'ALL' ? 'ALL' : statusFilter,
      search: search.trim() || undefined,
      sortBy,
      sortDir,
      page,
      pageSize: PAGE_SIZE,
    }).then(res => {
      setOrders(res.orders);
      setTotal(res.total);
      setLoading(false);
    });
  }, [statusFilter, search, sort, page]);

  useEffect(() => { setPage(1); }, [statusFilter, search, sort]);
  useEffect(() => { load(); }, [load]);

  function relDate(ts: string) {
    const d = new Date(ts);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' });
  }

  return (
    <div className="space-y-4">
      {/* Filter tabs */}
      <div className="flex gap-1 bg-white rounded-xl border border-[#E8E0D8] p-1 overflow-x-auto">
        {FILTER_TABS.map(tab => (
          <button
            key={tab.id}
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
        <select
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
          <table className="w-full text-xs min-w-[900px]">
            <thead className="bg-[#F8F4EF] border-b border-[#E8E0D8] sticky top-0">
              <tr>
                {[
                  { label: 'Order', w: 90 }, { label: 'Date', w: 80 }, { label: 'Customer', w: 160 },
                  { label: 'Items', w: 50 }, { label: 'Total', w: 80 }, { label: 'Payment', w: 100 },
                  { label: 'Status', w: 130 }, { label: 'Issue', w: 150 }, { label: '', w: 60 },
                ].map(({ label, w }) => (
                  <th key={label} className="text-left py-2.5 px-3 text-[#9C8B7E] font-semibold uppercase tracking-wider text-[10px] whitespace-nowrap" style={{ width: w }}>
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="p-4"><TableSkeleton rows={8} cols={8} /></td></tr>
              ) : orders.length === 0 ? (
                <tr><td colSpan={9}><EmptyState icon="📋" title="No orders found" desc="Try adjusting your filters or search term." /></td></tr>
              ) : orders.map(order => (
                <tr
                  key={order.id}
                  className={`border-b border-[#F8F4EF] hover:bg-[#FDFAF7] transition-colors cursor-pointer ${order.issueFlag ? 'border-l-2 border-l-[#F59E0B]' : ''}`}
                  onClick={() => onSelectOrder(order.id)}
                >
                  <td className="py-2.5 px-3">
                    <span className="font-mono font-bold text-[#1A1108]">{order.orderNumber}</span>
                  </td>
                  <td className="py-2.5 px-3 text-[#6B5B4E] whitespace-nowrap">{relDate(order.date)}</td>
                  <td className="py-2.5 px-3">
                    <p className="font-medium text-[#1A1108] truncate max-w-[140px]">{order.customer.name}</p>
                    <p className="text-[#9C8B7E] truncate max-w-[140px]">{order.customer.email}</p>
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
          </table>
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
