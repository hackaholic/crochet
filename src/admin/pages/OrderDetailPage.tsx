import { useEffect, useState } from 'react';
import type { Order, OrderStatus } from '../types';
import * as api from '../services/api';
import { OrderStatusBadge, PaymentStatusBadge } from '../components/StatusBadge';
import { inr, EmptyState, ConfirmDialog, SeverityBadge } from '../components/AdminShared';

interface Props {
  orderId: string | null;
  onBack: () => void;
}

const STATUS_ACTIONS: { status: OrderStatus; label: string; danger?: boolean }[] = [
  { status: 'CONFIRMED',       label: 'Confirm Order' },
  { status: 'PROCESSING',      label: 'Mark Processing' },
  { status: 'READY_TO_SHIP',   label: 'Mark Ready to Ship' },
  { status: 'SHIPPED',         label: 'Mark Shipped' },
  { status: 'DELIVERED',       label: 'Mark Delivered' },
  { status: 'CANCELLED',       label: 'Cancel Order', danger: true },
];

function copyToClipboard(text: string) {
  navigator.clipboard?.writeText(text).catch(() => {});
}

function CopyBtn({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => { copyToClipboard(value); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
      className="ml-1 text-[10px] text-[#C4622D] hover:underline"
    >
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  );
}

function InfoRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between items-start gap-2 py-1.5 border-b border-[#F8F4EF] last:border-0">
      <span className="text-xs text-[#9C8B7E] shrink-0">{label}</span>
      <span className={`text-xs text-[#1A1108] text-right ${mono ? 'font-mono' : 'font-medium'}`}>
        {value}
        {mono && <CopyBtn value={value} />}
      </span>
    </div>
  );
}

