import { useEffect, useState } from 'react';
import { getCustomer, getCustomerOrders, type Customer } from '../services/customers';
import type { AdminOrderList } from '../../lib/api/admin';
import { EmptyState, TableSkeleton } from './AdminShared';
import AdminPagination from './AdminPagination';
export default function CustomerProfile({ id, onBack, onSelectOrder }: { id: number; onBack: () => void; onSelectOrder: (number: string) => void }) {
  const [customer, setCustomer] = useState<Customer>();
  const [orders, setOrders] = useState<AdminOrderList>();
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(false); setCustomer(undefined); setOrders(undefined);
    Promise.all([getCustomer(id, controller.signal), getCustomerOrders(id, page, controller.signal)])
      .then(([profile, history]) => { if (!controller.signal.aborted) { setCustomer(profile); setOrders(history); } })
      .catch(() => { if (!controller.signal.aborted) setError(true); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [id, page, retry]);
  return <div className="space-y-5">
    <button className="underline text-sm" onClick={onBack}>Back to customers</button>
    {loading ? <TableSkeleton /> : error ? <div role="alert">Customer details could not be loaded. <button className="underline" onClick={() => setRetry(x => x + 1)}>Try again</button></div> : customer && <>
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-5">
        <h2 className="font-serif text-xl">{customer.name || 'Unnamed customer'}</h2>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div><dt>Email</dt><dd className="break-all">{customer.email || 'Not provided'}</dd></div>
          <div><dt>Phone</dt><dd>{customer.phone || 'Not provided'}</dd></div>
          <div><dt>Status</dt><dd>{customer.status}</dd></div>
          <div><dt>Orders</dt><dd>{customer.orderCount}</dd></div>
          <div><dt>Joined</dt><dd>{customer.createdAt ? new Date(customer.createdAt).toLocaleDateString() : 'Not recorded'}</dd></div>
          <div><dt>Last login</dt><dd>{customer.lastLoginAt ? new Date(customer.lastLoginAt).toLocaleDateString() : 'Not recorded'}</dd></div>
        </dl>
      </section>
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-4"><h2 className="mb-4 font-serif text-xl">Order history</h2>
        {!orders?.items.length ? <EmptyState title="No linked orders" desc="This account has no linked orders yet." /> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th className="p-3">Order</th><th className="p-3">Status</th><th className="p-3">Payment</th><th className="p-3">Actions</th></tr></thead><tbody>{orders.items.map(order => <tr key={order.id} className="border-t border-[#E8E0D8]"><td className="p-3">{order.orderNumber}</td><td className="p-3">{order.status}</td><td className="p-3">{order.paymentStatus}</td><td className="p-3"><button className="underline" aria-label={`View order ${order.orderNumber}`} onClick={() => onSelectOrder(order.orderNumber)}>View</button></td></tr>)}</tbody></table></div>}
        {orders && <AdminPagination data={orders} onPage={setPage} label="Customer order pages" />}
      </section>
    </>}
  </div>;
}
