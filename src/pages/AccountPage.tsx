import OrderItems from '../components/account/OrderItems';
import ProfileEditor from '../components/account/ProfileEditor';
import AddressManager from '../components/account/AddressManager';
import AccountNavigation, { type AccountSection } from '../components/account/AccountNavigation';
import OrderTrackingPanel from '../components/orders/OrderTrackingPanel';
import { useEffect, useState } from 'react';
import { accountProfileApi, type AccountOverviewOut } from '../lib/api/account';
import { accountApi, type AddressOut, type OrderOut } from '../lib/api/orders';
import { LoadingState } from '../components/StorefrontState';

export default function AccountPage({ onSignIn, onLogout }: { onSignIn: () => void; onLogout: () => Promise<void> }) {
  const [attempt,setAttempt] = useState(0);
  const [section, setSection] = useState<AccountSection>('profile');
  const [overview, setOverview] = useState<AccountOverviewOut | null>(null);
  const [addresses, setAddresses] = useState<AddressOut[]>([]);
  const [trackingOrder, setTrackingOrder] = useState<string>();
  const [orders, setOrders] = useState<OrderOut[]>([]);
  const [state, setState] = useState<'loading' | 'ready' | 'signedOut' | 'error'>('loading');
  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutMessage, setLogoutMessage] = useState('');

  useEffect(() => {
    let active = true;
    setState('loading');
    Promise.all([accountProfileApi.overview(), accountApi.addresses(), accountApi.orders()])
      .then(([accountOverview, savedAddresses, savedOrders]) => {
        if (!active) return;
        setOverview(accountOverview);
        setAddresses(savedAddresses);
        setOrders(savedOrders);
        setState('ready');
      })
      .catch(error => {if(active) setState(error instanceof Error && error.message === '401' ? 'signedOut' : 'error');});
    return () => {active=false;};
  }, [attempt]);

  useEffect(() => {
    if (state === 'signedOut') onSignIn();
  }, [onSignIn, state]);

  const signOut = async () => {
    setLoggingOut(true);
    setLogoutMessage('');
    try { await onLogout(); }
    catch { setLogoutMessage('We could not sign you out. Please try again.'); setLoggingOut(false); }
  };

  if (state === 'loading') return <div className="min-h-screen bg-[#FAF7F2] pt-28"><LoadingState label="Loading your account…" /></div>;
  if (state === 'signedOut') return null;
  if (state === 'error') return <div className="min-h-screen bg-[#FAF7F2] px-4 pt-36 text-center text-[#8B6B4A]">We could not load your account right now.<button type="button" onClick={()=>setAttempt(value=>value+1)} className="mt-4 block mx-auto underline">Retry account</button></div>;

  return <main className="min-h-screen bg-[#FAF7F2] pt-28"><div className="mx-auto max-w-5xl px-4 py-10">
    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#C4622D]">Sulocraft account</p>
    <div className="flex flex-wrap items-center justify-between gap-4">
      <h1 className="mt-2 text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>Welcome back{overview?.profile.name ? `, ${overview.profile.name}` : ''}</h1>
      <div className="flex flex-col items-end gap-2">
        <button type="button" onClick={signOut} disabled={loggingOut} className="rounded-full border border-[#C4622D] px-5 py-2.5 text-sm font-semibold text-[#C4622D] transition-colors hover:bg-[#C4622D] hover:text-white disabled:cursor-wait disabled:opacity-60">
          {loggingOut ? 'Signing out…' : 'Sign out'}
        </button>
        {logoutMessage && <p className="text-sm text-red-700" role="alert">{logoutMessage}</p>}
      </div>
    </div>
    <section className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" aria-label="Account overview">
      <Metric label="Orders" value={overview?.totalOrders ?? 0} /><Metric label="Active orders" value={overview?.activeOrders ?? 0} /><Metric label="Saved addresses" value={overview?.savedAddresses ?? 0} /><Metric label="Wishlist items" value={overview?.wishlistItemsCount ?? 0} />
    </section>
    <div className="mt-8"><AccountNavigation selected={section} onSelect={next => { setSection(next); setTrackingOrder(undefined); }} /></div>
    <div className="mt-6 grid gap-6">
      {section === 'profile' && overview && <ProfileEditor profile={overview.profile} onSaved={saved => setOverview(current => current ? {...current,profile:saved} : current)} />}
      {section === 'orders' && <section id="account-orders" aria-label="Orders" className="min-w-0 rounded-2xl border border-[#EDE4D0] bg-white p-6"><h2 className="text-xl font-semibold text-[#2C1810]">Order history</h2>{orders.length ? orders.map(order => <div key={order.id} className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-[#EDE4D0] pt-4 text-sm"><div><button type="button" className="break-all font-semibold text-[#2C1810] underline" onClick={()=>setTrackingOrder(order.orderNumber)} aria-label={`View order ${order.orderNumber}`}>{order.orderNumber}</button><p className="capitalize text-[#8B6B4A]">{order.status.replaceAll('_', ' ').toLowerCase()}</p></div><div><p className="font-semibold text-[#2C1810]">₹{order.totalAmount}</p><button type="button" aria-label={`Track shipment for ${order.orderNumber}`} aria-expanded={trackingOrder === order.orderNumber} className="mt-2 underline text-[#C4622D]" onClick={() => setTrackingOrder(order.orderNumber)}>Track shipment</button></div></div>) : <p className="mt-4 text-sm text-[#8B6B4A]">Your orders will appear here.</p>}</section>}
      {section === 'orders' && trackingOrder && <div className="min-w-0 space-y-3"><button type="button" className="underline text-sm" onClick={() => setTrackingOrder(undefined)}>Close shipment details</button><OrderItems key={`items-${trackingOrder}`} orderNumber={trackingOrder} /><OrderTrackingPanel key={trackingOrder} orderNumber={trackingOrder} /></div>}
      {section === 'addresses' && <AddressManager addresses={addresses} onChanged={fresh => {setAddresses(fresh);setOverview(current => current ? {...current,savedAddresses:fresh.length} : current);}} />}
    </div>
  </div></main>;
}

function Metric({ label, value }: { label: string; value: number }) { return <div className="rounded-2xl border border-[#EDE4D0] bg-white p-5"><p className="text-2xl font-semibold text-[#2C1810]">{value}</p><p className="mt-1 text-sm text-[#8B6B4A]">{label}</p></div>; }
