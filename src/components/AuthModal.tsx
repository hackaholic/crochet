import { useEffect, useState } from 'react';
import { FacebookIcon, GoogleIcon, XIcon, YarnLogo } from './Icons';
import { authApi, type User } from '../lib/api/auth';

type GoogleIdentityApi = {
  accounts: {
    id: {
      initialize: (options: { client_id: string; callback: (response: { credential: string }) => void }) => void;
      prompt: () => void;
    };
  };
};

type FacebookSdkApi = {
  init: (options: { appId: string; cookie?: boolean; xfbml?: boolean; version: string }) => void;
  login: (
    callback: (response: { authResponse?: { accessToken: string; userID: string } }) => void,
    options?: { scope: string },
  ) => void;
};

export default function AuthModal({
  open,
  onClose,
  onSignedIn,
}: {
  open: boolean;
  onClose: () => void;
  onSignedIn: (user: User) => void;
}) {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [hint, setHint] = useState('');

  useEffect(() => {
    if (open) {
      setOtp('');
      setSent(false);
      setError('');
      setHint('');
    }
  }, [open]);

  if (!open) return null;

  const send = async () => {
    setBusy(true);
    setError('');
    try {
      const response = await authApi.sendOtp(phone);
      setHint(response.devOtp ? `Local development code: ${response.devOtp}` : 'We sent a code to your phone.');
      setSent(true);
    } catch {
      setError('We could not send a code. Check the phone number and try again.');
    } finally {
      setBusy(false);
    }
  };

  const verify = async () => {
    setBusy(true);
    setError('');
    try {
      const response = await authApi.verifyOtp(phone, otp);
      onSignedIn(response.user);
      onClose();
    } catch {
      setError('That code could not be verified. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const facebookAppId = import.meta.env.VITE_FACEBOOK_APP_ID;

  const completeGoogleSignIn = async (credential: string) => {
    setBusy(true);
    setError('');
    try {
      const response = await authApi.google(credential);
      onSignedIn(response.user);
      onClose();
    } catch {
      setError('Google sign-in could not be completed. Please try again or use your phone number.');
    } finally {
      setBusy(false);
    }
  };

  const signInWithGoogle = () => {
    if (!googleClientId) {
      completeGoogleSignIn('mock_google_dev_token');
      return;
    }
    const openGooglePrompt = () => {
      const google = (window as unknown as { google?: GoogleIdentityApi }).google;
      if (!google) {
        completeGoogleSignIn('mock_google_dev_token');
        return;
      }
      google.accounts.id.initialize({
        client_id: googleClientId,
        callback: (res) => completeGoogleSignIn(res.credential),
      });
      google.accounts.id.prompt();
    };

    if ((window as unknown as { google?: GoogleIdentityApi }).google) {
      openGooglePrompt();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.onload = openGooglePrompt;
    script.onerror = () => completeGoogleSignIn('mock_google_dev_token');
    document.head.appendChild(script);
  };

  const completeFacebookSignIn = async (accessToken: string, userId?: string) => {
    setBusy(true);
    setError('');
    try {
      const response = await authApi.facebook({
        accessToken,
        userId,
        email: 'guest.facebook@example.com',
        name: 'Facebook User',
      });
      onSignedIn(response.user);
      onClose();
    } catch {
      setError('Facebook sign-in could not be completed. Please try again or use your phone number.');
    } finally {
      setBusy(false);
    }
  };

  const signInWithFacebook = () => {
    if (!facebookAppId) {
      completeFacebookSignIn('mock_fb_dev_token', 'fb_dev_user');
      return;
    }
    const openFacebookLogin = () => {
      const fb = (window as unknown as { FB?: FacebookSdkApi }).FB;
      if (!fb) {
        completeFacebookSignIn('mock_fb_dev_token', 'fb_dev_user');
        return;
      }
      fb.login(
        (response) => {
          if (response.authResponse?.accessToken) {
            completeFacebookSignIn(response.authResponse.accessToken, response.authResponse.userID);
          } else {
            setError('Facebook sign-in was cancelled or not authorized.');
          }
        },
        { scope: 'public_profile,email' },
      );
    };

    if ((window as unknown as { FB?: FacebookSdkApi }).FB) {
      openFacebookLogin();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://connect.facebook.net/en_US/sdk.js';
    script.async = true;
    script.onload = () => {
      const fb = (window as unknown as { FB?: FacebookSdkApi }).FB;
      if (fb) {
        fb.init({ appId: facebookAppId, cookie: true, xfbml: true, version: 'v20.0' });
        openFacebookLogin();
      }
    };
    script.onerror = () => completeFacebookSignIn('mock_fb_dev_token', 'fb_dev_user');
    document.head.appendChild(script);
  };

  return (
    <div className="fixed inset-0 z-[90] flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="sign-in-title">
      <button className="absolute inset-0 bg-[#2C1810]/55 backdrop-blur-sm" onClick={onClose} aria-label="Close sign in" />
      <section className="relative w-full max-w-md overflow-hidden rounded-[2rem] bg-white shadow-2xl">
        <div className="bg-[#FAF7F2] px-7 pb-6 pt-7 text-center">
          <button onClick={onClose} className="absolute right-5 top-5 rounded-full p-1.5 text-[#8B6B4A] hover:bg-[#F5EDE0]" aria-label="Close sign in">
            <XIcon size={20} />
          </button>
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm">
            <YarnLogo size={32} />
          </div>
          <h2 id="sign-in-title" className="mt-4 text-3xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
            {sent ? 'Check your phone' : 'Welcome to Sulocraft'}
          </h2>
          <p className="mt-2 text-sm leading-6 text-[#8B6B4A]">
            {sent ? 'Enter the six-digit code we sent to continue.' : 'Sign in to save your favourites, addresses, and orders.'}
          </p>
        </div>

        <div className="px-7 py-6">
          {!sent ? (
            <>
              <label htmlFor="phone" className="mb-2 block text-sm font-semibold text-[#3F2A20]">
                Mobile number
              </label>
              <div className="flex rounded-xl border border-[#D9C9B8] bg-[#FFFCF8] focus-within:border-[#C4622D] focus-within:ring-2 focus-within:ring-[#C4622D]/20">
                <span className="select-none border-r border-[#EDE4D0] px-4 py-3.5 text-sm font-medium text-[#5C3D2E]">+91</span>
                <input
                  id="phone"
                  value={phone}
                  onChange={(event) => setPhone(event.target.value.replace(/\D/g, '').slice(-10))}
                  placeholder="98765 43210"
                  inputMode="tel"
                  autoComplete="tel"
                  className="min-w-0 flex-1 bg-transparent px-4 py-3.5 text-[#2C1810] outline-none"
                />
              </div>

              <button
                disabled={busy || phone.length !== 10}
                onClick={send}
                className="mt-5 w-full rounded-full bg-[#C4622D] py-3.5 font-semibold text-white transition-colors hover:bg-[#AA4F20] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {busy ? 'Sending code…' : 'Continue with phone'}
              </button>

              <div className="my-5 flex items-center gap-3 text-xs text-[#8B6B4A]">
                <span className="h-px flex-1 bg-[#EDE4D0]" />
                or continue with
                <span className="h-px flex-1 bg-[#EDE4D0]" />
              </div>

              <div className="flex flex-col gap-2.5">
                <button
                  type="button"
                  disabled={busy}
                  onClick={signInWithGoogle}
                  className="flex w-full items-center justify-center gap-3 rounded-full border border-[#D9C9B8] bg-white py-3 text-sm font-semibold text-[#2C1810] shadow-sm transition-all hover:bg-[#FAF7F2] hover:border-[#8B6B4A] disabled:opacity-50"
                >
                  <GoogleIcon size={18} />
                  <span>Continue with Google</span>
                </button>

                <button
                  type="button"
                  disabled={busy}
                  onClick={signInWithFacebook}
                  className="flex w-full items-center justify-center gap-3 rounded-full border border-[#1877F2]/30 bg-[#1877F2]/5 py-3 text-sm font-semibold text-[#1877F2] transition-all hover:bg-[#1877F2]/10 hover:border-[#1877F2]/50 disabled:opacity-50"
                >
                  <FacebookIcon size={18} />
                  <span>Continue with Facebook</span>
                </button>
              </div>

              <p className="mt-5 text-center text-xs leading-5 text-[#8B6B4A]">
                New here? Verifying your number creates your Sulocraft account.
              </p>
            </>
          ) : (
            <>
              <label htmlFor="otp" className="mb-2 block text-sm font-semibold text-[#3F2A20]">
                One-time password
              </label>
              <input
                id="otp"
                value={otp}
                onChange={(event) => setOtp(event.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="123456"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                className="w-full rounded-xl border border-[#D9C9B8] bg-[#FFFCF8] px-4 py-3.5 text-center text-xl tracking-[0.35em] text-[#2C1810] outline-none focus:border-[#C4622D] focus:ring-2 focus:ring-[#C4622D]/20"
              />
              <p className="mt-3 text-sm text-[#5C7A5A]">{hint}</p>
              <button
                disabled={busy || otp.length !== 6}
                onClick={verify}
                className="mt-5 w-full rounded-full bg-[#C4622D] py-3.5 font-semibold text-white transition-colors hover:bg-[#AA4F20] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {busy ? 'Verifying…' : 'Verify and sign in'}
              </button>
              <button
                onClick={() => {
                  setSent(false);
                  setOtp('');
                  setHint('');
                }}
                className="mt-4 w-full text-sm font-semibold text-[#8B6B4A] hover:text-[#C4622D]"
              >
                Use a different number
              </button>
            </>
          )}

          {error && (
            <p className="mt-4 text-sm text-[#B54A2A]" role="alert">
              {error}
            </p>
          )}

          <p className="mt-6 text-center text-xs leading-5 text-[#8B6B4A]">
            By continuing, you agree to our Terms of Use and Privacy Policy.
          </p>
        </div>
      </section>
    </div>
  );
}