export default function OrderDetailPage({ orderId, onBack }: Props) {
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirm, setConfirm] = useState<{ status: OrderStatus; label: string; danger?: boolean } | null>(null);
  const [updating, setUpdating] = useState(false);
  const [note, setNote] = useState('');
  const [trackingInput, setTrackingInput] = useState('');
  const [showTracking, setShowTracking] = useState(false);

  useEffect(() => {
    if (!orderId) return;
    setLoading(true);
    api.getOrder(orderId).then(o => { setOrder(o); setLoading(false); });
  }, [orderId]);

  const handleStatusUpdate = async () => {
    if (!confirm || !order) return;
    setUpdating(true);
    await api.updateOrderStatus(order.id, confirm.status, note || undefined);
    setOrder(prev => prev ? { ...prev, orderStatus: confirm.status } : prev);
    setConfirm(null);
    setNote('');
    setUpdating(false);
  };

  if (loading) return (
    <div className="space-y-4 animate-pulse">
      <div className="h-6 bg-[#F5EDE0] rounded w-48" />
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 h-80 bg-[#F5EDE0] rounded-xl" />
        <div className="h-80 bg-[#F5EDE0] rounded-xl" />
      </div>
    </div>
  );

  if (!order) return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-10">
      <EmptyState icon="❓" title="Order not found" desc="This order may have been removed or the ID is invalid." action={<button onClick={onBack} className="text-sm text-[#C4622D] font-semibold">← Back to Orders</button>} />
    </div>
  );

  const relDate = (ts?: string) => ts ? new Date(ts).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—';

  return (
    <div className="space-y-4 max-w-full">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-[#9C8B7E]">
        <button onClick={onBack} className="hover:text-[#C4622D] transition-colors">Orders</button>
        <span>/</span>
        <span className="font-mono text-[#1A1108] font-bold">{order.orderNumber}</span>
      </div>

      {/* Header card */}
      <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 flex-wrap mb-2">
              <h2 className="text-xl font-bold text-[#1A1108]" style={{ fontFamily: 'var(--font-serif)' }}>{order.orderNumber}</h2>
              <OrderStatusBadge status={order.orderStatus} />
              <PaymentStatusBadge status={order.paymentStatus} />
              {order.issueFlag && <SeverityBadge severity="warning" />}
            </div>
            <div className="flex flex-wrap gap-4 text-xs text-[#6B5B4E]">
              <span>📅 {relDate(order.date)}</span>
              <span>👤 {order.customer.name}</span>
              <span>💳 {order.paymentMethod}</span>
              <span className="font-bold text-[#1A1108] text-sm">{inr(order.total)}</span>
            </div>
          </div>

          {/* Status actions */}
          <div className="flex flex-wrap gap-2">
            {STATUS_ACTIONS.filter(a => a.status !== order.orderStatus).slice(0, 3).map(action => (
              <button
                key={action.status}
                onClick={() => setConfirm(action)}
                className={`px-3 py-2 text-xs font-semibold rounded-lg border transition-colors ${action.danger ? 'border-[#FECACA] text-[#991B1B] hover:bg-[#FEF2F2]' : 'border-[#E8E0D8] text-[#6B5B4E] hover:bg-[#F5F0EA] hover:text-[#1A1108]'}`}
              >
                {action.label}
              </button>
            ))}
            <div className="relative">
              <button
                onClick={() => setShowTracking(!showTracking)}
                className="px-3 py-2 text-xs font-semibold rounded-lg border border-[#C4622D] text-[#C4622D] hover:bg-[#C4622D] hover:text-white transition-colors"
              >
                + Add Tracking
              </button>
              {showTracking && (
                <div className="absolute right-0 top-10 bg-white border border-[#E8E0D8] rounded-xl shadow-xl p-4 z-20 w-72">
                  <p className="text-xs font-semibold text-[#1A1108] mb-2">Add Tracking</p>
                  <input
                    type="text"
                    value={trackingInput}
                    onChange={e => setTrackingInput(e.target.value)}
                    placeholder="Tracking ID"
                    className="w-full px-3 py-2 text-sm border border-[#E8E0D8] rounded-lg mb-2 focus:outline-none focus:border-[#C4622D]"
                  />
                  <div className="flex gap-2">
                    <button onClick={() => setShowTracking(false)} className="flex-1 py-2 text-xs border border-[#E8E0D8] rounded-lg text-[#6B5B4E] hover:bg-[#F5F0EA]">Cancel</button>
                    <button onClick={() => setShowTracking(false)} className="flex-1 py-2 text-xs bg-[#C4622D] text-white rounded-lg font-semibold hover:bg-[#D4795A]">Save</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Left col: items + timeline */}
        <div className="lg:col-span-2 space-y-4">
          {/* Order items */}
          <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
            <h3 className="font-bold text-[#1A1108] text-sm mb-4" style={{ fontFamily: 'var(--font-serif)' }}>Order Items</h3>
            <div className="space-y-3">
              {order.items.map(item => (
                <div key={item.id} className="flex gap-3 p-3 rounded-xl bg-[#F8F4EF]">
                  {item.image && <img src={item.image} alt={item.productName} className="w-14 h-14 rounded-lg object-cover shrink-0 bg-[#EDE4D0]" />}
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-[#1A1108] text-sm">{item.productName}</p>
                    <p className="text-xs text-[#9C8B7E] font-mono mt-0.5">{item.sku}</p>
                    {item.customization && Object.entries(item.customization).length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        {Object.entries(item.customization).map(([k, v]) => (
                          <span key={k} className="text-[10px] bg-[#F2C4CE]/40 text-[#8B4A3E] px-2 py-0.5 rounded-full border border-[#F2C4CE]/60">
                            {k}: {v}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs text-[#9C8B7E]">Qty: {item.quantity} × {inr(item.unitPrice)}</p>
                    {item.discount > 0 && <p className="text-xs text-[#9C8B7E] line-through">{inr(item.unitPrice * item.quantity)}</p>}
                    <p className="font-bold text-[#1A1108] text-sm">{inr(item.finalAmount)}</p>
                  </div>
                </div>
              ))}
            </div>
            {/* Totals */}
            <div className="mt-4 pt-4 border-t border-[#F0EAE3] space-y-1.5 text-xs">
              {[
                { label: 'Subtotal', value: inr(order.subtotal) },
                { label: 'Discount', value: order.discount > 0 ? `-${inr(order.discount)}` : '—' },
                { label: 'Shipping', value: order.shipping === 0 ? 'FREE' : inr(order.shipping) },
                { label: 'GST (5%)', value: inr(order.gst) },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-[#6B5B4E]">
                  <span>{label}</span><span className="font-medium">{value}</span>
                </div>
              ))}
              <div className="flex justify-between font-bold text-[#1A1108] text-sm pt-2 border-t border-[#F0EAE3]">
                <span>Total</span><span>{inr(order.total)}</span>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
            <h3 className="font-bold text-[#1A1108] text-sm mb-4" style={{ fontFamily: 'var(--font-serif)' }}>Order Timeline</h3>
            <div className="relative pl-5">
              <div className="absolute left-2 top-2 bottom-2 w-px bg-[#E8E0D8]" />
              {order.timeline.map((event, i) => (
                <div key={event.id} className="relative mb-4 last:mb-0">
                  <div className="absolute -left-[13px] w-2.5 h-2.5 rounded-full bg-[#C4622D] border-2 border-white ring-1 ring-[#C4622D]/30" />
                  <div>
                    <p className="text-xs font-semibold text-[#1A1108]">{event.label}</p>
                    <p className="text-[10px] text-[#9C8B7E] mt-0.5">
                      {relDate(event.timestamp)} · {event.actor}
                    </p>
                    {event.note && <p className="text-[10px] text-[#6B5B4E] italic mt-0.5">{event.note}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Shipment */}
          <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
            <h3 className="font-bold text-[#1A1108] text-sm mb-4" style={{ fontFamily: 'var(--font-serif)' }}>Shipment</h3>
            {order.shipment ? (
              <div>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {[
                    { label: 'Courier', value: order.shipment.courier },
                    { label: 'Tracking ID', value: order.shipment.trackingId, mono: true },
                    { label: 'Current Status', value: order.shipment.currentState },
                    { label: 'Est. Delivery', value: order.shipment.estimatedDelivery ? new Date(order.shipment.estimatedDelivery).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—' },
                  ].map(({ label, value, mono }) => (
                    <div key={label} className="p-3 bg-[#F8F4EF] rounded-lg">
                      <p className="text-[10px] text-[#9C8B7E] mb-0.5">{label}</p>
                      <p className={`text-xs font-semibold text-[#1A1108] ${mono ? 'font-mono' : ''}`}>{value}</p>
                      {mono && <CopyBtn value={value} />}
                    </div>
                  ))}
                </div>
                <div className="relative pl-5">
                  <div className="absolute left-2 top-2 bottom-2 w-px bg-[#E8E0D8]" />
                  {order.shipment.history.map((h, i) => (
                    <div key={i} className="relative mb-3 last:mb-0">
                      <div className="absolute -left-[13px] w-2.5 h-2.5 rounded-full bg-[#8FAF8C] border-2 border-white" />
                      <p className="text-xs font-semibold text-[#1A1108]">{h.event}</p>
                      <p className="text-[10px] text-[#9C8B7E]">{relDate(h.timestamp)}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <EmptyState icon="🚚" title="No shipment created" desc="Create a shipment once the order is ready to ship." action={
                <button className="text-xs text-[#C4622D] font-semibold border border-[#C4622D]/30 px-3 py-1.5 rounded-lg hover:bg-[#C4622D] hover:text-white transition-colors">
                  Create Shipment
                </button>
              } />
            )}
          </div>
        </div>

        {/* Right col: customer + notes */}
        <div className="space-y-4">
          {/* Customer */}
          <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
            <h3 className="font-bold text-[#1A1108] text-sm mb-3" style={{ fontFamily: 'var(--font-serif)' }}>Customer</h3>
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-9 h-9 rounded-full bg-[#F2C4CE] flex items-center justify-center text-[#C4622D] font-bold text-sm">
                {order.customer.name[0]}
              </div>
              <div>
                <p className="font-semibold text-sm text-[#1A1108]">{order.customer.name}</p>
                <p className="text-xs text-[#9C8B7E]">Customer</p>
              </div>
            </div>
            <InfoRow label="Email" value={order.customer.email} mono />
            <InfoRow label="Phone" value={order.customer.phone} mono />
          </div>

          {/* Shipping address */}
          <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
            <h3 className="font-bold text-[#1A1108] text-sm mb-3" style={{ fontFamily: 'var(--font-serif)' }}>Shipping Address</h3>
            <div className="text-xs text-[#6B5B4E] leading-relaxed">
              <p className="font-medium text-[#1A1108]">{order.customer.name}</p>
              <p>{order.shippingAddress.line1}</p>
              {order.shippingAddress.line2 && <p>{order.shippingAddress.line2}</p>}
              <p>{order.shippingAddress.city}, {order.shippingAddress.state} {order.shippingAddress.pinCode}</p>
              <p>{order.shippingAddress.country}</p>
            </div>
            <button className="mt-2 text-[10px] text-[#C4622D] hover:underline">Copy address</button>
          </div>

          {/* Order summary */}
          <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
            <h3 className="font-bold text-[#1A1108] text-sm mb-3" style={{ fontFamily: 'var(--font-serif)' }}>Summary</h3>
            <InfoRow label="Payment" value={order.paymentMethod} />
            <InfoRow label="Items" value={String(order.items.reduce((s, i) => s + i.quantity, 0))} />
            <InfoRow label="Subtotal" value={inr(order.subtotal)} />
            <InfoRow label="Shipping" value={order.shipping === 0 ? 'Free' : inr(order.shipping)} />
            <InfoRow label="GST" value={inr(order.gst)} />
            <InfoRow label="Total" value={inr(order.total)} />
          </div>

          {/* Internal notes */}
          <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
            <h3 className="font-bold text-[#1A1108] text-sm mb-3" style={{ fontFamily: 'var(--font-serif)' }}>Internal Notes</h3>
            <textarea
              value={note}
              onChange={e => setNote(e.target.value)}
              placeholder="Add an internal note (not visible to customer)…"
              rows={3}
              className="w-full text-xs border border-[#E8E0D8] rounded-lg px-3 py-2 focus:outline-none focus:border-[#C4622D] resize-none bg-[#FDFAF7] text-[#1A1108] placeholder-[#C5B4A8]"
            />
            <button className="mt-2 text-xs font-semibold text-[#C4622D] border border-[#C4622D]/30 px-3 py-1.5 rounded-lg hover:bg-[#C4622D] hover:text-white transition-colors">
              Save Note
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation dialog */}
      <ConfirmDialog
        open={!!confirm}
        title={confirm?.label ?? ''}
        message={`Are you sure you want to ${confirm?.label?.toLowerCase()} for order ${order.orderNumber}? This action will update the order status.`}
        confirmLabel={confirm?.label}
        danger={confirm?.danger}
        onConfirm={handleStatusUpdate}
        onCancel={() => { setConfirm(null); setNote(''); }}
      />
    </div>
  );
}
