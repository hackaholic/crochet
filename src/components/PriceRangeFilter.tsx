import { useEffect, useId, useState } from 'react';
import type { PriceBounds } from '../config/catalogue';
import './priceRangeFilter.css';

interface Props {
  bounds: PriceBounds;
  value: PriceBounds;
  onChange: (value: PriceBounds) => void;
  onReset: () => void;
  active: boolean;
}

export default function PriceRangeFilter({ bounds, value, onChange, onReset, active }: Props) {
  const id = useId();
  const [draft, setDraft] = useState({ min: String(value.min), max: String(value.max) });
  const [error, setError] = useState('');
  useEffect(() => { setDraft({ min: String(value.min), max: String(value.max) }); setError(''); }, [value.min, value.max]);

  const update = (key: 'min' | 'max', next: number) => {
    const clamped = Math.max(bounds.min, Math.min(bounds.max, next));
    onChange({ ...value, [key]: key === 'min' ? Math.min(clamped, value.max) : Math.max(clamped, value.min) });
  };
  const commit = (key: 'min' | 'max') => {
    const raw = draft[key].trim();
    const next = Number(raw);
    if (!raw || !Number.isSafeInteger(next)) {
      setDraft(previous => ({ ...previous, [key]: String(value[key]) }));
      setError('Enter a whole rupee amount.');
      return;
    }
    const clamped = Math.max(bounds.min, Math.min(bounds.max, next));
    const resolved = key === 'min' ? Math.min(clamped, value.max) : Math.max(clamped, value.min);
    setDraft(previous => ({ ...previous, [key]: String(resolved) }));
    setError('');
    update(key, next);
  };

  return <div className="price-range-filter">
    <div className="price-range-track">
      {(['min', 'max'] as const).map(key => <input
        key={key} type="range" aria-label={key === 'min' ? 'Minimum price slider' : 'Maximum price slider'}
        min={bounds.min} max={bounds.max} step={1} value={value[key]}
        onChange={event => update(key, Number(event.target.value))}
        style={{ zIndex: key === 'min' && value.min === bounds.max ? 3 : key === 'max' ? 2 : 1 }}
      />)}
    </div>
    <div className="price-range-fields">
      {(['min', 'max'] as const).map(key => <div key={key}>
        <label htmlFor={`${id}-${key}`}>{key === 'min' ? 'Min ₹' : 'Max ₹'}</label>
        <input id={`${id}-${key}`} type="number" inputMode="numeric" min={bounds.min} max={bounds.max} step={1}
          value={draft[key]} aria-describedby={error ? `${id}-error` : undefined}
          onChange={event => setDraft(previous => ({ ...previous, [key]: event.target.value }))}
          onBlur={() => commit(key)} onKeyDown={event => { if (event.key === 'Enter') event.currentTarget.blur(); }} />
      </div>)}
    </div>
    {error && <p id={`${id}-error`} role="status" className="price-range-error">{error}</p>}
    <button type="button" onClick={onReset} disabled={!active} className="price-range-reset">Reset price</button>
  </div>;
}
