import { useState } from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import PriceRangeFilter from './PriceRangeFilter';
import type { PriceBounds } from '../config/catalogue';

const bounds = { min: 0, max: 100000 };
function Harness() {
  const [value, setValue] = useState<PriceBounds>(bounds);
  return <PriceRangeFilter bounds={bounds} value={value} onChange={setValue} onReset={() => setValue(bounds)} active={value.min !== bounds.min || value.max !== bounds.max} />;
}
afterEach(cleanup);
const edit = (label: string, value: string) => {
  const input = screen.getByLabelText(label);
  fireEvent.change(input, { target: { value } });
  fireEvent.blur(input);
};
describe('native price range filter', () => {
  it('synchronizes both sliders and precise numeric fields, then resets', () => {
    render(<Harness />);
    expect(screen.getByRole('button', { name: 'Reset price' })).toBeDisabled();
    fireEvent.change(screen.getByRole('slider', { name: 'Maximum price slider' }), { target: { value: '2500' } });
    expect(screen.getByLabelText('Max ₹')).toHaveValue(2500);
    edit('Min ₹', '499');
    expect(screen.getByRole('slider', { name: 'Minimum price slider' })).toHaveValue('499');
    fireEvent.click(screen.getByRole('button', { name: 'Reset price' }));
    expect(screen.getByLabelText('Min ₹')).toHaveValue(0);
    expect(screen.getByLabelText('Max ₹')).toHaveValue(100000);
  });
  it('clamps bounds and crossed values without allowing an inverted range', () => {
    render(<Harness />);
    edit('Max ₹', '999999');
    expect(screen.getByLabelText('Max ₹')).toHaveValue(100000);
    edit('Min ₹', '-50');
    expect(screen.getByLabelText('Min ₹')).toHaveValue(0);
    edit('Min ₹', '800');
    edit('Max ₹', '300');
    expect(screen.getByLabelText('Max ₹')).toHaveValue(800);
    edit('Min ₹', '900');
    expect(screen.getByLabelText('Min ₹')).toHaveValue(800);
  });
  it('rejects blank, fractional and unsafe numeric edits without changing the filter', () => {
    render(<Harness />);
    for (const invalid of ['', '2.5', '1e30']) {
      edit('Max ₹', invalid);
      expect(screen.getByLabelText('Max ₹')).toHaveValue(100000);
      expect(screen.getByRole('status')).toHaveTextContent('Enter a whole rupee amount.');
      expect(screen.getByRole('slider', { name: 'Maximum price slider' })).toHaveValue('100000');
    }
  });
  it('gives simultaneous sidebar and mobile instances independent labels', () => {
    const { container } = render(<><Harness /><Harness /></>);
    const ids = Array.from(container.querySelectorAll('input[id]')).map(input => input.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
