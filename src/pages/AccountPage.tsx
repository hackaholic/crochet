import { Link } from 'react-router';
import OrderHistory from '../components/account/OrderHistory';
import OrderItems from '../components/account/OrderItems';
import ProfileEditor from '../components/account/ProfileEditor';
import AddressManager from '../components/account/AddressManager';
import AccountNavigation, { type AccountSection } from '../components/account/AccountNavigation';
import OrderTrackingPanel from '../components/orders/OrderTrackingPanel';
import { useEffect, useState } from 'react';
import { accountProfileApi, type AccountOverviewOut } from '../lib/api/account';
import { accountApi, type AddressOut, type OrderOut } from '../lib/api/orders';
import { LoadingState } from '../components/StorefrontState';

export default function AccountPage({ onSignIn, onLogout, isAdmin = false }: { onSignIn: () => void; onLogout: () => Promise<void>; isAdmin?: boolean }) {
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
    {!isAdmin && <section className="mt-8 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Account overview">
      <Metric tone="rose" icon="orders" label="Orders" value={overview?.totalOrders ?? 0} /><Metric tone="sage" icon="active" label="Active orders" value={overview?.activeOrders ?? 0} /><Metric tone="sand" icon="address" label="Saved addresses" value={overview?.savedAddresses ?? 0} /><Metric tone="lavender" icon="wishlist" label="Wishlist items" value={overview?.wishlistItemsCount ?? 0} />
    </section>}
    {isAdmin && <Link to="/admin" className="mt-6 inline-flex rounded-full bg-[#C4622D] px-5 py-2.5 text-sm font-semibold text-white">Admin Dashboard</Link>}
    <div className="mt-8"><AccountNavigation hideOrders={isAdmin} selected={section} onSelect={next => { setSection(next); setTrackingOrder(undefined); }} /></div>
    <div className="mt-6 grid gap-6">
      {section === 'profile' && overview && <ProfileEditor profile={overview.profile} onSaved={saved => setOverview(current => current ? {...current,profile:saved} : current)} />}
      {section === 'orders' && <OrderHistory orders={orders} selected={trackingOrder} onSelect={setTrackingOrder} />}
      {section === 'orders' && trackingOrder && <div className="min-w-0 space-y-3"><button type="button" className="underline text-sm" onClick={() => setTrackingOrder(undefined)}>Close shipment details</button><OrderItems key={`items-${trackingOrder}`} orderNumber={trackingOrder} /><OrderTrackingPanel key={trackingOrder} orderNumber={trackingOrder} /></div>}
      {section === 'addresses' && <AddressManager addresses={addresses} onChanged={fresh => {setAddresses(fresh);setOverview(current => current ? {...current,savedAddresses:fresh.length} : current);}} />}
    </div>
  </div></main>;
}

const METRIC_TONES = {
  rose: { surface: '#FFF5F1', ink: '#9A4025', border: '#F1D5C9' },
  sage: { surface: '#EFF6F0', ink: '#305E46', border: '#D5E5D9' },
  sand: { surface: '#FBF5E9', ink: '#79572D', border: '#EADCC1' },
  lavender: { surface: '#F5F1FB', ink: '#664A88', border: '#E3D8EF' },
};
const METRIC_ICONS = {
  orders: 'M5 7h14v13H5z M8 7V5a4 4 0 0 1 8 0v2',
  active: 'M3 6h11v12H3z M14 10h4l3 4v4h-7 M5 18a2 2 0 1 0 4 0 M16 18a2 2 0 1 0 4 0',
  address: 'M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0z M15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
  wishlist: 'M20 5c-3-3-6-1-8 1-2-2-5-4-8-1-4 4 0 9 8 15 8-6 12-11 8-15z',
};
function Metric({ label, value, tone, icon }: { label: string; value: number; tone: keyof typeof METRIC_TONES; icon: keyof typeof METRIC_ICONS }) {
  const palette = METRIC_TONES[tone];
  return <div className="min-w-0 rounded-2xl border p-4 shadow-[0_3px_12px_rgba(44,24,16,0.025)] sm:p-5" style={{ background: palette.surface, borderColor: palette.border }}>
    <div className="mb-4 flex items-center justify-between gap-2"><span aria-hidden="true" className="flex h-10 w-10 items-center justify-center rounded-xl border bg-white/75" style={{ color: palette.ink, borderColor: palette.border }}><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d={METRIC_ICONS[icon]} /></svg></span><span aria-hidden="true" className="h-1.5 w-1.5 rounded-full" style={{ background: palette.ink }} /></div>
    <p className="text-3xl font-semibold tabular-nums text-[#2C1810]">{value}</p><p className="mt-1.5 text-sm font-medium" style={{ color: palette.ink }}>{label}</p>
  </div>;
}
