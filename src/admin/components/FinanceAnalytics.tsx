import type { OrderStatus } from '../types';
import AdminTable from './AdminTable';
import { useEffect, useState, type ReactNode } from 'react';
import { getFinanceAnalytics, type CategorySales, type DestinationSales, type ProductSales, type FinanceTrends, type ReportingRange, type RankingMetric } from '../services/financeAnalytics';
import { inr, TableSkeleton } from './AdminShared';
import FinanceTableHeader from './FinanceTableHeader';
import FinanceProductTable from './FinanceProductTable';
import FinanceTrendsTables from './FinanceTrendsTables';
import CountryFlag from './CountryFlag';
const money = (paise: number) => inr(paise / 100);
function Panel<T>({ title, range, endpoint, options, children, controls }: { title: string; range: ReportingRange; endpoint: Parameters<typeof getFinanceAnalytics>[0]; options?: Parameters<typeof getFinanceAnalytics>[2]; children: (data:T)=>ReactNode; controls?: ReactNode }) {
  const [data,setData]=useState<T|null>(null), [error,setError]=useState(false), [loading,setLoading]=useState(true), [attempt,setAttempt]=useState(0);
  const { metric,limit,sortBy }=options || {};
  useEffect(()=>{ const controller=new AbortController(); let active=true; setData(null); setLoading(true); setError(false);
    getFinanceAnalytics<T>(endpoint,range,{metric,limit,sortBy},controller.signal).then(value=>{if(active)setData(value);}).catch(()=>{if(active)setError(true);}).finally(()=>{if(active)setLoading(false);});
    return ()=>{active=false;controller.abort();};
  },[endpoint,range.from,range.to,metric,limit,sortBy,attempt]);
  return <section aria-label={title} className="min-w-0 rounded-xl border border-[#E8E0D8] bg-white p-5"><h2 className="mb-3 font-semibold">{title}</h2>{controls}{loading ? <TableSkeleton rows={3} cols={3}/> : error ? <p role="alert">Could not load {title.toLowerCase()}. <button className="underline" onClick={()=>setAttempt(v=>v+1)}>Retry {title.toLowerCase()}</button></p> : data && children(data)}</section>;
}
function SalesTable({rows,nameLabel}: {rows:{name:ReactNode;orders:number;units:number;paise:number;share:number}[];nameLabel:string}) {
  if(!rows.length)return <p className="text-sm text-[#6B5B4E]">No qualifying sales in this period.</p>;
  return <div className="finance-table-scroll"><AdminTable className="w-full text-left text-sm"><FinanceTableHeader columns={[nameLabel,'Orders','Units','Gross product sales','Share']}/><tbody>{rows.map((row,index)=><tr key={index} className="border-t border-[#F0EAE3]"><th scope="row" className="px-2 py-3 font-normal">{row.name}</th><td className="px-2">{row.orders}</td><td className="px-2">{row.units}</td><td className="px-2 whitespace-nowrap">{money(row.paise)}</td><td className="px-2">{row.share.toFixed(1)}%</td></tr>)}</tbody></AdminTable></div>;
}
export default function FinanceAnalytics({range,onSelectProduct,onFilterOrders}:{range:ReportingRange;onSelectProduct?:(id:number)=>void;onFilterOrders?:(status:OrderStatus,range:ReportingRange)=>void}) {
  const [metric,setMetric]=useState<RankingMetric>('revenue'),[limit,setLimit]=useState(10),[sortBy,setSortBy]=useState('sales');
  useEffect(()=>setLimit(10),[range.from,range.to,metric]);
  return <div className="grid min-w-0 gap-5 lg:grid-cols-2">
    <Panel<CategorySales> title="Sales by Category" endpoint="categories" range={range} options={{sortBy,limit:200}} controls={<label className="mb-3 block text-sm">Category ranking <select aria-label="Category ranking" value={sortBy} onChange={e=>setSortBy(e.target.value)}>{['sales','units','orders','name'].map(v=><option key={v} value={v}>{v}</option>)}</select></label>}>{data=><><p className="mb-2 text-xs text-[#6B5B4E]">Share of {money(data.totalGrossSalesPaise)} gross product sales. Current category attribution; each item counted once. Refund attribution unavailable.</p><SalesTable nameLabel="Category" rows={data.categories.map(v=>({name:v.categoryName,orders:v.orderCount,units:v.unitsSold,paise:v.grossSalesPaise,share:v.salesSharePct}))}/></>}</Panel>
    <Panel<DestinationSales> title="Sales by Destination" endpoint="destinations" range={range}>{data=><><p className="mb-2 text-xs text-[#6B5B4E]">Checkout shipping snapshots; share of {money(data.totalGrossSalesPaise)} gross product sales.</p><SalesTable nameLabel="Country" rows={data.countries.map(v=>({name:<span className="inline-flex items-center"><CountryFlag countryCode={v.countryCode} title={v.countryCode==='UNKNOWN'?'Unknown destination':v.countryName}/><span>{v.countryCode==='UNKNOWN'?'Unknown destination':v.countryName}</span></span>,orders:v.orderCount,units:v.unitsSold,paise:v.grossSalesPaise,share:v.salesSharePct}))}/>{data.countries.filter(v=>v.regions.length).map(country=><details key={country.countryCode} className="mt-3"><summary className="cursor-pointer text-sm">{country.countryName} regions</summary><SalesTable nameLabel="State" rows={country.regions.map(v=>({name:v.state,orders:v.orderCount,units:v.unitsSold,paise:v.grossSalesPaise,share:v.salesSharePct}))}/></details>)}</>}</Panel>
    <Panel<ProductSales> title="Top-selling Products" endpoint="top-products" range={range} options={{metric,limit}} controls={<label className="mb-3 block text-sm">Rank by <select aria-label="Product ranking" value={metric} onChange={e=>setMetric(e.target.value as RankingMetric)}><option value="revenue">Product revenue</option><option value="units">Units sold</option></select></label>}>{data=><><FinanceProductTable data={data} onSelectProduct={onSelectProduct}/>{data.items.length>=limit && limit<100 && <button className="mt-3 underline" onClick={()=>setLimit(v=>Math.min(100,v+10))}>Show more products</button>}</>}</Panel>
    <Panel<FinanceTrends> title="Trends & Operations" endpoint="trends" range={range}>{data=><FinanceTrendsTables data={data} onFilterOrders={onFilterOrders ? status=>onFilterOrders(status,range) : undefined}/>}</Panel>
  </div>;
}
