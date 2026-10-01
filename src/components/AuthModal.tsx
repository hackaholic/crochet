import { useEffect, useState } from 'react';
import { FacebookIcon, GoogleIcon, XIcon, YarnLogo } from './Icons';
import { authApi, type User } from '../lib/api/auth';

type GoogleIdentityApi = {
  accounts: { id: { initialize: (options: { client_id: string; callback: (response: { credential: string }) => void }) => void; prompt: () => void } };
};

type FacebookSdkApi = {
  init: (options: { appId: string; cookie?: boolean; xfbml?: boolean; version: string }) => void;
  login: (callback: (response: { authResponse?: { accessToken: string; userID: string } }) => void, options?: { scope: string }) => void;
};

export default function AuthModal({ open, onClose, onSignedIn, initialError = '' }: { open: boolean; onClose: () => void; onSignedIn: (user: User) => void; initialError?: string }) {
  const [email, setEmail] = useState('');
  const [sentEmail, setSentEmail] = useState('');
  const [devMagicLink, setDevMagicLink] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const facebookAppId = import.meta.env.VITE_FACEBOOK_APP_ID;

  useEffect(() => {
    if (open) {
      setEmail('');
      setSentEmail('');
      setDevMagicLink('');
      setError(initialError);
    }
  }, [initialError, open]);

  if (!open) return null;

  const completeGoogleSignIn = async (credential: string) => {
    setBusy(true);
    setError('');
    try {
      const response = await authApi.google(credential);
      onSignedIn(response.user);
      onClose();
    } catch {
      setError('Google sign-in could not be completed. Please try again or use email.');
    } finally {
      setBusy(false);
    }
  };

  const signInWithGoogle = () => {
    if (!googleClientId) {
      setError('Google sign-in is not configured for this environment yet. Add VITE_GOOGLE_CLIENT_ID and register this site origin in Google Cloud.');
      return;
    }
    const openPrompt = () => {
      const google = (window as unknown as { google?: GoogleIdentityApi }).google;
      if (!google) return setError('Google sign-in could not load. Check your connection and try again.');
      google.accounts.id.initialize({ client_id: googleClientId, callback: (response) => completeGoogleSignIn(response.credential) });
      google.accounts.id.prompt();
    };
    if ((window as unknown as { google?: GoogleIdentityApi }).google) return openPrompt();
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.onload = openPrompt;
    script.onerror = () => setError('Google sign-in could not load. Check your connection and try again.');
    document.head.appendChild(script);
  };

  const completeFacebookSignIn = async (accessToken: string, userId?: string) => {
    setBusy(true);
    setError('');
    try {
      const response = await authApi.facebook({ accessToken, userId });
      onSignedIn(response.user);
      onClose();
    } catch {
      setError('Facebook sign-in could not be completed. Please try again or use email.');
    } finally {
      setBusy(false);
    }
  };

  const signInWithFacebook = () => {
    if (!facebookAppId) {
      setError('Facebook sign-in is not configured for this environment yet. Add VITE_FACEBOOK_APP_ID and register this site domain in Meta for Developers.');
      return;
    }
    const openLogin = () => {
      const facebook = (window as unknown as { FB?: FacebookSdkApi }).FB;
      if (!facebook) return setError('Facebook sign-in could not load. Check your connection and try again.');
      facebook.login((response) => {
        if (response.authResponse?.accessToken) completeFacebookSignIn(response.authResponse.accessToken, response.authResponse.userID);
        else setError('Facebook sign-in was cancelled or not authorized.');
      }, { scope: 'public_profile,email' });
    };
    if ((window as unknown as { FB?: FacebookSdkApi }).FB) return openLogin();
    const script = document.createElement('script');
    script.src = 'https://connect.facebook.net/en_US/sdk.js';
    script.async = true;
    script.onload = () => {
      const facebook = (window as unknown as { FB?: FacebookSdkApi }).FB;
      if (facebook) {
        facebook.init({ appId: facebookAppId, cookie: true, xfbml: true, version: 'v20.0' });
        openLogin();
      }
    };
    script.onerror = () => setError('Facebook sign-in could not load. Check your connection and try again.');
    document.head.appendChild(script);
  };

  const sendMagicLink = async () => {
    setBusy(true);
    setError('');
    try {
      const response = await authApi.startEmail(email.trim());
      setSentEmail(email.trim());
      if (response.devMagicLink) {
        const returnTo = window.location.pathname.startsWith('/') ? window.location.pathname : '/';
        const separator = response.devMagicLink.includes('?') ? '&' : '?';
        setDevMagicLink(`${response.devMagicLink}${separator}returnTo=${encodeURIComponent(returnTo)}`);
      }
    } catch {
      setError('We could not send the sign-in link. Check the email address and try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[90] flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="sign-in-title">
      <button className="absolute inset-0 bg-[#2C1810]/55 backdrop-blur-sm" onClick={onClose} aria-label="Close sign in" />
      <section className="relative w-full max-w-md overflow-hidden rounded-[2rem] bg-white shadow-2xl">
        <div className="bg-[#FAF7F2] px-7 pb-6 pt-7 text-center">
          <button onClick={onClose} className="absolute right-5 top-5 rounded-full p-1.5 text-[#8B6B4A] hover:bg-[#F5EDE0]" aria-label="Close sign in"><XIcon size={20} /></button>
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm"><YarnLogo size={32} /></div>
          <h2 id="sign-in-title" className="mt-4 text-3xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{sentEmail ? 'Check your email' : 'Welcome to Sulocraft'}</h2>
          <p className="mt-2 text-sm leading-6 text-[#8B6B4A]">{sentEmail ? 'Use the secure link we sent to continue.' : 'Sign in to save your favourites, addresses, and orders.'}</p>
        </div>
        <div className="px-7 py-6">
          {!sentEmail ? (
            <>
              <div className="flex flex-col gap-2.5">
                <button type="button" disabled={busy} onClick={signInWithGoogle} className="flex w-full items-center justify-center gap-3 rounded-full border border-[#D9C9B8] bg-white py-3 text-sm font-semibold text-[#2C1810] shadow-sm transition-all hover:border-[#8B6B4A] hover:bg-[#FAF7F2] disabled:opacity-50"><GoogleIcon size={18} /><span>Continue with Google</span></button>
                <button type="button" disabled={busy} onClick={signInWithFacebook} className="flex w-full items-center justify-center gap-3 rounded-full border border-[#1877F2]/30 bg-[#1877F2]/5 py-3 text-sm font-semibold text-[#1877F2] transition-all hover:border-[#1877F2]/50 hover:bg-[#1877F2]/10 disabled:opacity-50"><FacebookIcon size={18} /><span>Continue with Facebook</span></button>
              </div>
              <div className="my-5 flex items-center gap-3 text-xs text-[#8B6B4A]"><span className="h-px flex-1 bg-[#EDE4D0]" />or<span className="h-px flex-1 bg-[#EDE4D0]" /></div>
              <label htmlFor="email" className="mb-2 block text-sm font-semibold text-[#3F2A20]">Email address</label>
              <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" autoComplete="email" className="w-full rounded-xl border border-[#D9C9B8] bg-[#FFFCF8] px-4 py-3.5 text-[#2C1810] outline-none focus:border-[#C4622D] focus:ring-2 focus:ring-[#C4622D]/20" />
              <button disabled={busy || !/^\S+@\S+\.\S+$/.test(email.trim())} onClick={sendMagicLink} className="mt-4 w-full rounded-full bg-[#C4622D] py-3.5 font-semibold text-white transition-colors hover:bg-[#AA4F20] disabled:cursor-not-allowed disabled:opacity-50">{busy ? 'Sending link…' : 'Continue with Email'}</button>
              <p className="mt-3 text-center text-xs leading-5 text-[#8B6B4A]">No password required. We’ll email you a secure sign-in link.</p>
            </>
          ) : (
            <>
              <div className="rounded-2xl bg-[#F5F8F1] px-5 py-4 text-center"><p className="text-sm text-[#5C3D2E]">We sent a secure sign-in link to:</p><p className="mt-1 break-all font-semibold text-[#2C1810]">{sentEmail}</p></div>
              {devMagicLink && <a href={devMagicLink} className="mt-4 block w-full rounded-full bg-[#5C7A5A] py-3.5 text-center text-sm font-semibold text-white transition-colors hover:bg-[#496747]">Open local sign-in link</a>}
              <button onClick={() => { setSentEmail(''); setError(''); }} className="mt-4 w-full text-sm font-semibold text-[#8B6B4A] hover:text-[#C4622D]">Use another email</button>
            </>
          )}
          {error && <p className="mt-4 text-sm text-[#B54A2A]" role="alert">{error}</p>}
          <p className="mt-6 text-center text-xs leading-5 text-[#8B6B4A]">By continuing, you agree to our Terms of Use and Privacy Policy.</p>
        </div>
      </section>
    </div>
  );
}
