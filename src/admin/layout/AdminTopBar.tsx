import { useState, useEffect, useRef } from 'react';
import type { AdminPage, DateRangePreset, Order } from '../types';
import { getOrders } from '../services/api';
import { inr } from '../components/AdminShared';
import { OrderStatusBadge } from '../components/StatusBadge';

const PAGE_TITLES: Record<AdminPage, string> = {
  dashboard: 'Dashboard', orders: 'Orders', 'order-detail': 'Order Detail', products: 'Products',
  inventory: 'Inventory', customers: 'Customers', finance: 'Finance & Analytics', returns: 'Returns', occasions: 'Gift by Occasion', settings: 'Settings',
};
const DATE_PRESETS: { id: DateRangePreset; label: string }[] = [
  { id: 'today', label: 'Today' }, { id: 'yesterday', label: 'Yesterday' }, { id: '7d', label: 'Last 7 Days' },
  { id: '30d', label: 'Last 30 Days' }, { id: 'this_month', label: 'This Month' }, { id: 'prev_month', label: 'Previous Month' },
];
const PAGES_WITH_DATE: AdminPage[] = ['dashboard', 'finance'];

interface Props {
  currentPage: AdminPage;
  onSearch?: (q: string) => void;
  datePreset?: DateRangePreset;
  onDateChange?: (preset: DateRangePreset) => void;
  onSelectOrder?: (orderId: string) => void;
  onNavigateToOrders?: (q: string) => void;
  initialSearch?: string;
}

