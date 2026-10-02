import type { OrderStatus, PaymentStatus, ReturnStatus } from '../types';

const ORDER_STATUS_CONFIG: Record<OrderStatus, { label: string; bg: string; text: string; dot: string }> = {
  PENDING_PAYMENT: { label: 'Pending payment', bg: '#FFFBEB', text: '#92400E', dot: '#F59E0B' },
  PAID: { label: 'Paid', bg: '#DCFCE7', text: '#166534', dot: '#16A34A' },
  CONFIRMED: { label: 'Confirmed', bg: '#EDE9FE', text: '#5B21B6', dot: '#7C3AED' },
  PROCESSING: { label: 'Processing', bg: '#FFFBEB', text: '#92400E', dot: '#F59E0B' },
  READY_TO_SHIP: { label: 'Ready to Ship', bg: '#FDF4FF', text: '#6B21A8', dot: '#A855F7' },
  SHIPPED: { label: 'Shipped', bg: '#E0F2FE', text: '#0C4A6E', dot: '#0EA5E9' },
  OUT_FOR_DELIVERY: { label: 'Out for Delivery', bg: '#F0FDF4', text: '#14532D', dot: '#22C55E' },
  DELIVERED: { label: 'Delivered', bg: '#DCFCE7', text: '#166534', dot: '#16A34A' },
  CANCELLED: { label: 'Cancelled', bg: '#FEF2F2', text: '#991B1B', dot: '#EF4444' },
  REFUNDED: { label: 'Refunded', bg: '#F9FAFB', text: '#374151', dot: '#6B7280' },
};

const PAYMENT_CONFIG: Record<PaymentStatus, { label: string; bg: string; text: string }> = {
  PENDING: { label: 'Pending', bg: '#FFFBEB', text: '#92400E' },
  PAID: { label: 'Paid', bg: '#DCFCE7', text: '#166534' },
  FAILED: { label: 'Failed', bg: '#FEF2F2', text: '#991B1B' },
  PARTIALLY_REFUNDED: { label: 'Part. Refunded', bg: '#FFF7ED', text: '#9A3412' },
  REFUNDED: { label: 'Refunded', bg: '#F9FAFB', text: '#374151' },
};

const RETURN_CONFIG: Record<ReturnStatus, { label: string; bg: string; text: string }> = {
  REQUESTED: { label: 'Requested', bg: '#FFF7ED', text: '#9A3412' },
  APPROVED: { label: 'Approved', bg: '#DCFCE7', text: '#166534' },
  ITEMS_RECEIVED: { label: 'Items Received', bg: '#ECFDF5', text: '#065F46' },
  INSPECTED: { label: 'Inspected', bg: '#EDE9FE', text: '#5B21B6' },
  REJECTED: { label: 'Rejected', bg: '#FEF2F2', text: '#991B1B' },
  CANCELLED: { label: 'Cancelled', bg: '#F3F4F6', text: '#6B7280' },
  REFUNDED: { label: 'Refunded', bg: '#F9FAFB', text: '#374151' },
};

interface Props { size?: 'sm' | 'md' }

function Badge({ label, bg, text, size = 'md', dot }: Props & { label: string; bg: string; text: string; dot?: string }) {
  const pad = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';
  return <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${pad}`} style={{ background: bg, color: text }}>{dot && <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: dot }} />}{label}</span>;
}

export function OrderStatusBadge({ status, size = 'md' }: Props & { status: OrderStatus }) {
  const cfg = ORDER_STATUS_CONFIG[status];
  return <Badge {...cfg} size={size} />;
}
export function PaymentStatusBadge({ status, size = 'md' }: Props & { status: PaymentStatus }) {
  const cfg = PAYMENT_CONFIG[status] ?? { label: status, bg: '#F3F4F6', text: '#374151' };
  return <Badge {...cfg} size={size} />;
}
export function ReturnStatusBadge({ status, size = 'md' }: Props & { status: ReturnStatus }) {
  const cfg = RETURN_CONFIG[status] ?? { label: status, bg: '#F3F4F6', text: '#374151' };
  return <Badge {...cfg} size={size} />;
}
