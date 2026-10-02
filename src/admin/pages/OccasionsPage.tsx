import { useEffect, useState } from 'react';
import type { AdminOccasion } from '../types';
import * as api from '../services/api';
import { EmptyState } from '../components/AdminShared';

function dateValue(value?: string | null) {
  if (!value) return '';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '' : new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(date);
}

function localDateTime(value: string, endOfDay = false) {
  return value ? `${value}T${endOfDay ? '23:59:59' : '00:00:00'}+05:30` : null;
}

export default function OccasionsPage() {
  const [occasions, setOccasions] = useState<AdminOccasion[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [error, setError] = useState('');

  const refresh = () => {
    setLoading(true);
    setError('');
    api.getAdminOccasions()
      .then(setOccasions)
      .catch(() => setError('Could not load occasions. Check your admin session and try again.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const save = async (id: string, patch: Partial<Pick<AdminOccasion, 'isEnabled' | 'startsAt' | 'endsAt'>>) => {
    setSavingId(id);
    setError('');
    try {
      const updated = await api.updateAdminOccasion(id, patch);
      setOccasions(current => current.map(item => item.id === id ? updated : item));
    } catch {
      setError('The change was not saved. Please try again.');
      refresh();
    } finally {
      setSavingId(null);
    }
  };

  return (
    <section className="space-y-5" aria-labelledby="occasions-title">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#C4622D]">Storefront content</p>
          <h1 id="occasions-title" className="mt-1 text-2xl font-semibold text-[#1A1108]" style={{ fontFamily: 'var(--font-serif)' }}>Gift by Occasion</h1>
          <p className="mt-1 max-w-2xl text-sm text-[#6B5B4E]">Keep year-round occasions always available and turn seasonal gifting on when it is relevant.</p>
        </div>
        <button onClick={refresh} className="rounded-lg border border-[#E8E0D8] bg-white px-3 py-2 text-xs font-semibold text-[#6B5B4E] hover:bg-[#F8F4EF]">Refresh</button>
      </header>

      {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</p>}
      {loading ? (
        <div className="rounded-xl border border-[#E8E0D8] bg-white p-6 text-sm text-[#6B5B4E]" role="status">Loading occasions…</div>
      ) : occasions.length === 0 ? (
        <div className="rounded-xl border border-[#E8E0D8] bg-white"><EmptyState icon="🎁" title="No occasions configured" desc="Occasion cards will appear here after the store has occasion records." /></div>
      ) : (
        <div className="space-y-3">
          {occasions.map(occasion => {
            const evergreenKnown = occasion.isEvergreen !== null;
            const evergreen = occasion.isEvergreen === true;
            const busy = savingId === occasion.id;
            return (
              <article key={occasion.id} className="grid gap-4 rounded-2xl border border-[#E8E0D8] bg-white p-4 sm:grid-cols-[112px_minmax(0,1fr)] sm:p-5">
                <div className="aspect-[4/3] overflow-hidden rounded-xl bg-[#F5EDE0]">
                  {occasion.imageUrl && <img src={occasion.imageUrl} alt="" loading="lazy" className="h-full w-full object-cover" />}
                </div>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="font-semibold text-[#1A1108]">{occasion.icon ? `${occasion.icon} ` : ''}{occasion.name}</h2>
                        {evergreen && <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-800">Always on</span>}
                        {!evergreen && <span className="rounded-full bg-[#F8F4EF] px-2.5 py-1 text-[11px] font-medium text-[#6B5B4E]">Seasonal</span>}
                      </div>
                      <p className="mt-1 text-xs text-[#9C8B7E]">{occasion.productCount} associated products · Display order {occasion.displayOrder}</p>
                    </div>
                    <label className={`inline-flex items-center gap-2 text-xs font-medium ${evergreen || !evergreenKnown ? 'text-[#9C8B7E]' : 'text-[#6B5B4E]'}`}>
                      <input
                        aria-label={`Show ${occasion.name} on storefront`}
                        type="checkbox"
                        checked={evergreen || occasion.isEnabled}
                        disabled={evergreen || !evergreenKnown || busy}
                        onChange={event => save(occasion.id, { isEnabled: event.currentTarget.checked })}
                        className="h-4 w-4 accent-[#C4622D]"
                      />
                      {evergreen ? 'Always visible' : occasion.isEnabled ? 'Enabled' : 'Hidden'}
                    </label>
                  </div>
                  {occasion.description && <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5B4E]">{occasion.description}</p>}
                  {!evergreenKnown && <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-900">The backend has not identified evergreen status yet. Visibility and schedule controls are locked until that contract is available.</p>}
                  {!evergreen && evergreenKnown && (
                    <form
                      className="mt-4 flex flex-wrap items-end gap-3 border-t border-[#F0E9E2] pt-4"
                      onSubmit={event => {
                        event.preventDefault();
                        const data = new FormData(event.currentTarget);
                        void save(occasion.id, {
                          startsAt: localDateTime(String(data.get('startsAt') || '')),
                          endsAt: localDateTime(String(data.get('endsAt') || ''), true),
                        });
                      }}
                    >
                      <label className="grid gap-1 text-[11px] font-medium text-[#6B5B4E]">Starts (India time)
                        <input name="startsAt" type="date" defaultValue={dateValue(occasion.startsAt)} disabled={busy} className="rounded-lg border border-[#E8E0D8] px-2.5 py-2 text-xs text-[#1A1108]" />
                      </label>
                      <label className="grid gap-1 text-[11px] font-medium text-[#6B5B4E]">Ends (India time)
                        <input name="endsAt" type="date" defaultValue={dateValue(occasion.endsAt)} disabled={busy} className="rounded-lg border border-[#E8E0D8] px-2.5 py-2 text-xs text-[#1A1108]" />
                      </label>
                      <button type="submit" disabled={busy} className="rounded-lg bg-[#1A1108] px-3 py-2 text-xs font-semibold text-white disabled:opacity-50">{busy ? 'Saving…' : 'Save schedule'}</button>
                    </form>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
