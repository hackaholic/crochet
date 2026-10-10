import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import OrderTrackingPanel from './OrderTrackingPanel';
import { getOrderTracking } from '../../lib/api/tracking';
vi.mock('../../lib/api/tracking', () => ({ getOrderTracking: vi.fn() }));
const data = { orderNumber: 'TEST-1', status: 'SHIPPED', paymentStatus: 'PAID', courierName: null, trackingNumber: 'TRACK-1', estimatedDelivery: null, timeline: [] };
afterEach(() => { cleanup(); vi.resetAllMocks(); });
it('loads the exact order and handles absent shipment fields', async () => {
  vi.mocked(getOrderTracking).mockResolvedValue(data);
  render(<OrderTrackingPanel orderNumber="TEST-1" />);
  expect(await screen.findByText('TRACK-1')).toBeVisible();
  expect(getOrderTracking).toHaveBeenCalledWith('TEST-1', expect.any(AbortSignal), undefined);
});
it('clears private data on denied access and supports retry', async () => {
  vi.mocked(getOrderTracking).mockRejectedValueOnce(new Error('404')).mockResolvedValue(data);
  render(<OrderTrackingPanel orderNumber="TEST-1" />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Tracking is unavailable');
  expect(screen.queryByText('TRACK-1')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
  expect(await screen.findByText('TRACK-1')).toBeVisible();
});
it('aborts old requests and ignores a late previous order response', async () => {
  let resolve!: (value: typeof data) => void;
  vi.mocked(getOrderTracking).mockReturnValueOnce(new Promise(r => { resolve = r; })).mockResolvedValueOnce({ ...data, orderNumber: 'TEST-2', trackingNumber: 'TRACK-2' });
  const view = render(<OrderTrackingPanel orderNumber="TEST-1" />);
  const signal = vi.mocked(getOrderTracking).mock.calls[0][1];
  view.rerender(<OrderTrackingPanel orderNumber="TEST-2" />);
  expect(await screen.findByText('TRACK-2')).toBeVisible();
  expect(signal.aborted).toBe(true);
  resolve(data);
  expect(screen.queryByText('TRACK-1')).not.toBeInTheDocument();
});