export default function AdminTopBar({
  currentPage,
  onSearch,
  datePreset = '30d',
  onDateChange,
  onSelectOrder,
  onNavigateToOrders,
  initialSearch = '',
}: Props) {
  const [search, setSearch] = useState(initialSearch);
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState<Order[]>([]);
  const [totalMatches, setTotalMatches] = useState(0);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const reqSeq = useRef(0);

  const showDate = PAGES_WITH_DATE.includes(currentPage);

  useEffect(() => {
    if (initialSearch !== undefined) {
      setSearch(initialSearch);
    }
  }, [initialSearch]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const query = search.trim();
    if (!query) {
      setResults([]);
      setTotalMatches(0);
      setLoading(false);
      setIsOpen(false);
      return;
    }

    setLoading(true);
    setIsOpen(true);
    const seq = ++reqSeq.current;

    const timer = setTimeout(async () => {
      try {
        const res = await getOrders({ search: query, pageSize: 6 });
        if (reqSeq.current === seq) {
          setResults(res.orders);
          setTotalMatches(res.total);
          setLoading(false);
        }
      } catch {
        if (reqSeq.current === seq) {
          setResults([]);
          setTotalMatches(0);
          setLoading(false);
        }
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [search]);

  const handleInputChange = (value: string) => {
    setSearch(value);
    onSearch?.(value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      setIsOpen(false);
      if (onNavigateToOrders) {
        onNavigateToOrders(search.trim());
      } else {
        onSearch?.(search);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleSelectOrder = (id: string) => {
    setIsOpen(false);
    onSelectOrder?.(id);
  };

  const handleViewAll = () => {
    setIsOpen(false);
    if (onNavigateToOrders) {
      onNavigateToOrders(search.trim());
    } else {
      onSearch?.(search);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex min-h-14 shrink-0 items-center gap-4 border-b border-[#E8E0D8] bg-white px-4 sm:px-5">
      <h1 className="mr-1 shrink-0 font-serif text-base font-bold text-[#1A1108]">{PAGE_TITLES[currentPage]}</h1>
      {currentPage !== 'products' && currentPage !== 'inventory' && currentPage !== 'customers' && (
        <div ref={wrapperRef} className="relative min-w-0 max-w-sm flex-1">
          <span aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[#9C8B7E]">⌕</span>
          <input
            type="search"
            value={search}
            onChange={event => handleInputChange(event.target.value)}
            onFocus={() => { if (search.trim()) setIsOpen(true); }}
            onKeyDown={handleKeyDown}
            aria-label="Search orders"
            placeholder="Search orders by number, ID, email, phone…"
            className="w-full rounded-lg border border-[#E8E0D8] bg-[#FDFAF7] py-2 pl-9 pr-7 text-sm text-[#1A1108] outline-none placeholder:text-[#9C8B7E] focus:border-[#C4622D] transition-colors"
          />
          {search && (
            <button
              type="button"
              onClick={() => { setSearch(''); onSearch?.(''); setIsOpen(false); }}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-[#9C8B7E] hover:text-[#1A1108]"
              aria-label="Clear search"
            >
              ✕
            </button>
          )}

          {isOpen && search.trim() && (
            <div
              role="region"
              aria-label="Search results"
              className="absolute left-0 right-0 top-full mt-1.5 z-50 max-h-[420px] overflow-y-auto rounded-xl border border-[#E8E0D8] bg-white shadow-xl p-2 text-left"
            >
              {loading ? (
                <div className="py-4 text-center text-xs text-[#6B5B4E]">
                  <span className="inline-block animate-pulse">Searching orders…</span>
                </div>
              ) : results.length === 0 ? (
                <div className="py-4 px-3 text-center text-xs text-[#6B5B4E]">
                  <p className="font-semibold text-[#1A1108]">No orders found for "{search.trim()}"</p>
                  <p className="mt-1 text-[11px] text-[#9C8B7E]">Try order number (SLC-...), ID, email, or phone.</p>
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="flex items-center justify-between px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-[#9C8B7E]">
                    <span>Matching Orders</span>
                    <span>{totalMatches} found</span>
                  </div>
                  {results.map(order => (
                    <button
                      key={order.id}
                      type="button"
                      onClick={() => handleSelectOrder(order.id)}
                      className="w-full text-left rounded-lg p-2.5 transition hover:bg-[#FDFAF7] border border-transparent hover:border-[#F5F0EA] group"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-mono font-bold text-xs text-[#1A1108] group-hover:text-[#C4622D] transition-colors">
                          {order.orderNumber}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-xs text-[#1A1108]">{inr(order.total)}</span>
                          <OrderStatusBadge status={order.orderStatus} size="sm" />
                        </div>
                      </div>
                      <div className="mt-1 flex items-center justify-between text-xs text-[#6B5B4E]">
                        <span className="truncate max-w-[200px]">
                          {order.customer.name || 'Customer'}{order.customer.phone ? ` • ${order.customer.phone}` : ''}
                        </span>
                        <span className="text-[11px] text-[#9C8B7E]">
                          {order.date ? new Date(order.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : ''}
                        </span>
                      </div>
                      {order.customer.email && (
                        <div className="text-[11px] text-[#9C8B7E] truncate mt-0.5">
                          {order.customer.email}
                        </div>
                      )}
                    </button>
                  ))}
                  <div className="pt-1 border-t border-[#F5F0EA]">
                    <button
                      type="button"
                      onClick={handleViewAll}
                      className="w-full rounded-lg bg-[#F5F0EA] py-2 text-center text-xs font-semibold text-[#C4622D] hover:bg-[#EFE8DF] transition-colors"
                    >
                      View all {totalMatches} matching orders →
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      <div className="flex-1" />
      {showDate && onDateChange && (
        <label className="flex shrink-0 items-center gap-2 text-xs text-[#6B5B4E]">
          <span className="hidden sm:inline">Period</span>
          <select
            aria-label="Date range"
            value={datePreset}
            onChange={event => onDateChange(event.target.value as DateRangePreset)}
            className="max-w-32 rounded-lg border border-[#E8E0D8] bg-white px-2.5 py-2 text-xs outline-none focus:border-[#C4622D]"
          >
            {DATE_PRESETS.map(preset => (
              <option key={preset.id} value={preset.id}>{preset.label}</option>
            ))}
          </select>
        </label>
      )}
      <span className="flex shrink-0 items-center gap-2 rounded-full bg-[#F5F0EA] px-3 py-2 text-xs font-medium text-[#6B5B4E]">
        <span className="grid h-6 w-6 place-items-center rounded-full bg-[#C4622D] text-[10px] font-bold text-white">S</span>
        <span className="hidden sm:inline">Sulocraft Admin</span>
      </span>
    </header>
  );
}
