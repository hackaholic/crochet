import { useEffect, useState } from 'react';
import { accountProfileApi, type AccountOverviewOut, type ProfileOut } from '../lib/api/account';
import { accountApi, type AddressOut, type OrderOut } from '../lib/api/orders';
import { LoadingState } from '../components/StorefrontState';

type AddressDraft = { name: string; phone: string; line1: string; city: string; state: string; postalCode: string };
const emptyAddress: AddressDraft = { name: '', phone: '', line1: '', city: '', state: '', postalCode: '' };

export default function AccountPage({ onSignIn }: { onSignIn: () => void }) {
  const [overview, setOverview] = useState<AccountOverviewOut | null>(null);
  const [addresses, setAddresses] = useState<AddressOut[]>([]);
  const [orders, setOrders] = useState<OrderOut[]>([]);
  const [state, setState] = useState<'loading' | 'ready' | 'signedOut' | 'error'>('loading');
  const [profile, setProfile] = useState<Pick<ProfileOut, 'name' | 'email'>>({ name: '', email: '' });
  const [profileMessage, setProfileMessage] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);
  const [address, setAddress] = useState<AddressDraft>(emptyAddress);
  const [addressMessage, setAddressMessage] = useState('');
  const [savingAddress, setSavingAddress] = useState(false);

  useEffect(() => {
    Promise.all([accountProfileApi.overview(), accountApi.addresses(), accountApi.orders()])
      .then(([accountOverview, savedAddresses, savedOrders]) => {
        setOverview(accountOverview);
        setProfile({ name: accountOverview.profile.name ?? '', email: accountOverview.profile.email ?? '' });
        setAddresses(savedAddresses);
        setOrders(savedOrders);
        setState('ready');
      })
      .catch(error => setState(error instanceof Error && error.message === '401' ? 'signedOut' : 'error'));
  }, []);

  useEffect(() => {
    if (state === 'signedOut') onSignIn();
  }, [onSignIn, state]);

  const saveProfile = async () => {
    setSavingProfile(true);
    setProfileMessage('');
    try {
      const saved = await accountProfileApi.updateProfile(profile);
      setOverview(current => current ? { ...current, profile: saved } : current);
      setProfileMessage('Profile saved.');
    } catch { setProfileMessage('We could not save your profile. Please try again.'); }
    finally { setSavingProfile(false); }
  };

  const saveAddress = async () => {
    if (Object.values(address).some(value => !value.trim())) { setAddressMessage('Please complete every address field.'); return; }
    setSavingAddress(true);
    setAddressMessage('');
    try {
      const saved = await accountApi.createAddress(address);
      setAddresses(current => [...current, saved]);
      setOverview(current => current ? { ...current, savedAddresses: current.savedAddresses + 1 } : current);
      setAddress(emptyAddress);
      setAddressMessage('Address saved.');
    } catch { setAddressMessage('We could not save this address. Please try again.'); }
    finally { setSavingAddress(false); }
  };

  if (state === 'loading') return <div className="min-h-screen bg-[#FAF7F2] pt-28"><LoadingState label="Loading your account…" /></div>;
  if (state === 'signedOut') return null;
  if (state === 'error') return <div className="min-h-screen bg-[#FAF7F2] px-4 pt-36 text-center text-[#8B6B4A]">We could not load your account right now.</div>;

  return <main className="min-h-screen bg-[#FAF7F2] pt-28"><div className="mx-auto max-w-5xl px-4 py-10">
    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#C4622D]">Sulocraft account</p>
    <h1 className="mt-2 text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>Welcome back{overview?.profile.name ? `, ${overview.profile.name}` : ''}</h1>
    <section className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" aria-label="Account overview">
      <Metric label="Orders" value={overview?.totalOrders ?? 0} /><Metric label="Active orders" value={overview?.activeOrders ?? 0} /><Metric label="Saved addresses" value={overview?.savedAddresses ?? 0} /><Metric label="Wishlist items" value={overview?.wishlistItemsCount ?? 0} />
    </section>
    <div className="mt-8 grid gap-8 lg:grid-cols-2">
      <section className="rounded-2xl border border-[#EDE4D0] bg-white p-6"><h2 className="text-xl font-semibold text-[#2C1810]">Profile</h2><p className="mt-1 text-sm text-[#8B6B4A]">Keep your contact details up to date.</p><div className="mt-5 grid gap-3">
        <label className="grid gap-1 text-sm font-medium text-[#5C3D2E]">Name<input value={profile.name ?? ''} onChange={event => setProfile(current => ({ ...current, name: event.target.value }))} className="rounded-lg border border-[#EDE4D0] px-3 py-2" /></label>
        <label className="grid gap-1 text-sm font-medium text-[#5C3D2E]">Email<input type="email" value={profile.email ?? ''} onChange={event => setProfile(current => ({ ...current, email: event.target.value }))} className="rounded-lg border border-[#EDE4D0] px-3 py-2" /></label>
        {overview?.profile.phone && <p className="text-sm text-[#8B6B4A]">Phone: {overview.profile.phone}</p>}
        <button onClick={saveProfile} disabled={savingProfile} className="w-fit rounded-full bg-[#C4622D] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{savingProfile ? 'Saving…' : 'Save profile'}</button>{profileMessage && <p className="text-sm text-[#8B6B4A]" role="status">{profileMessage}</p>}
      </div></section>
      <section className="rounded-2xl border border-[#EDE4D0] bg-white p-6"><h2 className="text-xl font-semibold text-[#2C1810]">Order history</h2>{orders.length ? orders.map(order => <div key={order.id} className="mt-4 flex items-center justify-between border-t border-[#EDE4D0] pt-4 text-sm"><div><p className="font-semibold text-[#2C1810]">{order.orderNumber}</p><p className="capitalize text-[#8B6B4A]">{order.status.replaceAll('_', ' ').toLowerCase()}</p></div><p className="font-semibold text-[#2C1810]">₹{order.totalAmount}</p></div>) : <p className="mt-4 text-sm text-[#8B6B4A]">Your completed orders will appear here.</p>}</section>
      <section className="rounded-2xl border border-[#EDE4D0] bg-white p-6 lg:col-span-2"><h2 className="text-xl font-semibold text-[#2C1810]">Saved addresses</h2><div className="mt-4 grid gap-4 md:grid-cols-2">{addresses.map(item => <div key={item.id} className="rounded-xl border border-[#EDE4D0] p-4 text-sm text-[#5C3D2E]"><p className="font-semibold">{item.name} {item.isDefault && <span className="text-xs text-[#C4622D]">Default</span>}</p><p>{item.line1}, {item.city}, {item.state} {item.postalCode}</p><p>{item.phone}</p></div>)}</div>
        <div className="mt-5 grid gap-2 border-t border-[#EDE4D0] pt-4 md:grid-cols-2">{Object.entries(address).map(([key, value]) => <input key={key} value={value} onChange={event => setAddress(current => ({ ...current, [key]: event.target.value }))} placeholder={key === 'line1' ? 'Address line' : key === 'postalCode' ? 'PIN code' : key[0].toUpperCase() + key.slice(1)} className="rounded-lg border border-[#EDE4D0] px-3 py-2 text-sm" />)}</div>
        <button onClick={saveAddress} disabled={savingAddress} className="mt-3 rounded-full bg-[#C4622D] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{savingAddress ? 'Saving…' : 'Save address'}</button>{addressMessage && <p className="mt-2 text-sm text-[#8B6B4A]" role="status">{addressMessage}</p>}
      </section>
    </div>
  </div></main>;
}

function Metric({ label, value }: { label: string; value: number }) { return <div className="rounded-2xl border border-[#EDE4D0] bg-white p-5"><p className="text-2xl font-semibold text-[#2C1810]">{value}</p><p className="mt-1 text-sm text-[#8B6B4A]">{label}</p></div>; }
