import { useEffect, useState } from 'react';
import { LoadingState } from '../components/StorefrontState';
import { getAdminAnalytics } from '../lib/api/admin';
import AdminApp from '../admin/AdminApp';

interface Props {
  onSignIn: () => void;
  onExitAdmin: () => void;
}

type GateState = 'loading' | 'allowed' | 'forbidden' | 'error';

export default function AdminPage({ onSignIn, onExitAdmin }: Props) {
  const [state, setState] = useState<GateState>('loading');
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let active = true;
    getAdminAnalytics().then(() => {
      if (active) setState('allowed');
    }).catch(error => {
      if (!active) return;
      setState(error instanceof Error && /401|403/.test(error.message) ? 'forbidden' : 'error');
    });
    return () => { active = false; };
  }, [retry]);

  if (state === 'loading') return <main className="min-h-screen bg-[#F8F4EF] px-4 pt-16"><LoadingState label="Loading Sulocraft admin…" /></main>;
  if (state === 'forbidden') return <main className="grid min-h-[80vh] place-items-center bg-[#F8F4EF] px-4"><div className="max-w-md text-center"><span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-[#C4622D] font-serif text-2xl text-white">S</span><h1 className="mt-5 font-serif text-3xl text-[#2C1810]">Admin access required</h1><p className="mt-2 text-sm leading-6 text-[#806F61]">Sign in with an administrator account to manage the Sulocraft store.</p><button onClick={onSignIn} className="mt-6 rounded-xl bg-[#C4622D] px-6 py-3 text-sm font-semibold text-white hover:bg-[#A9502A]">Sign in to admin</button></div></main>;
  if (state === 'error') return <main className="grid min-h-[80vh] place-items-center bg-[#F8F4EF] px-4"><div className="text-center"><h1 className="font-serif text-2xl text-[#2C1810]">Admin workspace unavailable</h1><p className="mt-2 text-sm text-[#806F61]">The Sulocraft dashboard could not be loaded from the API.</p><button onClick={() => setRetry(value => value + 1)} className="mt-5 rounded-xl bg-[#C4622D] px-5 py-2.5 text-sm font-semibold text-white">Try again</button></div></main>;
  return <AdminApp onExitAdmin={onExitAdmin} />;
}
