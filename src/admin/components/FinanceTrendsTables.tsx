import type { OrderStatus } from '../types';
import AdminTable from './AdminTable';
import type { FinanceTrends, Comparison } from '../services/financeAnalytics';
import { inr } from './AdminShared';
import FinanceTableHeader from './FinanceTableHeader';
export default function FinanceTrendsTables({data,onFilterOrders}:{data:FinanceTrends;onFilterOrders?:(status:OrderStatus)=>void}) {
  const metrics: [string,Comparison,boolean][]=[['Gross product sales',data.grossSales,true],['Net revenue',data.netRevenue,true],['Orders',data.orders,false],['Average order value',data.averageOrderValue,true],['Refunds',data.refunds,true]];
  const ops=data.operationalIndicators;
  const states: [string,number,string][]=[['Pending payment',ops.pendingPaymentCount,'PENDING_PAYMENT'],['Cancelled',ops.cancelledCount,'CANCELLED'],['Refunded',ops.refundedCount,'REFUNDED'],...Object.entries(ops.fulfillmentStates).map(([state,count]):[string,number,string]=>[state.replaceAll('_',' '),count,state.toUpperCase()])];
  const supported:OrderStatus[]=['PENDING_PAYMENT','PAID','CONFIRMED','PROCESSING','READY_TO_SHIP','SHIPPED','OUT_FOR_DELIVERY','DELIVERED','CANCELLED','REFUNDED'];
  return <><p className="mb-2 text-xs">Compared with {data.previousRange.from} to {data.previousRange.to} (IST).</p>
    <div className="finance-table-scroll"><AdminTable className="w-full text-left text-sm"><FinanceTableHeader columns={['Metric','Current','Previous','Change']}/><tbody>{metrics.map(([label,value,currency])=><tr key={label} className="border-t border-[#F0EAE3]"><th scope="row" className="p-2 font-normal">{label}</th><td className="whitespace-nowrap p-2">{currency?inr((value.currentPaise??value.current*100)/100):value.current}</td><td className="whitespace-nowrap p-2">{currency?inr((value.previousPaise??value.previous*100)/100):value.previous}</td><td className="p-2">{value.growthPct===null?'No previous baseline':`${value.growthPct>0?'+':''}${value.growthPct.toFixed(1)}%`}</td></tr>)}</tbody></AdminTable></div>
    <h3 className="mb-2 mt-4 text-sm font-semibold">Operational counts (separate from revenue)</h3><p className="mb-2 text-xs">Pending payment amount: {inr(ops.pendingPaymentTotalPaise/100)}</p>
    <div className="finance-table-scroll"><AdminTable className="w-full text-left text-sm"><FinanceTableHeader columns={['Status','Orders']}/><tbody>{states.map(([label,count,status],index)=><tr key={`${label}-${index}`} className="border-t border-[#F0EAE3]"><th scope="row" className="font-normal">{onFilterOrders && supported.includes(status as OrderStatus) ? <button type="button" className="admin-entity-link block w-full p-2" onClick={()=>onFilterOrders(status as OrderStatus)}>{label}</button> : label}</th><td className="p-2">{count}</td></tr>)}</tbody></AdminTable></div>
  </>;
}
