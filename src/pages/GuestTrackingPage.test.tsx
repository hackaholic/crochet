import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, useLocation } from 'react-router';
import { afterEach, expect, it, vi } from 'vitest';
import GuestTrackingPage from './GuestTrackingPage';
import { getOrderTracking, requestTrackingLink } from '../lib/api/tracking';
vi.mock('../lib/api/tracking', () => ({ getOrderTracking: vi.fn(), requestTrackingLink: vi.fn() }));
const tracking = { orderNumber: 'TEST-1', status: 'CONFIRMED', paymentStatus: 'PAID', courierName: null, trackingNumber: 'TRACK-1', estimatedDelivery: null, timeline: [] };
afterEach(() => { cleanup(); vi.resetAllMocks(); });
function Location() { const location = useLocation(); return <div data-testid="location">{location.pathname}{location.search}{location.hash}</div>; }
function setup(path: string) { return render(<MemoryRouter initialEntries={[path]}><GuestTrackingPage /><Location /></MemoryRouter>); }
it('opens a scoped fragment link without login and preserves fragment for refresh', async () => {
  vi.mocked(getOrderTracking).mockResolvedValue(tracking);
  setup('/track/TEST-1#token=test-credential');
  expect(await screen.findByText('TRACK-1')).toBeVisible();
  expect(getOrderTracking).toHaveBeenCalledWith('TEST-1', expect.any(AbortSignal), 'test-credential');
  expect(screen.getByTestId('location')).toHaveTextContent('#token=test-credential');
});
it('replaces legacy query credentials with fragment without storage writes', async () => {
  vi.mocked(getOrderTracking).mockResolvedValue(tracking);
  const storage = vi.spyOn(Storage.prototype, 'setItem');
  setup('/track/TEST-1?token=legacy-credential');
  await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/track/TEST-1#token=legacy-credential'));
  expect(screen.getByTestId('location').textContent).not.toContain('?token=');
  expect(storage).not.toHaveBeenCalled(); storage.mockRestore();
});
it('does not fetch guest details without a token and presents recovery', () => {
  setup('/track/TEST-1');
  expect(getOrderTracking).not.toHaveBeenCalled();
  expect(screen.getByRole('button', { name: 'Email tracking link' })).toBeVisible();
});
it('hides details for denied or expired token and keeps recovery available', async () => {
  vi.mocked(getOrderTracking).mockRejectedValue(new Error('404'));
  setup('/track/TEST-1#token=expired');
  expect(await screen.findByRole('alert')).toHaveTextContent('Tracking is unavailable');
  expect(screen.queryByText('TRACK-1')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Checkout email')).toBeVisible();
});
it('requests a link with a generic result and guards duplicate submits', async () => {
  let resolve!: () => void;
  vi.mocked(requestTrackingLink).mockReturnValue(new Promise(r => { resolve = r; }));
  setup('/track');
  fireEvent.change(screen.getByLabelText('Order number'), { target: { value: 'TEST-1' } });
  fireEvent.change(screen.getByLabelText('Checkout email'), { target: { value: 'guest@example.com' } });
  fireEvent.click(screen.getByRole('button', { name: 'Email tracking link' }));
  expect(screen.getByRole('button', { name: 'Requesting…' })).toBeDisabled();
  expect(requestTrackingLink).toHaveBeenCalledOnce();
  resolve();
  expect(await screen.findByRole('status')).toHaveTextContent('If the order number and email match');
});
it('retains form fields on network/rate-limit failure for retry', async () => {
  vi.mocked(requestTrackingLink).mockRejectedValueOnce(new Error('429')).mockResolvedValueOnce(undefined);
  setup('/track/TEST-1');
  fireEvent.change(screen.getByLabelText('Checkout email'), { target: { value: 'guest@example.com' } });
  fireEvent.click(screen.getByRole('button', { name: 'Email tracking link' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Please wait and try again');
  expect(screen.getByLabelText('Checkout email')).toHaveValue('guest@example.com');
  fireEvent.click(screen.getByRole('button', { name: 'Email tracking link' }));
  expect(await screen.findByRole('status')).toHaveTextContent('If the order number and email match');
});
