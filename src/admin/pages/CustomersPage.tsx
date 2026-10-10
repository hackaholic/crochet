import { useEffect, useState } from 'react';
import { getCustomers, type CustomerList } from '../services/customers';
import { controlClass } from '../components/CatalogueFields';
import { EmptyState, TableSkeleton } from '../components/AdminShared';
import CustomerProfile from '../components/CustomerProfile';
import AdminPagination from '../components/AdminPagination';
export default function CustomersPage({ onSelectOrder }: { onSelectOrder: (number: string) => void }) {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number>();
  const [data, setData] = useState<CustomerList>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(false); setData(undefined);
    const timer = window.setTimeout(() => {
      getCustomers(query.trim(), page, controller.signal)
        .then(result => { if (!controller.signal.aborted) setData(result); })
        .catch(() => { if (!controller.signal.aborted) setError(true); })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 275);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [query, page, retry]);
  if (selected !== undefined) return <CustomerProfile key={selected} id={selected} onBack={() => setSelected(undefined)} onSelectOrder={onSelectOrder} />;
  return <div className="space-y-5">
    <div><h1 className="font-serif text-2xl font-bold">Customers</h1><p className="mt-1 text-sm text-[#6B5B4E]">View customer profiles and linked order history.</p></div>
    <label className="block text-sm">Search customers<input type="search" maxLength={200} className={controlClass} value={query} onChange={e => { setQuery(e.target.value); setPage(1); }} /></label>
    <section className="rounded-xl border border-[#E8E0D8] bg-white p-4">
      {loading ? <TableSkeleton /> : error ? <div role="alert">Customers could not be loaded. <button className="underline" onClick={() => setRetry(x => x + 1)}>Try again</button></div> : !data?.items.length ? <EmptyState title="No customers found" desc="Try another search." /> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th className="p-3">Customer</th><th className="p-3">Email / phone</th><th className="p-3">Status</th><th className="p-3">Orders</th><th className="p-3">Actions</th></tr></thead><tbody>{data.items.map(customer => <tr key={customer.id} className="border-t border-[#E8E0D8]"><td className="p-3">{customer.name || 'Unnamed customer'}</td><td className="p-3"><span className="block">{customer.email || 'Not provided'}</span><span className="block">{customer.phone || 'Not provided'}</span></td><td className="p-3">{customer.status}</td><td className="p-3">{customer.orderCount}</td><td className="p-3"><button className="underline" aria-label={`View customer ${customer.name || customer.id}`} onClick={() => setSelected(customer.id)}>View</button></td></tr>)}</tbody></table></div>}
      {data && !loading && <AdminPagination data={data} onPage={setPage} label="Customer pages" />}
    </section>
  </div>;
}
