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

  it('does not silently replace real social login with mock identities', () => {
    render(<AuthModal open onClose={vi.fn()} onSignedIn={vi.fn()} />);

    fireEvent.click(screen.getByRole('button', { name: /continue with google/i }));
    expect(screen.getByText(/google sign-in is not configured/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /continue with facebook/i }));
    expect(screen.getByText(/facebook sign-in is not configured/i)).toBeInTheDocument();
  });

  it('starts email magic-link login and shows the generic confirmation state', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'If the email address is valid, a sign-in link has been sent.' }),
    });
    vi.stubGlobal('fetch', fetchMock);
    render(<AuthModal open onClose={vi.fn()} onSignedIn={vi.fn()} />);

    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'customer@example.com' } });
    fireEvent.click(screen.getByRole('button', { name: /continue with email/i }));

    await waitFor(() => expect(screen.getByRole('heading', { name: /check your email/i })).toBeInTheDocument());
    expect(screen.getByText('customer@example.com')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/auth\/email\/start$/),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ email: 'customer@example.com' }) }),
    );
  });
});
