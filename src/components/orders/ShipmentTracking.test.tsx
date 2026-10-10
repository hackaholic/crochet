import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import ShipmentTracking from './ShipmentTracking';
import type { OrderTracking } from '../../lib/api/orderTrackingTypes';

afterEach(cleanup);
const tracking: OrderTracking = {
  orderNumber: 'TEST-001', status: 'SHIPPED', paymentStatus: 'PAID',
  courierName: 'Test carrier', trackingNumber: 'TRACK-001', estimatedDelivery: '2026-10-15',
  timeline: [{ id: 1, status: 'SHIPPED', note: 'Parcel handed to courier', timestamp: '2026-10-10T10:00:00Z' }],
};
it('renders persisted shipment fields and semantic timeline times', () => {
  const { container } = render(<ShipmentTracking tracking={tracking} />);
  expect(screen.getByRole('heading', { name: 'Shipment details' })).toBeVisible();
  expect(screen.getByText('Test carrier')).toBeVisible();
  expect(screen.getByText('TRACK-001')).toBeVisible();
  expect(screen.getByText('Parcel handed to courier')).toBeVisible();
  expect(container.querySelector('time[datetime="2026-10-15"]')).not.toBeNull();
  expect(container.querySelectorAll('ol li')).toHaveLength(1);
});
it('shows absent shipment and empty timeline honestly', () => {
  render(<ShipmentTracking tracking={{ ...tracking, courierName: null, trackingNumber: null, estimatedDelivery: null, timeline: [] }} />);
  expect(screen.getAllByText('Not yet available')).toHaveLength(3);
  expect(screen.getByText('No order updates yet.')).toBeVisible();
  expect(screen.queryByText('Test carrier')).not.toBeInTheDocument();
});
it('handles invalid dates without displaying Invalid Date', () => {
  const { container } = render(<ShipmentTracking tracking={{ ...tracking, estimatedDelivery: 'invalid', timeline: [{ ...tracking.timeline[0], timestamp: 'invalid' }] }} />);
  expect(screen.getByText('Time not recorded')).toBeVisible();
  expect(container.querySelector('time')).toBeNull();
  expect(screen.queryByText(/Invalid Date/)).not.toBeInTheDocument();
});
it('escapes untrusted API strings and never constructs carrier links', () => {
  const note = '<img src=x onerror=alert(1)>';
  const { container } = render(<ShipmentTracking tracking={{ ...tracking, trackingNumber: 'javascript:alert(1)', timeline: [{ ...tracking.timeline[0], note }] }} />);
  expect(screen.getByText(note)).toBeVisible();
  expect(screen.getByText('javascript:alert(1)')).toBeVisible();
  expect(container.querySelector('img,script,a')).toBeNull();
});
it('does not retain previous order data when the selected payload changes', () => {
  const view = render(<ShipmentTracking tracking={tracking} />);
  view.rerender(<ShipmentTracking tracking={{ ...tracking, orderNumber: 'TEST-002', trackingNumber: null, courierName: null, timeline: [] }} />);
  expect(screen.getByText('Order TEST-002')).toBeVisible();
  expect(screen.queryByText('TRACK-001')).not.toBeInTheDocument();
  expect(screen.queryByText('Parcel handed to courier')).not.toBeInTheDocument();
});
it('constrains wrapping of long untrusted identifiers', () => {
  render(<ShipmentTracking tracking={{ ...tracking, trackingNumber: 'X'.repeat(500) }} />);
  expect(screen.getByRole('region', { name: 'Shipment tracking' })).toHaveClass('min-w-0', '[overflow-wrap:anywhere]');
  expect(screen.getByText('X'.repeat(500))).toBeInTheDocument();
});
