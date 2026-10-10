import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router';
import OrderTrackingPanel from '../components/orders/OrderTrackingPanel';
import { requestTrackingLink } from '../lib/api/tracking';

export default function GuestTrackingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const encodedOrder = location.pathname.split('/')[2] ?? '';
  let selectedOrder = '';
  try { selectedOrder = decodeURIComponent(encodedOrder); } catch { /* Invalid link uses recovery form. */ }
  const queryToken = new URLSearchParams(location.search).get('token');
  const token = new URLSearchParams(location.hash.slice(1)).get('token') || queryToken;
  const [orderNumber, setOrderNumber] = useState(selectedOrder);
  const [email, setEmail] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState(false);
  useEffect(() => {
    if (queryToken) navigate({ pathname: location.pathname, hash: `token=${encodeURIComponent(queryToken)}` }, { replace: true });
  }, [queryToken, location.pathname, navigate]);
  return <div className="min-h-screen bg-[#FAF7F2] px-4 pb-12 pt-32"><div className="mx-auto max-w-3xl space-y-6">
    <h1 className="font-serif text-3xl text-[#2C1810]">Track your order</h1>
    <p className="text-sm text-[#8B6B4A]">Use your secure tracking link to view shipment details without signing in.</p>
    {token && selectedOrder && <OrderTrackingPanel key={`${selectedOrder}:${token}`} orderNumber={selectedOrder} guestToken={token} />}
    <section className="rounded-2xl border border-[#EDE4D0] bg-white p-5">
      <h2 className="font-serif text-xl">Need a tracking link?</h2>
      <p className="mt-2 text-sm text-[#8B6B4A]">Enter your order number and the email used at checkout. Expired links can be replaced here.</p>
      <form className="mt-4 grid gap-4" onSubmit={async event => {
        event.preventDefault(); if (busy) return;
        setBusy(true); setMessage(''); setError(false);
        try { await requestTrackingLink(orderNumber, email); setMessage('If the order number and email match our records, a secure tracking link has been sent.'); }
        catch { setError(true); }
        finally { setBusy(false); }
      }}>
        <label className="grid gap-1 text-sm">Order number<input required maxLength={50} value={orderNumber} disabled={busy} onChange={e => setOrderNumber(e.target.value)} className="min-w-0 rounded-lg border border-[#EDE4D0] p-3" /></label>
        <label className="grid gap-1 text-sm">Checkout email<input required type="email" maxLength={255} autoComplete="email" value={email} disabled={busy} onChange={e => setEmail(e.target.value)} className="min-w-0 rounded-lg border border-[#EDE4D0] p-3" /></label>
        <button disabled={busy} className="rounded-full bg-[#C4622D] px-5 py-3 text-white disabled:opacity-50">{busy ? 'Requesting…' : 'Email tracking link'}</button>
        {message && <p role="status" className="text-sm">{message}</p>}
        {error && <p role="alert" className="text-sm">We could not request a link right now. Please wait and try again.</p>}
      </form>
    </section>
  </div></div>;
}
