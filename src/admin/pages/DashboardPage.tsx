import { useEffect, useState } from 'react';
import type { DashboardSummary, OrderStatusCount, AttentionItem, ActivityItem, InventoryAlert, SalesDataPoint, Order, DateRangePreset } from '../types';
import * as api from '../services/api';
import { MetricCard, SectionHeader, SeverityBadge, inr, pct, EmptyState, TableSkeleton } from '../components/AdminShared';
import { OrderStatusBadge } from '../components/StatusBadge';
import RevenueChart from '../components/RevenueChart';

interface Props {
  onNavigate: (page: 'orders' | 'order-detail') => void;
  onSelectOrder: (id: string) => void;
  datePreset: DateRangePreset;
}

// ─── Status pipeline ──────────────────────────────────────────────────────────
const PIPELINE_STATUSES = ['PENDING_PAYMENT','PAID','CONFIRMED','PROCESSING','READY_TO_SHIP','SHIPPED','OUT_FOR_DELIVERY','DELIVERED'] as const;
const EXCEPTION_STATUSES = ['CANCELLED','REFUNDED'] as const;

function StatusPipeline({ counts }: { counts: OrderStatusCount[] }) {
  const byStatus = Object.fromEntries(counts.map(c => [c.status, c.count]));
  return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
      <SectionHeader title="Order Pipeline" />
      {/* Main flow */}
      <div className="grid grid-cols-4 lg:grid-cols-8 gap-2 mb-4">
        {PIPELINE_STATUSES.map(status => {
          const count = byStatus[status] ?? 0;
          return (
            <div key={status} className="text-center p-2 rounded-lg bg-[#F8F4EF] border border-[#F0EAE3]">
              <p className="text-2xl font-bold text-[#1A1108]" style={{ fontFamily: 'var(--font-serif)' }}>{count}</p>
              <OrderStatusBadge status={status} size="sm" />
            </div>
          );
        })}
      </div>
      {/* Exceptions */}
      <p className="text-[10px] text-[#9C8B7E] uppercase tracking-wider font-semibold mb-2">Exceptions</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {EXCEPTION_STATUSES.map(status => {
          const count = byStatus[status] ?? 0;
          return (
            <div key={status} className={`text-center p-2 rounded-lg border ${count > 0 ? 'bg-[#FFF7F5] border-[#F2C4CE]' : 'bg-[#F8F4EF] border-[#F0EAE3]'}`}>
              <p className={`text-xl font-bold ${count > 0 ? 'text-[#C4622D]' : 'text-[#9C8B7E]'}`} style={{ fontFamily: 'var(--font-serif)' }}>{count}</p>
              <OrderStatusBadge status={status} size="sm" />
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Needs attention ──────────────────────────────────────────────────────────
function NeedsAttention({ items, onView }: { items: AttentionItem[]; onView: (id: string) => void }) {
  const severityOrder = { critical: 0, warning: 1, info: 2 };
  const sorted = [...items].sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);

  return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
      <SectionHeader
        title="Needs Attention"
        subtitle={`${items.filter(i => i.severity === 'critical').length} critical · ${items.filter(i => i.severity === 'warning').length} warnings`}
        action={
          <span className="w-6 h-6 flex items-center justify-center bg-[#FEF2F2] text-[#991B1B] text-xs font-bold rounded-full">
            {items.length}
          </span>
        }
      />
      {items.length === 0 ? (
        <EmptyState icon="✅" title="No attention needed" desc="All orders are running smoothly." />
      ) : (
        <div className="space-y-3">
          {sorted.map(item => (
            <div
              key={item.id}
              className={`flex gap-3 p-3 rounded-xl border ${item.severity === 'critical' ? 'border-[#FECACA] bg-[#FFF8F8]' : item.severity === 'warning' ? 'border-[#FDE68A] bg-[#FFFCF0]' : 'border-[#BFDBFE] bg-[#F8FBFF]'}`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-xs font-bold text-[#1A1108]">{item.orderNumber}</span>
                  <SeverityBadge severity={item.severity} />
                </div>
                <p className="text-xs font-semibold text-[#1A1108] mb-0.5">{item.issueType}</p>
                <p className="text-xs text-[#6B5B4E] leading-snug">{item.description}</p>
                <p className="text-[10px] text-[#9C8B7E] mt-1">
                  Age in status: {item.ageInStatusHours >= 24 ? `${Math.floor(item.ageInStatusHours / 24)}d ${item.ageInStatusHours % 24}h` : `${item.ageInStatusHours}h`}
                </p>
              </div>
              {item.orderNumber && <button onClick={() => onView(item.orderId)} className="shrink-0 self-start rounded-lg border border-[#C4622D]/30 px-3 py-1.5 text-xs font-semibold text-[#C4622D] transition-colors hover:bg-[#C4622D] hover:text-white">View</button>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Inventory alerts ─────────────────────────────────────────────────────────
function InventoryAlerts({ items }: { items: InventoryAlert[] }) {
  return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
      <SectionHeader title="Inventory Alerts" subtitle={`${items.filter(i => i.alertLevel === 'out').length} out of stock`} />
      {items.length === 0 ? (
        <EmptyState icon="📦" title="Inventory OK" />
      ) : (
        <div className="space-y-2.5">
          {items.map(item => (
            <div key={item.id} className="flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-semibold text-[#1A1108] truncate">{item.productName}</p>
                  <span className={`shrink-0 text-[10px] px-1.5 py-0.5 rounded font-semibold ${item.alertLevel === 'out' ? 'bg-[#FEF2F2] text-[#991B1B]' : 'bg-[#FFFBEB] text-[#92400E]'}`}>
                    {item.alertLevel === 'out' ? 'OUT' : 'LOW'}
                  </span>
                </div>
                <p className="text-[10px] text-[#9C8B7E] mt-0.5">{item.sku} · Available stock</p>
              </div>
              <div className="text-right shrink-0">
                <p className="text-xs text-[#6B5B4E]">Avail: <span className={`font-bold ${item.available === 0 ? 'text-[#EF4444]' : 'text-[#1A1108]'}`}>{item.available}</span></p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Activity feed ────────────────────────────────────────────────────────────
const ACTIVITY_ICONS: Record<string, string> = {
  order_placed: '🛒', order_updated: '↻', order_shipped: '🚚', return_requested: '↩',
  refund_completed: '💸', low_stock: '📦', payment_failed: '❌', order_delivered: '✅',
};
function ActivityFeed({ items }: { items: ActivityItem[] }) {
  function relTime(ts: string) {
    const diff = (Date.now() - new Date(ts).getTime()) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  }
  return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
      <SectionHeader title="Activity Feed" />
      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
        {items.map(item => (
          <div key={item.id} className="flex items-start gap-2.5">
            <span className="text-sm shrink-0 mt-0.5">{ACTIVITY_ICONS[item.type] ?? '•'}</span>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-[#1A1108] leading-snug">{item.message}</p>
              {item.orderNumber && <p className="text-[10px] font-mono text-[#C4622D] mt-0.5">{item.orderNumber}</p>}
            </div>
            <span className="text-[10px] text-[#9C8B7E] shrink-0 mt-0.5">{relTime(item.timestamp)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Recent orders ────────────────────────────────────────────────────────────
function RecentOrders({ orders, onView, onViewAll }: { orders: Order[]; onView: (id: string) => void; onViewAll: () => void }) {
  return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
      <SectionHeader
        title="Recent Orders"
        action={
          <button onClick={onViewAll} className="text-xs text-[#C4622D] font-semibold hover:underline">
            View All →
          </button>
        }
      />
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-[#F0EAE3]">
              {['Order', 'Customer', 'Amount', 'Status', 'Time', ''].map(h => (
                <th key={h} className="text-left py-2 px-2 text-[#9C8B7E] font-semibold text-[10px] uppercase tracking-wider whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {orders.slice(0, 8).map(order => (
              <tr key={order.id} className="border-b border-[#F8F4EF] hover:bg-[#FDFAF7] transition-colors">
                <td className="py-2 px-2">
                  <span className="font-mono font-semibold text-[#1A1108]">{order.orderNumber}</span>
                </td>
                <td className="py-2 px-2">
                  <span className="text-[#6B5B4E] truncate max-w-[100px] block">{order.customer.name}</span>
                </td>
                <td className="py-2 px-2 font-semibold text-[#1A1108] whitespace-nowrap">{inr(order.total)}</td>
                <td className="py-2 px-2">
                  <OrderStatusBadge status={order.orderStatus} size="sm" />
                </td>
                <td className="py-2 px-2 text-[#9C8B7E] whitespace-nowrap">
                  {new Date(order.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
                </td>
                <td className="py-2 px-2">
                  <button onClick={() => onView(order.id)} className="text-[#C4622D] hover:underline font-semibold">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── Dashboard Page ───────────────────────────────────────────────────────────
export default function DashboardPage({ onNavigate, onSelectOrder, datePreset }: Props) {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [counts, setCounts] = useState<OrderStatusCount[]>([]);
  const [attention, setAttention] = useState<AttentionItem[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [inventory, setInventory] = useState<InventoryAlert[]>([]);
  const [chartData, setChartData] = useState<SalesDataPoint[]>([]);
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getDashboardSummary(datePreset),
      api.getOrderStatusCountsForPeriod(datePreset),
      api.getAttentionItems(),
      api.getActivityFeed(),
      api.getInventoryAlerts(),
      api.getSalesChart(datePreset === '7d' ? '7d' : '30d'),
      api.getOrders({ pageSize: 10, sortBy: 'date' }),
    ]).then(([s, c, a, act, inv, chart, orders]) => {
      setSummary(s);
      setCounts(c);
      setAttention(a);
      setActivity(act);
      setInventory(inv);
      setChartData(chart);
      setRecentOrders(orders.orders);
      setLoading(false);
    });
  }, [datePreset]);

  const kpis = summary ? [
    { label: 'Total Sales', value: inr(summary.totalRevenue), icon: '₹', change: summary.comparison?.salesGrowthPercent ?? undefined, prev: summary.comparison ? 'previous period' : undefined },
    { label: 'Net Revenue', value: inr(summary.netRevenue), icon: '💰', prev: summary.period },
    { label: 'Orders', value: String(summary.orders), icon: '📋', change: summary.comparison?.orderGrowthPercent ?? undefined, prev: summary.comparison ? 'previous period' : undefined },
    { label: 'Average Order Value', value: inr(summary.avgOrderValue), icon: '📊', prev: summary.period },
    { label: 'Refunds', value: inr(summary.refunds), icon: '↩', accent: '#EF4444' },
  ] : [];

  const handleViewOrder = (id: string) => {
    onSelectOrder(id);
    onNavigate('order-detail');
  };

  return (
    <div className="space-y-5 max-w-full">
      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {loading
          ? Array.from({ length: 5 }).map((_, i) => <MetricCard key={i} label="" value="" icon="" loading />)
          : kpis.map(k => (
              <MetricCard key={k.label} label={k.label} value={k.value} icon={k.icon} change={k.change} prev={k.prev} accent={k.accent} />
            ))}
      </div>

      {/* Chart */}
      <RevenueChart data={chartData} loading={loading} />

      {/* Status pipeline */}
      {!loading && <StatusPipeline counts={counts} />}

      {/* Attention + Activity */}
      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <NeedsAttention items={attention} onView={handleViewOrder} />
        </div>
        <div>
          <ActivityFeed items={activity} />
        </div>
      </div>

      {/* Recent orders + Inventory */}
      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          {loading ? <div className="bg-white rounded-xl border border-[#E8E0D8] p-5"><TableSkeleton rows={6} cols={5} /></div>
            : <RecentOrders orders={recentOrders} onView={handleViewOrder} onViewAll={() => onNavigate('orders')} />
          }
        </div>
        <div>
          <InventoryAlerts items={inventory} />
        </div>
      </div>
    </div>
  );
}
