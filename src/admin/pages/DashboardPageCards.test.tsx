import { describe, it, expect, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import { MetricCard } from '../components/AdminShared';

describe('Admin KPI MetricCard styling and hover', () => {
  afterEach(() => {
    cleanup();
  });

  it('renders semantic background, border classes and hover micro-interaction', () => {
    const { container } = render(
      <MetricCard
        label="Total Sales"
        value="₹1,200"
        icon="₹"
        accent="#C4622D"
        bgClass="bg-[#FDF9F6]"
        borderClass="border-[#EADCCF]"
      />
    );
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('bg-[#FDF9F6]');
    expect(card).toHaveClass('border-[#EADCCF]');
    expect(card).toHaveClass('hover:shadow-md');
    expect(card).toHaveClass('hover:-translate-y-0.5');
  });

  it('renders all semantic cards properly with custom accents', () => {
    const { container } = render(
      <div>
        <MetricCard label="Net Revenue" value="₹1,000" icon="💰" accent="#3F6E50" bgClass="bg-[#F6FAF6]" borderClass="border-[#D2E2D5]" />
        <MetricCard label="Orders" value="12" icon="📋" accent="#2B5C8F" bgClass="bg-[#F6F9FD]" borderClass="border-[#D4E2F0]" />
        <MetricCard label="Average Order Value" value="₹100" icon="📊" accent="#7A6B5D" bgClass="bg-[#FBF9F6]" borderClass="border-[#E8E0D8]" />
        <MetricCard label="Refunds" value="₹200" icon="↩" accent="#B84545" bgClass="bg-[#FDF6F6]" borderClass="border-[#F0D5D5]" />
      </div>
    );
    expect(screen.getByText('Net Revenue')).toBeInTheDocument();
    expect(screen.getByText('Orders')).toBeInTheDocument();
    expect(screen.getByText('Average Order Value')).toBeInTheDocument();
    expect(screen.getByText('Refunds')).toBeInTheDocument();
  });
});
