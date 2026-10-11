import FinanceAnalytics from '../components/FinanceAnalytics';
import { dateRange } from '../services/dateRange';
import { useEffect, useMemo, useState } from 'react';
import type { FinanceSummary, SalesDataPoint, DateRangePreset, OrderStatus } from '../types';
import * as api from '../services/api';
import { inr, SectionHeader, TableSkeleton, MetricCard } from '../components/AdminShared';
import RevenueChart from '../components/RevenueChart';

interface Props { datePreset: DateRangePreset; onSelectProduct?:(id:number)=>void; onFilterOrders?:(status:OrderStatus,range:{from:string;to:string})=>void }

function FinanceRow({ label, value, note, negative, bold }: { label: string; value: string; note?: string; negative?: boolean; bold?: boolean }) {
  return <div className="flex items-start justify-between gap-4 border-b border-[#F0EAE3] py-3 last:border-0"><div><p className={`text-sm ${bold ? 'font-bold text-[#1A1108]' : 'text-[#6B5B4E]'}`}>{label}</p>{note && <p className="mt-0.5 text-[10px] text-[#9C8B7E]">{note}</p>}</div><span className={`shrink-0 font-mono text-sm font-semibold ${negative ? 'text-red-600' : 'text-[#1A1108]'}`}>{value}</span></div>;
}

export default function FinancePage({ datePreset,onSelectProduct,onFilterOrders }: Props) {
  const range = useMemo(()=>dateRange(datePreset),[datePreset]);
  const [attempt,setAttempt] = useState(0);
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [chart, setChart] = useState<SalesDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true); setError(''); setSummary(null); setChart([]);
    Promise.all([api.getFinanceSummary(datePreset,range), api.getSalesChartFinance(datePreset,range)])
      .then(([nextSummary, nextChart]) => { if (active) { setSummary(nextSummary); setChart(nextChart); } })
      .catch(reason => { if (active) setError(reason instanceof Error ? reason.message : 'Could not load finance data.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [datePreset,range,attempt]);

  const metrics = summary ? [
    { label: 'Gross Sales', value: inr(summary.grossSales), icon: '↗', accent: '#C4622D', bgClass: 'bg-[#FDF9F6]', borderClass: 'border-[#EADCCF]' },
    { label: 'Net Revenue', value: inr(summary.netRevenue), icon: '₹', accent: '#3F6E50', bgClass: 'bg-[#F6FAF6]', borderClass: 'border-[#D2E2D5]' },
    { label: 'Stored Tax', value: inr(summary.gstCollected), icon: '▤', accent: '#7A6B5D', bgClass: 'bg-[#FBF9F6]', borderClass: 'border-[#E8E0D8]' },
    { label: 'Refunds', value: inr(summary.refunds), icon: '↩', accent: '#B84545', bgClass: 'bg-[#FDF6F6]', borderClass: 'border-[#F0D5D5]' },
  ] : [];

  return <div className="max-w-full space-y-5">
    {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">Finance data could not be loaded.<button type="button" className="ml-3 underline" onClick={()=>setAttempt(value=>value+1)}>Retry finance</button></div>}
    {!loading && !error && summary?.effectiveRange && <p className="text-sm text-[#6B5B4E]" aria-label="Reporting period">Reporting period: <time dateTime={summary.effectiveRange.from}>{summary.effectiveRange.from}</time> to <time dateTime={summary.effectiveRange.to}>{summary.effectiveRange.to}</time> (IST, inclusive)</p>}
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">{loading ? Array.from({ length: 4 }).map((_, i) => <MetricCard key={i} label="" value="" icon="" loading />) : metrics.map(metric => <MetricCard key={metric.label} {...metric} />)}</div>
    <RevenueChart data={chart} loading={loading} />
    <div className="grid gap-5 lg:grid-cols-2">
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-5"><SectionHeader title="Recorded Finance" subtitle="Amounts are supplied by Sulocraft’s backend." />{loading ? <TableSkeleton rows={6} cols={2} /> : summary && <><FinanceRow label="Gross Sales" value={inr(summary.grossSales)} /><FinanceRow label="Discounts" value={`−${inr(summary.discounts)}`} negative /><FinanceRow label="Shipping Collected" value={inr(summary.shippingCollected)} /><FinanceRow label="Stored Tax" value={inr(summary.gstCollected)} note="Stored order tax total; tax components are not reported." /><FinanceRow label="Refunds" value={`−${inr(summary.refunds)}`} negative /><FinanceRow label="Net Revenue" value={inr(summary.netRevenue)} bold /><FinanceRow label="Gateway Fees" value={summary.gatewayFeesAvailable && summary.paymentFees !== null ? inr(summary.paymentFees) : 'Not available'} note={summary.gatewayFeesNote || (summary.gatewayFeesAvailable ? 'Recorded fees for this period.' : 'No fee ledger is connected.')} /></>}</section>
      <section className="rounded-xl border border-[#E8E0D8] bg-white p-5"><SectionHeader title="Order Totals" subtitle="Backend summary for the selected period." />{loading ? <TableSkeleton rows={3} cols={2} /> : summary && <><FinanceRow label="Orders" value={summary.orderCount.toLocaleString('en-IN')} /><FinanceRow label="Completed Refunds" value={summary.refundCount.toLocaleString('en-IN')} /><FinanceRow label="Taxable Sales" value={inr(summary.taxableSales)} note="Backend-reported amount; not recalculated here." /></>}</section>
    </div>
    <FinanceAnalytics range={range} onSelectProduct={onSelectProduct} onFilterOrders={onFilterOrders}/>
  </div>;
}
