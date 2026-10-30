import AuthDialogFrame, { AuthDialogHeader } from './AuthDialogFrame';
import { useEffect, useState } from 'react';
import { FacebookIcon, GoogleIcon } from './Icons';
import { authApi, type User } from '../lib/api/auth';

type GooglePromptNotification = {
  isNotDisplayed?: () => boolean;
  isSkippedMoment?: () => boolean;
};

type GoogleTokenResponse = {
  access_token?: string;
  error?: string;
};

type GoogleIdentityApi = {
  accounts: {
    id?: {
      initialize: (options: { client_id: string; callback: (response: { credential: string }) => void }) => void;
      prompt: (momentListener?: (notification: GooglePromptNotification) => void) => void;
    };
    oauth2?: {
      initTokenClient: (options: {
        client_id: string;
        scope: string;
        callback: (response: GoogleTokenResponse) => void;
        error_callback?: (error: { type?: string; message?: string }) => void;
      }) => { requestAccessToken: (overrideConfig?: { prompt?: string }) => void };
    };
  };
};

const ensureGoogleScript = (onLoad?: () => void, onError?: () => void) => {
  if ((window as unknown as { google?: GoogleIdentityApi }).google) {
    onLoad?.();
    return;
  }
  const existing = document.querySelector<HTMLScriptElement>('script[src="https://accounts.google.com/gsi/client"]');
  if (existing) {
    if (onLoad) existing.addEventListener('load', onLoad, { once: true });
    if (onError) existing.addEventListener('error', () => onError(), { once: true });
    return;
  }
  const script = document.createElement('script');
  script.src = 'https://accounts.google.com/gsi/client';
  script.async = true;
  if (onLoad) script.onload = onLoad;
  if (onError) script.onerror = () => onError();
  document.head.appendChild(script);
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
  const [runtimeGoogleClientId, setRuntimeGoogleClientId] = useState<string>('');
  const [runtimeFacebookAppId, setRuntimeFacebookAppId] = useState<string>('');
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || runtimeGoogleClientId;
  const facebookAppId = import.meta.env.VITE_FACEBOOK_APP_ID || runtimeFacebookAppId;

  useEffect(() => {
    if (open) {
      setEmail('');
      setSentEmail('');
      setDevMagicLink('');
      setError(initialError);
      if (googleClientId) {
        ensureGoogleScript();
      } else {
        authApi
          .config()
          .then((cfg) => {
            if (cfg.googleClientId) {
              setRuntimeGoogleClientId(cfg.googleClientId);
              ensureGoogleScript();
            }
            if (cfg.facebookAppId) {
              setRuntimeFacebookAppId(cfg.facebookAppId);
            }
          })
          .catch(() => {
            // Keep default unconfigured fallback if runtime config endpoint is unreachable.
          });
      }
    }
  }, [googleClientId, initialError, open]);

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
    setError('');
    const openPrompt = () => {
      const google = (window as unknown as { google?: GoogleIdentityApi }).google;
      if (!google?.accounts) return setError('Google sign-in could not load. Check your connection and try again.');
      if (google.accounts.oauth2?.initTokenClient) {
        const tokenClient = google.accounts.oauth2.initTokenClient({
          client_id: googleClientId,
          scope: 'openid email profile',
          callback: (response) => {
            if (response.access_token) {
              void completeGoogleSignIn(response.access_token);
            } else if (response.error) {
              setError('Google sign-in was cancelled or could not be completed.');
            }
          },
          error_callback: () => {
            setError('Google sign-in was cancelled or could not be completed.');
          },
        });
        tokenClient.requestAccessToken({ prompt: 'select_account' });
        return;
      }
      if (google.accounts.id) {
        google.accounts.id.initialize({
          client_id: googleClientId,
          callback: (response) => void completeGoogleSignIn(response.credential),
        });
        google.accounts.id.prompt((notification) => {
          if (notification?.isNotDisplayed?.() || notification?.isSkippedMoment?.()) {
            setError('Google sign-in prompt was suppressed by the browser. Please allow popups or third-party sign-in and try again.');
          }
        });
        return;
      }
      setError('Google sign-in could not load. Check your connection and try again.');
    };
    ensureGoogleScript(
      openPrompt,
      () => setError('Google sign-in could not load. Check your connection and try again.'),
    );
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
    <AuthDialogFrame onClose={onClose}>
      <AuthDialogHeader onClose={onClose} sent={Boolean(sentEmail)} />
        <div className="auth-dialog-body px-7 py-6">
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
    </AuthDialogFrame>
  );
}
