import { useEffect, useState } from 'react';
import type { FinanceSummary, SalesDataPoint, DateRangePreset } from '../types';
import * as api from '../services/api';
import { inr, SectionHeader, TableSkeleton, MetricCard } from '../components/AdminShared';
import RevenueChart from '../components/RevenueChart';

interface Props { datePreset: DateRangePreset }

function FinanceRow({ label, value, note, negative, bold }: { label: string; value: string; note?: string; negative?: boolean; bold?: boolean }) {
  return <div className="flex items-start justify-between gap-4 border-b border-[#F0EAE3] py-3 last:border-0"><div><p className={`text-sm ${bold ? 'font-bold text-[#1A1108]' : 'text-[#6B5B4E]'}`}>{label}</p>{note && <p className="mt-0.5 text-[10px] text-[#9C8B7E]">{note}</p>}</div><span className={`shrink-0 font-mono text-sm font-semibold ${negative ? 'text-red-600' : 'text-[#1A1108]'}`}>{value}</span></div>;
}

export default function FinancePage({ datePreset }: Props) {
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [chart, setChart] = useState<SalesDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true); setError('');
    Promise.all([api.getFinanceSummary(datePreset), api.getSalesChartFinance(datePreset === '7d' ? '7d' : '30d')])
      .then(([nextSummary, nextChart]) => { if (active) { setSummary(nextSummary); setChart(nextChart); } })
      .catch(reason => { if (active) setError(reason instanceof Error ? reason.message : 'Could not load finance data.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [datePreset]);

  const metrics = summary ? [
    { label: 'Gross Sales', value: inr(summary.grossSales), icon: '↗' },
    { label: 'Net Revenue', value: inr(summary.netRevenue), icon: '₹', accent: '#8FAF8C' },
    { label: 'Stored Tax', value: inr(summary.gstCollected), icon: '▤' },
    { label: 'Refunds', value: inr(summary.refunds), icon: '↩', accent: '#EF4444' },
  ] : [];

  return <div className="max-w-full space-y-5">
    {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">Finance data could not be loaded. {error}</div>}
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">{loading ? Array.from({ length: 4 }).map((_, i) => <MetricCard key={i} label="" value="" icon="" loading />) : metrics.map(metric => <MetricCard key={metric.label} {...metric} />)}</div>
    <RevenueChart data={chart} loading={loading} />
    <div className="grid gap-5 lg:grid-cols-2">
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-5"><SectionHeader title="Recorded Finance" subtitle="Amounts are supplied by Sulocraft’s backend." />{loading ? <TableSkeleton rows={6} cols={2} /> : summary && <><FinanceRow label="Gross Sales" value={inr(summary.grossSales)} /><FinanceRow label="Discounts" value={`−${inr(summary.discounts)}`} negative /><FinanceRow label="Shipping Collected" value={inr(summary.shippingCollected)} /><FinanceRow label="Stored Tax" value={inr(summary.gstCollected)} note="Stored order tax total; tax components are not reported." /><FinanceRow label="Refunds" value={`−${inr(summary.refunds)}`} negative /><FinanceRow label="Net Revenue" value={inr(summary.netRevenue)} bold /><FinanceRow label="Gateway Fees" value={summary.gatewayFeesAvailable && summary.paymentFees !== null ? inr(summary.paymentFees) : 'Not available'} note={summary.gatewayFeesNote || 'No fee ledger is connected.'} /></>}</section>
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-5"><SectionHeader title="Order Totals" subtitle="Backend summary for the selected period." />{loading ? <TableSkeleton rows={3} cols={2} /> : summary && <><FinanceRow label="Orders" value={summary.orderCount.toLocaleString('en-IN')} /><FinanceRow label="Completed Refunds" value={summary.refundCount.toLocaleString('en-IN')} /><FinanceRow label="Taxable Sales" value={inr(summary.taxableSales)} note="Backend-reported amount; not recalculated here." /></>}</section>
    </div>
  </div>;
}
