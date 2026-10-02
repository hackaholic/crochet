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
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<ReturnStatus | 'ALL'>('ALL');
  const [confirm, setConfirm] = useState<{ action: 'approve' | 'reject' | 'refund'; item: Return } | null>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getReturns().then(r => { setReturns(r); setLoading(false); });
  }, []);

  const filtered = statusFilter === 'ALL' ? returns : returns.filter(r => r.status === statusFilter);

  const handleAction = async () => {
    if (!confirm) return;
    setProcessing(true);
    if (confirm.action === 'approve') await api.approveReturn(confirm.item.id);
    else if (confirm.action === 'reject') await api.rejectReturn(confirm.item.id);
    else await api.processReturnRefund(confirm.item.id);
    setReturns(prev => prev.map(r => r.id === confirm.item.id ? { ...r, status: confirm.action === 'approve' ? 'APPROVED' : confirm.action === 'reject' ? 'REJECTED' : 'REFUNDED' } : r));
    setConfirm(null);
    setProcessing(false);
  };

  const relDate = (ts: string) => new Date(ts).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' });

  return (
    <div className="space-y-4">
      {/* Summary KPIs */}
      {!loading && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'Total Returns', value: returns.length, icon: '↩' },
            { label: 'Pending Review', value: returns.filter(r => r.status === 'REQUESTED').length, icon: '⏳' },
            { label: 'Awaiting Inspection', value: returns.filter(r => r.status === 'ITEMS_RECEIVED').length, icon: '⌕' },
            { label: 'Refunded Value', value: inr(returns.filter(r => r.status === 'REFUNDED').reduce((s, r) => s + r.refundAmount, 0)), icon: '₹' },
          ].map(({ label, value, icon }) => (
            <div key={label} className="bg-white rounded-xl border border-[#E8E0D8] p-4">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-base">{icon}</span>
                <p className="text-xs text-[#9C8B7E] font-medium">{label}</p>
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
          <table className="w-full text-xs min-w-[800px]">
            <thead className="bg-[#F8F4EF] border-b border-[#E8E0D8]">
              <tr>
                {['Return ID', 'Order', 'Customer', 'Product', 'Reason', 'Requested', 'Status', 'Refund', 'Actions'].map(h => (
                  <th key={h} className="text-left py-2.5 px-3 text-[#9C8B7E] font-semibold uppercase tracking-wider text-[10px] whitespace-nowrap">{h}</th>
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
                    <p className="font-medium text-[#1A1108]">{item.customer.name}</p>
                    <p className="text-[#9C8B7E]">{item.customer.email}</p>
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
                            onClick={() => setConfirm({ action: 'approve', item })}
                            className="px-2.5 py-1 text-[10px] font-semibold bg-[#DCFCE7] text-[#166534] rounded-lg hover:bg-[#BBF7D0] transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => setConfirm({ action: 'reject', item })}
                            className="px-2.5 py-1 text-[10px] font-semibold bg-[#FEF2F2] text-[#991B1B] rounded-lg hover:bg-[#FECACA] transition-colors"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {item.status === 'APPROVED' && <span className="text-[10px] text-[#9C8B7E]">Awaiting returned items</span>}
                      {item.status === 'ITEMS_RECEIVED' && <span className="text-[10px] text-[#9C8B7E]">Awaiting inspection</span>}
                      {item.status === 'INSPECTED' && <button onClick={() => setConfirm({ action: 'refund', item })} className="rounded-lg border border-[#FDE68A] bg-[#FFFBEB] px-2.5 py-1 text-[10px] font-semibold text-[#92400E] hover:bg-[#FDE68A]">Issue refund</button>}
                      {(item.status === 'REFUNDED' || item.status === 'REJECTED' || item.status === 'CANCELLED') && (
                        <span className="text-[10px] text-[#9C8B7E]">Closed</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Confirm dialog */}
      <ConfirmDialog
        open={!!confirm}
        title={confirm?.action === 'approve' ? 'Approve Return' : confirm?.action === 'refund' ? 'Issue Refund' : 'Reject Return'}
        message={`Are you sure you want to ${confirm?.action === 'refund' ? 'issue the verified refund for' : confirm?.action} the return request for order ${confirm?.item.orderNumber}?`}
        confirmLabel={confirm?.action === 'approve' ? 'Yes, Approve' : confirm?.action === 'refund' ? 'Issue Refund' : 'Yes, Reject'}
        danger={confirm?.action !== 'approve'}
        onConfirm={handleAction}
        onCancel={() => setConfirm(null)}
      />
    </div>
  );
}
