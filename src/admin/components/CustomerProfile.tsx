import { useEffect, useState } from 'react';
import { getCustomer, getCustomerOrders, type CustomerDetail } from '../services/customers';
import type { AdminOrderList } from '../../lib/api/admin';
import { EmptyState, TableSkeleton } from './AdminShared';
import AdminPagination from './AdminPagination';
export default function CustomerProfile({ id, onBack, onSelectOrder }: { id: number; onBack: () => void; onSelectOrder: (number: string) => void }) {
  const [customer, setCustomer] = useState<CustomerDetail>();
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
  return <div className="min-w-0 space-y-5 [overflow-wrap:anywhere]">
    <button className="underline text-sm" onClick={onBack}>Back to customers</button>
    {loading ? <TableSkeleton /> : error ? <div role="alert">Customer details could not be loaded. <button className="underline" onClick={() => setRetry(x => x + 1)}>Try again</button></div> : customer && <>
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-5">
        <h2 className="font-serif text-xl">{customer.name || 'Unnamed customer'}</h2>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div><dt className="text-[#6B5B4E]">Email</dt><dd className="break-all font-medium">{customer.email || 'Not provided'}</dd></div>
          <div><dt className="text-[#6B5B4E]">Account Phone</dt><dd className="font-medium">{customer.phone || 'Not provided'}</dd></div>
          <div><dt className="text-[#6B5B4E]">Status</dt><dd className="font-medium">{customer.status}</dd></div>
          <div><dt className="text-[#6B5B4E]">Orders</dt><dd className="font-medium">{customer.orderCount}</dd></div>
          <div><dt className="text-[#6B5B4E]">Joined</dt><dd className="font-medium">{customer.createdAt ? new Date(customer.createdAt).toLocaleDateString() : 'Not recorded'}</dd></div>
          <div><dt className="text-[#6B5B4E]">Last login</dt><dd className="font-medium">{customer.lastLoginAt ? new Date(customer.lastLoginAt).toLocaleDateString() : 'Not recorded'}</dd></div>
        </dl>
      </section>

      <section className="rounded-xl border border-[#E8E0D8] bg-white p-5">
        <h2 className="mb-4 font-serif text-xl">Saved addresses</h2>
        {!customer.addresses?.length ? (
          <EmptyState title="No saved addresses" desc="This account has no saved addresses on file." />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {customer.addresses.map(addr => (
              <div
                key={addr.id}
                className="min-w-0 relative rounded-lg border border-[#E8E0D8] p-4 text-sm space-y-1 bg-[#FAF7F4]"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-base text-[#2E241E]">{addr.name}</span>
                  {addr.isDefault && (
                    <span className="rounded-full bg-[#E5D7C7] px-2.5 py-0.5 text-xs font-semibold text-[#5B3E2B]">
                      Default
                    </span>
                  )}
                </div>
                <p className="text-[#6B5B4E]">
                  <span className="font-medium text-[#2E241E]">Contact:</span> {addr.phone || 'Not provided'}
                </p>
                <p className="text-[#2E241E]">{addr.line1}</p>
                {addr.line2 && <p className="text-[#2E241E]">{addr.line2}</p>}
                {addr.landmark && (
                  <p className="text-xs text-[#6B5B4E]">
                    <span className="font-medium">Landmark:</span> {addr.landmark}
                  </p>
                )}
                <p className="text-[#2E241E]">
                  {addr.city}, {addr.state} {addr.postalCode}
                </p>
                <p className="text-xs text-[#6B5B4E]">{addr.country}</p>
              </div>
            ))}
          </div>
        )}
      </section>
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-4"><h2 className="mb-4 font-serif text-xl">Order history</h2>
        {!orders?.items.length ? <EmptyState title="No linked orders" desc="This account has no linked orders yet." /> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th className="p-3">Order</th><th className="p-3">Status</th><th className="p-3">Payment</th><th className="p-3">Actions</th></tr></thead><tbody>{orders.items.map(order => <tr key={order.id} className="border-t border-[#E8E0D8]"><td className="p-3">{order.orderNumber}</td><td className="p-3">{order.status}</td><td className="p-3">{order.paymentStatus}</td><td className="p-3"><button className="underline" aria-label={`View order ${order.orderNumber}`} onClick={() => onSelectOrder(order.orderNumber)}>View</button></td></tr>)}</tbody></table></div>}
        {orders && <AdminPagination data={orders} onPage={setPage} label="Customer order pages" />}
      </section>
    </>}
  </div>;
}
