import CustomerPopup, {type CustomerPreviewInput} from '../components/CustomerPopup';
import AdminTable from '../components/AdminTable';
import { useEffect, useState } from 'react';
import type { Return, ReturnStatus } from '../types';
import * as api from '../services/api';
import { ReturnStatusBadge } from '../components/StatusBadge';
import { inr, EmptyState, TableSkeleton, SectionHeader, ConfirmDialog } from '../components/AdminShared';

interface Props {
  onSelectOrder?: (id: string) => void;
}

const STATUS_TABS: { id: ReturnStatus | 'ALL'; label: string }[] = [
  { id: 'ALL', label: 'All Returns' },
  { id: 'REQUESTED', label: 'Requested' },
  { id: 'APPROVED', label: 'Approved' },
  { id: 'ITEMS_RECEIVED', label: 'Items Received' },
  { id: 'INSPECTED', label: 'Inspected' },
  { id: 'REFUNDED', label: 'Refunded' },
  { id: 'REJECTED', label: 'Rejected' },
];

export default function ReturnsPage({ onSelectOrder }: Props) {
  const [returns, setReturns] = useState<Return[]>([]);
  const [previewCustomer,setPreviewCustomer]=useState<CustomerPreviewInput>();
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<ReturnStatus | 'ALL'>('ALL');
  const [confirm, setConfirm] = useState<{ action: 'approve' | 'reject' | 'refund'; item: Return } | null>(null);
  const [processing, setProcessing] = useState(false);

  const [loadError,setLoadError] = useState(false);
  const [actionError,setActionError] = useState('');
  const [retry,setRetry] = useState(0);
  useEffect(() => {
    let active=true;setLoading(true);setLoadError(false);
    api.getReturns().then(r => {if(active)setReturns(r);})
      .catch(()=>{if(active)setLoadError(true);}).finally(()=>{if(active)setLoading(false);});
    return()=>{active=false;};
  }, [retry]);

  const filtered = statusFilter === 'ALL' ? returns : returns.filter(r => r.status === statusFilter);

  const handleAction = async () => {
    if (!confirm || processing) return;
    setProcessing(true);setActionError('');
    try {
    if (confirm.action === 'approve') await api.approveReturn(confirm.item.id);
    else if (confirm.action === 'reject') await api.rejectReturn(confirm.item.id);
    else await api.processReturnRefund(confirm.item.id);
    setReturns(prev => prev.map(r => r.id === confirm.item.id ? { ...r, status: confirm.action === 'approve' ? 'APPROVED' : confirm.action === 'reject' ? 'REJECTED' : 'REFUNDED' } : r));
    setConfirm(null);
    } catch {setActionError('Return could not be updated. Its status is unchanged. Try again.');}
    finally {setProcessing(false);}
  };

  if(loadError) return <div role="alert" className="rounded-xl border bg-white p-5">Returns could not be loaded. <button className="underline" onClick={()=>setRetry(x=>x+1)}>Retry returns</button></div>;

  const relDate = (ts: string) => new Date(ts).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' });

  return (
    <div className="space-y-4">
      {previewCustomer && <CustomerPopup customer={previewCustomer} onClose={()=>setPreviewCustomer(undefined)} onSelectOrder={id=>{setPreviewCustomer(undefined);onSelectOrder?.(id);}}/>}
      {/* Summary KPIs */}
      {!loading && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            {
              label: 'Total Returns',
              value: returns.length,
              icon: '↩',
              accent: '#C25E00',
              bgClass: 'bg-[#FFF7ED]', // Warm Amber
              borderClass: 'border-[#FED7AA]',
            },
            {
              label: 'Pending Review',
              value: returns.filter(r => r.status === 'REQUESTED').length,
              icon: '⏳',
              accent: '#1D4ED8',
              bgClass: 'bg-[#EFF6FF]', // Sky / Blue
              borderClass: 'border-[#BFDBFE]',
            },
            {
              label: 'Awaiting Inspection',
              value: returns.filter(r => r.status === 'ITEMS_RECEIVED').length,
              icon: '⌕',
              accent: '#6D28D9',
              bgClass: 'bg-[#FAF5FF]', // Purple
              borderClass: 'border-[#E9D5FF]',
            },
            {
              label: 'Refunded Value',
              value: inr(returns.filter(r => r.status === 'REFUNDED').reduce((s, r) => s + r.refundAmount, 0)),
              icon: '₹',
              accent: '#BE123C',
              bgClass: 'bg-[#FFF1F2]', // Rose Red
              borderClass: 'border-[#FECDD3]',
            },
          ].map(({ label, value, icon, accent, bgClass, borderClass }) => (
            <div
              key={label}
              className={`${bgClass} rounded-xl border ${borderClass} p-4 shadow-none hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-default group`}
            >
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs text-[#6B5B4E] uppercase tracking-wider font-medium">{label}</p>
                <span className="text-base transition-transform duration-200 group-hover:scale-110" style={{ color: accent }}>{icon}</span>
              </div>
              <p className="font-bold text-[#1A1108] text-xl" style={{ fontFamily: 'var(--font-serif)' }}>{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-1 bg-white rounded-xl border border-[#E8E0D8] p-1 overflow-x-auto">
        {STATUS_TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setStatusFilter(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${statusFilter === tab.id ? 'bg-[#C4622D] text-white shadow-sm' : 'text-[#6B5B4E] hover:bg-[#F5F0EA]'}`}
          >
            {tab.label}
          </button>
        ))}
        <div className="ml-auto flex items-center">
          <button disabled title="Export is unavailable until the backend provides a returns export endpoint." className="cursor-not-allowed px-3 py-1.5 text-xs font-medium text-[#B7AAA0] flex items-center gap-1">↓ Export CSV</button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-[#E8E0D8] overflow-hidden">
        <div className="overflow-x-auto">
          <AdminTable className="w-full text-xs min-w-[800px]">
            <thead className="bg-[#F8F4EF] border-b border-[#E8E0D8]">
              <tr>
                {['Return ID', 'Order', 'Customer', 'Product', 'Reason', 'Requested', 'Status', 'Refund', 'Actions'].map(h => (
                  <th scope="col" key={h} className="text-left py-2.5 px-3 text-[#9C8B7E] font-semibold uppercase tracking-wider text-[10px] whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="p-4"><TableSkeleton rows={5} cols={8} /></td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={9}><EmptyState icon="📦" title="No returns" desc="No returns match the current filter." /></td></tr>
              ) : filtered.map(item => (
                <tr key={item.id} className="border-b border-[#F8F4EF] hover:bg-[#FDFAF7] transition-colors">
                  <td className="py-2.5 px-3">
                    <span className="font-mono font-semibold text-[#6B5B4E]">{item.id}</span>
                  </td>
                  <td className="py-2.5 px-3">
                    <button
                      onClick={() => onSelectOrder?.(item.orderId)}
                      className="font-mono font-bold text-[#C4622D] hover:underline"
                    >
                      {item.orderNumber}
                    </button>
                  </td>
                  <td className="py-2.5 px-3">
                    <button type="button" className="admin-entity-link block w-full" aria-label={`View customer ${item.customer.name}`} onClick={()=>setPreviewCustomer(item.customer)}><span className="block font-medium">{item.customer.name}</span><span className="block text-[#9C8B7E]">{item.customer.email}</span></button>
                  </td>
                  <td className="py-2.5 px-3 text-[#1A1108] max-w-[120px] truncate">{item.productName}</td>
                  <td className="py-2.5 px-3 text-[#6B5B4E] max-w-[150px]">
                    <span title={item.reason} className="truncate block max-w-[140px]">{item.reason}</span>
                  </td>
                  <td className="py-2.5 px-3 text-[#9C8B7E] whitespace-nowrap">{relDate(item.requestedDate)}</td>
                  <td className="py-2.5 px-3">
                    <ReturnStatusBadge status={item.status} size="sm" />
                  </td>
                  <td className="py-2.5 px-3 font-bold text-[#1A1108] whitespace-nowrap">{inr(item.refundAmount)}</td>
                  <td className="py-2.5 px-3">
                    <div className="flex items-center gap-1.5">
                      {item.status === 'REQUESTED' && (
                        <>
                          <button
                            onClick={() => {setActionError('');setConfirm({ action: 'approve', item });}}
                            className="px-2.5 py-1 text-[10px] font-semibold bg-[#DCFCE7] text-[#166534] rounded-lg hover:bg-[#BBF7D0] transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => {setActionError('');setConfirm({ action: 'reject', item });}}
                            className="px-2.5 py-1 text-[10px] font-semibold bg-[#FEF2F2] text-[#991B1B] rounded-lg hover:bg-[#FECACA] transition-colors"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {item.status === 'APPROVED' && <span className="text-[10px] text-[#9C8B7E]">Awaiting returned items</span>}
                      {item.status === 'ITEMS_RECEIVED' && <span className="text-[10px] text-[#9C8B7E]">Awaiting inspection</span>}
                      {item.status === 'INSPECTED' && <button onClick={() => {setActionError('');setConfirm({ action: 'refund', item });}} className="rounded-lg border border-[#FDE68A] bg-[#FFFBEB] px-2.5 py-1 text-[10px] font-semibold text-[#92400E] hover:bg-[#FDE68A]">Issue refund</button>}
                      {(item.status === 'REFUNDED' || item.status === 'REJECTED' || item.status === 'CANCELLED') && (
                        <span className="text-[10px] text-[#9C8B7E]">Closed</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </AdminTable>
        </div>
      </div>

      {/* Confirm dialog */}
      <ConfirmDialog
        open={!!confirm}
        title={confirm?.action === 'approve' ? 'Approve Return' : confirm?.action === 'refund' ? 'Issue Refund' : 'Reject Return'}
        message={`Are you sure you want to ${confirm?.action === 'refund' ? 'issue the verified refund for' : confirm?.action} the return request for order ${confirm?.item.orderNumber}?`}
        confirmLabel={confirm?.action === 'approve' ? 'Yes, Approve' : confirm?.action === 'refund' ? 'Issue Refund' : 'Yes, Reject'}
        danger={confirm?.action !== 'approve'}
        busy={processing}
        error={actionError}
        onConfirm={handleAction}
        onCancel={() => setConfirm(null)}
      />
    </div>
  );
}
