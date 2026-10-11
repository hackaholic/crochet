import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { StatusPipeline } from './DashboardPage';
afterEach(cleanup);
it('opens every exact pipeline/exception status including zero-count stages', () => {
  const select = vi.fn();
  render(<StatusPipeline counts={[{status:'SHIPPED',count:2}]} onSelect={select} />);
  const statuses = ['PENDING_PAYMENT','PAID','CONFIRMED','PROCESSING','READY_TO_SHIP','SHIPPED','OUT_FOR_DELIVERY','DELIVERED','CANCELLED','REFUNDED'];
  for (const status of statuses) {
    const button = screen.getByRole('button',{name:`View ${status.replaceAll('_',' ').toLowerCase()} orders`});
    expect(button).toHaveAttribute('type','button');
    expect(button).not.toBeDisabled();
    fireEvent.click(button);
    expect(select).toHaveBeenLastCalledWith(status);
  }
});
