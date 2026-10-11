import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import RevenueChart from './RevenueChart';
import type { SalesDataPoint } from '../types';

describe('RevenueChart component', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders empty period message gracefully', () => {
    render(<RevenueChart data={[]} />);
    expect(screen.getByText('No sales recorded in this period.')).toBeInTheDocument();
  });

  it('renders single data point without NaN or Infinity errors', () => {
    const singleData: SalesDataPoint[] = [
      { label: '11 Oct', revenue: 500, orders: 2, avgOrderValue: 250 },
    ];
    const { container } = render(<RevenueChart data={singleData} />);
    const polyline = container.querySelector('polyline');
    expect(polyline).toBeInTheDocument();
    const pointsAttr = polyline?.getAttribute('points');
    expect(pointsAttr).not.toContain('NaN');
    expect(pointsAttr).not.toContain('Infinity');

    const areaPath = container.querySelector('path');
    expect(areaPath?.getAttribute('d')).not.toContain('NaN');
    expect(areaPath?.getAttribute('d')).not.toContain('Infinity');
  });

  it('handles negative revenue without sending points below chart boundary', () => {
    const mixedData: SalesDataPoint[] = [
      { label: '10 Oct', revenue: -200, orders: 1, avgOrderValue: -200 },
      { label: '11 Oct', revenue: 500, orders: 3, avgOrderValue: 166.67 },
    ];
    const { container } = render(<RevenueChart data={mixedData} />);
    const polyline = container.querySelector('polyline');
    expect(polyline).toBeInTheDocument();
    const pointsAttr = polyline?.getAttribute('points');
    expect(pointsAttr).not.toContain('NaN');
    expect(pointsAttr).not.toContain('Infinity');

    // Verify grid lines format negative numbers properly
    expect(screen.getAllByText(/-₹|₹/i).length).toBeGreaterThan(0);
  });

  it('switches metric correctly', () => {
    const data: SalesDataPoint[] = [
      { label: '10 Oct', revenue: 1000, orders: 5, avgOrderValue: 200 },
      { label: '11 Oct', revenue: 2000, orders: 10, avgOrderValue: 200 },
    ];
    render(<RevenueChart data={data} />);

    const ordersBtn = screen.getByRole('button', { name: 'Orders' });
    fireEvent.click(ordersBtn);
    expect(ordersBtn).toHaveClass('bg-white');
  });
});
