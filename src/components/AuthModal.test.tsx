import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import AuthModal from './AuthModal';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('AuthModal', () => {
  it('offers global social and passwordless email sign-in in an accessible popup', () => {
    render(<AuthModal open onClose={vi.fn()} onSignedIn={vi.fn()} />);

    expect(screen.getByRole('dialog', { name: /welcome to sulocraft/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /continue with google/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /continue with facebook/i })).toBeInTheDocument();

    expect(screen.queryByText(/continue with phone/i)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /continue with email/i })).toBeDisabled();
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'customer@example.com' } });
    expect(screen.getByRole('button', { name: /continue with email/i })).toBeEnabled();
  });

  it('does not silently replace real social login with mock identities when client IDs are blank', () => {
    vi.stubEnv('VITE_GOOGLE_CLIENT_ID', '');
    vi.stubEnv('VITE_FACEBOOK_APP_ID', '');
    render(<AuthModal open onClose={vi.fn()} onSignedIn={vi.fn()} />);

    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }));
    expect(screen.getByText(/google sign-in is not configured/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /continue with facebook/i }));
    expect(screen.getByText(/facebook sign-in is not configured/i)).toBeInTheDocument();
  });

  it('opens the Google account chooser popup via oauth2.initTokenClient when VITE_GOOGLE_CLIENT_ID is configured', async () => {
    vi.stubEnv('VITE_GOOGLE_CLIENT_ID', 'test-google-client-id.apps.googleusercontent.com');
    const requestAccessToken = vi.fn();
    const initTokenClient = vi.fn().mockImplementation(({ callback }) => ({
      requestAccessToken: (opts?: { prompt?: string }) => {
        requestAccessToken(opts);
        callback({ access_token: 'google-oauth-access-token' });
      },
    }));
    vi.stubGlobal('google', {
      accounts: {
        oauth2: { initTokenClient },
      },
    });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user: { id: 7, email: 'googleuser@example.com', fullName: 'Google User', role: 'CUSTOMER', identities: ['google'] },
        cartMerged: false,
      }),
    });
    vi.stubGlobal('fetch', fetchMock);
    const onSignedIn = vi.fn();
    const onClose = vi.fn();

    render(<AuthModal open onClose={onClose} onSignedIn={onSignedIn} />);
    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }));

    expect(initTokenClient).toHaveBeenCalledWith(
      expect.objectContaining({
        client_id: 'test-google-client-id.apps.googleusercontent.com',
        scope: 'openid email profile',
      }),
    );
    expect(requestAccessToken).toHaveBeenCalledWith({ prompt: 'select_account' });
    await waitFor(() => expect(onSignedIn).toHaveBeenCalledWith(expect.objectContaining({ email: 'googleuser@example.com' })));
    expect(onClose).toHaveBeenCalled();
  });

  it('resolves googleClientId at runtime from /api/v1/auth/config when build-time env is empty', async () => {
    vi.stubEnv('VITE_GOOGLE_CLIENT_ID', '');
    const requestAccessToken = vi.fn();
    const initTokenClient = vi.fn().mockImplementation(() => ({
      requestAccessToken,
    }));
    vi.stubGlobal('google', {
      accounts: {
        oauth2: { initTokenClient },
      },
    });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        googleClientId: 'sops-runtime-client-id.apps.googleusercontent.com',
        facebookAppId: null,
      }),
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<AuthModal open onClose={vi.fn()} onSignedIn={vi.fn()} />);

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringMatching(/\/auth\/config$/),
        expect.any(Object),
      ),
    );
    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }));

    expect(initTokenClient).toHaveBeenCalledWith(
      expect.objectContaining({
        client_id: 'sops-runtime-client-id.apps.googleusercontent.com',
      }),
    );
    expect(requestAccessToken).toHaveBeenCalledWith({ prompt: 'select_account' });
  });

  it('starts email magic-link login and shows the generic confirmation state', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'If the email address is valid, a sign-in link has been sent.', devMagicLink: 'http://localhost:8000/api/v1/auth/email/verify?token=local-token' }),
    });
    vi.stubGlobal('fetch', fetchMock);
    render(<AuthModal open onClose={vi.fn()} onSignedIn={vi.fn()} />);

    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'customer@example.com' } });
    fireEvent.click(screen.getByRole('button', { name: /continue with email/i }));

    await waitFor(() => expect(screen.getByRole('heading', { name: /check your email/i })).toBeInTheDocument());
    expect(screen.getByText('customer@example.com')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /open local sign-in link/i })).toHaveAttribute('href', expect.stringContaining('returnTo='));
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/email\/start$/),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ email: 'customer@example.com' }) }),
    );
  });

  it('shows a generic invalid-link message without exposing token details', () => {
    render(<AuthModal open initialError="That sign-in link is invalid, expired, or has already been used. Request a new link below." onClose={vi.fn()} onSignedIn={vi.fn()} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/invalid, expired, or has already been used/i);
  });
});
